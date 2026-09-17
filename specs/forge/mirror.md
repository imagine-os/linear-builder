---
identifier: "PAP-47"
title: "Configure bidirectional push mirroring between Forgejo and the GitHub org imagine-os for all repos"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Forgejo live and mirrored"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-273", "PAP-45"]
blocks: ["PAP-22", "PAP-51", "PAP-53"]
key: "forge/mirror"
url: "https://linear.app/paperos/issue/PAP-47/configure-bidirectional-push-mirroring-between-forgejo-and-the-github"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-47: Configure bidirectional push mirroring between Forgejo and the GitHub org imagine-os for all repos

**Goal**

Make every repository in the GitHub org imagine-os exist on Forgejo as well, with commits pushed to either side arriving on the other within one minute, so that either forge can act as primary and agents never have to care which one is up. Drift must be detected automatically.

**Scope**

- In: Forgejo -> GitHub push mirrors, GitHub -> Forgejo propagation via a workflow plus a Forgejo pull-mirror fallback, a script that configures all repos, a drift monitor, and a documented conflict rule.
- Out: creating new repos for new apps (forge/repo-bootstrap) and issue/PR metadata sync (issues live in Linear).
- Out: mirroring wikis or GitHub-only features (Discussions, Projects).

**Spec**

In `imagine-os/paperos-infra`:

- `ops/forge/mirror-all.ts` (TypeScript, run with `pnpm tsx`): lists imagine-os repos via GitHub REST (`GET /orgs/imagine-os/repos`), and for each: creates the Forgejo repo under `imagine-os` if missing (private flag copied), sets a Forgejo push mirror to `https://github.com/imagine-os/<repo>.git` with a fine-grained GitHub PAT (contents: read/write, scoped to the org) and `interval=10m` plus `sync_on_commit=true`, and records the pair in `ops/forge/repos.yml`. Idempotent; `--dry-run` prints planned changes; `--only <repo>` limits scope.
- GitHub -> Forgejo: a reusable workflow `.github/workflows/mirror-to-forgejo.yml` added to every repo (via the bootstrap script later, by hand for the first set) triggered on `push` to any branch and tag; it does `git push --mirror` (excluding `refs/pull/*`) to Forgejo using a deploy token from forge/bot-accounts (interim: `paperos-admin` token). Fallback: a Forgejo pull mirror is not used for the same repo (Forgejo forbids push and pull mirror on one repo); instead the fallback is a Forgejo Actions cron in forge/actions-runner that fetches from GitHub every 10 minutes when the workflow has not run.
- Loop safety: mirror pushes are no-ops when refs already match, so the push-back path terminates; document this and add a test that pushes a commit on Forgejo and asserts exactly one GitHub push event.
- Conflict rule: Forgejo is primary. If refs diverge (non-fast-forward in either direction), no force-push happens automatically; the monitor opens a Linear issue in project forge labelled `Infra` with both SHAs.
- Drift monitor `ops/forge/mirror-check.ts` scheduled every 5 minutes (Forgejo Actions cron and a Coolify cron as belt and braces): compares `git ls-remote --heads --tags` on both sides for every repo in `repos.yml`; drift older than 5 minutes posts to the orchestrator webhook (pm-linear/webhooks) and, if unavailable, creates the Linear issue directly with the Linear API.
- Docs: `docs/runbooks/mirroring.md` with the token rotation procedure.

**Definition of done**

- Every current imagine-os repo appears on Forgejo with identical branch heads and tags (`mirror-check.ts` reports zero drift).
- A commit pushed to Forgejo `main` on a test repo appears on GitHub within 60 s; a commit pushed to GitHub appears on Forgejo within 60 s; timings recorded in the PR.
- Divergence test: force-different commits on both sides produce a Linear issue, not a force-push (evidence linked).
- `mirror-all.ts --dry-run` and real run are idempotent (second run makes no API writes; test asserts on recorded HTTP calls).
- Secrets only in sops or forge secret stores; Sentinel Security Auditor confirms token scopes are minimal.
- Runbook merged; Linear comment with the drift dashboard output and timing evidence.
- Changelog entry under "Infra".

**Edge cases**

- Repo over 1 GB or with LFS objects: enable LFS mirroring flag; document that initial sync may exceed a minute.
- GitHub PAT expires (fine-grained tokens max 1 year): monitor treats 401 as drift with a distinct message "credential expired".
- Repo renamed on GitHub: script detects by repo id, renames on Forgejo, updates `repos.yml`.
- Archived GitHub repo: mirrored read-only, flagged `archived: true` in `repos.yml`; push mirror disabled.
- Protected branch on GitHub rejects the mirror push: the mirror token must bypass rulesets via an actor allowlist (set in forge/branch-policy rulesets).
- Forgejo down while GitHub receives pushes: the workflow fails and retries with backoff; the cron fallback catches up.

**Dependencies**

- forge/forgejo-deploy (must exist to host repos). Soft: forge/bot-accounts (dedicated mirror token), forge/actions-runner (cron fallback), forge/branch-policy (bypass allowlist), pm-linear/webhooks (alert path).

**Agent**

- Builds: Forge, via the Ops Runner sub-agent.
- Reviews: Sentinel (Security Auditor on tokens; Edge Case Hunter runs the divergence scenario).

**Size**

M: two propagation paths and a monitor, all scriptable, but with real timing and divergence evidence required.
