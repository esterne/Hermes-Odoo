# 04 — Authentication and API keys

## JSON-2 auth

JSON-2 uses bearer tokens:

```http
Authorization: bearer <API_KEY>
```

The route uses `auth='bearer'` and `save_session=False`, so it is designed for stateless API calls.

## API key storage in Odoo

Community source defines API keys on model `res.users.apikeys` in `odoo/addons/base/models/res_users.py`.

Important implementation details:

- Keys belong to a `res.users` user.
- Keys can have a scope.
- A `NULL` scope behaves like a global key for RPC.
- Keys can have expiration dates.
- The cleartext key is generated once and stored hashed.
- A key prefix/index is stored to locate candidate hashes efficiently.
- Expired keys are garbage-collected by an autovacuum method.

## Creating keys

Normal path:

1. Log into Odoo as the target user.
2. Open user preferences / account security.
3. Generate a new API key.
4. Copy it immediately; it is shown once.

Programmatic path:

- Model: `res.users.apikeys`
- Methods: `generate`, `revoke`
- Controlled by config parameter `base.enable_programmatic_api_keys`
- Administrators have special handling, but relying on temporarily enabling programmatic key creation is risky.

## Recommended bot-user pattern

For an integration agent:

1. Create a dedicated Odoo user, e.g. `api.hermes@example.com`.
2. Give it only the groups it needs.
3. Prefer no interactive use from this user.
4. Generate a named API key such as `Hermes Odoo integration`.
5. Store the key outside the repo in environment variables or a secret store.
6. Rotate before expiration.
7. Audit by user and key name.

## Multi-database instances

If one server hosts multiple Odoo databases, either:

- configure host/dbfilter so the host maps to one DB, or
- send `X-Odoo-Database: <db>`.

Bad or missing database selection returns a not-found-style failure before model dispatch.

## Security implications

Bearer token = act as that Odoo user.

Access is limited by:

- model access rights (`ir.model.access`)
- record rules (`ir.rule`)
- field-level group restrictions
- method-level checks inside public methods

Do not use admin API keys for routine automation.
