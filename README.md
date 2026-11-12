# TomeOferta

Sistema de descoberta, histórico de preços e curadoria humana de ofertas com envio assistido pelo WhatsApp. **n8n local é o orquestrador visual**; código só entra onde o canvas não for suficiente.

## Fluxo de negócio

1. **Descoberta:** APIs oficiais/feeds autorizados (começando por Mercado Livre).
2. **Histórico:** persistência de observações de preço em SQLite próprio do projeto.
3. **Ranking:** pontuação explicável, top 2–3 e inclusão/remoção manual.
4. **Afiliados:** humana gera e valida o link comissionável antes de aprovar.
5. **Template:** n8n prepara imagem, preço e texto para WhatsApp.
6. **Envio:** Meta Cloud API manda para o número da operadora, que encaminha manualmente ao grupo opt-in.

A etapa de link afiliado é deliberadamente humana na primeira versão. Preço original anunciado não prova desconto real; preços e cupons devem ser verificados.

## Primeiros passos

1. Clone: `git clone https://github.com/RrR2010/afiliados-test.git`
2. Copie `.env.example` para `.env` (`Copy-Item .env.example .env` no PowerShell).
3. Preencha os campos necessários. Guarde tokens no **n8n Credentials** quando possível; nunca em Git. Este arquivo `.env` **não é carregado automaticamente pelo n8n**.
4. Confirme como o n8n foi instalado (Docker, npm, serviço etc.) antes de escolher a integração SQLite.
5. Crie os workflows visualmente; exporte JSON sem segredos para `workflows/` e abra PR para revisão.

## Documentação

- [Arquitetura](docs/architecture.md)
- [Versionamento de workflows e n8n](docs/n8n-versioning.md)
- [Roadmap](docs/roadmap.md)
- [Regras para agentes locais](AGENTS.md)
- [Schema SQLite inicial](db/schema.sql)
- [Workflows planejados](workflows/README.md)

## Estado atual

**Fundação de arquitetura apenas.** Este PR não instala nem executa workflows n8n, não cria o arquivo SQLite em produção e não envia mensagens. A integração deverá ser implementada e validada passo a passo.

**Fontes de verdade:** GitHub para arquivos/versionamento; n8n local para a edição visual e credenciais; SQLite do TomeOferta para os dados históricos (com backups fora do Git).
