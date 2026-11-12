# Orientações para agentes locais e assistentes

**Todo o projeto deve ser escrito em português do Brasil**, incluindo documentação, mensagens de commit, títulos de PR, nomes de pastas, arquivos próprios, variáveis próprias e rótulos dos fluxos do n8n. Siga obrigatoriamente [as convenções de nomenclatura](documentacao/convencoes.md). Preserve os identificadores externos exigidos pelas APIs e os nomes-padrão de arquivos usados pelas ferramentas.

## Forma de trabalho

1. Antes de atuar, verificar `git status`, branch, mudanças recentes da `main` e PRs abertos.
2. Criar uma branch curta por tarefa, partindo da `main` atualizada. Não enviar commits diretamente à `main`.
3. Priorizar nós visuais do n8n em vez de scripts. Separar os fluxos por etapa de negócio.
4. Editar os fluxos no editor local; exportar o JSON completo e revisado para `fluxos/` em cada alteração. Não incluir credenciais, dados pessoais ou conteúdos fixados de execuções reais.
5. Não inventar identificadores de credenciais do n8n; configurar vínculos localmente após a importação.
6. Não editar simultaneamente o mesmo fluxo em duas máquinas ou agentes. Git guarda versões exportadas, não sincroniza o editor automaticamente.
7. Não incluir `.env`, tokens OAuth, chaves de API, contatos pessoais, cópias do SQLite ou o banco interno do n8n em commits ou prompts.
8. Não executar disparos reais de WhatsApp, serviços pagos, varreduras em massa ou mudanças destrutivas sem aprovação explícita. Testar primeiro com dados simulados.
9. Exigir revisão humana e link de afiliado verificado antes de enviar conteúdo publicitário. Um preço original anunciado ou cupom não verificado não comprova um desconto.
10. Na entrega, informar branch, PR, arquivos alterados, testes, situação da exportação JSON, passos manuais necessários e pendências.

## Primeira tarefa sugerida

Inspecionar a versão, o método de instalação e os recursos disponíveis no n8n local, incluindo integração com SQLite, API, MCP e exportação de JSON. **Somente diagnóstico**, sem alterar configurações nem executar fluxos.
