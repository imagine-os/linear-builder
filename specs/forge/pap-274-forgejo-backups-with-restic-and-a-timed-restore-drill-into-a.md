---
identifier: "PAP-274"
title: "Forgejo backups with restic and a timed restore drill into a scratch stack"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Forgejo live and mirrored"
state: "Backlog"
parent: "PAP-45"
children: []
blockedBy: ["PAP-25", "PAP-273"]
blocks: ["PAP-275"]
key: "child/PAP-45/19"
url: "https://linear.app/paperos/issue/PAP-274/forgejo-backups-with-restic-and-a-timed-restore-drill-into-a-scratch"
source: "Linear snapshot 2026-09-17T06:03Z (round-2 issue)"
---

# PAP-274: Forgejo backups with restic and a timed restore drill into a scratch stack

**Goal**

Back up Forgejo data and its database nightly with a `restic` sidecar to `paperos-backups/forgejo`, write a nightly snapshot manifest of repo heads, and prove `restore.sh` restores the latest snapshot into a scratch stack whose UI lists the same repos, with timing recorded.

**Scope**

In: `forgejo-backup` sidecar (`forgejo dump` plus `pg_dump`, restic init and prune policy 14 daily, 8 weekly), `manifest.json` writer, `restore.sh <snapshot> <target-dir>`, read-only restore credential, failure alert to the orchestrator webhook.

Out: full DR drill on a fresh host (PAP-53).

**Spec**

* Nightly 03:00 UTC; `restic forget --prune` weekly; `restic check` weekly.
* Manifest `{ snapshotAt, repos: [{ name, heads }] }` produced from the Forgejo API before the dump.
* Backup failure exits non-zero and POSTs to the orchestrator webhook.

**Interface contract**

Provides: repo path, `restore.sh`, `manifest.json` format, read-only credential name `RESTIC_RO_*`. Consumes: stack (child 1), bucket (PAP-25). Consumed by PAP-53 and the object-storage DR issue.

**Definition of done**

* First snapshot exists; `restore.sh` into `ops/forgejo/scratch` shows the same repos; timing in the runbook.
* Failure path tested with a bad credential (alert received).

**Test plan**

* Unit: `bats` for `restore.sh` argument handling.
* Integration: snapshot, restore, compare repo lists via API; rotated credential produces a webhook POST.
* Timing recorded in `docs/runbooks/forgejo.md`.

**Demo**

Reviewer runs `restic snapshots` against the forge repo, then `ops/forgejo/restore.sh latest /tmp/forgejo-scratch` and opens the scratch UI on a local port listing the repos. Under 2 minutes for a small forge.

**Edge cases**

* Bucket credentials rotated: loud failure.
* Restore of a newer Forgejo dump into an older image: version check refuses.

**Dependencies**

Child 1 (hard), PAP-25. Feeds PAP-53.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Edge Case Hunter).

**Size**

S
