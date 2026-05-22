# Odoo Module Baseline

Last updated: 2026-05-22

This document records the installed day-one module baseline for the two separate Odoo 19 Community databases.

## Databases

- `SimianSyndicate` — Simian Syndicate
- `lalogic` — LA Logic

## Simian Syndicate baseline + extras

Installed modules:

| App | Technical module | Status | Reason |
|---|---:|---|---|
| Contacts | `contacts` | Installed | Customers, suppliers, companies, and partner records |
| CRM | `crm` | Installed | Lead/opportunity pipeline |
| Sales | `sale_management` | Installed | Quotations and sales orders |
| Invoicing / Accounting | `account` | Installed | Invoices, payments, journals, and accounting setup |
| South Africa Accounting | `l10n_za` | Installed | South African localization / ZAR accounting basis |
| Inventory | `stock` | Installed | Product stock, deliveries, receipts, and inventory valuation |
| Purchase | `purchase` | Installed | Supplier RFQs/purchase orders and incoming receipts |
| eCommerce | `website_sale` | Installed | Online product catalogue / checkout readiness |

Verification on 2026-05-22:

- All listed modules report `state = installed` through JSON-2.
- Company is `Simian Syndicate`, country `South Africa`, currency `ZAR`.
- Accounting journals are present, including Sales, Purchases, Bank, Inventory Valuation, and general journals.

## LA Logic baseline

Installed modules:

| App | Technical module | Status | Reason |
|---|---:|---|---|
| Contacts | `contacts` | Installed | Clients, vendors, companies, and contact records |
| Invoicing / Accounting | `account` | Installed | Client invoices, payments, journals, and accounting setup |
| South Africa Accounting | `l10n_za` | Installed | South African localization / ZAR accounting basis |
| CRM | `crm` | Installed | Client lead/opportunity pipeline |
| Sales | `sale_management` | Installed | Quotations and service sales orders |
| Project | `project` | Installed | Client/compliance work tracking |

Verification on 2026-05-22:

- All listed modules report `state = installed` through JSON-2.
- Company is `LA Logic`, country `South Africa`, currency `ZAR`.
- Accounting journals are present, including Sales, Purchases, Bank, and general journals.
- `Hermes Admin` was added to `Accounting / Administrator` so accounting models can be inspected/configured through the API.

## Deferred modules

Deferred unless explicitly needed:

- POS / `point_of_sale`
- Manufacturing / `mrp`
- Repairs
- Fleet
- Enterprise-only document/sign/helpdesk features, unless the deployment gains those apps separately

## Notes

- Installations were performed via each database's dedicated `Hermes Admin` JSON-2 API key.
- No API keys, passwords, database dumps, or private customer/business data are stored in this document.
