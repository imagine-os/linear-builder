---
identifier: "PAP-26"
title: "Build the app deploy pipeline: Docker images for apps/web and apps/api, staging on merge to main, production on tag, per-PR previews and rollback via Coolify"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13", "PAP-25", "PAP-30"]
blocks: ["PAP-29", "PAP-86", "PAP-88", "PAP-253", "PAP-357", "PAP-358", "PAP-365"]
key: "app-shell/app-deploy-pipeline"
url: "https://linear.app/paperos/issue/PAP-26/build-the-app-deploy-pipeline-docker-images-for-appsweb-and-appsapi"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:18:47.925Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-26: Build the app deploy pipeline: Docker images for apps/web and apps/api, staging on merge to main, production on tag, per-PR previews and rollback via Coolify

**Goal**

Turn a merge into a running application: Docker images for `apps/web`, `apps/api` and `apps/worker`, staging on merge to `main`, production on tag, per-PR preview environments and a two-minute rollback, all through Coolify on the PAP-25 host. The release train (PAP-88), e2e flows (PAP-86) and the drill (PAP-29) all deploy through this.

**Scope**

In:

* `apps/web/Dockerfile` (Turbo prune, Vite build, Caddy static with SPA fallback and immutable caching) and `apps/api/Dockerfile` (Node 22 distroless); `healthz` stub in `apps/api` until PAP-35 replaces it; `apps/worker` image once PAP-43 exists.
* `deploy.yml`: build, tag `sha-<short>` and `main`, push to GHCR and mirror to Forgejo registry (after PAP-50), then Coolify deploy webhooks.
* Production on `v*` tags (PAP-52) deploying the same digest; never rebuild.
* `preview.yml`: `pr-<n>.preview.PAPEROS_DOMAIN`, removed on close.
* Migrations as a pre-deploy step with `drizzle-kit migrate` (PAP-32).
* `pnpm deploy:rollback <env> <sha>`.

Out: Pages static demo (PAP-15), desktop and mobile artifacts (PAP-19, PAP-20).

**Spec**

* Image budgets: web under 40 MB, api under 200 MB; CI fails above.
* `docker/build-push-action` with GHA cache; no-change rebuild under 3 minutes.
* Deploy job polls Coolify deployment status until `finished`, then asserts `GET /healthz` and `/__version` equals the SHA; failure posts to Linear via PAP-97 when available.
* Concurrency `deploy-<env>` cancels superseded staging deploys; production never cancels.
* Secrets injected by Coolify from sops (`ops/secrets/<env>-api.enc.yaml`); Trivy scan before push (PAP-80).
* `paperos create` copies `deploy.yml` and `preview.yml` with resource names templated.

**Interface contract**

Provides:

* Images `ghcr.io/imagine-os/<app>-web|api|worker:sha-<short>`; Coolify resources `paperos-<env>-web|api|worker`.
* Endpoints `/healthz` and `/__version` on every service (PAP-25 convention).
* Preview URL pattern `https://pr-<n>.preview.PAPEROS_DOMAIN` consumed by PAP-82, PAP-86, PAP-83.
* Workflow inputs: repository secrets `COOLIFY_TOKEN`, `GHCR_TOKEN`; reusable workflow `imagine-os/paperos-infra/.github/workflows/deploy.yml@main` with inputs `app`, `env`, `sha`.
* Command `pnpm deploy:rollback`.

Consumes: host, domain and token (PAP-25), staging and production databases (PAP-30), `drizzle-kit migrate` (PAP-32), tags (PAP-52), env schema (PAP-17).

**Definition of done**

* Merge to `main` deploys `https://staging.PAPEROS_DOMAIN`; `/__version` shows the SHA.
* Tag `v0.0.1-test` deploys the same digest to production (digests compared in the log), then the tag is removed.
* PR preview live within 5 minutes and removed within 5 minutes of close.
* Rollback restores the previous SHA on staging in under 2 minutes (timed log).
* Broken-migration PR blocked before rollout; staging keeps serving.
* `docs/runbooks/deploy.md`, ADR, CHANGELOG, Linear comment.

**Test plan**

* Unit: Vitest for the deploy script's Coolify status polling and version assertion against a mocked API.
* Build: image size checks and Trivy gate in CI.
* Integration: staging deploy smoke (`/healthz`, `/__version`) after every merge; preview smoke on every PR.
* Failure injection: PR with `SELECT 1/0` migration; assert workflow red, staging version unchanged.
* Timing: rollback timed with `date` in the job log; must be under 120 s.

**Demo**

Reviewer opens the latest `deploy.yml` run, clicks through to `https://staging.PAPEROS_DOMAIN/__version` and matches the SHA to the merge commit, then opens any PR's `pr-<n>.preview` URL. Under 90 seconds.

**Edge cases**

* GHCR outage: Forgejo registry as fallback pull source.
* Wrong `BASE_PATH`: web images always use `/`.
* Two merges in a minute: the concurrency group keeps the newest.
* Rotated Coolify token: clear failure pointing at `INVENTORY.md`.
* Fork PR previews skipped with a comment.
* Rollout fails health after a successful migration: previous image redeployed; migration rollback manual and documented.

**Dependencies**

PAP-13, PAP-25, PAP-30 (hard). Milestone: moved on 2026-09-17 (round-2 FIX-1) from "Template scaffolds and runs on web" (09-20) to "Desktop and mobile shells build" (09-24) because the staging deploy needs the database PAP-30 provisions, whose milestone is 09-22; the template still scaffolds and runs locally on 09-20 without this pipeline. Soft: PAP-17, PAP-32, PAP-35, PAP-43, PAP-52, PAP-80. Consumed by PAP-86, PAP-88, PAP-29, PAP-22, PAP-147.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor for secrets handling).

**Size**

M: two Dockerfiles, two workflows, one rollback script, all provable.
