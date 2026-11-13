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
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen


VERSAO = "0.1.0"
ENDERECO_PADRAO = "127.0.0.1"
PORTA_PADRAO = 5688
CHAVE_CABECALHO = "X-Adaptador-Chave"
PADRAO_ID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")
DOMINIO_API = "api.mercadolibre.com"
DOMINIO_AUTORIZACAO = "auth.mercadolivre.com.br"


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
    """Persistência local atômica de tokens, nunca exposta pela API."""

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
        if not isinstance(dados, dict):
            raise ErroAdaptador(503, "armazenamento_token", "estado de autenticação inválido")
        return dados

    def gravar_atomico(self, dados: dict[str, Any]) -> None:
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


class ClienteMercadoLivre:
    """Cliente com host e caminhos fixos; não aceita URL fornecida pelo usuário."""

    def __init__(self, ficticio: bool = True, armazenamento: ArmazenamentoToken | None = None) -> None:
        self.ficticio = ficticio
        self.armazenamento = armazenamento

    def buscar_catalogo(self, consulta: str, limite: int, deslocamento: int) -> dict[str, Any]:
        self._validar_consulta(consulta)
        self._validar_paginacao(limite, deslocamento)
        if self.ficticio:
            if consulta == "produto-404":
                raise RespostaFicticia(404, "sem_resultados", "nenhum produto encontrado")
            if consulta == "produto-429":
                raise RespostaFicticia(429, "limite_upstream", "limite fictício atingido")
            produtos = [{"id": "MLB-FAKE-1", "titulo": "Produto fictício 1"}, {"id": "MLB-FAKE-2", "titulo": "Produto fictício 2"}]
            return {"site_id": "MLB", "consulta": consulta, "paging": {"limit": limite, "offset": deslocamento}, "results": produtos[:limite]}
        return self._requisitar("/sites/MLB/search", {"q": consulta, "limit": limite, "offset": deslocamento})

    def buscar_anuncios(self, id_produto: str) -> dict[str, Any]:
        self._validar_id(id_produto, "idProduto")
        if self.ficticio:
            if id_produto == "MLB-FAKE-SEM-OFERTAS":
                raise RespostaFicticia(404, "sem_anuncios", "nenhum anúncio encontrado")
            if id_produto == "MLB-FAKE-429":
                raise RespostaFicticia(429, "limite_upstream", "limite fictício atingido")
            anuncios = [{"item_id": "MLB-ANUNCIO-1", "price": 129.90}, {"item_id": "MLB-ANUNCIO-2", "price": 149.90}]
            return {"idProduto": id_produto, "results": anuncios}
        return self._requisitar(f"/products/{id_produto}", {})

    def renovar_token(self, dados: dict[str, Any], requisitar: Any) -> dict[str, Any]:
        """Renova sob bloqueio e grava somente a resposta válida de forma atômica."""
        if self.armazenamento is None:
            raise ErroAdaptador(503, "armazenamento_token", "renovação não configurada")
        with self.armazenamento.bloqueio:
            atual = self.armazenamento.ler()
            if atual.get("refresh_token") != dados.get("refresh_token"):
                return atual
            try:
                novo = requisitar(dados["refresh_token"])
                if not isinstance(novo, dict) or not novo.get("access_token"):
                    raise ValueError("resposta sem access_token")
                self.armazenamento.gravar_atomico(novo)
                return novo
            except Exception as exc:
                raise ErroAdaptador(502, "renovacao_falhou", "não foi possível renovar a autorização") from exc

    def _requisitar(self, caminho: str, parametros: dict[str, Any]) -> dict[str, Any]:
        if not caminho.startswith("/") or "//" in caminho or ".." in caminho:
            raise ErroAdaptador(400, "rota_invalida", "rota upstream não permitida")
        token = self.armazenamento.ler().get("access_token") if self.armazenamento else None
        if not token:
            raise ErroAdaptador(503, "autenticacao_indisponivel", "autorização não configurada")
        url = f"https://{DOMINIO_API}{caminho}?{urlencode(parametros)}" if parametros else f"https://{DOMINIO_API}{caminho}"
        requisicao = Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
        try:
            with urlopen(requisicao, timeout=15) as resposta:
                return json.loads(resposta.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code in (404, 429):
                raise ErroAdaptador(exc.code, "resposta_upstream", "resposta do serviço externo") from exc
            raise ErroAdaptador(502, "falha_upstream", "serviço externo indisponível") from exc
        except (OSError, ValueError) as exc:
            raise ErroAdaptador(502, "falha_upstream", "serviço externo indisponível") from exc

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

    @classmethod
    def ambiente(cls) -> "Configuracao":
        chave = os.environ.get("ADAPTADOR_ML_CHAVE_LOCAL", "")
        ficticio = os.environ.get("ADAPTADOR_ML_MODO_FICTICIO", "true").lower() == "true"
        if not chave:
            raise SystemExit("ADAPTADOR_ML_CHAVE_LOCAL não configurada")
        if not ficticio and not os.environ.get("ADAPTADOR_ML_ARMAZENAMENTO_TOKENS"):
            raise SystemExit("armazenamento de tokens não configurado")
        caminho = Path(os.environ["ADAPTADOR_ML_ARMAZENAMENTO_TOKENS"]) if os.environ.get("ADAPTADOR_ML_ARMAZENAMENTO_TOKENS") else None
        return cls(chave=chave, endereco=ENDERECO_PADRAO, porta=int(os.environ.get("ADAPTADOR_ML_PORTA", PORTA_PADRAO)), ficticio=ficticio, caminho_tokens=caminho)


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
        self.cliente = ClienteMercadoLivre(configuracao.ficticio, armazenamento)
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
