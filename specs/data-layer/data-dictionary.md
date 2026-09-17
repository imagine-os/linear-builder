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
blockedBy: ["PAP-128", "PAP-32"]
blocks: []
key: "data-layer/data-dictionary"
url: "https://linear.app/paperos/issue/PAP-41/generate-a-living-data-dictionary-from-the-drizzle-schema-into-the"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-41: Generate a living data dictionary from the Drizzle schema into the docs system

**Goal**

Generate a living data dictionary from the Drizzle schema so anyone (Justin, agents, future staff) can browse every table, column, relation, index, RLS policy and audit setting inside the product's docs engine, with descriptions kept next to the code and regenerated on every merge.

**Scope**

In:
- Generator `packages/db/src/dictionary/generate.ts`: introspects Drizzle schema objects (tables, columns, types, defaults, relations, indexes, checks) plus live database metadata via `information_schema`/`pg_policies`/`pg_trigger` on a migrated dev database, merges column comments and a `dictionary.yaml` sidecar for prose, emits `docs/data/dictionary/*.md` (one page per table) and `dictionary.json`.
- Content per table: purpose, owner project (from a `@owner` tag in schema file comments), columns table (name, type, nullable, default, description, PII flag), relations (in/out), indexes, RLS policies with SQL, audit inclusion, search registration, seeds present, linked issues.
- ER diagrams: Mermaid `erDiagram` per domain (core, identity, pm, finance, crm) and a whole-schema diagram.
- Docs engine integration (`collab/docs-engine`): pages carry front-matter (`title`, `owner`, `generated: true`, `sourceHash`); rendered under `/_app/docs/data/*` with search via `data-layer/search`; a "generated, edit descriptions in `dictionary.yaml`" banner.
- CI: `pnpm gen:dictionary --check` fails if committed output is stale; PR comment listing schema changes (added/removed columns) as a schema changelog fragment for `collab/changelog`.
- Coverage rule: every column needs a description; CI warns under 100 percent and fails if a new column has none.

Out: editing the schema from the UI, data browsing (that is the tables project), external tool exports beyond JSON.

**Spec**

- `dictionary.yaml` schema: `tables.<name>.description`, `tables.<name>.columns.<col>.{description, pii: boolean, example}`; validated with Zod; unknown keys fail.
- PII flags feed the OTel attribute filter (`data-layer/observability`) and the audit redaction table (`data-layer/audit-log`) through a generated `pii.json`, making the dictionary the single source for sensitivity.
- Diagram grouping via `@domain` tag; cross-domain relations drawn dashed.
- Output is deterministic (sorted keys) to keep diffs small.
- `dictionary.json` shape: `{ generatedAt, schemaHash, tables: [{ name, domain, owner, description, columns:[...], relations:[...], indexes:[...], policies:[...], audited, searchable }] }` consumed by `spec-builder/data-section` to validate that page specs reference real tables and columns.
- Rendering component `<DataDictionaryTable/>` uses the design system table (`design-system/data-display`) for column lists, with anchors per column for deep links from specs.

**Definition of done**

- Dictionary generated for all tables existing at merge time; 100 percent description coverage for core entities.
- `--check` stale detection proven in PR; schema-change PR comment appears on a test PR.
- Vitest: YAML validation, determinism (two runs identical), PII export, Mermaid output snapshot.
- Rendered pages in the docs engine at 375, 768, 1024, 1280, 1920 (screenshots), including one table page and the ER diagram.
- `pii.json` consumed by observability filter test.
- `docs/data/dictionary/README.md` on maintaining descriptions; CHANGELOG; Linear comment with in-app docs link.

**Edge cases**

- Table exists in database but not in Drizzle (e.g. Better Auth or pg-boss internal tables): listed under "External" with a note, not an error.
- Enum types and arrays render readable types.
- Partitioned tables list the parent only, with partition strategy noted.
- Views and materialised views included with their definition SQL.
- Column renamed: YAML key mismatch fails with suggestion of the nearest name.
- Very wide tables (80+ columns): page collapses groups by prefix.

**Dependencies**

`data-layer/drizzle-schema` and `collab/docs-engine` (hard). Soft: `data-layer/rls-tenancy` (policies), `data-layer/audit-log`, `data-layer/search`, `design-system/data-display`. Consumed by `spec-builder/data-section`, `migration/import-framework` (mapping targets), `agents/character-docs`.

**Agent**

Built by Quill (Spec and Documentation Lead) with Forge (Schema Wright) on the introspection code. Reviewed by Sentinel (Code Reviewer) and Iris for rendering.

**Size**

S: introspection plus templating; the schema and docs engine do the heavy lifting.
