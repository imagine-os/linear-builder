---
key: "gp/app-shell/acceptance"
title: "Build the golden path acceptance test: nightly CI runs three canned ideas from paragraph to preview URL, asserts gates 1 to 4 and under ten minutes, publishes `golden-path.json`, badge and friction issues"
project: "app-shell"
parent: null
phase: "P2"
type: "Review"
priority: 2
size: "M"
surfaces: ["Developer", "Agent"]
milestone: "Multi-monitor and PWA polish"
intendedState: "Backlog"
blockedBy: ["gp/app-shell/driver", "gp/app-shell/provisioning", "PAP-239"]
blocks: ["PAP-29"]
source: "round2/pending-issues-golden-path.json (Golden Path)"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-golden-path-8-98e27ab16f4f"
identifier: "PAP-429"
status: "created"
createdAt: "2026-09-17"
---

# Build the golden path acceptance test: nightly CI runs three canned ideas from paragraph to preview URL, asserts gates 1 to 4 and under ten minutes, publishes `golden-path.json`, badge and friction issues

**Goal**

Prove the ten-minute claim every night and keep it true: a workflow in `paperos-template` runs `paperos create --idea` for three canned ideas in throwaway repos, asserts the acceptance criterion from the golden path document ("a new app passes gates 1 to 4 and deploys to a preview URL in under 10 minutes of wall clock"), publishes the report and a README badge, and files one Linear issue per failing checkpoint in the owning project. PAP-29 starts its human-realistic drill from a passing golden path; this issue makes that starting line dependable.

**Scope**

In:

* `.github/workflows/golden-path.yml` (nightly 04:00 UTC after the warm pool refill, `workflow_dispatch` with an `idea` input, and on PRs touching `packages/cli` or `packages/spec` in a reduced one-idea mode), matrix over `fixtures/golden-path/{clinic-booking,agency-retainers,retail-inventory}.txt`.
* Runner script `ops/golden-path/run.ts`: pre-provisions a `gp-<idea>-<date>` GitHub repo, runs the driver with `--yes --json --budget 10`, collects `.paperos/golden-path.json`, runs the assertions, uploads the report as a workflow artifact and to `reports/golden-path/<date>-<idea>.json` in `paperos-infra`.
* Assertions: total C0 to C6 under 600 s warm (cold runs are recorded with `cache: cold` and not asserted until two consecutive warm passes exist); every checkpoint status `ok` or `warn`; gates 1 to 3 `pass` and gate 4 `pass|skipped`; smoke test passed; `paperos gen --check` clean; validator zero warnings; `costUsd` under 5.
* Friction issues: one Linear issue per failing checkpoint in the owning project (mapping table in `ops/golden-path/owners.json`), labels Build and `drill-finding`, deduplicated by a `golden-path:<checkpoint>:<idea>` marker in the description; reopened by comment when it recurs.
* Badge: `reports/golden-path/latest.json` with median duration over the last seven runs rendered by shields.io endpoint syntax into the README.
* Cleanup: repos deleted and pool slots released at the end of each run through the PAP-273 runbook script, after the report is archived; kept for 24 hours when the run failed.
* Trend page `docs/drills/golden-path.mdx` (PAP-128) with a per-checkpoint chart over time (static SVG until PAP-172).

Out: the driver, provisioning and generators (their issues), human drills (PAP-29), load testing (PAP-146), release certification (PAP-88).

**Spec**

* Report contract: consumes `GoldenPathReport` from the driver and wraps it in the PAP-239 artifact envelope (`kind: golden-path`, finding ids `GP-<checkpoint>-<n>`) so gate tooling and the Justin digest can read it.
* Warm cache definition: pnpm store, Docker build cache and Turbo cache restored from the previous nightly run via `actions/cache`; `cache: cold` when any restore missed.
* Three ideas are fixed text files; changing them requires updating the snapshot specs in the app interview and entity-pages fixtures (the same files).
* Time source is the runner clock; checkpoint budgets are read from the driver report, not duplicated here.
* Concurrency: the three matrix jobs run in parallel and each claims its own pool slots; the pool must hold at least three free slots of each kind or the job fails early with `pool-empty`.
* Workflow total runtime capped at 25 minutes; the `pull_request` mode runs only `clinic-booking` with `--no-wait` and asserts C0 to C4.

**Interface contract**

Provides: `reports/golden-path/*.json` in the PAP-239 envelope, `latest.json` for the badge, the `drill-finding` issue convention and owners mapping, and the `golden-path` workflow reusable by generated apps (`workflow_call`) to re-verify themselves after `paperos upgrade`. Consumes: golden path driver report and flags, provisioning pool and cleanup (`releaseSlot`), gate artifact contract (PAP-239), Linear issue creation through the `linear-update` skill (PAP-105) with the PAP-91 labels, docs engine (PAP-128), repo cleanup (PAP-273). Consumed by: PAP-29 (starting point and comparison), PAP-88 release train (golden path must be green for a release candidate), the Justin digest (PAP-97, informational).

**Test plan**

* Unit: assertion function over fixture reports (pass, over budget, gate failed, cold cache not asserted); owners mapping covers all six checkpoints; dedupe marker logic.
* Dry run: workflow executed with the driver in fake mode (all external clients faked) to validate the YAML, artifact upload and badge rendering in under 3 minutes.
* Real: three consecutive nightly runs recorded before this issue closes, at least two of them under 600 s warm for all three ideas.
* Friction path: force a failure (budget 1 minute) in `workflow_dispatch` and verify exactly one issue per failing checkpoint is created, then closed as duplicate-safe on rerun.

**Definition of done**

* Workflow merged and green for three nights; `latest.json` and README badge live; the trend page shows the runs.
* At least one friction issue was filed and linked by the workflow (from the forced-failure test or a real failure).
* Cleanup proven: no `gp-` repos older than 24 hours and pool `claimed[]` empty after runs.
* PAP-29 protocol document references this report as its C0 baseline; CHANGELOG; Linear comment on this issue and on PAP-5 with the first passing numbers.

**Edge cases**

* Nightly run collides with a template release merge: the workflow pins the template ref at start and records it in the report.
* One idea fails, two pass: matrix continues, the run is marked failed, friction issues filed only for the failing idea.
* Linear rate limited while filing issues: retries with the header wait; if still failing, the report stores `pendingIssues[]` and the next run files them.
* Preview URL passes `/healthz` but the smoke sign-in fails (mail provider outage in preview): C6 `failed` with the Playwright trace attached, owner mapped to identity.
* Warm pool refill still running at 04:00: workflow waits up to 5 minutes for `free >= 3`, then fails early with `pool-empty` rather than running cold.
* Cost over 5 USD because gate 2 retried: assertion fails with the per-stage cost table so the fix targets gate 2, not the interview.

**Dependencies**

Hard: golden path driver, golden path provisioning, PAP-239. Soft: PAP-105 `linear-update`, PAP-91 labels, PAP-128 docs engine, PAP-273 cleanup, PAP-88. Blocks PAP-29.

**Agent**

Run and owned by Sentinel (Quality Lead) with Forge for the workflow and Quill for the trend page; Atlas reads the nightly result in the digest. No Needs Justin item; the badge is the scoreboard.

**Size**

M: one workflow, one runner script, assertions, issue filing, badge and trend page.

**Demo**

Workflow run page showing three green matrix jobs, the checkpoint table per idea, the README badge reading the median duration, and the PAP-5 comment with the first passing numbers.
