---
identifier: "PAP-273"
title: "Forgejo compose stack behind Caddy with hardened app.ini, accounts and org"
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
blockedBy: ["PAP-25"]
blocks: ["PAP-47", "PAP-48", "PAP-50", "PAP-274", "PAP-498", "PAP-519", "PAP-520", "PAP-521", "PAP-522", "PAP-529", "PAP-530", "PAP-534", "PAP-535"]
key: "child/PAP-45/18"
url: "https://linear.app/paperos/issue/PAP-273/forgejo-compose-stack-behind-caddy-with-hardened-appini-accounts-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:48.946Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-20"
cycle: null
---

# PAP-273: Forgejo compose stack behind Caddy with hardened app.ini, accounts and org

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Infra M

**Goal**

Bring Forgejo up on the PAP-25 host as a Coolify Docker Compose resource behind Caddy with TLS, its own Postgres, hardened `app.ini`, admin and service accounts, and the `imagine-os` org with `owners`, `agents`, `reviewers` teams.

**Scope**

In: `ops/forgejo/docker-compose.yml`, `app.ini.tmpl`, Coolify resource, DNS `git.`, health check, accounts `justin` and `paperos-admin`, org and teams, container registry enabled, SSH 2222.

Out: backups (child 2), OIDC (child 3).

**Spec**

* Image pinned by digest; `postgres:17-alpine` for Forgejo's database; named volumes.
* `app.ini` keys per parent, including `DEFAULT_ACTIONS_URL` and `[packages] ENABLED=true`.
* `paperos-admin` API token stored in `ops/secrets/forge.enc.yaml`.

*Round 4 amendment (2026-09-18):*

* `[repository] DEFAULT_REPO_UNITS = repo.code,repo.releases,repo.actions,repo.packages` (issues, wiki, projects and pull-request discussions beyond review are disabled: Linear is the system of record). \* `[packages]` retention: `LIMIT_TOTAL_OWNER_SIZE = 20 GiB`, a weekly `forgejo admin packages cleanup` cron keeping the last 20 versions per package (shared with PAP-498) and container images referenced by no Coolify resource for 30 days.

**Interface contract**

Provides: `https://git.PAPEROS_DOMAIN`, API `/api/v1`, SSH 2222, registry path, `FORGEJO_ADMIN_TOKEN`, org and team names. Consumes: PAP-25 host, Caddy, DNS, sops, Resend SMTP.

**Definition of done**

* Landing page over valid TLS; `/api/healthz` 200; clone over HTTPS token and SSH from another network.
* Registration disabled; only two accounts; Sentinel confirms no plaintext secrets.
* Screenshots at 1280 and 375.

**Test plan**

* Unit: template render test; `docker compose config` validation.
* Integration: health, clone HTTPS and SSH from CI; sign-up returns 403.
* Security: `gitleaks` on the infra repo.
* Visual: landing page two widths.

**Demo**

Reviewer opens the forge URL, logs in as `justin`, views the `imagine-os` org and teams, then clones a repo with a token. Under a minute.

**Edge cases**

* Traefik default proxy: switch to Caddy first.
* ACME rate limit: staging CA during retries.

**Dependencies**

PAP-25 (hard). Blocks children 2 and 3, PAP-47, PAP-48, PAP-50.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor).

**Size**

M

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/app-shell/upgrade-package-registry` = PAP-498.
