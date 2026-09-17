---
identifier: "PAP-25"
title: "Provision the Hetzner VPS with Coolify, Caddy, DNS for the PaperOS domain, object storage, sops keys and the paperos-infra repo"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Template scaffolds and runs on web"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-140", "PAP-26", "PAP-273", "PAP-274", "PAP-30", "PAP-45", "PAP-96"]
key: "app-shell/vps-coolify-bootstrap"
url: "https://linear.app/paperos/issue/PAP-25/provision-the-hetzner-vps-with-coolify-caddy-dns-for-the-paperos"
source: "plan/specs/gaps.json (round-1 canonical spec JSON)"
---

# PAP-25: Provision the Hetzner VPS with Coolify, Caddy, DNS for the PaperOS domain, object storage, sops keys and the paperos-infra repo

**Goal**

Create the single self-hosted environment that `forge/forgejo-deploy`, `data-layer/postgres-provision`, `realtime/yjs-server`, `pm-linear/orchestrator`, `data-layer/local-first-sync` (Electric) and `quality/release-train` all silently assume already exists: a Hetzner VPS running Coolify behind Caddy, the `PAPEROS_DOMAIN` DNS zone, a Hetzner Object Storage bucket for backups, an age/sops key pair for encrypted secrets, a Resend account with a verified sending domain, and the `imagine-os/paperos-infra` repository that holds all of it as code. Without this issue the P0 infra issues are not actually parallel: each would provision its own host or block on Justin.

**Scope**

In:
- Hetzner Cloud project and one VPS (`cpx31` class, Ubuntu 24.04, 8 GB RAM minimum so Forgejo, Postgres, Hocuspocus, Electric and the orchestrator co-locate; document the upgrade path to a second host).
- Coolify (latest stable) installed via the official script; server proxy switched from Traefik to Caddy before any resource is created (matches `forge/forgejo-deploy`); Coolify admin account for Justin; API token for the release pipeline stored as a GitHub Actions secret `COOLIFY_TOKEN` and in sops.
- DNS: zone for `PAPEROS_DOMAIN` (Justin's registrar; if he has none, Cloudflare free) with records `@`, `app.`, `api.`, `staging.`, `git.`, `collab.`, `sync.`, `orchestrator.`, `s3.`; wildcard `*.preview.` for per-PR previews; Let's Encrypt via Caddy.
- Hetzner Object Storage bucket `paperos-backups` (restic repo) and `paperos-files` (MinIO alternative for `data-layer/file-storage` if MinIO is not self-hosted); access keys in sops.
- sops with age: `ops/secrets/.sops.yaml`, one age key held by Justin (recovery) and one by the orchestrator service; `ops/secrets/*.enc.yaml` per service; `pnpm secrets:edit <service>` wrapper.
- Resend account, domain verification (SPF, DKIM, DMARC records added to the zone), `RESEND_API_KEY` in sops; sandbox mode default (matches `identity/better-auth` and `growth/outreach-sequences`).
- Tailscale tailnet (free tier) joining the VPS and Justin's machine so Postgres and Coolify admin are never public (`data-layer/postgres-provision` already assumes a tailnet).
- Firewall (Hetzner Cloud firewall): 80/443 public; 22 and 8000 (Coolify) tailnet only.
- Repo `imagine-os/paperos-infra`: `ops/terraform/` (hcloud provider: server, firewall, volumes, DNS if Cloudflare) or, if Terraform is judged too heavy for one host, `ops/cloud-init.yaml` plus `ops/bootstrap.sh`, with the choice recorded in an ADR; `docs/runbooks/host.md`.

Out: any application container (owned by the consuming issues); GitHub Pages (`app-shell/gh-pages-demo`); monitoring dashboards (`data-layer/observability`); the disaster-recovery drill (`forge/dr-drill`, which re-uses this bootstrap on a fresh VM).

**Spec**

- `ops/bootstrap.sh` is idempotent: re-running on a provisioned host changes nothing (checked with a dry-run flag that prints planned actions).
- Environment matrix recorded in `docs/runbooks/host.md`: `production` and `staging` are separate Coolify projects on the same host with separate Postgres instances (`data-layer/postgres-provision`), separate domains (`app.` vs `staging.`) and separate secrets files.
- Coolify resource naming convention `paperos-<env>-<service>` and a label `paperos.owner=<agent>` so the orchestrator can list what each character deployed.
- Health endpoint convention: every service exposes `GET /healthz` returning `{ ok, version, sha }`; Coolify health checks every 30 s.
- Secret inventory `ops/secrets/INVENTORY.md`: name, service, rotation owner, last rotated; CI job fails when a secret referenced in any `*.enc.yaml` is missing from the inventory.
- Cost note in the ADR: monthly total for VPS, object storage, domain, Resend, Tailscale (expected under 40 EUR/month) so Justin approves once.

**Definition of done**

- `https://git.PAPEROS_DOMAIN`, `https://staging.PAPEROS_DOMAIN` and `https://app.PAPEROS_DOMAIN` return a Coolify placeholder or the first deployed service over valid TLS (screenshots at 1280 and 375).
- `ssh` to the host works only over the tailnet; public port scan shows 80/443 only (nmap output attached).
- `sops -d ops/secrets/example.enc.yaml` works with the orchestrator key; Justin's recovery key decrypts the same file (he confirms once in the Needs Justin item that also asks for the Hetzner and registrar credentials).
- Resend test email delivered to Justin's inbox from `noreply@PAPEROS_DOMAIN` with passing SPF/DKIM (headers attached).
- Restic repo initialised in `paperos-backups`; `restic snapshots` lists the first snapshot of `/data/coolify`.
- `docs/runbooks/host.md`, ADR `docs/adr/00xx-hosting-bootstrap.md`, `CHANGELOG.md` entry, Linear comment with URLs and the cost table.

**Edge cases**

- Justin has no domain yet: use a `*.sslip.io` address for staging so nothing blocks, and leave a single Needs Justin item asking for the domain; switching later is one env var (`PAPEROS_DOMAIN`) and a Caddy reload.
- Hetzner account needs identity verification (can take a day): the Needs Justin item is filed first thing in the session, and the rest of the issue proceeds against a local Coolify in a VM (`multipass`) so scripts are verified before the host exists.
- Coolify install script fails on Ubuntu 24.04 kernel: pin the Coolify version tested and record the fix.
- Cloudflare proxy (orange cloud) breaks Let's Encrypt HTTP challenge and WebSockets for `collab.`: keep DNS-only (grey cloud) for all records.
- sops key loss: the recovery key is printed once for Justin to store offline; the runbook covers re-keying every file.
- Host disk fills from Docker images: weekly `docker system prune` cron in Coolify, alert at 80 percent via `data-layer/observability` when available.

**Dependencies**

None; ready now, and the earliest infra issue to start because `forge/forgejo-deploy`, `data-layer/postgres-provision`, `pm-linear/orchestrator`, `realtime/yjs-server` and `app-shell/app-deploy-pipeline` deploy onto it. Soft: `app-shell/env-config` (secret names), `libraries/license-policy`.

**Agent**

Built by Forge (Ops Runner sub-agent). Reviewed by Sentinel (Security Auditor) on firewall, secrets and account scopes. One Needs Justin item batches every credential and purchase this issue needs (Hetzner account, registrar or Cloudflare access, Resend sign-up, cost approval).

**Size**

M: mostly scripted, but it waits on real accounts, and every later infra issue is blocked until the host answers.
