---
identifier: "PAP-50"
title: "Run Forgejo Actions runners so CI works even when GitHub is unavailable"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "CI runs on both forges"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-273", "PAP-45"]
blocks: ["PAP-53"]
key: "forge/actions-runner"
url: "https://linear.app/paperos/issue/PAP-50/run-forgejo-actions-runners-so-ci-works-even-when-github-is"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-50: Run Forgejo Actions runners so CI works even when GitHub is unavailable

**Goal**

Run Forgejo Actions runners on our own infrastructure so that the same workflow files execute on Forgejo when GitHub is unavailable, giving CI independence to match repo independence. Workflows stay single-sourced and action dependencies are fetched from a mirror we control.

**Scope**

- In: runner deployment (docker-in-docker), labels matching the GitHub images we use, action-source configuration, caching, artifact storage, a proof that the gate-1 workflow passes on Forgejo, and a workflow-compatibility guide.
- Out: writing the gate workflows themselves (quality/ci-gate1 and later gates), and Playwright browser images (added when quality/playwright-matrix needs them, following this guide).

**Spec**

In `imagine-os/paperos-infra`:

- `ops/forgejo-runner/docker-compose.yml`: service `runner` using `code.forgejo.org/forgejo/runner:<current stable, pinned>` with a `docker:dind` sidecar, registered against `https://git.${PAPEROS_DOMAIN}` with a registration token minted by `paperos-admin`. Two runner instances (`runner-1`, `runner-2`) with `capacity: 2` each so four jobs run concurrently; a separate compose profile `heavy` for a future Playwright runner on a bigger host.
- `ops/forgejo-runner/config.yml`: labels `ubuntu-latest:docker://ghcr.io/catthehacker/ubuntu:act-22.04`, `ubuntu-22.04` alias, `node-22:docker://node:22-bookworm`; `container.network: host` disabled; `cache.enabled: true` with `cache.dir` on a named volume; `actions.url` left default but `DEFAULT_ACTIONS_URL` in Forgejo `app.ini` set to `https://code.forgejo.org` so `actions/checkout@v4` and friends resolve to the Forgejo mirror instead of github.com.
- Workflow single-sourcing: workflows live only in `.github/workflows/*.yml`; Forgejo reads that directory natively. A compatibility test in this issue runs the current gate-1 workflow from quality/ci-gate1 (or a placeholder `ci-smoke.yml` that installs pnpm, runs `pnpm -r typecheck` and `pnpm -r test`) on Forgejo and records the run URL.
- Artifacts: Forgejo Actions artifacts v4 enabled; retention 14 days; `actions/upload-artifact@v4` verified.
- `docs/engineering/ci-portability.md`: list of GitHub-only features we avoid (`github.token` scopes differences, `pull_request_target`, OIDC federation, required-workflows) and the substitutions (`secrets.FORGEJO_TOKEN`, explicit `on: pull_request` only). A lint script `scripts/check-workflow-portability.ts` flags disallowed constructs and is wired into gate 1.
- Runner health: `runner-1` exposes a heartbeat via `forgejo-runner status`; a Coolify cron restarts a runner that has been idle-offline for 5 minutes; metrics scraped later by data-layer/observability.

**Definition of done**

- Two runners show as online in Forgejo org settings (screenshot at 1280 attached).
- The smoke or gate-1 workflow passes on Forgejo and on GitHub from the same commit; both run URLs in the PR.
- Runs on Forgejo fetch `actions/checkout` from code.forgejo.org (job log excerpt proves no github.com access).
- Cache hit demonstrated on a second run (`pnpm store` restored; timing before/after recorded).
- Artifact upload and download demonstrated.
- `check-workflow-portability.ts` has tests with one passing and one failing fixture.
- `ci-portability.md` merged and linked from the branch policy.
- Linear comment with both run URLs and the concurrency figure.
- Changelog entry under "Infra".

**Edge cases**

- Docker-in-docker needs privileged mode: document the host hardening (dedicated VM or firewall) and keep runners off the Forgejo host if RAM is under 8 GB.
- An action pinned to a GitHub-hosted repo not mirrored on code.forgejo.org: guide says vendor it under `.github/actions/` or pin a Forgejo mirror URL.
- Secrets differ per forge: use identical secret names on both; `check-workflow-portability.ts` warns on any secret referenced but missing from `ops/forge/secrets-manifest.yml`.
- Runner disk fills with images: nightly `docker system prune -af --filter until=72h` cron.
- Concurrency spike from twenty sessions: jobs queue; document expected wait and the `heavy` profile scale-out.
- `pull_request` events from forks: disabled on Forgejo (no forks allowed for agents) and documented.

**Dependencies**

- forge/forgejo-deploy (Actions enabled in `app.ini`). Consumers: quality/ci-gate1, forge/mirror (cron fallback), forge/dr-drill.

**Agent**

- Builds: Forge (Ops Runner sub-agent).
- Reviews: Sentinel (Security Auditor on privileged runners; Code Reviewer on portability lint).

**Size**

M: runner deployment is routine, but proving action-source independence and portability adds verification work.
