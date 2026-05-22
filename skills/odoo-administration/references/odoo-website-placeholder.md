# Odoo Website Placeholder via JSON-2

Session-derived pattern from building a simple LA Logic placeholder site in an Odoo 19 Community multi-database deployment.

## When useful

Use this when Erwin asks to create or replace a simple Odoo Website landing/placeholder page, especially before a proper domain/dbfilter route exists.

## Key pattern

1. Install Website module in the target database:
   - module: `website`
   - install through `ir.module.module.button_immediate_install` using that database's dedicated API key.
2. Inspect website records:
   - `website.search_read([], fields=['name','domain','company_id','homepage_url'])`
   - `website.page.search_read([['url','=','/']], fields=['name','url','website_id','is_published','view_id'])`
   - `website.menu.search_read([['website_id','=',website_id]], fields=['name','url','parent_id','sequence','website_id'])`
3. Rename the website record and set homepage URL:
   - `website.write(ids=[website_id], vals={'name': '<Brand>', 'homepage_url': '/'})`
4. Find the website-specific homepage page/view when present:
   - Prefer `website.page` where `url == '/'` and `website_id == website_id`.
   - Its `view_id` points to the QWeb `ir.ui.view` to replace.
5. Replace `ir.ui.view.arch_db` with a complete QWeb homepage:
   - Use `<t name="Homepage" t-name="website.homepage"><t t-call="website.layout" pageName.f="homepage">...`.
   - Put custom HTML/CSS inside `<div id="wrap" class="oe_structure ...">`.
6. Publish the page:
   - `website.page.write(ids=[page_id], vals={'name':'<Brand>', 'is_published': True})`
7. Update menus if needed:
   - Rename top menu/root and home/contact entries through `website.menu.write`.

## Hiding stock Odoo chrome for a placeholder

If the default Website header/footer shows demo phone numbers, demo links, Odoo branding, or stock footer content, a fast placeholder-safe workaround is to hide them in page CSS:

```css
#top,
#bottom {
  display: none !important;
}

.o_skip_to_content:not(:focus) {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
}
```

The skip-link rule keeps accessibility behavior while preventing a visible default blue browser link at the top of the page.

## Verification in multi-database hosting

When multiple Odoo databases share one hostname, normal public requests may show the database selector. For read-only verification of the target database, fetch with an explicit database header:

```python
requests.get('https://host.example/', headers={'X-Odoo-Database': '<db-name>'})
```

Verify:

- page title is brand-specific
- placeholder headline/content appears
- default Odoo header/footer are not visible in a browser screenshot
- no demo phone/email/footer/Odoo branding remains visible

## Routing caveat

`?db=<db-name>` on `/` may redirect to login or `/odoo` depending on Odoo routing and session state. Do not treat that as page failure if the header-selected database renders correctly.

For a proper public website, configure a dedicated domain/subdomain and Odoo/proxy dbfilter/database selection so that the desired database is automatically selected for that host.

## Durable documentation

Record the result in the project repo, but do not store API keys, passwords, dumps, customer data, or private business records in the documentation. If the note is a persistent user-facing artifact, store it via `ens-files` too.
