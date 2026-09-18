---
identifier: "PAP-692"
title: "Enable Fibonacci estimates on team PAP and backfill every issue's estimate from its Size (S=2, M=3, L=5) with roll-up on umbrellas and projects"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Agent"]
milestone: "Linear configured for the pipeline"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-91"]
blocks: ["PAP-98", "PAP-102", "PAP-693"]
key: "r4/pm-linear/linear-estimates-and-size-labels"
url: "https://linear.app/paperos/issue/PAP-692/enable-fibonacci-estimates-on-team-pap-and-backfill-every-issues"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:26.615Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-20"
cycle: null
---

# PAP-692: Enable Fibonacci estimates on team PAP and backfill every issue's estimate from its Size (S=2, M=3, L=5) with roll-up on umbrellas and projects

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Team PAP has `issueEstimationType: notUsed` and zero estimates, so Linear cannot show scope per milestone, project progress by points or velocity per cycle, and Size lives only in prose. Turn estimates on, derive them from the `**Size**` line of every description, keep the two in step from now on, and let Linear's native roll-ups do the reporting Atlas otherwise reimplements.

**Scope**

* In: extension of `ops/linear/configure-workspace.ts` (PAP-91) with `teamUpdate({ issueEstimationType: 'fibonacci', issueEstimationAllowZero: false, issueEstimationExtended: false })`, backfill script `ops/linear/backfill-estimates.ts` (Size to estimate mapping, umbrellas left at the sum of children as Linear computes), validator rule `ESTIMATE_MISMATCH` (warning) in PAP-93, `docs/pm/linear-setup.md` section "Estimates".
* Out: changing Size semantics (S half session, M one, L two), time tracking, velocity targets (cycles issue), PM-module mirroring (PAP-100 already has `estimate`).

**Spec**

* Mapping: `S` 2, `M` 3, `L` 5; a leaf without a parsable Size gets `M` and a `needs-size` comment; umbrellas (issues with children) get no estimate of their own so Linear's project and milestone progress sum the children.
* Backfill: `issueUpdate({ estimate })` for every non-archived PAP issue where the estimate differs; idempotent; rate-limited 5 per second; a diff table before and after in the Linear comment.
* `linear-workspace.json` records `estimation: { type: 'fibonacci', mapping: { S: 2, M: 3, L: 5 } }`; `pnpm linear:configure --check` reports team-setting drift as `manual` (never flips a setting back without `--apply`).
* PAP-93 gains `ESTIMATE_MISMATCH` (warn): estimate disagrees with the Size line; PAP-307 triage sets the estimate when it sets Size; PAP-96 claims never depend on it.
* Consumers: PAP-98 records `estimate` on `usage_events` so the burn report shows cost per point; PAP-102 board cards show the estimate; the execution schedule's allowances (S $10, M $22, L $50) are documented as the dollar view of the same points.

**Interface contract**

* Provides: team estimation settings, `backfill-estimates.ts`, mapping constant `SIZE_ESTIMATE`, validator code `ESTIMATE_MISMATCH`, `estimate` field on `usage_events`.
* Consumes: PAP-91 configure script and `linear-workspace.json`, PAP-93 validator, PAP-98 metering, PAP-307 triage; Linear API `teamUpdate`, `issueUpdate`.

**Definition of done**

* Team shows Fibonacci estimates; every leaf issue has one matching its Size; umbrellas none; counts posted.
* Project view screenshot at 1280 px showing points per milestone; `--check` clean after `--apply`.
* `ESTIMATE_MISMATCH` fixture passes; changelog; Linear comment with the diff table.

**Test plan**

* Unit: Size parsing on 30 description fixtures (`S`, `M`, `L`, `Small`, missing, umbrella), idempotent diff, rate limiter.
* E2E: live backfill on team PAP with before and after counts.

**Demo**

Open the Quality Pipeline project in Linear and read points per milestone; open PAP-342 and see estimate 3 beside `Size: M`. Under one minute.

**Edge cases**

* Size line says `L (umbrella; children M, M, S)`: the issue has children, so no estimate is set.
* A future L leaf (allowed but rare): estimate 5 and a `SPLIT_CANDIDATE` note for PAP-306.
* Justin edits an estimate by hand: the validator warns on mismatch; nothing overwrites his value until the Size line changes.
* Linear plan lacks a setting (Basic supports estimates): documented; extended scale never enabled.

**Dependencies**

Hard: PAP-91. Soft: PAP-93, PAP-98, PAP-102, PAP-307.

**Agent**

Builder: Atlas (Dispatcher). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.
