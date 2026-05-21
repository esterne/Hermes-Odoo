# Two-Company Odoo From-Scratch Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task once deployment and company-structure decisions are confirmed.

**Goal:** Build a clean Odoo 19 Community installation path for two companies: Simian Syndicate and LA Logic.

**Architecture:** Start with the existing self-hosted Odoo 19 Community deployment on the Zimaboard, then keep Simian Syndicate and LA Logic in separate databases with separate users/API keys, accounting setup, backups, and data boundaries.

**Tech Stack:** Odoo 19 Community, PostgreSQL, Docker Compose or native service deployment, JSON-2 API, GitHub repo `esterne/Hermes-Odoo`.

---

## Current Repo Baseline

This repo currently contains Odoo 19 Community API research, integration notes, and examples. It does not yet contain deployment automation, environment templates, company configuration manifests, or operational runbooks.

Relevant existing docs:

- `README.md` — repo scope and Odoo 19 Community API assumptions
- `docs/11-deployment-caveat-hosted-vs-self-hosted.md` — self-hosted vs hosted API caveats
- `docs/06-community-models.md` — Community modules and business models
- `docs/09-security-checklist.md` — integration security checklist

## First Design Decision: One Database or Two?

### Option A — One Odoo database, two companies

Use when:

- Simian Syndicate and LA Logic should be managed by the same admin team.
- Shared users need to switch companies inside one Odoo session.
- Shared customers/vendors/products are acceptable or useful.
- Inter-company transactions may matter later.

Pros:

- Easier user management.
- Easier consolidated reporting.
- Less infrastructure and maintenance.
- Odoo multi-company is a core workflow.

Cons:

- We must be very careful with company rules, record visibility, accounting configuration, and defaults.
- Accidental cross-company data exposure is possible if permissions are sloppy.

### Option B — One Odoo instance, two separate databases

Use when:

- Simian Syndicate and LA Logic need strong operational separation.
- Backups/restores should be independent.
- Different users, apps, chart of accounts, or compliance settings are expected.
- The businesses should not share records by default.

Pros:

- Clean isolation.
- Safer for unrelated operations.
- Easier to archive/move one company later.

Cons:

- More admin duplication.
- Cross-company reporting/integration requires external aggregation.
- Users may need separate accounts/API keys per database.

### Recommended starting assumption

Decision confirmed by Erwin: **Option B: two databases**.

Reason: from-scratch business systems are easier to keep clean when legal/operational entities are isolated. If we later discover they need shared operations, we can still plan a multi-company database deliberately instead of accidentally mixing data.

## Implementation Phases

### Phase 0 — Scope confirmation

**Objective:** Avoid building the wrong Odoo shape.

Confirm:

1. Deployment target: local Mac dev, VPS, Docker host, Odoo.sh, or other.
2. Odoo edition/version: assume Odoo 19 Community unless changed.
3. Company topology: confirmed as two separate databases.
4. Required first apps per company: CRM, Sales, Invoicing/Accounting, Inventory, Purchase, Project, Website/eCommerce, POS, Manufacturing.
5. Accounting localization and currency: likely South Africa / ZAR unless changed.
6. Email/domain requirements for outgoing mail and aliases.
7. Integration/API requirements and bot users.
8. Backup/restore expectations.

Verification:

- A short decisions file exists at `docs/decisions/two-company-odoo-decisions.md`.
- No secrets or credentials are committed.

### Phase 1 — Add reproducible deployment scaffold

**Objective:** Make a fresh Odoo environment boot repeatably.

Files to create:

- `deploy/docker-compose.yml`
- `deploy/odoo.conf.example`
- `deploy/.env.example`
- `deploy/README.md`
- `scripts/healthcheck.sh`
- `scripts/init-databases.sh`

Expected behavior:

- PostgreSQL runs as a named service.
- Odoo runs as a named service.
- Volumes are named and documented.
- `.env.example` contains placeholders only.
- Real `.env`, database passwords, admin passwords, API keys, and backups are gitignored.

Verification commands:

```bash
docker compose -f deploy/docker-compose.yml config
docker compose -f deploy/docker-compose.yml up -d
curl -sS http://localhost:8069/web/version
```

Expected:

- Compose config validates.
- Odoo web endpoint responds.
- No credentials are present in git diff.

### Phase 2 — Database/company initialization runbook

**Objective:** Document exact steps to initialize Simian Syndicate and LA Logic from scratch.

Files to create:

- `docs/runbooks/initial-install.md`
- `docs/runbooks/create-company-databases.md`
- `docs/runbooks/backup-restore.md`

Confirmed two-database topology:

- Database 1: `SimianSyndicate` — existing live Simian Syndicate database
- Database 2: `LALogic` — planned LA Logic database

For one multi-company database topology:

- Database: `hermes_odoo`
- Companies:
  - `Simian Syndicate`
  - `LA Logic`

Verification:

- Fresh install can be repeated from the runbook.
- `/web/version` works after setup.
- Database manager access is protected or disabled appropriately for production.

### Phase 3 — Module baseline per company

**Objective:** Install only the modules needed for day-one operations.

Candidate module groups:

- Base/company/users/contacts
- CRM
- Sales
- Invoicing/accounting
- Inventory
- Purchase
- Project
- Website/eCommerce only if needed
- POS only if needed
- Manufacturing only if needed

Files to create:

- `docs/config/module-baseline.md`
- `docs/config/company-checklists/simian-syndicate.md`
- `docs/config/company-checklists/la-logic.md`

Verification:

- Module list is explicit.
- Each module has a reason.
- Unneeded modules are deferred.

### Phase 4 — Security, users, and API access

**Objective:** Establish safe admin/user/API access before integrations.

Files to create:

- `docs/security/user-roles.md`
- `docs/security/api-users.md`
- `docs/security/production-hardening.md`

Rules:

- No shared admin account for integrations.
- Dedicated bot/API user per database or per company.
- Minimum permissions for API users.
- API keys are generated in Odoo UI and never committed.
- JSON-2 is the default API path for Odoo 19 self-hosted Community.

Verification:

```bash
curl -sS "$ODOO_URL/web/version"
curl -i -X POST "$ODOO_URL/json/2/res.users/context_get" \
  -H "Authorization: bearer <api-key>" \
  -H "Content-Type: application/json" \
  -H "X-Odoo-Database: <database-name>" \
  -d '{}'
```

Expected:

- `/web/version` returns version info.
- JSON-2 returns `200 OK` for valid API key/context.
- Invalid API key returns `401`/`403`.

### Phase 5 — Accounting/localization setup

**Objective:** Configure accounting correctly rather than retrofitting later.

Files to create:

- `docs/config/accounting-localization.md`
- `docs/config/tax-and-currency.md`

Confirm:

- Country/jurisdiction.
- Base currency.
- VAT/tax registration status.
- Chart of accounts template.
- Invoice numbering expectations.
- Bank accounts/journals.

Verification:

- Test customer invoice can be created in draft.
- Test invoice can be posted only after accounting setup is reviewed.
- Tax behavior is correct for a sample transaction.

### Phase 6 — Data migration/import templates

**Objective:** Prepare clean import paths for contacts, products, opening balances, and inventory.

Files to create:

- `imports/templates/contacts.csv`
- `imports/templates/products.csv`
- `imports/templates/vendors.csv`
- `imports/templates/opening-inventory.csv`
- `docs/runbooks/data-import.md`

Rules:

- Keep source import files out of git if they contain private/customer/business data.
- Commit only empty templates and validation docs.
- Use Odoo import UI or API scripts depending on data volume.

Verification:

- A tiny non-private sample import succeeds in staging/dev.
- Required fields are documented.

### Phase 7 — Operations runbooks

**Objective:** Make the install maintainable.

Files to create:

- `docs/runbooks/start-stop.md`
- `docs/runbooks/update-odoo.md`
- `docs/runbooks/backup-restore.md`
- `docs/runbooks/logs-and-troubleshooting.md`
- `docs/runbooks/disaster-recovery.md`

Verification:

- Backup can be created.
- Restore can be tested into a disposable database.
- Logs can be retrieved.
- Odoo service restart is documented.

## Initial Work Breakdown

### Task 1: Record decisions

Create `docs/decisions/two-company-odoo-decisions.md` with a table of pending/confirmed choices.

Commit message:

```bash
git commit -m "docs: add two-company Odoo decision log"
```

### Task 2: Add deployment scaffold

Create Docker Compose, config example, env example, and deployment README.

Commit message:

```bash
git commit -m "feat: add Odoo deployment scaffold"
```

### Task 3: Add initial install runbook

Create step-by-step fresh install runbook for selected topology.

Commit message:

```bash
git commit -m "docs: add Odoo initial install runbook"
```

### Task 4: Add company setup checklists

Create one checklist per company.

Commit message:

```bash
git commit -m "docs: add company setup checklists"
```

### Task 5: Add security/API access runbook

Create safe user/API setup docs with JSON-2 verification commands.

Commit message:

```bash
git commit -m "docs: add Odoo security and API runbooks"
```

## Open Questions

1. Where should LA Logic be exposed publicly: same host with direct `:8069` plus database selector, separate subdomain, or internal/admin-only at first?
2. Where should the first deployment run: existing Zimaboard only, local dev mirror, VPS, Docker host, Odoo.sh, or something else?
3. Is Odoo 19 Community confirmed, or should we use the latest stable packaged version available through Docker at implementation time?
4. Which apps are needed first for each company?
5. Is the accounting jurisdiction South Africa with ZAR as base currency for both companies?
6. Do both companies need email sending/receiving from Odoo immediately?
7. Any existing data to import: contacts, products, invoices, inventory, bank statements?
8. Who needs admin/user access on day one?

## Non-Negotiables

- Do not commit real credentials, API keys, database passwords, admin passwords, exports, backups, or private customer data.
- Use `.env.example` placeholders only.
- Keep deployment repeatable.
- Verify JSON-2 availability on the actual deployment before building integrations against it.
- Prefer simple operational docs over clever automation until the basic install is stable.
