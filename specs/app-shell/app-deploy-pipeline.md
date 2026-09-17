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
blocks: ["PAP-253", "PAP-29", "PAP-86", "PAP-88"]
key: "app-shell/app-deploy-pipeline"
url: "https://linear.app/paperos/issue/PAP-26/build-the-app-deploy-pipeline-docker-images-for-appsweb-and-appsapi"
source: "plan/specs/gaps.json (round-1 canonical spec JSON)"
---

# PAP-26: Build the app deploy pipeline: Docker images for apps/web and apps/api, staging on merge to main, production on tag, per-PR previews and rollback via Coolify

**Goal**

Turn a merge into a running application. `quality/release-train` schedules a nightly staging deploy and a Monday production promotion, `quality/e2e-flows` and `realtime/load-test` need a staging URL, and `app-shell/create-cli` promises every new app a live environment, but no issue builds the images or the Coolify applications they deploy to. This issue does, for the template itself and for every app generated from it.

**Scope**

In:
- `apps/web/Dockerfile` (multi-stage: pnpm install with Turbo prune, Vite build, `caddy` static image serving `dist/` with SPA fallback and immutable asset caching) and `apps/api/Dockerfile` (Node 22 distroless, `node dist/server.js`); if `apps/api` does not exist yet when this issue runs, ship a `healthz` stub server in `apps/api` that `data-layer/api-layer` replaces.
- GitHub Actions workflow `deploy.yml`: on push to `main` build both images, tag `sha-<short>` and `main`, push to GHCR (`ghcr.io/imagine-os/<app>-web|api`) and mirror to Forgejo's registry when `forge/actions-runner` lands; then call the Coolify deploy webhook for `paperos-staging-web` and `paperos-staging-api`.
- Production: on tag `v*` (from `forge/release-tags`) deploy the same immutable image digest to `paperos-production-*`; never rebuild for production.
- Migrations: `apps/api` container runs `drizzle-kit migrate` as a Coolify pre-deploy command against the environment's Postgres (`data-layer/postgres-provision`); a failing migration aborts the rollout.
- Per-PR previews: `preview.yml` deploys the web image to `pr-<n>.preview.PAPEROS_DOMAIN` (Coolify preview deployments) pointed at the staging API with `?tenant=preview-<n>`; torn down on PR close. Complements `app-shell/gh-pages-demo`, which stays the public static demo path.
- Rollback: `pnpm deploy:rollback <env> <sha>` calls Coolify to redeploy a previous image tag; `quality/release-train` calls this.
- Runtime config: images read `serverEnvSchema` and `publicEnvSchema` from `app-shell/env-config`; `/__version` returns SHA and build time; `/healthz` per the host convention.
- Coolify resource definitions exported to `ops/coolify/<env>-<service>.json` for reproducibility (`forge/dr-drill` restores from them).

Out: Tauri binaries (`app-shell/tauri-desktop` handles signed builds), Storybook and Pages deploys, Hocuspocus/Electric/Forgejo containers (their own issues), blue/green or canary strategies.

**Spec**

- Image size budgets: web under 40 MB, api under 200 MB; CI fails above.
- Build cache: `docker/build-push-action` with GHA cache; a no-change rebuild completes under 3 minutes.
- Deploy job waits on Coolify's deployment status API until `finished`, then smoke-tests `GET /healthz` and asserts `/__version` equals the pushed SHA; failure marks the job red and posts to the Linear issue through `pm-linear/webhooks` when available.
- Concurrency group `deploy-<env>` cancels superseded staging deploys; production deploys never cancel.
- Secrets are injected by Coolify from sops-decrypted values (`ops/secrets/<env>-api.enc.yaml`), never baked into images; `quality/security-scans` scans images with Trivy before push.
- `paperos create` (`app-shell/create-cli`) copies `deploy.yml` and `preview.yml` and templates the app name into Coolify resource names.

**Definition of done**

- Merge to `main` deploys to `https://staging.PAPEROS_DOMAIN`; `/__version` shows the SHA (screenshot and workflow link).
- A test tag `v0.0.1-test` deploys the same digest to production; `docker inspect` digests match (log attached), then the tag is deleted.
- A PR opens a preview at `pr-<n>.preview.PAPEROS_DOMAIN` within 5 minutes and is removed within 5 minutes of close.
- Rollback command restores the previous SHA on staging in under 2 minutes (timed log).
- Migration failure test: a PR with a deliberately broken migration is blocked before rollout, staging keeps serving the old version.
- `docs/runbooks/deploy.md`, ADR on image and registry choices, `CHANGELOG.md` entry, Linear comment with the URLs.

**Edge cases**

- GHCR rate limits or outage: registry mirror on Forgejo is the fallback pull source; documented in the runbook.
- Web image built with the wrong `BASE_PATH`: web images always use `/`; only `app-shell/gh-pages-demo` sets a sub-path.
- Two merges within a minute: the concurrency group cancels the first staging deploy; the second carries both changes.
- Coolify webhook fires but the API token was rotated: job fails with a clear message pointing at `ops/secrets/INVENTORY.md`.
- Preview environment for a PR from a fork: skipped (no secrets exposure) with a comment explaining why.
- Database migration succeeds but the rollout fails health checks: automatic redeploy of the previous image; migration rollback stays manual and documented, since Drizzle migrations are forward-only by default.

**Dependencies**

`app-shell/monorepo-scaffold` (build scripts), `app-shell/vps-coolify-bootstrap` (host, Coolify token, domain), `data-layer/postgres-provision` (staging and production databases). Soft: `app-shell/env-config`, `data-layer/api-layer`, `forge/release-tags`, `quality/security-scans`. Consumed by `quality/release-train`, `quality/e2e-flows`, `realtime/load-test`, `app-shell/create-cli`, `app-shell/new-app-drill`.

**Agent**

Built by Forge (Ops Runner sub-agent). Reviewed by Sentinel (Security Auditor for secrets handling, Code Reviewer for workflows) and Atlas (Merger sub-agent, who will operate promotions).

**Size**

M: standard container pipeline, but it is on the critical path of the release train and of the P0 goal that parallel sessions can see their work running.
