# 06 — Community modules and business models

Odoo Community is modular. Installed addons determine which models and methods exist.

## Core/base

- `res.partner` — contacts, companies, customers, vendors
- `res.users` — users
- `res.company` — companies
- `res.currency` — currencies
- `ir.attachment` — files/binary attachments
- `ir.model`, `ir.model.fields` — model metadata
- `ir.config_parameter` — config parameters
- `ir.cron` — scheduled actions
- `ir.actions.*` — UI/server/report actions

## Products

- `product.template` — product template / commercial product
- `product.product` — variant-level product
- `product.category` — product categories
- `uom.uom` — units of measure
- `uom.category` — UoM categories

Typical API work:

- create/update products
- sync SKUs/barcodes
- set sale/purchase flags
- read inventory-facing product fields

## Sales

- `sale.order` — quotation/sales order
- `sale.order.line` — order line
- `sale.report` — reporting model

Typical API work:

- create quotation
- add lines via One2many commands
- confirm with `action_confirm`
- read order status/invoice/delivery links

## CRM

- `crm.lead` — leads and opportunities
- `crm.team` — sales teams
- `crm.stage` — pipeline stages

Typical API work:

- create lead/opportunity
- move stages
- assign salesperson/team
- mark won/lost via business methods where available

## Accounting/Invoicing

- `account.move` — invoices, bills, journal entries
- `account.move.line` — journal item/invoice line
- `account.payment` — payments
- `account.journal` — journals
- `account.account` — chart of accounts
- `account.tax` — taxes

Typical API work:

- create draft invoice
- add invoice lines
- post with `action_post`
- read payment state

Caution: accounting localization and compliance vary by country and installed localization modules.

## Inventory/stock

- `stock.picking` — transfers/receipts/deliveries
- `stock.move` — stock movement demand
- `stock.move.line` — detailed operations/reservations
- `stock.quant` — on-hand quantities
- `stock.location` — locations
- `stock.warehouse` — warehouses
- `stock.lot` — lots/serial numbers

Typical API work:

- read stock levels from `stock.quant`
- create internal transfers
- validate deliveries/receipts through business methods

Caution: do not fake stock state by writing state fields. Use Odoo workflows.

## Purchase

- `purchase.order`
- `purchase.order.line`

Typical API work:

- create RFQs/purchase orders
- confirm orders
- read incoming shipments and vendor bills

## Point of Sale

- `pos.order`
- `pos.order.line`
- `pos.session`
- `pos.config`

Typical API work:

- read POS orders
- sync products/prices
- reporting

Caution: POS has offline/session mechanics; avoid bypassing its intended flows.

## Manufacturing

- `mrp.production`
- `mrp.bom`
- `mrp.bom.line`
- `mrp.workorder`

Typical API work:

- create/confirm manufacturing orders
- read BoMs
- track production state

## Projects and timesheets

- `project.project`
- `project.task`
- `account.analytic.line` for timesheet-like records when installed

Typical API work:

- create/update tasks
- sync stages/deadlines/assignees
- read project progress

## Mail/chatter

- `mail.message`
- `mail.activity`
- `mail.followers`

Typical API work:

- post chatter messages through model methods
- create activities/reminders
- read communication history when permissions allow

## Website/ecommerce

Community source includes website and ecommerce-related modules, but exposed API flows may combine model calls with web controllers. For robust integrations, prefer model methods and official website controllers only when needed.

## Generated model inventory

See [`references/model-inventory-major-community.json`](../references/model-inventory-major-community.json) for a source-scan inventory of model classes from major Community modules.
