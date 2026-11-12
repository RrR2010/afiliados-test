# F01 — Descobrir Ofertas no Mercado Livre

## Objetivo

Criar visualmente no n8n um fluxo **manual e inicialmente inativo** que busca produtos de catálogo por palavra-chave e consulta os anúncios relacionados. **Não** gravar histórico, enviar WhatsApp ou gerar links afiliados neste fluxo. Persistência será responsabilidade do F02.

## Pré-requisitos

- n8n 2.47.3 (npm no Windows), com credencial OAuth do Mercado Livre configurada localmente.
- Tabelas do MVP descritas em [modeloDadosN8n.md](modeloDadosN8n.md), após validação local.
- Usar somente APIs autorizadas. Os endpoints `GET /products/search` e `GET /products/{id}/items` funcionaram em testes anteriores; `GET /sites/MLB/search` e leitura direta de `/items/{id}` apresentaram HTTP 403. Não depender desses dois últimos.
- A instância local nunca deve ter tokens, números de clientes ou valores secretos exportados no JSON versionado.

## Fluxo visual planejado

| Ordem | Nó sugerido | Função |
| --- | --- | --- |
| 1 | Manual Trigger | Iniciar somente por ação humana no teste |
| 2 | Edit Fields | Parâmetros explícitos: `termoBusca`, `limiteProdutosEncontrados`, `limiteProdutosExaminados`, `intervaloSegundos` |
| 3 | HTTP Request | `GET https://api.mercadolibre.com/products/search?status=active&site_id=MLB&q=...` com autenticação da instância |
| 4 | Loop Over Items | Percorrer os produtos e as páginas gradualmente, respeitando limite de varredura |
| 5 | HTTP Request | `GET https://api.mercadolibre.com/products/{id}/items` |
| 6 | IF | Tratar 200 com anúncios; 404 com `No winners found` significa ausência de anúncios |
| 7 | Wait | Respeitar intervalo entre chamadas; tratar 429 com espera e quantidade limitada de tentativas |
| 8 | Edit Fields | Normalizar um registro por anúncio e preservar ID do produto, anúncio, preço e origem |
| 9 | Resumo visual | Contagem de produtos examinados, produtos com anúncios, anúncios coletados e erros |

Nomes e rótulos na interface devem estar em português. Os tipos exatos dos nós, estrutura de paginação e tratamento de erros precisam ser confirmados na instalação, sem inventar configuração não testada.

## Contrato de saída sugerido

Um item JSON por anúncio, com:

- `idProduto`: ex. `ML:MLB22246671`;
- `idAnuncio`: ex. `ML:MLB6225112300`;
- `plataforma`: `mercadoLivre`;
- `nomeProduto`: título retornado pelo catálogo;
- `precoCentavos`: preço positivo convertido para inteiro;
- `precoOriginalCentavos`: opcional, indicado como metadado e **não** prova de desconto real;
- `freteGratis`: booleano somente quando explicitamente informado;
- `urlProduto` e `urlAnuncio`: URLs construídas com IDs, sujeitas à validação; **não são links de afiliados**;
- `coletadoEm`: data UTC no formato `YYYY-MM-DDTHH:mm:ss.sssZ`;
- `origem`: endpoint consultado.

Se `original_price` e `shipping` estiverem ausentes, não atribuir automaticamente zero. Preservar distinção entre desconhecido e gratuito.

## Critérios de aceite

1. Pesquisa manual e limitada, sem ativação de agendamento.
2. Executa com credenciais locais, sem expô-las em logs, JSON exportado ou Git.
3. 404 sem vencedores não interrompe a execução.
4. Limita total de produtos examinados e requisições; não faz varredura ilimitada.
5. Gera resultados normalizados para o F02, sem acessar diretamente tabelas.
6. Testado primeiro com dados fictícios, depois com pequena consulta real aprovada.
7. Exporta JSON sanitizado como `fluxos/F01DescobrirOfertasMercadoLivre.json`, mediante validação.
8. Registra no PR instruções de importação, requisitos de credenciais e resultado dos testes.

## Condução do trabalho

Esta especificação pode ser revisada sem acesso ao PC. A criação dos nós e o teste na instância local devem ser tarefas do agente. Não é necessário criar scripts Python para reproduzir a orquestração.


## Estado das Data Tables no ambiente local

Em 12 de novembro de 2026, o agente local confirmou que as quatro Data Tables foram criadas e testadas com dados fictícios. Identificadores da instância (referência operacional, **não portáveis para outros ambientes**):

| Tabela | ID local |
| --- | --- |
| `produtos` | `ObzUTIbHK3OmOatY` |
| `historicoPrecos` | `6pg0hW5nQQsgyzhD` |
| `ofertasCandidatas` | `ygU6Y1nOD2mVV5rI` |
| `publicacoes` | `CRuVaS3CcAmEajVd` |

A inserção, leitura e atualização foram confirmadas pelo agente, sem executar automações reais. O n8n acrescentou `id`, `createdAt` e `updatedAt`. Os dados de teste deverão ser identificados e removidos de modo controlado antes de gerar histórico real. O workflow experimental `Afiliados` e a tabela `testePersistencia` permanecem separados. A exportação CSV não foi repetida nessa etapa.
