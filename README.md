# TomeOferta

Sistema de descoberta, comparação, histórico de preços e curadoria de ofertas para divulgação assistida no WhatsApp. **O n8n local é o orquestrador visual**; scripts entram somente quando o editor não atender à necessidade.

## Processo previsto

1. **Descobrir ofertas** em APIs oficiais ou fontes autorizadas, começando pelo Mercado Livre.
2. **Guardar histórico** de anúncios e observações de preço no banco SQLite do TomeOferta.
3. **Avaliar e selecionar** as duas ou três oportunidades mais interessantes com pontuação explicável e possibilidade de inclusão manual.
4. **Revisar e gerar o link de afiliado** manualmente, até existir integração autorizada para automatizar a geração.
5. **Montar a mensagem** com imagem, preço, condições, texto e indicação publicitária.
6. **Enviar ao operador** via API oficial da Meta; o encaminhamento ao grupo de participantes é feito manualmente.

O preço anterior informado pela loja não comprova um desconto real. Cupons e condições de compra também devem ser verificados.

## Instalação inicial

1. Clonar o repositório: `git clone https://github.com/RrR2010/afiliados-test.git`.
2. No PowerShell, copiar `.env.example` para `.env` com `Copy-Item .env.example .env`.
3. Preencher apenas as variáveis necessárias. Configurar tokens e segredos preferencialmente nas **Credenciais** do n8n; nunca enviá-los ao Git. O n8n **não carrega automaticamente** o `.env` desta pasta.
4. Identificar a versão e o método de instalação do n8n (Docker, npm ou outro) antes de definir a comunicação com SQLite.
5. Criar e testar os fluxos visualmente. Exportar versões revisadas em JSON, sem dados pessoais ou segredos, para a pasta `fluxos/`.

## Estrutura

- [Convenções de nomenclatura](documentacao/convencoes.md)
- [Arquitetura e etapas](documentacao/arquitetura.md)
- [Versionamento do n8n](documentacao/versionamentoN8n.md)
- [Plano de evolução](documentacao/planoDeEvolucao.md)
- [Orientações aos agentes](AGENTS.md)
- [Esquema SQLite inicial](banco/esquema.sql)
- [Fluxos planejados](fluxos/README.md)

## Situação atual

**Somente estrutura inicial e documentação.** Ainda não existem fluxos n8n executáveis, automações programadas ou envio de WhatsApp instalado por este repositório.

**Fontes de verdade:** GitHub para definições versionadas; n8n local para execução e credenciais; SQLite do TomeOferta para observações e histórico, com cópias de segurança externas ao Git.
