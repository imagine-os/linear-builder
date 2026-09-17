---
identifier: "PAP-312"
title: "Data section: typed hook generator for server, live and local sync modes"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Codegen and conformance tests"
state: "Backlog"
parent: "PAP-119"
children: []
blockedBy: ["PAP-35", "PAP-311"]
blocks: ["PAP-313", "PAP-473"]
key: "spec-builder/data-section/generator"
url: "https://linear.app/paperos/issue/PAP-312/data-section-typed-hook-generator-for-server-live-and-local-sync-modes"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:23.486Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-312: Data section: typed hook generator for server, live and local sync modes

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Generate typed React hooks from the data section: `use<Query>()` and `use<Mutation>()` backed by TanStack Query plus the oRPC client for `server`, and by Electric shapes plus the offline outbox for `live` and `local`, with access rows merged into filters, optimistic updaters and a drift check so generated files stay in sync with specs.

**Scope**

* In: `packages/spec/src/codegen/data.ts`, templates, `pnpm spec gen:data [id] [--all] [--check]`, `dataStates` export, drift banner.
* Out: schema and rules (PAP-311), the live example (PAP-313).

**Spec**

* Output `apps/web/src/generated/<id>.data.ts` with a banner (spec hash), imports from `@paperos/api-contract` (PAP-35) and `@paperos/sync` (PAP-36).
* `server`: `useQuery` keyed by `[specId, queryName, params]`, `fetchNextPage` cursor paging at `page`, types from the contract; mutations via `useMutation` with optimistic `setQueryData` updater and rollback when `optimistic: true` (requires `input.id`, enforced by the schema child).
* `live | local`: `useShape` with a server-set `where` derived from filter plus PAP-116 rows; mutations enqueue to the PAP-36 outbox with the same optimistic updater; `isStale` from the shape status.
* Access rows merged as an `all` node at generation time; `audit: true` adds a required `reason` input per PAP-38.
* `dataStates` export maps `status` to spec `states` keys for PAP-120; hook name collisions fail generation; deterministic output; `--check` compares hashes.

**Interface contract**

* Provides: `generateData(spec, app, contract): GeneratedFile`, hooks `use<PascalCase(name)>`, `dataStates`, CLI, drift banner format shared with PAP-120.
* Consumers: PAP-120 views import hooks and `dataStates`; PAP-122 mocks the module path; PAP-125 commits generated files; PAP-105 `page-from-spec` runs `gen:data`.
* Requires: schema child, PAP-35 client and contract, PAP-36 `useShape` and outbox, PAP-116 `rows`, PAP-38 audit input.

**Definition of done**

* Snapshots for `server`, `live`, `local` on minimal and maximal fixtures; typecheck of generated output in `apps/web`.
* Optimistic rollback tested with a failing mocked client.
* `--check` red on a changed spec without regeneration; drift job wired in gate 1.
* Changelog; Linear comment with a generated file excerpt.

**Test plan**

* Unit: template snapshots, name derivation and collision, access row merge, `reason` injection.
* Integration: hooks rendered with Testing Library against a mocked oRPC client and a mocked shape; paging.
* No UI in this child; visuals in the example child.

**Demo**

Run `pnpm spec gen:data customer-invoices`, open the generated file and point at `useInvoices` with its merged filter and `useMarkPaid` with the optimistic updater; change `sync` to `server`, regenerate and diff. One minute.

**Edge cases**

* Entity without a registered shape in `live`: fallback to `server` with a warning comment in the file.
* Contract type missing for a field: generation fails naming the field.
* Two queries on one entity with different fields: two hooks, shared query key prefix.
* `page` above 200: capped; hook paginates in 100s.
* Biome missing: unformatted output with a warning.

**Dependencies**

Blocked by PAP-311, PAP-35. Soft: PAP-36, PAP-116, PAP-38.

**Agent**

Built by Forge (Schema Wright); reviewed by Nova and Sentinel.

**Size**

M
