---
name: odoo-administration
description: "Administer self-hosted Odoo instances: safe login, proxy/base URL fixes, users/API keys, JSON-2 verification, module/company inspection, and setup runbooks."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [odoo, erp, administration, json-2, reverse-proxy, api-keys]
    related_skills: [github-repo-management, shared-file-store]
---

# Odoo Administration

## When to use

Use this skill when working on Odoo setup or administration, especially:

- connecting to a self-hosted Odoo instance
- checking Odoo version, database selection, installed modules, company/user setup
- fixing public URL / reverse proxy / HTTPS metadata problems
- creating dedicated automation users and API keys
- verifying JSON-2 or legacy RPC access
- documenting Odoo deployment decisions in a repo or runbook

## Safety rules

1. **Do not store secrets in repo docs, `ens-files`, memory, or final artifacts.** API keys and passwords belong only in local secret stores such as `~/.hermes/profiles/<profile>/.env` with `0600` permissions.
2. Prefer a dedicated automation user over the human's main admin account.
3. If the human gives a temporary password, use it only for the current task and remind them to rotate it afterward.
4. Before mutating Odoo settings, perform read-only inspection and report findings unless the user explicitly authorizes changes.
5. Server-side proxy changes (`proxy_mode`, OpenResty/Nginx headers, service restarts) usually cannot be fully fixed from inside Odoo's database. Distinguish database-level fixes from host-level fixes.

## Public endpoint checks

Safe unauthenticated probes:

```bash
curl -sS https://example.com/web/version
curl -sS -H 'Content-Type: application/json' -d '{}' https://example.com/web/database/list
curl -i -X POST https://example.com/json/2/res.users/context_get \
  -H 'Content-Type: application/json' \
  -H 'X-Odoo-Database: <db-name>' \
  -d '{}'
```

Expected JSON-2 behavior without an API key:

- `401` with a message like “User not authenticated, use an API Key with a Bearer Authorization header” means the JSON-2 endpoint exists and auth is enforced.
- `404 No database is selected` often means the `X-Odoo-Database` header is missing or wrong.

## Authenticated JSON-RPC workflow

Use `/web/session/authenticate` to obtain a session, then `/web/dataset/call_kw/<model>/<method>` for model calls.

Python pattern:

```python
import requests

BASE = 'https://example.com'
DB = '<db-name>'
LOGIN = '<login>'
PASSWORD = '<temporary-password-or-secret>'

s = requests.Session()

def post(path, payload):
    r = s.post(BASE + path, json=payload, timeout=30)
    data = r.json()
    if 'error' in data:
        raise RuntimeError(data['error'])
    return data.get('result')

def rpc(model, method, args=None, kwargs=None):
    return post(f'/web/dataset/call_kw/{model}/{method}', {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'model': model,
            'method': method,
            'args': args or [],
            'kwargs': kwargs or {},
        },
    })

post('/web/session/authenticate', {
    'jsonrpc': '2.0',
    'method': 'call',
    'params': {'db': DB, 'login': LOGIN, 'password': PASSWORD},
})
```

Odoo 19 pitfall: some self-hosted setups return a successful `/web/session/authenticate` JSON result but do **not** set a `session_id` cookie, so the next `/web/dataset/call_kw` returns `Odoo Session Expired`. In that case, log in through the normal web form to establish the cookie, then call dataset routes:

```python
import re, requests
s = requests.Session()
login_page = s.get(BASE + f'/web/login?db={DB}', timeout=30)
csrf = re.search(r'name="csrf_token"\s+value="([^"]+)"', login_page.text).group(1)
s.post(BASE + '/web/login', data={
    'login': LOGIN,
    'password': PASSWORD,
    'csrf_token': csrf,
    'db': DB,
}, allow_redirects=False, timeout=30)
# s now carries the session_id cookie for /web/dataset/call_kw/... calls
```

Useful read-only calls:

```python
rpc('ir.config_parameter', 'search_read', [[['key', 'in', [
    'web.base.url', 'web.base.url.freeze', 'database.uuid'
]]]], {'fields': ['key', 'value']})

rpc('res.company', 'search_read', [[]], {
    'fields': ['name', 'email', 'phone', 'website', 'country_id', 'currency_id']
})

rpc('res.users', 'search_read', [[]], {
    'fields': ['name', 'login', 'active', 'share', 'company_id', 'company_ids']
})

rpc('ir.module.module', 'search_read', [[['state', '=', 'installed']]], {
    'fields': ['name', 'shortdesc', 'state'],
    'limit': 300,
    'order': 'name',
})
```

Odoo 19 field-name pitfall: when reading users via JSON-2, group membership may be exposed as `group_ids` rather than older examples that use `groups_id`. If a field errors, call `fields_get` for the model and adapt instead of assuming field names from memory.

## Installing Invoicing / Accounting

In Odoo Community, the **Invoicing** app is module `account`:

```python
mods = rpc('ir.module.module', 'search_read', [[['name', '=', 'account']]], {
    'fields': ['name', 'shortdesc', 'state', 'application'],
    'limit': 1,
})
if mods and mods[0]['state'] != 'installed':
    rpc('ir.module.module', 'button_immediate_install', [[mods[0]['id']]])
```

After installing `account`, verify both module state and actual accounting access:

```python
rpc('ir.module.module', 'search_read', [[['name', '=', 'account']]], {
    'fields': ['name', 'shortdesc', 'state'], 'limit': 1,
})
rpc('account.journal', 'search_read', [[]], {
    'fields': ['name', 'type', 'company_id'], 'limit': 10,
})
```

If the automation/API user gets `AccessError` on `account.journal`, add it to the appropriate accounting group, often `Accounting / Administrator` for administration work or `Accounting / Invoicing` for narrower invoicing work. The group lookup can use `res.groups.search_read` on `full_name`.

## Public URL / reverse proxy fix

Symptoms:

- public HTTPS works, but generated HTML still contains `http://...` or direct `:8069` URLs
- canonical/open-graph metadata is wrong
- Odoo redirects to internal hostnames or ports

Terminology pitfall:

- If response headers say `openresty`, do not assume the user manages OpenResty directly. On Zimaboard/ZimaOS setups this may be **Nginx Proxy Manager** under the hood. Use the user's UI terminology (`Nginx Proxy Manager`, proxy host, SSL tab, advanced/custom config) when guiding them.
- If ZimaOS or the app store UI does not expose Odoo config, move to container-level inspection via SSH/Dockhand/Docker rather than trying to find an Odoo setting in the web UI. `proxy_mode` is an Odoo service config/startup option, not a database/admin-page setting.

Database-level fixes:

```python
# set base URL
param = rpc('ir.config_parameter', 'search_read', [[['key', '=', 'web.base.url']]], {'fields': ['key', 'value'], 'limit': 1})
if param:
    rpc('ir.config_parameter', 'write', [[param[0]['id']], {'value': 'https://www.example.com'}])
else:
    rpc('ir.config_parameter', 'create', [{'key': 'web.base.url', 'value': 'https://www.example.com'}])

# freeze base URL if Odoo auto-reverts it from request metadata
freeze = rpc('ir.config_parameter', 'search_read', [[['key', '=', 'web.base.url.freeze']]], {'fields': ['key', 'value'], 'limit': 1})
if freeze:
    rpc('ir.config_parameter', 'write', [[freeze[0]['id']], {'value': 'True'}])
else:
    rpc('ir.config_parameter', 'create', [{'key': 'web.base.url.freeze', 'value': 'True'}])
```

Also update the company website field if it still points at HTTP:

```python
rpc('res.company', 'write', [[company_id], {'website': 'https://www.example.com'}])
```

Host-level checks (Nginx/OpenResty/Nginx Proxy Manager):

```nginx
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto https;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
```

If the proxy is Nginx Proxy Manager (NPM), use NPM terminology with the user: Proxy Host **Details** and **SSL** tabs first; the **Advanced** tab may be missing/hidden depending on the ZimaOS/NPM packaging. If Odoo canonical URLs are HTTPS but OpenGraph `og:url` remains HTTP, suspect Odoo `proxy_mode = True` is not active/effective or forwarded-proto headers are not reaching Odoo.

Odoo service config:

Odoo service config:

```ini
proxy_mode = True
```

If the container has no exposed config file, look for a startup flag instead:

```bash
odoo --proxy-mode=True
```

For Docker/Compose deployments, prefer a persistent host-mounted `odoo.conf` or compose `command:` over editing only inside the running container; container filesystem edits may disappear on recreate/update.

After host-level config changes, restart Odoo and the proxy if needed, then re-check public metadata.

Verification:

```bash
curl -sS -L https://www.example.com/ -o /tmp/odoo-root.html
python3 - <<'PY'
from pathlib import Path
import re
s = Path('/tmp/odoo-root.html').read_text(errors='replace')
for label, pat in [
    ('canonical', r'<link rel="canonical" href="([^"]+)"'),
    ('og_url', r'<meta property="og:url" content="([^"]+)"'),
]:
    m = re.search(pat, s, re.I)
    print(label, m.group(1) if m else None)
print('contains :8069', ':8069' in s)
PY
```

Note: `web.base.url.freeze=True` can fix canonical URLs while `og:url` still shows HTTP if server-side forwarded-proto/proxy-mode remains wrong.

## Multi-database admin website access

When multiple databases exist on one Odoo host, give Erwin the direct database-scoped login URL instead of only the generic `/web/login` URL:

```text
https://<host>/web/login?db=<exact-db-name>
```

If the direct login loops or the wrong database is selected, use the selector:

```text
https://<host>/web/database/selector
```

Always use the exact database name returned by `/web/database/list`; for example `lalogic` is not `LALogic`.

## JSON-2 call-shape pitfall

Odoo 19 `/json/2/<model>/<method>` is not the same envelope as `/web/dataset/call_kw`. Do **not** send JSON like `{"args": [...], "kwargs": {...}}` to JSON-2 model methods unless the endpoint explicitly documents that shape; it can leak `args`/`kwargs` through as unexpected Python keyword arguments, e.g. `BaseModel._read_format() got an unexpected keyword argument 'args'` on `search_read`.

For JSON-2, pass method parameters as the method expects them. Common examples:

```python
# search_read(domain, fields=..., limit=...)
post('/json/2/ir.module.module/search_read', [
    [['name', 'in', ['website', 'account']]],
], {'fields': ['name', 'shortdesc', 'state'], 'limit': 10})

# record method with JSON-2 ids style
post('/json/2/ir.module.module/button_immediate_install', [], {'ids': [module_id]})
```

If unsure, verify with a read-only method first (`context_get`, `search_read`) before calling install/write methods.

## Installing apps/modules via JSON-2

When Erwin explicitly asks to add an app, install the module through `ir.module.module` rather than driving the UI. For multiple databases, use each database's own dedicated automation/API key and verify each database separately.

For module-baseline installs, see `references/module-baseline-installation.md` for a worked pattern and retry guidance.

Example for the Odoo Community **Invoicing** app:

```python
mods = rpc('ir.module.module', 'search_read', [[['name', '=', 'account']]], {
    'fields': ['name', 'shortdesc', 'state', 'application'],
    'limit': 1,
})
if mods and mods[0]['state'] != 'installed':
    rpc('ir.module.module', 'button_immediate_install', [[mods[0]['id']]])
```

Post-install verification:

```python
rpc('ir.module.module', 'search_read', [[['name', '=', 'account']]], {
    'fields': ['name', 'shortdesc', 'state'],
    'limit': 1,
})
rpc('account.journal', 'search_read', [[]], {
    'fields': ['name', 'type', 'company_id'],
    'limit': 10,
})
```

Pitfall: installing `account` may create accounting groups and journals, but the automation user may still lack model access. If `account.journal` returns an access error, add the dedicated agent user to `Accounting / Administrator` or the narrowest accounting group needed. In Odoo 19, the user group field is `group_ids` (not legacy `groups_id`).

## Module/app installation via JSON-2

Odoo apps are `ir.module.module` records. For Odoo Community, **Invoicing** is the `account` module.

Safe pattern:

```python
mods = rpc('ir.module.module', 'search_read', [[['name', '=', 'account']]], {
    'fields': ['name', 'shortdesc', 'state', 'application'],
    'limit': 1,
})
if mods and mods[0]['state'] != 'installed':
    rpc('ir.module.module', 'button_immediate_install', [[mods[0]['id']]])
```

With JSON-2, pass record IDs as `{'ids': [module_id]}` when calling record methods such as `button_immediate_install`. Verify installation by re-reading `ir.module.module.state == 'installed'`.

If module installation fails because Odoo is currently processing a scheduled action, treat it as a transient lock: wait briefly and retry the specific module install before reporting failure. Do not encode the initial lock as a permanent environment limitation.

After installing Accounting/Invoicing, the automation user may still lack access to accounting models. If `account.journal` access fails with an Accounting group error, inspect `res.groups` for `Accounting / Administrator` or `Accounting / Invoicing`, then add the appropriate group to the automation user via `res.users.write`. In Odoo 19, the user group M2M field is `group_ids` (not legacy `groups_id`).

Verify with a read-only accounting model call, for example:

```python
rpc('account.journal', 'search_read', [[]], {
    'fields': ['name', 'type', 'company_id'],
    'limit': 10,
})
```

## New database creation boundary

A database-scoped Odoo API key, even for a Settings/Admin user, can administer records inside the selected database but cannot by itself create a new Odoo/PostgreSQL database. Creating a new database requires one of:

- Odoo database manager/master password through `/web/database/create`, or
- server/container shell access to run the Odoo database creation flow, or
- direct deployment/PostgreSQL control according to the hosting setup.

Do not imply that a JSON-2 API key for `SimianSyndicate` can create a separate `LALogic` database. If the user is blocked on container access, suggest a temporary multi-company pilot only after explaining the trade-off.

## Dedicated automation user

Recommended pattern:

1. Create `Hermes Admin` / automation user with a dedicated login.
2. Assign internal user and settings/admin groups only if administration is required.
3. Generate an API key for that user.
4. Store the API key locally in profile `.env`, not in docs:

```dotenv
ODOO_SIMIAN_URL=https://www.example.com
ODOO_SIMIAN_DB=<db-name>
ODOO_SIMIAN_LOGIN=hermes@example.com
ODOO_SIMIAN_API_KEY=<secret>
```

Verify JSON-2 with the key:

```bash
curl -i -X POST "$ODOO_SIMIAN_URL/json/2/res.users/context_get" \
  -H "Authorization: bearer $ODOO_SIMIAN_API_KEY" \
  -H 'Content-Type: application/json' \
  -H "X-Odoo-Database: $ODOO_SIMIAN_DB" \
  -d '{}'
```

Expected: `200 OK`.

## Odoo 19 API key identity-check pitfall

In Odoo 19, `res.users.apikeys.description.make_key()` is guarded by an identity-check wizard. Calling `make_key()` may return an action for `res.users.identitycheck` instead of the key.

Flow:

1. Create the description wizard: `res.users.apikeys.description.create({'name': ..., 'duration': '0'})`.
2. Call `make_key()`.
3. If the returned action has `res_model == 'res.users.identitycheck'`, call `res.users.identitycheck.run_check()` on the returned `res_id`, passing the user's password in **`kwargs.context.password`**.
4. The second action contains `context.default_key`.

The context placement matters:

```python
action2 = rpc(
    'res.users.identitycheck',
    'run_check',
    [[identity_wizard_id]],
    {'context': {'password': user_password}},
)
api_key = action2['context']['default_key']
```

Passing the password in an outer JSON-RPC context parameter can fail with “Incorrect Password”.

## Odoo Website placeholder pages

When Erwin asks to create a simple public placeholder/landing page inside Odoo Website, prefer API-driven setup over slow UI editing:

1. Install the `website` module in the target database using that database's dedicated API key.
2. Inspect `website`, `website.page`, `website.menu`, and the homepage `ir.ui.view`.
3. Prefer the website-specific homepage page where `url == '/'` and `website_id` matches the target website.
4. Replace the homepage view's `arch_db` with a complete QWeb page wrapped in `website.layout` and `<div id="wrap" class="oe_structure ...">`.
5. Rename the website/page/menu records to the brand name and publish the page.
6. If the stock Odoo Website header/footer show demo phone numbers, demo links, or Odoo branding on a placeholder page, hide `#top` and `#bottom` in page CSS. Also hide `.o_skip_to_content` until focus so the accessibility skip link does not appear as a stray blue link.
7. Verify the rendered target database. On multi-database hosts, a normal public request may show the database selector; use an explicit `X-Odoo-Database: <db>` header for read-only verification, then explain that a proper public site needs domain/subdomain database routing.
8. Do not treat Odoo Website `domain`, company `website`, or `web.base.url` as database-selection mechanisms. Odoo must select the database before it can read those records. If both public domains hit `/web/database/selector` but forced `X-Odoo-Database` requests render the correct sites, the website content is fine and the missing fix is proxy/dbfilter routing.
9. For Nginx Proxy Manager on a multi-database Odoo host, prefer one proxy host per public domain, each forwarding to the same Odoo upstream but setting the correct `X-Odoo-Database` header. Verify the Simian proxy host does not accidentally set `lalogic`, and the LA Logic proxy host does not accidentally set `SimianSyndicate`.

See `references/odoo-website-placeholder.md` for the LA Logic worked pattern, QWeb structure, CSS chrome-hiding snippet, and multi-database verification caveat.
See `references/odoo-multidb-website-routing.md` for the multi-domain/multi-database routing diagnostic and Nginx Proxy Manager header pattern.

## Documentation habit

For project repos, record durable Odoo decisions and changes in a decision/runbook doc, but never include passwords, API keys, token prefixes, database dumps, customer data, or other secrets. Run a quick secret-pattern sanity check before committing.

See `references/odoo19-simian-session-notes.md` for a compact worked example from an Odoo 19 Community Zimaboard setup.
