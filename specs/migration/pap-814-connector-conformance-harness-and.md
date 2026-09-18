---
identifier: "PAP-814"
title: "Connector conformance harness and scaffold: `connectorConformance()` Vitest suite every SourceConnector passes, recorded-HTTP fixture conventions and `pnpm paperos connector scaffold`"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Import framework and CSV"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-347", "PAP-348"]
blocks: []
key: "r4/migration/connector-conformance-harness-and-scaffold"
url: "https://linear.app/paperos/issue/PAP-814/connector-conformance-harness-and-scaffold-connectorconformance-vitest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:47.975Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-28"
cycle: null
---

# PAP-814: Connector conformance harness and scaffold: `connectorConformance()` Vitest suite every SourceConnector passes, recorded-HTTP fixture conventions and `pnpm paperos connector scaffold`

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Seven connector specs (PAP-202, PAP-414, PAP-417, PAP-423, PAP-424, PAP-204, PAP-422) list 'passes the framework `connectorConformance()` suite' in their test plans and no issue writes it. PAP-494 proves the module contract; this proves each connector implementation, and a scaffold command makes 'write a connector in an hour' true for the next twenty sources.

**Scope**

In: `packages/import/src/testing/conformance.ts` exporting `connectorConformance({ factory, fixtures, capabilities })`: cases for `discover` shape validity, `stream` pagination and cursor resume, `capabilities` honesty (an advertised `incremental` must yield fewer records on a second cursor run), rate-limit backoff on injected 429, attachment refs fetchable through `fetchAttachment`, error mapping to framework item errors, dry-run purity (no writes), rollback hook when declared; recorded-HTTP conventions (`msw` handlers under `fixtures/<source>/api/`, `pnpm fixtures record <source>` when credentials exist); `pnpm paperos connector scaffold <name>` generating `connectors/<name>/{index,auth,discover,stream}.ts`, a fixture folder, the conformance test file and a docs stub; `docs/migration/writing-a-connector.md`.

Out: module-level contract conformance and golden fixtures (PAP-494), connector-specific mapping tests (each connector), UI.

**Spec**

* Cases are capability-gated: a connector without `attachments` reports those cases `unsupported`, never failing; `--strict` turns `unsupported` into failure for CI of connectors that claim the capability.
* The suite runs against the in-memory fixture connector (PAP-347) as its own reference and must pass there first.
* Stable case ids `connector.<case>.<n>` so PAP-494 can include them and Linear comments can cite them.
* Scaffold output passes lint, typecheck and the conformance suite with `TODO` markers only where source-specific logic goes; the generator is idempotent and refuses to overwrite edited files.

**Interface contract**

Provides: `connectorConformance()`, recording conventions and `pnpm fixtures record`, scaffold command, `docs/migration/writing-a-connector.md`, case id catalogue. Consumes: `SourceConnector`, engine and fixture connector (PAP-347), dry run and rollback semantics (PAP-348), test accounts env names (PAP-813, soft), conformance runner registration (PAP-494, soft).

**Definition of done**

* Suite green on the fixture connector and on the CSV connector (PAP-200) via recorded fixtures; a deliberately broken connector under `testing/negative/` fails exactly its cases.
* Scaffold produces a connector that passes the suite unchanged; docs page reviewed by Quill; CHANGELOG; comments on PAP-414, PAP-417, PAP-423, PAP-424 naming the import path.

**Test plan**

* Unit: each case against the fixture connector; capability gating; strict mode; scaffold idempotence.
* E2E: `pnpm paperos connector scaffold demo && pnpm test connectors/demo` passes in under 60 s.

**Demo**

Reviewer scaffolds a `demo` connector, runs its tests and reads the conformance report, then breaks pagination on purpose and sees the exact case fail. Under two minutes.

**Edge cases**

* Connector streams faster than fixtures assume (different page size): cases assert set equality, not page boundaries.
* Source with no stable ids (spreadsheets): cursor cases marked `unsupported` by capability.
* Recording with credentials leaks a token into a fixture: the recorder redacts headers and the PAP-80 scan gates the commit.

**Dependencies**

Hard: PAP-347, PAP-348. Soft: PAP-200, PAP-494, PAP-813. Consumed by every connector issue (soft; they may merge with unit tests and adopt the suite after).

**Agent**

Builder: Scout (Import Mapper) with Sentinel on case design. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/migration/importer-test-accounts-and-fixture-workspaces` = PAP-813.
