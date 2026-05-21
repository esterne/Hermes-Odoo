# Two-Company Odoo Decisions

Last updated: 2026-05-21

## Current live instance

| Item | Current value | Status |
|---|---:|---|
| Hostname | `eshost.dyndns.info` | Confirmed reachable |
| Business website domain | `www.simiansyndicate.co.za` | Confirmed pointed at the same host, but normal port 80 currently serves OpenResty default site |
| Public HTTPS root | `https://eshost.dyndns.info/` | Reaches `openresty` / `ZimaOS-Gateway` static/default site, not Odoo paths |
| Public HTTP website root | `http://www.simiansyndicate.co.za/` | Currently serves OpenResty `Default Site`, not Odoo |
| Public HTTPS website root | `https://www.simiansyndicate.co.za/` | TLS currently fails with SNI/name error during probe |
| Odoo HTTP URL | `http://eshost.dyndns.info:8069` and `http://www.simiansyndicate.co.za:8069` | Confirmed Odoo |
| Odoo host hardware | Zimaboard | User-confirmed |
| Odoo edition | Odoo Community Edition 19 | User-confirmed; version endpoint reports `19.0-20260504` |
| Odoo version | `19.0-20260504` | Confirmed via `/web/version` |
| Odoo server | `Werkzeug/3.0.1 Python/3.12.3` | Confirmed from response headers |
| Database list | `SimianSyndicate` | Confirmed via `/web/database/list` |
| Website state | Basic Odoo website template | User-confirmed; Odoo template pages are visible on direct `:8069` access |
| JSON-2 endpoint | `/json/2/res.users/context_get` | Confirmed present; unauthenticated request returns `401` with API-key message when `X-Odoo-Database: SimianSyndicate` is provided |

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
```

The JSON-2 command intentionally omitted an API key and returned `401`, which confirms the endpoint exists and authentication is required.

## Security notes

- Do not commit Odoo admin passwords, API keys, database passwords, exports, or backups.
- For API integration, create a dedicated Odoo bot/API user with minimum required permissions.
- Use bearer API keys only in local shell/session secrets, never in repo docs.
- Production HTTPS should eventually route Odoo cleanly through the reverse proxy instead of requiring direct `:8069` access.
- Current domain routing gap: `www.simiansyndicate.co.za` reaches the Zimaboard/OpenResty default site on normal HTTP, while Odoo responds on `:8069`. Configure the ZimaOS/OpenResty reverse proxy so `www.simiansyndicate.co.za` proxies to Odoo on `127.0.0.1:8069` or the container/service equivalent, then issue/attach a valid TLS certificate for HTTPS.
