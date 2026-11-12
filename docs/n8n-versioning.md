# How to version a visual n8n project

Git stores the **exported definition** of a workflow; n8n stores the editable and running copy. Git pull is not automatic deployment.

## Free-compatible manual approach

1. Use the local n8n editor and save the workflow.
2. Export its workflow JSON; verify no real credentials, phone numbers, pinned customer payloads or private webhook URLs are in the file.
3. Save as workflows/WF-xx-name.json and document required credentials in the PR.
4. Use Git: git switch main && git pull --ff-only && git switch -c feat/task-name
5. Commit exported JSON and docs, push your task branch, then open a PR.
6. After merging, pull the repo on the other PC and import the approved JSON back to n8n; rebind local credentials and activation.

Use a single editor per workflow change. Never silently overwrite n8n's local working copy.

## Notes

n8n has native Git source control on eligible plans, but do not assume the client's installation includes it or use it alongside manual exports without an explicit migration plan. Credentials live in n8n, not in workflow JSON. The project's .env.example is only a configuration checklist; it is not automatically loaded by n8n.

Windows PowerShell initial copy: Copy-Item .env.example .env

Do not commit n8n's internal database, project SQLite data or backups.
