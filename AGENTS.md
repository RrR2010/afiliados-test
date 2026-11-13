# Orientações para agentes locais e assistentes

**Todo o projeto deve ser escrito em português do Brasil**, incluindo documentação, mensagens de commit, títulos de PR, nomes de pastas, arquivos próprios, variáveis próprias e rótulos dos fluxos do n8n. Siga [as convenções de nomenclatura](documentacao/convencoes.md). Preserve os identificadores externos exigidos pelas APIs e os nomes-padrão de arquivos usados pelas ferramentas.

## Responsabilidades

- **Assistente remoto:** pesquisa pública, arquitetura, especificações, documentação, revisão de PRs e alterações no GitHub que não dependam do computador local.
- **Agente local:** edição e teste do n8n, operações com a instalação da cliente, exportação de workflows e outras tarefas que dependam de acesso local.
- **Pessoa responsável:** prioridades, autorização de operações reais, decisões comerciais e aprovação de publicações.
- O mesmo agente local pode receber tarefas sucessivas; os prompts de continuidade devem indicar apenas objetivo, **branch e PR de destino**, restrições e critérios de aceite. Não é necessário pedir a releitura integral destes arquivos em cada prompt, exceto quando forem alterados.

## Organização de branches e pull requests

1. Antes de atuar, conferir `git status`, branch atual, alterações locais não versionadas, PRs abertos e a `main` remota.
2. **Uma tarefa = uma branch = um PR**. Criar branch a partir de `main` atualizada quando for trabalho novo.
3. **Continuação ou correção de PR aberto:** permanecer na **mesma branch do PR**, atualizar e enviar novos commits; **não abrir outro PR** para a mesma entrega.
4. Manter `main` protegida como referência estável: não enviar commits diretamente; integrar alterações por PR após revisão.
5. Evitar PRs dependentes: mesclar primeiro a especificação, depois a implementação. Se uma implementação já estiver aberta, atualizar sua branch com `main` antes do merge, com cuidado para não sobrescrever alterações locais. Não fazer `git reset --hard`, `git clean` ou `git push --force` sem autorização.
6. Trabalhos paralelos são permitidos se alterarem arquivos diferentes. **Um único responsável por workflow JSON em cada momento**. Se dois trabalhos precisarem modificar o mesmo arquivo, fazê-los sequencialmente.
7. Antes de abrir PR, informar arquivos alterados, testes realizados, dependências e riscos. O revisor confere referências, conflitos e o comportamento do fluxo antes de integrar.
8. Após merge, atualizar a `main` local com `git pull --ff-only`. A exclusão automática da branch remota mesclada é desejável; branches locais só são apagadas após confirmar que não contêm alterações não enviadas.
9. **Nomes sugeridos:** `funcionalidade/descobertaOfertas`, `correcao/normalizarAnuncios`, `documentacao/revisarArquitetura`. Não manter branches antigas apenas como histórico: o histórico permanece em commits e PRs.
10. **Não criar PR para cada teste temporário:** preservar arquivos experimentais fora do versionamento até decidir se são úteis, sem confundi-los com o fluxo oficial.

## Edição dos workflows e segurança

1. Priorizar nós visuais do n8n em vez de scripts; separar os fluxos por etapa de negócio.
2. Editar os fluxos no editor local; exportar JSON completo e revisado para `fluxos/` em cada alteração aprovada. Não incluir credenciais, dados pessoais ou conteúdos fixados de execuções reais.
3. Não inventar IDs de credenciais e não editar simultaneamente o mesmo fluxo em diferentes instâncias. Git guarda exportações, mas **não sincroniza automaticamente** o editor do n8n.
4. Preservar arquivos locais não versionados e workflows de teste. Não modificar workflows existentes que estejam fora do escopo da tarefa.
5. Não incluir `.env`, tokens OAuth, chaves de API, contatos pessoais, cópias do SQLite ou banco interno do n8n em commits ou prompts.
6. Não executar disparos reais de WhatsApp, serviços pagos, varreduras em massa ou mudanças destrutivas sem aprovação explícita. Testar com dados simulados primeiro.
7. Exigir revisão humana e link de afiliado verificado antes de enviar conteúdo publicitário. Um preço original anunciado ou cupom não verificado não comprova desconto.

## Formato de entrega do agente local

Informar: branch trabalhada, PR existente ou novo, arquivos alterados, testes, situação da exportação JSON, operações locais, necessidade de importação no n8n, limitações e próximos passos. Caso um prompt cite um PR existente, **atualizar aquele PR, sem abrir um novo**.
