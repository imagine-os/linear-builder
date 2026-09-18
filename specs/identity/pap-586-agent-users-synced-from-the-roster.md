---
identifier: "PAP-586"
title: "Agent users synced from the roster, Better Auth `apiKey()` with the `pos_agent_` prefix and metadata, `withScopes()` intersection with the scope map and the `pnpm agents:key` CLI for the orchestrator"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: "PAP-60"
children: []
blockedBy: ["PAP-59", "PAP-219", "PAP-223", "PAP-229", "PAP-456"]
blocks: ["PAP-146", "PAP-587", "PAP-594", "PAP-610"]
key: "r4/identity/agent-keys"
url: "https://linear.app/paperos/issue/PAP-586/agent-users-synced-from-the-roster-better-auth-apikey-with-the-pos"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:12.117Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-586: Agent users synced from the roster, Better Auth `apiKey()` with the `pos_agent_` prefix and metadata, `withScopes()` intersection with the scope map and the `pnpm agents:key` CLI for the orchestrator

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

First half of PAP-60 and the part the orchestrator (PAP-96) blocks on: agents exist as principals and hold keys that can do only what their character and issue allow. One agent user per lead character, session keys minted per issue with an expiry, and a scope intersection that denies an action even when the role would allow it.

**Scope**

In: `pnpm agents:sync` reading `.claude/agents/*.md` frontmatter (PAP-104; fixture roster until it lands) and upserting `users` rows with `principalType = 'agent'`, `attributes: { character, subAgent?, lead }`, membership `staff` with `agent: true` in every tenant; `apiKey({ defaultPrefix: 'pos_agent_' })` plugin config with metadata `{ character, issue?, session?, scopes }`, expiry 7 days for session keys and 90 for character keys, hashed at rest; `withScopes(actor, scopes)` in `packages/permissions` and `packages/agents/src/scope-map.ts` mapping plan access lists (`repo:write`, `linear:comment`, `specs:write`, `prod:read-only`) to policy patterns; CLI `pnpm agents:key create|list|revoke|rotate` with JSON output; docs `docs/platform/agent-principals.md` scope table and minting sequence diagram.

Out: Attribution header, audit fields, `ActorBadge` and quotas (sibling PAP-587), character definitions (PAP-103, PAP-104), MCP allowlists (PAP-106), customer API keys (PAP-222), delegation semantics (PAP-594).

**Spec**

* Only a character key holding `agent.key.create` may mint session keys; session keys inherit at most the character's scopes; `rotate --character` overlaps old and new for ten minutes (PAP-48 pattern).
* `withScopes` intersects the policy set from `can()` with the scope patterns: a key lacking `specs:write` is denied `page_spec.update` even for a `staff` member; denial explains with the missing scope.
* Rate limiting per key uses `rateLimit('apiKey')` from PAP-558 (soft: plugin limiter until it lands); the per-key default is 600/min from key metadata.
* `withTenant` (PAP-578) resolves the tenant from key metadata for tenant-scoped keys and refuses a differing header.
* Keys never appear in logs (grep test during creation); revocation on issue `Done` is called by the orchestrator webhook handler (PAP-97) through `agents:key revoke --issue`.
* `agents:sync --prune` deactivates and revokes characters removed from the roster; history stays.

**Interface contract**

Provides: `withScopes()`, `ScopePattern`, `scope-map.ts`, `AgentPrincipalAttributes`, CLI JSON shapes, events `agent.key.created|revoked`, `verifyApiKey(key)` for non-HTTP consumers (PAP-140, PAP-270).

Consumes: `can()` and adapter (PAP-227, PAP-229), Better Auth server (PAP-223), roster frontmatter (PAP-104, soft), tenancy middleware (PAP-578), rate limits (PAP-558, soft), key-handling controls (PAP-219). Consumed by PAP-96 (mints), PAP-111, PAP-146, PAP-107, PAP-140, PAP-222 (reuses `withScopes`), the sibling.

**Definition of done**

* `pnpm agents:sync` creates nine agent users idempotently; second run makes no changes (test).
* Session key with `linear:comment` only: 403 with the missing scope on `invoice.update`, 200 on allowed calls (Vitest integration through `callAs` and a real key).
* Mint via character key, use, expire with a faked clock, revoke on issue Done (webhook stub); Security Auditor confirms hashing and expiry; docs; changelog under Identity.

**Test plan**

* Unit: scope-map coverage for all nine characters, intersection cases including wildcard scopes, expiry arithmetic, CLI argument parsing.
* E2E: orchestrator dry run (PAP-96 stub) mints a key for `PAP-123`, an agent call carries it and lands in `audit_event` with the character (sibling asserts fields).

**Demo**

Run `pnpm agents:key create --character forge --issue PAP-123 --ttl 1h --scopes linear:comment`, call a read procedure with it (200), then `invoice.update` (403 with explain), then `agents:key list`. Under two minutes.

**Edge cases**

* Parallel sessions for one character: distinct session keys; audit distinguishes by `sessionId`.
* Key used after its issue is Done but before revocation lands: server soft-checks the Linear cache and logs a warning.
* Roster frontmatter invalid: sync refuses with the file and line; existing users untouched.
* Character renamed: new user; old one pruned with history kept.

**Dependencies**

Blocked by PAP-229 and PAP-223 (hard). Soft: PAP-104, PAP-219, PAP-578, PAP-558, PAP-97. Blocks PAP-146 and the sibling.

**Agent**

Builder: Forge (Platform Engineer); Atlas's Dispatcher validates minting. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/data-layer/rate-limits` = PAP-558, `r4/identity/agent-attribution-quotas` = PAP-587, `r4/identity/delegated-authority` = PAP-594, `r4/identity/tenancy-core` = PAP-578.
