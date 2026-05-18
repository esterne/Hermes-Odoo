# 08 — Integration patterns and examples

## Pattern: find-or-create partner

1. Search by a stable identifier, preferably email, VAT, external reference, or custom field.
2. If not found, create.
3. If found, update only intended fields.

```http
POST /json/2/res.partner/search_read
```

```json
{
  "domain": [["email", "=", "buyer@example.com"]],
  "fields": ["id", "name", "email"],
  "limit": 1
}
```

```http
POST /json/2/res.partner/create
```

```json
{
  "vals_list": [{
    "name": "Buyer Example",
    "email": "buyer@example.com",
    "customer_rank": 1
  }]
}
```

## Pattern: create quotation and confirm

1. Ensure partner exists.
2. Ensure products exist.
3. Create `sale.order` with line commands.
4. Confirm via `action_confirm`.

```json
{
  "vals_list": [{
    "partner_id": 7,
    "order_line": [
      [0, 0, {"product_id": 12, "product_uom_qty": 2, "price_unit": 99.0}]
    ]
  }]
}
```

Then:

```json
{"ids": [123]}
```

against:

```http
POST /json/2/sale.order/action_confirm
```

## Pattern: create and post invoice

1. Create `account.move` with `move_type='out_invoice'`.
2. Add `invoice_line_ids` using command arrays.
3. Post with `action_post`.

Do not directly set posted/payment state fields.

## Pattern: read stock on hand

Use `stock.quant` for on-hand quantities. Domain depends on warehouse/location strategy.

```json
{
  "domain": [["product_id", "=", 12]],
  "fields": ["product_id", "location_id", "quantity", "reserved_quantity"]
}
```

## Pattern: external IDs

For stable mapping between external systems and Odoo:

- Use a custom field like `x_external_id`, or
- Create `ir.model.data` records if you are managing module-style external IDs, or
- Maintain a separate mapping table in the external system.

For business integrations, a custom field is usually simplest.

## Pattern: attachments

Use `ir.attachment` with base64-encoded binary data.

Typical fields:

- `name`
- `res_model`
- `res_id`
- `mimetype`
- `datas` or raw/binary fields depending on method/context

For large files, verify current Odoo behavior and limits in the target deployment.

## Pattern: idempotent sync

Every write integration should be idempotent:

- external ID mapping
- retry-safe creates
- no blind duplicate contacts/orders
- reconciliation jobs that compare changed timestamps
- logging of Odoo record IDs returned by create calls

## Pattern: incremental reads

Use date fields like `write_date` or model-specific dates:

```json
{
  "domain": [["write_date", ">", "2026-05-18 00:00:00"]],
  "fields": ["id", "display_name", "write_date"],
  "order": "write_date asc",
  "limit": 100
}
```

## Pattern: capability check before workflow

Before using a workflow, check:

- model exists
- fields exist
- method exists
- user has access
- required modules are installed

Use `api_doc`, `ir.model`, `ir.module.module`, and lightweight test calls in staging.
