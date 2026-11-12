# Plano de evolução

## Etapa 0 — Estrutura inicial

- [x] Organizar arquitetura visual do n8n e nomenclaturas em português.
- [x] Criar inventário de configuração sem valores secretos.
- [x] Preservar esquema SQLite inicial como alternativa futura.
- [x] Confirmar n8n 2.47.3 instalado via npm e MCP autenticado.
- [x] Confirmar Data Tables v1.1 e importação/exportação CSV na interface.
- [x] Adotar Data Tables como persistência do MVP.
- [x] Testar criação, leitura, atualização e exportação com dados fictícios (tabela temporária `testePersistencia`; exportação CSV com vírgula e BOM).\n- [ ] Reproduzir e diagnosticar divergência de fuso na coluna `date`; usar `string` ISO UTC para datas de negócio até validação.
- [ ] Definir rotina de backup e restauração da instância.\n- [ ] Exportar/versionar ou descartar de forma controlada o workflow temporário `Afiliados` após documentação do teste.

## Etapa 1 — Descoberta e histórico

- [ ] Criar `produtos`, `historicoPrecos`, `ofertasCandidatas` e `publicacoes` conforme [modelo de dados](modeloDadosN8n.md).
- [ ] Criar F01 com APIs autorizadas do Mercado Livre, paginação e limites.
- [ ] Tratar `404 No winners found` como ausência de anúncios.
- [ ] Criar F02 com observações de preço sem sobrescrever histórico.
- [ ] Testar com respostas simuladas antes das APIs reais.
- [ ] Exportar JSON sanitizado de cada fluxo para `fluxos/`.

## Etapa 2 — Curadoria e afiliado

- [ ] Criar F03: pontuação explicável e seleção de 2–3 oportunidades.
- [ ] Sinalizar histórico insuficiente e cupons não validados.
- [ ] Criar F04: revisão humana, adição manual e validação do link afiliado.

## Etapa 3 — WhatsApp

- [ ] Criar F05: mensagem e prévia de imagem.
- [ ] Criar F06: envio ao operador e registro do status de entrega.
- [ ] Operador encaminha manualmente ao grupo.

## Futuro

- [ ] Cupons por regras de elegibilidade; novas plataformas autorizadas.
- [ ] Correspondência de produtos entre plataformas com apoio de IA.
- [ ] Exportação auditada e migração a SQLite ou PostgreSQL, se necessária.

## Decisões pendentes

- Teste real das Data Tables e exportação CSV.
- Política de backup, tamanho de dados e retenção.
- Estratégia de versionamento conforme plano do n8n.
- Credenciais e número de WhatsApp de produção.
