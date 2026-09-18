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
blocks: ["PAP-47", "PAP-48", "PAP-50", "PAP-54", "PAP-276", "PAP-519", "PAP-520", "PAP-521"]
key: "forge/forgejo-deploy"
url: "https://linear.app/paperos/issue/PAP-45/deploy-forgejo-on-the-vps-behind-caddy-with-sso-from-better-auth-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T12:56:49.095Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-20"
cycle: null
---

# PAP-45: Deploy Forgejo on the VPS behind Caddy with SSO from Better Auth and nightly backups

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Umbrella: stand up PaperOS's own forge, Forgejo in Docker on the PAP-25 host under Coolify, served over TLS by Caddy, with org `imagine-os`, nightly backups proven restorable and an OIDC login path from Better Auth ready to switch on. Three children; closes when the restore drill passes and every later forge issue has a live server.

**Scope**

Children:

1. **PAP-273** — Forgejo compose stack behind Caddy with hardened `app.ini` (services, volumes, Coolify resource, TLS, admin and service accounts, org).
2. **PAP-274** — Backups and restore drill (`restic` sidecar to `paperos-backups/forgejo`, `restore.sh` into a scratch stack, timing).
3. **PAP-275** — OIDC auth source preparation and runbook (documented switch-on path, upgrade procedure, monitoring hooks).

Out: mirroring (PAP-47), runners (PAP-50), bots (PAP-48), using the application Postgres (Forgejo gets its own database container).

**Spec**

* Repository `imagine-os/paperos-infra`, files under `ops/forgejo/`: `docker-compose.yml` with `forgejo` (`codeberg.org/forgejo/forgejo`, pinned digest), `forgejo-db` (`postgres:17-alpine`), `forgejo-backup`; volumes `forgejo-data`, `forgejo-db`; HTTP 3000 internal, SSH host port 2222.
* `app.ini.tmpl`: `ROOT_URL=https://git.${PAPEROS_DOMAIN}/`, `DISABLE_REGISTRATION=true`, `[actions] ENABLED=true`, `DEFAULT_ACTIONS_URL=https://code.forgejo.org`, `[lfs] enabled`, `[webhook] ALLOWED_HOST_LIST=private,${ORCHESTRATOR_HOST}`, `[mailer]` via Resend SMTP, `[oauth2_client] ENABLE_AUTO_REGISTRATION=true`, `[repository] DEFAULT_BRANCH=main`, `[security] INSTALL_LOCK=true`, `[packages] ENABLED=true` (container registry for PAP-26 and PAP-50).
* Coolify Docker Compose resource, domain `git.${PAPEROS_DOMAIN}`, health `GET /api/healthz` every 30 s.
* Accounts: admin `justin` (must change password), service `paperos-admin` with an API token in sops; org `imagine-os` with teams `owners`, `agents`, `reviewers` (filled by PAP-48).

**Interface contract**

Provides:

* URLs `https://git.PAPEROS_DOMAIN` (web and API `/api/v1`), SSH `ssh://git@git.PAPEROS_DOMAIN:2222`, container registry `git.PAPEROS_DOMAIN/imagine-os/<image>`.
* Secret `FORGEJO_ADMIN_TOKEN` in `ops/secrets/forge.enc.yaml` used by PAP-46 (`apply-branch-policy.ts`), PAP-47, PAP-48 until bot tokens exist.
* Org `imagine-os` and team names above.
* Backup repo `paperos-backups/forgejo` and `restore.sh <snapshot> <target-dir>` used by PAP-53 and the object-storage DR issue.
* Webhook allowlist including the orchestrator host (PAP-97).
* OIDC auth source name `paperos` expecting issuer `https://app.PAPEROS_DOMAIN/api/auth` (PAP-57 provides).

Consumes: host, Caddy proxy, `git.` DNS, sops keys, bucket, Resend SMTP (PAP-25).

**Definition of done**

* All three children Done.
* Integration test: `git clone` over HTTPS with a deploy token and over SSH 2222 from a fresh machine; registration disabled; only `justin` and `paperos-admin` exist; `restore.sh` restores the latest snapshot into a scratch stack whose UI lists the same repos (timing recorded).
* Sentinel (Security Auditor) confirms no plaintext secret; runbook `docs/runbooks/forgejo.md`; Playwright screenshots of the landing page at 1280 and 375; Linear comment with URL, bucket and restore timing.

**Test plan**

* Unit: `app.ini.tmpl` render test with fixture env asserting every hardened key; compose file validated with `docker compose config`.
* Integration: `curl /api/healthz` 200 over TLS; `git clone` HTTPS and SSH from a CI job on a different network.
* Security: `POST /user/sign_up` returns 403; `gitleaks` on the infra repo.
* Backup: nightly cron produces a snapshot; `restore.sh` into `ops/forgejo/scratch` and compare repo lists via API.
* Visual: landing page at 1280 and 375.

**Demo**

Reviewer opens `https://git.PAPEROS_DOMAIN`, sees the imagine-os org with the mirrored repos, runs `git clone https://git.PAPEROS_DOMAIN/imagine-os/paperos-template.git` with a token, then runs `restic snapshots` against the forge bucket. Under 2 minutes.

**Edge cases**

* Under 4 GB RAM: conservative cron settings; no runners on this host.
* Coolify default proxy is Traefik: switch to Caddy first.
* Let's Encrypt rate limits: staging CA during retries.
* Rotated storage credentials: backup fails loudly and posts to the orchestrator webhook.
* Major upgrade: pre-upgrade snapshot then `forgejo migrate` in the runbook.
* SSH 2222 blocked on some networks: HTTPS token auth is the primary agent path.

**Dependencies**

PAP-25 (hard). Soft: PAP-57 SSO, PAP-40 metrics, PAP-44 rationale. Unblocks PAP-47, PAP-48, PAP-50, PAP-54.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor).

**Size**

L as an umbrella; children are M, S, S.
