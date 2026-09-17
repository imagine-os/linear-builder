---
identifier: "PAP-90"
title: "Build flaky-test detection and quarantine so agents are not blocked by nondeterminism"
project: "quality"
projectName: "Quality Pipeline"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Edge-case hunting and release trains"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-86"]
blocks: []
key: "quality/flake-quarantine"
url: "https://linear.app/paperos/issue/PAP-90/build-flaky-test-detection-and-quarantine-so-agents-are-not-blocked-by"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:18:16.864Z"
---

# PAP-90: Build flaky-test detection and quarantine so agents are not blocked by nondeterminism

**Goal**

Stop nondeterministic tests from blocking twenty parallel agent sessions: detect flaky unit, e2e, visual, flow and edge-case tests from retry data, score them, quarantine repeat offenders automatically with a Linear issue for the owning character, keep running them out of band, and un-quarantine when they stabilise.

**Scope**

* In: `ops/quality/flakes.json` (bot-updated) plus `qa_flakes` table, collector `ops/quality/collect-flakes.ts` run at the end of every gate workflow, scoring, quarantine wrappers for Vitest and Playwright, Linear automation via PAP-97, ownership mapping, dashboard page, guardrails.
* Out: fixing the flaky tests, infrastructure flakiness (PAP-40), CI retry policy (set per gate).

**Spec**

* Test ID `<suite>::<file>::<fullTitle>`; near-identical titles (Levenshtein under 5) in the same file link histories.
* Collector inputs: Vitest JUnit/JSON (`retry`), Playwright JSON (`status: flaky`), `visual.json` diffs that vanish on rerun, `videos.json`, `edgecases.json`; each gate already writes `reports/flakes-delta.json` (PAP-239 kind `flakes-delta`); on PRs the collector comments one line ("1 flaky test detected, not blocking, tracked as FL-123") and uploads the delta; on `main` it posts to `POST /api/qa/flakes` (PAP-35) or bot-commits `flakes.json`.
* `qa_flakes (test_id, suite, env_key, first_seen, last_seen, runs, failures, retried_passes, score, state: active | quarantined | resolved, linear_key, owner, expires)`; `score = retriedPasses / runs` over the last 20 runs; candidate at `>= 0.15` for three runs; auto-quarantine after 24 h as candidate or when the same test blocks two PRs; scoring per environment key (shard, width, theme).
* Quarantine: Vitest `isQuarantined(id)` wrapper in `packages/core/src/testing/quarantine.ts`; Playwright annotations plus a `quarantine` project running quarantined tests with `retries: 0`; visual tests informational; `expires` default 14 days, extended on activity; expired entries fail the collector.
* Linear: issue `Flaky: <test id>` labelled `Bug` with evidence links, owner from `git blame` through `.mailmap` with `ops/quality/owners.yaml` overrides; template asks `test-bug` vs `product-bug` (product bugs become S1 findings); auto-close and un-quarantine under 0.05 over 30 runs.
* Guardrail: quarantine above 5 percent of a suite fails the gate "too many quarantined". Dashboard `docs/quality/flakes.md` generated; weekly top-5 in PAP-89 section 3.

**Interface contract**

* Provides: `flakes-delta.json` writer used by PAP-78, PAP-82, PAP-83, PAP-85, PAP-86; `isQuarantined()`; `quarantine` Playwright project; `qa_flakes` table and `POST /api/qa/flakes`; `owners.yaml`; `flakeSummary` for PAP-89.
* Requires: PAP-86 (hard: first real flake source and Playwright report shape), PAP-78 Vitest retry output, PAP-239 schema, PAP-97 webhooks, PAP-35 endpoint (soft: JSON commit fallback), PAP-48 bot commits.
* Consumers: PAP-88 certification (guardrail), PAP-89, PAP-110, PAP-241 (flake-vs-defect classification).

**Definition of done**

* Collector runs at the end of Gate 1, e2e, visual and flow workflows and updates the store (links).
* Seeded flaky test (30 percent random failure) is detected within 5 runs, quarantined with a Linear issue (screenshot), and the PR containing it goes green with the note.
* Removing the randomness leads to auto-resolution after a compressed run threshold (test).
* Quarantine cap test: exceeding 5 percent fails the gate with a clear message.
* `docs/quality/flakes.md` generated; changelog entry; Linear comment with the seeded issue and dashboard links.

**Test plan**

* Unit: score window math, per-environment keys, title linking, expiry, ownership resolution with overrides, cap computation.
* Integration: collector on fixture reports from each of the five formats; quarantine wrapper skips and the `quarantine` project still runs the test.
* Workflow: seeded flake on the sandbox repo end to end including Linear dry run.
* Guardrail: fixture with 6 percent quarantined fails.

**Demo**

Open the seeded PR: the one-line flake note; open the auto-created `Flaky:` Linear issue with evidence links; run `pnpm flakes:report` and read the dashboard table with scores and states. Under one minute.

**Edge cases**

* Deterministic failure on one shard or width only: scored and quarantined per environment.
* Product race condition: classified `product-bug`, escalates to S1, not quarantined.
* Bot commit racing agent PRs: only `main` runs commit.
* Deleted test: resolved with reason `deleted`.

**Dependencies**

PAP-86 (hard). Soft: PAP-78, PAP-82, PAP-83, PAP-85, PAP-239, PAP-97, PAP-35, PAP-48.

**Agent**

Sentinel (Edge Case Hunter). Reviewed by Forge (CI plumbing) and Atlas (Linear issue policy).

**Size**

M.
