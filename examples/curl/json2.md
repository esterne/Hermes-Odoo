# curl examples for Odoo 19 JSON-2

Set environment variables first:

```bash
export ODOO_URL="https://odoo.example.com"
export ODOO_DB="mydb"
# Put the real key in your shell/session, not in Git:
export ODOO_API_KEY="<your-api-key>"
```

## Version check

```bash
curl -sS "$ODOO_URL/web/version"
```

## Search/read partners

```bash
curl -sS -X POST "$ODOO_URL/json/2/res.partner/search_read"   -H "Authorization: bearer $ODOO_API_KEY"   -H "Content-Type: application/json"   -H "X-Odoo-Database: $ODOO_DB"   -d '{"domain": [["is_company", "=", true]], "fields": ["name", "email"], "limit": 5}'
```

## Create a contact

```bash
curl -sS -X POST "$ODOO_URL/json/2/res.partner/create"   -H "Authorization: bearer $ODOO_API_KEY"   -H "Content-Type: application/json"   -H "X-Odoo-Database: $ODOO_DB"   -d '{"vals_list": [{"name": "API Test Contact", "email": "api-test@example.com"}]}'
```

## Update a contact

```bash
curl -sS -X POST "$ODOO_URL/json/2/res.partner/write"   -H "Authorization: bearer $ODOO_API_KEY"   -H "Content-Type: application/json"   -H "X-Odoo-Database: $ODOO_DB"   -d '{"ids": [42], "vals": {"phone": "+27 00 000 0000"}}'
```

## Call a business method

```bash
curl -sS -X POST "$ODOO_URL/json/2/sale.order/action_confirm"   -H "Authorization: bearer $ODOO_API_KEY"   -H "Content-Type: application/json"   -H "X-Odoo-Database: $ODOO_DB"   -d '{"ids": [123]}'
```

## API discovery with api_doc

```bash
curl -sS "$ODOO_URL/doc-bearer/res.partner.json"   -H "Authorization: bearer $ODOO_API_KEY"   -H "Content-Type: application/json"   -H "X-Odoo-Database: $ODOO_DB"
```
