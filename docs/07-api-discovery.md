# 07 — API discovery with `api_doc`

Odoo 19 Community includes an `api_doc` addon that exposes a documentation UI and JSON reflection endpoints.

## What it gives you

- Installed modules
- Available models
- Fields visible to the current user
- Public methods visible/callable to the current user
- Method signatures and docstrings where available

## Key routes from source

- `/doc` — browser UI, `auth='user'`
- `/doc/index.json` — JSON index, `auth='user'`
- `/doc/<model_name>.json` — model detail, `auth='user'`
- `/doc-bearer/index.json` — JSON index with bearer auth
- `/doc-bearer/<model_name>.json` — model detail with bearer auth

The bearer endpoints use `type='json2'` and `auth='bearer'`.

## Permissions

The controller checks group membership:

- `api_doc.group_allow_doc`

The docs are filtered by the current user's model access and field access, so a bot user sees only what that bot can access.

## Suggested integration workflow

1. Install/enable `api_doc` on a development or staging database.
2. Grant `api_doc.group_allow_doc` to the API/bot user.
3. Call `/doc-bearer/index.json` to discover installed modules and models.
4. Call `/doc-bearer/<model>.json` for fields and public method signatures.
5. Generate typed client wrappers or integration tests from that live schema.
6. Do not assume another Odoo database has the same modules/fields.

## Example

```bash
curl -sS "$ODOO_URL/doc-bearer/res.partner.json"   -H "Authorization: bearer $ODOO_API_KEY"   -H "Content-Type: application/json"   -H "X-Odoo-Database: $ODOO_DB"
```

The route is `json2`, so use JSON-compatible headers even though the body can be empty.

## Why discovery matters

Odoo is modular and customized often. A field or method available in one database may not exist in another because of:

- different installed addons
- localization modules
- custom modules
- user permissions
- company rules
- field-level group restrictions

A robust client should discover or verify capabilities before writing data.
