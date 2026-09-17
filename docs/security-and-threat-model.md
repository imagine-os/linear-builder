# PaperOS Security & Threat Model

Round 2, 2026-09-17. What we protect, where trust changes hands, what can go wrong at each boundary, and which issue owns each control. PAP-219 turns this into the executable version (`controls.yaml`, `securityHeaders()`, runbooks); Sentinel audits against it. Eleven mitigations had no owner; their full specs are in the companion document [Round 2 pending issues: security (11)](https://linear.app/paperos/document/round-2-pending-issues-security-11-27d8ebfcd8d0) and are cited as `[security/<key>]` until Linear's issue cap allows creation.

## 1. Assets

| Asset | Where | Why it matters |
| -- | -- | -- |
| Tenant data (tables, docs, files, CRM, ledger) | Postgres with RLS (PAP-34), MinIO (PAP-37), Yjs (PAP-140) | Customer confidentiality; the ledger is legal record (PAP-179) |
| Identities and sessions | Better Auth (PAP-57), agent keys (PAP-60) | Every control assumes the principal is real |
| Root credentials (age keys, GitHub App, Linear, Anthropic, Stripe, Coolify) | sops in `paperos-infra` (PAP-25), orchestrator | Total-compromise point (round-1 critique) |
| Code and CI on two forges | Forgejo (PAP-45), GitHub mirror (PAP-47), runners (PAP-50) | Supply chain; branch protection is the last human-free gate (PAP-46) |
| Linear workspace | SaaS | The queue agents act on; a poisoned issue is an instruction |
| Audit and prompt logs | PAP-38, PAP-129 | Proof of who did what when most contributors are agents |
| Claude credit (about $10K) | Anthropic Console, PAP-98 | A hijacked session is a financial attack (PAP-111) |
| Justin's external accounts | GitHub, Linear, Hetzner, registrar, Stripe, Anthropic, Resend, Tailscale | Root of trust for everything above |

## 2. Trust boundaries

| \# | Boundary | Entry points | Authentication | Owning issues |
| -- | -- | -- | -- | -- |
| B1 | Browser and PWA | oRPC over HTTPS, shape proxy, Hocuspocus WSS | Better Auth cookie (`SameSite=Lax`, `Secure`, `HttpOnly`) | PAP-57, PAP-18, PAP-219 |
| B2 | Tauri shell | `tauri://localhost`, IPC, deep links, updater | Bearer token in OS keychain (PAP-17), capabilities (PAP-255), signed updates (PAP-257) | PAP-19, PAP-225, PAP-260 |
| B3 | API (`apps/api`, Hono and oRPC) | `/api/v1/*`, `/api/auth/*`, `/api/sync/shape`, webhooks | Session or API key to `actor`; `withTenant` sets RLS context | PAP-35, PAP-267, PAP-59, PAP-229 |
| B4 | Postgres with RLS | `paperos_app` (NOBYPASSRLS), `paperos_owner`, `paperos_readonly`, `electric` | Role plus `app.tenant_id` session context; fail closed on missing context | PAP-30, PAP-34, PAP-228 |
| B5 | Yjs server (Hocuspocus) | `wss://collab.` rooms `doc:<tenant>:<type>:<id>` | `onAuthenticate` verifies session or `pos_agent_` key, calls `can()` | PAP-140, PAP-141 |
| B6 | Orchestrator VPS | 80/443 public; 22 and 8000 tailnet only; webhooks | Tailscale, Hetzner firewall, HMAC signatures | PAP-25, PAP-96, PAP-97 |
| B7 | Forgejo and GitHub | Git over SSH 2222 and HTTPS, Actions, API, mirror | Bot tokens per character (PAP-48), rulesets (PAP-46), OIDC from Better Auth (PAP-226) | PAP-45, PAP-273, PAP-47 |
| B8 | Stripe and payroll provider | Checkout, Portal, Connect onboarding, webhooks | Restricted keys, `constructEvent` signatures, provider-hosted flows | PAP-177, PAP-181, PAP-184 |
| B9 | Agent sessions | Claude Code in worktrees reading issues, comments, PRs, web | Bundles (PAP-106), sandbox (\[agents/runtime-sandbox\]), broker (\[security/credential-broker\]) | PAP-104, PAP-107, PAP-111 |

## 3. STRIDE by boundary

Threat, then control and owner; bracketed keys are pending.

**B1 Browser.** Spoofing: session theft via XSS; nonce CSP, `HttpOnly` cookies, passkeys first (PAP-219, PAP-57). Tampering: cross-origin mutations; origin check plus `SameSite=Lax` (PAP-219), tested by \[security/dast\]. Repudiation: `request_id` on every mutation into `audit_event` (PAP-38). Disclosure: secrets in the bundle; Vite guard on non-`VITE_` vars (PAP-17); OTel drops PII (PAP-40). Denial: hostile tabs; 600/min per actor (PAP-35), Postgres-backed limiter pending in data-layer. Elevation: `useCan` only hides; the server re-checks (PAP-229, PAP-64).

**B2 Tauri.** Spoofing: rogue `paperos://` handler; single-use PKCE-bound deep-link tokens (PAP-225). Tampering: malicious update; minisign updater plus cosign provenance (PAP-257, \[security/supply-chain\]). Disclosure: tokens on disk; OS keychain only (PAP-17, PAP-260). Elevation: IPC abuse; capabilities scoped to the main window, Semgrep rule on allowlist widening (PAP-255, PAP-80).

**B3 API.** Spoofing: forged webhooks; HMAC and 60 s window for Linear, forges, Stripe (PAP-97, PAP-177), replay tests in \[security/dast\]. Tampering: mass assignment; Zod on every procedure (PAP-35, PAP-268). Repudiation: `app.reason` mandatory for agents (PAP-38). Disclosure: IDOR across tenants; `withTenant` plus RLS, HTTP matrix (PAP-64), IDOR suite (\[security/dast\]); connector secrets in clear text; gap \[security/field-encryption\]. Denial: unbounded lists; `limit <= 100`, batch caps, k6 budgets (PAP-35, PAP-242). Elevation: procedure without `authorize`; Semgrep S0 (PAP-80), spec-conformance reviewer (PAP-244).

**B4 Postgres.** Spoofing: wrong role; PgBouncer per-role credentials, TLS, tailnet only (PAP-30). Tampering: audit rows edited; append-only triggers, per-tenant hash chain, `pnpm audit:verify` (PAP-38); ledger immutability (PAP-179). Repudiation: silent `app.bypass`; every bypass is an audit and security event (\[security/security-telemetry\]). Disclosure: agent query leaks a tenant; `FORCE ROW LEVEL SECURITY`, fail-closed context, cross-tenant harness (PAP-34); Electric shapes server-filtered (PAP-270). Denial: stuck replication slot; lag alert (PAP-40). Elevation: `paperos_owner` only in the migrator connection, migrations as a pre-deploy step (PAP-26).

**B5 Yjs.** Spoofing: stolen token joins a room; session or agent key verified on connect (PAP-140). Tampering: `connection.readOnly` from `can('document.write')`. Repudiation: awareness carries `principalId`; agents visually distinct (PAP-141, PAP-146). Disclosure: presence leaks; `presence.view` policy (PAP-141). Denial: 20 MB cap, throttle, load test (PAP-140, PAP-147). Elevation: unknown entity types rejected `4403`.

**B6 Orchestrator VPS.** Spoofing: fake webhook triggers a claim; signature plus `webhookId` dedupe (PAP-97). Tampering: host drift; everything in `paperos-infra`, idempotent bootstrap (PAP-25), pinned digests (\[security/supply-chain\]). Repudiation: `orchestrator.events` and session footers (PAP-92, PAP-96). Disclosure: root credentials; sops with two recipients, off-site escrow (\[security/platform-dr\], \[security/founder-break-glass\]). Denial: single 8 GB host; 6 GB service budget (PAP-214), RTO 4 h drill (\[security/platform-dr\]). Elevation: Docker or Coolify abuse from a session; no infra credentials in sessions, egress allowlist (\[agents/runtime-sandbox\], \[security/credential-broker\]).

**B7 Forges.** Spoofing: commits attributed to a character; SSH signing keys with `allowed_signers` (PAP-48). Tampering: force-push on `main`; rulesets on both forges (PAP-46), deny list blocks earlier (\[security/agent-deny-list\]). Repudiation: squash merges by the Merger only, mandatory trailers (PAP-46). Disclosure: secrets in git; gitleaks on diff and history (PAP-80). Denial: GitHub outage; Forgejo primary, runners, DR drill (PAP-50, PAP-53, PAP-274). Elevation: malicious dependency or action; SBOM and OSV (PAP-80), release age, digest pinning, provenance at deploy (\[security/supply-chain\]).

**B8 Stripe and payroll.** Spoofing: `constructEvent`, `stripe_event` idempotency (PAP-177). Tampering: agent triggers live refunds; test keys until Justin approves, deny list on `sk_live_` (\[security/agent-deny-list\], \[security/pci-posture\]). Repudiation: every billing event is a `fin_transaction`; ledger hash chain (PAP-177, PAP-179). Disclosure: card or bank data on our servers; SAQ-A, PAN Semgrep rules, provider-hosted onboarding (\[security/pci-posture\], PAP-184). Denial: webhook backlog; Stripe retries, alert after three failures (PAP-177). Elevation: over-scoped keys; restricted keys per service (\[security/pci-posture\]).

**B9 Agent sessions.** Spoofing: non-Justin comment says `approve`; actor id verification, trust tiers (\[security/prompt-injection\], PAP-94). Tampering: session edits its allowlist, hooks or memory; deny rules on `.claude/**`, memory review gate (PAP-106, \[security/agent-deny-list\], PAP-109). Repudiation: every prompt, tool call and denial logged with redaction (PAP-107, PAP-129). Disclosure: exfiltration via `env` or `curl`; `broker:*` placeholders, proxy injection, canaries (\[security/credential-broker\], \[security/prompt-injection\]). Denial: runaway spend; caps, kill switch, Console limit as outer wall (PAP-111). Elevation: injected PR drives a destructive action; untrusted wrapping, read-only reviewers, destructive MCP tools removed, deny list, sandbox (\[security/prompt-injection\], \[security/agent-deny-list\], \[agents/runtime-sandbox\]).

## 4. Destructive-action deny list for agents

One file, `ops/security/agent-deny.yaml`, enforced three times: the PreToolUse hook (PAP-106, extended by \[security/agent-deny-list\]), removal of `destructive`-scoped MCP tools from every character except Atlas (PAP-210), and a server-side backstop required for every S0 rule.

* Git: force-push, branch or tag deletion, pushes to `main` or `release/*`. Backstop: rulesets (PAP-46).
* Filesystem: `rm -rf` outside the worktree; writes to `ops/secrets/**`, `.claude/**`, `*.age`, `.env*`. Backstop: read-only sandbox root (\[agents/runtime-sandbox\]).
* Database: `DROP`, `TRUNCATE`, `DELETE` or `UPDATE` without `WHERE`, disabling RLS, `ALTER ROLE`, `SET app.bypass`, any production host. Backstop: `paperos_app` role, tailnet-only Postgres (PAP-30, PAP-34).
* Linear: archive or delete of anything, state changes to `Done` or `Canceled`, PAP-1..PAP-12, views. Backstop: Linear write proxy allowlist (\[security/credential-broker\]).
* Forges: repo deletion, protection, secret, webhook or mirror edits. Backstop: bot token scopes (PAP-48).
* Stripe and payroll: any `sk_live_` use, refunds, payouts, transfers, payroll submit. Backstop: restricted test keys (\[security/pci-posture\]).
* Infrastructure: production deploys, volume pruning, `hcloud server delete`, DNS and firewall edits, `sops --decrypt` outside `secretsFor`. Backstop: credentials absent from sessions.
* Secrets: `env`, `printenv`, `/proc/*/environ`, `curl --data` to non-allowlisted hosts, base64 of secret paths. Backstop: egress allowlist, canaries.
* Communications: live email, SMS or social publishing outside sandbox or an approved queue item (PAP-190, PAP-191).
* Agents: `kill --all`, editing `roster.json` or `ops/security/**` from a non-Sentinel character.

A blocked but needed action goes through `/request-approval`, which files a PAP-94 decision card and ends the session. Three S0 hits in one session trigger a kill (PAP-111).

## 5. Secrets handling

* Storage: `ops/secrets/*.enc.yaml` with sops and age, two recipients (Justin's offline key, the orchestrator host key), mirrored into Coolify secrets (PAP-25); gitleaks on every diff and nightly over history (PAP-80).
* Per-agent scoped tokens: Forgejo bot per lead character, one GitHub App with per-session installation tokens, SSH signing keys (PAP-48); PaperOS agent keys with scopes, 8 h session TTL, minted only by the orchestrator (PAP-60); connector keys per owning character (PAP-106).
* Broker and proxy: sessions hold `broker:*` placeholders; the egress proxy injects credentials per host and logs use; the Linear key never leaves the orchestrator; `pnpm revoke --all` in under a minute (\[security/credential-broker\]).
* Stored secrets: AES-256-GCM envelope encryption, per-tenant data keys under a sops master key, zero-downtime rotation, CI scanner for plaintext secret columns (\[security/field-encryption\]).
* Rotation: runbook per class with blast radius and proof of death (PAP-219); bots rotate with a ten-minute overlap (PAP-48); suppressions expire (PAP-80).
* Logging: prompt logs redacted at hook and ingest with the character's own secret values in the pattern set (PAP-107, PAP-129); OTel drops payloads and PII (PAP-40).
* Root of trust: hardware-key MFA everywhere, offline recovery key in sealed escrow, break-glass runbook (\[security/founder-break-glass\]).

## 6. Prompt-injection defences

Only the orchestrator's rendered prompt (T0) and comments whose Linear `user.id` is Justin's (T1) instruct an agent. Issue bodies and bot comments are T2; fork PRs, imported documents, web pages and third-party responses are T3; scanner hits are T4. T2 and below is wrapped in `<untrusted source= tier=>` blocks with a fixed preamble and never enters the instruction section; the scanner strips overrides, hidden HTML, zero-width and bidi text, base64 blobs and tool-call lookalikes and posts what it removed. The PAP-94 grammar and `KILL` honour only T1. Ready for Claude issues get a spec hash; a non-Justin edit before claim bounces them. Gate 2 reviewers (PAP-81, PAP-243) run read-only, without MCP servers on fork PRs, emitting schema-validated JSON. Memory updates with imperatives or links wait for Quill (PAP-109). Canaries in fixtures and secret maps alert on any outbound appearance. A 60-attack suite runs nightly through PAP-110 with a 100 percent S0 pass requirement (\[security/prompt-injection\]).

## 7. Backup and disaster recovery

| Component | Mechanism | RPO | RTO | Drill | Owner |
| -- | -- | -- | -- | -- | -- |
| Postgres (prod, staging) | pgBackRest WAL archiving, nightly full, hourly incremental, 14 days | 1 h | 30 min | Weekly automated restore to a scratch container | PAP-30 |
| Forgejo, repos, CI | `forgejo dump` plus `pg_dump` nightly via restic, 30 daily / 8 weekly | 24 h | 2 h to green PR with GitHub blocked | Monthly | PAP-45, PAP-274, PAP-53 |
| MinIO tenant files | Hourly `mc mirror` into restic, 24 hourly / 14 daily / 8 weekly | 1 h | within platform RTO | Monthly platform drill | \[security/platform-dr\] |
| Yjs documents | In Postgres (`yjs_documents`, `yjs_updates`), covered by PITR; compaction on first load | 1 h | within platform RTO | Monthly platform drill | PAP-140, \[security/platform-dr\] |
| Orchestrator state | Hourly `pg_dump` of schema `orchestrator`; `interrupted` sessions re-queue | 1 h | within platform RTO | Monthly platform drill | PAP-96, \[security/platform-dr\] |
| Coolify and Caddy definitions | Daily export to `ops/coolify/*.json` in git | 24 h | rebuilt by bootstrap | Monthly | PAP-25, PAP-26 |
| sops age keys, restic passwords | Age-encrypted escrow in a second provider plus sealed printed copy | n/a | first step of any drill | Decrypt tested in the first drill | \[security/platform-dr\], \[security/founder-break-glass\] |
| Whole platform on a fresh host | `ops/dr/platform-drill.sh` | 1 h | 4 h | Monthly, first run before the 2026-09-30 RC | \[security/platform-dr\] |

Backup age and `restic check` alert at 2 h (hourly jobs) and 26 h (daily) (\[security/platform-dr\], PAP-40). A release candidate requires a green drill within 30 days (PAP-252, PAP-254).

## 8. Compliance posture

* PCI: SAQ-A only. Card data enters only Stripe Checkout, Elements and the Customer Portal; payroll bank details go to provider-hosted links; Semgrep blocks PAN-shaped fields and `sk_live_` literals; restricted keys per service; live mode is a hard-block Needs Justin decision; quarterly SAQ-A checklist (\[security/pci-posture\], PAP-177, PAP-184).
* GDPR: tenant export in open formats, re-importable (PAP-205); per-person export and erasure with pseudonyms kept in ledgers and audit chains, consent records, legal pages (PAP-221); schema PII classification driving redaction, telemetry filters and the DSAR registry, retention jobs, legal hold, export-first tenant purge after 30 days (\[security/retention-pii\]); impersonation visible to the customer (PAP-61); session control and MFA fallback (PAP-220).
* Audit log: append-only `audit_event` with actor kind, diff, reason, request and session ids, per-tenant hash chain, 24-month retention then Parquet, CSV export (PAP-38); full prompt and tool-call log per session (PAP-107, PAP-129); security event catalogue with weekly digest (\[security/security-telemetry\]).
* Testing: SAST, secret, dependency and container scans per PR (PAP-80); security reviewer agent (PAP-245); nightly ZAP and control-tagged regression suite gating release candidates (\[security/dast\]); permission matrix at policy, HTTP and UI level (PAP-64); cross-tenant RLS harness (PAP-34).

## 9. Gap register

| Key | Project | Phase | Prio | Blocked by |
| -- | -- | -- | -- | -- |
| security/agent-deny-list | agents | P0 | 1 | PAP-106, PAP-210 |
| security/prompt-injection | agents | P0 | 1 | PAP-92, PAP-97 |
| security/credential-broker | pm-linear | P0 | 1 | PAP-96, PAP-48, PAP-25 |
| security/founder-break-glass | identity | P0 | 1 | PAP-25 |
| security/field-encryption | data-layer | P1 | 1 | PAP-32, PAP-17 |
| security/platform-dr | data-layer | P1 | 1 | PAP-30, PAP-37, PAP-140, PAP-96 |
| security/retention-pii | data-layer | P1 | 2 | PAP-33, PAP-43, PAP-38 |
| security/security-telemetry | quality | P1 | 2 | PAP-40, PAP-97, PAP-38 |
| security/dast | quality | P1 | 2 | PAP-80, PAP-240, PAP-26 |
| security/supply-chain | forge | P1 | 2 | PAP-80, PAP-52, PAP-26 |
| security/pci-posture | business-core | P1 | 2 | PAP-177 |

Owned elsewhere but relied on: `[agents/runtime-sandbox]` (agents pending document; container, worktree and limits only, since 2026-09-17 the egress proxy and allowlist live in `[security/credential-broker]`) and Postgres-backed rate limiting (`[contracts/idempotency-rate-limits]`, contracts pending document). Linear refused `issueCreate` with `USAGE_LIMIT_EXCEEDED` on 2026-09-17; `round2/agent6/create_issues.py` creates all eleven idempotently, with labels, milestones and relations, once the plan is upgraded.

## 10. Cadence

PAP-219 is revised whenever a boundary changes. Sentinel's weekly digest (\[security/security-telemetry\]) reports open S0 and S1 findings, rotation status, backup age and the last drill. The monthly platform drill and the quarterly SAQ-A checklist are the only recurring human touchpoints, each a single Needs Justin item under PAP-94.
