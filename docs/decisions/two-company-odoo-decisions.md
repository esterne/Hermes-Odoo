# Two-Company Odoo Decisions

Last updated: 2026-05-21

## Current live instance

| Item | Current value | Status |
|---|---:|---|
| Hostname | `eshost.dyndns.info` | Confirmed reachable |
| Business website domain | `www.simiansyndicate.co.za` | Confirmed routing through OpenResty to Odoo over HTTPS |
| Public HTTPS root | `https://eshost.dyndns.info/` | Reaches `openresty` / `ZimaOS-Gateway` static/default site, not Odoo paths |
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

## Current topology decision

Decision: **Simian Syndicate and LA Logic will use separate Odoo databases.**

Current database:

- `SimianSyndicate` — Simian Syndicate

Planned database:

- `LALogic` — LA Logic

Rationale:

- Cleaner operational isolation between the two companies.
- Separate backups/restores.
- Separate users/API keys and permissions.
- Separate accounting setup and data boundaries.
- Avoids accidental cross-company leakage inside one multi-company database.

## Current recommendation

Treat `SimianSyndicate` as the dedicated Simian Syndicate database.

Create LA Logic as a separate database when ready. Do **not** add LA Logic as a second company inside `SimianSyndicate`.

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
- Production HTTPS now routes `www.simiansyndicate.co.za` to Odoo through OpenResty.
- Review Odoo proxy settings because generated canonical/open-graph URLs still showed `http://www.simiansyndicate.co.za/...` and `http://eshost.dyndns.info:8069/...` during the HTTPS probe. Check Odoo `proxy_mode`, reverse-proxy `X-Forwarded-*` headers, and the `web.base.url` system parameter.
