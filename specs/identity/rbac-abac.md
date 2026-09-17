---
identifier: "PAP-59"
title: "Build permission engine combining role-based grants with attribute policies declared in page specs"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: null
children: ["PAP-227", "PAP-228", "PAP-229"]
blockedBy: ["PAP-279", "PAP-34", "PAP-55"]
blocks: ["PAP-116", "PAP-131", "PAP-140", "PAP-163", "PAP-172", "PAP-178", "PAP-222", "PAP-39", "PAP-60", "PAP-61", "PAP-64"]
key: "identity/rbac-abac"
url: "https://linear.app/paperos/issue/PAP-59/build-permission-engine-combining-role-based-grants-with-attribute"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-59: Build permission engine combining role-based grants with attribute policies declared in page specs

**Goal**

Build the permission engine every layer shares: one `can(actor, action, resource, context)` that combines role-based grants with attribute policies declared in page specs, evaluates identically in the API, compiles to SQL predicates for Postgres RLS and where-clauses, and drives UI affordances through a `useCan` hook. Deny by default, explainable on request.

**Scope**

- In: `packages/permissions` with the policy model, evaluator, SQL compiler, spec loader, explain mode, React hook, oRPC middleware, Drizzle RLS helpers, fixtures and benchmarks.
- Out: the access-section YAML format itself (spec-builder/access-section defines it; this issue consumes it via an adapter), agent keys (identity/agent-principals), generated matrix tests (identity/permission-tests).

**Spec**

`packages/permissions` in `imagine-os/paperos-template`:

- Model (`src/model.ts`, Zod): `Policy = { id, effect: 'allow' | 'deny', audiences: AudienceId[] (from identity/audience-model), actions: Action[] , resource: ResourceType | '*', condition?: Condition, source: { specPath, line } }`. `Action` is a dotted string `<entity>.<verb>` with verbs `read | list | create | update | delete | export | share | impersonate | manage` and page-level `page.view` and `page.action:<name>`. `Condition` is a small typed expression tree: `{ all | any | not }`, and leaves comparing a resource path to a literal or an actor path (`{ path: 'resource.ownerId', op: 'eq', ref: 'actor.id' }`, ops `eq | neq | in | contains | gte | lte | isNull`). No arbitrary code, so it can compile to SQL.
- Evaluation (`src/evaluate.ts`): `can(actor: Principal, action, resource: { type, id?, attrs? }, ctx: { tenantId }) => Decision { allowed, matched: PolicyId[], explain(): string }`. Order: explicit deny wins, then any allow, else deny. Role grants are expressed as built-in policies for the five roles (`owner` and `admin` get `*.manage`; `staff` gets `*.read/list/create/update` on staff resources; `member` and `viewer` get scoped reads) loaded from `src/builtin-policies.ts`. Target under 20 microseconds per call with 200 policies; benchmark with `tinybench`.
- SQL compilation (`src/compile-sql.ts`): `toPredicate(actor, action, resourceType) => SQL` (Drizzle `sql` fragment) implementing the same semantics so list endpoints filter rows instead of post-filtering; and `toRlsPolicy(resourceType)` emitting a `CREATE POLICY` statement using session variables `app.principal_id`, `app.tenant_id`, `app.role`, and `app.attrs jsonb` set by the `withTenant` middleware from identity/org-tenancy. Conditions referencing `actor.attributes.*` compile to `current_setting('app.attrs')::jsonb ->> key`.
- Spec loader (`src/from-spec.ts`): reads `access:` sections from `specs/**/page.spec.yaml` and `app.spec.yaml` through the adapter contract published by spec-builder/access-section (`AccessSection -> Policy[]`); until that lands, a draft adapter for `{ view: AudienceId[], actions: Record<name, { audiences, condition? }> }` is used and marked `@draft`.
- Integration: oRPC middleware `authorize(action, resolveResource)` returns 403 with `decision.explain()` in non-production; React `useCan(action, resource)` reads a `PermissionProvider` seeded with the actor's policies fetched once per session and refetched on tenant switch; components from the design system accept `hiddenWhenDenied` or `disabledWhenDenied`.
- Explain: `pnpm permissions explain --actor fixtures/staff-support.json --action invoice.update --resource invoice:123` prints the matched policies with spec file and line.
- Docs: `docs/platform/permissions.md` with the decision algorithm, a table of verbs, and three worked examples (customer sees own invoices; support staff can impersonate; agents may not delete).

**Definition of done**

- Evaluator has 100 per cent branch coverage; property test asserts SQL predicate and in-memory `can` agree on 10 000 random actor/resource pairs (using PGlite for SQL).
- Benchmark shows under 20 microseconds median for `can` with 200 policies (numbers in PR).
- `toRlsPolicy` output applied to the `invoices` fixture table in the data-layer/rls-tenancy harness; cross-tenant and cross-owner reads fail.
- oRPC 403 responses include explain text in dev and a generic message in prod (tests).
- `useCan` demonstrated in Storybook with a story per outcome (screenshots at 375 and 1280).
- Draft or final spec adapter has fixture specs and tests; Quill confirms alignment with spec-builder/access-section.
- Docs merged; changelog entry under "Identity"; Linear comment with benchmark table and Storybook link.

**Edge cases**

- Policy references an audience not declared: loader fails validation with file and line; never silently denies at runtime.
- Resource without a tenantId (global reference data): `resource.tenantId` null matches only policies marked `global: true`.
- Conflicting allow and deny at different specificity: deny always wins; documented, no precedence by specificity.
- Actor attributes change mid-session (promoted to admin): `PermissionProvider` refetches on `session.updated` events; server always evaluates fresh.
- Condition compares to an array attribute (`actor.attributes.regions contains resource.region`): supported by `contains`; SQL uses `?` jsonb operator.
- More than 1 000 policies in one app: loader warns and the benchmark test fails above 100 microseconds so growth is noticed.

**Dependencies**

- identity/audience-model (principal and audience types), data-layer/rls-tenancy (session variables and harness). Soft: spec-builder/access-section (adapter contract), data-layer/api-layer (middleware), identity/org-tenancy (`withTenant`).

**Agent**

- Builds: Forge (lead) with Schema Wright for SQL compilation.
- Reviews: Sentinel (Security Auditor mandatory, Code Reviewer, Edge Case Hunter for the property tests).

**Size**

L: a policy language with two execution targets that must provably agree.
