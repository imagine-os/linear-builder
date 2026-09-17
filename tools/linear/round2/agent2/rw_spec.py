"""Rewritten descriptions for spec-builder (PAP-114..PAP-126)."""
DESCRIPTIONS = {}

DESCRIPTIONS["PAP-114"] = """**Goal**

Define the canonical `page.spec.yaml` format every PaperOS page must have: a Zod 4 schema in `packages/spec` with generated JSON Schema for editors and TypeScript types for codegen. Validator, codegen, conformance tests, canvas and permission engine all read this contract, so it lands first and changes only through ADRs.

**Scope**

* In: `packages/spec/src/schema/page.ts`, `packages/spec/schema/page.spec.schema.json`, fixtures (valid and invalid), `docs/spec/page-spec.md`, the format ADR, `migrateSpec()` skeleton, the `specVersion` field.
* Out: final `access` (PAP-116), `data` (PAP-119), `integrations` (PAP-121) shapes, which ship here as interim placeholders; the validator CLI (PAP-115); versioning tooling ({{spec-builder/spec-versioning}}); i18n of copy ({{spec-builder/spec-i18n}}).

**Spec**

* Sections: `meta` (`id`, `title`, `route`, `surface: customer | staff | developer | agent | public`, `owner`, `status: draft | ready | built | deprecated`, `specVersion: 1`), `purpose` (`summary`, `successMetric`), `logic.actions` (`steps[]`, `guard`, `effects[]`, `onError`), `access`, `data`, `integrations`, `layout` (`template: app | public | focus | kiosk`, `slots`), `components` (tree `{ id: ComponentRef, key, props, slot, events, children }`), `states` (`loading`, `empty`, `error`, `offline`, `denied`, custom; each `{ copy, component? }`), `events` (`{ on, to: RouteRef, guard?, kind }`), `edgeCases[]` (`{ id, scenario, expected, test: unit | e2e | manual }`).
* File `specs/pages/<id>.spec.yaml`; `meta.id` equals the filename stem; first line points at the JSON Schema.
* `status: ready` requires `access`, `data` or `x-static: true`, three edge cases and resolvable `events[].to`; component `events` values must reference `logic.actions`.
* `RouteRef` accepts TanStack `$param` syntax; `ComponentRef` regex agreed with PAP-74; `states.copy` strings are plain until {{spec-builder/spec-i18n}} adds message ids (`x-i18n` reserved).
* YAML anchors and merge keys resolved before validation; errors carry `line` and `col` of the merged document.

**Interface contract**

* Provides: `@paperos/spec` exporting `PageSpec`, `PageSpecSchema`, `ComponentRef`, `RouteRef`, `SpecIssue = { code, severity, message, path, line, col, hint }`, `parseSpec(yaml): Result<PageSpec, SpecIssue[]>`, `migrateSpec(doc)`, the JSON Schema, `specVersion` constant.
* Consumers: PAP-115 rules, PAP-116, PAP-119, PAP-121 (section schemas extend this file), PAP-120 and PAP-122 codegen, PAP-123 graph, PAP-124 editor, PAP-16 `useSpec` (replaces its interim type), PAP-74 registry, PAP-85 edge-case hunter, PAP-132 canvas loader.
* Requires: nothing hard; `ComponentRef` pattern from PAP-74 (interim regex acceptable).

**Definition of done**

* Fixtures parse; each invalid fixture fails with expected `code`, `line`, `col`; JSON Schema snapshot committed.
* `pnpm spec schema:build` idempotent; drift wired into gate 1 (PAP-78).
* VS Code autocompletion screenshot on a fixture.
* `docs/spec/page-spec.md` generated with every field; ADR registered in PAP-130.
* `@paperos/spec` types consumed by PAP-16; changelog; Linear comment with links.

**Test plan**

* Unit (Vitest): parse every fixture; codes `SPEC_DUP_KEY`, `SPEC_BAD_ROUTE`, `SPEC_ACTION_UNBOUND`, `SPEC_READY_INCOMPLETE`, `SPEC_TOO_LARGE`; anchor resolution positions; BOM and CRLF normalisation.
* Property: `parseSpec(stringify(spec))` round-trips for generated valid specs.
* Snapshot: JSON Schema.
* No UI; no breakpoints.

**Demo**

Open `fixtures/valid/customer-invoices.spec.yaml` in VS Code and trigger completion on `layout.template`; then run `pnpm spec parse fixtures/invalid/dup-key.spec.yaml` and read `SPEC_DUP_KEY` with both line numbers. Under one minute.

**Edge cases**

* Duplicate `components[].key`: error listing both lines.
* Route with `:param`: rejected, `$param` only.
* Spec over 200 KB: warn, suggest splitting.
* `specVersion` missing: treated as 1 with a warning.
* Unknown top-level key without `x-` prefix: error; `x-*` passes through untouched.

**Dependencies**

None hard (`readyNow`). Soft: PAP-74. Blocks PAP-115, PAP-116, PAP-117, PAP-119, PAP-120, PAP-121, PAP-123, PAP-124, PAP-132, PAP-85, PAP-74, {{spec-builder/spec-versioning}}.

**Agent**

Built by Quill (Page Spec Writer); reviewed by Atlas for architecture and Nova for codegen fit.

**Size**

M
"""

DESCRIPTIONS["PAP-115"] = """**Goal**

Ship the `paperos-spec` CLI and CI job that make specs mandatory: every route in an app has a valid `page.spec.yaml`, every reference inside a spec resolves, and a PR that breaks either rule turns gate 1 red with a precise annotation.

**Scope**

* In: `packages/spec/src/cli.ts` (`validate`, `routes`), the rule engine, core rules, baseline file, three output formats, watch mode, the library API, `docs/spec/validator.md`.
* Out: section-specific rules (added by PAP-116, PAP-119, PAP-121 through `defineRule`), codegen (PAP-120), fixing specs automatically beyond `--fix` renames.

**Spec**

* `paperos-spec validate [paths] [--format pretty | json | github] [--fix] [--baseline] [--strict] [--watch]`, `paperos-spec routes`; exit codes 0 clean, 1 errors, 2 warnings with `--strict`, 3 internal.
* Rules via `defineRule({ id, severity, check(ctx) })`, `ctx = { specs, app, routes, registry, git }`: `SPEC_PARSE`, `SPEC_ROUTE_UNCOVERED` (route under `apps/web/src/routes/_app/**` or `_public/**` lacking `staticData.spec`), `SPEC_ORPHAN`, `SPEC_DUP_ID`, `SPEC_DUP_ROUTE`, `SPEC_UNKNOWN_COMPONENT` (delegates to PAP-74 registry), `SPEC_UNKNOWN_ENTITY`, `SPEC_UNKNOWN_AUDIENCE` (against PAP-117), `SPEC_DANGLING_TRANSITION`, `SPEC_ACTION_UNBOUND`, `SPEC_BASELINE_GROWTH`, `SPEC_EDGE_TODO`.
* Routes read from TanStack `routeTree.gen.ts`; exemptions in `specs/.validator-ignore`.
* Baseline `specs/.validator-baseline.json` with an expiry date; growth requires label `spec-baseline`.
* Cache by content hash in `node_modules/.cache/paperos-spec`; 300 specs under 2 s.

**Interface contract**

* Provides: `validateSpecs(options): Promise<Report>` with `Report = { issues: SpecIssue[], stats, durationMs }`, `defineRule`, `RuleContext`, GitHub annotation output consumed by gate 1, `pnpm spec:validate`, JSON output schema `validator-report.schema.json`.
* Consumers: PAP-78 gate 1 job; PAP-116, PAP-119, PAP-121 register rules; PAP-118 and {{pm-linear/inbound-triage}} call the CLI with `--format json`; PAP-124 runs `validateSpecs` in a worker; PAP-122 reads `SPEC_EDGE_TODO`; PAP-81 spec-conformance reviewer reads the report.
* Requires: PAP-114 schema; PAP-74 `registry.json` (skip component rules with one warning if absent); PAP-117 app spec (entity and audience rules activate when present); PAP-78 job slot.

**Definition of done**

* Vitest per rule (pass and fail), CLI snapshots for three formats, exit-code tests.
* Seeded failing PR shows inline annotations on GitHub and Forgejo runs.
* Green run on `paperos-template` with the baseline; baseline expiry test fails after the date.
* Docs with every code, hint and fix; timing on 300 generated specs pasted; changelog; Linear comment with red and green run links.

**Test plan**

* Unit: each rule with fixtures; route discovery against a generated `routeTree.gen.ts`; ignore file; cache hit after no-op edit.
* Integration: CLI on the template repo; `--watch` reacts to a file change within 500 ms.
* e2e: gate 1 job on a seeded failing branch, both forges.
* Bench: 300-spec fixture set under 2 s (`hyperfine`).
* No UI breakpoints.

**Demo**

Delete the spec of one route and run `pnpm spec:validate --format pretty`: `SPEC_ROUTE_UNCOVERED` names the route file and the hint; restore it, run again, clean. Then `paperos-spec routes` lists coverage. One minute.

**Edge cases**

* Transition to another app: allowed only with `x-external: true`.
* Two specs on one route: `SPEC_DUP_ROUTE` with both files.
* Deleted route with `status: built`: error hinting `deprecated`.
* Symlinked spec folders in worktrees: real paths before dedupe.
* Registry missing: skip component rules with one warning, never crash.

**Dependencies**

Blocked by PAP-114. Soft: PAP-74, PAP-117, PAP-78. Blocks PAP-118, PAP-122, PAP-125.

**Agent**

Built by Quill (Page Spec Writer) with Sentinel pairing on CI wiring; reviewed by Atlas.

**Size**

M
"""

DESCRIPTIONS["PAP-116"] = """**Goal**

Finalise the `access` section so "who can see this page and do what" is written once in YAML and compiled losslessly into PAP-59 policies, SQL predicates and permission tests. Replace the draft adapter in the permission engine with this contract.

**Scope**

* In: Zod `AccessSection` in `packages/spec/src/schema/access.ts`, compiler `toPolicies()`, validator rules, `pnpm spec gen:policies`, `access-matrix` output, `docs/spec/access.md`.
* Out: the evaluator (PAP-59), audience definitions (PAP-55, PAP-117), the conformance tests (PAP-122 consumes the matrix).

**Spec**

* Shape: `public: boolean`, `view: AudienceId[]`, `actions: Record<name, { audiences[], condition? }>`, `rows: Record<entity, Condition>`, `deny: AudienceId[]`, `fields: Record<"entity.field", { view[] }>`, `inherit: boolean`.
* `Condition` imported from the shared filter grammar `@paperos/core/filter` (PAP-279) so identity, tables and specs share one tree (`all | any | not`, ops `eq | neq | in | contains | gte | lte | isNull`); depth limit 8.
* Semantics: `deny` beats everything; `view` grants `page.view`; an action grants only itself (warn if its audience lacks view); `rows` compile to predicates merged by PAP-119 and enforced by oRPC `authorize`; `public: true` grants `anonymous` and conflicts with `actor.*` references; `app.spec.yaml` `defaults.access` merges unless `inherit: false`.
* Output sorted and deterministic; `packages/permissions/src/generated/spec-policies.json` with `source: { specPath, line }` per policy.
* Rules: `ACCESS_UNKNOWN_AUDIENCE`, `ACCESS_ACTION_NAME` (`^[a-z][a-zA-Z0-9]*$`), `ACCESS_ATTR_UNAVAILABLE` (warn), `ACCESS_FIELD_ENTITY_MISSING`, `ACCESS_PUBLIC_ACTOR_REF`, `ACCESS_DEPTH`.

**Interface contract**

* Provides: `AccessSectionSchema`, type `AccessSection`, `toPolicies(page, app): Policy[]`, `accessMatrix(page, app): Matrix` (`audience x action -> boolean`), `pnpm spec gen:policies`, generated `spec-policies.json`.
* Consumers: PAP-59 loads `spec-policies.json` (its `from-spec.ts` draft is replaced); PAP-64 permission tests and PAP-122 conformance read `accessMatrix`; PAP-119 merges `rows`; PAP-120 emits `DeniedState` when `page.view` fails; PAP-124 access editor edits this shape.
* Requires: PAP-114 schema; PAP-59 `Policy` type (pinned branch import if not merged); PAP-279 `Condition`; PAP-55 and PAP-117 audience ids.

**Definition of done**

* Compile fixtures to expected `Policy[]` snapshots; wildcard expansion; inheritance; each rule pass and fail.
* Property test: `can()` from PAP-59 agrees with a naive reference evaluator on 500 random actor and action pairs for any valid section.
* Draft adapter replaced; its tests pass or are updated with reasons.
* Matrix committed for the three PAP-125 examples; docs; changelog; Linear comment with matrix and PR links.

**Test plan**

* Unit: compiler per feature, determinism (two runs byte-equal), condition depth, action name regex.
* Property (`fast-check`): compile then evaluate vs reference for random principals.
* Integration: `pnpm spec gen:policies` in the template repo, then PAP-59 loads the file and `can()` answers for the examples.
* No UI breakpoints; matrix rendered in the docs page at 1280 px.

**Demo**

Edit `customer-invoices.spec.yaml` to add `markPaid` for `staff.billing`, run `pnpm spec gen:policies && pnpm spec access-matrix customer-invoices` and read the matrix row flip from false to true; then `pnpm permissions explain --as staff.support --action page.action:markPaid` shows the denying line. One minute.

**Edge cases**

* Audience renamed in app spec: every page fails with file and line; `--fix` renames when `x-renamedFrom` is set.
* Staff audience referencing `actor.customerId`: warning.
* `public: true` with actions: allowed (pay-by-link); matrix marks them.
* Field rule for an entity missing from `data.entities`: error.
* Deeper than eight levels: error.

**Dependencies**

Blocked by PAP-114, PAP-59 (types), PAP-279 (`Condition`). Uses PAP-55, PAP-117. Blocks PAP-64, PAP-122.

**Agent**

Built by Quill (Page Spec Writer) with Forge (Schema Wright) on the compiler; reviewed by Sentinel (Security Auditor).

**Size**

M
"""

DESCRIPTIONS["PAP-117"] = """**Goal**

Define `specs/app.spec.yaml`, the single app-wide file holding audiences, navigation, entities, integrations, defaults and theme that page specs inherit from, so page specs stay short and the router, permission engine, canvas and search read app structure from one place.

**Scope**

* In: Zod `AppSpec` in `packages/spec/src/schema/app.ts`, merge precedence, `pnpm spec gen:app`, validator rules, `docs/spec/app-spec.md`, a populated template file.
* Out: business profile section (PAP-126 extends this file), connector registry content (PAP-121), navigation rendering (PAP-16 consumes).

**Spec**

* Shape: `app { id, name, tenantModel: multi | single, defaultLocale }`, `audiences[] { id, kind: customer | staff | partner | admin | agent | anonymous, label, extends?, segment? }` (shape agreed with PAP-55), `navigation: Record<audienceKind, NavItem[]>` (static routes only), `entities[] { id, table, label, plural, searchable, owner, fields? }`, `integrations[] { connector, mode }`, `defaults { layout, access, states }`, `theme`.
* Precedence: page beats app defaults; `inherit: false` clears; audience `extends` expands transitively with cycle detection.
* `gen:app` writes `apps/web/src/generated/app/{navigation,audiences,entities}.ts`; navigation items render through `useCan('page.view')` at runtime, never trusting the static list.
* Rules: `APP_SINGLE_FILE`, `APP_NAV_PARAM_ROUTE`, `APP_ENTITY_TABLE_MISSING` (against Drizzle schema when available), `APP_NAV_ORPHAN_PAGES` (warn), `APP_AUDIENCE_CYCLE`, `APP_DUP_AUDIENCE_LABEL` (warn), `APP_TENANT_ROWS_REDUNDANT` (warn).
* Merge for 500 entities under 100 ms, memoised by file hash.

**Interface contract**

* Provides: `AppSpecSchema`, types `AppSpec`, `AudienceId`, `EntityId`, `NavItem`, functions `loadAppSpec(root)`, `resolvePage(page, app): ResolvedPageSpec`, `expandAudience(id)`, generated navigation and entity modules, `pnpm spec gen:app`.
* Consumers: PAP-116 audience expansion, PAP-119 entity check, PAP-121 enabled connectors, PAP-123 start nodes per audience, PAP-16 navigation, PAP-59 `AudienceId` type, PAP-138 entity registration, PAP-126 `business:` extension, PAP-22 writes the file for new apps.
* Requires: PAP-114 schema. Soft: PAP-32 Drizzle schema for table checks, PAP-55 kinds, PAP-16 nav consumer.

**Definition of done**

* Vitest: parse fixture, precedence, `inherit: false`, audience expansion and cycle, each rule.
* `gen:app` outputs committed and drift-checked; router nav renders from generated navigation (screenshots at 375 and 1280 px for staff and customer audiences).
* Template ships a populated `app.spec.yaml` that validates.
* Docs; changelog; `AudienceId` imported by PAP-59 compiles; Linear comment with screenshots.

**Test plan**

* Unit: merge matrix (app default only, page only, both, `inherit: false`), expansion, rule fixtures.
* Bench: 500-entity fixture merge under 100 ms.
* Integration: `gen:app` then typecheck of the generated modules in `apps/web`.
* Visual: navigation rendered for two audiences at 375 and 1280 px through gate 3.

**Demo**

Add a `Reports` item under `navigation.staff`, run `pnpm spec gen:app`, reload the staff console and see the new item; sign in as a customer and it is absent. One minute.

**Edge cases**

* Nav route with params: rejected.
* Same label, different ids: warning.
* Entity table renamed by migration: blocks the PR until the spec updates.
* Audience with pages but empty navigation: warning listing routes.
* `tenantModel: single` with tenant row conditions: redundancy warning.

**Dependencies**

Blocked by PAP-114. Soft: PAP-32, PAP-55, PAP-16. Blocks PAP-126, PAP-28, PAP-123.

**Agent**

Built by Quill (Page Spec Writer); reviewed by Atlas and Forge (Schema Wright).

**Size**

S
"""

DESCRIPTIONS["PAP-118"] = """**Goal**

Give every character a repeatable way to turn a request into a validated page spec and a contract-valid Linear issue: interview the requester or read a brief, draft `page.spec.yaml`, run the validator until clean, commit on a branch, open a PR and the issue. This is how hundreds of specs get written without Justin editing YAML.

**Scope**

* In: `.claude/skills/author-spec/` (`SKILL.md`, `references/question-bank.md`, `templates/page.spec.yaml`, `scripts/{context,commit,open-issue}.ts`), listing in `skills.json` for Quill, Atlas and Nova, `docs/agents/skills.md` update.
* Out: freeform issue triage for humans ({{pm-linear/inbound-triage}} reuses this skill's scripts), the editor UI (PAP-124), the validator (PAP-115).

**Spec**

* Flow: `context.ts` prints audiences, entities, existing page ids and routes from the app spec so names are never invented; interview of at most 12 questions from the bank grouped by surface, skipped when the brief answers them; draft from the template; `paperos-spec validate --format json` with up to three fix rounds; `commit.ts` writes `specs/pages/<id>.spec.yaml` on branch `spec/<id>` with commit `spec(<id>): add page spec` and `Linear:` and `Character:` trailers (PAP-46), pushes, opens a PR (PAP-49); `open-issue.ts` creates "Build `<id>` page from spec" in contract format (PAP-93) with the spec link, labels and Size, idempotent by `spec:<id>` marker.
* Drafting rules: prefer registry components (PAP-74); every action has an access entry; every entity exists in the app spec; at least five edge cases across empty, huge, offline, denied, concurrent edit; field prose at most two sentences.
* Budget guard: abort after 40 turns leaving a `draft` spec and a comment.
* Every script's last stdout line is JSON `{ ok, specPath, prUrl?, issueUrl?, issues[] }`.

**Interface contract**

* Provides: skill id `author-spec` in `skills.json`, script CLIs `author-spec context`, `author-spec commit --id <id>`, `author-spec open-issue --id <id> [--parent PAP-n]`, the question bank as data (`question-bank.yaml` with `surface`, `section`, `question`, `skipIf`).
* Consumers: Quill, Atlas, Nova sessions; {{pm-linear/inbound-triage}} calls `open-issue` for issues that need a spec; PAP-125 uses the skill to write the fourth example; PAP-110 golden task for Quill.
* Requires: PAP-115 CLI, PAP-105 lint and `linear-update`, PAP-93 `validateIssue`, PAP-46 trailers, PAP-49 PR template, PAP-117 app spec (soft).

**Definition of done**

* Dry run from a brief ("customers list and pay invoices") produces a spec valid within two rounds, a PR and an issue (links in comment).
* Second dry run from Justin's pasted answers.
* Vitest for scripts: context output, trailer format, issue body passes `validateIssue`, idempotent re-run.
* Lint passes; listed in `skills.json`; docs updated; changelog; Linear comment with both transcripts.

**Test plan**

* Unit: question selection given a brief (skip logic), template rendering, `open-issue` idempotency against a mocked Linear search, trailer regex.
* Integration: full script chain against a temp git remote and `nock` Linear.
* e2e: two dry-run transcripts saved under `packages/agents/smoke/author-spec/`.
* No UI breakpoints.

**Demo**

Run `claude -p --agent quill "use author-spec: customers list and pay invoices"`; watch it ask at most a handful of questions, print the validator result, and end with a PR link and a Linear issue whose description has all contract sections. Two minutes.

**Edge cases**

* Brief needs a missing entity: stop and propose a data-layer issue, never invent a table.
* Validator package not built: build once, then fail loudly.
* Page id exists: offer update, set `status: draft`, note in `x-history`.
* Linear rate limit: `linear-update` writes to `artifacts/pending-comments/`.
* Interview reveals two pages: draft both and cross-link via `events`.

**Dependencies**

Blocked by PAP-115, PAP-105. Soft: PAP-93, PAP-46, PAP-49, PAP-117.

**Agent**

Built by Quill (Page Spec Writer) with Atlas (Decomposer) on the issue script; reviewed by Sentinel.

**Size**

M
"""

DESCRIPTIONS["PAP-119"] = """**Goal**

Finalise the `data` section so pages declare the entities, queries and mutations they need together with a sync mode, and a generator turns that declaration into typed React hooks backed by oRPC or Electric shapes. Agents stop hand-writing data plumbing and the spec stays the truth about what a page reads and writes. Umbrella for three children.

**Scope**

* Children (build in order):
  * {{spec-builder/data-section/schema}}: data section schema and validator rules.
  * {{spec-builder/data-section/generator}}: hook generator for server, live and local modes.
  * {{spec-builder/data-section/example}}: example page end to end with offline test.
* Out: the API and sync layers (PAP-35, PAP-36), table view models (PAP-161), server-side query compilation (PAP-163).

**Spec**

* Shape: `entities[]`, `queries: Record<name, { entity, filter: FilterTree, sort[], fields[], sync: live | local | server, page }>`, `mutations: Record<name, { entity, action: create | update | delete | custom, input, optimistic, audit }>`.
* `FilterTree` imported from `@paperos/core/filter` (PAP-279); no local copy.
* Access rows from PAP-116 are merged into every query filter as an `all` node at generation time; the server still enforces.
* Generated `apps/web/src/generated/<id>.data.ts`: `use<PascalCase(query)>()` returning `{ data, status, error, fetchNextPage, isStale }`, `use<PascalCase(mutation)>()` returning `{ mutate, mutateAsync, status }` with optimistic update and rollback; `server` uses TanStack Query and the PAP-35 client, `live | local` use `useShape` from PAP-36 with the offline outbox.
* Types resolved from the PAP-35 contract package so `fields` are checked at generation time; hook name collisions fail generation; files carry a banner and are drift-checked.

**Interface contract**

* Provides: `DataSectionSchema`, type `DataSection`, `pnpm spec gen:data [id] [--all] [--check]`, generated hooks, `dataStates` export for PAP-120, rules `DATA_UNKNOWN_ENTITY`, `DATA_UNKNOWN_FIELD`, `DATA_PARAM_UNBOUND`, `DATA_MUTATION_WITHOUT_ACCESS`, `DATA_UNSCOPED`.
* Consumers: PAP-120 imports hooks and `dataStates`; PAP-122 mocks `../generated/<id>.data`; PAP-123 derives `reads` and `writes` edges; PAP-124 form editor edits this shape; PAP-125 examples.
* Requires: PAP-114 schema, PAP-35 client and contract package (hard for `server`), PAP-279 `FilterTree`, PAP-116 rows, PAP-36 (`live | local`), PAP-38 audit `reason` field.

**Definition of done**

* All three children Done.
* Umbrella: `customer-invoices` hooks render a list from seeded Postgres in Playwright at 375 and 1280 px; a mutation appears in a second browser context within 1 s in `live` mode; offline mutation queues and applies on reconnect.
* `docs/spec/data.md`; drift check in gate 1; changelog; Linear comment with screenshots and the generated file.

**Test plan**

* Umbrella e2e (Playwright): two contexts, `context.setOffline`, list render at 375 and 1280 px.
* Generator snapshots for all three modes (child 2); rule fixtures (child 1).
* Visual: the example list at 375 and 1280 px in light and dark through gate 3.

**Demo**

Add a `sort` to the `invoices` query in the example spec, run `pnpm spec gen:data customer-invoices`, open the page and see the order change; toggle the browser offline, mark an invoice paid, go online and watch it sync. Two minutes.

**Edge cases**

* Unscoped query on a tenant table: generator injects tenant scope; warning if no access row.
* `page` above 200: capped with warning; hook paginates.
* Field renamed in Drizzle: generation fails, not runtime.
* `sync: live` without a registered shape: falls back to `server` with a warning.
* Route param type mismatch: validator error from `validateSearch` types.

**Dependencies**

Blocked by PAP-114, PAP-35, PAP-279. Soft: PAP-36, PAP-116, PAP-38. Consumed by PAP-120, PAP-122.

**Agent**

Built by Forge (Schema Wright) for the generator with Quill (Page Spec Writer) on the schema; reviewed by Sentinel.

**Size**

L (umbrella; children S, M, M)
"""

DESCRIPTIONS["PAP-120"] = """**Goal**

Turn a validated page spec into a working page skeleton: the TanStack route file, layout slot wiring, the component tree as JSX bound to real design-system components, and loading, empty, error, offline and denied states. An agent building a page starts from a rendering scaffold and only writes logic. Umbrella for three children.

**Scope**

* Children (build in order):
  * {{spec-builder/layout-codegen/templates}}: codegen templates and two-file ownership rules.
  * {{spec-builder/layout-codegen/wiring}}: state wiring, slot mapping and event binding.
  * {{spec-builder/layout-codegen/examples}}: example specs generated, screenshotted and conformance-tested.
* Out: business logic, data hooks (PAP-119), design decisions, non-React targets, i18n of copy ({{spec-builder/spec-i18n}}).

**Spec**

* `pnpm spec gen:page <id> [--all] [--check] [--force]` produces the route file (created once), `generated/pages/<id>.view.tsx` (always regenerated), `pages/<id>.logic.ts` (created once, typed stubs per `logic.actions`), and `<id>.stories.tsx` (one story per state).
* Components resolve through `resolveComponent()` from PAP-74; every element gets `data-spec-key`; `events` bind to `actions.<name>`; state components come from PAP-234 (`ErrorState`, `DeniedState`, `OfflineBanner`, `IntegrationUnavailable`, `LoadingPage`) and PAP-71 (`EmptyState`, `Skeleton`).
* Templates are type-checked TypeScript functions with a `Printer` for indentation and import dedupe; Biome formats output; generation is deterministic and the banner carries the spec hash for `--check`.
* Layout templates map to PAP-16 shells; unknown slots fail; search params from `data` filters produce a Zod `validateSearch`.

**Interface contract**

* Provides: `generatePage(spec, registry, options): GeneratedFiles`, the CLI, `data-spec-key` attribute convention, `data-action` attribute on event-bound elements (used by PAP-64 and PAP-122), the two-file ownership rule documented in `docs/spec/codegen.md`, `MissingComponent` dev fallback.
* Consumers: PAP-105 `page-from-spec` skill, PAP-122 (`data-spec-key`), PAP-124 preview compiles templates in-browser, PAP-125 examples, PAP-29 new-app drill, PAP-126 regenerates on terminology change.
* Requires: PAP-114 schema, PAP-74 registry and resolver (hard), PAP-234 state components, PAP-16 slot API, PAP-119 hooks (stubs otherwise), PAP-59 `useCan`.

**Definition of done**

* All three children Done.
* Umbrella: the three PAP-125 example specs generate, typecheck, render; generating a page then running PAP-122 passes with zero manual edits; screenshots of each state at 320, 375, 768, 1024, 1280, 1536 and 1920 px in light and dark; Storybook stories deployed.
* Docs including the two-file pattern; changelog; Linear comment with screenshots and story links.

**Test plan**

* Umbrella integration: generate all examples twice, assert byte-identical output; typecheck `apps/web`; run conformance suites.
* Visual: seven-width matrix per state through gate 3, both themes.
* e2e: Playwright loads each example route and asserts `data-spec-key` presence for the success state.

**Demo**

Run `pnpm spec gen:page customer-invoices`, open the route and see the table scaffold with an empty state; edit `states.empty.copy` in the spec, regenerate, reload: the copy changes and the logic file is untouched. Ninety seconds.

**Edge cases**

* Component `key` renamed: view regenerates; logic keeps the old handler with `// TODO(unused)`.
* Route file exists with another `staticData.spec`: abort with the conflict.
* Tree deeper than 12: warning.
* `kiosk` template before PAP-23 exists: falls back to `focus` with warning.
* Biome unavailable: unformatted output with warning; drift check formats before compare.

**Dependencies**

Blocked by PAP-114, PAP-74, PAP-234. Soft: PAP-119, PAP-16, PAP-59. Blocks PAP-29, {{spec-builder/spec-i18n}}.

**Agent**

Built by Nova with Iris (Component Crafter) on component emit; reviewed by Sentinel (spec-conformance).

**Size**

L (umbrella; children M, M, S)
"""

DESCRIPTIONS["PAP-121"] = """**Goal**

Finalise the `integrations` section so a page declares which external systems and capabilities it touches, backed by a connector registry that knows each connector's auth, env vars, MCP server, modes and limits. Validation catches pages using connectors the app has not enabled, env-config knows which secrets to require, and the canvas can draw external systems.

**Scope**

* In: Zod `IntegrationsSection`, connector registry built from `packages/spec/integrations/*.connector.yaml`, eleven connector files, validator rules, mode narrowing, generated `integrations.json`, `docs/spec/integrations.md`.
* Out: connector implementations (`packages/integrations/<id>` owned by consuming projects), MCP server catalogue content (PAP-210), automation triggers (PAP-174 consumes).

**Spec**

* Page shape: `integrations[] { connector, capabilities[], mode: live | test | mock, onFailure: degrade | block | queue }`.
* Connector file: `{ id, name, docsUrl, mcpServer, auth: { kind: apiKey | oauth | webhook, envVars[] }, capabilities[] { id, description, scope, rateLimit, maps: sdkCall | mcpTool }, modes[], webhooks[], mock?, owner, deprecated? }`; seeded for `stripe`, `linear`, `notion`, `google-drive`, `webflow`, `miro`, `gamma`, `resend`, `twilio`, `github`, `forgejo`.
* Capability ids `<area>.<verbNoun>`; `mode: mock` requires a mock module; app-level mode is the default and a page may only narrow (`live` app allows `test` page, not the reverse); registry build fails on duplicate capability ids or colliding env var names.
* `onFailure` drives PAP-120 wiring: `degrade` renders `IntegrationUnavailable` (PAP-234), `block` shows the error state, `queue` defers via PAP-148 with a pending badge.
* Rules: `INT_UNKNOWN_CONNECTOR`, `INT_UNKNOWN_CAPABILITY`, `INT_NOT_ENABLED`, `INT_MODE_WIDENING`, `INT_MOCK_MISSING`, `INT_DEPRECATED` (warn, error after date), `INT_DUP_CONNECTOR` (warn).

**Interface contract**

* Provides: `IntegrationsSectionSchema`, `ConnectorSchema`, `registry: Record<ConnectorId, Connector>`, `requiredEnvVars(app, pages): string[]`, generated `integrations.json`, `pnpm spec gen:integrations`.
* Consumers: PAP-17 env-config boot check (`requiredEnvVars`), PAP-120 wiring, PAP-123 external nodes and inbound webhook edges, PAP-106 (MCP server ids per character cross-check), PAP-174 triggers, PAP-177 Stripe billing pages, PAP-193 landing forms, PAP-15 forces `mock` in Pages builds.
* Requires: PAP-114 schema, PAP-210 catalogue (start from the plan's list if not merged), PAP-117 app-level `integrations`.

**Definition of done**

* Vitest: schema fixtures, registry build, each rule, narrowing logic, generated JSON snapshot.
* Eleven connector files cross-checked against the PAP-210 catalogue (reviewer confirms).
* CI test: enabling `stripe` in `live` mode without `STRIPE_SECRET_KEY` fails boot with the variable named.
* `customer-invoices` runs in `mock` mode in Playwright with a mocked Stripe checkout; screenshots at 375 and 1280 px.
* Docs; changelog; Linear comment with catalogue link.

**Test plan**

* Unit: rules with fixtures, narrowing matrix (app x page modes), env var collision detection, deprecation date logic with fake clock.
* Integration: registry build from the eleven files; `requiredEnvVars` against the template app.
* e2e: example page in mock mode at 375 and 1280 px.
* Visual: `IntegrationUnavailable` degrade state screenshot at 375 and 1280 px.

**Demo**

Set the app-level `stripe` mode to `test` and a page to `live`, run `pnpm spec:validate` and read `INT_MODE_WIDENING`; then run the example in mock mode and click "Pay" to see the mocked checkout. One minute.

**Edge cases**

* Connector deprecated: warning until the date, then error with `replaceWith`.
* Capability missing from a connector: error hinting a PAP-210 issue.
* Connector listed twice on a page: merged with warning.
* Preview deploy: forced `mock` recorded in generated JSON.
* Webhook-only connector on a page: allowed; canvas draws an inbound edge.

**Dependencies**

Blocked by PAP-114, PAP-210. Soft: PAP-117, PAP-17, PAP-106. Blocks PAP-174.

**Agent**

Built by Quill (Page Spec Writer) with Scout (Library Evaluator) on connector facts; reviewed by Sentinel (Security Auditor) for env handling.

**Size**

M
"""

DESCRIPTIONS["PAP-122"] = """**Goal**

Derive tests from specs automatically so a page that drifts from its spec fails gate 1 without anyone writing a test: the access matrix is checked against the permission engine, required components and states are asserted in a render, routes are verified and edge cases become tracked stubs. Spec drift becomes a red build, not a review comment.

**Scope**

* In: `pnpm spec gen:tests [id] [--all]` writing Vitest conformance files and Playwright route suites, actor fixtures, `reports/spec-conformance.json`, `docs/spec/conformance.md`.
* Out: hand-written page tests (live beside the logic file), visual baselines (PAP-82), reviewer prompts (PAP-81).

**Spec**

* Unit file `apps/web/src/generated/__tests__/<id>.conformance.test.tsx` (Vitest 3, Testing Library 16, jsdom): render the view for every `states` entry with mocked hooks and assert the state component and copy; assert every `components[].key` via `data-spec-key` in the success state (unless `optional: true`); assert every `events[].to` exists in `routeTree.gen.ts`; access matrix from PAP-116 `accessMatrix` evaluated with PAP-59 `can()` for every audience and action; denied state asserts no data hook call; `edgeCases[]` with `test: unit` become `it.todo` or import a named test from `pages/<id>.edge.test.ts`.
* Playwright file `apps/web/e2e/generated/<id>.routes.spec.ts`: for two audiences per page, log in via PAP-240 `login-as`, load the route at 375 and 1280 px, assert the success or denied state.
* Actor fixtures `packages/permissions/fixtures/<audience>.json` generated from the app spec; hooks mocked with `vi.mock('../generated/<id>.data')`.
* `status: draft` pages generate `describe.skip` with a reason; `SPEC_EDGE_TODO` blocks `status: built` with open unit todos.

**Interface contract**

* Provides: `pnpm spec gen:tests`, generated files (never hand-edited), `reports/spec-conformance.json` (`{ pages: [{ id, passed, failed, todos, matrixChecks }] }`) uploaded as a gate artifact per PAP-239, the `pages/<id>.edge.test.ts` naming convention for imported edge tests.
* Consumers: PAP-78 gate 1 test job, PAP-97 status comment (conformance section), PAP-81 spec-conformance reviewer, PAP-64 (matrix checks feed its report), PAP-125 examples, PAP-102 and PAP-113 page specs.
* Requires: PAP-115 report, PAP-78 job and drift, PAP-116 matrix, PAP-59 `can()`, PAP-120 `data-spec-key`, PAP-240 login fixtures, PAP-239 artifact schema.

**Definition of done**

* Snapshots of generated tests for minimal and maximal fixtures; a mutated spec (removed component, changed audience) makes the generated test fail in a seeded PR.
* Three example pages produce green suites; total under 20 s.
* Playwright route suite runs for two audiences per page at 375 and 1280 px.
* `reports/spec-conformance.json` appears in a Linear status comment; docs; changelog; Linear comment with green and red run links.

**Test plan**

* Unit: generator snapshots; matrix evaluation both branches of resource conditions; optional components; draft skip.
* Integration: run generated suites for the examples in CI; sharding across the matrix.
* e2e: generated Playwright suites at 375 and 1280 px against test-mode seeds.
* Visual: none beyond the route suite's success and denied screenshots.

**Demo**

Remove the `invoiceTable` component from the example spec's `components`, run `pnpm spec gen:tests customer-invoices && pnpm vitest run customer-invoices`: the presence assertion fails naming the key; restore and rerun green. One minute.

**Edge cases**

* `public: true`: anonymous fixture, login skipped.
* Conditionally rendered component: `optional: true` excludes it.
* Resource-dependent access: representative fixture per condition branch.
* Hundreds of pages: files independent, sharded.
* Edge-case id renamed: orphaned test becomes a todo with a warning.

**Dependencies**

Blocked by PAP-115, PAP-78. Uses PAP-116, PAP-59, PAP-120, PAP-240, PAP-239. Blocks PAP-64.

**Agent**

Built by Sentinel (Code Reviewer sub-agent as builder) with Quill on docs; reviewed by Atlas.

**Size**

M
"""

DESCRIPTIONS["PAP-123"] = """**Goal**

Compile every page spec plus `app.spec.yaml` into one UX-flow graph (pages, transitions, audiences, entities, external systems) with deterministic layout positions, so the canvas view opens an accurate map of the whole app and updates whenever specs change. Specs draw the map; nobody maintains a diagram by hand.

**Scope**

* In: `buildFlowGraph()` in `packages/spec/src/graph/build.ts`, Zod `FlowGraph`, ELK layout, audience reachability, flags, `pnpm spec gen:graph [--diff]`, `docs/spec/flow-graph.md`, a temporary dev route if PAP-132 is not merged.
* Out: canvas rendering and interaction (PAP-132), thumbnails production (PAP-82), the org chart (PAP-113 reuses the loader pattern).

**Spec**

* `nodes[] { id, type: page | external | entity | start, label, route?, surface?, audiences[], layoutTemplate?, status, specPath, thumbnail?, flags[], position }`, `edges[] { id, from, to, kind: navigate | mutation | integration | reads | writes, on?, guard?, audiences[], back?, count? }`, `groups[] { id, kind: surface | navSection, label, nodeIds[] }`, `meta { app, generatedAt, specHash }`.
* Derivation: `events[]` produce `navigate`; `data.queries` produce `reads`, `data.mutations` produce `writes` (collapsed per page and entity with counts); `integrations[]` produce `integration` edges to `ext:<connector>`; navigation roots produce `start:<audience>` edges.
* Stable ids `page:<id>`, `entity:<id>`, `ext:<connector>`, `start:<audience>`; positions keyed by id so manual overrides survive.
* Layout with `elkjs` 0.9 layered, direction right, groups as compound nodes, fixed options and sorted node order for determinism; 300 pages under 5 s.
* Flags: `unreachable`, `deadEnd`, `orphan` (entity with no page), listed in the PR comment; audiences precomputed from `access.view` and guards.

**Interface contract**

* Provides: `FlowGraphSchema`, type `FlowGraph`, `buildFlowGraph(specs, app)`, `diffGraphs(a, b): GraphDiff`, `apps/web/src/generated/flow-graph.json`, node and edge types shared in `packages/collab/canvas/types.ts` (agreed with PAP-132 first).
* Consumers: PAP-132 canvas loader, PAP-124 Graph tab (neighbourhood query `subgraph(graph, pageId, depth)`), PAP-113 loader pattern, PAP-97 PR comment diff summary, PAP-138 search (page and entity index).
* Requires: PAP-114 and PAP-117 (hard), PAP-121 for external nodes (soft), PAP-82 thumbnails (soft), PAP-132 type agreement.

**Definition of done**

* Vitest: edge derivation per kind, reachability, flags, stable ids, layout determinism, diff output.
* Graph generated for the template examples and rendered in PAP-132 (screenshots at 1280 and 1920 px) or the temporary React Flow route.
* PR comment shows the diff summary on a seeded spec change.
* Docs; drift job in gate 1; changelog; Linear comment with screenshots.

**Test plan**

* Unit: fixtures for each derivation rule; cycle marks `back: true`; collapse counts; orphan and dead-end detection.
* Determinism: build twice, deep-equal; bench 300-page fixture under 5 s.
* Integration: `gen:graph --diff` between two fixture sets produces the expected summary.
* Visual: rendered graph at 1280 and 1920 px in both themes.

**Demo**

Add a transition from the invoices page to a new `invoice-detail` spec, run `pnpm spec gen:graph --diff`, read "1 node, 1 edge added", open the canvas and see the new page connected. One minute.

**Edge cases**

* Cyclic navigation: `back` edges styled differently.
* Fifty audiences on one page: ids only.
* `x-external` transition: external node labelled with the app id.
* Thousands of `reads` edges: collapsed with counts.
* Thumbnail expired: field omitted; canvas placeholder.

**Dependencies**

Blocked by PAP-114, PAP-117 and, per the current plan edge, PAP-132 (the canvas). In practice PAP-132 consumes this graph, so agree `packages/collab/canvas/types.ts` in the first day and ship the dev-route fallback; the audit recommends flipping that edge. Soft: PAP-121, PAP-82.

**Agent**

Built by Nova (Canvas Cartographer); reviewed by Quill for spec fidelity.

**Size**

M
"""

DESCRIPTIONS["PAP-124"] = """**Goal**

Let Justin and agents edit page specs inside PaperOS: a form view for people who do not want YAML, a YAML view with live validation for those who do, and a preview of the generated page and its place in the flow graph. Saving opens a PR, so the repo stays the source of truth. Umbrella for three children.

**Scope**

* Children (build in order, 2 and 3 can run in parallel after 1):
  * {{spec-builder/spec-editor-ui/yaml}}: spec list, YAML editor with worker validation, and save-to-PR flow.
  * {{spec-builder/spec-editor-ui/form}}: form view, component tree editor and two-way sync.
  * {{spec-builder/spec-editor-ui/preview}}: preview, graph tab, keyboard and accessibility polish.
* Out: multiplayer editing of one spec, a drag-and-drop page builder, editing `app.spec.yaml` (read-only viewer).

**Spec**

* Routes `/_app/dev/specs` and `/_app/dev/specs/$id`, surface `developer | staff`, access `staff.admin` write, `agent.*` read.
* Layout via PAP-70 `SplitPane`: left tabs Form and YAML, right tabs Preview, Graph, Issues.
* Save: oRPC `specs.save({ id, yaml, message, baseSha })` writes on branch `spec/<id>` through the Forgejo API, commits with trailers and opens or updates a PR; optimistic locking returns `CONFLICT` with a three-way diff; drafts autosave to `localStorage`.
* Diagnostics keyed by `path` render in Issues, as YAML gutter markers and as inline form messages.
* Keyboard `Cmd/Ctrl+S` save, `Cmd/Ctrl+Shift+V` toggle view via PAP-151; unsaved-changes guard; `spec_editor.save` audit event (PAP-38).

**Interface contract**

* Provides: page specs `specs/dev/spec-list.spec.yaml`, `spec-editor.spec.yaml`; procedures `specs.list()`, `specs.get(id)`, `specs.save(...)`, `specs.validate(yaml)` (server fallback for the worker); component `SpecForm` in `apps/web/src/features/specs/`; event `spec.saved { id, prUrl }`.
* Consumers: Justin; Quill sessions for spec edits; PAP-126 business profile editing later; PAP-131 comments anchor on `data-spec-key` in the preview.
* Requires: PAP-114 schema, PAP-70 layout (hard), PAP-115 `validateSpecs` library API, PAP-120 templates for preview, PAP-74 registry, Forgejo API client (PAP-276 or direct), PAP-123 subgraph, PAP-151, PAP-165 grid (soft).

**Definition of done**

* All three children Done.
* Umbrella e2e: open example spec, edit title in Form, YAML updates, break YAML, see diagnostic, fix, save, PR link appears (mocked Forgejo in CI); screenshots at 768, 1024, 1280, 1536 and 1920 px in light and dark; 320 and 375 px show read-only YAML with a "desktop recommended" notice.
* axe clean on both tabs; keyboard-only flow recorded (PAP-83 flow file).
* Justin edits one real spec and the PR merges; docs; changelog; Linear comment with preview link and video.

**Test plan**

* Umbrella e2e (Playwright) as above at 375, 768 and 1280 px.
* Round-trip test: Form edits patch the `yaml` Document so comments and `x-*` keys survive (child 2).
* Visual: five desktop widths plus two phone widths through gate 3.

**Demo**

Open `/_app/dev/specs/customer-invoices`, change the title in the form and watch the YAML tab update, type an invalid `surface` in YAML and see the gutter error, fix it, press `Cmd+S` and click the PR link. Two minutes.

**Edge cases**

* YAML with comments and anchors: Document patching preserves them.
* Registry component removed: node shows a warning with a replace action.
* 300-component spec: virtualised tree; preview compile capped at 5 s with an outline fallback.
* Offline: editing continues, save disabled with reason, draft kept.
* Worker crash: "validation unavailable", saving requires explicit confirm.

**Dependencies**

Blocked by PAP-114, PAP-70. Soft: PAP-115, PAP-120, PAP-123, PAP-74, PAP-151, PAP-165, PAP-276.

**Agent**

Built by Nova with Iris (Component Crafter) on forms; reviewed by Sentinel (Visual Inspector) and Quill.

**Size**

L (umbrella; children M, M, M)
"""

DESCRIPTIONS["PAP-125"] = """**Goal**

Document the spec builder end to end and ship three fully specified, generated and screenshotted example pages (customer invoice list, staff dashboard, agent console) that agents copy when writing new specs. The examples are executable: they validate, generate, pass conformance and render in the template app.

**Scope**

* In: `specs/pages/examples/{customer-invoices,staff-dashboard,agent-console}.spec.yaml` with explanatory comments under 150 lines each, their generated artifacts committed, `docs/spec/` pages (`workflow.mdx`, `page-spec`, `app-spec`, `access`, `data`, `integrations`, `codegen`, `conformance`, `flow-graph`, `editor`, `faq`, glossary) with `_meta.yaml` reading order.
* Out: the generators themselves, docs engine features (PAP-128), the authoring skill (PAP-118, exercised here).

**Spec**

* `customer-invoices`: surface customer, live query on `invoice`, `payInvoice` via Stripe in mock mode, five edge cases. `staff-dashboard`: `ui.dashboardBlocks` (PAP-173) or `ui.responsiveGrid` fallback, three aggregate queries, `staff.*` wildcard access with a condition. `agent-console`: lists prompt sessions from PAP-129, actions for `agent.builder` and `staff.admin`, `deny` customers, offline and denied states.
* Docs use the PAP-128 frontmatter and `<FileRef path lines>` includes so code never goes stale; `pnpm docs:lint` fails on missing paths; screenshots come from Playwright artifacts stored under `docs/spec/examples/<id>/` in light and dark.
* Language: second person, short sentences, one concept per heading; glossary defines spec, surface, audience, slot, state, transition; FAQ entries cite the spec version.
* Examples live under the `examples/` namespace and `/_app/examples/*` routes, excluded from production navigation; seeds use fixed dates.

**Interface contract**

* Provides: the three example specs as the canonical copy sources, `docs/spec/workflow.mdx` as the single onboarding page for spec writers, `docs/spec/examples/<id>/{access-matrix.md, flow-graph.json, *.png}`, glossary anchors linked from validator hints (`docs/spec/validator.md#<code>`).
* Consumers: PAP-105 `page-from-spec` and PAP-118 `author-spec` reference `workflow.mdx`; PAP-116, PAP-120, PAP-122 use the examples as fixtures; PAP-24 template docs link here; PAP-110 Quill golden task; PAP-29 drill.
* Requires: PAP-115 (hard); PAP-120, PAP-119, PAP-122, PAP-116, PAP-128, PAP-82 expected but each has a documented fallback.

**Definition of done**

* Three examples pass `paperos-spec validate --strict`, `gen:page`, `gen:data`, `gen:tests` and their suites in CI.
* Screenshots of each example in success, empty and denied states at 375 and 1280 px, light and dark, embedded.
* Docs render in the docs engine or Pages fallback with working includes and zero lint errors.
* A fresh session given only `workflow.mdx` writes a valid spec for a fourth page in one attempt (transcript linked).
* Changelog; Linear comment with docs link, screenshots and transcript.

**Test plan**

* Unit: docs lint (paths, frontmatter, glossary anchors), line-count limit on examples.
* Integration: full generator chain on the examples in CI as part of the drift job.
* e2e: Playwright captures the nine state screenshots per theme.
* Visual: docs pages at 375 and 1280 px; example pages at 375 and 1280 px through gate 3.

**Demo**

Open `docs/spec/workflow.mdx`, follow its five steps against `staff-dashboard`, then run `pnpm spec:validate --strict specs/pages/examples` and open `/_app/examples/staff-dashboard` in the template app to see the generated page. Two minutes.

**Edge cases**

* Dependency not merged (dashboard blocks): fallback component with a callout naming the blocking key.
* Generators change: examples are in the drift job, so generator PRs regenerate them.
* Docs engine unavailable: same MDX builds to Pages with a minimal Vite MDX setup.
* Example ids collide with real pages later: namespaced routes.
* Screenshot flake from dates: fixed seeds.

**Dependencies**

Blocked by PAP-115. Soft: PAP-116, PAP-119, PAP-120, PAP-122, PAP-128, PAP-82.

**Agent**

Built by Quill (Page Spec Writer, Changelog Scribe); reviewed by Nova for codegen accuracy and Sentinel for test claims.

**Size**

M
"""

DESCRIPTIONS["PAP-126"] = """**Goal**

"One-size-fits-all software that adapts to every type of business" needs a place where the adaptation is declared. Add a `business:` section to `app.spec.yaml` with an industry taxonomy, a terminology map that renames core concepts (customer becomes patient, guest, client, member, student) across UI strings, navigation, view headers, notification templates and agent prompts, plus locale, currency, tax regime and enabled modules. The migration agent fills it in; codegen and templates read it.

**Scope**

* In: schema extension in `packages/spec/src/schema/app.ts`, `packages/spec/src/industries.yaml` (40 industries with subtypes, defaults), terminology helper in `packages/i18n`, `useBusinessProfile()`, `pnpm spec business:apply <profile>`, validator rules, ADR, `docs/spec/business-profile.md`.
* Out: seed pack contents (PAP-207), the interview (PAP-208), tax calculation (PAP-182), module semantics (PAP-28).

**Spec**

* `business { industry, subtype?, secondaryIndustries[], audiences[] { id, kind, label, plural }, terminology: Record<CoreTerm, { singular, plural }>, locale { default, enabled[], timezone }, currency { default, enabled[] }, taxRegime: us-sales-tax | vat | gst | none, modules[], compliance[] }`.
* `CoreTerm` is a closed set of 30 concepts (`customer`, `order`, `product`, `service`, `staff`, `location`, `appointment`, `invoice`, `project`, `task`, ...); unknown keys fail.
* `t.term('customer', { plural: true })` resolves through PAP-27 catalogs; changing terminology is a spec change that regenerates pages (PAP-120) and is reviewed like any spec change.
* Taxonomy and defaults are data: adding an industry is a YAML PR; secondary industries merge modules and terminology with explicit conflict resolution.
* Rules: `BIZ_UNKNOWN_INDUSTRY`, `BIZ_UNKNOWN_TERM`, `BIZ_INVALID_CURRENCY`, `BIZ_UNKNOWN_AUDIENCE`, `BIZ_TERM_COLLISION` (warn), `BIZ_MODULE_UNKNOWN` (against PAP-264 registry).

**Interface contract**

* Provides: `BusinessProfileSchema`, type `BusinessProfile`, `CoreTerm`, `industries.yaml` with `IndustrySchema`, `useBusinessProfile()`, `t.term()`, `pnpm spec business:apply <industry | generic>`, generated `apps/web/src/generated/app/business.ts`.
* Consumers: PAP-120 labels and empty-state copy, PAP-16 navigation labels, PAP-165 column headers, PAP-136 templates, PAP-104 prompts (terminology fragment), PAP-207 seed packs declare `industry`, PAP-208 interview writes the profile, PAP-175 and PAP-182 read `currency` and `taxRegime`, PAP-124 edits it later.
* Requires: PAP-117 app spec (hard), PAP-28 and PAP-264 module registry, PAP-27 catalogs. Soft: PAP-120, PAP-207, PAP-208.

**Definition of done**

* Switching the template between clinic and agency profiles by editing `app.spec.yaml` alone changes navigation labels, table headers, empty states and notification templates (before and after screenshots at 375 and 1280 px in `en` and `es`).
* Validator catches unknown audience, term and currency.
* `business:apply clinic` produces a valid profile; PAP-208 writes an equivalent one in a recorded run.
* Five seed packs declare their industry; docs, ADR, changelog; Linear comment. Justin reviews industries and defaults in the same `Needs Justin` item PAP-207 files (one item).

**Test plan**

* Unit: schema and rules, term resolution with plural and locale, secondary-industry merge conflicts, `generic` profile validity.
* Integration: `business:apply` then `gen:page` for the examples; snapshot of generated labels.
* e2e: Playwright switches profiles and asserts the nav label text at 375 and 1280 px.
* Visual: before and after screenshots in two locales through gate 3.

**Demo**

Run `pnpm spec business:apply clinic && pnpm spec gen:page --all`, reload the staff console: "Customers" now reads "Patients" in navigation, table headers and the empty state; switch to `agency` and it reads "Clients". Ninety seconds.

**Edge cases**

* Gym with a cafe: `secondaryIndustries` with explicit conflict resolution.
* Two terms mapping to one label: warning; codegen disambiguates.
* Case-inflected plurals: base term in the map; catalogs carry full forms.
* Non-profit `taxRegime: none`: tax fields hidden, ledger kept.
* Pre-existing apps: `business:apply generic` fills a neutral profile.

**Dependencies**

Blocked by PAP-117, PAP-28, PAP-27. Soft: PAP-120, PAP-124, PAP-207, PAP-208, PAP-175, PAP-182.

**Agent**

Written by Quill (Page Spec Writer) with Scout (Library Evaluator) on the taxonomy; reviewed by Atlas and Ledger for finance fields.

**Size**

M
"""
