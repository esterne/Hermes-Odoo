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

My recommendation has shifted slightly from the original default. Given the current practical friction around server/container access and the fact that both businesses are owned/managed by you, I recommend a **short, deliberate pilot of Option A: one database with two companies**, provided we first tighten access rules and document exactly which records are shared vs company-specific.

If LA Logic needs hard isolation, independent backup/restore, or different future ownership/users/compliance, then we should stay with **Option B: two separate databases**. But for getting productive quickly, multi-company inside the existing database is probably the better next experiment.

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
| Fastest path to working LA Logic setup | 5 | 5 | 25 | 2 | 10 |
| Hard data isolation | 5 | 3 | 15 | 5 | 25 |
| Ease of admin/user management | 4 | 5 | 20 | 3 | 12 |
| Independent backup/restore | 4 | 2 | 8 | 5 | 20 |
| Consolidated reporting | 3 | 5 | 15 | 2 | 6 |
| Lower chance of accidental cross-company leakage | 5 | 3 | 15 | 5 | 25 |
| Ease of inter-company workflows | 2 | 5 | 10 | 2 | 4 |
| Simplicity of deployment today | 4 | 5 | 20 | 2 | 8 |
| Long-term portability/sell/spin-off | 3 | 2 | 6 | 5 | 15 |
| **Total** |  |  | **134** |  | **125** |

The score is close. Option A wins mainly because of current setup speed and lower operational friction. Option B wins on pure isolation and backup discipline.

---

## Recommendation

### Recommended next step: pilot multi-company inside the existing database

I recommend we **pilot LA Logic as a second company inside the existing `SimianSyndicate` database**, before committing to a separate `LALogic` database.

Why:

1. **We can proceed now.** Creating a second database is currently blocked by server/database-manager access.
2. **Both companies are under the same owner/admin context.** That makes shared users and central administration useful.
3. **Odoo multi-company is a first-class feature.** We should not avoid it purely out of fear, but we should configure it deliberately.
4. **LA Logic probably benefits from shared setup at this early stage.** Contacts, users, configuration patterns, and reporting may be easier in one DB while the system is still young.
5. **The current database is still early enough to adjust.** We have not imported years of messy operational data yet.

### Recommendation boundary

This recommendation changes if any of the following are true:

- LA Logic must be sold, transferred, or operated independently later.
- Different people should administer each business with strict data separation.
- You need independent backup/restore as a hard requirement.
- There is sensitive data in one company that should never be visible to users of the other.
- The companies will have very different modules, workflows, fiscal setups, or compliance needs.

If any of those become true, choose **two separate databases**.

---

## Proposed safe pilot plan

### Phase 1 — Add LA Logic as a company, not a branch

Create `LA Logic` under:

```text
Settings → Users & Companies → Companies
```

Do **not** create it as a branch of Simian Syndicate. It should be a separate company in the same database, not a subdivision.

### Phase 2 — Configure company basics

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

### Phase 3 — Accounting/Invoicing setup

- Confirm/initialize LA Logic journals
- Confirm invoice sequence prefix
- Confirm tax configuration
- Confirm bank/cash journals
- Test one draft customer invoice in LA Logic context
- Test one draft vendor bill in LA Logic context

### Phase 4 — Access control audit

- Create or update users with explicit company access
- Confirm daily users only see the companies they should see
- Confirm Hermes Admin can administer both companies only if desired
- Avoid using the all-powerful admin account for day-to-day operations

### Phase 5 — Shared-data policy

Decide this before importing real data:

| Record type | Recommended policy |
|---|---|
| Contacts/customers/vendors | Shared initially only if the same real-world entities deal with both companies; otherwise company-specific |
| Products/services | Shared only for truly common offerings; otherwise company-specific |
| Accounting journals | Company-specific |
| Taxes | Company-specific / localization-controlled |
| Invoice sequences | Company-specific, with clear prefixes |
| Email templates | Company-specific where customer-facing |
| Websites | Company-specific if both companies have public sites |

### Phase 6 — Go/no-go checkpoint

After the pilot, decide:

- If multi-company feels clean: continue with one DB.
- If it feels risky/confusing: stop, create `LALogic` as a separate database once Dockhand/server access is ready.

---

## Rollback / exit plan

Before adding real LA Logic transactions:

1. Take an Odoo database backup.
2. Add LA Logic company and configure basics.
3. Test with disposable draft records only.
4. If the setup feels wrong, archive/delete test records and revert from backup if necessary.

After real transactions exist, splitting LA Logic into a separate database becomes much harder. The pilot should therefore happen before serious data entry/imports.

---

## Final recommendation in one sentence

**Pilot LA Logic as a second company inside the existing `SimianSyndicate` database now, because it is faster and operationally simpler at this stage — but keep a clear exit criterion: if data isolation or independent restore matters more than shared administration, move back to the separate `LALogic` database plan before entering real transactional data.**
