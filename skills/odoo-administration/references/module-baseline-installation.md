# Module Baseline Installation via JSON-2

Session-derived pattern from installing Odoo 19 Community baselines for two databases on one self-hosted instance.

## Context

Databases:

- `SimianSyndicate` — Simian Syndicate
- `lalogic` — LA Logic

Each database had its own dedicated `Hermes Admin` user and API key stored locally in the Hermes profile `.env`.

## Installed baseline example

Simian baseline plus extras:

- `contacts` — Contacts
- `crm` — CRM
- `sale_management` — Sales
- `account` — Invoicing / Accounting
- `l10n_za` — South Africa Accounting
- `stock` — Inventory
- `purchase` — Purchase
- `website_sale` — eCommerce

LA Logic baseline:

- `contacts` — Contacts
- `account` — Invoicing / Accounting
- `l10n_za` — South Africa Accounting
- `crm` — CRM
- `sale_management` — Sales
- `project` — Project

## Durable technique

Install through `ir.module.module` using each database's own JSON-2 API key. For record methods, call `button_immediate_install` with `ids=[module_id]`.

Before installing, resolve module records with `search_read` on `ir.module.module` and treat missing modules explicitly. If `sale_management` is unavailable in a variant, check whether `sale` exists as a fallback before giving up.

## Retry pitfall

Odoo may reject module installs with:

```text
Odoo is currently processing a scheduled action.
Module operations are not possible at this time, please try again later or contact your system administrator.
```

This is often transient. Do not mark the install failed immediately. Wait briefly and retry the blocked module operation. In the observed session, retrying after the scheduled action cleared allowed `sale_management` and `project` to install successfully.

## Post-install verification

For each database:

1. Re-read `ir.module.module` for all requested modules and verify `state = installed`.
2. Verify company basics (`res.company`) still match the intended company/country/currency.
3. If `account` is installed, verify `account.journal/search_read` works and journals exist.
4. Ensure the automation user has `Accounting / Administrator` or an appropriately narrow accounting group if future API configuration/inspection requires accounting model access.
5. Document the installed baseline in project docs without credentials or private business data.
