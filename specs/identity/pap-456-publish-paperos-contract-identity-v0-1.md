---
identifier: "PAP-456"
title: "Publish @paperos/contract-identity v0.1 with manifest"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-33", "PAP-55", "PAP-433"]
blocks: ["PAP-60", "PAP-61", "PAP-220", "PAP-457", "PAP-458", "PAP-580", "PAP-586"]
key: "module/identity/contract"
url: "https://linear.app/paperos/issue/PAP-456/publish-paperoscontract-identity-v01-with-manifest"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:05.613Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-23"
cycle: null
---

# PAP-456: Publish @paperos/contract-identity v0.1 with manifest

**Model / Effort:** Opus 5 / high

**Goal**

Publish `@paperos/contract-identity` v0.1 and the `identity` module manifest so every other module codes against a versioned package instead of `packages/auth, packages/permissions, packages/core/audience` internals (`docs/module-system.md` sections 1 to 3). The contract holds only types, Zod schemas, event topics, route signatures, slot definitions and port interfaces; the implementation stays where the existing issues put it. Swap risk is declared `critical`, which decides how much of the swap playbook a rewrite must follow.

**Scope**

In:

* `packages/contracts/identity/` published as `@paperos/contract-identity` (workspace-private, `0.1.0`): `src/index.ts`, `ports.ts`, `events.ts`, `routes.ts`, `slots.ts` as applicable, an empty `conformance/` (filled by the conformance issue) and `fixtures/`.
* `module.ts` via `defineModule()` (PAP-264 shape) extended with `provides: [{ contract: '@paperos/contract-identity', version: '0.1.0' }]`, `requires`, `capabilities`, `slots`, `events`, `owner: { agent: 'Forge', project: 'identity' }`, `swapRisk: 'critical'`, `kind: 'runtime core'`, plus the generated `module.manifest.json`.
* `ownership.json` `contracts` entry (PAP-305 file) and the generated `docs/platform/contracts/identity.md` (a `typedoc` stub until the docs generator lands).

Out: runtime behaviour, React, Drizzle tables, network calls; the conformance suite and the kernel binding (own issues). Nothing already fixed by PAP-55, PAP-33 is redesigned; it is packaged.

**Spec**

Ports and schemas exported at v0.1:

* `Principal`, `PrincipalType`, `ActorRef` projection, audience segments (PAP-55)
* `AuthPort`: `getSession`, `signIn.*`, `signOut`, `issueAgentKey`, `revokeKey`, device and session listing (PAP-57, PAP-60, PAP-220)
* `PermissionPort`: `can`, `explain`, `sqlPredicate`, `withScopes`, spec adapter input (PAP-59, PAP-227 to PAP-229)
* `TenantPort`: tenants, workspaces, memberships, invitations, `switchTenant`, `useTenant` (PAP-58)
* `ImpersonationPort` with mandatory reason (PAP-61) and `EntitlementHook` for business-core (PAP-178)
* Slot fills declared: `shell.userMenu`, `shell.tenantSwitcher`, `shell.settings.sections:members`

Events declared with `defineTopic()` (payload schemas, version 1): `tenant.created|deleted`, `membership.invited|accepted|removed`, `agent.session.started|finished|blocked`, `session.revoked`.

Requires (manifest `requires[]`): \* `@paperos/contract-data-layer` ^0.1 (repositories, RLS session variables, event bus)

Rules: Zod 4 only, JSON Schema generated; no `z.bigint()` on wire schemas (PAP-302 codec); one sentence and one fixture per port method; `size-limit` under 50 KB minified; lint R9 passes; manifest `dependsOn` is derived from `requires`.

**Interface contract**

Provides: `@paperos/contract-identity@0.1.0` with the exports above; `module.manifest.json` valid against `manifest.schema.json`; `ownership.json` `contracts.identity`. Consumes: the manifest schema and validator (`PAP-433`), contract-zero (`@paperos/core/types|filter|events`), the decisions in PAP-55 (Specify the audience model: customer tiers, staff roles, par), PAP-33 (Model core platform entities: tenant, workspace, user, membe). Consumed by: PAP-60 (agent principals), PAP-61 (impersonation), PAP-220 (session management), PAP-64 (permission matrix tests), PAP-140 (Hocuspocus auth hook), every `can()` caller, and the module's conformance and wire issues.

**Test plan**

* Static: lint rules R7 to R9; generated JSON Schema committed and unchanged; `size-limit`; `tsc --noEmit` with `exactOptionalPropertyTypes`.
* Unit: every schema accepts its valid fixture and rejects its invalid one (the five base roles times four audiences as a permission matrix (80 cases), six policy explain traces, three tenant switch sequences, two agent key scopes, one impersonation with audit expectation); `defineTopic` registrations resolve at import; the manifest validates and its `requires` resolve against the other manifests.
* Review: Sentinel confirms no implementation leaked into the package.

**Definition of done**

* Package merged, `0.1.0` in the workspace changeset; manifest validates; compatibility matrix shows every `requires` as `ok` or a named pending provider.
* `docs/platform/contracts/identity.md` generated; short ADR `docs/adr/00xx-contract-identity.md` recording what was pinned.
* Comments on PAP-60, PAP-61, PAP-220 that their Interface contract sections now import from `@paperos/contract-identity`; Linear comment here with the docs link.

**Edge cases**

* A port the implementation has not built yet: declared `@experimental` with a fixture; conformance marks it `pending`, never `passed`.
* A type two modules want (for example `Money`) belongs to contract-zero; the validator rejects a schema whose `$id` collides with a core one.
* Implementation disagrees with the contract after merge: the contract wins; the implementation issue gets a comment and a fix child.

**Dependencies**

Blocked by `PAP-433` and PAP-55, PAP-33. Blocks PAP-60, PAP-61, PAP-220, `PAP-457` and `PAP-458`. Soft: docs generator, compatibility matrix job.

**Agent**

Specified by Forge (Identity, Roles & Audiences owner). Reviewed by Sentinel and Atlas (contract ownership).

**Size**

M

**Demo**

Reviewer runs `pnpm contract:show identity`, then `pnpm conformance identity --impl memory` and sees the 80-case permission matrix pass against the in-memory evaluator. Under two minutes.
