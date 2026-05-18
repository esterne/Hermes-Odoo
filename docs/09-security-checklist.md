# 09 — Security checklist for Odoo API automation

## Bot user

- [ ] Dedicated user per integration.
- [ ] Minimum required groups only.
- [ ] No shared admin API key.
- [ ] Key has a clear name and expiration.
- [ ] Key is rotated before expiry.
- [ ] Key stored in a secret manager or environment variable, never Git.

## Access control

- [ ] Confirm `ir.model.access` permissions for each target model.
- [ ] Test record rules with the bot user, not admin.
- [ ] Check multi-company context and `allowed_company_ids`.
- [ ] Avoid `sudo()` in custom public methods unless absolutely necessary.
- [ ] Field-level `groups` restrictions are understood.

## Public methods

Odoo warns that public methods are callable via RPC. Therefore:

- [ ] Helper methods that are not API-safe start with `_`.
- [ ] Public methods validate state and permissions.
- [ ] Public methods do not trust raw `ids` or input domains.
- [ ] Business methods use ORM access checks.

## Data safety

- [ ] Use business methods instead of writing state fields.
- [ ] Make writes idempotent.
- [ ] Avoid multi-call workflows that require atomicity.
- [ ] Validate values against Odoo metadata before bulk writes.
- [ ] Run destructive syncs in staging first.

## Network/security

- [ ] HTTPS only.
- [ ] Reverse proxy strips/limits unwanted headers.
- [ ] Request size/timeouts are sane.
- [ ] Logs do not print API keys or full Authorization headers.
- [ ] IP allowlisting if practical.

## Observability

- [ ] Log external request IDs.
- [ ] Log Odoo model, method, and returned IDs.
- [ ] Log errors without secrets.
- [ ] Alert on repeated authentication failures.
- [ ] Track key expiry.

## Custom modules

- [ ] No SQL string interpolation.
- [ ] Use ORM domains or parameterized SQL wrappers.
- [ ] Use `ast.literal_eval`/JSON parsing instead of `eval`.
- [ ] Escape/sanitize web content correctly.
- [ ] Add integration tests for public API methods.
