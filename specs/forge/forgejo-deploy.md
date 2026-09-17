---
identifier: "PAP-45"
title: "Deploy Forgejo on the VPS behind Caddy with SSO from Better Auth and nightly backups"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Forgejo live and mirrored"
state: "Backlog"
parent: null
children: ["PAP-275", "PAP-274", "PAP-273"]
blockedBy: ["PAP-25"]
blocks: ["PAP-276", "PAP-47", "PAP-48", "PAP-50", "PAP-54"]
key: "forge/forgejo-deploy"
url: "https://linear.app/paperos/issue/PAP-45/deploy-forgejo-on-the-vps-behind-caddy-with-sso-from-better-auth-and"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-45: Deploy Forgejo on the VPS behind Caddy with SSO from Better Auth and nightly backups

**Goal**

Stand up PaperOS's own Git forge: Forgejo running in Docker on the Hetzner VPS under Coolify, served over TLS by Caddy, with an org structure that mirrors imagine-os, nightly backups that are proven restorable, and an OIDC login path from Better Auth ready to switch on. After this issue, every later forge issue has a live server to configure.

**Scope**

- In: Docker Compose stack (Forgejo, its Postgres, backup sidecar), Caddy/Coolify routing, `app.ini` hardening, admin and service accounts, org `imagine-os`, backup and restore scripts, runbook.
- In: OIDC auth source configuration prepared and documented; enabled when identity/better-auth ships.
- Out: mirroring (forge/mirror), runners (forge/actions-runner), per-character bots (forge/bot-accounts).
- Out: using the application Postgres from data-layer/postgres-provision; Forgejo gets its own isolated database container.

**Spec**

Repository: `imagine-os/paperos-infra` (one of the pre-provisioned empty imagine-os repos; if it does not exist, create it with that exact name). Files:

- `ops/forgejo/docker-compose.yml`: services `forgejo` (image `codeberg.org/forgejo/forgejo:<current stable major, pinned to a digest>`), `forgejo-db` (`postgres:17-alpine`), `forgejo-backup` (alpine with `restic` cron). Volumes `forgejo-data`, `forgejo-db`. Forgejo HTTP on 3000 internal; SSH on host port 2222.
- `ops/forgejo/app.ini.tmpl` rendered by Coolify env vars: `ROOT_URL=https://git.${PAPEROS_DOMAIN}/`, `DISABLE_REGISTRATION=true`, `REQUIRE_SIGNIN_VIEW=false`, `ENABLE_PUSH_CREATE_ORG=false`, `[actions] ENABLED=true`, `[lfs] enabled`, `[webhook] ALLOWED_HOST_LIST=private,${ORCHESTRATOR_HOST}`, `[mailer]` via Resend SMTP, `[oauth2_client] ENABLE_AUTO_REGISTRATION=true`, `[repository] DEFAULT_BRANCH=main`, `[security] INSTALL_LOCK=true`.
- Coolify: create a "Docker Compose" resource pointing at this file; proxy set to Caddy; domain `git.${PAPEROS_DOMAIN}` with automatic Let's Encrypt; health check `GET /api/healthz` every 30 s.
- Accounts: admin `justin` (created via `forgejo admin user create`, must-change-password), service admin `paperos-admin` with an API token stored in the Coolify secrets store and in `ops/secrets/forgejo.enc.yaml` (sops + age).
- Org `imagine-os` with teams `owners`, `agents` (write), `ci` (read). Repos are created in forge/mirror, not here.
- Backups: `ops/forgejo/backup.sh` runs `forgejo dump` plus `pg_dump` at 03:00 UTC, uploads with restic to a Hetzner Object Storage bucket `paperos-forgejo-backups`, keeps 30 daily / 8 weekly snapshots. `ops/forgejo/restore.sh <snapshot>` restores into a fresh compose project and is executed once in CI-less form to prove it works.
- OIDC: `docs/runbooks/forgejo.md` documents the exact `forgejo admin auth add-oauth` command against the Better Auth OIDC provider endpoint (`https://${APP_DOMAIN}/api/auth/oauth2/...`), with a flag `SSO_ENABLED` in the compose env defaulting to false until identity/better-auth merges.
- Observability: expose `/metrics` (`[metrics] ENABLED=true`, bearer token) for data-layer/observability to scrape later.

**Definition of done**

- `https://git.<domain>/` loads with a valid certificate; `/api/healthz` returns 200.
- `git clone` over HTTPS and over SSH port 2222 works from a fresh machine using a deploy token.
- Registration is disabled; only `justin` and `paperos-admin` exist.
- One backup snapshot exists in object storage and `restore.sh` restores it into a scratch stack whose UI shows the same repos.
- Compose file and `app.ini.tmpl` committed; secrets only in sops-encrypted files (Sentinel Security Auditor confirms no plaintext).
- Runbook `docs/runbooks/forgejo.md` covers deploy, upgrade, backup, restore and the SSO switch.
- Playwright screenshot of the Forgejo landing page at 1280 and 375 widths attached to the PR (proves TLS and branding).
- Linear comment with the forge URL, backup bucket name and the restore drill timing.

**Edge cases**

- VPS has under 4 GB RAM: set `FORGEJO__cron__ENABLED` conservatively and document the minimum spec; do not co-locate runners on the same host yet.
- Coolify's default proxy is Traefik: switch the server proxy to Caddy before creating the resource, or document the equivalent Traefik labels as a fallback.
- Let's Encrypt rate limit hit during retries: use the staging CA for testing, switch to production once.
- Object storage credentials rotate: backup script must fail loudly (exit non-zero, post to the orchestrator webhook) rather than silently skipping.
- Forgejo major upgrade requires migration: runbook includes a pre-upgrade snapshot step and a `forgejo migrate` command.
- SSH port 2222 blocked on some networks: document HTTPS token auth as the primary agent path.

**Dependencies**

- app-shell/vps-coolify-bootstrap (hard: the Hetzner host, Coolify with Caddy proxy, `git.` DNS record, sops keys and backup bucket). Soft: identity/better-auth (SSO switch), data-layer/observability (metrics scrape), forge/vcs-decision-adr (rationale).

**Agent**

- Builds: Forge, via the Ops Runner sub-agent.
- Reviews: Sentinel (Security Auditor for secrets, exposure and registration settings; Code Reviewer for compose correctness).

**Size**

L: infrastructure with TLS, backups and a restore proof, each of which can surface environment surprises.
