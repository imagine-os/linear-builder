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
children: []
blockedBy: ["PAP-219", "PAP-229", "PAP-59"]
blocks: ["PAP-146"]
key: "identity/agent-principals"
url: "https://linear.app/paperos/issue/PAP-60/make-agents-first-class-principals-with-scoped-api-keys-rate-limits"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-60: Make agents first-class principals with scoped API keys, rate limits and visible attribution

**Goal**

Make Claude agents first-class principals: each character gets scoped API keys, per-key rate limits and quotas, and everything an agent does is attributed visibly in audit logs, presence and UI, with the same `can()` checks as humans. This is what keeps the audit trail honest when most contributors are agents.

**Scope**

- In: agent principal records, API key issuance and rotation via Better Auth's API key plugin, scope model derived from character access lists, rate limiting, attribution headers and UI badge, audit integration, a CLI for the orchestrator, and docs.
- Out: defining characters (agents/character-schema, agents/roster-v1), MCP tool allowlists (agents/tool-scopes), presence rendering (realtime/agent-presence consumes the attribution).

**Spec**

In `imagine-os/paperos-template`:

- Data: `users` rows with `principalType = 'agent'` and `attributes: { character: 'forge', subAgent?: 'schema-wright', lead: 'atlas' }`; one agent user per lead character, created by `pnpm agents:sync` reading `.claude/agents/*.md` frontmatter from agents/roster-v1 (name, role, reportsTo, access). Agents are members of tenants with role `staff` plus attribute `agent: true`; the audience model's `agent` audience matches them.
- Keys: Better Auth `apiKey()` plugin with `defaultPrefix: 'pos_agent_'`, `rateLimit: { enabled: true, timeWindow: 60_000, maxRequests: per-scope default 600 }`, metadata `{ character, issue?: 'PAP-123', session?: id, scopes: string[] }`, expiry default 7 days for session-scoped keys and 90 days for character keys. Keys are hashed at rest by the plugin; only the orchestrator (pm-linear/orchestrator) mints session keys using a character key with `agent.key.create` permission.
- Scopes: `packages/permissions` gains `withScopes(actor, scopes)` that intersects the actor's policies with scope patterns (for example `repo:write`, `linear:comment`, `specs:write`, `prod:read-only`) mapped from the plan.json access lists by `packages/agents/src/scope-map.ts`. Requests using a key whose scopes exclude the action are denied even if the agent's role would allow it.
- Attribution: every mutation through oRPC records `actorId`, `actorType`, `character`, `onBehalfOf?`, `sessionId`, `issueKey` into data-layer/audit-log; responses carry `X-PaperOS-Actor: agent:forge` for debugging; `packages/ui` `ActorBadge` renders an agent glyph, character colour from agents/character-schema and a tooltip "Forge (agent) on PAP-123". Comments, records and presence show the badge wherever a human avatar would appear.
- Rate limits and quotas: per key (plugin), plus per character daily request quota configurable in `ops/agents/quotas.yml`; exceeding returns 429 with `Retry-After` and emits a `agent.quota.exceeded` event the orchestrator turns into a Linear comment (agents/cost-controls consumes).
- CLI: `pnpm agents:key create --character forge --issue PAP-123 --ttl 8h --scopes repo:write,linear:comment`, `list`, `revoke <id>`, `rotate --character forge`; output is JSON for the orchestrator.
- Docs: `docs/platform/agent-principals.md` including the scope table and a sequence diagram of key minting per session.

**Definition of done**

- `pnpm agents:sync` creates nine agent users idempotently; second run makes no changes (test).
- A session key with `linear:comment` only receives 403 on `invoice.update` and 200 on allowed calls (Vitest integration).
- Rate limit test: the 601st request in a minute returns 429 with `Retry-After`.
- Audit rows for agent mutations include character, session and issue fields (test against data-layer/audit-log or its interface mock).
- `ActorBadge` stories for human, agent and agent-on-behalf-of, screenshots at 375 and 1280, light and dark; axe clean.
- Keys never logged: test greps server logs during key creation.
- Security Auditor confirms hashing and expiry; docs and changelog entry under "Identity"; Linear comment with Storybook link.

**Edge cases**

- Character removed from the roster: `agents:sync --prune` deactivates the user and revokes keys; history and attribution remain.
- Key used after its issue moved to Done: orchestrator revokes on state change; server also rejects keys whose `issue` metadata is closed if the Linear cache says so (soft check, logged).
- Two sessions for one character run in parallel: separate session keys with different `session` metadata; audit distinguishes them.
- Agent acts on behalf of a human (approved impersonation): `onBehalfOf` set and identity/impersonation rules apply; badge shows both.
- Clock drift between orchestrator and API: expiry evaluated server-side only.
- Plugin rate limit resets on server restart: acceptable for now; documented as a known gap with a Redis-backed option later.

**Dependencies**

- identity/rbac-abac (`can`, scope intersection). Soft: agents/roster-v1 (source of characters), data-layer/audit-log, pm-linear/orchestrator (key minting), agents/cost-controls (quota events), realtime/agent-presence (badge).

**Agent**

- Builds: Forge (lead); Atlas's Dispatcher sub-agent validates the minting flow from the orchestrator side.
- Reviews: Sentinel (Security Auditor, Code Reviewer); Iris (Component Crafter) reviews `ActorBadge`.

**Size**

M: mostly plugin configuration and a scope mapping, with careful attribution plumbing.
