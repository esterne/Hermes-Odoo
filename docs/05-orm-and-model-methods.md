# 05 — ORM and model methods that matter for the API

Odoo API calls are thin wrappers around the ORM.

## Models

Models are Python classes. Common base classes:

- `models.Model` — persistent database model
- `models.TransientModel` — temporary/wizard model
- `models.AbstractModel` — shared abstract behavior

Model technical names use dot notation:

- `res.partner`
- `product.template`
- `sale.order`
- `account.move`
- `stock.picking`
- `crm.lead`

## Recordsets

Most methods operate on recordsets. In JSON-2, `ids` determines the recordset:

```json
{"ids": [10, 11]}
```

Then the method is called roughly as:

```python
request.env[model].browse(ids).method(**kwargs)
```

## `@api.model` methods

For model-level methods, do not send `ids`. JSON-2 explicitly rejects `ids` for `@api.model` methods.

Examples:

- `search`
- `search_read`
- `create`
- `fields_get`
- `default_get`

## Public method rule

Odoo's security docs warn: any method not starting with `_` is potentially callable through RPC if it is public and exposed. JSON-2 resolves methods through `get_public_method`.

Implications:

- Private helpers should start with `_`.
- Public methods must validate permissions and state themselves.
- ACLs are checked during CRUD, but custom public methods can do unsafe things if poorly written.

## Core ORM methods

### Search/read

- `search(domain, offset=0, limit=None, order=None)`
- `search_count(domain)`
- `read(fields=None, load='_classic_read')`
- `search_read(domain=None, fields=None, offset=0, limit=None, order=None)`
- `read_group(domain, fields, groupby, ...)`

### Write lifecycle

- `create(vals_list)`
- `write(vals)`
- `unlink()`
- `copy(default=None)`

### Metadata/discovery

- `fields_get()`
- `default_get(fields_list)`
- `name_search(name='', args=None, operator='ilike', limit=100)`
- `name_get()` in older patterns / display-name behavior in newer flows

## Domains

Domains are lists of predicates:

```json
[["customer_rank", ">", 0], ["email", "!=", false]]
```

Operators include:

- `=`, `!=`, `>`, `<`, `>=`, `<=`
- `in`, `not in`
- `like`, `ilike`, `not like`, `not ilike`
- `child_of`, `parent_of` for hierarchical models
- logical operators: `&`, `|`, `!`

## Fields

Common field types:

- scalar: `Boolean`, `Char`, `Text`, `Integer`, `Float`, `Monetary`, `Selection`, `Date`, `Datetime`, `Binary`, `Html`
- relational: `Many2one`, `One2many`, `Many2many`
- computed/related fields may or may not be stored/searchable

## Many2one values

Reads often return Many2one fields as `[id, display_name]` unless using lower-level options.

Writes use the integer ID:

```json
{"partner_id": 7}
```

## One2many/Many2many writes

Use command arrays. See [JSON-2 API deep dive](02-json2-api.md#relation-field-write-commands).

## Business methods

Many important operations are methods, not simple field writes:

- `sale.order/action_confirm`
- `account.move/action_post`
- `stock.picking/action_confirm`
- `stock.picking/button_validate`
- `mrp.production/action_confirm`
- `crm.lead/action_set_won` or related CRM methods depending on version/modules

Prefer business methods over directly changing state fields.
