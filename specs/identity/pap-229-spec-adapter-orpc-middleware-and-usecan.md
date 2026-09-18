---
identifier: "PAP-229"
title: "Spec adapter, oRPC middleware and useCan hook"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: "PAP-59"
children: []
blockedBy: ["PAP-227"]
blocks: ["PAP-60", "PAP-61", "PAP-64", "PAP-116", "PAP-131", "PAP-140", "PAP-163", "PAP-172", "PAP-178", "PAP-222", "PAP-317", "PAP-335", "PAP-458", "PAP-501", "PAP-538", "PAP-566", "PAP-586", "PAP-590", "PAP-591", "PAP-623", "PAP-638", "PAP-658", "PAP-849", "PAP-884", "PAP-902", "PAP-912"]
key: "identity/rbac-abac/adapter-middleware-hook"
url: "https://linear.app/paperos/issue/PAP-229/spec-adapter-orpc-middleware-and-usecan-hook"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:48.455Z"
model: "claude-opus-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-23"
cycle: null
---

# PAP-229: Spec adapter, oRPC middleware and useCan hook

**Model / Effort:** Opus 5 (`claude-opus-5`) / medium — Build M, P0 in identity

**Goal**

Connect the engine to the three places it is used: page specs (adapter from `access:` sections), the API (`authorize()` middleware) and the UI (`useCan()` with `PermissionProvider`), with Storybook stories that show each affordance.

**Scope**

* In: `from-spec.ts` adapter (draft shape until PAP-116 finalises), `authorize(action, resolveResource)` oRPC middleware with dev-mode explain, `PermissionProvider`, `useCan`, `hiddenWhenDenied` and `disabledWhenDenied` props on design-system Button and Menu items, policy fetch endpoint `permissions.mine`.
* Out: engine and SQL (siblings), matrix tests (PAP-64).

**Spec**

* Adapter: `accessToPolicies(section: AccessSection, source) => Policy[]`; draft `AccessSection = { view: AudienceId[], actions: Record<name, { audiences, condition? }> }` marked `@draft` and swapped when PAP-116 lands; loader reads `specs/**/page.spec.yaml` and `app.spec.yaml`.
* Middleware: `authorize('invoice.update', ({ input }) => ({ type: 'invoice', id: input.id }))` runs `can()` after `withTenant`; 403 body `{ code: 'FORBIDDEN', explain? }` with explain only when `PAPEROS_ENV !== 'production'`.
* Client: `permissions.mine` returns the actor's applicable policies (compressed); `PermissionProvider` caches per session and tenant, refetches on `session.updated` and tenant switch; `useCan(action, resource) => boolean | 'loading'`.
* Design system: Button, IconButton, Menu.Item accept `can?: { action, resource }` and apply hidden or disabled behaviour with a tooltip reason.

*Round 4 amendment (2026-09-18):*
`PermissionProvider` also refetches on the `permission.changed` topic (PAP-591) delivered through the push transport or a 30 s version poll of `permissions.version`; `useCan` gains an optional `{ field }` argument once PAP-590 lands and returns `'loading'` for unknown fields until then.

**Interface contract**

* Provides: `authorize()`, `PermissionProvider`, `useCan()`, `accessToPolicies()`, procedure `permissions.mine`.
* Requires: sibling evaluator; PAP-35 oRPC; PAP-58 `withTenant`; PAP-67 components; PAP-116 final shape (soft).

**Definition of done**

* 403 responses carry explain text in dev and a generic message in prod (tests).
* Fixture specs (three pages) convert to policies with correct sources; Quill confirms alignment with PAP-116.
* Storybook stories for allowed, denied-hidden, denied-disabled, loading; screenshots at 375 and 1280.
* Docs section "Using permissions".

**Test plan**

* Unit: adapter on fixture specs, invalid audience error.
* Integration: middleware with a fake resolver, tenant switch refetch.
* Visual: four stories; axe on disabled-with-tooltip.

**Demo**

Open the Storybook "Permissions" group, toggle the actor control between customer and support, watch the Delete button hide and disable; then call a denied procedure in dev and read the explain. Under two minutes.

**Edge cases**

* `useCan` before policies load: returns `'loading'`; components render disabled, never allowed.
* Resource id unknown client-side (create actions): resource `{ type }` only.
* Spec declares an action with no policy: adapter emits an explicit deny with source.

**Dependencies**

Sibling evaluator child (hard). Soft: PAP-116, PAP-35, PAP-58, PAP-67.

**Agent**

Built by Forge with Iris on component props. Reviewed by Sentinel (Code Reviewer) and Quill (spec alignment).

**Size**

M.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/identity/field-permissions` = PAP-590, `r4/identity/permission-propagation` = PAP-591.
