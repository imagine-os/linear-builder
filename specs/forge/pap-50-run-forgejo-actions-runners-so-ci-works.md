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
blockedBy: ["PAP-45", "PAP-273"]
blocks: ["PAP-53"]
key: "forge/actions-runner"
url: "https://linear.app/paperos/issue/PAP-50/run-forgejo-actions-runners-so-ci-works-even-when-github-is"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:45.357Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-50: Run Forgejo Actions runners so CI works even when GitHub is unavailable

**Goal**

Run Forgejo Actions runners on our own infrastructure so the same workflow files execute on Forgejo when GitHub is unavailable, giving CI independence to match repo independence. Linux only; macOS and Windows capacity is the separate forge non-Linux runner issue.

**Scope**

In:

* Runner deployment (docker-in-docker), labels matching the GitHub images we use, action source pointed at `code.forgejo.org`, cache, artifacts, a proof that Gate 1 passes on Forgejo, `check-workflow-portability.ts`, and `docs/engineering/ci-portability.md`.

Out: writing the gate workflows (PAP-78 onward), Playwright browser images (added when PAP-82 needs them per the guide), non-Linux runners.

**Spec**

* `ops/forgejo-runner/docker-compose.yml`: `runner-1`, `runner-2` on `code.forgejo.org/forgejo/runner` (pinned) with `docker:dind` sidecars, `capacity: 2` each (four concurrent jobs); profile `heavy` for a future Playwright runner on a bigger host. Registered against `git.${PAPEROS_DOMAIN}` with a token minted by `paperos-admin`.
* `config.yml` labels `ubuntu-latest:docker://ghcr.io/catthehacker/ubuntu:act-22.04`, `ubuntu-22.04` alias, `node-22:docker://node:22-bookworm`; `cache.enabled: true` on a named volume; `DEFAULT_ACTIONS_URL=https://code.forgejo.org` in `app.ini` (PAP-45).
* Workflows live only in `.github/workflows/`; Forgejo reads that directory natively.
* `check-workflow-portability.ts` flags GitHub-only actions not mirrored on `code.forgejo.org`, `github.*` context use without fallbacks, and secrets missing from `ops/forge/secrets-manifest.yml`.
* Nightly `docker system prune -af --filter until=72h`.

**Interface contract**

Provides:

* Runner labels `ubuntu-latest`, `ubuntu-22.04`, `node-22` usable in `runs-on` on both forges; concurrency figure (four jobs) documented for PAP-102 scheduling.
* Script `pnpm tsx scripts/check-workflow-portability.ts <workflow>` run in Gate 1 (PAP-78) and by PAP-51 during bootstrap.
* `ops/forge/secrets-manifest.yml` as the single list of CI secret names for both forges (PAP-51 sets them).
* Cron workflow `ops/forge/mirror-fallback.yml` fetching from GitHub every 10 minutes (PAP-47 fallback).
* Guide `ci-portability.md` linked from PAP-46.

Consumes: Actions enabled and `DEFAULT_ACTIONS_URL` (PAP-45), host capacity (PAP-25; runners on a second host if RAM is under 8 GB).

**Definition of done**

* Two runners online in org settings (screenshot at 1280).
* Smoke or Gate 1 workflow passes on Forgejo and GitHub from the same commit (both URLs).
* Forgejo job log proves `actions/checkout` came from `code.forgejo.org`, no `github.com` access.
* Cache hit on second run with before and after timings; artifact upload and download shown.
* Portability script has passing and failing fixtures; guide merged; Linear comment with both run URLs and the concurrency figure; changelog under Infra.

**Test plan**

* Unit: portability checker fixtures (GitHub-only action, missing secret, `github.token` use).
* Integration: `ci-smoke.yml` (or PAP-78 Gate 1) runs on both forges; job log grep for `code.forgejo.org`; `pnpm store` cache restore timing recorded.
* Capacity: launch five jobs; assert four run concurrently and one queues (screenshot).
* Ops: prune cron verified by disk usage before and after.

**Demo**

Reviewer opens the Forgejo Actions tab on `paperos-template`, watches the smoke workflow run on `runner-1`, opens the checkout step to see `code.forgejo.org` in the log, then compares with the same commit's GitHub run. Under 90 seconds.

**Edge cases**

* DinD needs privileged mode: dedicated VM or firewall documented; runners off the Forgejo host under 8 GB.
* Unmirrored action: vendor under `.github/actions/` or pin a Forgejo mirror URL.
* Secret names differ per forge: identical names enforced by the manifest.
* Twenty sessions spike: jobs queue; `heavy` profile scale-out documented.
* Fork `pull_request` events disabled on Forgejo.

**Dependencies**

PAP-45 (hard). Consumers: PAP-78, PAP-47, PAP-53, the non-Linux runner issue.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Code Reviewer).

**Size**

M: compose, config, one checker script and proofs.
