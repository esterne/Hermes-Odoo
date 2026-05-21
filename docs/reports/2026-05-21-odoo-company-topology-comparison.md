# Odoo Topology Report: One Multi-Company Database vs Two Separate Databases

**Date:** 2026-05-21  
**Project:** Simian Syndicate + LA Logic Odoo 19 Community setup  
**Repo:** `esterne/Hermes-Odoo`  
**Current live database:** `SimianSyndicate`  
**Current installed business app baseline:** Website + Invoicing (`account`) on `SimianSyndicate`

---

## Executive summary

There are two viable ways to run Simian Syndicate and LA Logic on the current Odoo 19 Community installation:

1. **One Odoo database with two companies**  
   Add LA Logic as a second company inside the existing `SimianSyndicate` database.

2. **One Odoo instance with two separate databases**  
   Keep `SimianSyndicate` as-is and create a new `LALogic` database.

New context changes the recommendation materially: **LA Logic is a financial compliance company**. That makes separation, auditability, and independent recovery more important than speed of setup.

I now recommend **Option B: one Odoo instance with two separate databases**: keep `SimianSyndicate` as the Simian Syndicate database and create a separate `LALogic` database for LA Logic. The practical friction around database creation is real, but it is worth solving rather than accepting avoidable compliance/data-boundary risk.

---

## Current context

| Area | Current state |
|---|---|
| Odoo version | Odoo Community Edition 19, version endpoint reports `19.0-20260504` |
| Hosting | Zimaboard, publicly served at `https://www.simiansyndicate.co.za` |
| Proxy | Nginx Proxy Manager in front of Odoo |
| Existing database | `SimianSyndicate` |
| Existing company | `Simian Syndicate` |
| Planned second company | `LA Logic` |
| Installed business apps | Invoicing installed in `SimianSyndicate` |
| Bot/API access | `Hermes Admin` has JSON-2 API access to `SimianSyndicate` |
| Constraint | Creating a new database requires database manager/master password or container/server access |

---

## Side-by-side comparison

| Dimension | Option A: One database, two companies | Option B: Two separate databases |
|---|---|---|
| Basic shape | `SimianSyndicate` database contains both `Simian Syndicate` and `LA Logic` as companies | `SimianSyndicate` database for Simian; new `LALogic` database for LA Logic |
| Setup effort now | **Low**. Can be done from inside Odoo/API once permissions are right | **Medium/high** right now. Requires database manager/master password or container access |
| Speed to proceed | **Fastest** | Blocked until Dockhand/server access or DB manager password is available |
| Data isolation | Good if configured carefully, but not absolute | Strongest. Databases are physically separate |
| Risk of accidental data mixing | **Medium**. Products/contacts can be shared by default unless company restrictions are set | Low. Records cannot cross database boundaries |
| User experience | Best. Same login/session, company switcher in Odoo | More separate. Users/API keys may need to exist in both databases |
| Shared contacts/products | Easy and sometimes useful | Requires duplication or integration/export/import |
| Accounting separation | Supported by Odoo multi-company; invoices/bills link to active company | Naturally separate by database |
| Consolidated reporting | Easier inside one Odoo database | Requires external aggregation or manual export/reporting |
| Inter-company transactions | Odoo supports inter-company flows inside one database | Requires custom integration between databases |
| Backups/restores | One database backup contains both businesses | Independent backup/restore per company |
| Disaster recovery | Restoring one company means restoring the whole DB unless using selective export/import | Can restore LA Logic without touching Simian, and vice versa |
| Security model | More nuanced. Requires correct company access, record rules, active company context | Simpler. Database boundary is the main security boundary |
| App/module configuration | One module set shared by the database, with company-specific settings where Odoo supports it | Each database can have its own modules/settings |
| Email/templates/sequences | Can be company-specific, but must be checked carefully | Naturally separate |
| Website/domain handling | Multiple websites/companies possible, but needs care | Simpler conceptual split per database/domain |
| Future migration | Moving LA Logic out later is possible but not trivial | Already isolated from day one |
| Best fit | Same owner/admin, overlapping users, shared contacts/products/reporting, fast setup | Separate operations, different users, strong compliance/isolation, independent backups |

---

## What Odoo’s own model implies

Odoo explicitly supports multiple companies in one database. In Odoo 19:

- A **company** is an independent business entity with its own legal identity, financial records, and operational settings.
- Users can be allowed into multiple companies and switch active company context from the company selector.
- Documents like quotations, invoices, and vendor bills are linked to the active company when created.
- Products and contacts are generally shareable/global by default unless restricted with a company field.
- Inter-company transactions can automate flows between companies in the same database.

The important catch: multi-company is powerful because it shares a database. That is also the risk. You get convenience and consolidated reporting, but you must be intentional about access rights, defaults, journals, sequences, contacts, products, and user company access.

Sources:

- Odoo 19 Companies docs: https://www.odoo.com/documentation/19.0/applications/general/companies.html
- Odoo 19 Multi-company docs: https://www.odoo.com/documentation/19.0/applications/general/companies/multi_company.html
- Odoo 19 Developer multi-company guidelines: https://www.odoo.com/documentation/19.0/developer/howtos/company.html

---

## Practical implications for Simian Syndicate and LA Logic

### If we choose one database / two companies

We would keep the existing `SimianSyndicate` database and add:

- Company: `LA Logic`
- LA Logic company profile, address, logo, email domain, website, tax details
- LA Logic accounting journals/sequences/document layout
- User access rules so each user has only the companies they should see
- Separate document sequences if needed, e.g. invoice prefixes for each company
- Clear policy for shared vs restricted contacts/products

This option lets you start configuring LA Logic immediately without waiting for Dockhand or database-manager access.

The main work is not technical deployment; it is careful Odoo configuration.

### If we choose two separate databases

We would keep:

- `SimianSyndicate` for Simian Syndicate
- `LALogic` for LA Logic

This remains cleaner from a hard-boundary perspective, but we currently need one of:

- Odoo database manager/master password, or
- container/server access via Dockhand/SSH, or
- direct PostgreSQL/Odoo deployment control.

Once available, this is still a very solid architecture. It is just slower and more operationally involved right now.

---

## Risk analysis

### Option A risks: one database, two companies

| Risk | Severity | Mitigation |
|---|---:|---|
| Accidental cross-company visibility | Medium/high | Restrict user company access; audit record rules; avoid broad admin use for daily work |
| Shared contacts/products become messy | Medium | Decide which records are global vs company-specific before importing data |
| Wrong active company when creating documents | Medium | Train users to check the company selector; use company-specific sequences/layouts |
| Company-specific settings missed | Medium | Use a setup checklist per company |
| Harder future split | Medium/high | Keep LA Logic data clean from day one; avoid unnecessary shared records |

### Option B risks: two separate databases

| Risk | Severity | Mitigation |
|---|---:|---|
| Slower setup due to server access requirements | Medium | Wait for Dockhand or use database manager password |
| Duplicate configuration work | Medium | Create setup runbooks/checklists and reuse module baseline |
| No built-in consolidated reporting | Medium | Use exports, spreadsheets, BI, or future integration |
| Duplicate contacts/products | Low/medium | Accept duplication or build sync later if needed |
| More API/user/key management | Low/medium | Create a named Hermes API user/key per database |

---

## Decision matrix

Scoring: 1 = weak, 5 = strong.

| Criterion | Weight | Option A: one DB / two companies | Weighted | Option B: two DBs | Weighted |
|---|---:|---:|---:|---:|---:|
| Fastest path to working LA Logic setup | 3 | 5 | 15 | 2 | 6 |
| Hard data isolation | 5 | 3 | 15 | 5 | 25 |
| Compliance/audit boundary clarity | 5 | 2 | 10 | 5 | 25 |
| Ease of admin/user management | 3 | 5 | 15 | 3 | 9 |
| Independent backup/restore | 5 | 2 | 10 | 5 | 25 |
| Consolidated reporting | 2 | 5 | 10 | 2 | 4 |
| Lower chance of accidental cross-company leakage | 5 | 3 | 15 | 5 | 25 |
| Ease of inter-company workflows | 1 | 5 | 5 | 2 | 2 |
| Simplicity of deployment today | 3 | 5 | 15 | 2 | 6 |
| Long-term portability/sell/spin-off | 4 | 2 | 8 | 5 | 20 |
| **Total** |  |  | **118** |  | **147** |

With LA Logic treated as a financial compliance company, Option B wins clearly. The scoring shifts because compliance/audit clarity and independent recovery matter more than immediate setup speed.

---

## Recommendation

### Recommended next step: create `LALogic` as a separate database

I recommend we **do not add LA Logic as a second company inside `SimianSyndicate`**. LA Logic should get its own Odoo database: `LALogic`.

Why:

1. **Financial compliance work deserves a hard boundary.** A separate database gives cleaner separation than record rules and company context inside one shared database.
2. **Auditability is easier to explain.** “LA Logic has its own database, backups, users, API keys, and access policy” is clearer than “it shares a database, but Odoo rules separate the records.”
3. **Independent backup/restore matters.** If LA Logic data needs to be restored, exported, retained, or archived, it should not affect Simian Syndicate.
4. **Future risk is lower.** If LA Logic gains different staff, clients, compliance obligations, or operational processes, the architecture is already prepared.
5. **The current setup friction is temporary.** Dockhand/server access or the Odoo database manager password solves database creation once. Data mixing risk, by contrast, becomes harder to unwind after real transactions exist.

### Recommendation boundary

Only choose one shared multi-company database if LA Logic is genuinely lightweight, internally administered only, and there is no meaningful compliance/client-data separation requirement. Based on the financial compliance context, that does **not** sound like the right assumption.

---

## Proposed implementation plan

### Phase 1 — Wait for database creation capability

Use one of:

- Dockhand/container terminal access;
- Odoo database manager/master password; or
- direct server/SSH/PostgreSQL/Odoo deployment access.

Do not create LA Logic as a company inside `SimianSyndicate` just to move faster.

### Phase 2 — Create the separate database

Create:

```text
Database: LALogic
Company: LA Logic
```

Keep `SimianSyndicate` dedicated to Simian Syndicate.

### Phase 3 — Configure LA Logic from a clean baseline

For LA Logic:

- Legal/company name
- Address
- Email
- Website/domain if applicable
- Logo
- Country: South Africa, unless different
- Currency: ZAR, unless different
- Document layout
- Invoice/report footer details
- Accounting/invoicing baseline
- Dedicated Hermes API user/key for the `LALogic` database

### Phase 4 — Security and audit boundary

- Separate admin/API users per database
- Separate backups per database
- Separate access review for LA Logic
- No shared credentials between databases
- No LA Logic records in `SimianSyndicate` except deliberate non-sensitive references, if ever needed

### Phase 5 — Optional reporting integration later

If you later need cross-company reporting, build it explicitly via exports, BI/spreadsheets, or an integration layer. Do not trade away compliance separation just to get consolidated reporting on day one.

---

## Rollback / exit plan

The safest rollback plan is to avoid entering LA Logic data into `SimianSyndicate` in the first place.

Before creating `LALogic`:

1. Take/verify a backup of the current Odoo/PostgreSQL state.
2. Confirm the database manager/master password or container command path.
3. Create `LALogic` as a separate database.
4. Test with disposable draft records inside `LALogic`.
5. Only after verification, begin real LA Logic configuration and data entry.

If someone accidentally creates LA Logic records inside `SimianSyndicate`, stop before real transactions accumulate and remove/archive the test records. Do not normalize that as the production topology.

---

## Final recommendation in one sentence

**Create LA Logic as its own separate `LALogic` database, because financial compliance work makes separation, auditability, and independent backup/restore more important than the speed advantage of a shared multi-company database.**
