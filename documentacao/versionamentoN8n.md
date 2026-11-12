# Versionamento dos fluxos visuais do n8n

## Conceito

O **editor do n8n** contém a versão editável e executável do fluxo. O **GitHub** guarda a cópia exportada e revisada em JSON. Editar um fluxo no n8n não atualiza o GitHub; fazer `git pull` não instala nem ativa um fluxo.

O controle de versões nativo do n8n depende da edição e do plano disponível. Até confirmar as condições da instalação, usar exportação/importação manual com Git.

## Procedimento

1. Criar uma branch a partir da `main` atualizada, antes das alterações.
2. Editar e salvar o fluxo visualmente no n8n local.
3. Exportar o JSON completo, sem valores de credenciais, dados pessoais ou exemplos fixados com informações reais.
4. Salvar o JSON na pasta `fluxos/`, seguindo [convenções](convencoes.md); exemplo: `F01DescobrirOfertasMercadoLivre.json`.
5. Criar um commit em português e enviar a branch para o GitHub.
6. Abrir um pull request (PR) com descrição, versão do n8n, testes e passos de importação.
7. Após aprovação e merge, atualizar a cópia local e importar a versão revisada, verificando credenciais e ativação.
8. Não editar o mesmo fluxo simultaneamente em duas máquinas/agentes.

### Comandos Git de exemplo

```powershell
git switch main
git pull --ff-only
git switch -c funcionalidade/descobertaOfertas
git add fluxos/ documentacao/
git commit -m "feat: adicionar descoberta visual de ofertas"
git push -u origin funcionalidade/descobertaOfertas
```

Ao clonar no PowerShell, copiar o arquivo de exemplo com `Copy-Item .env.example .env`.

## Segurança e persistência

- O JSON do fluxo não pode conter segredos, contatos reais da cliente, dados pessoais de execuções ou links privados de teste.
- As credenciais são configuradas na instância local do n8n, não em Git.
- O arquivo `.env.example` é um inventário; o n8n **não lê automaticamente** o `.env` do repositório.
- O banco interno do n8n e o SQLite do TomeOferta são independentes e não entram no repositório.
- Uma exportação é um retrato do fluxo em determinada data, não uma sincronização automática.
