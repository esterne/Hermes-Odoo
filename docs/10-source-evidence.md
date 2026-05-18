# 10 — Source evidence log

Research snapshot:

- Date: `2026-05-18 18:49:48 UTC`
- Source repo: `https://github.com/odoo/odoo`
- Branch: `19.0`
- Commit: `e5144dd38cb9161d8ebbf6a7d06f1698a20a4901`

## Primary official docs consulted

- Odoo 19 External JSON-2 API documentation
- Odoo 19 ORM API documentation
- Odoo 19 Web Controllers documentation
- Odoo 19 Security documentation
- Odoo 19 Access Rights documentation
- Odoo 19 Actions documentation

## Primary source files inspected

### JSON-2

- `addons/rpc/controllers/json2.py`
  - route: `/json/2/<__model__>/<__method__>`
  - methods: `POST`
  - auth: `bearer`
  - type: `json2`
  - session saving: disabled
  - public method dispatch via `get_public_method`

### Legacy RPC

- `addons/rpc/controllers/xmlrpc.py`
  - `/xmlrpc/<service>`
  - `/xmlrpc/2/<service>`
- `addons/rpc/controllers/jsonrpc.py`
  - `/jsonrpc`
- `addons/rpc/controllers/__init__.py`
  - deprecation warning
  - `/web/version`
  - `/json/version`

### HTTP dispatcher

- `odoo/http.py`
  - `Json2Dispatcher`
  - route auth modes including `bearer`
  - error serialization

### API docs addon

- `addons/api_doc/controllers/api_doc.py`
  - `/doc`
  - `/doc/index.json`
  - `/doc/<model_name>.json`
  - `/doc-bearer/index.json`
  - `/doc-bearer/<model_name>.json`

### API keys

- `odoo/addons/base/models/res_users.py`
  - `res.users.apikeys`
  - `_check_credentials`
  - `_generate`
  - `generate`
  - `revoke`

## Generated references

- [`references/source-routes.json`](../references/source-routes.json)
- [`references/community-addons.json`](../references/community-addons.json)
- [`references/model-inventory-major-community.json`](../references/model-inventory-major-community.json)

## Caveats

- Odoo's hosted pricing/plan restrictions are not the same thing as self-hosted Community source capabilities. See [`docs/11-deployment-caveat-hosted-vs-self-hosted.md`](11-deployment-caveat-hosted-vs-self-hosted.md).
- Installed addons determine the live API. A plain database and a production database can expose very different models and fields.
- Custom modules can add fields, models, methods, controllers, and security rules.
- Enterprise-only models/apps are intentionally out of scope.
