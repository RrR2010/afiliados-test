"""Adaptador local e restrito para consultas do Mercado Livre pelo n8n.

O modo fictício é o padrão e não realiza chamadas externas. A integração real
deve ser habilitada explicitamente somente após revisão de segurança.
"""

from __future__ import annotations

import hmac
import json
import os
import re
import tempfile
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen


VERSAO = "0.2.0"
ENDERECO_PADRAO = "127.0.0.1"
PORTA_PADRAO = 5688
CHAVE_CABECALHO = "X-Adaptador-Chave"
PADRAO_ID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")
DOMINIO_API = "api.mercadolibre.com"
DOMINIO_AUTORIZACAO = "api.mercadolibre.com"
URL_TOKEN = f"https://{DOMINIO_AUTORIZACAO}/oauth/token"
Transporte = Callable[[str, str, dict[str, str], bytes | None], tuple[int, Any]]


class ErroAdaptador(Exception):
    """Falha controlada que pode ser apresentada sem segredos."""

    def __init__(self, status: int, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.status = status
        self.codigo = codigo
        self.mensagem = mensagem


class RespostaFicticia(ErroAdaptador):
    """Resposta simulada equivalente a uma falha upstream."""


class BloqueioArquivo:
    """Bloqueio entre processos por criação exclusiva de arquivo.

    O arquivo nunca contém token. Em caso de processo interrompido, o tempo
    limite permite recuperação segura do bloqueio abandonado.
    """

    def __init__(self, caminho: Path, tempo_limite: float = 30.0) -> None:
        self.caminho = caminho
        self.tempo_limite = tempo_limite
        self._proprietario = False

    def __enter__(self) -> "BloqueioArquivo":
        inicio = time.monotonic()
        while True:
            try:
                fd = os.open(self.caminho, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                self._proprietario = True
                return self
            except FileExistsError:
                if time.monotonic() - inicio >= self.tempo_limite:
                    try:
                        if time.time() - self.caminho.stat().st_mtime >= self.tempo_limite:
                            self.caminho.unlink()
                            continue
                    except FileNotFoundError:
                        continue
                    raise ErroAdaptador(503, "bloqueio_token", "renovação ocupada")
                time.sleep(0.05)

    def __exit__(self, *_: object) -> None:
        if self._proprietario:
            try:
                self.caminho.unlink()
            except FileNotFoundError:
                pass


class ArmazenamentoToken:
    """Cache atômico compatível com o formato usado por ``ml_auth.py``."""

    CAMPOS_OBRIGATORIOS = {"app_id", "access_token", "refresh_token", "expires_at"}

    def __init__(self, caminho: Path) -> None:
        self.caminho = caminho
        self.bloqueio = BloqueioArquivo(caminho.with_suffix(caminho.suffix + ".lock"))

    def ler(self) -> dict[str, Any]:
        try:
            dados = json.loads(self.caminho.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}
        except (OSError, json.JSONDecodeError) as exc:
            raise ErroAdaptador(503, "armazenamento_token", "estado de autenticação indisponível") from exc
        if not isinstance(dados, dict) or not self._formato_valido(dados):
            raise ErroAdaptador(503, "armazenamento_token", "formato de autenticação incompatível")
        return dados

    def gravar_atomico(self, dados: dict[str, Any]) -> None:
        if not self._formato_valido(dados):
            raise ErroAdaptador(502, "resposta_token", "resposta de autenticação incompatível")
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        fd, temporario = tempfile.mkstemp(prefix=self.caminho.name + ".", dir=self.caminho.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, separators=(",", ":"))
                arquivo.flush()
                os.fsync(arquivo.fileno())
            os.replace(temporario, self.caminho)
        finally:
            try:
                os.unlink(temporario)
            except FileNotFoundError:
                pass

    @classmethod
    def _formato_valido(cls, dados: dict[str, Any]) -> bool:
        return (
            cls.CAMPOS_OBRIGATORIOS.issubset(dados)
            and all(isinstance(dados[campo], str) and bool(dados[campo]) for campo in ("app_id", "access_token", "refresh_token"))
            and isinstance(dados["expires_at"], (int, float))
        )


def transporte_urllib(metodo: str, url: str, cabecalhos: dict[str, str], corpo: bytes | None = None) -> tuple[int, Any]:
    """Transporte real isolado para permitir testes sem rede."""
    requisicao = Request(url, data=corpo, headers=cabecalhos, method=metodo)
    try:
        with urlopen(requisicao, timeout=15) as resposta:
            return resposta.status, _ler_json(resposta.read())
    except HTTPError as exc:
        return exc.code, _ler_json(exc.read())
    except OSError as exc:
        raise ErroAdaptador(502, "falha_upstream", "serviço externo indisponível") from exc


def _ler_json(conteudo: bytes) -> Any:
    try:
        return json.loads(conteudo.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}


class ClienteMercadoLivre:
    """Cliente com rotas fixas, renovação única e refresh rotativo."""

    def __init__(self, ficticio: bool = True, armazenamento: ArmazenamentoToken | None = None, app_id: str | None = None, client_secret: str | None = None, transporte: Transporte | None = None, relogio: Callable[[], float] = time.time) -> None:
        self.ficticio = ficticio
        self.armazenamento = armazenamento
        self.app_id = app_id
        self.client_secret = client_secret
        self.transporte = transporte or transporte_urllib
        self.relogio = relogio

    def buscar_catalogo(self, consulta: str, limite: int, deslocamento: int) -> dict[str, Any]:
        self._validar_consulta(consulta)
        self._validar_paginacao(limite, deslocamento)
        if self.ficticio:
            if consulta == "produto-404":
                raise RespostaFicticia(404, "sem_resultados", "nenhum produto encontrado")
            if consulta == "produto-429":
                raise RespostaFicticia(429, "limite_upstream", "limite fictício atingido")
            produtos = [
                {"id": "MLB-FAKE-1", "titulo": "Produto fictício 1"},
                {"id": "MLB-FAKE-2", "titulo": "Produto fictício 2"},
                {"id": "MLB-FAKE-3", "titulo": "Produto fictício 3"},
            ]
            return {"site_id": "MLB", "consulta": consulta, "status": "active", "paging": {"limit": limite, "offset": deslocamento, "total": len(produtos)}, "results": produtos[deslocamento:deslocamento + limite]}
        return self._requisitar("/products/search", {"status": "active", "site_id": "MLB", "q": consulta, "limit": limite, "offset": deslocamento})

    def buscar_anuncios(self, id_produto: str) -> dict[str, Any]:
        self._validar_id(id_produto, "idProduto")
        if self.ficticio:
            if id_produto == "MLB-FAKE-SEM-OFERTAS":
                raise RespostaFicticia(404, "sem_anuncios", "nenhum anúncio encontrado")
            if id_produto == "MLB-FAKE-429":
                raise RespostaFicticia(429, "limite_upstream", "limite fictício atingido")
            anuncios = [{"item_id": "MLB-ANUNCIO-1", "price": 129.90}, {"item_id": "MLB-ANUNCIO-2", "price": 149.90}]
            return {"idProduto": id_produto, "results": anuncios}
        return self._requisitar(f"/products/{id_produto}/items", {})

    def _requisitar(self, caminho: str, parametros: dict[str, Any]) -> dict[str, Any]:
        if not caminho.startswith("/") or "//" in caminho or ".." in caminho:
            raise ErroAdaptador(400, "rota_invalida", "rota upstream não permitida")
        token = self._obter_access_token()
        resposta = self._chamar_api(caminho, parametros, token)
        if resposta[0] == 401:
            token = self._renovar_token(forcar=True, token_rejeitado=token)
            resposta = self._chamar_api(caminho, parametros, token)
        return self._interpretar_api(resposta)

    def _chamar_api(self, caminho: str, parametros: dict[str, Any], token: str) -> tuple[int, Any]:
        url = f"https://{DOMINIO_API}{caminho}"
        if parametros:
            url += "?" + urlencode(parametros)
        return self.transporte("GET", url, {"Authorization": f"Bearer {token}", "Accept": "application/json"}, None)

    def _obter_access_token(self) -> str:
        if self.armazenamento is None:
            raise ErroAdaptador(503, "autenticacao_indisponivel", "autorização não configurada")
        dados = self.armazenamento.ler()
        self._validar_app_id(dados)
        if float(dados["expires_at"]) > self.relogio() + 120:
            return str(dados["access_token"])
        return self._renovar_token()

    def _renovar_token(self, forcar: bool = False, token_rejeitado: str | None = None) -> str:
        if self.armazenamento is None or not self.app_id or not self.client_secret:
            raise ErroAdaptador(503, "autenticacao_indisponivel", "renovação não configurada")
        with self.armazenamento.bloqueio:
            atual = self.armazenamento.ler()
            self._validar_app_id(atual)
            if token_rejeitado and atual["access_token"] != token_rejeitado:
                return str(atual["access_token"])
            if not forcar and float(atual["expires_at"]) > self.relogio() + 120:
                return str(atual["access_token"])
            corpo = urlencode({"grant_type": "refresh_token", "client_id": self.app_id, "client_secret": self.client_secret, "refresh_token": atual["refresh_token"]}).encode("utf-8")
            status, resposta = self.transporte("POST", URL_TOKEN, {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}, corpo)
            if status != 200:
                if status == 400 and isinstance(resposta, dict) and resposta.get("error") == "invalid_grant":
                    raise ErroAdaptador(401, "refresh_token_invalido", "renovação rejeitada")
                if status == 429:
                    raise ErroAdaptador(429, "limite_upstream", "limite de renovação atingido")
                raise ErroAdaptador(502, "renovacao_falhou", "não foi possível renovar a autorização")
            if not isinstance(resposta, dict) or not resposta.get("access_token") or not resposta.get("refresh_token"):
                raise ErroAdaptador(502, "resposta_token", "resposta de renovação incompleta")
            novo = {"app_id": self.app_id, "access_token": str(resposta["access_token"]), "refresh_token": str(resposta["refresh_token"]), "expires_at": self.relogio() + int(resposta.get("expires_in", 21600))}
            self.armazenamento.gravar_atomico(novo)
            return novo["access_token"]

    def _validar_app_id(self, dados: dict[str, Any]) -> None:
        if self.app_id and dados.get("app_id") != self.app_id:
            raise ErroAdaptador(503, "armazenamento_token", "cache de autenticação incompatível")

    @staticmethod
    def _interpretar_api(resposta: tuple[int, Any]) -> dict[str, Any]:
        status, payload = resposta
        if status == 200:
            return payload if isinstance(payload, dict) else {"resultado": payload}
        if status in (401, 403, 404, 429):
            codigo = {401: "nao_autorizado", 403: "acesso_negado", 404: "nao_encontrado", 429: "limite_upstream"}[status]
            raise ErroAdaptador(status, codigo, "resposta do serviço externo")
        raise ErroAdaptador(502, "falha_upstream", "serviço externo indisponível")

    @staticmethod
    def _validar_consulta(consulta: str) -> None:
        if not consulta or len(consulta) > 120 or any(ord(ch) < 32 for ch in consulta):
            raise ErroAdaptador(400, "consulta_invalida", "consulta ausente ou inválida")

    @staticmethod
    def _validar_id(valor: str, nome: str) -> None:
        if not PADRAO_ID.fullmatch(valor):
            raise ErroAdaptador(400, "id_invalido", f"{nome} inválido")

    @staticmethod
    def _validar_paginacao(limite: int, deslocamento: int) -> None:
        if not 1 <= limite <= 50 or not 0 <= deslocamento <= 10000:
            raise ErroAdaptador(400, "paginacao_invalida", "limite ou deslocamento inválido")


@dataclass
class Configuracao:
    chave: str
    endereco: str = ENDERECO_PADRAO
    porta: int = PORTA_PADRAO
    ficticio: bool = True
    caminho_tokens: Path | None = None
    app_id: str | None = None
    client_secret: str | None = None

    @classmethod
    def ambiente(cls) -> "Configuracao":
        chave = os.environ.get("ADAPTADOR_ML_CHAVE_LOCAL", "")
        ficticio = os.environ.get("ADAPTADOR_ML_MODO_FICTICIO", "true").lower() == "true"
        if not chave:
            raise SystemExit("ADAPTADOR_ML_CHAVE_LOCAL não configurada")
        if not ficticio and not os.environ.get("ADAPTADOR_ML_ARMAZENAMENTO_TOKENS"):
            raise SystemExit("armazenamento de tokens não configurado")
        caminho = Path(os.environ["ADAPTADOR_ML_ARMAZENAMENTO_TOKENS"]) if os.environ.get("ADAPTADOR_ML_ARMAZENAMENTO_TOKENS") else None
        return cls(chave=chave, endereco=ENDERECO_PADRAO, porta=int(os.environ.get("ADAPTADOR_ML_PORTA", PORTA_PADRAO)), ficticio=ficticio, caminho_tokens=caminho, app_id=os.environ.get("ML_APP_ID"), client_secret=os.environ.get("ML_CLIENT_SECRET"))


class ManipuladorHTTP(BaseHTTPRequestHandler):
    server_version = "AdaptadorMercadoLivre/" + VERSAO

    def do_GET(self) -> None:  # noqa: N802 - nome exigido pela biblioteca padrão.
        configuracao: Configuracao = self.server.configuracao  # type: ignore[attr-defined]
        chave_recebida = self.headers.get(CHAVE_CABECALHO, "")
        if not chave_recebida or not hmac.compare_digest(chave_recebida, configuracao.chave):
            self._responder(401, {"erro": "nao_autorizado", "mensagem": "chave local inválida"})
            return
        try:
            consulta = parse_qs(urlparse(self.path).query, keep_blank_values=True)
            rota = urlparse(self.path).path
            cliente: ClienteMercadoLivre = self.server.cliente  # type: ignore[attr-defined]
            if rota == "/diagnostico":
                payload = {"status": "ok", "versao": VERSAO, "modoFicticio": cliente.ficticio, "endereco": configuracao.endereco, "apiExterna": False if cliente.ficticio else True}
                self._responder(200, payload)
                return
            if rota == "/catalogo":
                payload = cliente.buscar_catalogo(self._unico(consulta, "q"), self._inteiro(consulta, "limite", 10), self._inteiro(consulta, "deslocamento", 0))
                self._responder(200, payload)
                return
            if rota == "/anuncios":
                payload = cliente.buscar_anuncios(self._unico(consulta, "idProduto"))
                self._responder(200, payload)
                return
            raise ErroAdaptador(404, "rota_nao_encontrada", "rota não encontrada")
        except ErroAdaptador as exc:
            self._responder(exc.status, {"erro": exc.codigo, "mensagem": exc.mensagem})
        except (TypeError, ValueError):
            self._responder(400, {"erro": "parametros_invalidos", "mensagem": "parâmetros inválidos"})

    @staticmethod
    def _unico(consulta: dict[str, list[str]], nome: str) -> str:
        valores = consulta.get(nome, [])
        if len(valores) != 1:
            raise ErroAdaptador(400, "parametro_invalido", f"parâmetro {nome} obrigatório")
        return valores[0]

    @classmethod
    def _inteiro(cls, consulta: dict[str, list[str]], nome: str, padrao: int) -> int:
        valor = cls._unico(consulta, nome) if nome in consulta else str(padrao)
        return int(valor)

    def _responder(self, status: int, payload: dict[str, Any]) -> None:
        corpo = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *_: object) -> None:
        return


class ServidorAdaptador(ThreadingHTTPServer):
    allow_reuse_address = True

    def __init__(self, configuracao: Configuracao) -> None:
        armazenamento = ArmazenamentoToken(configuracao.caminho_tokens) if configuracao.caminho_tokens else None
        self.configuracao = configuracao
        self.cliente = ClienteMercadoLivre(configuracao.ficticio, armazenamento, configuracao.app_id, configuracao.client_secret)
        super().__init__((configuracao.endereco, configuracao.porta), ManipuladorHTTP)


def executar() -> None:
    configuracao = Configuracao.ambiente()
    servidor = ServidorAdaptador(configuracao)
    print(f"Adaptador local em http://{configuracao.endereco}:{configuracao.porta} (modo fictício: {configuracao.ficticio})", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == "__main__":
    executar()
