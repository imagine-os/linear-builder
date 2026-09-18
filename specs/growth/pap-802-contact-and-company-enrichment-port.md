---
identifier: "PAP-802"
title: "Contact and company enrichment port: provider adapter interface with a fixture adapter, domain-based company enrichment, email verification, consent-aware field writes and cost caps"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Acquisition analytics"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-111", "PAP-790"]
blocks: []
key: "r4/growth/contact-enrichment-port"
url: "https://linear.app/paperos/issue/PAP-802/contact-and-company-enrichment-port-provider-adapter-interface-with-a"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:46.611Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-802: Contact and company enrichment port: provider adapter interface with a fixture adapter, domain-based company enrichment, email verification, consent-aware field writes and cost caps

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

A lead that arrives as an email address becomes useful when the company, size and industry are filled in. Attio and HubSpot enrich automatically; PaperOS does it behind a port so Clearbit, Apollo, Hunter or an OSS lookup can be swapped, with a fixture adapter for CI and hard spend caps.

**Scope**

In: `EnrichmentPort { enrichCompany(domain), enrichPerson(email), verifyEmail(email), capabilities() }` with `fixture` adapter (deterministic data for demo domains), `clearbit` and `apollo` adapters in `dryRun` until keys exist (NJ), `mx` adapter for verification without a vendor; `enrichment_result` cache table with TTL; write policy: only fills empty fields unless `overwrite`, records `source: enrichment:<provider>` per field in `custom.__sources`; triggers on `crm.contact.created` and manual 'Enrich' action; monthly cost cap per tenant via PAP-111-style counters; settings page.

Out: people-search prospecting lists (purchased data is out of scope for compliance), enrichment of personal data beyond business contact fields.

**Spec**

* Only business fields (company name, domain, industry, size band, location, logo, job title) are written; personal social profiles are not fetched by default.
* Results cached 90 days per key; the same domain is never billed twice in a period.
* Verification status writes `crm_contact.email_status` (`valid|risky|invalid|unknown`) used by PAP-405 to skip invalid sends.

**Interface contract**

Provides: `EnrichmentPort`, adapters registry, `crm.enrich`, cache table, field source annotations, settings. Consumes: CRM schema, cost controls pattern (PAP-111), jobs (PAP-43), secrets (PAP-17), outbound suppression on invalid (PAP-405, soft).

**Definition of done**

* Fixture adapter end to end; `mx` verification tests with recorded DNS; cost cap trips in a test; screenshots at 375, 1024 of the settings and the enriched company card.
* `docs/growth/enrichment.md` with the vendor comparison and privacy note; CHANGELOG.

**Test plan**

* Unit: write policy (empty-only versus overwrite), cache TTL, cap counters, status mapping.
* E2E: create a contact at a demo domain, see the company card fill from the fixture adapter, hit the cap and see the pause banner.

**Demo**

Reviewer adds `ana@acme.example`, watches Acme's industry and size appear with a source badge, then runs verify and sees `valid`. Under one minute.

**Edge cases**

* Provider disagrees with user-entered data: never overwritten; a suggestion chip offers it.
* Domain is a free mail provider: company enrichment skipped.
* Vendor 429: backoff; no partial writes.

**Dependencies**

Hard: PAP-790, PAP-111. Soft: PAP-43, PAP-17, PAP-405.

**Agent**

Builder: Beacon (CRM Builder). Reviewer: Sentinel (Security Auditor for data minimisation).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/growth/crm-schema-routers-page-specs` = PAP-790.
