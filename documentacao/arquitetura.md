# Arquitetura do TomeOferta

## Objetivo

A cliente executará o n8n no próprio computador, priorizando fluxos visuais e a possibilidade de acompanhar cada execução. Scripts e serviços auxiliares serão usados somente quando houver uma necessidade técnica concreta.

## Etapas do processo

| Fluxo visual | Responsabilidade | Solução inicial |
| --- | --- | --- |
| F01 - Descobrir Ofertas | Consultar APIs e fontes autorizadas, limitar consultas e paginar resultados | Nós HTTP Request, Loop Over Items e Wait do n8n |
| F02 - Guardar Histórico | Normalizar e persistir observações de preços | n8n e integração controlada com SQLite |
| F03 - Avaliar Ofertas | Calcular pontuação explicável, ordenar e selecionar duas ou três candidatas | Regras visuais e critérios auditáveis |
| F04 - Revisar e Gerar Link | Conferir produto, vendedor, condições e link de afiliado; aprovar ou rejeitar | Etapa humana registrada no banco |
| F05 - Montar Mensagem | Preparar imagem, texto, preço, condições e identificação de publicidade | Modelo de mensagem no n8n com prévia |
| F06 - Enviar ao Operador | Enviar à pessoa responsável pelo WhatsApp e registrar o retorno da Meta | API oficial; encaminhamento manual ao grupo |

**Nenhum fluxo executável está incluído nesta estrutura inicial.** Primeiro é necessário identificar a versão e a instalação do n8n.

## Dados

O banco do TomeOferta usa SQLite próprio, independente do banco interno do n8n. A primeira definição está em [esquema.sql](../banco/esquema.sql).

- `produtos`: identificação normalizada do item.
- `anuncios`: ofertas de vendedores e marketplaces específicos.
- `observacoes_preco`: histórico imutável de preço, horário, fonte e condições de compra.
- `cupons`: regras, datas e situação de verificação de cupons.
- `ofertas_candidatas`: pontuação, justificativas e aprovação humana.
- `publicacoes`: conteúdo aprovado e estado de envio.

O preço anterior divulgado pelo marketplace não comprova desconto histórico. Na ausência de observações suficientes, a avaliação deve registrar **histórico insuficiente**, não afirmar que houve redução.

A comparação de produtos precisa considerar variante, capacidade, cor, tamanho, volume, procedência e condição. Uma LLM futura pode auxiliar na correspondência ambígua, mas não deve substituir validações objetivas.

## Cuidados operacionais

- O computador da cliente precisa estar ligado, com o n8n em execução, para tarefas programadas.
- Realizar cópias de segurança do SQLite fora do Git e testar a restauração.
- Guardar credenciais do Mercado Livre, Meta, chaves do n8n e outros segredos fora do repositório.
- Verificar se há um nó SQLite apropriado na instalação. Caso contrário, avaliar um pequeno serviço local autenticado; não presumir disponibilidade do nó Execute Command.
- Registrar erros, controlar o ritmo das consultas e respeitar os termos das plataformas.
- A aceitação de uma mensagem pela API Meta não significa que ela foi entregue; acompanhar retornos por webhook.
- Verificar janela de atendimento de 24 horas e modelos de mensagem aprovados quando aplicável.
- Não disparar diretamente para grupos. A pessoa responsável recebe e encaminha manualmente, depois de aprovar a oferta e o link comissionável.
