# Integração real com Mercado Livre — autenticação e liberação do F01

## Decisão provisória

Priorizar credencial **OAuth2 API** nativa do n8n com **Authorization Code**, sem criar uma rotina caseira de tokens no workflow de descoberta. **Não ativar a rota real nem agendamentos antes de validar o retorno HTTPS e a renovação do refresh token.**

## Fontes oficiais

- Autenticação Mercado Livre: https://developers.mercadolivre.com.br/autenticacao-e-autorizacao
- Desenvolvimento in-house / callback HTTPS: https://developers.mercadolivre.com.br/desenvolvimento-in-house
- Credenciais HTTP Request do n8n: https://docs.n8n.io/integrations/builtin/credentials/httprequest/

## Parâmetros propostos (sem valores secretos)

| Campo no n8n | Valor/ação |
| --- | --- |
| Tipo da credencial | `OAuth2 API` (genérica) |
| Grant Type | `Authorization Code` |
| Authorization URL | `https://auth.mercadolivre.com.br/authorization` |
| Access Token URL | `https://api.mercadolibre.com/oauth/token` |
| Client ID | App ID da aplicação no DevCenter (preencher **localmente**) |
| Client Secret | Secret da aplicação (preencher **localmente**) |
| Scope | `read offline_access` se o campo/scopes da aplicação exigir; validar com DevCenter e retorno real |
| Authentication | `Body` (client ID/secret no corpo da solicitação) |
| PKCE | A aplicação exploratória usava PKCE desabilitado; não ativar sem ajustar o cadastro e a credencial |
| OAuth Redirect URL | **Copiar literalmente do formulário da credencial n8n**, sem presumir domínio nem caminho |

Use sempre cabeçalho `Authorization: Bearer <access_token>` ao consultar a API. O n8n deve enviar esse cabeçalho automaticamente pelo método de autenticação escolhido. Não acrescentar token em query string nem imprimir tokens nos logs.

## Bloqueio do callback no ambiente local

O n8n inspecionado atende em `http://localhost:5678`. A documentação da aplicação Mercado Livre exige Redirect URI **HTTPS** e correspondência exata da URL cadastrada com a enviada na autorização e troca do código.

O callback HTTPS anteriormente usado no script Python apontava para um Worker Cloudflare; ele **não** é o callback OAuth da credencial n8n e não deve ser reutilizado simplesmente alterando o valor do campo.

Possibilidades para análise posterior:

1. Expor **apenas o callback OAuth** sob HTTPS por uma ponte autenticada/corretamente encaminhada até o n8n local, com proteção de entrada e sem publicar o editor inteiro. Exige aprovação de TI e validação de origem, disponibilidade e encaminhamento do caminho correto.
2. Se o provedor aceitar um retorno local especial na configuração concreta, validar documentalmente antes de tentar; não assumir que `http://localhost` será aceito.
3. Como contingência, manter temporariamente o script Python comprovado para autenticação, com segurança apropriada, sem copiar tokens para Data Tables, workflow JSON ou Git. Essa via não resolve ainda a integração visual de tokens rotativos; é apenas plano alternativo.

**Não alterar ainda a aplicação no DevCenter**, não substituir o Redirect URI existente e não conectar a credencial sem solução confirmada para HTTPS.

## Particularidades dos tokens

- Access token: normalmente `expires_in=21600` segundos (seis horas).
- Refresh token: **uso único**; cada renovação devolve outro, e apenas o mais recente funciona.
- Evitar que script Python e n8n compartilhem/renovem a **mesma concessão OAuth** simultaneamente. Para o teste, congelar a renovação de um lado ou separar as autorizações e confirmar se os grants não se invalidam mutuamente.
- Evitar execução concorrente do F01 ou múltiplas tentativas simultâneas de renovação.
- Se houver `invalid_grant`, interromper e investigar; não fazer loops de renovação.
- Não presumir que a credencial genérica do n8n renova antes da expiração ou persiste corretamente a rotação: testar um ciclo completo com execução posterior à expiração e verificar comportamento sem visualizar valores dos tokens.
- Proteger a chave de criptografia do n8n e seu backup.

## Sequência de testes locais planejada

**Teste 1 — Configuração (somente inspeção):** consultar a URL OAuth Redirect exibida na credencial genérica, campos disponíveis e possibilidade de configurar client authentication pelo corpo; sem preencher credenciais reais, conectar contas ou alterar DevCenter.

**Teste 2 — Callback:** somente após autorização explícita e definição segura de HTTPS, validar que uma autorização chega ao callback e resulta em credencial conectada.

**Teste 3 — Consulta mínima:** `GET https://api.mercadolibre.com/users/me`, manualmente, sem divulgar resposta pessoal e com status resumido.

**Teste 4 — Rotação:** executar após expiração real do access token; confirmar que a credencial mantém funcionamento e não perde o refresh token. Não acessar/compartilhar valores.

**Teste 5 — F01 real:** com credencial validada, habilitar procura limitada de catálogo e anúncios, com limites e tratamento de HTTP 404/429/403/401; ainda sem gravar em Data Tables ou enviar WhatsApp.

## Restrições atuais do F01

O PR #4 foi integrado como **protótipo de simulação**. Não há comprovação de paginação real, limites efetivos de varredura, tratamento do formato de erro, retries ou credencial real. Não ativar o fluxo nem mudar `modoTesteFicticio` sem esses mecanismos e revisão.

A nova implementação real será feita em uma **branch e PR novos**, sem alterar diretamente a `main`. Preferir nós visuais, com código curto se eliminar complexidade excessiva.

## Critério de sucesso da autenticação

Somente considerar pronta após callback HTTPS válido, autorização concluída, `/users/me` com sucesso, execução após a expiração com refresh bem-sucedido, sem exposição de tokens nem alteração descontrolada do token usado pelo script exploratório.
