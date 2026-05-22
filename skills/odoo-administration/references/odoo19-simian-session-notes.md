# Odoo 19 Simian Session Notes

Session context: self-hosted Odoo Community Edition 19 on a Zimaboard, proxied through OpenResty, with a public website domain and JSON-2 enabled.

This reference captures reusable details from the session without secrets.

## Public routing checks

Working public state after proxy setup:

- `http://www.simiansyndicate.co.za` redirected to HTTPS.
- `https://www.simiansyndicate.co.za/` served the Odoo website.
- `https://www.simiansyndicate.co.za/web/version` returned Odoo `19.0-20260504`.
- `https://www.simiansyndicate.co.za/web/database/list` returned database `SimianSyndicate` when POSTed with JSON content.
- `POST /json/2/res.users/context_get` with `X-Odoo-Database: SimianSyndicate` returned `401` without an API key and `200` with a valid bearer key.

## Base URL correction

Observed problem:

- Odoo served over HTTPS, but generated metadata still contained HTTP/direct-host values.
- `ir.config_parameter:web.base.url` was `http://www.simiansyndicate.co.za`.
- `web.base.url.freeze` was absent.

Fix applied:

- Set `web.base.url = https://www.simiansyndicate.co.za`.
- Set `web.base.url.freeze = True` because Odoo reverted the base URL back to HTTP when freeze was absent.
- Set `res.company.website = https://www.simiansyndicate.co.za`.

Verification result:

- Canonical URLs switched to HTTPS.
- Direct `:8069` URLs disappeared from checked public HTML.
- `og:url` still reported HTTP, indicating remaining server-side proxy/header config.

## Proxy/header follow-up

If canonical URLs are fixed but OpenGraph metadata still shows HTTP, review:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto https;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
```

and Odoo service config:

```ini
proxy_mode = True
```

Restart OpenResty/Odoo after service config changes.

## Odoo 19 user/group notes

- `res.users` exposes groups as `group_ids` / `all_group_ids`, not `groups_id`.
- `base.group_user` and `base.group_system` can be resolved via `ir.model.data` and assigned through `group_ids`.
- Creating a dedicated automation user with internal + settings/admin groups worked for admin automation.

## API key generation detail

Odoo 19 API key generation through `res.users.apikeys.description.make_key()` can return an identity-check action instead of the key.

Correct flow:

```python
wiz_id = rpc('res.users.apikeys.description', 'create', [{
    'name': 'Hermes Agent JSON-2 access',
    'duration': '0',  # persistent, if allowed for the user
}])

action = rpc('res.users.apikeys.description', 'make_key', [[wiz_id]])

if action.get('res_model') == 'res.users.identitycheck':
    identity_id = action['res_id']
    action = rpc(
        'res.users.identitycheck',
        'run_check',
        [[identity_id]],
        {'context': {'password': user_password}},
    )

api_key = action['context']['default_key']
```

Pitfall: passing `password` in an outer JSON-RPC context field failed. It needed to be inside `kwargs.context.password` for `run_check()`.

## Secret-handling pattern

- Do not print the generated API key.
- Store it only in the local profile secret env file, e.g. `~/.hermes/profiles/cael/.env`.
- Document only that the key exists and where it is stored; never document the key or token prefix.
- Verify with JSON-2 immediately after storing.

## Project documentation pattern

For an Odoo project repo, maintain:

- `docs/decisions/...` for durable topology, domain, proxy, and access decisions.
- `docs/plans/...` for implementation plans.
- Secret-pattern scans before committing.
- Exact changed settings and verification commands, but no credentials.
