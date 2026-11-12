# Fluxos visuais do n8n

Esta pasta receberá arquivos JSON **exportados do editor visual do n8n**, revisados e sem segredos. A estrutura inicial não disponibiliza fluxos executáveis.

| Código | Nome visível no n8n | Arquivo planejado |
| --- | --- | --- |
| F01 | Descobrir Ofertas - Mercado Livre | `F01DescobrirOfertasMercadoLivre.json` |
| F02 | Guardar Histórico de Preços | `F02GuardarHistoricoPrecos.json` |
| F03 | Avaliar e Selecionar Ofertas | `F03AvaliarOfertas.json` |
| F04 | Revisar e Validar Link de Afiliado | `F04RevisarOfertas.json` |
| F05 | Montar Mensagem de WhatsApp | `F05MontarMensagemWhatsApp.json` |
| F06 | Enviar ao Operador | `F06EnviarAoOperador.json` |

Todo PR que alterar fluxos deve informar: versão do n8n, credenciais a configurar, testes efetuados, instruções de importação e forma de desfazer a mudança. Não salvar informações reais de clientes nem valores de credenciais nos arquivos exportados.
