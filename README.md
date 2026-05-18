# Hermes-Odoo

Odoo 19 **Community Edition** API research notes, integration patterns, and examples.

Scope is intentionally limited to **Odoo 19 Community source** — not Enterprise-only apps, not Odoo Studio, and not private Odoo Online feature assumptions.

## What this repo covers

- The modern **JSON-2 external API**: `POST /json/2/<model>/<method>`
- Legacy **XML-RPC** and **JSON-RPC** endpoints, including deprecation notes
- Authentication with Odoo API keys / bearer tokens
- How Odoo exposes models, public methods, ORM methods, access rights, and record rules
- API discovery via the Community `api_doc` addon
- Integration examples for common business objects: contacts, products, sales, invoices, inventory, CRM, projects
- Security and implementation gotchas for automation agents

## Important Odoo 19 Community conclusion

Odoo 19 Community source includes the `rpc` addon with:

- `addons/rpc/controllers/json2.py` — JSON-2 endpoint implementation
- `addons/rpc/controllers/xmlrpc.py` — legacy XML-RPC endpoints
- `addons/rpc/controllers/jsonrpc.py` — legacy JSON-RPC endpoint
- `addons/rpc/__manifest__.py` — auto-installed `RPC endpoints` addon

Odoo's hosted-plan documentation says JSON-2 availability is restricted on hosted Odoo Online pricing tiers. For this repo, the target is **self-hosted / source-level Odoo 19 Community Edition**. See [Deployment caveat: hosted plans vs self-hosted Community](docs/11-deployment-caveat-hosted-vs-self-hosted.md) for the practical distinction and test commands.

## Docs

1. [API surface overview](docs/01-api-surface.md)
2. [JSON-2 API deep dive](docs/02-json2-api.md)
3. [Legacy XML-RPC and JSON-RPC](docs/03-legacy-rpc.md)
4. [Authentication and API keys](docs/04-authentication-api-keys.md)
5. [ORM concepts that matter for the API](docs/05-orm-and-model-methods.md)
6. [Community business models and modules](docs/06-community-models.md)
7. [API discovery with `api_doc`](docs/07-api-discovery.md)
8. [Integration patterns and examples](docs/08-integration-patterns.md)
9. [Security checklist](docs/09-security-checklist.md)
10. [Source evidence log](docs/10-source-evidence.md)
11. [Deployment caveat: hosted plans vs self-hosted Community](docs/11-deployment-caveat-hosted-vs-self-hosted.md)

## Examples

- [Python JSON-2 client](examples/python/json2_client.py)
- [Python XML-RPC legacy client](examples/python/xmlrpc_legacy_client.py)
- [curl examples](examples/curl/json2.md)

## Source snapshot

- Odoo source: `odoo/odoo` branch `19.0`
- Inspected commit: `e5144dd38cb9161d8ebbf6a7d06f1698a20a4901`
- Research timestamp: `2026-05-18 18:49:48 UTC`

## Repo status

This is documentation and research. It does **not** contain credentials, API keys, or private customer data.
