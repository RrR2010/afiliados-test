# Architecture: n8n-first TomeOferta

The client runs n8n locally and wants to see each step on the canvas. Separate visual workflows should own orchestration; only specialized logic gets code.

## Pipeline

| Workflow | Responsibility | Initial implementation |
| --- | --- | --- |
| WF-01 Discovery | Find listings from authorized APIs/feeds; limit and paginate scans | n8n HTTP Request + loops + Wait |
| WF-02 Persistence | Normalize and store immutable observations | n8n + narrowly scoped SQLite adapter if needed |
| WF-03 Scoring | Rank credible opportunities; shortlist 2-3 | n8n rules and explicit reason fields |
| WF-04 Review & Affiliate | Human verifies product, conditions, coupon and official affiliate link | Manual approval with persisted state |
| WF-05 Compose | Prepare image, description, price conditions and affiliate disclosure | n8n Set/Edit Fields and preview |
| WF-06 Operator WhatsApp | Meta Cloud API message to operator only, webhook receipt, manual group forward | n8n HTTP Request, human forwarding |

Avoid building six production workflows before inspecting the installed n8n. No workflow is live in this initial repository.

## Data design

SQLite is the **TomeOferta project database**; it must not share the n8n internal application DB. See db/schema.sql. Products are canonical identities, listings belong to specific marketplaces/sellers, price observations are timestamped and immutable, candidates carry explainable rankings, and publications carry delivery status.

A same-model comparison must check variations (storage, size, color, import condition, fragrance volume, warranty). Future LLM matching is optional; strong identifier mismatches must not be overridden.

Scoring distinguishes marketplace “original price” from observed history. Insufficient history = unknown, never “verified discount”. Coupon value is only included when eligibility is validated.

## Reliability and security

- The PC must remain powered on for schedules; configure local backup/restore and prevent unexpected sleep.
- Keep SQLite backups **outside Git** and test restorations.
- Preserve Meta OAuth credentials and the n8n encryption key securely, outside the repository.
- Meta API acceptance (wamid) is distinct from confirmed delivery; inspect webhook statuses.
- Free-form WhatsApp messages depend on the active customer-service window; use an approved template outside it where required.
- Never send directly to a group; operator reviews and forwards manually.
- A local SQLite helper, if necessary, should run on localhost with authentication and prepared statements; do not expose a generic SQL execution endpoint.
- Respect marketplace terms and API rate limits; do not use evasive scraping.
