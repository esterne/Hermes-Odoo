# 02 — JSON-2 API deep dive

JSON-2 is the modern external API introduced for Odoo 19.

## Endpoint

```http
POST /json/2/<model>/<method>
Content-Type: application/json
Authorization: bearer <API_KEY>
X-Odoo-Database: <database-name>   # when needed
```

Examples:

```http
POST /json/2/res.partner/search_read
POST /json/2/product.template/create
POST /json/2/sale.order/action_confirm
POST /json/2/account.move/action_post
```

## Request body

JSON-2 accepts a JSON object. Parameters are passed by name.

Common parameters:

- `ids`: record IDs for recordset methods. Omit for `@api.model` methods.
- `context`: Odoo context overrides, e.g. language, timezone, company IDs.
- method-specific parameters such as `domain`, `fields`, `vals_list`, `limit`, `offset`, `order`.

Example search/read:

```json
{
  "domain": [["is_company", "=", true]],
  "fields": ["name", "email", "phone"],
  "limit": 10
}
```

Example recordset call:

```json
{
  "ids": [42],
  "context": {"lang": "en_US"}
}
```

## Response body

Success returns the JSON-serialized method result directly.

Examples:

- `search` returns a list of IDs.
- `read` returns a list of dictionaries.
- `search_read` returns a list of dictionaries.
- `create` returns created record IDs.
- methods returning Odoo recordsets are converted to IDs by the JSON-2 controller.

Errors return a JSON object containing roughly:

- `name`
- `message`
- `arguments`
- `context`
- `debug`

## Controller behavior from Community source

`addons/rpc/controllers/json2.py` defines:

```python
@http.route(
    '/json/2/<__model__>/<__method__>',
    methods=['POST'],
    auth='bearer',
    type='json2',
    readonly=_web_json_2_rpc_readonly,
    save_session=False,
)
```

The controller:

1. Looks up the model in `request.env[__model__]`.
2. Applies `with_context(context)`.
3. Resolves only public methods via `get_public_method`.
4. Rejects `ids` when calling an `@api.model` method.
5. Binds named kwargs against the Python method signature.
6. Calls the method on `Model.browse(ids)`.
7. Converts returned recordsets to `ids`.

## Read-only optimization

The JSON-2 controller checks whether the target method has a `_readonly` marker and may dispatch through a read-only cursor. ORM methods like `search_read` are read-only. Writes and business actions should use the normal write transaction path.

## Transactions

Each HTTP request is its own transaction. You cannot create a multi-call transaction from the outside.

Good:

- call `sale.order.action_confirm` once
- create a custom public model method that performs all related writes atomically

Risky:

- create order in one API call
- create lines in separate API calls
- confirm in another call
- assume those calls are one transaction

## Common methods

### `search`

```json
{
  "domain": [["name", "ilike", "airbank"]],
  "limit": 20,
  "order": "name asc"
}
```

### `read`

```json
{
  "ids": [1, 2, 3],
  "fields": ["name", "email"]
}
```

### `search_read`

```json
{
  "domain": [["customer_rank", ">", 0]],
  "fields": ["name", "email", "phone"],
  "limit": 50
}
```

### `create`

```json
{
  "vals_list": [{"name": "ACME", "email": "ops@example.com"}]
}
```

Depending on the exact method signature, some models accept a dict or list of dicts. Check the model method signature through `api_doc` or source.

### `write`

```json
{
  "ids": [42],
  "vals": {"phone": "+27 00 000 0000"}
}
```

### `unlink`

```json
{
  "ids": [42]
}
```

## Relation field write commands

Odoo uses command tuples for One2many/Many2many changes. Over JSON they are arrays.

Common commands:

- `[0, 0, values]` — create related record
- `[1, id, values]` — update related record
- `[2, id, 0]` — delete related record
- `[3, id, 0]` — unlink relation
- `[4, id, 0]` — link existing record
- `[5, 0, 0]` — clear all links
- `[6, 0, ids]` — replace with IDs

Example sale order with lines:

```json
{
  "vals_list": [{
    "partner_id": 7,
    "order_line": [
      [0, 0, {"product_id": 12, "product_uom_qty": 2}]
    ]
  }]
}
```

## Context usage

Useful context keys:

- `lang`: e.g. `en_US`
- `tz`: timezone
- `allowed_company_ids`: multi-company access
- `company_id`: active company in some flows
- module-specific flags used by business methods

Be careful: context can change business behavior.

## HTTP status patterns

- `200 OK`: success
- `400 Bad Request`: malformed JSON / bad content type / parameter binding issues
- `401/403`: authentication or access problems depending on failure path
- `404 Not Found`: model/method/DB not found, or wrong `/json/2` shape
- `422 Unprocessable Entity`: method signature mismatch, inappropriate `ids` for model methods
- `500`: internal error / unhandled application error

## Minimal curl

```bash
curl -sS -X POST "$ODOO_URL/json/2/res.partner/search_read"   -H "Authorization: bearer $ODOO_API_KEY"   -H "Content-Type: application/json"   -H "X-Odoo-Database: $ODOO_DB"   -d '{"domain": [], "fields": ["name"], "limit": 5}'
```
