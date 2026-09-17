---
identifier: "PAP-426"
title: "Template pack format, Zod schema, lint, and the `template` applier connector with conflict strategies, composition and upgrade"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer", "Staff"]
milestone: "Business migrations"
state: "Backlog"
parent: "PAP-207"
children: []
blockedBy: ["PAP-114", "PAP-161", "PAP-199"]
blocks: ["PAP-427"]
key: "child/PAP-207/0"
url: "https://linear.app/paperos/issue/PAP-426/template-pack-format-zod-schema-lint-and-the-template-applier"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:53.416Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-426: Template pack format, Zod schema, lint, and the `template` applier connector with conflict strategies, composition and upgrade

**Goal**

Define how a business template is written and applied: a versioned `pack.yaml` schema, a lint that enforces minimum content, and a `SourceConnector` applier so packs get dry run, rollback and id mapping for free, including `extends`, multi-pack composition and additive upgrades.

**Scope**

In: `packages/import/src/templates/{schema,lint,apply,upgrade}.ts`; pack sections `tables[]`, `views[]`, `pipelines[]`, `chartOfAccounts[]`, `segments[]`, `sequences[]`, `pages[]`, `navigation`, `docs[]`, `sampleData/*.jsonl` (`demo: true`), `roles[]`, `entitlements`; conflict strategy `skip|merge|rename` per table and account; `extends: base`; `upgrade` computing added tables and fields only; a `base` pack (contacts, companies, tasks, documents) used by the five packs.

Out: pack content (child 2), gallery (child 3).

**Spec**

* Lint minimums: 3 page specs, 6 views, 1 pipeline, 1 chart, 2 segments, 1 sequence, 1 doc.
* Mapping system `template:<type>@<version>` so re-apply detects and offers upgrade.
* Sample data applied as a sub-run so "Remove sample data" is a rollback of that sub-run.

**Interface contract**

Provides: `PackSchema` (Zod), `registerConnector('template', ...)`, `lintPack(path)`, `planUpgrade(tenant, pack): Diff`, CLI `pnpm template lint|apply|upgrade`. Consumes: PAP-199 children 1 and 2, PAP-161 field and view schema, PAP-114 page spec schema, PAP-117 navigation, PAP-179 accounts, PAP-187 pipelines, PAP-201. Children 2 and 3 and future packs depend only on these names.

**Definition of done**

* `base` pack applies to an empty tenant, re-apply is a no-op, a bumped version upgrades additively.
* Conflict strategies proven on a tenant with an existing `contacts` table.
* `docs/migration/templates.md` authoring section.

**Test plan**

* Vitest: schema validation, every lint rule, `extends` merge, composition of two packs, conflict strategies, upgrade diff, sample sub-run rollback.
* Integration: apply `base` with sample data, remove sample data, assert structure remains.
* Snapshot of the upgrade diff output.

**Demo**

Reviewer runs `pnpm template apply base --tenant empty --dry`, reads the diff, applies, then bumps the pack version and runs `upgrade` to see only additions listed. Under two minutes.

**Edge cases**

* Pack references a view kind not built yet (Gantt): saved with `unsupported`, renders as list.
* Rollback after real rows exist: tables with non-demo rows kept; only empty structure removed.
* Two packs define the same account code: second skipped with a note.

**Dependencies**

PAP-199 children 1 and 2 (hard), PAP-161 (hard), PAP-114, PAP-117, PAP-179, PAP-187, PAP-201. Blocks children 2 and 3.

**Agent**

Built by Scout (Template Packager). Reviewed by Sentinel (Code Reviewer, Edge Case Hunter) and Nova.

**Size**

M
