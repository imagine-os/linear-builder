---
identifier: "PAP-55"
title: "Specify the audience model: customer tiers, staff roles, partners, admins, agents and composable segments in between"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Customer", "Staff", "Agent"]
milestone: "Auth works across web and desktop"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-227", "PAP-59"]
key: "identity/audience-model"
url: "https://linear.app/paperos/issue/PAP-55/specify-the-audience-model-customer-tiers-staff-roles-partners-admins"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-55: Specify the audience model: customer tiers, staff roles, partners, admins, agents and composable segments in between

**Goal**

Define the single vocabulary every page spec, policy, view and campaign uses to say who: principal types, tenant roles, customer tiers, partners, admins, agents, and composable segments for everything in between. Ship it as a typed schema and a document so specs are validated against real audience names rather than free text.

**Scope**

- In: the audience model document, Zod schema and TypeScript types in `packages/core`, the segment expression language, seed audiences for the template app, and the `audiences` section shape for `app.spec.yaml`.
- Out: evaluating permissions (identity/rbac-abac), storing memberships (identity/org-tenancy), and marketing segments over behavioural data (growth/segments extends this model with usage attributes).

**Spec**

Document `docs/specs/audience-model.md` and code in `packages/core/src/audience/`:

- `principal.ts`: `PrincipalType = 'human' | 'agent' | 'service' | 'anonymous'`. A `Principal` has `id`, `type`, `tenantId | null`, `attributes: Record<string, string | number | boolean | string[]>` (for example `tier`, `staffRole`, `partnerId`, `character`, `emailVerified`, `mfa`).
- `role.ts`: tenant roles as a fixed enum `owner | admin | staff | member | viewer` (maps to Better Auth organization roles in identity/org-tenancy); optional custom roles per tenant are named strings that must extend one of the five as a base.
- `audience.ts`: an `Audience` is `{ id: kebab-case, name, description, match: Segment }`. `Segment` is a recursive expression: `{ all: Segment[] } | { any: Segment[] } | { not: Segment } | { attr: string, op: 'eq' | 'neq' | 'in' | 'gte' | 'lte' | 'exists', value }` plus shorthand leaves `{ role: TenantRole }`, `{ principalType: PrincipalType }`, `{ tier: string }`. Depth limited to 6; evaluated in under 50 microseconds per principal by `matches(principal, segment)` (pure function, no I/O).
- Built-in audiences exported as `BUILTIN_AUDIENCES`: `anonymous`, `authenticated`, `customer` (human, tenantId set, role member or viewer, no staffRole), `customer-free`, `customer-pro`, `customer-enterprise` (tier attribute), `staff` (staffRole exists), `staff-support`, `staff-finance`, `admin` (role admin or owner), `owner`, `partner` (partnerId exists), `agent` (principalType agent), `developer` (attr `developer: true`), `everyone`. Each has a doc entry with an example principal that matches and one that does not.
- Composition rules: audiences may reference other audiences by id (`{ audience: 'staff' }`) with cycle detection in the schema refinement; an app declares extra audiences in `app.spec.yaml` under `audiences:` (shape agreed with spec-builder/app-level-spec: `audiences: Record<string, Omit<Audience, 'id'>>`), and page specs may only reference declared or built-in ids; `spec validate` enforces this.
- Human-readable rendering: `describe(segment)` returns text like "staff whose staffRole is support, or admins" for the spec editor and permission tests.
- Versioning: `AUDIENCE_MODEL_VERSION = 1` exported; changes require an ADR in the decision log.

**Definition of done**

- `packages/core/src/audience` exports schemas, types, `matches`, `describe`, `BUILTIN_AUDIENCES`; typecheck and Biome clean.
- Vitest: 100 per cent branch coverage of `matches`, cycle detection test, depth-limit test, property-based test with `fast-check` that `not(not(x))` equals `x` for random principals.
- Document merged with a table of built-in audiences and worked examples for "customer who is also a partner" and "agent acting for a staff member".
- `app.spec.yaml` shape documented and referenced by spec-builder/app-level-spec (comment left on that issue).
- Sentinel Code Reviewer and Quill approve; Atlas confirms agent audience matches agents/character-schema fields.
- Storybook or docs page not required; Linear comment with the doc link and coverage report.
- Changelog entry under "Platform".

**Edge cases**

- Principal belongs to several tenants: `Principal` is always tenant-scoped; multi-tenant users are represented as one principal per active tenant (identity/org-tenancy sets it).
- Attribute is an array (`staffRole: ['support', 'finance']`): `eq` on arrays matches any element; `in` intersects; documented.
- Unknown attribute referenced in a segment: `exists` returns false, other ops return false (never throw); `spec validate` warns.
- Anonymous principal with a tenant (public portal page): allowed; `anonymous` audience ignores tenantId.
- Agent impersonating a human (identity/impersonation): principal carries `actingFor` attribute; built-in `agent` still matches, and the model documents that policies must check `actingFor` explicitly.
- Tier names differ per app (clinic uses `plan: basic`): apps map their own attributes in `app.spec.yaml`; built-in tiers are examples, not requirements.

**Dependencies**

- None blocking. Consumers: identity/rbac-abac, spec-builder/access-section, spec-builder/app-level-spec, identity/staff-console-shell (audience filters), growth/segments, agents/character-schema.

**Agent**

- Builds: Quill (Page Spec Writer sub-agent) for the model document; Forge (Schema Wright) for the Zod implementation.
- Reviews: Sentinel (Code Reviewer) and Atlas.

**Size**

M: small code surface but it must be exact because every later policy depends on it.
