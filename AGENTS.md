# Collaboration agreement for AI/local agents

Prefer visual n8n nodes over scripts. GitHub PRs are the versioned source of truth; n8n remains the live visual editor.

1. Inspect current branch, git status, latest main and open PRs before editing.
2. Create a dedicated short-lived branch from updated main; never push to main directly.
3. One task per PR; coordinate ownership of workflow exports to prevent concurrent overwrites.
4. When editing n8n canvases, export sanitized workflow JSON into workflows/ and record the n8n version and manual settings in the PR. No secrets, credentials, local user data or pinned customer payloads.
5. Use English for code, schemas, comments and docstrings; Portuguese is fine for operator-facing text.
6. Do not trigger real WhatsApp sends, pay-per-use APIs, mass scans or destructive changes without approval. Mock external responses first.
7. Human approval, variant verification and a validated affiliate URL are hard gates before sending affiliate content.
8. Never claim an advertised original price proves a real discount; represent insufficient price history honestly.
9. At handoff report branch, PR, tests, changed files, manual n8n steps and any unresolved blockers.

First agent assignment: read-only inspect local n8n installation type/version, available nodes for SQLite, availability of workflow export and n8n API/MCP. Report only; do not edit or run workflows.
