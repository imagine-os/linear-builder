---
identifier: "PAP-746"
title: "Per-page performance budgets from specs: `budgets` section compiled into Lighthouse CI assertions, `size-limit` entries and k6 p95 thresholds"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-87", "PAP-740"]
blocks: []
key: "r4/spec-builder/page-budgets"
url: "https://linear.app/paperos/issue/PAP-746/per-page-performance-budgets-from-specs-budgets-section-compiled-into"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:36.027Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-26"
cycle: null
---

# PAP-746: Per-page performance budgets from specs: `budgets` section compiled into Lighthouse CI assertions, `size-limit` entries and k6 p95 thresholds

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-87 enforces web budgets and PAP-242 API budgets with hand-maintained config lists that drift from the routes specs declare. Let the spec own the numbers: a page says its LCP, INP, bundle and API p95 budgets, and one generator writes the three tool configurations, so a new page is measured the day it is specified.

**Scope**

In: generator `budgets` in PAP-362's pipeline writing `lighthouserc.generated.json` assertions per public and key route, `size-limit` entries per route chunk (`apps/web/.size-limit.generated.json`) and `k6` thresholds per generated procedure (`load/generated/thresholds.json` for PAP-242); app defaults from PAP-117 `defaults.budgets`; a `budgets` column in the PAP-97 status comment; `docs/spec/budgets.md`. Out: the measurement tools themselves (PAP-87, PAP-242), fixing regressions.

**Spec**

* Defaults: `lcpMs 2500`, `inpMs 200`, `bundleKb 250` (route chunk gzip), `apiP95Ms 300`; `layout.template: public` pages default tighter (`lcpMs 1800`, `bundleKb 150`); a page may only tighten below app defaults without `x-budget-waiver: <PAP-n>`.
* Route to chunk mapping uses the PAP-314 route file names; procedures for k6 come from the page's `data` section queries and mutations mapped to generated routers (PAP-741).
* Generated configs are merged with hand-written ones by the tools (Lighthouse `extends`, size-limit array concat, k6 thresholds object spread); conflicts error at generation.
* Regression report: PAP-87 and PAP-242 already fail the PR; this issue adds the budget source line (`from specs/pages/x.spec.yaml:budgets`) to their messages so an agent fixes the right place.
* `--check` red when a route exists without a budget entry (defaults apply, so this only fires for unspecced routes already caught by PAP-115).

**Interface contract**

Provides: `budgets` generator, three generated config files, waiver convention, status-comment column. Consumes: v1.1 `budgets`, PAP-117 defaults, route naming (PAP-314), pipeline (PAP-362), Lighthouse CI config (PAP-87), k6 harness (PAP-242), status comment (PAP-97). Consumed by: PAP-87, PAP-242, PAP-89 digest (budget table), PAP-363 landing page.

**Definition of done**

* Three example pages produce entries; tightening `bundleKb` below the current chunk turns PAP-87 red on a seeded branch; loosening without a waiver fails validation.
* `docs/spec/budgets.md`; comments on PAP-87 and PAP-242 with the generated file paths; CHANGELOG entry.

**Test plan**

* Unit: defaults and tightening rule, route to chunk mapping, config merge conflicts, waiver parsing.
* Integration: Lighthouse CI dry run with the generated config on the template; k6 threshold file loads.
* E2E: none.

**Demo**

Set `budgets: { bundleKb: 80 }` on the invoices page, run `paperos gen --only budgets`, open the generated size-limit entry, push and watch PAP-87 fail with the spec path in the message. Under two minutes.

**Edge cases**

* Page with no chunk (redirect-only route): skipped with a note.
* Procedure shared by ten pages: strictest p95 wins and the winner page is named.
* Lighthouse unavailable in CI: generated file still written; check skipped.

**Dependencies**

Hard: PAP-740, PAP-87. Soft: PAP-242, PAP-362, PAP-314, PAP-97, PAP-741.

**Agent**

Builder: Sentinel (Code Reviewer sub-agent as builder). Reviewer: Sentinel (Edge Case Hunter, a second session) with Atlas.

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/spec-builder/entity-backend-codegen` = PAP-741, `r4/spec-builder/schema-v1-1-extensions` = PAP-740.
