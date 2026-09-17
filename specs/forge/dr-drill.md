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
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-53: Run a disaster-recovery drill rebuilding all repos and CI from Forgejo backups with GitHub offline

**Goal**

Prove, not assume, that PaperOS survives GitHub disappearing: rebuild the forge, every repository and a working CI pipeline on a fresh host from Forgejo backups while github.com is blocked, then record recovery time and data loss. The drill is scripted so it can be repeated monthly.

**Scope**

- In: a drill script, a throwaway Hetzner host provisioned and destroyed by the script, network isolation from GitHub, restoration of Forgejo and runners, verification that a PR passes gate 1 on the restored forge, a timed report, and fixes for any gap found.
- Out: application database recovery (data-layer/postgres-provision owns its own PITR drill) and restoring Linear (external SaaS).

**Spec**

In `imagine-os/paperos-infra`, `ops/forge/dr/`:

- `drill.sh` orchestrates: (1) `hcloud server create` a `cpx31`-class VM from a cloud-init that installs Docker; (2) adds `0.0.0.0 github.com api.github.com objects.githubusercontent.com ghcr.io` to `/etc/hosts` and an `nftables` drop rule for GitHub IP ranges fetched beforehand from `https://api.github.com/meta` so isolation is real; (3) installs `restic`, restores the latest snapshot from the `paperos-forgejo-backups` bucket (forge/forgejo-deploy) using the read-only restore credential; (4) brings up the Forgejo compose stack from the restored dump with a temporary domain `dr-git.${PAPEROS_DOMAIN}` (DNS record created via the Hetzner DNS API, TLS via Let's Encrypt staging to avoid rate limits); (5) starts one Forgejo runner from forge/actions-runner registered to the restored instance; (6) verifies every repo in `repos.yml` exists and that `git ls-remote` heads match the snapshot manifest; (7) pushes a `chore(dr): drill <date>` commit to a branch of `paperos-template`, opens a PR via the API and waits for the gate-1 workflow to pass; (8) records timestamps for each phase into `report.json`; (9) tears down the VM and DNS record unless `--keep`.
- Action dependencies must resolve without GitHub: step 7 succeeds only if `DEFAULT_ACTIONS_URL` points at code.forgejo.org and any GitHub-only actions have been vendored; any failure here is itself a drill finding.
- Targets: RTO under 2 hours from start to green PR; RPO under 24 hours (age of the newest restorable commit versus the current heads on the live forge, measured by comparing manifests).
- Report: `render-report.ts` writes `docs/runbooks/dr-reports/<yyyy-mm-dd>.md` with a phase timing table, RTO and RPO figures against targets, the list of repos verified, gaps found with linked follow-up Linear issues, and screenshots of the restored Forgejo UI and the green PR captured with Playwright at 1280 width.
- Schedule: a Forgejo Actions cron on the first day of each month runs `drill.sh --auto` and opens a Linear issue in project forge with the report summary; failures label the issue `Infra` and move it to Ready for Claude for Forge to address.
- Cost guard: the script aborts if the VM has run more than 4 hours.

**Definition of done**

- One full drill executed; `report.json` and the rendered markdown report committed.
- Isolation proven: the report includes `curl -sS https://api.github.com` failing from the drill host.
- All repos in `repos.yml` restored with matching heads; any mismatch explained.
- Gate-1 PR passed on the restored forge without GitHub access (run URL and screenshot).
- RTO and RPO figures reported; if a target is missed, a follow-up issue exists and is linked.
- Monthly cron configured and its first scheduled run date noted.
- Runbook `docs/runbooks/disaster-recovery.md` explains manual execution and what to do if the backup bucket itself is unavailable (secondary copy recommendation).
- Sentinel (Edge Case Hunter) reviews the report; Linear comment with the report link and headline numbers.

**Edge cases**

- Latest snapshot is corrupt: script falls back to the previous snapshot and records the extra RPO.
- Hetzner API quota or region capacity exhausted: retry in a second location; report the delay.
- Let's Encrypt staging certificates are untrusted by the runner's git: configure `GIT_SSL_CAINFO` with the staging root in the drill host only; never in production.
- Runner images cached from ghcr.io are unavailable: the runner must pull from `code.forgejo.org` or a pre-pushed copy in the Forgejo container registry; document which images are pre-mirrored.
- Restored Forgejo still has webhooks pointing at production orchestrator: drill disables webhooks after restore to avoid triggering production actions.
- Someone pushes to production during the drill: manifests are compared against the snapshot time, not the live heads, to avoid false drift.

**Dependencies**

- forge/mirror (repo list and manifests), forge/actions-runner (runner and action-source independence). Soft: forge/forgejo-deploy (backups), quality/ci-gate1 (workflow to run).

**Agent**

- Builds: Forge (Ops Runner sub-agent) executes; Sentinel's Edge Case Hunter co-designs the failure scenarios.
- Reviews: Sentinel (lead) signs off the report; Atlas confirms follow-up issues are filed.

**Size**

M: the script is a sequence of known operations, but the live drill will take hours and likely produce fixes.
