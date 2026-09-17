---
identifier: "PAP-41"
title: "Generate a living data dictionary from the Drizzle schema into the docs system"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P2"
type: "Docs"
priority: 3
surfaces: ["Developer"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-32", "PAP-128"]
blocks: []
key: "data-layer/data-dictionary"
url: "https://linear.app/paperos/issue/PAP-41/generate-a-living-data-dictionary-from-the-drizzle-schema-into-the"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:40:59.930Z"
model: "claude-sonnet-5"
effort: "low"
---

# PAP-41: Generate a living data dictionary from the Drizzle schema into the docs system

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Docs S

**Goal**

Generate a living data dictionary from the Drizzle schema so Justin, agents and future staff can browse every table, column, relation, index, RLS policy and audit setting in the docs engine, with descriptions kept beside the code and regenerated on every merge. Its `pii.json` output is the single source for sensitivity used by audit redaction, OTel filtering and the retention issue.

**Scope**

In:

* Generator `packages/db/src/dictionary/generate.ts` merging Drizzle objects, live `information_schema`, `pg_policies`, `pg_trigger` and a `dictionary.yaml` sidecar into `docs/data/dictionary/*.md` and `dictionary.json`.
* Per-table content: purpose, owner project (`@owner`), columns (type, nullable, default, description, PII, retention), relations, indexes, policies, audit inclusion, search registration, seeds, linked issues.
* Mermaid ER diagrams per `@domain` and whole schema.
* `pii.json`, `--check` stale detection, PR comment on schema change.
* `<DataDictionaryTable/>` rendering in PAP-128.

Out: editing descriptions in-app, external tables' semantics.

**Spec**

* `dictionary.yaml`: `tables.<name>.description`, `columns.<col>.{ description, pii: boolean, retention?: string, example }`; Zod-validated; unknown keys fail.
* Deterministic output (sorted keys).
* `dictionary.json`: `{ generatedAt, schemaHash, tables: [{ name, domain, owner, description, columns, relations, indexes, policies, audited, searchable, retention }] }`.
* Front-matter `title`, `owner`, `generated: true`, `sourceHash`.
* Cross-domain relations drawn dashed; wide tables collapse column groups by prefix.

**Interface contract**

Provides:

* `dictionary.json` consumed by PAP-119 (spec data-section validation), PAP-199 (mapping targets), PAP-115.
* `pii.json` `{ [table]: string[] }` consumed by PAP-38 redactions, PAP-40 span filter and the retention issue.
* Scripts `pnpm dictionary:generate`, `pnpm dictionary:check` (Gate 1 via PAP-78).
* Tags `@owner <project>`, `@domain <name>`, `@pii`, `@retention <duration>` in schema file comments as the annotation convention for every schema author.

Consumes: schema (PAP-32), policies (PAP-34), audit exclusions (PAP-38), search registry (PAP-39), docs engine (PAP-128), table component (PAP-71).

**Definition of done**

* Dictionary for every table at merge time; 100 percent description coverage for core entities.
* `--check` stale detection proven; schema-change PR comment on a test PR.
* Vitest: YAML validation, determinism, PII export, Mermaid snapshot.
* Rendered pages at 375, 768, 1024, 1280, 1920 including one table page and the ER diagram.
* `pii.json` consumed by the PAP-40 filter test; README on maintaining descriptions; CHANGELOG; Linear comment.

**Test plan**

* Unit: two runs produce byte-identical output; YAML with a renamed column fails with the nearest-name suggestion; Mermaid snapshot for a three-table fixture.
* Integration (CI compose): generate against the migrated dev database; external tables (Better Auth, pg-boss) listed under External.
* Contract: `dictionary.json` validates against its JSON schema; PAP-119 fixture consumes it.
* Visual: five widths of a table page and the ER diagram in the docs engine.

**Demo**

Reviewer opens the in-app docs, navigates Data, Dictionary, `membership`, reads columns with PII badges and the RLS policy SQL, clicks a relation to `role`, then views the core ER diagram. Under a minute.

**Edge cases**

* Table in database but not Drizzle: External section, not an error.
* Enums and arrays rendered readably.
* Partitioned tables show parent with strategy.
* Views include definition SQL.
* Eighty-plus columns collapse by prefix.

**Dependencies**

PAP-32, PAP-128 (hard). Soft: PAP-34, PAP-38, PAP-39, PAP-71. Consumed by PAP-119, PAP-199, PAP-115, the retention issue.

**Agent**

Built by Quill (Documentation Lead) with Forge (Schema Wright) on introspection. Reviewed by Sentinel.

**Size**

S: a generator and templates.
