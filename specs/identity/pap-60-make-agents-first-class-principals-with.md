---
identifier: "PAP-60"
title: "Make agents first-class principals with scoped API keys, rate limits and visible attribution"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: ["PAP-587", "PAP-586"]
blockedBy: ["PAP-59", "PAP-219", "PAP-229", "PAP-456"]
blocks: ["PAP-146", "PAP-834", "PAP-913"]
key: "identity/agent-principals"
url: "https://linear.app/paperos/issue/PAP-60/make-agents-first-class-principals-with-scoped-api-keys-rate-limits"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:37.757Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-30"
cycle: null
---

# PAP-60: Make agents first-class principals with scoped API keys, rate limits and visible attribution

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Make Claude agents first-class principals: one agent user per character, scoped API keys with rate limits and quotas minted per session by the orchestrator, and visible attribution on every mutation, comment and presence indicator, all going through the same `can()` as humans.

**Scope**

* In: agent principal records synced from the roster, Better Auth `apiKey()` plugin configuration, scope intersection `withScopes()`, rate limits and quotas, attribution fields and `ActorBadge`, audit integration, `pnpm agents:key` CLI for the orchestrator, docs.
* Out: character definitions (PAP-103, PAP-104), MCP allowlists (PAP-106), presence rendering (PAP-146), customer developer keys (PAP-222).

**Spec**

* Data: `users` rows with `principalType = 'agent'` and `attributes: { character, subAgent?, lead }`; `pnpm agents:sync` reads `.claude/agents/*.md` frontmatter (PAP-104) and upserts one user per lead character, member of each tenant with role `staff` and attribute `agent: true` so the `agent` audience matches.
* Keys: `apiKey({ defaultPrefix: 'pos_agent_', rateLimit: { enabled: true, timeWindow: 60_000, maxRequests: 600 } })`; metadata `{ character, issue?, session?, scopes }`; expiry 7 days for session keys, 90 days for character keys; hashed at rest; only a character key with `agent.key.create` may mint session keys.
* Scopes: `withScopes(actor, scopes)` in `packages/permissions` intersects policies with patterns (`repo:write`, `linear:comment`, `specs:write`, `prod:read-only`) mapped from plan access lists by `packages/agents/src/scope-map.ts`; a key whose scopes exclude the action is denied even when the role allows.
* Attribution: every oRPC mutation records `actorId`, `actorType`, `character`, `onBehalfOf?`, `sessionId`, `issueKey` to PAP-38; responses carry `X-PaperOS-Actor: agent:forge`; `ActorBadge` in `packages/ui` renders the agent glyph and character colour with tooltip "Forge (agent) on PAP-123".
* Quotas: per-character daily quota in `ops/agents/quotas.yml`; exceeding returns 429 with `Retry-After` and emits `agent.quota.exceeded` (PAP-111 consumes).
* CLI: `pnpm agents:key create --character forge --issue PAP-123 --ttl 8h --scopes repo:write,linear:comment | list | revoke <id> | rotate --character forge`, JSON output.

*Round 4 amendment (2026-09-18):*
Rate limiting: replace the plugin's in-memory `rateLimit` with `rateLimit('apiKey')` from PAP-558 so limits survive restarts and are shared by both API replicas; the "state lost on restart" edge case is then void. Work is split into PAP-586 and PAP-587.

**Interface contract**

* Provides: `withScopes()`, `ScopePattern` type and `scope-map.ts`; `ActorBadge`; `AgentPrincipalAttributes` type; CLI JSON shapes; events `agent.quota.exceeded`, `agent.key.created`, `agent.key.revoked`; header `X-PaperOS-Actor`.
* Requires: PAP-59 `can()`, PAP-57 server for the plugin, PAP-104 roster frontmatter, PAP-38 audit sink, PAP-219 key-handling controls.
* Consumers: PAP-96 orchestrator (mints keys), PAP-111 cost controls, PAP-146 presence, PAP-107 prompt log (session id), PAP-222 (reuses `withScopes`).
* Tables: `apikey` (plugin), `agent_quota_usage`.

**Definition of done**

* `pnpm agents:sync` creates nine agent users idempotently; second run makes no changes (test).
* Session key with `linear:comment` only: 403 on `invoice.update`, 200 on allowed calls (Vitest integration).
* 601st request in a minute returns 429 with `Retry-After`; daily quota exceeded emits the event.
* Audit rows for agent mutations carry character, session and issue (test against PAP-38 or its mock).
* Keys never logged (grep test during creation); Security Auditor confirms hashing and expiry.
* `ActorBadge` stories (human, agent, agent on behalf of) at 375 and 1280 light and dark; axe clean; docs `docs/platform/agent-principals.md` with the scope table and minting sequence diagram; changelog under "Identity".

**Test plan**

* Unit: scope-map coverage for all nine characters, scope intersection cases, quota arithmetic across midnight UTC.
* Integration: mint via character key, use, expire with faked clock, revoke on issue Done (webhook stub).
* E2E: an agent comment in the example app shows the badge and tooltip.
* Visual: badge stories.

**Demo**

Run `pnpm agents:key create --character forge --issue PAP-123 --ttl 1h --scopes linear:comment`, call a read procedure with it (200), then `invoice.update` (403 with explain), then `pnpm agents:key list` showing last-used. Under two minutes.

**Edge cases**

* Character removed from roster: `agents:sync --prune` deactivates and revokes; history stays.
* Key used after its issue is Done: orchestrator revokes on state change; server soft-checks the Linear cache and logs.
* Parallel sessions for one character: distinct session keys; audit distinguishes.
* Rate-limit state lost on restart: accepted, documented with a Redis option later.

**Dependencies**

PAP-59, PAP-219 (hard). Soft: PAP-104, PAP-38, PAP-96, PAP-111, PAP-146.

**Agent**

Forge leads; Atlas's Dispatcher validates minting from the orchestrator side. Reviewed by Sentinel (Security Auditor, Code Reviewer); Iris reviews `ActorBadge`.

**Size**

M.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/data-layer/rate-limits` = PAP-558, `r4/identity/agent-attribution-quotas` = PAP-587, `r4/identity/agent-keys` = PAP-586.
