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
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-90: Build flaky-test detection and quarantine so agents are not blocked by nondeterminism

**Goal**

Stop nondeterministic tests from blocking twenty parallel agent sessions: detect flaky unit, e2e, visual and flow tests from retry data, score them, automatically quarantine repeat offenders with a Linear issue assigned to the owning character, keep running them out of band, and un-quarantine when they stabilise.

**Scope**

In:
- Flake database `ops/quality/flakes.json` (committed, bot-updated) plus a nightly aggregate in the LHCI-style SQLite store or Postgres table `qa_flakes` (`test_id, suite, first_seen, last_seen, runs, failures, retried_passes, score, state: active|quarantined|resolved, linear_key, owner`).
- Collectors: Vitest JUnit and JSON reports (`retry` flag), Playwright JSON reports (`status: flaky`), visual suite `reports/visual.json` (diffs that vanish on rerun), flow and edge-case reports; a reporter step `ops/quality/collect-flakes.ts` runs at the end of every gate workflow and posts to `POST /api/qa/flakes` on the API (`data-layer/api-layer`) or appends to the JSON in a bot commit on `main` runs.
- Scoring: `score = retriedPasses / runs` over the last 20 runs; `>= 0.15` for three runs = quarantine candidate; auto-quarantine when candidate persists for 24h or when the same test blocks two different PRs.
- Quarantine mechanism: Vitest `test.skip` via a runtime `isQuarantined(id)` wrapper (`packages/core/src/testing/quarantine.ts`) reading the JSON; Playwright uses `test.info().annotations` plus a `quarantine` project that runs quarantined tests without affecting status; visual tests move to informational.
- Linear integration via `pm-linear/webhooks`: create issue `Flaky: <test id>` with evidence links, label `flake`, owner = character from `git blame` of the test file mapped through `.mailmap`; close automatically when score falls under 0.05 for 30 runs and remove from quarantine.
- Dashboard: `docs/quality/flakes.md` auto-generated table plus a small page in the app later (`tables/*`).
- Guardrails: quarantine cap 5 percent of tests per suite; beyond that the gate fails with "too many quarantined" so rot is impossible.

Out: fixing the flaky tests themselves, load-related infrastructure flakiness (observability), retry policy changes in CI (already set in each gate).

**Spec**

- Test ID grammar: `<suite>::<file>::<fullTitle>` with paths relative to repo root; stable across renames only if title unchanged (documented).
- `collect-flakes.ts` inputs: report paths via CLI flags; outputs `reports/flakes-delta.json`; on PRs it comments a one-line note when a retried pass occurred ("1 flaky test detected, not blocking, tracked as FL-123").
- Quarantine file schema (Zod) with `expires` (default 14 days, extended on activity) so no test stays quarantined silently; expired entries fail the collect step until renewed or resolved.
- The `quarantine` Playwright project runs quarantined tests with `retries: 0` to gather clean statistics.
- Weekly summary comment on the release digest (`quality/review-report` section 3) with counts and top 5 flakes.
- Ownership mapping: `ops/quality/owners.yaml` overrides blame when a file is shared.

**Definition of done**

- Collector runs at the end of Gate 1, e2e, visual and flow workflows and updates the DB (links).
- A seeded flaky test (random 30 percent failure) gets detected within 5 runs, quarantined automatically with a Linear issue created (screenshot), and the PR that contains it goes green with the note.
- Fixing the test (remove randomness) leads to auto-resolution after the configured runs in a compressed test (runs threshold overridable for the demo).
- Quarantine cap test: exceeding 5 percent fails the gate with a clear message.
- `docs/quality/flakes.md` generated and linked; CHANGELOG entry; Linear comment with the seeded flake issue link and dashboard.

**Edge cases**

- Test that fails deterministically only on one shard or width: score per environment key; quarantine scoped to that environment.
- Renamed test title resets history: collector detects same file and near-identical title (Levenshtein under 5) and links histories.
- Flaky because of a real race condition in product code: quarantine issue template asks the owner to classify `test-bug` vs `product-bug`; product bugs escalate to S1 finding, not quarantine.
- Bot commit of `flakes.json` racing with agent PRs: only `main` runs commit; PR runs post deltas as artifacts.
- Test removed from the codebase: entry resolved with reason `deleted`.
- Quarantined visual baseline drifts silently: quarantined visual tests still record diffs to the report as informational.

**Dependencies**

`quality/e2e-flows` (hard: first real flake source and Playwright report shape). Soft: `quality/ci-gate1`, `quality/playwright-matrix`, `quality/video-replays`, `pm-linear/webhooks`, `data-layer/api-layer` (storage), `forge/bot-accounts` (commits). Consumed by `quality/release-train`, `quality/review-report`, `agents/eval-harness`.

**Agent**

Built by Sentinel (Edge Case Hunter sub-agent, who sees flakes first). Reviewed by Forge (CI plumbing) and Atlas (Linear issue policy).

**Size**

M: collectors for four report formats, scoring, quarantine wrappers and Linear automation.
