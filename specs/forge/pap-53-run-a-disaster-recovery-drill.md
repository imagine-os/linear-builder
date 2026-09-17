---
identifier: "PAP-53"
title: "Run a disaster-recovery drill rebuilding all repos and CI from Forgejo backups with GitHub offline"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P2"
type: "Review"
priority: 2
surfaces: ["Developer"]
milestone: "Disaster recovery proven"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-47", "PAP-50"]
blocks: []
key: "forge/dr-drill"
url: "https://linear.app/paperos/issue/PAP-53/run-a-disaster-recovery-drill-rebuilding-all-repos-and-ci-from-forgejo"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:05:43.693Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-53: Run a disaster-recovery drill rebuilding all repos and CI from Forgejo backups with GitHub offline

**Goal**

Prove, not assume, that PaperOS survives GitHub disappearing: rebuild the forge, every repository and a working CI pipeline on a fresh host from Forgejo backups while `github.com` is blocked, then record recovery time and data loss. The drill is scripted so it repeats monthly. Application data recovery is PAP-30's drill and the object-storage DR issue.

**Scope**

In:

* `ops/forge/dr/drill.sh`, a throwaway Hetzner host created and destroyed by the script, real network isolation from GitHub, restoration of Forgejo and one runner, a gate-1 PR on the restored forge, a timed report, and follow-up issues for gaps.

Out: application database recovery (PAP-30), Linear restoration (external SaaS).

**Spec**

* Phases: (1) `hcloud server create` `cpx31` from cloud-init with Docker; (2) `/etc/hosts` blackhole for `github.com`, `api.github.com`, `objects.githubusercontent.com`, `ghcr.io` plus `nftables` drop for GitHub ranges from `/meta`; (3) `restic restore` latest from `paperos-backups/forgejo` with the read-only credential; (4) Forgejo stack up on `dr-git.${PAPEROS_DOMAIN}` (Hetzner DNS API, Let's Encrypt staging); (5) one PAP-50 runner registered; (6) every repo in `repos.yml` present and `git ls-remote` heads match the snapshot manifest; (7) push `chore(dr): drill <date>` to a branch, open a PR via API, wait for Gate 1; (8) `report.json` timestamps per phase; (9) teardown unless `--keep`.
* Webhooks disabled after restore so production is never triggered.
* Monthly cron via Forgejo Actions on the production instance; report committed to the infra repo.

**Interface contract**

Provides:

* `ops/forge/dr/report.json` schema `{ startedAt, phases: [{ name, startedAt, endedAt, ok }], rtoMinutes, rpoMinutes, snapshotId, reposChecked, mismatches: [] }` rendered to `docs/runbooks/dr-reports/<date>.md` and quoted by PAP-88's digest.
* Runbook `docs/runbooks/disaster-recovery.md` including the "backup bucket unavailable" branch (secondary copy recommendation feeding the object-storage DR issue).
* Snapshot manifest format `manifest.json` `{ snapshotAt, repos: [{ name, heads: { [ref]: sha } }] }` written nightly by PAP-45's backup sidecar (this issue adds the manifest step).

Consumes: `repos.yml` (PAP-47), runner compose (PAP-50), backups and `restore.sh` (PAP-45), Gate 1 workflow (PAP-78), Hetzner token (PAP-25).

**Definition of done**

* One full drill executed; `report.json` and the rendered report committed.
* Isolation proven: `curl https://api.github.com` fails from the drill host (in report).
* All repos restored with matching heads; mismatches explained.
* Gate 1 PR passed on the restored forge without GitHub access (run URL and screenshot).
* RTO and RPO reported; missed targets have linked follow-up issues; monthly cron configured with first run date; runbook merged; Sentinel (Edge Case Hunter) reviews; Linear comment with headline numbers.

**Test plan**

* Unit: `bats` for phase ordering and `--keep`; manifest comparison with a fixture containing one mismatch.
* Integration: the drill itself, run once for this issue and monthly after; assert isolation (`curl` failure), repo count, Gate 1 success.
* Failure: corrupt latest snapshot simulated by pointing at a bad id; script falls back to the previous snapshot and records the extra RPO.
* Cost: report includes Hetzner hours consumed; target under 2 EUR per drill.

**Demo**

Reviewer opens the latest `dr-reports/<date>.md`, reads the phase table with minutes per phase and the RTO and RPO lines, then opens the linked Gate 1 run on `dr-git` (if kept) or its screenshot. Under a minute.

**Edge cases**

* Corrupt snapshot: previous snapshot, extra RPO recorded.
* Hetzner capacity exhausted: retry in a second location.
* Staging certificates untrusted by git: `GIT_SSL_CAINFO` on the drill host only.
* Runner images from `ghcr.io` unavailable: pre-mirrored on Forgejo's registry; list documented.
* Production pushes during the drill: compare against snapshot time, not live heads.

**Dependencies**

PAP-47, PAP-50 (hard). Soft: PAP-45, PAP-78, PAP-25.

**Agent**

Executed by Forge (Ops Runner); Sentinel (Edge Case Hunter) reviews the report.

**Size**

M: one script and one real run with evidence.
