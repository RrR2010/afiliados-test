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

## Resultado da inspeção local — 12/11/2026

O agente verificou o n8n 2.47.3 **sem criar credenciais**:

- OAuth Redirect URL exibida: `http://localhost:5678/rest/oauth2-credential/callback`.
- `Authorization Code`, `Client Credentials` e `PKCE` estão disponíveis como opções de grant.
- Autenticação do cliente por `Header` (padrão) ou `Body`.
- Campos `Scope` e `Auth URI Query Parameters` disponíveis, ambos vazios.
- URLs e identificadores de aplicação não foram preenchidos.

### Recomendação de implantação

A documentação do Mercado Livre confirma a exigência de HTTPS no redirect cadastrado e correspondência exata do `redirect_uri`; o refresh token é rotativo e de uso único. **Não autorizar ainda** com o callback HTTP.

Para manter o editor n8n apenas em localhost, estudar um **hostname HTTPS estável com encaminhamento exclusivo do caminho** `/rest/oauth2-credential/callback` para um proxy local que alcance o n8n; demais caminhos devem responder 404/403. Um túnel Cloudflare com rota restrita por caminho é uma opção, não configuração aprovada. O próprio retorno OAuth transporta código sensível temporário; exigir HTTPS, correspondência de `state`, mínimo de logs e controles adequados. Não publicar toda a API `/rest` nem a interface gráfica.

O n8n usa parâmetros de ambiente para configurar URLs externas (ex.: `N8N_EDITOR_BASE_URL`, `N8N_PROTOCOL`, `N8N_HOST`), mas **não presumir** qual deles altera a URL OAuth no n8n 2.47.3: validar na interface depois de qualquer alteração controlada e documentar efeito sobre acesso local e MCP. O `N8N_WEBHOOK_URL` documentado é voltado aos webhooks, não constitui garantia de ajuste do callback OAuth.

A aplicação exploratória já utiliza um Cloudflare Worker para callback Python; investigar sua disponibilidade e arquitetura **sem reutilizar a rota existente de forma destrutiva, sem revelar segredos e sem alterar o redirect do aplicativo existente**.

Referências:
- https://developers.mercadolivre.com.br/autenticacao-e-autorizacao
- https://developers.mercadolivre.com.br/desenvolvimento-in-house
- https://docs.n8n.io/hosting/configuration/environment-variables/deployment/
- https://github.com/n8n-io/n8n-docs/blob/main/docs/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/configure-webhook-urls-with-reverse-proxy.md
- https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/configuration-file/

### Próxima tarefa local autorizada

Fazer somente diagnóstico de infraestrutura existente: disponibilidade de domínio HTTPS estável, Cloudflare/Worker/túnel pré-existente, como o n8n é iniciado (sem mostrar valores secretos), riscos de alteração do endereço local e se há um proxy local. Não criar túnel, não mexer em DNS, não mudar configurações nem executar login. A pessoa responsável realizará o preenchimento dos segredos e a autorização interativa quando a solução tiver sido aprovada.

## Diagnóstico de rede local e decisão incremental

O agente confirmou instalação n8n global por npm no Windows, ouvindo em `0.0.0.0:5678` e `[::]:5678`; sem proxy/túnel/Cloudflare DNS encontrados, e sem variáveis de endereço externo visíveis. **O n8n não está limitado à interface localhost**. Prioridade: avaliar restrição de escuta local e firewall, sem alterar ainda o processo. Acessar pelo endereço localhost não significa que outros dispositivos na rede não possam alcançar o serviço.

**Antes de contratar/configurar Cloudflare**, executar um teste reversível de configuração, sem credenciais reais: em processo local isolado (com backup e parada controlada, se indispensável), definir temporariamente `N8N_EDITOR_BASE_URL=https://oauth.exemplo.invalid` e observar se a OAuth Redirect URL exibida muda para `https://oauth.exemplo.invalid/rest/oauth2-credential/callback`, preservando o editor e MCP. Depois restaurar configuração anterior e confirmar `http://localhost:5678/rest/oauth2-credential/callback`. A URL `.invalid` é *somente fictícia*, nunca usar no DevCenter.

Referências de implementação indicam `N8N_EDITOR_BASE_URL` como origem da base do callback OAuth; o efeito real deve ser confirmado na instalação 2.47.3, não pressuposto. Configurar `N8N_EDITOR_BASE_URL` público pode alterar outros links do editor mesmo mantendo-o local.

Quando e **somente quando** houver domínio público HTTPS estável sob controle da pessoa responsável, encaminhar exclusivamente `GET /rest/oauth2-credential/callback` (e métodos estritamente necessários), retornando 404/403 para demais caminhos. Controlar acesso, registros de URL e query string, validação de `state`, e não publicar editor nem REST. Testar bloqueio externo com URL real antes da autorização.

Alternativa a estudar se não houver domínio: aproveitar o mecanismo HTTPS de callback do script Python existente **sem reutilizá-lo indevidamente**; a solução será comparada por esforço de operação, risco e rotação de token.

### Etapas autorizadas agora
- Inspeção não destrutiva da configuração de escuta e do firewall para alcance na LAN, sem varredura de rede.
- Teste isolado e reversível do efeito de `N8N_EDITOR_BASE_URL` sobre o OAuth Redirect URL, sem adicionar credenciais nem iniciar autenticação, somente se puder ser feito sem interromper a instância ativa; caso contrário, reportar pré-requisitos e pedir aprovação.
- Nenhum serviço Cloudflare, DNS, DevCenter, token ou credencial deve ser alterado sem autorização explícita.


## Decisão revisada — sem domínio próprio (13/11/2026)

A pessoa responsável confirmou que não dispõe de domínio próprio e autorizou avaliar o uso do OAuth em Python já funcional. **Para o MVP, a recomendação passa a ser um adaptador HTTP local em Python com OAuth encapsulado, sem Cloudflare Tunnel.** O caminho de OAuth2 nativo do n8n permanece documentado como alternativa futura, não como implementação escolhida agora.

### Limite entre visual e código

O fluxo de negócio F01 continua no n8n, com nós visuais para configuração de buscas, paginação, loops, decisões, espera, normalização e consolidação. Somente a autenticação/renovação e as chamadas à API previamente permitidas ficam encapsuladas no adaptador Python, com contrato HTTP simples.

```text
n8n (HTTP Request, IF, Loop etc.)
  -> 127.0.0.1:8765 (adaptador Python local)
     -> GET /users/me (diagnóstico)
     -> GET /products/search (busca por catálogo)
     -> GET /products/{id}/items (anúncios)
     -> OAuth Mercado Livre com refresh token rotativo
```

A porta 8765 é **exemplo**, não porta já configurada. A ligação ocorre apenas via loopback, sem túnel, DNS, proxy público ou callback n8n. O callback HTTPS do Python já usado anteriormente é preservado para reautorização humana caso necessária.

### Requisitos de segurança e robustez

1. Escutar **somente** em `127.0.0.1`, não em `0.0.0.0` / `::`; acesso pela instância local n8n no mesmo Windows. Verificar firewall/isolamento do próprio n8n separadamente.
2. Expor **apenas rotas GET predefinidas** e validar `q`, `limit`, `offset`, IDs e demais parâmetros; jamais aceitar URL externa arbitrária nem endpoint genérico de proxy.
3. Preferir chave local independente do Mercado Livre entre n8n e adaptador (guardada em credencial HTTP Header do n8n, não no JSON exportado). Não retornar `access_token`, `refresh_token`, client secret ou conteúdo sensível em respostas/logs.
4. Credenciais ML e tokens pertencem **somente** ao adaptador local; persistir novos pares de tokens com escrita atômica e travamento para que duas requisições simultâneas não usem o mesmo refresh token. Uma única fonte de verdade: adaptar o `ml_auth.py` já existente; não deixar outra rotina atualizando o mesmo cache de tokens.
5. Renovar token somente se necessário, conforme API, repetir uma única vez após 401 comprovadamente causado por expiração; `invalid_grant` bloqueia e exige nova autorização humana. Não fazer retry de autorização em loop.
6. Respostas e status HTTP coerentes: `404` sem vencedores retornado como caso controlado e `429` como limite de taxa; erros 401/403 ou falhas de rede não podem virar `results: []` silenciosamente. Minimizar e higienizar erros, com contagens sem dados secretos.
7. Testar primeiro as rotas do adaptador com respostas simuladas (sem chamadas externas), depois conectar o n8n com volume mínimo autorizado e sem gravação em Data Tables nem WhatsApp.
8. Não iniciar serviço persistente no Windows nem criar tarefas agendadas sem aprovação. Documentar o procedimento de inicialização/parada; avaliar inicialização automática e healthcheck antes de agendar F01.
9. Quando a proteção SSRF do n8n estiver ativa, verificar a necessidade de autorizar o loopback local de maneira **específica**, sem desabilitar a proteção global. Ver documentação n8n.
10. Não incluir scripts locais, arquivos de token ou segredos em PR inadvertidamente; antes de versionar, revisar fontes e dependências.

### Decisão de fase e critérios de aceite

**Etapa 1 (agora):** implementar adaptador local pequeno, com endpoints falsos e testes sem ML real; preparar documentação e código revisável em PR próprio, mantendo F01 e PR #6 separados. **Etapa 2:** conectar o F01 visual aos endpoints locais e testar simulação fim-a-fim. **Etapa 3:** pessoa responsável confere o estado da autorização já existente e insere segredos/autoriza quando necessário; executar teste mínimo de catálogo e anúncios reais; validar token após expiração antes da execução diária.

Este design elimina a necessidade de alterar `N8N_EDITOR_BASE_URL`, cadastrar o callback n8n ou contratar domínio para o MVP. É uma **recomendação de arquitetura** pendente de validação operacional, não integração já concluída.

Fontes: https://developers.mercadolivre.com.br/autenticacao-e-autorizacao ; https://docs.n8n.io/hosting/securing/ssrf-protection
