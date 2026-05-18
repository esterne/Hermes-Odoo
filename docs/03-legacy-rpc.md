# 03 — Legacy XML-RPC and JSON-RPC

Odoo 19 Community still ships XML-RPC and legacy JSON-RPC through the auto-installed `rpc` addon, but both are deprecated.

`addons/rpc/controllers/__init__.py` contains the deprecation notice:

> The `/xmlrpc`, `/xmlrpc/2` and `/jsonrpc` endpoints are deprecated in Odoo 19 and scheduled for removal in Odoo 22.

## XML-RPC endpoints

- `/xmlrpc/<service>` — historical entrypoint
- `/xmlrpc/2/<service>` — newer XML-RPC v2 entrypoint

Common services:

- `common`
  - `version`
  - `authenticate`
- `object`
  - `execute`
  - `execute_kw`

Typical flow:

1. Authenticate against `/xmlrpc/2/common`.
2. Call `/xmlrpc/2/object` with `execute_kw`.

Example method call shape:

```python
models.execute_kw(
    db, uid, password,
    'res.partner', 'search_read',
    [[['is_company', '=', True]]],
    {'fields': ['name', 'email'], 'limit': 10}
)
```

## JSON-RPC endpoint

- `/jsonrpc`

Payload shape:

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": [
      "db", 2, "password-or-api-key",
      "res.partner", "search_read",
      [[[]]],
      {"fields": ["name"], "limit": 5}
    ]
  },
  "id": 1
}
```

## Migration to JSON-2

Legacy:

```python
execute_kw(db, uid, password, model, method, args, kwargs)
```

JSON-2:

```http
POST /json/2/<model>/<method>
Authorization: bearer <API_KEY>
Content-Type: application/json

{...named arguments...}
```

Key differences:

- JSON-2 uses bearer API keys, not `(db, uid, password)` per call.
- JSON-2 uses the URL path for model/method.
- JSON-2 uses named parameters only.
- DB is selected from host/dbfilter or `X-Odoo-Database`.
- JSON-2 returns method results directly, not JSON-RPC envelopes.

## When legacy RPC is still useful

- Existing mature client libraries
- Integrations that must support Odoo < 19
- Quick compatibility testing

For new Odoo 19-only work, prefer JSON-2.
