---
identifier: "PAP-559"
title: "`pii()` Drizzle column annotation and registry: generated `pii.json`, the unannotated-column lint, and wiring into audit redaction, OTel filtering, the data dictionary and exports"
project: "data-layer"
projectName: "Data Layer & Database"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Tenant-safe and observable"
state: "Backlog"
parent: "PAP-355"
children: []
blockedBy: ["PAP-33", "PAP-38", "PAP-564"]
blocks: ["PAP-41", "PAP-221"]
key: "r4/data-layer/pii-registry"
url: "https://linear.app/paperos/issue/PAP-559/pii-drizzle-column-annotation-and-registry-generated-piijson-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:07.560Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-559: `pii()` Drizzle column annotation and registry: generated `pii.json`, the unannotated-column lint, and wiring into audit redaction, OTel filtering, the data dictionary and exports

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

First child of PAP-355 and the single source of PII truth: one annotation on the schema that audit redaction (PAP-38), the OTel span processor (PAP-40), the prompt-log redaction map (PAP-107), the DSAR registry (PAP-221), the data dictionary (PAP-41) and exports (PAP-205) all read. PAP-41 currently also claims to generate `pii.json`; after this issue PAP-41 reads the registry and renders it.

**Scope**

In: `packages/db/src/pii/{annotation,registry,build}.ts`, `pii()` column wrapper, `pnpm pii:build` writing `packages/db/generated/pii.json`, Biome rule `@paperos/config-biome/db/pii-required`, consumer wiring: `paperos.audit_redactions` seed (PAP-38), span processor denylist loader (PAP-40), `docs/data/pii.md`.

Out: Retention jobs and legal hold (PAP-560), tenant purge (PAP-561), per-user erasure (PAP-221), field encryption (PAP-353).

**Spec**

* `pii(column, { kind: 'identifier'|'contact'|'content'|'financial'|'credential'|'location', subject: 'user'|'contact'|'employee', retention?: Duration })` wraps any Drizzle column and records metadata in a module-level registry keyed by `table.column`.
* `pii.json` shape `{ generatedAt, schemaHash, columns: [{ table, column, kind, subject, encrypted: boolean, retention? }] }` plus the legacy `{ [table]: string[] }` view PAP-38 and PAP-40 already read; deterministic ordering.
* Lint: a column named `email|phone|name|address|ssn|tax_id|iban|dob|ip|first_name|last_name` without `pii()` fails Gate 1 with the nearest annotation suggestion; allowlist with expiry in `packages/db/src/pii/allowlist.yaml`.
* Encrypted columns (PAP-353 `encrypted()`) are auto-registered as `kind: 'credential'`, `encrypted: true`.
* Consumers: `audit_redactions` seeded for `credential` and `financial`; PAP-40 processor denies span attribute keys matching any annotated column name; PAP-41 renders the kind badge; PAP-205 export manifest marks PII files; PAP-555 payload refinement rejects annotated keys.
* `pnpm pii:build --check` fails when the committed file is stale; `pnpm pii:report` prints coverage per table and subject.

**Interface contract**

Provides: `pii()` annotation, `piiRegistry()`, `pii.json` (both shapes), lint rule, scripts `pii:build|report`, type `PiiEntry`.

Consumes: Schema and column helpers (PAP-32, PAP-33), `audit_redactions` table (PAP-38), span processor hook (PAP-40, soft), `encrypted()` (PAP-353, soft). Consumed by PAP-41, PAP-107, PAP-205, PAP-221, PAP-40, PAP-38, PAP-560, PAP-555.

**Definition of done**

* Every core table column holding personal data annotated; lint catches a seeded unannotated `phone` column (shown in PR).
* `pii.json` committed and consumed by the PAP-40 filter test and PAP-38 redaction seed; an annotated attribute never reaches the OTel exporter (test).
* PAP-41 description updated by comment: it reads the registry instead of generating `pii.json`.
* `docs/data/pii.md` with the kind and subject tables; CHANGELOG under Security; Linear comment.

**Test plan**

* Unit: annotation parser and registry determinism, lint fixtures (annotated, unannotated, allowlisted with expired date), legacy shape generation, `--check` staleness.
* E2E: CI compose: build `pii.json` against the migrated database, run the PAP-40 collector test and the PAP-38 redaction test with the generated file.

**Demo**

Reviewer adds a `phone text()` column to a scratch table, runs `pnpm lint` and reads the failure, wraps it in `pii()`, runs `pnpm pii:build` and opens the diff of `pii.json`. Under a minute.

**Edge cases**

* Column renamed: registry key changes; `--check` reports the stale entry and the redaction seed migration is regenerated.
* jsonb column with mixed content (`attributes`): annotate at the column level with `kind: 'content'`; per-key classification is out of scope and documented.
* External tables (Better Auth, pg-boss): registered by a sidecar list in `pii/external.ts`, not by annotation.
* Allowlist entry past its expiry: lint fails until renewed.

**Dependencies**

Blocked by PAP-33 (schema) and PAP-38 (`audit_redactions`). Soft: PAP-40, PAP-353, PAP-32. Blocks PAP-221 (registry) and PAP-41 (rendering); siblings PAP-560 and PAP-561 consume it softly.

**Agent**

Builder: Forge (Schema Wright). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/data-layer/events-core` = PAP-555, `r4/data-layer/retention-jobs` = PAP-560, `r4/data-layer/tenant-purge` = PAP-561.
