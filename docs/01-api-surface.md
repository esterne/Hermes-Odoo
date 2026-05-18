# 01 — Odoo 19 Community API surface

Odoo's external integration surface is model-centric. Most data access goes through models such as `res.partner`, `product.template`, `sale.order`, `account.move`, `stock.picking`, and `crm.lead`.

## Primary API options in Odoo 19 Community

### 1. JSON-2 — preferred for new integrations

- Endpoint: `POST /json/2/<model>/<method>`
- Request body: JSON object with named parameters
- Auth: `Authorization: bearer <API_KEY>`
- Database selection: `X-Odoo-Database: <db>` when needed
- Implemented in Community source: `addons/rpc/controllers/json2.py`

Use this for new work unless an existing library only supports XML-RPC.

### 2. XML-RPC — legacy but still present

- Endpoints:
  - `/xmlrpc/<service>`
  - `/xmlrpc/2/<service>`
- Typical services:
  - `common` for authentication/version
  - `object` for model calls
- Implemented in Community source: `addons/rpc/controllers/xmlrpc.py`
- Deprecated in Odoo 19 and scheduled for removal in Odoo 22.

### 3. JSON-RPC — legacy but still present

- Endpoint: `/jsonrpc`
- Body contains `service`, `method`, and `args`
- Implemented in Community source: `addons/rpc/controllers/jsonrpc.py`
- Deprecated in Odoo 19 and scheduled for removal in Odoo 22.

### 4. Web controller routes

Odoo modules also expose normal HTTP/JSON controller routes. These are **not** the same as the external model API. They power the web UI, website, portal, binary content, payment flows, and module-specific features.

Examples in Community source:

- `/web/version` and `/json/version`
- `/web/login`
- `/web/content`, `/web/image`
- `/web/database/*`
- `/doc/*` from the `api_doc` addon
- `/json/1/*` experimental read-oriented web view JSON route from `web`

## Mental model

For automation, think in this order:

1. Identify the Odoo model.
2. Use `search`, `read`, `search_read`, `create`, `write`, `unlink`, or a business method like `action_confirm`.
3. Let Odoo's access rights and record rules enforce permissions.
4. Prefer calling one high-level business method over stitching many low-level writes.

## Key source files

- `addons/rpc/controllers/json2.py`
- `addons/rpc/controllers/xmlrpc.py`
- `addons/rpc/controllers/jsonrpc.py`
- `addons/rpc/controllers/__init__.py`
- `odoo/http.py` — dispatchers, route types, auth modes
- `odoo/service/model.py` — legacy model RPC dispatch helpers
- `odoo/orm/models.py` — ORM methods exposed through model calls

Source snapshot: Odoo `19.0` commit `e5144dd38cb9161d8ebbf6a7d06f1698a20a4901`.
