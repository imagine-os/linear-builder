---
identifier: "PAP-115"
title: "Build the spec validator CLI and CI check that fails PRs whose pages lack or violate specs"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Spec schema and validator"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-114"]
blocks: ["PAP-118", "PAP-122", "PAP-125", "PAP-362", "PAP-473", "PAP-749"]
key: "spec-builder/validator"
url: "https://linear.app/paperos/issue/PAP-115/build-the-spec-validator-cli-and-ci-check-that-fails-prs-whose-pages"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:29.025Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-24"
cycle: null
---

# PAP-115: Build the spec validator CLI and CI check that fails PRs whose pages lack or violate specs

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Ship the `paperos-spec` CLI and CI job that make specs mandatory: every route in an app has a valid `page.spec.yaml`, every reference inside a spec resolves, and a PR that breaks either rule turns gate 1 red with a precise annotation.

**Scope**

* In: `packages/spec/src/cli.ts` (`validate`, `routes`), the rule engine, core rules, baseline file, three output formats, watch mode, the library API, `docs/spec/validator.md`.
* Out: section-specific rules (added by PAP-116, PAP-119, PAP-121 through `defineRule`), codegen (PAP-120), fixing specs automatically beyond `--fix` renames.

**Spec**

* `paperos-spec validate [paths] [--format pretty | json | github] [--fix] [--baseline] [--strict] [--watch]`, `paperos-spec routes`; exit codes 0 clean, 1 errors, 2 warnings with `--strict`, 3 internal.
* Rules via `defineRule({ id, severity, check(ctx) })`, `ctx = { specs, app, routes, registry, git }`: `SPEC_PARSE`, `SPEC_ROUTE_UNCOVERED` (route under `apps/web/src/routes/_app/**` or `_public/**` lacking `staticData.spec`), `SPEC_ORPHAN`, `SPEC_DUP_ID`, `SPEC_DUP_ROUTE`, `SPEC_UNKNOWN_COMPONENT` (delegates to PAP-74 registry), `SPEC_UNKNOWN_ENTITY`, `SPEC_UNKNOWN_AUDIENCE` (against PAP-117), `SPEC_DANGLING_TRANSITION`, `SPEC_ACTION_UNBOUND`, `SPEC_BASELINE_GROWTH`, `SPEC_EDGE_TODO`.
* Routes read from TanStack `routeTree.gen.ts`; exemptions in `specs/.validator-ignore`.
* Baseline `specs/.validator-baseline.json` with an expiry date; growth requires label `spec-baseline`.
* Cache by content hash in `node_modules/.cache/paperos-spec`; 300 specs under 2 s.

*Round 4 amendment (2026-09-18):*
Rule `SPEC_BAD_PROPS`: component `props` are validated against the PAP-74 registry JSON Schema for that id (Ajv, strict); skipped with one warning when the registry is absent. Rule `SPEC_TEMPLATE_PLACEHOLDER`: any `{{...}}` left in a spec is an error (templates issue).

**Interface contract**

* Provides: `validateSpecs(options): Promise<Report>` with `Report = { issues: SpecIssue[], stats, durationMs }`, `defineRule`, `RuleContext`, GitHub annotation output consumed by gate 1, `pnpm spec:validate`, JSON output schema `validator-report.schema.json`.
* Consumers: PAP-78 gate 1 job; PAP-116, PAP-119, PAP-121 register rules; PAP-118 and PAP-307 call the CLI with `--format json`; PAP-124 runs `validateSpecs` in a worker; PAP-122 reads `SPEC_EDGE_TODO`; PAP-81 spec-conformance reviewer reads the report.
* Requires: PAP-114 schema; PAP-74 `registry.json` (skip component rules with one warning if absent); PAP-117 app spec (entity and audience rules activate when present); PAP-78 job slot.

**Definition of done**

* Vitest per rule (pass and fail), CLI snapshots for three formats, exit-code tests.
* Seeded failing PR shows inline annotations on GitHub and Forgejo runs.
* Green run on `paperos-template` with the baseline; baseline expiry test fails after the date.
* Docs with every code, hint and fix; timing on 300 generated specs pasted; changelog; Linear comment with red and green run links.

**Test plan**

* Unit: each rule with fixtures; route discovery against a generated `routeTree.gen.ts`; ignore file; cache hit after no-op edit.
* Integration: CLI on the template repo; `--watch` reacts to a file change within 500 ms.
* e2e: gate 1 job on a seeded failing branch, both forges.
* Bench: 300-spec fixture set under 2 s (`hyperfine`).
* No UI breakpoints.

**Demo**

Delete the spec of one route and run `pnpm spec:validate --format pretty`: `SPEC_ROUTE_UNCOVERED` names the route file and the hint; restore it, run again, clean. Then `paperos-spec routes` lists coverage. One minute.

**Edge cases**

* Transition to another app: allowed only with `x-external: true`.
* Two specs on one route: `SPEC_DUP_ROUTE` with both files.
* Deleted route with `status: built`: error hinting `deprecated`.
* Symlinked spec folders in worktrees: real paths before dedupe.
* Registry missing: skip component rules with one warning, never crash.

**Dependencies**

Blocked by PAP-114. Soft: PAP-74, PAP-117, PAP-78. Blocks PAP-118, PAP-122, PAP-125.

**Agent**

Built by Quill (Page Spec Writer) with Sentinel pairing on CI wiring; reviewed by Atlas.

**Size**

M
