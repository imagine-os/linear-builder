---
identifier: "PAP-594"
title: "Delegated authority for agents: `actingFor` evaluation as the intersection of delegator permissions and agent scopes, delegation grants with expiry and consent, dual-actor audit and the \"Forge for Justin\" badge"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-38", "PAP-227", "PAP-586"]
blocks: []
key: "r4/identity/delegated-authority"
url: "https://linear.app/paperos/issue/PAP-594/delegated-authority-for-agents-actingfor-evaluation-as-the"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:13.651Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-594: Delegated authority for agents: `actingFor` evaluation as the intersection of delegator permissions and agent scopes, delegation grants with expiry and consent, dual-actor audit and the "Forge for Justin" badge

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Build M

**Goal**

PAP-55 defines `actingFor`, PAP-60 stores `onBehalfOf` and PAP-61 leaves 'agent onBehalfOf semantics beyond the marker' to nobody, yet the brief's agents act for people (migration, content, support). Without rules, an agent acting for an admin is an admin. This defines the rule: an agent may do what both the delegator and its own scopes allow, only under an explicit, expiring delegation, with both identities on every row.

**Scope**

In: Table `delegation (tenant_id, delegator_id, agent_user_id, scopes text[], reason, consented_at, expires_at, revoked_at, issue_key?)`; procedures `delegations.create|revoke|list|mine`; `can()` extension: when `actor.attributes.actingFor` is set, the decision is `can(delegator) AND can(agent) AND scopeAllows(delegation.scopes)`, deny from either side wins; `withScopes` reads the delegation; audit rows carry `actorId = agent`, `onBehalfOf = delegator`, `delegationId`; `ActorBadge` variant 'Forge for Justin' (from PAP-587); consent UI: a PAP-94 decision card or an in-app prompt for the delegator; orchestrator hook so a session started by Justin's approval mints a key with `actingFor` (PAP-96, soft); docs `docs/platform/delegation.md`.

Out: Agent keys and scopes (PAP-60 children), human impersonation (PAP-61), MCP allowlists (PAP-106), customer OAuth apps (PAP-222).

**Spec**

* A delegation is required for `actingFor`; a key carrying `actingFor` without a live delegation is refused with `DELEGATION_REQUIRED`; delegations expire (default 24 h, max 30 days) and are revocable by the delegator, tenant admins or `revoke-all` (PAP-301).
* Intersection semantics are proven by a property test: for random policy sets, `can(agent acting for D)` never exceeds `can(D)` nor `can(agent)`; `explain()` shows both branches.
* Delegator consent: staff and admins consent in-app (`requireRecentAuth`, PAP-581); customers consent through the portal prompt; Justin consents through a decision card; consent text names scopes and expiry.
* SQL: `toPredicate` for an acting principal compiles the delegator's predicate AND the agent's; RLS session variables carry `app.acting_for` so PAP-34 policies can reference it.
* Presence and comments show the dual identity (PAP-146, PAP-131 through `ActorRef.onBehalfOf`); `permission.changed` published on revoke.

**Interface contract**

Provides: Table `delegation`, procedures `delegations.*`, `can()` acting-for semantics, session variable `app.acting_for`, error `DELEGATION_REQUIRED`, consent components, docs.

Consumes: Policy engine and explain (PAP-227), SQL compiler (PAP-228), agent keys and `withScopes` (PAP-586), attribution and badge (PAP-587), audit (PAP-38), step-up (PAP-581, soft), decision cards (PAP-94, soft), orchestrator (PAP-96, soft), propagation (PAP-591, soft). Consumed by PAP-208 migration agent, PAP-192 content agent, PAP-118 spec agent, PAP-146, PAP-131.

**Definition of done**

* Agent with `specs:write` acting for a `viewer` cannot update a spec; acting for an admin with a delegation limited to `specs:write` cannot delete a user; both audited with both ids (compose tests through `callAs` and real keys).
* Property test of the intersection invariant; expired and revoked delegations refused; `revoke-all` clears them (PAP-301 dry run extended).
* Consent prompt at 375 and 1280; badge variant story; docs; changelog under Identity; Security Auditor signs off.

**Test plan**

* Unit: intersection logic including deny precedence, expiry and revocation, consent state machine, SQL predicate composition.
* E2E: Justin's decision card approves a migration agent for one tenant for 2 hours; the agent imports rows that carry both identities; revoking mid-run stops the next write.

**Demo**

Create a delegation from the seeded admin to `scout` limited to `import:write` for one hour, run the import example with the agent key, open the audit trail showing 'Scout for Ada', then revoke and rerun to see `DELEGATION_REQUIRED`. Under two minutes.

**Edge cases**

* Delegator loses the role mid-delegation: intersection shrinks immediately (server evaluates live).
* Agent acting for an agent: refused; delegations are human to agent only.
* Delegation across tenants: refused; one delegation per tenant.

**Dependencies**

Blocked by PAP-227, PAP-586, PAP-38 (hard). Soft: PAP-228, PAP-94, PAP-96, PAP-301, PAP-587, PAP-581, PAP-591. Consumed by PAP-208, PAP-192, PAP-118, PAP-146, PAP-131.

**Agent**

Builder: Forge (Platform Engineer); Atlas reviews the orchestrator hook. Reviewer: Sentinel (Security Auditor; Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/identity/agent-attribution-quotas` = PAP-587, `r4/identity/agent-keys` = PAP-586, `r4/identity/permission-propagation` = PAP-591, `r4/identity/sessions-stepup` = PAP-581.
