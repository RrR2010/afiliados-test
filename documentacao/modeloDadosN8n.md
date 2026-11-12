# Modelo inicial de dados — n8n Data Tables

## Decisão

No MVP, usar **Data Tables nativas do n8n** para manter o projeto visual e sem pacotes comunitários. A instância local instalada via npm (n8n 2.47.3) confirmou o nó `n8n-nodes-base.dataTable` v1.1 e importação/exportação CSV pela interface. Ainda **não** foram feitos testes de gravação, leitura ou exportação real.

As Data Tables fazem parte do armazenamento gerenciado pelo n8n. **Não** criar agora o banco SQLite do TomeOferta. O arquivo `banco/esquema.sql` fica guardado apenas como desenho futuro de migração, não como esquema implantado.

## Convenção

Nomes de tabelas em português, sem acentos, e nomes de campos em `camelCase`. As colunas devem usar somente tipos confirmados pelo agente local: `string`, `number`, `boolean` e `date`. Os identificadores de negócio são campos próprios, não dependem do ID interno da Data Table.

## Quatro tabelas para o MVP

### `produtos`

| Campo | Tipo | Uso |
| --- | --- | --- |
| `idProduto` | string | Identificador estável gerado pela aplicação; ex.: `ML:MLB22246671` |
| `nomeProduto` | string | Título normalizado |
| `marca` | string | Marca quando conhecida |
| `modelo` | string | Modelo quando conhecido |
| `categoria` | string | Categoria quando conhecida |
| `monitorado` | boolean | Participa das coletas periódicas |

### `historicoPrecos`

| Campo | Tipo | Uso |
| --- | --- | --- |
| `idObservacao` | string | Identificador único de cada observação |
| `idProduto` | string | Referência lógica ao produto |
| `idAnuncio` | string | Identificador de anúncio com prefixo da plataforma |
| `plataforma` | string | Ex.: `mercadoLivre` |
| `precoCentavos` | number | Preço anunciado, em centavos inteiros |
| `precoOriginalCentavos` | number | Preço anterior *informado pela plataforma*, se existente |
| `freteCentavos` | number | Somente se conhecido; vazio não equivale a frete grátis |
| `coletadoEm` | date | Data/hora da observação (preferir UTC) |
| `origem` | string | Endpoint ou feed autorizado |
| `condicoesJson` | string | Condições relevantes, serializadas em JSON |

### `ofertasCandidatas`

| Campo | Tipo | Uso |
| --- | --- | --- |
| `idOferta` | string | Identificador da candidatura |
| `idObservacao` | string | Origem da avaliação |
| `idAnuncio` | string | Oferta do vendedor |
| `pontuacao` | number | Pontuação calculada |
| `justificativa` | string | Texto de auditoria da avaliação |
| `situacao` | string | `pendente`, `aprovada` ou `rejeitada` |
| `urlAnuncio` | string | URL original ou reconstruída, a validar |
| `urlAfiliado` | string | Link comissionável verificado e inserido pela pessoa responsável |
| `revisadoEm` | date | Data da decisão humana |

### `publicacoes`

| Campo | Tipo | Uso |
| --- | --- | --- |
| `idPublicacao` | string | Identificador próprio |
| `idOferta` | string | Candidatura aprovada |
| `textoMensagem` | string | Texto produzido |
| `urlImagem` | string | Imagem, se validada |
| `situacao` | string | `rascunho`, `aprovada`, `submetida`, `enviada`, `entregue`, `falha` |
| `idMensagemMeta` | string | ID retornado pela API Meta |
| `enviadoEm` | date | Data do envio |

## Regras

1. `historicoPrecos` é **acrescentado**, nunca sobrescrito em uma nova coleta; evitar duplicatas por `idObservacao`. O n8n não impõe automaticamente unicidade desses campos próprios: verificar antes de inserir.
2. `produtos` pode usar atualização ou inclusão condicionada por `idProduto`.
3. Data Tables não substituem validações de integridade relacional: verificar referências nos fluxos.
4. Nunca considerar cupom sem regras confirmadas como desconto efetivo. Para o MVP, condições e cupons podem permanecer em `condicoesJson`; criar tabela própria quando necessário.
5. Manter observações suficientes para reconstruir o histórico. Não confundir valores vazios com zero.
6. Em migrações futuras, conferir contagens, IDs, datas, referências, preços, exportação completa e ausência de duplicatas antes de desativar as tabelas.
7. Realizar backup da instalação n8n e exportações periódicas. CSV nativo pode não usar `;` e UTF-8 com BOM: converter em fluxo específico se necessário.
8. Avaliar o limite efetivo de armazenamento no ambiente da cliente; não pressupor capacidade ilimitada.

## Próximo teste local autorizado

Criar **somente uma tabela descartável** com dados fictícios, executar inserção/leitura/atualização/exportação e removê-la após confirmação e autorização. Não colocar credenciais ou dados reais nos testes. Após validação, criar as quatro tabelas e exportar o primeiro fluxo para `fluxos/`.
