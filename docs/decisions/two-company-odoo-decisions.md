# Two-Company Odoo Decisions

Last updated: 2026-05-21

## Current live instance

| Item | Current value | Status |
|---|---:|---|
| Hostname | `eshost.dyndns.info` | Confirmed reachable |
| Business website domain | `www.simiansyndicate.co.za` | Confirmed routing through Nginx Proxy Manager to Odoo over HTTPS |
| Public HTTPS root | `https://eshost.dyndns.info/` | Reaches proxy/default site, not Odoo paths |
| Public HTTP website root | `http://www.simiansyndicate.co.za/` | Redirects to `https://www.simiansyndicate.co.za/` |
| Public HTTPS website root | `https://www.simiansyndicate.co.za/` | Valid Let's Encrypt certificate; serves Odoo website |
| Odoo public URL | `https://www.simiansyndicate.co.za` | Confirmed Odoo via `/web/version` |
| Odoo direct HTTP URL | `http://eshost.dyndns.info:8069` and `http://www.simiansyndicate.co.za:8069` | Confirmed Odoo direct access |
| Odoo host hardware | Zimaboard | User-confirmed |
| Odoo edition | Odoo Community Edition 19 | User-confirmed; version endpoint reports `19.0-20260504` |
| Odoo version | `19.0-20260504` | Confirmed via `/web/version` |
| Odoo server | `Werkzeug/3.0.1 Python/3.12.3` | Confirmed from response headers |
| Database list | `SimianSyndicate` | Confirmed via `/web/database/list` |
| Website state | Basic Odoo website template | User-confirmed; Odoo template pages visible over HTTPS |
| Database list | `SimianSyndicate` | Confirmed through `https://www.simiansyndicate.co.za/web/database/list` |
| JSON-2 endpoint | `/json/2/res.users/context_get` | Confirmed present over HTTPS; unauthenticated request returns `401` with API-key message when `X-Odoo-Database: SimianSyndicate` is provided |
| Remaining proxy/config note | Odoo generated metadata still exposes `http://...` canonical/og URLs during probe | Likely needs Odoo `proxy_mode` / `web.base.url` review after proxy changes |

## Authenticated read-only inspection

Checked through the Odoo web session on 2026-05-21 with temporary admin access.

Findings:

- Logged in as administrator user `erwin@simiansyndicate.co.za` on database `SimianSyndicate`.
- Odoo session confirms user is admin, timezone is `Africa/Johannesburg`, and current company is `Simian Syndicate`.
- `ir.config_parameter:web.base.url` is currently `http://www.simiansyndicate.co.za` and should be changed to `https://www.simiansyndicate.co.za` once proxy headers/proxy mode are correct.
- No `web.base.url.freeze` parameter is currently set.
- Company `Simian Syndicate` is configured with country `South Africa`, currency `ZAR`, email `erwin@simiansyndicate.co.za`, and website `http://www.simiansyndicate.co.za`.
- Only one internal user is currently present: administrator login `erwin@simiansyndicate.co.za`.
- No API keys exist yet for users.
- API key UI path: top-right user menu → **My Preferences** → **Security** → **Add API Key**.
- Installed app/module baseline is still very light: Website, Discuss/Mail, API docs, RPC endpoints, auth/security helpers, Google/Microsoft mail helpers, SMS/Snailmail/IAP, Cobalt theme, and base web modules. Sales/CRM/Accounting/Inventory/Purchase/Project are not installed yet.

Recommended next changes, after confirmation:

1. Update `web.base.url` to `https://www.simiansyndicate.co.za`.
2. Update the company website field to `https://www.simiansyndicate.co.za`.
3. Verify Odoo service config has `proxy_mode = True`.
4. Verify OpenResty passes `X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-For`, and `X-Real-IP` to Odoo.
5. Create a dedicated `Hermes Admin` user and API key, then rotate/remove temporary admin access.

## Authenticated configuration changes

Applied on 2026-05-21 after Erwin approved changing settings.

Changes made:

- Updated `ir.config_parameter:web.base.url` from `http://www.simiansyndicate.co.za` to `https://www.simiansyndicate.co.za`.
- Added `ir.config_parameter:web.base.url.freeze = True` because Odoo auto-reverted the base URL back to HTTP when the freeze flag was absent.
- Updated company `Simian Syndicate` website from `http://www.simiansyndicate.co.za` to `https://www.simiansyndicate.co.za`.
- Created internal admin/settings user `Hermes Admin` with login `hermes@simiansyndicate.co.za`.
- Corrected `Hermes Admin` email/contact address to Cael's AgentMail address: `cael.ai@agentmail.to`.
- Assigned `Hermes Admin` to the internal user and settings/admin groups.
- Created one persistent API key for `Hermes Admin` named `Hermes Agent JSON-2 access`.
- Stored the API key only in Cael's local secret env file `~/.hermes/profiles/cael/.env`; it is not committed to the repo or stored in `ens-files`.
- Verified JSON-2 access using the new API key: `POST https://www.simiansyndicate.co.za/json/2/res.users/context_get` returned `200` with `X-Odoo-Database: SimianSyndicate`.

## App installation changes

Applied on 2026-05-21 through the `Hermes Admin` JSON-2 API key.

Changes made:

- Installed the Odoo Community `account` module, shown in Apps as **Invoicing**.
- Verified `ir.module.module` reports `account` / `Invoicing` as `installed`.
- Confirmed default accounting journals were created for company `Simian Syndicate`: Sales, Purchases, Bank, Miscellaneous Operations, Exchange Difference, and Cash Basis Taxes.
- Assigned `Hermes Admin` to `Accounting / Administrator` so the agent can inspect and configure accounting/invoicing models via the API.
- Confirmed administrator user `erwin@simiansyndicate.co.za` already had `Accounting / Administrator` access.

Post-change public verification:

- `http://www.simiansyndicate.co.za` redirects to HTTPS.
- `https://www.simiansyndicate.co.za/` serves Odoo.
- `https://www.simiansyndicate.co.za/web/login` serves Odoo.
- Canonical URLs now use `https://www.simiansyndicate.co.za/...`.
- Direct `:8069` URLs no longer appear in the checked public HTML.
- Remaining issue: OpenGraph `og:url` metadata still reports `http://www.simiansyndicate.co.za/...`. This likely requires server-side proxy config review: Odoo `proxy_mode = True` and Nginx Proxy Manager forwarding of `X-Forwarded-Proto https` / related headers. This cannot be fully changed from inside the Odoo database alone.

Follow-up needed on Zimaboard/Nginx Proxy Manager/Odoo service config:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto https;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
```

And in Odoo config:

```ini
proxy_mode = True
```

After changing service config, restart Odoo/OpenResty and re-check `og:url`.

## Current topology decision

Decision: **Simian Syndicate and LA Logic will use separate Odoo databases.**

Current database:

- `SimianSyndicate` — Simian Syndicate

Planned database:

- `LALogic` — LA Logic

Creation status:

- `https://www.simiansyndicate.co.za/web/database/list` currently returns only `SimianSyndicate`.
- Creating `LALogic` requires the Odoo database manager/master password or direct server/container access. The existing `Hermes Admin` database API key can administer records inside `SimianSyndicate`, but it cannot create a new PostgreSQL/Odoo database by itself.

Rationale:

- LA Logic is a financial compliance company, so separation, auditability, and clean access boundaries matter more than setup speed.
- Cleaner operational isolation between the two companies.
- Separate backups/restores.
- Separate users/API keys and permissions.
- Separate accounting setup and data boundaries.
- Avoids accidental cross-company leakage inside one multi-company database.
- Keeps the architecture easy to explain: LA Logic has its own database, backups, users, API keys, and access policy.

## Current recommendation

Treat `SimianSyndicate` as the dedicated Simian Syndicate database.

Create LA Logic as a separate database when ready. Do **not** add LA Logic as a second company inside `SimianSyndicate`, especially given LA Logic's financial compliance role.

## Safe probe commands used

```bash
curl -sS http://eshost.dyndns.info:8069/web/version
curl -sS -H 'Content-Type: application/json' -d '{}' http://eshost.dyndns.info:8069/web/database/list
curl -i -X POST http://eshost.dyndns.info:8069/json/2/res.users/context_get \
  -H 'Content-Type: application/json' \
  -H 'X-Odoo-Database: SimianSyndicate' \
  -d '{}'

curl -sS https://www.simiansyndicate.co.za/web/version
curl -sS -H 'Content-Type: application/json' -d '{}' https://www.simiansyndicate.co.za/web/database/list
curl -i -X POST https://www.simiansyndicate.co.za/json/2/res.users/context_get \
  -H 'Content-Type: application/json' \
  -H 'X-Odoo-Database: SimianSyndicate' \
  -d '{}'
```

The JSON-2 command intentionally omitted an API key and returned `401`, which confirms the endpoint exists and authentication is required.

## Security notes

- Do not commit Odoo admin passwords, API keys, database passwords, exports, or backups.
- For API integration, create a dedicated Odoo bot/API user with minimum required permissions.
- Use bearer API keys only in local shell/session secrets, never in repo docs.
- Production HTTPS now routes `www.simiansyndicate.co.za` to Odoo through Nginx Proxy Manager.
- Review Odoo proxy settings because generated OpenGraph URLs still show `http://www.simiansyndicate.co.za/...` during HTTPS probes. Check Odoo `proxy_mode`, Nginx Proxy Manager `X-Forwarded-*` headers, and the `web.base.url` system parameter.
