# 11 — Deployment caveat: hosted plans vs self-hosted Community

The key caveat for this repo is that **source-code capability** and **hosted-product availability** are not the same thing.

This repo documents Odoo 19 **Community Edition source behavior**, especially for self-hosted deployments. Odoo's hosted products may apply commercial plan restrictions that override what is visible in the public source tree.

## Short version

- **Self-hosted Odoo 19 Community:** the Community source includes JSON-2 through the auto-installed `rpc` addon.
- **Odoo Online hosted plans:** Odoo documentation says JSON-2 external API access is restricted to **Custom** pricing plans and unavailable on lower hosted plans such as One App Free or Standard.
- **Odoo.sh / Custom / self-hosted Enterprise:** JSON-2 is the expected path, but actual availability still depends on modules, plan, configuration, and permissions.

## Why this matters

Saying “Odoo 19 Community includes JSON-2” means the route implementation exists in the source tree:

- `addons/rpc/controllers/json2.py`
- route: `POST /json/2/<model>/<method>`
- auth: `Authorization: bearer <API_KEY>`
- route type: `json2`

It does **not** mean every Odoo-hosted subscription exposes that endpoint to external callers.

Hosted Odoo Online is a packaged commercial product. Odoo can disable, restrict, or gate external API access by plan even if similar code exists in the underlying product line.

## Deployment matrix

### Self-hosted Odoo 19 Community

Best assumption for this repo.

Expected:

- JSON-2 route exists if the `rpc` addon is installed/auto-installed.
- API keys are available through Odoo users/account security.
- Access is controlled by normal Odoo security: groups, model ACLs, record rules, field groups, and company context.
- Reverse proxy, dbfilter, database selection, and installed modules can still affect behavior.

Recommended integration target:

- JSON-2 first.
- Use `/web/version` to check server version.
- Use `/doc-bearer/*` from `api_doc` on development/staging if API discovery is needed.

### Odoo Online One App Free / Standard

Odoo documentation indicates JSON-2 external API access is not available on these hosted tiers.

Possible outcomes:

- `/json/2/...` returns `404`, `403`, or another access/plan-style error.
- API key generation may be unavailable or limited.
- Legacy XML-RPC may or may not remain available depending on Odoo's hosted policy at the time.

Recommended integration target:

- Do not assume JSON-2 works.
- Run the practical availability test below.
- If blocked, either upgrade/change hosted plan, move to Odoo.sh/Custom, or self-host Community.

### Odoo Online Custom

Expected to support the external JSON-2 API according to Odoo's hosted-plan language, but still verify on the actual database.

Recommended integration target:

- JSON-2.
- Confirm database/header behavior.
- Confirm bot-user permissions.

### Odoo.sh

Usually closer to managed self-hosting than Standard Odoo Online.

Expected:

- JSON-2 should be the right integration direction for Odoo 19.
- Actual availability depends on branch/version/modules/config.

Recommended integration target:

- JSON-2, verified in staging first.

### Self-hosted Odoo Enterprise

Out of scope for this repo, but likely similar for the core RPC layer plus Enterprise-only models/apps.

Recommended integration target:

- JSON-2 for core model access.
- Enterprise modules require separate documentation/discovery.

## Practical availability test

First check the server version:

```bash
curl -sS "$ODOO_URL/web/version"
```

Then test JSON-2 with a harmless authenticated call:

```bash
curl -i -X POST "$ODOO_URL/json/2/res.users/context_get" \
  -H "Authorization: bearer $ODOO_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Odoo-Database: $ODOO_DB" \
  -d '{}'
```

Interpretation:

- `200 OK` with JSON body: JSON-2 is available and the key works.
- `401` / `403`: authentication, key, permission, or plan restriction problem.
- `404`: wrong route, missing/blocked route, missing database selection, dbfilter issue, or hosted-plan restriction.
- `422`: route exists, but the request shape or method parameters are wrong.
- HTML error page: likely wrong endpoint, proxy behavior, database-selection issue, or hosted product blocking before JSON-2 dispatch.

For multi-database servers, include:

```http
X-Odoo-Database: <database-name>
```

If host/dbfilter already selects a single database, this header may not be required.

## Recommended wording for this repo

Use this phrasing:

> Odoo 19 Community source includes the JSON-2 implementation through the `rpc` addon. This repo targets self-hosted/source-level Community Edition. Hosted Odoo Online plans may restrict external API access by commercial tier; verify JSON-2 availability on the actual deployment before building against it.

Avoid this phrasing:

> All Odoo 19 Community users can use JSON-2.

That is too broad because “Community source” and “Odoo-hosted product plan” are different layers.

## Integration decision tree

1. Are you running self-hosted Odoo 19 Community?
   - Yes: target JSON-2 and verify with `/web/version` + `/json/2/res.users/context_get`.
   - No: continue.
2. Are you on Odoo Online Custom or Odoo.sh?
   - Yes: target JSON-2, but verify on the actual database.
   - No: continue.
3. Are you on Odoo Online Standard or One App Free?
   - Assume JSON-2 may be blocked.
   - Test before building.
   - Consider Custom/Odoo.sh/self-hosted if API access is required.
4. Do you need compatibility with older Odoo versions?
   - Consider legacy XML-RPC temporarily, but plan migration because Odoo 19 deprecates it and Odoo 22 is scheduled to remove it.

## Bottom line

For **Hermes-Odoo**, the clean assumption is:

> Target self-hosted Odoo 19 Community and use JSON-2 as the primary API.

For any hosted Odoo instance:

> Treat JSON-2 as a deployment capability to verify, not a guarantee from the source tree alone.
