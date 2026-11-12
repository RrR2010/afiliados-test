# Roadmap

## Foundation (this change)
- [x] Architecture and n8n versioning instructions
- [x] Local environment variable inventory with blank secrets
- [x] Initial project SQLite schema
- [ ] Inspect installed n8n version, packaging, plugins/nodes and permissions
- [ ] Select n8n-to-SQLite bridge if no suitable maintained node is installed

## MVP 1: real observations
- [ ] WF-01 Mercado Livre discovery (authorized catalog + commercial-offer endpoints; bounded scans)
- [ ] WF-02 price observation storage (transactional, history retained)
- [ ] Reasonable API retries; 404 No winners found means no listings, not fatal
- [ ] Tests using mocked API payloads

## MVP 2: reviewable offers
- [ ] WF-03 scoring with transparent reasons and insufficient-history flag
- [ ] Human shortlist and manual additions
- [ ] WF-04 approval and manual affiliate link generation/validation
- [ ] WF-05 WhatsApp preview and template
- [ ] WF-06 send to operator; verify webhook statuses and manual forwarding

## Later
- [ ] Coupon verification, multiple marketplaces, product matching/LLM
- [ ] Historical comparisons across Black Friday seasons

## Decisions to confirm
- n8n version and install method (Docker vs native)
- SQLite adapter vs suitable node
- Workflow manual export vs plan-supported native Git
- Production sender and message templates
- Backup policy and human approval UI
