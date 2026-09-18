---
identifier: "PAP-888"
title: "Author vertical packs wave 2 on the pack format: salon and spa, gym and studio, law firm, real estate brokerage, with pages, views, pipelines, services, chart of accounts, terminology, workflows, documents and sample data"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Operations packs, marketplace and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-126", "PAP-426", "PAP-427", "PAP-879", "PAP-883"]
blocks: ["PAP-889", "PAP-890"]
key: "r4/commerce/vertical-packs-wave2"
url: "https://linear.app/paperos/issue/PAP-888/author-vertical-packs-wave-2-on-the-pack-format-salon-and-spa-gym-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:03.670Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 5
dueDate: null
cycle: null
---

# PAP-888: Author vertical packs wave 2 on the pack format: salon and spa, gym and studio, law firm, real estate brokerage, with pages, views, pipelines, services, chart of accounts, terminology, workflows, documents and sample data

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build L

**Goal**

Extend the five packs (PAP-427) with four more on the same `pack.yaml` format (PAP-426): salon and spa (services, resources, booking page, retail shelf, loyalty), gym and studio (memberships, classes, check-in), law firm (matters as projects, time billing, documents and e-sign, restricted trust accounts), real estate brokerage (listings as a dataset with map view, showings as bookings, commission splits, transaction checklists), each with terminology (PAP-126), workflows, documents and sample data.

**Scope**

In: `packs/salon`, `packs/gym`, `packs/law`, `packs/real-estate`: `pack.yaml` with `tables[]`, `views[]`, `pipelines[]`, `services[]`, `resources[]`, `chartOfAccounts[]`, `pages[]`, `navigation`, `docs[]`, `workflows[]`, `documents[]`, `characters[]` (assistant starters), `sampleData/*.jsonl`, `roles[]`, `entitlements`, `modules` (enable engagement, commerce, workflows as needed). Terminology entries in `industries.yaml` (PAP-126) for each (client/guest/member/matter/listing) and default compliance profile hints (law: retention 7 years, trust account restrictions). Pack docs: a one-page "what you get" per pack rendered in the template gallery (PAP-428) with screenshots from the conformance run; Scout's Template Packager sub-character authors, Ledger reviews chart of accounts.

Out: New platform features: a pack may only compose existing objects; gaps found while authoring are filed as issues on the owning project. Localised legal templates (documents are marked `review required`).

**Spec**

* Every pack applies to a blank tenant with `--dry-run` producing an empty diff on re-apply (idempotent) and lints clean (PAP-426 lint minimums plus terminology coverage ≥ 90 percent of renamed concepts)
* Sample data is flagged `demo: true` and removable in one action; no real names or addresses
* Each pack declares its module dependencies; applying to a tenant without a module offers to enable it (PAP-266) or skips that content with a report
* Home dashboard per pack composed from PAP-173 blocks; at least one starter workflow and one document template per pack

**Interface contract**

Provides: four pack directories, terminology entries, gallery cards, starter characters, sample data. Consumes: pack format and applier (PAP-426), the five packs (PAP-427), template gallery (PAP-428), business profile (PAP-126), module toggles (PAP-266), commerce, engagement, workflows and assistant objects (soft: content skipped when a module is absent). Consumed by: PAP-890, PAP-428 gallery, PAP-208 migration agent (recommends packs), PAP-429 golden path (new canned ideas).

**Definition of done**

* Four packs apply, lint and re-apply idempotently in CI; gallery shows them with screenshots; a law demo tenant runs a matter from intake form to signed engagement letter to invoice using only pack content
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Static: pack lint; terminology coverage; schema validation of every file.
* Integration: apply to blank tenant, dry-run diff empty on second apply, remove sample data leaves structure.

**Demo**

Apply the salon pack to a blank tenant from the gallery, open the booking page, sell a product at the shelf POS, and show the terminology (guest, treatment) across navigation and notifications.

**Edge cases**

* Pack applied to a tenant that already has a `customers` table: conflict strategy `merge` maps fields by name and reports what it could not map (PAP-426 strategies)

**Dependencies**

PAP-426, PAP-427 (hard), PAP-126, PAP-428 (hard), commerce catalog and projects (soft), engagement booking and memberships (soft), workflows (soft).

**Agent**

Builder: Scout. Reviewer: Ledger (Bookkeeper).

**Size**

L: two sessions; split at the first natural seam if the first session does not reach the integration test.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/commerce/pack-conformance-tests` = PAP-890.
