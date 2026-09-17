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
blocks: ["PAP-118", "PAP-122", "PAP-125"]
key: "spec-builder/validator"
url: "https://linear.app/paperos/issue/PAP-115/build-the-spec-validator-cli-and-ci-check-that-fails-prs-whose-pages"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-115: Build the spec validator CLI and CI check that fails PRs whose pages lack or violate specs

**Goal**

Ship the `paperos-spec` CLI and CI job that make specs mandatory: every route in an app must have a valid `page.spec.yaml`, every reference inside a spec must resolve, and a PR that breaks either rule turns gate 1 red with a precise annotation. This is the enforcement point for the spec-first decision.

**Scope**

In:
- `packages/spec/src/cli.ts` (`cac` 6) exposing `paperos-spec validate [paths] [--format pretty|json|github] [--fix] [--baseline]`, `paperos-spec routes` (lists routes without specs), wired as `pnpm spec:validate`.
- Rule engine `packages/spec/src/rules/`: `defineRule({ id, severity: error|warn, check(ctx) })` with `ctx = { specs, app, routes, registry, git }`. Core rules: `SPEC_PARSE` (schema), `SPEC_ROUTE_UNCOVERED` (route file under `apps/web/src/routes/_app/**` or `_public/**` lacking `staticData.spec`), `SPEC_ORPHAN` (spec whose route file is missing when `status: built`), `SPEC_DUP_ID`, `SPEC_UNKNOWN_COMPONENT` and prop errors delegated to `design-system/component-spec-mapping`'s `registry.json`, `SPEC_UNKNOWN_ENTITY` and `SPEC_UNKNOWN_AUDIENCE` against `specs/app.spec.yaml` when present, `SPEC_DANGLING_TRANSITION` (`events[].to` not a known route), `SPEC_ACTION_UNBOUND` (component event references a missing action), `SPEC_READY_INCOMPLETE` (status ready without required sections).
- Output: pretty (colour, file:line:col), `--format json` to `reports/spec-validate.json` `{ status, counts, issues[] }`, `--format github` printing `::error file=...,line=...::` annotations readable by Forgejo Actions too.
- `--fix`: add missing `$schema` header, sort top-level keys, normalise line endings, migrate `specVersion`.
- Baseline `specs/.validator-baseline.json` listing pre-existing uncovered routes with an `expires` date (max 7 days) so adoption does not block unrelated PRs.
- CI job `spec` in `.github/workflows/ci.yml` added to the `gate-1` aggregate from `quality/ci-gate1`; `lefthook` pre-push runs `spec:validate --format pretty` on changed files.
- Plugin loading from `packages/spec/rules.config.ts` so `spec-builder/access-section` and others add rules without touching the core.

Out: authoring UX, codegen, conformance tests (`spec-builder/conformance-tests`).

**Spec**

- Exit codes: 0 clean, 1 errors, 2 warnings with `--strict`, 3 internal failure.
- Route discovery reads the TanStack generated `routeTree.gen.ts` rather than globbing, so it matches the router exactly; `_public/auth/*` and `__root` are exempt via `specs/.validator-ignore`.
- Performance: 300 specs validated under 2 s; registry and app spec parsed once; results cached by content hash in `node_modules/.cache/paperos-spec`.
- Each issue includes `hint` (one sentence) and `docs` URL into `docs/spec/validator.md#<code>`.
- Watch mode `--watch` for the spec editor and authoring skill.
- Library API `validateSpecs(options): Promise<Report>` used by `spec-builder/spec-editor-ui` in a worker.

**Definition of done**

- Vitest per rule with fixtures (pass and fail), CLI snapshot tests for all three formats, exit code tests.
- Seeded failing PR shows inline annotations on both GitHub and Forgejo runs (links in comment).
- Green run on paperos-template with the baseline; baseline expiry test fails the build after the date.
- `docs/spec/validator.md` with every code, hint and fix; CHANGELOG entry.
- `spec:validate` finishes under 2 s on 300 generated specs (timing pasted).
- Linear comment with green and red run links.

**Edge cases**

- Spec references a route in another app of the monorepo: allowed only via `x-external: true`, else `SPEC_DANGLING_TRANSITION`.
- `registry.json` missing (design system not built): skip component rules with a single warning, never crash.
- Two specs claim the same route: `SPEC_DUP_ROUTE` naming both files.
- Deleted route with spec still `status: built`: error with hint to set `deprecated`.
- Baseline file edited to add new entries in the same PR: rule `SPEC_BASELINE_GROWTH` fails unless PR has label `spec-baseline`.
- Symlinked spec folders in worktrees: resolve real paths before dedupe.

**Dependencies**

`spec-builder/schema` (hard). Soft: `design-system/component-spec-mapping` (registry), `spec-builder/app-level-spec` (entity and audience rules activate when present), `quality/ci-gate1` (job slot). Unblocks `spec-builder/spec-authoring-skill`, `spec-builder/conformance-tests`, `spec-builder/spec-docs`.

**Agent**

Built by Quill (Page Spec Writer) with Sentinel pairing on CI wiring. Reviewed by Sentinel (Code Reviewer) and Forge for router integration.

**Size**

M: rule engine and CI are straightforward; route discovery and baselines need care.
