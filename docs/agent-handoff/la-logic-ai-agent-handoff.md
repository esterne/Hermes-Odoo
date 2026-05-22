# LA Logic Odoo AI Agent Handoff

Last updated: 2026-05-22

This document is intended for a separate AI agent that will administer the LA Logic Odoo database. It contains operational context, repo pointers, and safe workflows. It intentionally excludes passwords, API keys, token prefixes, database dumps, customer records, and private business data.

## Start here

1. Read this handoff first.
2. Read the exported reusable skill at [`skills/odoo-administration/SKILL.md`](../../skills/odoo-administration/SKILL.md).
3. Read the current project docs:
   - [`docs/decisions/two-company-odoo-decisions.md`](../decisions/two-company-odoo-decisions.md)
   - [`docs/config/module-baseline.md`](../config/module-baseline.md)
   - [`docs/config/la-logic-website-placeholder.md`](../config/la-logic-website-placeholder.md)
4. If you need to change live Odoo state, get credentials/API keys from Erwin through a secure channel. Do not expect secrets to exist in this repository.

## Live environment summary

| Item | Value |
|---|---|
| Odoo edition | Odoo 19 Community Edition |
| Host hardware | Zimaboard / ZimaOS environment |
| Primary public Simian domain | `https://www.simiansyndicate.co.za` |
| LA Logic public domain | `https://www.lalogic.co.za` |
| Direct Odoo endpoint observed during setup | `http://eshost.dyndns.info:8069` |
| Reverse proxy | Nginx Proxy Manager / OpenResty-style proxying |
| LA Logic database name | `lalogic` — exact lowercase spelling |
| Simian database name | `SimianSyndicate` — exact mixed-case spelling |
| LA Logic company name | `LA Logic` |
| Country/currency | South Africa / ZAR |

Important: use the exact database name `lalogic`. Do not use `LALogic`, `la_logic`, or any other variant.

## Security boundary

- This repo must not contain API keys, passwords, `.env` files, bearer tokens, session cookies, database dumps, customer records, or private accounting data.
- Any automation user/API key should be created or rotated inside Odoo and stored only in the administering agent's secure secret store.
- If Erwin provides a temporary password, use it only for the immediate task and recommend rotating it in the web UI afterward.
- Confirm before destructive actions such as deleting records, uninstalling modules, resetting databases, changing mail routing, or modifying proxy hosts.

## Current topology

Simian Syndicate and LA Logic are intentionally separated into two Odoo databases on the same Odoo host:

- `SimianSyndicate` for Simian Syndicate
- `lalogic` for LA Logic

Reason: LA Logic is a financial/compliance-oriented company, so data isolation, auditability, separate backups/restores, and clean access boundaries matter more than the convenience of a single multi-company database.

## Current LA Logic module baseline

Installed in `lalogic`:

| App | Technical module | Purpose |
|---|---:|---|
| Contacts | `contacts` | Clients, vendors, companies, contacts |
| Invoicing / Accounting | `account` | Client invoices, payments, journals, accounting setup |
| South Africa Accounting | `l10n_za` | South African localization / ZAR accounting basis |
| CRM | `crm` | Client lead/opportunity pipeline |
| Sales | `sale_management` | Quotations and service sales orders |
| Project | `project` | Client/compliance work tracking |
| Website | `website` | Simple public placeholder site |

Deferred unless explicitly needed: POS, Manufacturing, Repairs, Fleet, and Enterprise-only apps such as Documents/Sign/Helpdesk unless the deployment gains those modules separately.

## Public website state

The LA Logic homepage is a custom Odoo Website placeholder page in the `lalogic` database.

Current page characteristics:

- Stripe-inspired professional/financial design.
- Default Odoo header/footer chrome is visually hidden for the placeholder.
- Footer email address was removed.
- The `Contact LA Logic` hero button was removed.
- The hero currently keeps only the `View focus areas` button.

Primary documentation: [`docs/config/la-logic-website-placeholder.md`](../config/la-logic-website-placeholder.md).

## Routing model

Odoo must select the database before it can read Website records, company website fields, or `web.base.url`. Therefore, Odoo Website domain settings alone do not route public hostnames to databases on a multi-database host.

The chosen routing pattern is one Nginx Proxy Manager proxy host per public domain, each forwarding to the same Odoo upstream but setting a database-selection header.

For LA Logic:

```nginx
proxy_set_header X-Odoo-Database lalogic;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto https;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
```

For Simian Syndicate:

```nginx
proxy_set_header X-Odoo-Database SimianSyndicate;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto https;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
```

Verify the LA Logic proxy host does not accidentally set `SimianSyndicate`, and the Simian proxy host does not accidentally set `lalogic`.

## Read-only verification commands

These are safe probes and do not require secrets for basic availability checks.

```bash
curl -sS https://www.lalogic.co.za/web/version
curl -sS -H 'Content-Type: application/json' -d '{}' https://www.lalogic.co.za/web/database/list
curl -k -L https://www.lalogic.co.za/ | grep -E 'database/selector|<title>|LA Logic'
curl -k -L https://www.lalogic.co.za/ -H 'X-Odoo-Database: lalogic' | grep -E '<title>|LA Logic|Contact LA Logic'
```

Expected behavior after routing is correct:

- `https://www.lalogic.co.za/` renders the LA Logic site without showing the database selector.
- A forced-header request with `X-Odoo-Database: lalogic` renders LA Logic content.
- `Contact LA Logic` should not appear as a hero button on the placeholder page.

## Authenticated API guidance

Preferred API for automation: Odoo 19 JSON-2 endpoints.

Base shape:

```bash
curl -i -X POST 'https://www.lalogic.co.za/json/2/res.users/context_get' \
  -H 'Authorization: bearer <api-key-from-secure-store>' \
  -H 'Content-Type: application/json' \
  -H 'X-Odoo-Database: lalogic' \
  -d '{}'
```

Expected with a valid API key: `200 OK` and a JSON context response.

See [`skills/odoo-administration/SKILL.md`](../../skills/odoo-administration/SKILL.md) for:

- JSON-2 call shape
- legacy web session fallback
- Odoo 19 API key identity-check pitfall
- module install pattern
- accounting access verification
- Nginx Proxy Manager routing caveats

## Known Odoo 19 pitfalls from this setup

1. JSON-2 call shape is not the same as `/web/dataset/call_kw`. Do not blindly send `args`/`kwargs` wrappers to JSON-2 unless the endpoint expects them.
2. Some self-hosted Odoo 19 setups return a successful `/web/session/authenticate` result without setting a `session_id` cookie. If `/web/dataset/call_kw` then says `Odoo Session Expired`, use a normal `/web/login?db=lalogic` form login with CSRF to establish the cookie.
3. `res.users` group membership may be exposed as `group_ids`, not older `groups_id` examples.
4. `account` is the technical module for Community Invoicing/Accounting.
5. After installing Accounting/Invoicing, the automation user may need `Accounting / Administrator` or another appropriate accounting group before it can inspect accounting models.
6. Module operations can fail transiently while Odoo is processing a scheduled action. Wait and retry once before treating it as permanent failure.
7. `web.base.url` and company website fields do not select databases; proxy/dbfilter routing must happen before database records are available.

## How to continue safely

Before changing anything:

1. Pull the latest repo.
2. Read the handoff and exported skill.
3. Verify the target database with read-only calls.
4. Confirm scope with Erwin for changes that affect accounting, users, mail, proxy routing, module installation, or public website content.
5. Use a dedicated automation user and API key supplied through a secure channel.
6. Document durable changes in this repo without secrets.
7. Commit and push documentation after changes.

## Documentation map

- Project overview: [`README.md`](../../README.md)
- Topology and decisions: [`docs/decisions/two-company-odoo-decisions.md`](../decisions/two-company-odoo-decisions.md)
- Module baseline: [`docs/config/module-baseline.md`](../config/module-baseline.md)
- LA Logic website placeholder: [`docs/config/la-logic-website-placeholder.md`](../config/la-logic-website-placeholder.md)
- Exported reusable skill: [`skills/odoo-administration/SKILL.md`](../../skills/odoo-administration/SKILL.md)
- Skill references:
  - [`skills/odoo-administration/references/module-baseline-installation.md`](../../skills/odoo-administration/references/module-baseline-installation.md)
  - [`skills/odoo-administration/references/odoo-multidb-website-routing.md`](../../skills/odoo-administration/references/odoo-multidb-website-routing.md)
  - [`skills/odoo-administration/references/odoo-website-placeholder.md`](../../skills/odoo-administration/references/odoo-website-placeholder.md)
  - [`skills/odoo-administration/references/odoo19-simian-session-notes.md`](../../skills/odoo-administration/references/odoo19-simian-session-notes.md)

## Explicit non-goals for this repo

- Do not use this repo as a password vault.
- Do not commit generated API keys.
- Do not commit customer/accounting data exports.
- Do not assume that the presence of a workflow in this repo authorizes live changes; Erwin still controls live credentials and scope.
