# Odoo Multi-Database Website Routing

Session-derived notes from routing Simian Syndicate and LA Logic on one Odoo 19 Community host behind Nginx Proxy Manager.

## Core lesson

Odoo Website `domain`, company website, and `web.base.url` are database-level records/parameters. They are **not enough** to select the database on a multi-database host, because Odoo must select the database before it can read those records.

If a public request reaches a host with multiple databases and no host/db routing, Odoo shows `/web/database/selector` even when each database has a Website app configured.

## Fast diagnostic pattern

Check the public domains without any special header:

```bash
curl -k -L https://www.example-a.co.za/ | grep -E "database/selector|<title>"
curl -k -L https://www.example-b.co.za/ | grep -E "database/selector|<title>"
```

Then force the database header from the client side:

```bash
curl -k -L https://www.example-a.co.za/ \
  -H 'X-Odoo-Database: DatabaseA'

curl -k -L https://www.example-b.co.za/ \
  -H 'X-Odoo-Database: database_b'
```

Interpretation:

- Public requests show selector, but forced-header requests render the right sites: website content is fine; proxy/database selection is missing.
- One public host renders the other company's site: the wrong database-selection header or dbfilter mapping is being applied to that proxy host.
- TLS certificate mismatch on the new domain: Nginx Proxy Manager needs a certificate for that hostname before browser testing is meaningful.

## Nginx Proxy Manager fix pattern

Create separate proxy hosts for each public hostname. Both can forward to the same Odoo upstream, but each must select a different database.

For the Simian host:

```nginx
proxy_set_header X-Odoo-Database SimianSyndicate;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto https;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
```

For the LA Logic host:

```nginx
proxy_set_header X-Odoo-Database lalogic;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto https;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
```

Important: verify that the Simian proxy host does **not** contain the LA Logic database header and vice versa.

## Alternative: Odoo dbfilter

Odoo `dbfilter` can route hostnames to databases, but it is awkward when public hostnames and database names do not match cleanly, especially with mixed-case database names such as `SimianSyndicate` and lowercase names such as `lalogic`.

For this setup, per-proxy-host `X-Odoo-Database` headers are simpler and more explicit.

## Verification target

After the proxy change, clean browser sessions should show:

- `https://www.simiansyndicate.co.za/` -> Simian site, no selector
- `https://www.lalogic.co.za/` -> LA Logic site, no selector

Also verify incognito/private mode to rule out stale Odoo session cookies.
