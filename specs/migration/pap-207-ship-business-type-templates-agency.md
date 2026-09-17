---
identifier: "PAP-207"
title: "Ship business-type templates (agency, retail, SaaS, clinic, restaurant) as importable seed packs"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer", "Staff"]
milestone: "Business migrations"
state: "Backlog"
parent: null
children: ["PAP-426", "PAP-427", "PAP-428"]
blockedBy: ["PAP-114", "PAP-161", "PAP-199", "PAP-349"]
blocks: []
key: "migration/business-templates"
url: "https://linear.app/paperos/issue/PAP-207/ship-business-type-templates-agency-retail-saas-clinic-restaurant-as"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:39.257Z"
---

# PAP-207: Ship business-type templates (agency, retail, SaaS, clinic, restaurant) as importable seed packs

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Make one-size-fits-all real on day one: five business templates (agency, retail, SaaS, clinic, restaurant) as importable seed packs that create tables, views, pipelines, chart of accounts, page specs, sample data and starter docs, applied through the import framework so they preview, partially apply and roll back like any import. Umbrella for three work packages.

**Scope**

Work packages (full specs in the project document):

* **WP1 Pack format and applier** (M): `pack.yaml` Zod schema with `tables[]`, `views[]`, `pipelines[]`, `chartOfAccounts[]`, `segments[]`, `sequences[]`, `pages[]`, `navigation`, `docs[]`, `sampleData/*.jsonl` (`demo: true`), `roles[]`, `entitlements`; lint minimums; `template` `SourceConnector`; conflict strategy `skip|merge|rename`; `extends: base`; multi-pack composition; additive `upgrade`; the shared `base` pack.
* **WP2 Five packs** (M): realistic content per type, clinic fields `sensitive: true`, fictional sample data with stable ids, staff role presets, Playwright preview screenshots.
* **WP3 Gallery** (S): cards in PAP-22 onboarding and `_app/settings/templates`, dry-run diff, "apply with sample data", "Remove sample data" banner action, upgrade prompt.

Out: industry integrations (POS hardware, EHR), compliance certification (HIPAA notes only), localisation beyond English.

**Spec**

* Packs are semver; `apply` records `system: template:<type>@<version>` so re-apply offers upgrade; upgrade never removes.
* Sample data runs as a sub-run so removal is a framework rollback of that sub-run.
* Lint minimums per pack: 3 page specs, 6 views, 1 pipeline, 1 chart, 2 segments, 1 sequence, 1 doc.
* Order WP1 -> WP2 -> WP3 on `PAP-207/wp<n>-<slug>`.

**Interface contract**

Provides: `PackSchema`, `registerConnector('template')`, `lintPack()`, `planUpgrade()`, CLI `pnpm template lint|apply|upgrade`, five packs with previews, `TemplateStep` for PAP-22, route `_app/settings/templates`, components `TemplateCard`, `PackDiff`, `SampleDataBanner`. Consumes: PAP-199 engine, dry run and `RunReport`; PAP-161 field and view schema; PAP-114 page specs; PAP-117 navigation; PAP-179 accounts; PAP-187 pipelines; PAP-191 sequence format (soft); PAP-59 role presets; PAP-122 conformance; PAP-201; PAP-206 chart mapping for code conflicts. PAP-208 reads pack metadata to recommend templates.

**Definition of done**

* Three work packages merged and reported.
* Integration test: apply each pack with sample data to an empty tenant; every generated page passes PAP-122 conformance; every view renders; trial balance is zero; remove sample data leaves structure intact (script and report attached). Applying a bumped version upgrades additively; composing clinic plus retail works.
* Justin reviews the five content lists in one Needs Justin item.
* Screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark for gallery and one dashboard per pack at 1280 in both themes; axe clean.
* `docs/migration/templates.md`; CHANGELOG; Linear comment with gallery and item counts.

**Test plan**

* Vitest: schema, every lint rule, `extends` merge, composition, conflict strategies, upgrade diff, sample sub-run rollback, sensitive annotations in clinic.
* Integration script `scripts/templates-verify.ts` in CI on the small fixture tenant.
* Playwright: gallery, diff, apply, browse, remove sample data; visual baselines at the seven widths, both themes.

**Demo**

Reviewer opens Settings > Templates, applies Restaurant with sample data, lands on the reservations calendar with tonight's fictional bookings, then clicks "Remove sample data" and sees the empty calendar with structure intact. Under two minutes.

**Edge cases**

* Existing `contacts` table with different fields: merge adds fields, never changes types.
* Same pack twice: detected, upgrade or no-op.
* Unbuilt view kind (Gantt): saved `unsupported`, renders as list.
* Rollback after real rows: non-demo tables kept.
* Chart conflicts with an imported QuickBooks chart: matched by code, duplicates skipped.
* Regulated sample data: fictional names and a banner until removed.

**Dependencies**

PAP-161 and PAP-199 (hard). PAP-114, PAP-117, PAP-179, PAP-187, PAP-59, PAP-122, PAP-201. Soft: PAP-191, PAP-22.

**Agent**

Built by Scout (Template Packager) with Quill for docs, Beacon for CRM and sequences, Iris for the gallery. Reviewed by Sentinel (Visual Inspector, Code Reviewer, Edge Case Hunter), Ledger for charts and Justin for realism.

**Size**

L umbrella; two M and one S work package. Pending sub-issue specs: [Round 2 pending issues: migration (20)](https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6)
