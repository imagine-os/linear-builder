---
identifier: "PAP-55"
title: "Specify the audience model: customer tiers, staff roles, partners, admins, agents and composable segments in between"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Agent"]
milestone: "Auth works across web and desktop"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-59", "PAP-227", "PAP-363", "PAP-456", "PAP-507", "PAP-730", "PAP-887", "PAP-893", "PAP-894"]
key: "identity/audience-model"
url: "https://linear.app/paperos/issue/PAP-55/specify-the-audience-model-customer-tiers-staff-roles-partners-admins"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T12:56:50.472Z"
model: "claude-fable-5-1"
effort: "high"
estimate: 3
dueDate: "2026-09-23"
cycle: {"number": 1, "name": "C1 Foundation & core systems", "startsAt": "2026-09-18", "endsAt": "2026-09-25"}
---

# PAP-55: Specify the audience model: customer tiers, staff roles, partners, admins, agents and composable segments in between

**Model / Effort:** Fable 5.1 (`claude-fable-5-1`) / high — keystone spec: audience model

**Goal**

Define the single vocabulary every page spec, policy, view and campaign uses to say who: principal types, tenant roles, customer tiers, partners, admins, agents, and composable segments for everything in between. Ship it as typed code in `packages/core` plus a document, so specs validate against real audience ids instead of free text.

**Scope**

* In: `docs/specs/audience-model.md`; `packages/core/src/audience/` with Zod schemas, types, `matches`, `describe`, `BUILTIN_AUDIENCES`; the segment expression language; the `audiences:` shape for `app.spec.yaml`.
* Out: evaluating permissions (PAP-59), storing memberships (PAP-58), behavioural marketing segments (PAP-195 extends this with usage attributes).

**Spec**

* `principal.ts`: `PrincipalType = 'human' | 'agent' | 'service' | 'anonymous'`; `Principal = { id, type, tenantId: string | null, attributes: Record<string, string | number | boolean | string[]> }` (attributes such as `tier`, `staffRole`, `partnerId`, `character`, `emailVerified`, `mfa`, `actingFor`). This is the canonical actor type; PAP-35's API context and PAP-60 import it rather than redefining it.
* `role.ts`: `TenantRole = 'owner' | 'admin' | 'staff' | 'member' | 'viewer'`, mapped one-to-one to Better Auth organization roles in PAP-58; custom roles are named strings that must extend one of the five.
* `audience.ts`: `Audience = { id: kebab-case, name, description, match: Segment }`; `Segment = { all } | { any } | { not } | { attr, op: eq|neq|in|gte|lte|exists, value }` with shorthand leaves `{ role }`, `{ principalType }`, `{ tier }`, `{ audience: id }`; depth limit 6; `matches(principal, segment)` is pure and under 50 µs.
* Built-ins: `anonymous`, `authenticated`, `customer`, `customer-free`, `customer-pro`, `customer-enterprise`, `staff`, `staff-support`, `staff-finance`, `admin`, `owner`, `partner`, `agent`, `developer`, `everyone`, each with a matching and a non-matching example principal.
* Composition: audiences reference others by id with cycle detection; apps add audiences in `app.spec.yaml` under `audiences: Record<string, Omit<Audience, 'id'>>` (shape agreed with PAP-117); page specs may only reference declared or built-in ids and `spec validate` enforces it.
* `describe(segment)` renders text such as "staff whose staffRole is support, or admins"; `AUDIENCE_MODEL_VERSION = 1`, changes need an ADR.

**Interface contract**

* Provides (from `@paperos/core/audience`): types `Principal`, `PrincipalType`, `TenantRole`, `Audience`, `AudienceId`, `Segment`; functions `matches`, `describe`, `validateAudiences`; constants `BUILTIN_AUDIENCES`, `AUDIENCE_MODEL_VERSION`; JSON Schema for the `audiences:` section.
* Consumers: PAP-59 (policy `audiences` field), PAP-116 and PAP-117 (spec validation), PAP-63 `AudienceFilter`, PAP-64 fixture principals, PAP-240 `testUsers`, PAP-195, PAP-103 (agent principal attributes).
* Requires: nothing at runtime.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (`Principal = { id, type: 'human'|'agent'|'service'|'anonymous', tenantId, attributes }` from `@paperos/core/audience` is the canonical actor type; `ActorRef = { id, type, character? }` is its projection stored on rows, events and comments; `user.kind` in PAP-33 and `principalType` in PAP-57/PAP-60 are storage views of the same enum); §2 row "Membership / Role" (five base roles `owner|admin|staff|member|viewer` come from this issue); §6 row "`Principal` and audiences" (consumers PAP-35/267, PAP-59, PAP-60, PAP-114, PAP-136, PAP-141, PAP-195). This issue is the provider: export exactly that shape and change it only through an ADR (PAP-130).

**Definition of done**

* Package exports the API above; typecheck and Biome clean.
* Vitest: 100 percent branch coverage of `matches`; cycle and depth tests; `fast-check` property that `not(not(x))` equals `x` and that `all([])` matches everyone.
* Document merged with the built-in table and two worked examples: a customer who is also a partner; an agent acting for a staff member.
* Comment left on PAP-117 confirming the `audiences:` shape; Atlas confirms `agent` attributes match PAP-103.
* Changelog entry under "Platform"; Linear comment with the doc link and coverage report.

**Test plan**

* Unit: every operator including arrays (`eq` matches any element, `in` intersects), unknown attribute returns false and never throws, shorthand leaves, audience references, `describe` snapshots for all built-ins.
* Property: 10 000 random principals against random segments, de Morgan equivalences hold.
* Bench: `tinybench` median under 50 µs at depth 6.
* Contract: JSON Schema round-trips a fixture `app.spec.yaml`.

**Demo**

Run `pnpm audience explain --principal fixtures/customer-partner.json` and read which built-in audiences match and why; then break a fixture `app.spec.yaml` with a cyclic audience and watch `pnpm spec validate` name the cycle. Under one minute.

**Edge cases**

* Multi-tenant user: one `Principal` per active tenant; PAP-58 sets it.
* Anonymous principal on a public tenant page: `anonymous` ignores `tenantId`.
* Agent impersonating a human: `actingFor` attribute; `agent` still matches and policies must check `actingFor` explicitly.
* App-specific tier names (`plan: basic`): apps map their own attributes; built-in tiers are examples.

**Dependencies**

None blocking. Consumers listed above.

**Agent**

Quill (Page Spec Writer) writes the document; Forge (Schema Wright) implements. Reviewed by Sentinel (Code Reviewer) and Atlas.

**Size**

M: small code, permanent decisions.
