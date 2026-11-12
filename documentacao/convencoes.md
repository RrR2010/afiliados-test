# Convenções de nomenclatura

A documentação, os nomes de fluxos e a estrutura do projeto devem usar **português do Brasil**. Este padrão vale para alterações futuras e para agentes de programação.

| Elemento | Convenção | Exemplo |
| --- | --- | --- |
| Pastas | palavras simples, minúsculas, sem acentos | `documentacao/`, `banco/`, `fluxos/`, `dados/` |
| Arquivos próprios com várias palavras | `camelCase`, sem acentos ou espaços | `versionamentoN8n.md`, `planoDeEvolucao.md` |
| Variáveis, funções e campos JSON próprios | `camelCase` em português | `precoAtual`, `gerarMensagem`, `urlAfiliado` |
| Classes, tipos e entidades de domínio | `PascalCase` em português | `ObservacaoPreco`, `OfertaCandidata` |
| Tabelas e colunas SQLite | `snake_case` em português, por clareza nas consultas SQL | `observacoes_preco`, `preco_centavos` |
| Identificadores de ambiente do projeto | `MAIUSCULAS_COM_SUBLINHADO` em português | `CAMINHO_SQLITE`, `TAMANHO_SELECAO` |
| Fluxos do n8n | número fixo + nome descritivo em português | `F01 - Descobrir Ofertas - Mercado Livre` |
| Arquivos exportados dos fluxos | prefixo `F01` + `camelCase` em português | `F01DescobrirOfertasMercadoLivre.json` |
| Títulos, notas e nomes de nós no n8n | português legível, com acentos permitidos na interface | `Consultar Ofertas`, `Validar Aprovação` |

## Exceções necessárias

- Arquivos convencionais reconhecidos por ferramentas permanecem com seus nomes: `README.md`, `AGENTS.md`, `.gitignore` e `.env.example`.
- Nomes de APIs, produtos, bibliotecas, parâmetros externos e campos de respostas **não devem ser traduzidos**. Exemplos: `access_token`, `phone_number_id`, `n8n`, `OAuth`, `ML_APP_ID` e `META_ACCESS_TOKEN`.
- Chaves de ambiente já utilizadas no script exploratório do Mercado Livre (`ML_APP_ID`, `ML_CLIENT_SECRET`, `ML_REDIRECT_URI`, `ML_PKCE`) permanecem compatíveis.
- Caminhos locais e nomes de arquivos devem usar somente caracteres ASCII. Na documentação textual e na interface do n8n, usar acentos normalmente.
- Não introduzir novos nomes em inglês quando existir uma alternativa clara em português.

## Git

Criar branches curtas como `funcionalidade/descobertaOfertas`, `correcao/paginacaoCatalogo` ou `documentacao/revisarInstalacao`. Mensagens de commit e descrições de PR devem ser em português. Preservar a sintaxe técnica de comandos Git e APIs.
