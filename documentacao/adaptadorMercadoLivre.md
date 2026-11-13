# Adaptador local do Mercado Livre

O `adaptador_ml.py` oferece uma ponte HTTP local para que o n8n consulte o
Mercado Livre sem receber tokens OAuth. A primeira versão opera em modo
fictício e não realiza chamadas externas.

## Contrato HTTP

Todas as rotas exigem o cabeçalho local `X-Adaptador-Chave`. A chave não deve
ser colocada no JSON do workflow; no n8n, use uma credencial de cabeçalho.

| Método e rota | Parâmetros | Sucesso fictício |
| --- | --- | --- |
| `GET /diagnostico` | nenhum | `200`, versão, modo fictício e endereço |
| `GET /catalogo?q=fone&limite=10&deslocamento=0` | `q`, `limite` 1–50, `deslocamento` 0–10000 | `200`, `site_id`, `paging` e `results` |
| `GET /anuncios?idProduto=MLB-FAKE-1` | `idProduto` alfanumérico, `_` ou `-`, até 80 caracteres | `200`, `idProduto` e `results` |

Os casos fictícios `produto-404`, `MLB-FAKE-SEM-OFERTAS` e `MLB-FAKE-429`
produzem, respectivamente, respostas `404` ou `429`. Parâmetros ausentes,
IDs inválidos, rotas desconhecidas e URLs arbitrárias são rejeitados. O
adaptador não aceita um parâmetro `url` e usa hosts/caminhos upstream fixos.

Respostas de erro têm somente `erro` e `mensagem` sanitizados. Tokens nunca
fazem parte de resposta, log ou mensagem de erro.

## Inicialização no Windows

No PowerShell, a partir da raiz do repositório:

```powershell
$env:ADAPTADOR_ML_CHAVE_LOCAL = 'defina-uma-chave-local-fora-do-Git'
$env:ADAPTADOR_ML_MODO_FICTICIO = 'true'
$env:ADAPTADOR_ML_PORTA = '5688'
py .\adaptador_ml.py
```

O processo não é iniciado permanentemente por este projeto. Para parar,
pressione `Ctrl+C`. A chave deve ser fornecida ao n8n por uma credencial de
cabeçalho com nome `X-Adaptador-Chave`.

## Autenticação real futura

O modo real permanece desativado. Quando aprovado, o serviço deverá receber
somente a localização de um armazenamento protegido por
`ADAPTADOR_ML_ARMAZENAMENTO_TOKENS`; o arquivo não deve ser versionado. A
renovação rotativa usa bloqueio exclusivo, relê o estado dentro do bloqueio e
grava a resposta nova com arquivo temporário e `os.replace`. Falhas retornam
mensagem genérica e não imprimem access token ou refresh token.

As chamadas reais, quando autorizadas, terão host fixo
`api.mercadolibre.com`, cabeçalho `Authorization` interno e timeout. Esta
entrega não configura credenciais, não acessa o DevCenter e não faz chamadas
externas.

## Dependências e limites

- Python 3.10 ou superior recomendado.
- Somente biblioteca padrão; não há `requirements.txt`.
- A chave local é uma barreira adicional, não substitui firewall.
- O serviço vincula-se a `127.0.0.1` por padrão e não deve ser publicado
  diretamente na rede.
- A persistência de tokens foi implementada apenas para a futura integração;
  não há token local incluído neste repositório.
