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
blocks: ["PAP-26", "PAP-30", "PAP-45", "PAP-96", "PAP-140", "PAP-273", "PAP-274", "PAP-280", "PAP-283", "PAP-300", "PAP-301"]
key: "app-shell/vps-coolify-bootstrap"
url: "https://linear.app/paperos/issue/PAP-25/provision-the-hetzner-vps-with-coolify-caddy-dns-for-the-paperos"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:40:55.760Z"
model: "claude-opus-5"
effort: "medium"
---

# PAP-25: Provision the Hetzner VPS with Coolify, Caddy, DNS for the PaperOS domain, object storage, sops keys and the paperos-infra repo

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Infra M

**Goal**

Create the single self-hosted environment that PAP-45, PAP-30, PAP-140, PAP-96, PAP-36 and PAP-88 assume: a Hetzner VPS running Coolify behind Caddy, the `PAPEROS_DOMAIN` zone, object storage for backups, an age/sops key pair, a Resend sending domain and the `imagine-os/paperos-infra` repo holding all of it as code. One Needs Justin item collects every credential ask.

**Read first.** Read before coding: [Blueprint](<https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1>) → [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) → your project's `Contract` section (Linear project content) → your character sheet ([Roster](<https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3>)) → [Execution Schedule](<https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795>) for your start day and the branch-start rule. Also [Security & Threat Model](<https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c>) §5 (sops and age layout, two recipients, Coolify secret mirror) and §7 (the backup rows owned by PAP-25 and PAP-30); the Execution Schedule's NJ-2 batch is the single credential ask this issue files.

**Scope**

In:

* Hetzner project and one `cpx31` (Ubuntu 24.04, 8 GB) with an upgrade path documented.
* Coolify with proxy switched to Caddy before any resource; admin for Justin; `COOLIFY_TOKEN` in GitHub secrets and sops.
* DNS records `@`, `app.`, `api.`, `staging.`, `git.`, `collab.`, `sync.`, `orchestrator.`, `s3.`, `*.preview.`; Let's Encrypt via Caddy; DNS-only (no proxying).
* Object Storage buckets `paperos-backups` (restic) and `paperos-files`.
* age key pair; `ops/secrets/*.enc.yaml`; Tailscale for SSH; UFW 80/443 only.
* Resend account with verified domain, SPF and DKIM.

Out: application services (each project deploys its own), Postgres (PAP-30), Forgejo (PAP-45).

**Spec**

* `ops/bootstrap.sh` idempotent with `--dry-run`.
* `docs/runbooks/host.md`: `production` and `staging` as separate Coolify projects with separate databases, domains and secrets files.
* Resource naming `paperos-<env>-<service>`; label `paperos.owner=<agent>`.
* Health convention `GET /healthz` returning `{ ok, version, sha }`, checked every 30 s.
* `ops/secrets/INVENTORY.md`: name, service, rotation owner, last rotated; CI fails when an `*.enc.yaml` key is missing from it.
* Cost table in the ADR (target under 40 EUR/month).
* Weekly `docker system prune` timer; disk alert at 80 percent.

**Interface contract**

Provides:

* Env var `PAPEROS_DOMAIN` and the host list above; Coolify API base `https://coolify.PAPEROS_DOMAIN` and token secret name `COOLIFY_TOKEN` (PAP-26, PAP-88).
* sops recipients: `justin` and `orchestrator` age keys; file layout `ops/secrets/<env>-<service>.enc.yaml` (PAP-17 env names are the keys).
* Buckets `paperos-backups` (PAP-30 WAL, PAP-45 restic, the object-storage DR issue) and `paperos-files` (PAP-37 alternative to MinIO).
* SMTP credentials secret `RESEND_API_KEY` and sender `noreply@PAPEROS_DOMAIN` (the email package issue, PAP-57).
* Tailnet hostname `paperos-vps`.

Consumes: nothing. Credential asks (Hetzner, registrar, Resend, Apple and Windows signing are separate) go in one Needs Justin issue filed on day one.

**Definition of done**

* `git.`, `staging.` and `app.` hosts answer over valid TLS (screenshots at 1280 and 375).
* SSH only over the tailnet; public nmap shows 80 and 443 (output attached).
* `sops -d ops/secrets/example.enc.yaml` works with the orchestrator key; Justin confirms his recovery key once.
* Resend test mail passes SPF and DKIM (headers attached).
* `restic snapshots` lists the first snapshot of `/data/coolify`.
* Runbook, ADR, CHANGELOG, Linear comment with URLs and cost table.

**Test plan**

* Unit: `bats` tests for `bootstrap.sh --dry-run` idempotency on a `multipass` VM.
* Integration: CI job decrypts a fixture with a CI-scoped age key and asserts the inventory check fails on an unlisted secret.
* Security: nmap from outside; `ssh` attempt from a non-tailnet IP times out (log).
* Ops: Coolify health endpoint for a placeholder service flips red when the container is stopped (screenshot).
* Visual: Coolify dashboard and the TLS placeholder pages at 1280 and 375.

**Demo**

Reviewer opens `https://staging.PAPEROS_DOMAIN` (valid padlock), `https://coolify.PAPEROS_DOMAIN` (login), runs `sops -d ops/secrets/example.enc.yaml` with the shared key and `restic snapshots`. Under 2 minutes.

**Edge cases**

* No domain yet: `*.sslip.io` for staging; switching later is one env var and a Caddy reload.
* Hetzner identity verification delay: file the Needs Justin item first, verify scripts in a local VM meanwhile.
* Coolify install fails on the 24.04 kernel: pin the tested version.
* Cloudflare orange cloud breaks ACME and WebSockets: grey cloud everywhere.
* sops key loss: recovery key printed once for Justin; re-key runbook.

**Dependencies**

None; the earliest infra issue. Unblocks PAP-26, PAP-30, PAP-45, PAP-96, PAP-140, the signing, email, field-encryption and DR issues.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor).

**Size**

M: many small external steps, all scriptable except the credential asks.
