---
identifier: "PAP-525"
title: "DR drill scheduling and reporting: monthly Forgejo Actions cron, `report.json` renderer into `docs/runbooks/dr-reports/`, RTO and RPO trend and automatic follow-up issue filing"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Disaster recovery proven"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-47", "PAP-50", "PAP-53", "PAP-274", "PAP-519", "PAP-520"]
blocks: []
key: "r4/forge/dr-cron-and-report"
url: "https://linear.app/paperos/issue/PAP-525/dr-drill-scheduling-and-reporting-monthly-forgejo-actions-cron"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:50.836Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-525: DR drill scheduling and reporting: monthly Forgejo Actions cron, `report.json` renderer into `docs/runbooks/dr-reports/`, RTO and RPO trend and automatic follow-up issue filing

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-53 runs the drill once with evidence; making it repeat monthly, render its report for the digest and file follow-ups is a separate half-session that should not delay the first real run. It also gives PAP-88 and Justin a trend instead of a one-off number.

**Scope**

In:

* `ops/forge/dr/drill.yml`: Forgejo Actions cron on the production instance (first Sunday 02:00 UTC) invoking `drill.sh` with `--teardown`, plus `workflow_dispatch` with `--keep`; GitHub fallback disabled by design (the drill must not need GitHub).
* `scripts/dr/render-report.ts`: `report.json` to `docs/runbooks/dr-reports/<date>.md` with the phase table, RTO and RPO lines, mismatches, Hetzner hours and cost; `docs/runbooks/dr-reports/index.md` with a trend table over runs and a static SVG sparkline until PAP-172.
* Follow-ups: missed RTO or RPO target, mismatched heads or a failed phase opens one Linear issue each in forge (label Infra, `drill-finding`) through the `linear-update` skill (PAP-105), deduplicated by phase marker; reopened on recurrence.
* Digest hook: the latest report path and headline numbers exposed in `reports/dr/latest.json` for PAP-89.

Out: the drill script and the first run (PAP-53), backups (PAP-274), application DR (PAP-354).

**Spec**

* Targets read from `ops/forge/dr/targets.yml` (`rtoMinutes: 60`, `rpoMinutes: 1440`) so a change is a PR.
* Report rendering is deterministic; the Markdown is committed by the cron run through the PAP-48 bot with the PAP-46 trailers.
* Cost line uses Hetzner hours from the script; target under 2 EUR per drill.

**Interface contract**

Provides: `drill.yml`, `render-report.ts`, `dr-reports/` and `latest.json`, `drill-finding` convention shared with PAP-429; consumed by PAP-89 (digest), PAP-88 (release gate reads the trend), PAP-354 (platform drill reuses the renderer), PAP-306.

Consumes: runners and cron (PAP-50), backups and manifest (PAP-274), `report.json` schema (PAP-53), Linear skill (PAP-105, soft), bot identity (PAP-48).

**Definition of done**

* Renderer snapshot over a fixture report; cron registered with the first run date in the runbook; a forced failure fixture files exactly one issue.
* `dr-reports/index.md` shows the first real run; CHANGELOG; Linear comment.

**Test plan**

* Unit: renderer snapshot; target comparison; dedupe marker logic; trend table from three fixture reports.
* E2E: dispatch `drill.yml` in dry mode (fake phases) and assert the committed report and index update.

**Demo**

Reviewer opens `docs/runbooks/dr-reports/index.md`, reads the trend row for the latest drill and clicks through to the phase table and the linked follow-up issue. Under a minute.

**Edge cases**

* Cron fires while production is under maintenance (PAP-575): drill still runs (separate host) and notes the mode.
* Report missing a phase (script crash): renderer marks it `unknown` and files a finding.
* Linear cap (NJ-1): findings queued in `pendingIssues[]` like PAP-429.

**Dependencies**

Hard: PAP-50, PAP-274. Soft: PAP-105, PAP-48, PAP-89. Parent PAP-53 supplies `report.json`.

**Agent**

Builder: Forge (Ops Runner) with Quill on the report. Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/data-layer/maintenance-mode` = PAP-575.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-53 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-53 blocks this issue (`blocks` relation).
