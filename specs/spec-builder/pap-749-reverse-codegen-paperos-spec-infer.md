---
identifier: "PAP-749"
title: "Reverse codegen: `paperos-spec infer <route>` drafts a page spec from an existing route file, component tree and data hooks for retrofitting unspecced pages"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Spec editor UI"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-74", "PAP-115"]
blocks: []
key: "r4/spec-builder/reverse-codegen-infer"
url: "https://linear.app/paperos/issue/PAP-749/reverse-codegen-paperos-spec-infer-route-drafts-a-page-spec-from-an"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:17.306Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-749: Reverse codegen: `paperos-spec infer <route>` drafts a page spec from an existing route file, component tree and data hooks for retrofitting unspecced pages

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

PAP-115 fails a PR on `SPEC_ROUTE_UNCOVERED` and the fix is to write a spec by hand. Hand-written pages already exist in the template (auth pages, settings, dev tools) and will keep appearing when agents prototype. Infer a draft spec from the code, the way Storybook's autodocs and Figma dev mode read what exists, so retrofitting is a review, not a rewrite.

**Scope**

In: `paperos-spec infer <routeFile|route> [--write] [--all-uncovered]` in `packages/spec/src/infer/` using `ts-morph` to read the route file (`createFileRoute`, `validateSearch`, `staticData`), the view component tree (JSX elements matching PAP-74 registry ids, `data-spec-key`, `data-action`), hooks from `@paperos/api-contract` and generated data modules, `useCan` calls for access hints and `t()` ids for copy; output `specs/pages/<id>.spec.yaml` with `meta.status: draft`, `x-inferred: { at, confidence, unresolved[] }`; `docs/spec/infer.md`. Out: inferring business logic, perfect fidelity (drafts are reviewed), non-React targets.

**Spec**

* Mapping rules: route path to `meta.route` and `layout.template` from the layout parent; registry components to `components[]` with props literal-extracted where static; `useQuery(orpc.x.list)` to `data.queries`; `useMutation` to `data.mutations`; `useCan('page.view')` and `authorize` middleware to `access.view` hints; `states` from `Suspense`, `ErrorBoundary`, `EmptyState` usage; `events` from `navigate()` and `<Link>` targets.
* Unknown JSX elements become `x-unresolved` entries with file and line; confidence is the share of resolved nodes; below 0.5 the file is written but the CLI exits 2.
* `--all-uncovered` walks PAP-115's `SPEC_ROUTE_UNCOVERED` list and writes drafts for each; a summary table is printed and, in CI, posted as a PR comment.
* Drafts never receive `status: ready`; the PAP-118 skill can open an issue per draft (`author-spec open-issue --from-infer`).
* Idempotent: re-running on an unchanged file yields the same draft; a spec that already exists is never overwritten without `--force`.

**Interface contract**

Provides: `inferSpec(routeFile): { spec, confidence, unresolved }`, CLI, `x-inferred` convention, PR comment table. Consumes: `PageSpecSchema` (PAP-114), route discovery (PAP-115), component registry and `data-spec-key` conventions (PAP-74, PAP-315), API contract types (PAP-268), `ts-morph`. Consumed by: PAP-118 skill, PAP-105 `page-from-spec` (retrofit mode), PAP-24 template guide, PAP-306 re-audit (uncovered routes count).

**Definition of done**

* Inferred drafts for the template's auth pages (PAP-224) and settings pages reach confidence at or above 0.7 and validate as `draft`; `--all-uncovered` on the template leaves zero uncovered routes after review.
* `docs/spec/infer.md` with the mapping table; CHANGELOG entry; Linear comment with one draft side by side with its source.

**Test plan**

* Unit: each mapping rule on fixture components; confidence math; unresolved reporting; idempotency.
* Integration: run on the template repo; every draft validates; typecheck untouched.
* E2E: none.

**Demo**

Run `paperos-spec infer apps/web/src/routes/_app/settings/members.tsx`, open the draft, read the `x-unresolved` list and the confidence, fix two entries and promote to `ready`. Under two minutes.

**Edge cases**

* Route file with dynamic component maps: components listed as `x-unresolved` with a hint.
* Page using a non-registry component: `SPEC_UNKNOWN_COMPONENT` on validate points at the component to register (PAP-74).
* Generated page (has a banner): refuses; the spec is the source there.

**Dependencies**

Hard: PAP-115, PAP-74. Soft: PAP-268, PAP-315, PAP-118, PAP-105.

**Agent**

Builder: Nova. Reviewer: Sentinel (Code Reviewer) with Quill checking spec fidelity.

**Size**

M: one session.
