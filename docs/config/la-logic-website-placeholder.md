# LA Logic Website Placeholder

Last updated: 2026-05-22

## Summary

A simple, stylish placeholder homepage was built inside the `lalogic` Odoo database after installing the Website app.

## Odoo database

- Database: `lalogic`
- Website record: `LA Logic`
- Homepage URL: `/`
- Homepage page: `LA Logic`
- Homepage view: website-specific `website.homepage` view, rendered through `website.layout`

## Installed app

- Website / `website`

## Design direction

The placeholder uses a Stripe-inspired financial/professional visual language:

- clean white and soft gradient background
- deep navy typography
- purple/magenta accent mark and CTAs
- lightweight, spacious hero headline
- elevated status card
- three simple focus cards
- minimal dark footer

## Homepage content

Hero headline:

> Clear financial logic for serious operators.

Intro copy:

> LA Logic is preparing a focused digital home for accounting, compliance, and operational finance work. The full site is coming soon — for now, we are keeping things simple, sharp, and useful.

Focus areas:

- Compliance-first
- Operational clarity
- Built to grow

Contact email displayed:

- `ls@lalogic.co.za`

## Odoo default chrome

The default Odoo website header/footer were visually hidden on this page so the placeholder does not show the stock Odoo menu, demo phone number, demo footer links, or Odoo branding.

The accessibility skip link is hidden until keyboard focus.

## Verification

Verified on 2026-05-22 by fetching the LA Logic website with `X-Odoo-Database: lalogic`:

- page title renders as `LA Logic | LA Logic`
- homepage contains the LA Logic placeholder content
- default Odoo header/footer are no longer visible in the rendered page
- visual screenshot check confirmed the page is clean, polished, and not broken

## Routing note

The current shared public host still has multiple Odoo databases behind one hostname. A normal browser request to `https://www.simiansyndicate.co.za/` may show the database selector unless a database is selected by the proxy/dbfilter/session.

For a proper public LA Logic website, next routing step is to point a LA Logic domain/subdomain at Odoo and configure Odoo/proxy database selection so that the `lalogic` database is selected automatically for that host.

No secrets, passwords, API keys, exports, customer data, or private business records are stored in this document.
