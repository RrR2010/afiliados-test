import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from adaptador_ml import Configuracao, ServidorAdaptador


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
            from adaptador_ml import ArmazenamentoToken

            armazenamento = ArmazenamentoToken(caminho)
            armazenamento.gravar_atomico({"refresh_token": "ficticio", "access_token": "ficticio"})
            self.assertEqual(armazenamento.ler()["refresh_token"], "ficticio")
            self.assertFalse(caminho.with_suffix(".json.lock").exists())


if __name__ == "__main__":
    unittest.main()
