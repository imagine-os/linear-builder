---
identifier: "PAP-536"
title: "Ephemeral runner autoscaling: start docker runners on a second Hetzner host when the Forgejo job queue exceeds capacity and stop them when idle, with a cost cap"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P2"
type: "Infra"
priority: 4
surfaces: ["Developer"]
milestone: "Disaster recovery proven"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-25", "PAP-50", "PAP-519"]
blocks: []
key: "r4/forge/runner-autoscaling"
url: "https://linear.app/paperos/issue/PAP-536/ephemeral-runner-autoscaling-start-docker-runners-on-a-second-hetzner"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:03.659Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-536: Ephemeral runner autoscaling: start docker runners on a second Hetzner host when the Forgejo job queue exceeds capacity and stop them when idle, with a cost cap

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra M

**Goal**

Deferred to v0.2 (past 2026-10-01). PAP-50 sizes four concurrent jobs and says a twenty-session spike "queues"; during the 09-21 to 09-26 peak the schedule runs twenty builders plus gates. GitHub absorbs the burst today; Forgejo independence at that scale needs runners that appear on demand.

**Scope**

In:

* `ops/forgejo-runner/autoscale.ts` polling the Forgejo Actions queue (admin API) every minute; when queued jobs exceed free capacity for 5 minutes, create a `cpx31` from a cloud-init snapshot with the runner pre-registered in ephemeral mode; destroy after 30 idle minutes; hard cap 3 extra hosts and a daily EUR budget in `autoscale.yml`.
* Snapshot build workflow (weekly) with the PAP-50 images pre-pulled and the PAP-532 cached.
* Metrics into PAP-534: hosts active, minutes, cost; daily summary line in the PAP-98 burn report so runner spend sits beside credit spend.
* Runbook `docs/engineering/ci-runners.md` autoscale section: how to raise the cap for a drill, how to drain, how to rebuild the snapshot after a runner image change.

Out: macOS and Windows capacity (PAP-371), Kubernetes.

**Spec**

* Ephemeral runners take one job then re-register; secrets never persist on the host; the host is destroyed, never reused, after 30 idle minutes.
* Budget exhausted: no scale-out; alert; jobs queue on the fixed runners.
* Hetzner API failure: retry with backoff; never leaves half-created hosts (reconcile on start compares live servers with `autoscale.state.json`).
* Scale decisions are logged with queue depth, free capacity and the rule that fired so the threshold can be tuned from evidence.

**Interface contract**

Provides: `autoscale.ts`, snapshot workflow, budget config; consumed by PAP-99 (concurrency figure), PAP-53 (drill can request capacity).

Consumes: runner registration (PAP-50), Hetzner token (PAP-25), observability.

**Definition of done**

* Simulated queue of 12 jobs scales to two hosts within 8 minutes and back to zero after idle (log with timings); cap enforced; CHANGELOG; Linear comment.

**Test plan**

* Unit: scaling decision over fixture queue series; budget accounting; reconcile of orphaned hosts.
* E2E: staging: real scale-out of one host and teardown.

**Demo**

Reviewer dispatches ten dummy jobs, watches a new runner appear in org settings within minutes, and see it gone half an hour later. Under a minute of attention.

**Edge cases**

* Runner token expired in the snapshot: refreshed at boot from sops.
* Job pinned to `heavy` label: only heavy snapshots scale for it.

**Dependencies**

Hard: PAP-50, PAP-25. Soft: PAP-532, PAP-534.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/forge/forge-observability` = PAP-534, `r4/forge/playwright-runner-image` = PAP-532.
