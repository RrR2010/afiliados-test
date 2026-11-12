# TomeOferta

Sistema de descoberta, comparação, histórico de preços e curadoria de ofertas para divulgação assistida no WhatsApp. **O n8n local é o orquestrador visual**; scripts entram somente quando o editor não atender à necessidade.

## Processo previsto

1. **Descobrir ofertas** em APIs oficiais ou fontes autorizadas, começando pelo Mercado Livre.
2. **Guardar histórico** de anúncios e observações de preço em **Data Tables nativas do n8n**.
3. **Avaliar e selecionar** as duas ou três oportunidades mais interessantes, com pontuação explicável e possibilidade de inclusão manual.
4. **Revisar e gerar o link de afiliado** manualmente, até existir integração autorizada para automatizar a geração.
5. **Montar a mensagem** com imagem, preço, condições, texto e identificação publicitária.
6. **Enviar ao operador** via API oficial da Meta; a pessoa responsável encaminha manualmente ao grupo.

O preço anterior informado pela loja não comprova um desconto real. Cupons e condições de compra precisam ser verificados.

## Instalação inicial

1. Clonar: `git clone https://github.com/RrR2010/afiliados-test.git`.
2. No PowerShell, copiar `.env.example` para `.env` com `Copy-Item .env.example .env`.
3. Configurar tokens e segredos preferencialmente nas **Credenciais** do n8n; nunca enviá-los ao Git. O n8n **não carrega automaticamente** o `.env` desta pasta.
4. A instalação verificada é n8n 2.47.3 via npm, com Data Tables disponíveis. Antes de configurar a máquina da cliente, validar versão e permissões dela.
5. Criar e testar fluxos visualmente e exportar JSON revisado, sem segredos, para `fluxos/`.

## Estrutura e documentos

- [Convenções](documentacao/convencoes.md)
- [Arquitetura](documentacao/arquitetura.md)
- [Modelo de dados no n8n](documentacao/modeloDadosN8n.md)
- [Versionamento](documentacao/versionamentoN8n.md)
- [Plano de evolução](documentacao/planoDeEvolucao.md)
- [Agentes](AGENTS.md)
- [Esquema SQLite futuro](banco/esquema.sql)
- [Fluxos planejados](fluxos/README.md)

## Situação atual

**Arquitetura/documentação, sem execução operacional.** As Data Tables foram detectadas na instalação local, mas nenhuma tabela real ou fluxo do TomeOferta foi criado ou testado.

**Fontes de verdade:** GitHub para definições versionadas; n8n para fluxos/credenciais/dados do MVP; exportações e backups locais fora do Git para recuperação e futura migração.
