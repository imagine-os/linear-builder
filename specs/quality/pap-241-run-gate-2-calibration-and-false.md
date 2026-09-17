---
identifier: "PAP-241"
title: "Run Gate 2 calibration and false-negative tracking: weekly manual spot check of five verdicts, precision and recall trend, reviewer prompt tuning loop"
project: "quality"
projectName: "Quality Pipeline"
phase: "P1"
type: "Review"
priority: 1
surfaces: ["Agent"]
milestone: "Visual and video gates"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-81", "PAP-244", "PAP-245"]
blocks: []
key: "quality/gate2-calibration"
url: "https://linear.app/paperos/issue/PAP-241/run-gate-2-calibration-and-false-negative-tracking-weekly-manual-spot"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:05.266Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-241: Run Gate 2 calibration and false-negative tracking: weekly manual spot check of five verdicts, precision and recall trend, reviewer prompt tuning loop

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Review

**Goal**

Measure the thing that replaced human code review: each week, sample five Gate 2 verdicts, have a second independent reviewer session judge them blind, record precision and recall against bugs found later (production incidents, Gate 4 findings, reverts), trend it, and tune reviewer prompts when agreement drops. Without this, the miss rate of PAP-81 is never known.

**Scope**

* In: `ops/quality/calibration/` with the weekly sampler, the blind re-review runner (a separate Sentinel session with a different prompt and no access to the original verdict), the escaped-defect linker (maps reverts, hotfixes, S0/S1 findings from later gates and incidents back to the PR that introduced them), metrics store, weekly report comment, prompt tuning procedure and a Needs Justin escalation when precision or recall falls under threshold twice.
* Out: the reviewers (PAP-81), eval harness for other characters (PAP-110; this issue feeds it).

**Spec**

* Sampler: every Monday pick 5 PRs merged in the last 7 days weighted toward risky paths (auth, permissions, ledger, migrations); store `ops/quality/calibration/samples/<yyyy-ww>.json`.
* Blind re-review: `pnpm review:blind --pr N` runs the correctness and security reviewers with `mode: 'audit'`, a stricter prompt and `maxTurns: 60`, output in the contracts `Finding` shape; a diff script classifies each original finding as `confirmed | disputed` and each new finding as `missed`.
* Escaped defects: script scans conventional commits `fix:` and `revert:`, hotfix labels, Gate 4 S0/S1 findings and incident records for `Introduced-By: <sha>` trailers or `git blame` of the fix hunk, then attributes to the original PR; weekly recall = caught / (caught + escaped).
* Metrics: `qa_calibration (week, reviewer, sampled, confirmed, disputed, missed, escaped, precision, recall, cost)`; rendered into `docs/quality/calibration.md` and PAP-89 section 3.
* Thresholds: precision 0.8, recall 0.7; two consecutive misses open a Needs Justin item with the failing examples and a proposed prompt change; prompt changes go through PAP-110 golden tasks before merge.

**Interface contract**

* Provides: `qa_calibration` table and `calibration.json` weekly artifact (contracts package kind `calibration`), `Introduced-By:` trailer convention for fixes, `calibrationHealth` consumed by PAP-89.
* Requires: PAP-81 reviewers and `runReview()`, `packages/contracts`, PAP-52 commit conventions, PAP-97 webhooks for the weekly comment.

**Definition of done**

* Three weekly cycles run (rehearsed on compressed history if needed) with reports committed and the digest section populated.
* Seeded escaped defect (a revert with `Introduced-By`) is attributed to the right PR and lowers recall (test).
* Blind re-review disputes at least one seeded false positive in the calibration set.
* Justin reads one weekly report and confirms the format in a comment.
* `docs/quality/calibration.md`; changelog under "Quality".

**Test plan**

* Unit: sampler weighting, attribution from trailers and blame, metric math.
* Integration: blind re-review against the PAP-79 15-case set reproduces expected severities within tolerance.
* Manual: one weekly run reviewed by Atlas.

**Demo**

Run `pnpm calibration:week --dry` and open the generated Markdown: five sampled PRs, confirmed and disputed counts, one escaped defect with its link, and the trend line for the last three weeks. Under two minutes.

**Edge cases**

* Fewer than five PRs merged: sample all, mark the week low-confidence.
* Escaped defect spans several PRs: attributed fractionally, documented.
* Blind reviewer costs more than budget: cap at $10 per week, sample fewer.
* Reviewer prompt changed mid-week: metrics tagged with prompt version.

**Dependencies**

PAP-81 (hard). Soft: PAP-89, PAP-110, PAP-97, PAP-52.

**Agent**

Run by Sentinel (a dedicated Calibration Auditor sub-agent, separate from the reviewers). Reviewed by Atlas; Justin sees the weekly summary.

**Size**

S: scripts around existing reviewers; the discipline of running it is the deliverable.
