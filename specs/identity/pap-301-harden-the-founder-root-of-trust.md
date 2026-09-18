---
identifier: "PAP-301"
title: "Harden the founder root of trust: hardware-key MFA on every external account, an offline recovery age key with escrow, a one-command revoke-all, and the break-glass runbook filed as a single Needs Justin checklist"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-25"]
blocks: []
key: "security/founder-break-glass"
url: "https://linear.app/paperos/issue/PAP-301/harden-the-founder-root-of-trust-hardware-key-mfa-on-every-external"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:24.366Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-23"
cycle: null
---

# PAP-301: Harden the founder root of trust: hardware-key MFA on every external account, an offline recovery age key with escrow, a one-command revoke-all, and the break-glass runbook filed as a single Needs Justin checklist

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — security-sensitive title keyword: break-glass

**Goal**

Every trust boundary in the platform ends at Justin's accounts on GitHub, Linear, Hetzner, the DNS registrar or Cloudflare, Stripe, the Anthropic Console, Resend and Tailscale. If one of them is phished, every mitigation below it is moot. This issue writes the checklist Justin completes once (hardware keys, recovery codes offline, org-level policies), the escrow procedure for the recovery age key, the `revoke-all` command that cuts every agent credential, and the break-glass runbook for the day something goes wrong. It is the one security item that is genuinely a human task.

**Scope**

* In: `docs/security/root-of-trust.md` (account inventory with required settings), `docs/security/break-glass.md`, `ops/security/revoke-all.sh` (calls PAP-48 rotate, PAP-60 revoke, PAP-300 revoke, PAP-111 kill, orchestrator pause), escrow procedure for the offline age key and printed recovery codes, a Needs Justin decision card listing the human steps with checkboxes, verification script `pnpm security:accounts-check` where APIs allow (GitHub org 2FA requirement, Linear allowed auth methods, Stripe 2FA status).
* Out: the accounts themselves, SSO for tenants (PAP-230), user-facing MFA (PAP-220), rotation mechanics per secret class (PAP-219 runbook, PAP-300).

**Spec**

* Account inventory and required state: GitHub (two FIDO2 keys, org-wide 2FA requirement, no classic PATs, `imagine-os` org secrets restricted to selected repos, App private key stored only in sops); Linear (passkey or hardware key, Google SSO only if Google is hardware-key protected, API keys reviewed monthly, webhook secrets rotated by PAP-97 register script); Hetzner (2FA, project-scoped API tokens, Cloud firewall per PAP-25, console access alerts on); registrar and Cloudflare (2FA, registrar lock, DNSSEC where supported, Cloudflare API token scoped to the zone); Stripe (2FA, restricted keys only, live mode toggled by Justin per PAP-359); Anthropic Console (2FA, monthly spend limit as the outer wall named in PAP-111, separate workspace key for the orchestrator); Resend (2FA, domain-scoped API key); Tailscale (Google or GitHub login protected by hardware key, key expiry on, ACL restricting Postgres and Coolify to Justin and the orchestrator node).
* Recovery: second FIDO2 key stored off-site; printed recovery codes for every account plus the offline age private key (recipient of every sops file per PAP-25) sealed in an envelope with a tamper seal and its serial recorded in `docs/security/root-of-trust.md`; the same age key can decrypt the escrow bundle PAP-354 uploads to the second provider; test decrypt once during the first DR drill.
* Revoke-all: `ops/security/revoke-all.sh --reason "<text>"` runs in order: orchestrator `POST /admin/kill {scope: all, hard: true}` (PAP-111), `pnpm revoke --all` (PAP-300), `ops/forge/bots.ts rotate` (PAP-48), `pnpm agents:key revoke --all` (PAP-60), invalidate all Better Auth sessions for agent principals, disable Linear webhooks (`webhookUpdate enabled: false`), then prints what remains manual (rotate Linear personal key, GitHub App key, Anthropic key); idempotent, under 3 minutes, dry-run flag.
* Break-glass runbook: triggers (lost device, suspected phish, leaked key in a public repo, agent exfiltration alert from PAP-356), first 15 minutes checklist (revoke-all, rotate the affected root account from the second key, check GitHub and Linear audit logs, snapshot the VPS), who to notify (Stripe, Anthropic support contacts), evidence preservation, return-to-service steps and the post-mortem template shared with PAP-219.
* Decision card: one PAP-94 card `Complete founder account hardening` with the checklist; Justin replies `approve` when done and pastes the envelope serial; the orchestrator marks the control `SEC-ROOT-01` verified in PAP-219 `controls.yaml`.

**Interface contract**

* Provides: `docs/security/root-of-trust.md`, `docs/security/break-glass.md`, `ops/security/revoke-all.sh`, `pnpm security:accounts-check` report, control ids `SEC-ROOT-*`.
* Consumers: PAP-219 (controls and incident playbook link), PAP-354 (escrow key), PAP-356 (runbook links from alerts), PAP-48 (no bot creation until the GitHub org 2FA policy is on), PAP-111 (outer spend wall recorded).
* Requires: PAP-25 sops age layout and account list; Justin's time, roughly 90 minutes.

**Definition of done**

* Inventory covers every external account the plan names with required settings and current status columns.
* `pnpm security:accounts-check` verifies GitHub org 2FA enforcement, absence of classic PATs, Linear auth methods and Stripe restricted keys via their APIs; manual items listed with a date.
* `revoke-all.sh --dry-run` prints every step; a live run on staging completes under 3 minutes and a following agent push and Linear call fail.
* Needs Justin card approved with the envelope serial; `SEC-ROOT-01` verified.
* Changelog under "Security"; Linear comment with the check report.

**Test plan**

* Unit: script argument handling, ordering, idempotency on a second run.
* Integration: staging revoke-all with a live rehearsal session.
* Manual: Justin performs the checklist; the accounts check confirms what it can.
* No UI.

**Demo**

Run `pnpm security:accounts-check` and read the table; then `ops/security/revoke-all.sh --dry-run` listing the eight steps. One minute.

**Edge cases**

* Justin has one device only: the card recommends two keys; until the second arrives the printed codes are the fallback and the status column says so.
* Revoke-all during a legitimate release: PAP-254 certification pauses; the runbook says when to resume.
* An account has no API for verification (registrar): manual attestation with date in the inventory, re-attested quarterly by a Scout routine reminder.
* Anthropic key rotation mid-session: sessions fail fast; the orchestrator re-queues with the last footer (PAP-96).
* Escrow bundle decrypt test fails: treated as S0; a new key pair is generated and every sops file re-encrypted (PAP-25 `pnpm secrets:rekey`).

**Dependencies**

Blocked by PAP-25. Blocks PAP-48. Soft: PAP-111, PAP-60, PAP-219, PAP-300, PAP-354.

*Round 4 (2026-09-18): PAP-48 soft: this issue no longer blocks PAP-48 because the founder root-of-trust hardening (09-23) lands after the forge milestone (09-20); PAP-48 proceeds (create the bot accounts and deploy keys with the current admin credentials; PAP-301 rotates and re-parents them when it lands) and reconciles when this issue lands.*

**Agent**

Written by Sentinel (Security Auditor sub-agent); Forge (Ops Runner) writes the scripts; Justin completes the checklist.

**Size**

S
