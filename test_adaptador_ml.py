import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from adaptador_ml import ArmazenamentoToken, ClienteMercadoLivre, Configuracao, ErroAdaptador, ServidorAdaptador, URL_TOKEN


class TesteAdaptadorMercadoLivre(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configuracao = Configuracao(chave="chave-de-teste", endereco="127.0.0.1", porta=0, ficticio=True)
        cls.servidor = ServidorAdaptador(cls.configuracao)
        cls.porta = cls.servidor.server_address[1]
        cls.thread = threading.Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        cls.thread.join(timeout=2)

    def requisicao(self, caminho, chave="chave-de-teste"):
        requisicao = Request(f"http://127.0.0.1:{self.porta}{caminho}", headers={"X-Adaptador-Chave": chave})
        try:
            with urlopen(requisicao, timeout=2) as resposta:
                return resposta.status, json.loads(resposta.read())
        except HTTPError as erro:
            return erro.code, json.loads(erro.read())

    def test_diagnostico_200_sem_api_externa(self):
        status, corpo = self.requisicao("/diagnostico")
        self.assertEqual(status, 200)
        self.assertTrue(corpo["modoFicticio"])
        self.assertFalse(corpo["apiExterna"])

    def test_catalogo_200_e_anuncios_200(self):
        status, corpo = self.requisicao("/catalogo?q=fone&limite=2")
        self.assertEqual(status, 200)
        self.assertEqual(len(corpo["results"]), 2)
        status, corpo = self.requisicao("/anuncios?idProduto=MLB-FAKE-1")
        self.assertEqual(status, 200)
        self.assertEqual([item["item_id"] for item in corpo["results"]], ["MLB-ANUNCIO-1", "MLB-ANUNCIO-2"])

    def test_simulador_respeita_deslocamento_e_limite(self):
        status, corpo = self.requisicao("/catalogo?q=fone&limite=1&deslocamento=1")
        self.assertEqual(status, 200)
        self.assertEqual(corpo["paging"]["limit"], 1)
        self.assertEqual(corpo["paging"]["offset"], 1)
        self.assertEqual([item["id"] for item in corpo["results"]], ["MLB-FAKE-2"])

    def test_404_ficticio(self):
        status, corpo = self.requisicao("/catalogo?q=produto-404")
        self.assertEqual(status, 404)
        self.assertEqual(corpo["erro"], "sem_resultados")

    def test_429_ficticio(self):
        status, corpo = self.requisicao("/anuncios?idProduto=MLB-FAKE-429")
        self.assertEqual(status, 429)
        self.assertEqual(corpo["erro"], "limite_upstream")

    def test_chave_e_parametros(self):
        status, _ = self.requisicao("/diagnostico", chave="errada")
        self.assertEqual(status, 401)
        status, _ = self.requisicao("/anuncios?idProduto=https%3A%2F%2Fexemplo.invalid")
        self.assertEqual(status, 400)
        status, _ = self.requisicao("/rota-inexistente")
        self.assertEqual(status, 404)

    def test_persistencia_atomica_e_bloqueio_sem_expor_token(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "tokens.json"
            armazenamento = ArmazenamentoToken(caminho)
            armazenamento.gravar_atomico({"app_id": "app-ficticio", "refresh_token": "ficticio", "access_token": "ficticio", "expires_at": time.time() + 3600})
            self.assertEqual(armazenamento.ler()["refresh_token"], "ficticio")
            self.assertFalse(caminho.with_suffix(".json.lock").exists())

    def test_cache_incompativel_nao_e_sobrescrito(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "tokens.json"
            conteudo = '{"access_token":"antigo"}'
            caminho.write_text(conteudo, encoding="utf-8")
            armazenamento = ArmazenamentoToken(caminho)
            with self.assertRaises(ErroAdaptador) as contexto:
                armazenamento.ler()
            self.assertEqual(contexto.exception.status, 503)
            self.assertEqual(caminho.read_text(encoding="utf-8"), conteudo)

    def test_rotas_reais_usam_products_search_e_items(self):
        with tempfile.TemporaryDirectory() as pasta:
            transporte = TransporteSimulado()
            cliente, armazenamento = self.cliente_real(Path(pasta) / "tokens.json", transporte)
            cliente.buscar_catalogo("fone", 7, 14)
            cliente.buscar_anuncios("MLB123")
            chamadas = [chamada for chamada in transporte.chamadas if chamada[0] == "GET"]
            consulta = parse_qs(urlparse(chamadas[0][1]).query)
            self.assertEqual(urlparse(chamadas[0][1]).path, "/products/search")
            self.assertEqual(consulta["status"], ["active"])
            self.assertEqual(consulta["site_id"], ["MLB"])
            self.assertEqual(consulta["q"], ["fone"])
            self.assertEqual(consulta["limit"], ["7"])
            self.assertEqual(consulta["offset"], ["14"])
            self.assertEqual(urlparse(chamadas[1][1]).path, "/products/MLB123/items")
            self.assertEqual(armazenamento.ler()["app_id"], "app-ficticio")

    def test_token_expirado_renova_por_oauth_e_substitui_refresh(self):
        with tempfile.TemporaryDirectory() as pasta:
            transporte = TransporteSimulado()
            cliente, armazenamento = self.cliente_real(Path(pasta) / "tokens.json", transporte, expirado=True)
            cliente.buscar_catalogo("fone", 2, 0)
            self.assertEqual(transporte.contagem(URL_TOKEN), 1)
            cache = armazenamento.ler()
            self.assertEqual(cache["access_token"], "access-novo")
            self.assertEqual(cache["refresh_token"], "refresh-novo")
            self.assertEqual(cache["app_id"], "app-ficticio")

    def test_401_renova_uma_vez_e_reenvia_sem_loop(self):
        with tempfile.TemporaryDirectory() as pasta:
            transporte = TransporteSimulado(api_statuses=[401, 200])
            cliente, _ = self.cliente_real(Path(pasta) / "tokens.json", transporte)
            self.assertEqual(cliente.buscar_catalogo("fone", 2, 0)["ok"], True)
            self.assertEqual(transporte.contagem(URL_TOKEN), 1)
            self.assertEqual(len([x for x in transporte.chamadas if x[0] == "GET"]), 2)

    def test_segundo_401_apos_renovacao_nao_faz_nova_tentativa_oauth(self):
        with tempfile.TemporaryDirectory() as pasta:
            transporte = TransporteSimulado(api_statuses=[401, 401])
            cliente, _ = self.cliente_real(Path(pasta) / "tokens.json", transporte)
            with self.assertRaises(ErroAdaptador) as contexto:
                cliente.buscar_catalogo("fone", 2, 0)
            self.assertEqual(contexto.exception.status, 401)
            self.assertEqual(transporte.contagem(URL_TOKEN), 1)
            self.assertEqual(len([x for x in transporte.chamadas if x[0] == "GET"]), 2)

    def test_invalid_grant_nao_faz_retry_infinito(self):
        with tempfile.TemporaryDirectory() as pasta:
            transporte = TransporteSimulado(refresh_status=400, refresh_payload={"error": "invalid_grant"})
            cliente, _ = self.cliente_real(Path(pasta) / "tokens.json", transporte, expirado=True)
            with self.assertRaisesRegex(ErroAdaptador, "renovação rejeitada") as contexto:
                cliente.buscar_catalogo("fone", 2, 0)
            self.assertEqual(contexto.exception.status, 401)
            self.assertEqual(transporte.contagem(URL_TOKEN), 1)

    def test_403_404_e_429_sao_preservados(self):
        for status in (403, 404, 429):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as pasta:
                transporte = TransporteSimulado(api_statuses=[status])
                cliente, _ = self.cliente_real(Path(pasta) / "tokens.json", transporte)
                with self.assertRaises(ErroAdaptador) as contexto:
                    cliente.buscar_catalogo("fone", 2, 0)
                self.assertEqual(contexto.exception.status, status)

    def test_renovacao_concorrente_faz_uma_so_troca(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "tokens.json"
            transporte = TransporteSimulado(atraso_renovacao=0.08)
            armazenamento_inicial = ArmazenamentoToken(caminho)
            armazenamento_inicial.gravar_atomico({"app_id": "app-ficticio", "access_token": "access-antigo", "refresh_token": "refresh-antigo", "expires_at": time.time() - 1})
            clientes = [ClienteMercadoLivre(False, ArmazenamentoToken(caminho), "app-ficticio", "segredo-ficticio", transporte) for _ in range(2)]
            resultados = []
            erros = []

            def consultar(cliente):
                try:
                    resultados.append(cliente.buscar_catalogo("fone", 2, 0))
                except Exception as erro:  # capturar falhas da thread para a asserção principal
                    erros.append(erro)

            threads = [threading.Thread(target=consultar, args=(cliente,)) for cliente in clientes]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=2)
            self.assertEqual(len(resultados), 2)
            self.assertEqual(erros, [])
            self.assertEqual(transporte.contagem(URL_TOKEN), 1)
            self.assertEqual(ArmazenamentoToken(caminho).ler()["refresh_token"], "refresh-novo")

    @staticmethod
    def cliente_real(caminho, transporte, expirado=False):
        armazenamento = ArmazenamentoToken(caminho)
        armazenamento.gravar_atomico({"app_id": "app-ficticio", "access_token": "access-antigo", "refresh_token": "refresh-antigo", "expires_at": time.time() - 1 if expirado else time.time() + 3600})
        return ClienteMercadoLivre(False, armazenamento, "app-ficticio", "segredo-ficticio", transporte), armazenamento


class TransporteSimulado:
    def __init__(self, api_statuses=None, refresh_status=200, refresh_payload=None, atraso_renovacao=0):
        self.chamadas = []
        self.api_statuses = list(api_statuses or [200])
        self.refresh_status = refresh_status
        self.refresh_payload = refresh_payload or {"access_token": "access-novo", "refresh_token": "refresh-novo", "expires_in": 3600}
        self.atraso_renovacao = atraso_renovacao
        self._lock = threading.Lock()

    def __call__(self, metodo, url, cabecalhos, corpo):
        with self._lock:
            self.chamadas.append((metodo, url, cabecalhos, corpo))
        if url == URL_TOKEN:
            if self.atraso_renovacao:
                time.sleep(self.atraso_renovacao)
            return self.refresh_status, self.refresh_payload
        status = self.api_statuses.pop(0) if self.api_statuses else 200
        return status, {"ok": True}

    def contagem(self, url):
        return sum(1 for _, chamada, _, _ in self.chamadas if chamada == url)


if __name__ == "__main__":
    unittest.main()
