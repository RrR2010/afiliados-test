# Arquitetura do TomeOferta

## Objetivo

A cliente executará o n8n instalado globalmente via npm no Windows, na versão 2.47.3, priorizando fluxos visuais e acompanhamento das execuções. Scripts e serviços auxiliares entram somente onde o editor não atender à necessidade.

## Etapas do processo

| Fluxo visual | Responsabilidade | Solução inicial |
| --- | --- | --- |
| F01 - Descobrir Ofertas | Consultar APIs e fontes autorizadas, limitar consultas e paginar resultados | Nós HTTP Request, Loop Over Items e Wait |
| F02 - Guardar Histórico | Normalizar e persistir observações | Nó nativo Data Table e quatro tabelas do projeto |
| F03 - Avaliar Ofertas | Calcular pontuação explicável e selecionar duas ou três oportunidades | Regras visuais do n8n |
| F04 - Revisar e Gerar Link | Conferir produto, condições e link comissionável | Etapa humana registrada nas Data Tables |
| F05 - Montar Mensagem | Preparar imagem, texto e identificação publicitária | Modelo visual e prévia no n8n |
| F06 - Enviar ao Operador | Enviar via Meta API e acompanhar status; encaminhamento manual ao grupo | Nó HTTP Request e webhook |

**Situação:** a versão e os recursos locais do n8n foram inspecionados, mas não existem fluxos operacionais nem tabelas criadas até o momento.

## Armazenamento: decisão para o MVP

Usar **Data Tables do n8n**, já identificadas na instalação: nó `n8n-nodes-base.dataTable` v1.1, criação, consulta, atualização e exportação CSV disponíveis. Sem nós SQLite comunitários e sem serviço auxiliar nesta etapa.

As quatro tabelas propostas são `produtos`, `historicoPrecos`, `ofertasCandidatas` e `publicacoes`. Consulte [modeloDadosN8n.md](modeloDadosN8n.md) para campos, tipos, regras e plano de migração.

O arquivo [banco/esquema.sql](../banco/esquema.sql) é uma **referência futura** para migração a SQLite; não descreve um banco existente nem deve ser executado no MVP. Não confundir as Data Tables com um banco SQLite externo ou com o banco interno gerenciado pela instalação.

## Qualidade das ofertas

O preço anterior divulgado pelo marketplace não comprova desconto histórico. Na ausência de observações suficientes, registrar **histórico insuficiente**. A comparação entre produtos considera marca, modelo e variação (capacidade, cor, tamanho, volume, procedência e condição). Uma IA futura pode auxiliar casos ambíguos, mas não substituir verificações objetivas.

## Operação e segurança

- O PC precisa permanecer ligado e o n8n em execução durante tarefas agendadas.
- Proteger credenciais e a chave de criptografia do n8n; manter backups fora do Git.
- Fazer exportações periódicas de dados com validação de integridade; a interface de exportação foi identificada, mas ainda não testada com registros.
- Controlar taxa de consulta, erros e limites de armazenamento; respeitar regras das plataformas.
- O ID de mensagem aceito pela Meta não prova entrega: acompanhar status por webhook.
- Respeitar janela de atendimento WhatsApp e exigências de templates aprovados.
- Enviar somente ao operador após validação humana do link afiliado; grupo recebe encaminhamento manual.
