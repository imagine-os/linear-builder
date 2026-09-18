---
identifier: "PAP-300"
title: "Build the credential broker: sessions hold no raw secrets; an egress proxy injects short-lived per-session tokens (GitHub App, Forgejo, Linear proxy, PaperOS agent keys, Anthropic) with usage logs and one-command revoke-all"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Orchestrator claims and ships issues"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-25", "PAP-48", "PAP-96", "PAP-521", "PAP-691"]
blocks: ["PAP-111", "PAP-280", "PAP-533"]
key: "security/credential-broker"
url: "https://linear.app/paperos/issue/PAP-300/build-the-credential-broker-sessions-hold-no-raw-secrets-an-egress"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:08.128Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-22"
cycle: null
---

# PAP-300: Build the credential broker: sessions hold no raw secrets; an egress proxy injects short-lived per-session tokens (GitHub App, Forgejo, Linear proxy, PaperOS agent keys, Anthropic) with usage logs and one-command revoke-all

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — security-sensitive title keyword: credential broker

**Goal**

A compromised or confused session must not be able to leak a credential it never had. The orchestrator mints or scopes a credential per session and per host, the sandbox egress proxy injects it into outbound requests, the session environment contains only placeholders, and every use is logged against the session. `pnpm revoke --all` invalidates everything in under a minute. This replaces the PAP-106 pattern of mounting secret values into the session environment.

**Scope**

* In: `packages/orchestrator/src/broker/` (minting, storage, rotation, revocation), the egress proxy container `ops/sandbox/egress/` (Dockerfile, per-character allowlist `ops/sandbox/egress/<character>.txt` generated from `roster.json`: Anthropic API, Linear, GitHub, Forgejo, npm registry plus the character's `access[]` connector hosts; every other host denied and logged as `egress-denied` in PAP-107 format; moved here from PAP-280 on 2026-09-17), proxy credential injection rules (`ops/sandbox/egress/credentials.yaml`), the Linear write proxy, session env placeholder contract, usage log, revoke-all CLI wired to the PAP-111 kill switch, `docs/security/credential-broker.md`.
* Out: the session container, worktree mount and resource limits (PAP-280, which attaches to this proxy as its only route), bot account creation (PAP-48), PaperOS API key plugin (PAP-60), sops layout (PAP-25).

**Spec**

* Credential classes and minting: GitHub App installation tokens per session (`POST /app/installations/{id}/access_tokens` with `repositories: [<repo>]` and permissions narrowed to the character's needs, 1 h, renewed by the proxy); Forgejo per-session tokens created via `POST /api/v1/users/{bot}/tokens` with `sudo` by `paperos-admin`, scopes from PAP-48, deleted at session end; PaperOS agent keys via PAP-60 `pnpm agents:key create --ttl 8h --issue PAP-n`; Linear through the write proxy below (the raw Linear key never leaves the orchestrator); Anthropic API key injected by the proxy only for `api.anthropic.com`, never in env; Stripe test restricted keys per character (Ledger only) injected for `api.stripe.com`; connector keys (Notion, Webflow, Drive) injected per host for the owning character only.
* Proxy injection: containers see `PAPEROS_PROXY=http://egress:3128` and placeholder variables (`GITHUB_TOKEN=broker:github`, `LINEAR_API_KEY=broker:linear`); the proxy matches `(sessionId from client cert or container label, host)` to a live credential, rewrites `Authorization`, strips any client-supplied credential header, and refuses hosts without a rule; TLS to upstream is verified; the proxy terminates TLS for allowlisted hosts with a per-sandbox CA installed in the image (mirrors the pattern this planning environment uses).
* Linear write proxy `POST /broker/linear/graphql`: parses the GraphQL document, allows queries freely, allows mutations only from the set `issueUpdate (stateId to In Progress|In Review|Needs Justin, assigneeId self, labelIds add), commentCreate, commentUpdate (own), attachmentCreate, issueRelationCreate` and only for the claimed issue or issues it blocks; denies `*Archive`, `*Delete`, `customView*`, `team*`, `workflowState*`, `webhook*`, `apiKey*`, anything touching PAP-1..PAP-12; logs `{ sessionId, operation, issue, decision }`.
* Storage: `orchestrator.credentials (id, session_id, class, host, expires_at, revoked_at, last_used_at, use_count)`, values encrypted at rest with the orchestrator age key, never logged.
* Revocation: `pnpm revoke --all | --session <id> | --character <name>` deletes Forgejo tokens, revokes PaperOS keys, drops proxy rules (GitHub installation tokens are dropped from the proxy and expire within the hour), and marks rows; PAP-111 `kill --all` calls `revoke --all`.
* Usage log: proxy emits `credential.used` events (host, method, path class, status) into PAP-107; anomalies (host or path never seen for that character) raise `credential.anomaly` for PAP-356.
* Rotation: root credentials (GitHub App private key, `paperos-admin` token, Linear key, Anthropic key) live only in sops (PAP-25) and the orchestrator process; PAP-219's rotation runbook gains a section per class with the `pnpm broker:rotate <class>` command.

**Interface contract**

* Provides: `mint(session, class): Credential`, `revoke(scope)`, `proxyRules(session): Rule[]`, `POST /broker/linear/graphql`, events `credential.minted|used|revoked|anomaly`, placeholder convention `broker:<class>`.
* Consumers: PAP-96 launcher (mints before launch, revokes after), PAP-280 (attaches session containers to the proxy network; no other route), PAP-105 `linear-update` skill (uses the proxy endpoint), PAP-81 reviewers (read-only GitHub tokens), PAP-111 (`kill` implies `revoke`), PAP-219 controls `SEC-SECRET-*`.
* Requires: PAP-48 bot accounts and GitHub App, PAP-25 sops and Docker, PAP-60 key CLI (interim: character key from sops for the platform API).

**Definition of done**

* `env` inside a running session shows only `broker:*` placeholders; grep for `ghp_|lin_api_|sk-ant-|sk_test_` returns nothing (CI assertion on a recorded session).
* A session pushes a branch, comments on Linear and opens a PR using injected credentials (recording).
* Linear proxy blocks `issueArchive` and a state change to `Done`; allows `commentCreate` on the claimed issue (integration test).
* `pnpm revoke --all` completes under 60 s; a subsequent push and Linear call from a live session fail with 401 (recording with timestamps).
* Docs; changelog under "Security"; Linear comment with proof links.

**Test plan**

* Unit: GraphQL mutation classifier on 40 documents, rule matcher, expiry arithmetic.
* Integration: proxy with a mock upstream verifying header rewrite and stripping; Forgejo token lifecycle against the staging forge.
* e2e: staging session through sandbox and broker; revoke-all drill.
* No UI.

**Demo**

Start a session, run `env | grep -i token` inside it (placeholders only), watch `credential.used` events stream as it pushes, then run `pnpm revoke --all` and see the next push fail. Two minutes.

**Edge cases**

* Session outlives a 1 h GitHub token: the proxy renews transparently; renewal failure surfaces as a 401 with `X-Broker-Reason`.
* Tool that pins its own TLS (some CLIs): documented list; those tools receive a real short-lived token via a one-shot file that the hook deletes after use, logged as `credential.direct`.
* Orchestrator restart: credentials table restores proxy rules; expired rows purged.
* Linear proxy rejects a mutation a skill needs: the skill posts the operation name; Sentinel extends the allowlist by PR, never ad hoc.
* Sandbox unavailable (degraded mode): broker still mints short-lived tokens into env with 2 h TTL and logs `degraded: true`; revoke-all still works.

**Dependencies**

Blocked by PAP-96 (launcher), PAP-48 (bots and App), PAP-25 (sops, host). Blocks PAP-111 (kill implies revoke) and PAP-280 (container, worktree and limits; needs this proxy as its only route). Soft: PAP-60, PAP-105.

**Agent**

Built by Atlas (Dispatcher sub-agent) with Forge (Ops Runner) for the proxy; reviewed by Sentinel (Security Auditor).

**Size**

M
