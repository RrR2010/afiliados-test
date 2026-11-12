# Plano de evolução

## Etapa 0 — Estrutura inicial

- [x] Organizar o projeto e descrever a arquitetura visual do n8n.
- [x] Padronizar nomenclaturas e documentações em português.
- [x] Criar inventário de configuração sem valores secretos.
- [x] Criar esquema inicial de SQLite do TomeOferta.
- [ ] Identificar versão, instalação, permissões e recursos do n8n local.
- [ ] Escolher a maneira mais simples e segura de integrar n8n ao SQLite.

## Etapa 1 — Descoberta e histórico

- [ ] Criar o fluxo F01 visualmente para buscar produtos e anúncios usando endpoints autorizados do Mercado Livre.
- [ ] Aplicar paginação, limites de consulta, tratamento de erros e intervalos entre requisições.
- [ ] Tratar `404 No winners found` como ausência de ofertas, não como falha geral.
- [ ] Criar F02 para gravar preços com data, origem, anúncio e condições.
- [ ] Testar com respostas simuladas antes de consultar dados reais.

## Etapa 2 — Curadoria e links

- [ ] Criar F03 com pontuação explicável e seleção das duas ou três melhores oportunidades.
- [ ] Identificar histórico insuficiente; não validar descontos pelo campo `original_price`.
- [ ] Criar F04 de revisão e aprovação humana.
- [ ] Permitir adicionar ofertas manualmente à seleção.
- [ ] Gerar e conferir link de afiliado manualmente na primeira versão.

## Etapa 3 — WhatsApp

- [ ] Criar F05 para prévia do texto, imagem e condições.
- [ ] Criar F06 para enviar ao número da pessoa responsável, não ao grupo.
- [ ] Registrar respostas e estados de entrega da Meta.
- [ ] A pessoa responsável encaminha manualmente ao grupo.

## Futuro

- [ ] Cupons com regras de elegibilidade verificáveis.
- [ ] Outras plataformas via APIs e feeds autorizados.
- [ ] Correspondência de produtos entre plataformas; IA somente onde ajudar.
- [ ] Histórico comparativo de promoções e Black Friday.

## Decisões pendentes

- Método de instalação do n8n: Docker, npm ou outro.
- Disponibilidade de nó SQLite ou necessidade de serviço local.
- Estratégia de versionamento de fluxos conforme plano do n8n.
- Número de WhatsApp de produção, modelos aprovados e credenciais.
- Destino e frequência das cópias de segurança.
