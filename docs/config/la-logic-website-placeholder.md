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

Footer contact email:

- Removed from the bottom/footer of the placeholder page on 2026-05-22.
- The primary `Contact LA Logic` button still uses `mailto:ls@lalogic.co.za` unless changed later.

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

The current shared public host has multiple Odoo databases behind one hostname. A normal browser request to `https://www.simiansyndicate.co.za/` shows the Odoo database selector because Odoo cannot choose between `SimianSyndicate` and `lalogic` without host/database routing.

Current DNS/public behavior checked on 2026-05-22:

- `www.lalogic.co.za` resolves to the same public IP / dyndns target as the Odoo host.
- `https://www.lalogic.co.za/` currently presents the `www.simiansyndicate.co.za` TLS certificate, so browsers reject it as a certificate mismatch.
- If certificate verification is bypassed, `https://www.lalogic.co.za/` reaches Odoo but still shows `/web/database/selector`, not the LA Logic homepage.
- A read-only request with `X-Odoo-Database: lalogic` renders the LA Logic placeholder correctly, proving the page itself is fine and the failure is host/database routing.

Database-level metadata updated on 2026-05-22:

- `ir.config_parameter:web.base.url = https://www.lalogic.co.za`
- `ir.config_parameter:web.base.url.freeze = True`
- LA Logic company website = `https://www.lalogic.co.za`
- LA Logic website record branded as `LA Logic`

Required host/proxy fix:

1. In Nginx Proxy Manager, create or update a proxy host for `www.lalogic.co.za`.
2. Request/attach a Let's Encrypt certificate covering `www.lalogic.co.za`.
3. Route it to the Odoo upstream, same host/port as Simian's proxy host.
4. Ensure the request selects the `lalogic` database. The most direct proxy-level option is to add this custom header for the LA Logic proxy host:

```nginx
proxy_set_header X-Odoo-Database lalogic;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto https;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
```

For Simian's proxy host, avoid ambiguity by routing that host to `SimianSyndicate` similarly if needed:

```nginx
proxy_set_header X-Odoo-Database SimianSyndicate;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto https;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
```

Alternative Odoo-level option: configure Odoo `dbfilter` so hostnames map to one database, but this is awkward because `www.lalogic.co.za` maps cleanly to `lalogic` while `www.simiansyndicate.co.za` does not cleanly map to the mixed-case database name `SimianSyndicate`.

No secrets, passwords, API keys, exports, customer data, or private business records are stored in this document.
