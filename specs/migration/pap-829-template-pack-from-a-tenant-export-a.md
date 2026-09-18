---
identifier: "PAP-829"
title: "Template pack from a tenant: export a tenant's structure (tables, views, pipelines, chart, segments, sequences, pages, navigation) as a lint-clean pack with optional anonymised sample data"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Business migrations"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-420", "PAP-426"]
blocks: []
key: "r4/migration/template-pack-from-tenant"
url: "https://linear.app/paperos/issue/PAP-829/template-pack-from-a-tenant-export-a-tenants-structure-tables-views"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:05.584Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-829: Template pack from a tenant: export a tenant's structure (tables, views, pipelines, chart, segments, sequences, pages, navigation) as a lint-clean pack with optional anonymised sample data

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

The fastest way to a fiftieth business type is not to author it but to capture it: a tenant that already works becomes a pack. This turns PAP-426's format into a round trip and lets Justin or a customer publish a vertical without writing YAML.

**Scope**

In: `pnpm template capture --tenant <slug> --out <dir>` and `_app/settings/templates/capture` reading structure through the PAP-420 export writers (schema, views, pipelines, chart of accounts, segments, sequences, page specs, navigation, docs) and emitting `pack.yaml` plus files that pass `lintPack`; sample-data option sampling N rows per table through an anonymiser (names, emails, phones, addresses, free text replaced; money and dates jittered; relations preserved) with `demo: true`; `extends: base` detection; version and provenance metadata; apply-back test on an empty tenant.

Out: pack marketplace or sharing between tenants (v0.3), capturing automations (PAP-174 export exists separately), capturing user data beyond anonymised samples.

**Spec**

* Anonymisation is deterministic per run seed so relations still resolve; PII classification from PAP-355 decides which columns are replaced; a report lists every replaced column.
* Captured packs reference module features by capability so they apply on tenants with fewer modules.
* Round-trip property: capture, apply to empty, capture again yields an identical pack (excluding provenance).

**Interface contract**

Provides: capture CLI and page, `anonymiseSample()`, provenance fields in `PackSchema`, round-trip test script. Consumes: pack schema, lint and applier (PAP-426), export writers (PAP-420), PII registry (PAP-355), conformance (PAP-122) for the apply-back test.

**Definition of done**

* Capturing each wave-1 pack tenant reproduces a lint-clean pack that applies back identically (round-trip test in CI); anonymiser leaves zero PII per a scan; screenshots at 375, 1024 light and dark; `docs/migration/templates.md` capture section; CHANGELOG.

**Test plan**

* Unit: anonymiser determinism and coverage, extends detection, provenance, round-trip equality.
* E2E: capture the demo restaurant tenant with 20 sample rows, apply to an empty tenant, browse the reservations calendar with fictional names.

**Demo**

Reviewer captures the demo tenant from Settings, downloads the pack, applies it to an empty tenant and sees the same structure with anonymised sample data. Under two minutes.

**Edge cases**

* Table with a custom field type not yet in the pack schema: captured as `unsupported` with a report line.
* Sequences with unapproved templates: captured in unapproved state (PAP-427 rule).

**Dependencies**

Hard: PAP-426, PAP-420. Soft: PAP-355, PAP-122.

**Agent**

Builder: Scout (Template Packager). Reviewer: Sentinel (Security Auditor for anonymisation, Code Reviewer).

**Size**

S: half a session.
