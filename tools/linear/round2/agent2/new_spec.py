"""New issues for spec-builder: 2 gap issues and 9 children (PAP-119, PAP-120, PAP-124)."""
P = "spec-builder"
GAPS = []
CHILDREN = {}

GAPS.append({
"key": "spec-builder/spec-i18n",
"title": "Add spec-level internationalisation: message IDs for spec copy fields, extraction into catalogs, pseudo-locale validation rule",
"phase": "P2", "type": "Build", "priority": 3, "surfaces": ["Developer"],
"milestone": "Spec editor UI", "state": "Backlog",
"blockedBy": ["PAP-27", "PAP-120"], "blocks": [],
"description": """**Goal**

Stop codegen from baking English into every generated app: copy fields in specs (`states.*.copy`, `purpose.summary` shown to users, navigation labels, component `props` marked as text, terminology from PAP-126) get message ids, an extractor writes them into the PAP-27 catalogs, generated pages render through `t()`, and a pseudo-locale validation rule catches hard-coded strings.

**Scope**

* In: `x-i18n` conventions in `PageSpecSchema` and `AppSpecSchema` (`copy` accepts a string or `{ id, default }`), `pnpm spec gen:messages`, catalog writer for `packages/i18n`, codegen changes in PAP-120 templates to emit `t('<id>')`, validator rules, pseudo-locale test in gate 3.
* Out: translation itself, runtime locale switching (PAP-27), terminology semantics (PAP-126).

**Spec**

* Message id derivation: `<specId>.<path>` (for example `customer-invoices.states.empty.copy`), overridable with `{ id }`; ids stable across regenerations; `default` is the source-locale text.
* Text-bearing props: the PAP-74 registry marks props `i18n: true` (`label`, `placeholder`, `title`, `description`); codegen wraps only those.
* Extractor writes `packages/i18n/messages/<locale>/spec.json` for the default locale, merges without dropping human edits, marks removed ids `obsolete`.
* Rules: `I18N_HARDCODED` (string copy without id when `app.i18n.strict` is true; warning otherwise), `I18N_DUP_ID`, `I18N_OBSOLETE` (warn).
* Pseudo-locale `en-XA` (accented, 30 percent longer) generated automatically; gate 3 screenshots one example page in `en-XA` at 375 and 1280 px to expose truncation.

**Interface contract**

* Provides: `MessageRef = string | { id: string; default: string }` type, `extractMessages(specs, app): Catalog`, `pnpm spec gen:messages`, rule ids above, `pseudoLocale()` helper, `spec.json` catalog namespace.
* Consumers: PAP-120 templates (`t()` emission), PAP-27 loader (namespace `spec`), PAP-126 terminology (`t.term` ids), PAP-124 form shows id and default side by side, PAP-82 pseudo-locale screenshots, PAP-136 templates reuse ids for notification copy.
* Requires: PAP-27 catalogs and `t()`, PAP-120 templates, PAP-74 `i18n` prop flags (soft; defaults to the four known props).

**Definition of done**

* Three example pages emit zero literal user-facing strings (grep test on generated views).
* `gen:messages` produces a catalog; a second run is a no-op; removing a state marks its id `obsolete`.
* Pseudo-locale screenshots of `customer-invoices` at 375 and 1280 px show no truncation after fixes.
* `docs/spec/i18n.md`; changelog; Linear comment with screenshots.

**Test plan**

* Unit: id derivation stability, merge preserving edits, rule fixtures, pseudo-locale transform.
* Integration: codegen snapshot with `t()` calls; catalog round trip through PAP-27 loader.
* e2e (Playwright): example page rendered in `en-XA` at 375 and 1280 px.
* Visual: two widths through gate 3 in the pseudo-locale.

**Demo**

Set `app.i18n.strict: true`, run `pnpm spec:validate` to see `I18N_HARDCODED` on a literal, replace it with `{ id, default }`, run `gen:messages`, switch the app to `en-XA` and see the accented copy. Ninety seconds.

**Edge cases**

* Copy with interpolation (`{count} invoices`): ICU placeholders preserved and validated.
* Same default text in two places: two ids; the extractor suggests sharing.
* Terminology term inside copy: nested `{term:customer}` resolved by PAP-126.
* Spec id renamed: ids change; migration note via {{spec-builder/spec-versioning}} codemod.
* Right-to-left locale: no layout work here; documented as PAP-27 scope.

**Dependencies**

Blocked by PAP-27, PAP-120. Soft: PAP-74, PAP-126, {{spec-builder/spec-versioning}}.

**Agent**

Built by Quill (Page Spec Writer) with Nova on codegen; reviewed by Iris for truncation review.

**Size**

M
"""})

GAPS.append({
"key": "spec-builder/spec-versioning",
"title": "Build spec versioning tooling: `specVersion` bumps, codemods for renamed keys, deprecation warnings and a rehearsed v1-to-v2 migration across 300 fixture specs",
"phase": "P2", "type": "Build", "priority": 3, "surfaces": ["Developer"],
"milestone": "Spec editor UI", "state": "Backlog",
"blockedBy": ["PAP-114", "PAP-74"], "blocks": [],
"description": """**Goal**

Make `migrateSpec()` real before hundreds of specs exist: a versioned schema registry, codemods that rewrite YAML documents without losing comments, deprecation warnings with removal dates for keys and components, and a rehearsed v1-to-v2 migration run across 300 generated fixture specs so the first real schema change is boring.

**Scope**

* In: `packages/spec/src/migrate/` (registry of versions, `Codemod` interface, runner), `paperos-spec migrate [--to N] [--dry-run]`, deprecation metadata in the schema and the PAP-74 registry, rule `SPEC_DEPRECATED`, the 300-spec fixture generator, the rehearsal (a synthetic v2 renaming `edgeCases` to `scenarios` and `layout.template` values).
* Out: real v2 design decisions (an ADR when needed), editor UI for migrations (PAP-124 shows warnings only).

**Spec**

* Registry `versions.ts`: `{ version, schema, codemodsFrom: Record<prev, Codemod[]> }`; `migrateSpec(doc, to)` applies codemods on the `yaml` Document API so comments and anchors survive, then validates with the target schema.
* `Codemod = { id, description, apply(doc): Change[] }` with helpers `renameKey`, `moveKey`, `mapEnum`, `wrapValue`; every codemod has a pass and fail fixture.
* Deprecations: schema keys carry `x-deprecated: { since, removeAfter, replaceWith }`; PAP-74 registry components carry the same; `SPEC_DEPRECATED` warns until `removeAfter`, then errors; `--fix` applies the replacement codemod.
* Fixture generator `pnpm spec fixtures --count 300 --seed 42` produces valid v1 specs covering every section and edge; rehearsal migrates all 300 to synthetic v2, validates, and diffs comment counts before and after.
* Gate 1 job `spec-migrate-check` runs `migrate --dry-run` and fails when a spec is older than the current version.

**Interface contract**

* Provides: `migrateSpec(doc, to)`, `paperos-spec migrate`, `Codemod` API, `x-deprecated` convention, rule `SPEC_DEPRECATED`, `pnpm spec fixtures`, `docs/spec/versioning.md` (how to add a version, checklist, ADR requirement).
* Consumers: PAP-114 (owns `specVersion`; this issue owns the tooling), PAP-74 deprecations, PAP-124 warning display and one-click `--fix`, {{spec-builder/spec-i18n}} id renames, PAP-125 examples kept current by the gate job, PAP-29 drill (template upgrade path).
* Requires: PAP-114 schema and `yaml` Document usage, PAP-74 registry metadata, PAP-78 job slot.

**Definition of done**

* Rehearsal: 300 fixtures migrate v1 to synthetic v2 with zero validation errors and zero lost comments; timing under 10 s (numbers in comment).
* `SPEC_DEPRECATED` warns before and errors after `removeAfter` (fake clock test); `--fix` applies the codemod.
* Gate job green on the template; red on a seeded stale spec.
* Docs; changelog; Linear comment with rehearsal results.

**Test plan**

* Unit: each codemod helper on documents with comments and anchors; registry ordering; deprecation date logic.
* Property (`fast-check`): generated specs migrate and validate; `migrate(migrate(x))` is idempotent.
* Integration: the 300-fixture rehearsal in CI weekly.
* No UI beyond PAP-124 warnings (visual there).

**Demo**

Run `pnpm spec fixtures --count 20`, then `paperos-spec migrate --to 2 --dry-run` and read the per-file change list; run without `--dry-run`, open one file and see comments intact with `scenarios:` in place of `edgeCases:`. One minute.

**Edge cases**

* Spec uses a key both renamed and deprecated: codemods apply in registry order; conflict detected in tests.
* Anchored value renamed: alias updated at all use sites.
* Custom `x-*` keys: never touched.
* Partial migration failure in a batch: report per file; nothing written for failed files.
* Version skipped (v1 to v3): codemods chained through v2.

**Dependencies**

Blocked by PAP-114, PAP-74. Soft: PAP-78, PAP-124.

**Agent**

Built by Quill (Page Spec Writer) with Forge on the codemod runner; reviewed by Sentinel.

**Size**

M
"""})

CHILDREN["PAP-119"] = [
{
"key": "spec-builder/data-section/schema", "title": "Data section: Zod schema, shared FilterTree import and validator rules", "type": "Spec", "size": "S",
"blockedBy": [], "blocks": ["spec-builder/data-section/generator", "spec-builder/data-section/example"],
"description": """**Goal**

Finalise the `data` section shape and its validator rules so the generator has a fixed target: entities, queries with the shared filter grammar, sort, fields, sync mode and paging, mutations with action, input, optimistic and audit flags, all checked against the app spec and the API contract at validation time.

**Scope**

* In: `packages/spec/src/schema/data.ts`, rules registered through PAP-115 `defineRule`, fixtures, `docs/spec/data.md` grammar section.
* Out: hook generation ({{spec-builder/data-section/generator}}), the example page ({{spec-builder/data-section/example}}).

**Spec**

* `DataSection = { entities: EntityId[], queries: Record<QueryName, Query>, mutations: Record<MutationName, Mutation> }`; `Query = { entity, filter?: FilterTree, sort?: { field, dir }[], fields: FieldPath[], sync: "live" | "local" | "server", page?: number (1-200) }`; `Mutation = { entity, action: "create" | "update" | "delete" | "custom", input: Record<string, ScalarType>, optimistic?: boolean, audit?: boolean }`.
* `FilterTree` imported from `@paperos/core/filter` (PAP-279); leaves may use `param: route.<name> | search.<name> | actor.<attr>` in place of `value`.
* `FieldPath` allows one relation hop (`customer.name`); names checked against the PAP-35 contract package when present, else against `entities[].fields` in the app spec with a warning.
* Rules: `DATA_UNKNOWN_ENTITY`, `DATA_UNKNOWN_FIELD`, `DATA_PARAM_UNBOUND`, `DATA_MUTATION_WITHOUT_ACCESS` (no matching `access.actions` entry), `DATA_UNSCOPED` (tenant-scoped entity, no access row, no tenant filter), `DATA_PAGE_RANGE` (warn), `DATA_OPTIMISTIC_NO_ID`.
* Names: `^[a-z][a-zA-Z0-9]*$`; hook names derived later must not collide (`DATA_HOOK_COLLISION` warn).

**Interface contract**

* Provides: `DataSectionSchema`, types `DataSection`, `Query`, `Mutation`, `FieldPath`, rule ids, `resolveFields(query, contract): ResolvedField[]`.
* Consumers: generator child, PAP-123 (`reads` and `writes` edges), PAP-124 form editor, PAP-116 (`rows` merge target), PAP-118 templates.
* Requires: PAP-114, PAP-279 `FilterTree`, PAP-115 rule API, PAP-35 contract types (soft), PAP-117 entities.

**Definition of done**

* Fixtures for every rule pass and fail; schema snapshot.
* Example spec sections for the three PAP-125 pages validate.
* Grammar documented; changelog; Linear comment.

**Test plan**

* Unit: schema and rule fixtures; `param` binding against a route with `$customerId` and a search schema.
* Integration: validator run with and without the contract package present.
* No UI.

**Demo**

Add `filter: { field: status, op: eq, param: route.status }` to a query on a route without `$status` and run `pnpm spec:validate`: `DATA_PARAM_UNBOUND` names the param and the route. Under one minute.

**Edge cases**

* Relation two hops deep: rejected with a hint to add a query.
* `sync: live` on a non-Electric entity: allowed here; generator falls back with a warning.
* Mutation `custom` without an oRPC procedure of that name: `DATA_UNKNOWN_PROCEDURE`.
* Filter referencing `actor.*` on a public page: error via PAP-116 interplay.
* Empty `fields`: error; at least the id.

**Dependencies**

Blocked by PAP-114, PAP-279 (through the parent). Blocks both sibling children.

**Agent**

Built by Quill (Page Spec Writer); reviewed by Forge (Schema Wright).

**Size**

S
"""},
{
"key": "spec-builder/data-section/generator", "title": "Data section: typed hook generator for server, live and local sync modes", "type": "Build", "size": "M",
"blockedBy": ["spec-builder/data-section/schema"], "blocks": ["spec-builder/data-section/example"],
"description": """**Goal**

Generate typed React hooks from the data section: `use<Query>()` and `use<Mutation>()` backed by TanStack Query plus the oRPC client for `server`, and by Electric shapes plus the offline outbox for `live` and `local`, with access rows merged into filters, optimistic updaters and a drift check so generated files stay in sync with specs.

**Scope**

* In: `packages/spec/src/codegen/data.ts`, templates, `pnpm spec gen:data [id] [--all] [--check]`, `dataStates` export, drift banner.
* Out: schema and rules ({{spec-builder/data-section/schema}}), the live example ({{spec-builder/data-section/example}}).

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

Blocked by {{spec-builder/data-section/schema}}, PAP-35. Soft: PAP-36, PAP-116, PAP-38.

**Agent**

Built by Forge (Schema Wright); reviewed by Nova and Sentinel.

**Size**

M
"""},
{
"key": "spec-builder/data-section/example", "title": "Data section: `customer-invoices` end to end with live sync, second-context and offline tests", "type": "Build", "size": "M",
"blockedBy": ["spec-builder/data-section/schema", "spec-builder/data-section/generator"], "blocks": [],
"description": """**Goal**

Prove the data section on a real page: the `customer-invoices` example uses generated hooks against seeded Postgres in `live` mode, a mutation in one browser shows in another within a second, and an offline mutation queues and applies on reconnect, all captured by Playwright at phone and desktop widths.

**Scope**

* In: the example's `data` section finalised, generated hooks committed, a minimal page wiring (or PAP-120 scaffold when available), Playwright suite `apps/web/e2e/data-section.spec.ts`, seeds via PAP-240, `docs/spec/data.md` usage section.
* Out: the generator and schema (sibling children), the full example documentation (PAP-125).

**Spec**

* Spec: query `invoices` (`live`, filter open or overdue, sort `dueAt`, fields including `customer.name`, page 50) and mutation `markPaid` (`update`, optimistic, audit).
* Page renders the list with `dataStates` mapping to loading, empty and error components (PAP-234, PAP-71) and a `Mark paid` button per row bound to `useMarkPaid`.
* Tests: two browser contexts logged in as `customer.any` via PAP-240 `login-as`; context A marks paid; context B sees the status within 1 s; `context.setOffline(true)` in A, mark another, badge shows pending, `setOffline(false)`, applied and audit row written with `reason`.
* Screenshots at 375 and 1280 px in light and dark for success, empty and error states.

**Interface contract**

* Provides: the canonical `customer-invoices` data section reused by PAP-125, PAP-120 and PAP-122; the e2e suite as a template for other pages; seed `invoices-basic` in PAP-240.
* Consumers: PAP-125 docs embed these screenshots; PAP-120 example child renders the same page; PAP-82 includes the page in the matrix.
* Requires: sibling children, PAP-36 Electric shape for `invoice`, PAP-240 seeds and login, PAP-38 audit, PAP-234 and PAP-71 components.

**Definition of done**

* Playwright suite green in CI on both forges with the timing assertions.
* Screenshots attached; audit row visible in the PAP-38 log for the mutation.
* Docs usage section; changelog; Linear comment with screenshots and the recording of the second-context update.

**Test plan**

* e2e (Playwright): the two-context and offline scenarios at 375 and 1280 px.
* Integration: hooks against the real seeded API in the test-mode stack.
* Visual: three states, two widths, two themes through gate 3.

**Demo**

Open the example in two windows side by side, click `Mark paid` in one and watch the other update; toggle offline in DevTools, mark another, reconnect, and see it sync with the audit entry. Two minutes.

**Edge cases**

* Electric not deployed in CI: suite falls back to `server` mode with a `test.skip` reason for the second-context timing.
* Slow CI: timing threshold 1 s local, 3 s CI with the value reported.
* Seed drift: fixed dates and ids from PAP-240.
* Mutation rejected by RLS: rollback and error toast asserted.
* Audit `reason` empty: mutation refused client-side with a message.

**Dependencies**

Blocked by {{spec-builder/data-section/schema}}, {{spec-builder/data-section/generator}}. Uses PAP-36, PAP-240, PAP-38, PAP-234.

**Agent**

Built by Nova with Forge; reviewed by Sentinel (Edge Case Hunter).

**Size**

M
"""},
]

CHILDREN["PAP-120"] = [
{
"key": "spec-builder/layout-codegen/templates", "title": "Layout codegen: Printer, route and view templates, two-file ownership and determinism", "type": "Build", "size": "M",
"blockedBy": [], "blocks": ["spec-builder/layout-codegen/wiring", "spec-builder/layout-codegen/examples"],
"description": """**Goal**

Build the codegen core: type-checked TypeScript templates with a `Printer` for indentation and import dedupe, the route file (created once), the regenerated view file, the logic stub file (created once) and the stories file, the two-file ownership rule with `--force`, Biome formatting and byte-identical determinism checked by `--check`.

**Scope**

* In: `packages/spec/src/codegen/{printer,page}.ts`, `templates/{route,view,logic,stories}.ts`, `pnpm spec gen:page <id> [--all] [--check] [--force]`, banner with spec hash, `docs/spec/codegen.md` ownership section.
* Out: state, slot and event wiring ({{spec-builder/layout-codegen/wiring}}), the example run ({{spec-builder/layout-codegen/examples}}).

**Spec**

* `Printer`: `line()`, `indent()`, `import(name, from)` with dedupe and sorted output, `block()`; templates are functions `(ctx: TemplateContext) => string`.
* Route: `createFileRoute('<route>')({ component, validateSearch?, staticData: { spec: '<id>' } })`; created if absent, otherwise compared: same `staticData.spec` leaves it; different aborts with the conflict.
* View: `<IdView>` placeholder rendering the component tree via `resolveComponent()` (PAP-74) with `data-spec-key`, props from the spec after schema validation, `children` recursed; wiring child adds states and events.
* Logic: `export const actions = { <name>: async (ctx) => { /* TODO */ } }` typed from `logic.actions`; created once; renamed actions leave `// TODO(unused)`.
* Stories: one story per `states` key with mocked hooks (wired fully by the wiring child).
* Determinism: sorted imports, LF, no timestamps; banner `// generated from specs/pages/<id>.spec.yaml sha256:<hash>`; `--check` regenerates in memory and diffs; Biome formats output.

**Interface contract**

* Provides: `Printer`, `TemplateContext = { spec, app, registry, hooks?, options }`, `generatePage(ctx): GeneratedFiles`, CLI, ownership rule (`owned: generator | human`) per output, banner format shared with PAP-119.
* Consumers: wiring child extends templates; PAP-124 preview compiles the view template in-browser; PAP-105 `page-from-spec`; PAP-29 drill.
* Requires: PAP-114 schema, PAP-74 `resolveComponent` and registry (hard).

**Definition of done**

* Snapshots for minimal and maximal fixtures; `--check` drift test; refusal to overwrite owned files test; `--force` test.
* Generating twice is byte-identical in CI.
* Docs ownership section; changelog; Linear comment.

**Test plan**

* Unit: `Printer` import dedupe and ordering, banner hash, conflict detection, recursion depth warning at 12.
* Integration: generated files typecheck in `apps/web` for the fixtures.
* No UI in this child.

**Demo**

Run `pnpm spec gen:page customer-invoices`, open the three files, edit the logic stub, regenerate and see the logic file untouched while the view banner hash changes only when the spec changes. One minute.

**Edge cases**

* Unknown component: dev renders `<MissingComponent id>`, `--check` errors.
* Props equal to schema defaults: omitted.
* Tree deeper than 12 levels: warning.
* Route file hand-edited beyond `staticData`: left alone; only `staticData.spec` compared.
* Biome unavailable: unformatted with a warning; drift check formats before comparing.

**Dependencies**

Blocked by PAP-114, PAP-74 (through the parent). Blocks both sibling children.

**Agent**

Built by Nova; reviewed by Sentinel (Code Reviewer).

**Size**

M
"""},
{
"key": "spec-builder/layout-codegen/wiring", "title": "Layout codegen: state switch, layout slot mapping, action binding and search-param schema", "type": "Build", "size": "M",
"blockedBy": ["spec-builder/layout-codegen/templates"], "blocks": ["spec-builder/layout-codegen/examples"],
"description": """**Goal**

Make generated views behave: a `states` switch driven by data hook status and permission (`loading`, `empty`, `error`, `offline`, `denied`, custom) using the PAP-234 and PAP-71 components, slots mapped to the PAP-16 layout templates through `useLayout()`, component `events` bound to `actions.<name>` from the logic file with `data-action` attributes, and a Zod `validateSearch` schema generated from `search.*` params.

**Scope**

* In: extensions to the view and stories templates, `states` resolver using PAP-119 `dataStates`, slot mapping table, event binding, `validateSearch` emission, `DeniedState` via PAP-59 `useCan('page.view')`, `OfflineBanner` from PAP-18 online status.
* Out: template infrastructure (sibling), example verification (sibling).

**Spec**

* State precedence: `denied` beats all; then `offline` banner overlays; `error`, `loading`, `empty`, then success; custom states are reachable through `logic` flags exposed by the logic file (`useViewState()` hook stub).
* Copy from `states.*.copy` rendered as-is until {{spec-builder/spec-i18n}} wraps it; `component?` overrides the default component per state.
* Slots: `layout.template` `app | public | focus | kiosk` maps to PAP-16 shells; `slots` keys validated against the shell's slot names; `kiosk` falls back to `focus` with a warning before PAP-23.
* Events: `events: { onClick: actions.markPaid }` emits `onClick={() => actions.markPaid(ctx)}` and `data-action="markPaid"`; unbound actions fail generation (`SPEC_ACTION_UNBOUND` already caught by PAP-115).
* Search params: every `param: search.<name>` yields a Zod field typed from the contract; `validateSearch` exported to the route file at creation time.
* Stories: one per state with `vi.fn` mocked hooks returning the matching status.

**Interface contract**

* Provides: `data-action` attribute convention (used by PAP-64 permission tests and PAP-122), `useViewState()` stub signature, slot mapping table `layoutSlots.ts`, `validateSearch` emission.
* Consumers: PAP-122 asserts states and `data-spec-key`; PAP-64 clicks `data-action` targets per audience; PAP-131 anchors comments on `data-spec-key`; PAP-83 video flows use `data-action`.
* Requires: templates child, PAP-234 state components, PAP-71 `EmptyState` and `Skeleton`, PAP-16 `useLayout`, PAP-59 `useCan`, PAP-119 `dataStates` (stubs otherwise), PAP-18 online hook.

**Definition of done**

* Snapshot tests for each state and each layout template; event binding and search schema tests.
* Stories for the maximal fixture render every state in Storybook (screenshots at 375 and 1280 px).
* Denied state renders no data hook call (asserted).
* Changelog; Linear comment with story links.

**Test plan**

* Unit: precedence table, slot validation, `data-action` emission, Zod search schema snapshot.
* Integration: Testing Library render of the generated maximal view under each mocked status.
* Visual: Storybook states at 375 and 1280 px, light and dark.

**Demo**

Open the generated stories for `customer-invoices` in Storybook and step through loading, empty, error, offline and denied; toggle the mocked `can` to false and watch `DeniedState` appear with no network calls in the panel. One minute.

**Edge cases**

* Spec omits `states.error`: app defaults (PAP-117 `defaults.states`) fill it.
* Two components bound to one action: allowed; both get `data-action`.
* Search param also a route param: error, ambiguous binding.
* Custom state never set by logic: story exists; runtime unreachable; validator warns `SPEC_STATE_UNREACHABLE`.
* Public page (`public: true`): `useCan` skipped; denied state unreachable and omitted.

**Dependencies**

Blocked by {{spec-builder/layout-codegen/templates}}, PAP-234. Soft: PAP-119, PAP-16, PAP-59, PAP-18.

**Agent**

Built by Nova with Iris (Component Crafter); reviewed by Sentinel.

**Size**

M
"""},
{
"key": "spec-builder/layout-codegen/examples", "title": "Layout codegen: generate the three example specs, screenshot seven widths and pass conformance with zero manual edits", "type": "Build", "size": "S",
"blockedBy": ["spec-builder/layout-codegen/templates", "spec-builder/layout-codegen/wiring"], "blocks": [],
"description": """**Goal**

Prove the generator on the three PAP-125 example specs: generate, typecheck, render, screenshot every state at seven widths in both themes, publish the stories and pass the PAP-122 conformance suites without touching a generated file by hand.

**Scope**

* In: generated files for `customer-invoices`, `staff-dashboard`, `agent-console` committed, Playwright capture, Storybook publication (PAP-69), conformance run, `docs/spec/codegen.md` walkthrough.
* Out: template and wiring code (sibling children), documentation prose beyond the walkthrough (PAP-125).

**Spec**

* Run `pnpm spec gen:page --all` for the examples; commit route, view, logic stub and stories; `--check` in gate 1 covers them.
* Playwright: each state of each page at 320, 375, 768, 1024, 1280, 1536 and 1920 px, light and dark, using PAP-240 login and seeds; artifacts named per PAP-82 (`screenshots/<page>/<state>/<width>-<theme>.png`).
* Storybook: stories appear in the PAP-69 deployment under `Generated/<page>`.
* Conformance: `pnpm spec gen:tests --all` then run; expect green with zero edits to generated files (CI asserts `git diff --exit-code` on `generated/`).
* Contact sheet: `pnpm screenshots:sheet` (PAP-82 reporter) assembles one image per page with the seven widths in a row per state, attached to the PR and the Linear comment so a reviewer reads the whole matrix at a glance.
* Walkthrough in `docs/spec/codegen.md`: the exact commands in order, expected output file list and how to fix a red `generated-untouched` assertion (edit the spec or the component, regenerate, never the output).

**Interface contract**

* Provides: committed generated examples as reference output, the screenshot set consumed by PAP-125 docs, the CI assertion pattern `generated-untouched`.
* Consumers: PAP-125, PAP-122, PAP-82 matrix, PAP-105 `page-from-spec` (points at the examples), PAP-29 drill.
* Requires: sibling children, PAP-122 generator, PAP-240, PAP-69, PAP-82 naming.

**Definition of done**

* Three pages generate and typecheck; conformance suites green; `generated-untouched` assertion passes.
* Screenshot matrix attached (three pages, up to six states, seven widths, two themes).
* Stories visible at the Storybook URL; walkthrough section; changelog; Linear comment with links.

**Test plan**

* Integration: full chain in CI (`gen:page`, `gen:data` if available, `gen:tests`, vitest, playwright).
* e2e: Playwright capture suite.
* Visual: the full matrix through gate 3.

**Demo**

Open the Storybook link, browse `Generated/customer-invoices` states, then open the Linear comment's contact sheet and compare the 320 px and 1920 px renders of the dashboard. One minute.

**Edge cases**

* `staff-dashboard` needs PAP-173 blocks: fallback `ui.responsiveGrid` with a callout naming PAP-173.
* `agent-console` needs PAP-129 data: mocked hooks in stories; Playwright uses the seed.
* Flaky screenshot from animation: PAP-72 reduced-motion flag forced.
* 320 px overflow found: fix in the spec or component, never in generated files.
* Theme token missing in dark: report to PAP-66 with the screenshot.

**Dependencies**

Blocked by {{spec-builder/layout-codegen/templates}}, {{spec-builder/layout-codegen/wiring}}. Uses PAP-122, PAP-240, PAP-69, PAP-82.

**Agent**

Built by Nova; reviewed by Sentinel (Visual Inspector).

**Size**

S
"""},
]

CHILDREN["PAP-124"] = [
{
"key": "spec-builder/spec-editor-ui/yaml", "title": "Spec editor: spec list, CodeMirror YAML editor with worker validation and save-to-PR flow", "type": "Build", "size": "M",
"blockedBy": [], "blocks": ["spec-builder/spec-editor-ui/form", "spec-builder/spec-editor-ui/preview"],
"description": """**Goal**

Ship the first usable editor: a list of specs with validation status, a YAML editor with schema completion and live diagnostics from the validator running in a Web Worker, and a save flow that commits to a `spec/<id>` branch through the Forgejo API and opens or updates a PR with optimistic locking.

**Scope**

* In: routes `/_app/dev/specs` and `/_app/dev/specs/$id` with page specs, `specs.list | get | save | validate` procedures, CodeMirror 6 YAML editor, worker validation, Issues tab, save and conflict flow, localStorage drafts.
* Out: form view ({{spec-builder/spec-editor-ui/form}}), preview and graph ({{spec-builder/spec-editor-ui/preview}}).

**Spec**

* List: PAP-165 grid if merged, else a simple table: id, title, route, surface, owner, status, validation, last commit; filters status and surface.
* Editor: `@codemirror/lang-yaml`, JSON Schema completion via `codemirror-json-schema` in YAML mode, diagnostics from `validateSpecs()` (PAP-115 library API) in a worker with 300 ms debounce; gutter markers keyed by `path`; Issues tab lists them with hints.
* Save: `specs.save({ id, yaml, message, baseSha })` writes the file on `spec/<id>`, commits with PAP-46 trailers, opens or updates a PR (PAP-49 template) via the Forgejo API client (PAP-276 if merged, else a thin client here); `CONFLICT` when `baseSha` moved returns the current content; UI shows a three-way diff (`diff` 7) and a rebase button.
* Drafts autosave per user and spec in `localStorage` with a restore banner; unsaved-changes guard on navigation; `spec_editor.save` audit event (PAP-38).
* Access: `staff.admin` write, `agent.*` read (PAP-116 section on the page spec).

**Interface contract**

* Provides: page specs `spec-list.spec.yaml`, `spec-editor.spec.yaml`; procedures `specs.list()`, `specs.get(id): { yaml, sha }`, `specs.save(...)`, `specs.validate(yaml)`; component `YamlEditor` with `onDiagnostics`; event `spec.saved { id, prUrl }`.
* Consumers: form child (shares the document model), preview child (reads editor state), Quill sessions, PAP-126 later.
* Requires: PAP-114, PAP-70 `SplitPane`, PAP-115 library API, Forgejo API access, PAP-46, PAP-49, PAP-38, PAP-165 (soft).

**Definition of done**

* Playwright: open example, introduce a YAML error, see gutter marker and Issues entry, fix, save, PR link appears (mocked Forgejo); conflict flow with a concurrent change.
* Worker validation under 300 ms for a 300-line spec (timing in comment).
* Screenshots at 768, 1024, 1280, 1536 and 1920 px light and dark; 320 and 375 px show read-only YAML with the notice.
* axe clean; changelog; Linear comment with screenshots.

**Test plan**

* Unit: diagnostics mapping from `SpecIssue` to CodeMirror ranges, draft restore, conflict state machine.
* Integration: `specs.save` against a mocked Forgejo API including `CONFLICT`.
* e2e (Playwright): the save and conflict flows at 375 (read-only) and 1280 px.
* Visual: seven widths through gate 3.

**Demo**

Open `/_app/dev/specs/customer-invoices`, type an invalid `surface`, watch the gutter error and Issues entry, fix it, press `Cmd+S` and click the PR link that appears. One minute.

**Edge cases**

* Worker crash: "validation unavailable", save requires confirm.
* Offline: editing continues, save disabled with reason, draft kept.
* Spec deleted upstream: save offers to recreate on the branch.
* Very large spec: editor virtualised by CodeMirror; validation still in worker.
* Agent user: read-only editor with a copy button.

**Dependencies**

Blocked by PAP-114, PAP-70 (through the parent). Soft: PAP-115, PAP-165, PAP-276.

**Agent**

Built by Nova; reviewed by Sentinel (Visual Inspector).

**Size**

M
"""},
{
"key": "spec-builder/spec-editor-ui/form", "title": "Spec editor: form view, component tree editor and two-way sync with YAML preserving comments", "type": "Build", "size": "M",
"blockedBy": ["spec-builder/spec-editor-ui/yaml"], "blocks": [],
"description": """**Goal**

Let people who do not want YAML edit specs: section forms generated from the `PageSpec` Zod schema, a component tree editor that adds components from the registry with prop forms from each component's JSON Schema, an access editor with audience multiselect and condition builder, and two-way sync with the YAML tab that patches the `yaml` Document so comments and `x-*` keys survive.

**Scope**

* In: `SpecForm` with `react-hook-form` 7 and the zod resolver, section panels (meta, purpose, access, data, layout, components, states, events, edge cases), component tree editor, access editor, sync engine, inline diagnostics keyed by `path`.
* Out: YAML editor and save ({{spec-builder/spec-editor-ui/yaml}}), preview and graph ({{spec-builder/spec-editor-ui/preview}}).

**Spec**

* Forms derived from `PageSpecSchema` field metadata (labels, descriptions, enums as selects, defaults shown); arrays as sortable lists (PAP-155 drag with keyboard alternative).
* Component tree: nested list with add-from-registry (searchable list from PAP-74 `registry.json`), prop form per component from its JSON Schema, `slot` picker limited to the layout template's slots, `events` picker limited to `logic.actions`.
* Access editor: audiences from the app spec (PAP-117) as multiselect; condition builder reusing PAP-166 filter UI when merged, else a minimal `all | any | not` tree editor over the PAP-279 grammar.
* Sync: form edits produce JSON patches applied to the `yaml` Document (`yaml` 2.x `Document` API) at the mapped path; YAML edits reparse into the form on debounce; invalid YAML shows a banner and freezes the form until fixed.
* Diagnostics from the yaml child's worker map to form fields by `path`.

**Interface contract**

* Provides: `SpecForm` component, `applyFormPatch(doc, path, value)`, `docToForm(doc)`, `ComponentTreeEditor`, `AccessEditor` (reusable by PAP-126 for the business profile).
* Consumers: PAP-126 (profile editing), PAP-118 skill may open a prefilled form link, PAP-131 comments anchor on `data-spec-key` in the tree editor.
* Requires: yaml child document model, PAP-74 registry, PAP-117 audiences, PAP-279 grammar, PAP-155 (soft), PAP-166 (soft), PAP-233 form adapters.

**Definition of done**

* Round-trip test: load a spec with comments and anchors, change a title and add a component in the form, serialise; comments, anchors and `x-*` keys intact; only the edited paths changed.
* Playwright: edit title in Form, see YAML update; add a component from the registry; toggle an audience; diagnostics appear inline on an invalid value.
* Screenshots at 1024, 1280 and 1920 px light and dark; axe clean.
* Changelog; Linear comment.

**Test plan**

* Unit: patch mapping for nested arrays, enum selects, prop schema rendering for three registry components, invalid-YAML freeze.
* Integration: two-way sync with a debounce clock.
* e2e (Playwright) at 1280 px; 768 px shows stacked panels.
* Visual: three widths through gate 3.

**Demo**

Open the Form tab, change the page title, switch to YAML and see it changed with the comments still there; add `ui.badge` from the registry into the `main` slot and watch the YAML gain the node. One minute.

**Edge cases**

* Registry component removed: node shows a warning with a replace action.
* 300 components: tree virtualised.
* Prop schema with `oneOf`: rendered as a variant selector.
* Form and YAML edited within the same debounce window: YAML wins, form re-derives.
* Anchored value edited in the form: alias updated at all sites, user informed.

**Dependencies**

Blocked by {{spec-builder/spec-editor-ui/yaml}}. Soft: PAP-166, PAP-155, PAP-233.

**Agent**

Built by Iris (Component Crafter) with Nova; reviewed by Sentinel.

**Size**

M
"""},
{
"key": "spec-builder/spec-editor-ui/preview", "title": "Spec editor: live preview at selectable widths, flow-graph tab, keyboard shortcuts and accessibility polish", "type": "Build", "size": "M",
"blockedBy": ["spec-builder/spec-editor-ui/yaml"], "blocks": [],
"description": """**Goal**

Complete the editor: a live preview that compiles the PAP-120 view template in-memory with `esbuild-wasm` inside an iframe at a selectable width and theme, a Graph tab showing the page's neighbourhood from the PAP-123 flow graph, command-registry shortcuts, and the accessibility pass with a recorded keyboard-only flow.

**Scope**

* In: Preview tab (width presets 320 to 1920, theme toggle, state selector), Graph tab (React Flow mini view via `subgraph()`), shortcuts through PAP-151, focus order and axe fixes, PAP-83 flow file and video, `docs/spec/editor.md`.
* Out: YAML and form editing (sibling children), canvas interactions beyond viewing (PAP-132).

**Spec**

* Preview: on valid spec, run `generatePage()` templates in a worker, bundle with `esbuild-wasm` against the design-system package externals resolved from a prebuilt vendor bundle, render in a sandboxed iframe with `postMessage` for width and theme; compile capped at 5 s with an outline fallback (component tree with slots); state selector forces `dataStates` via mocked hooks.
* Graph: `subgraph(graph, 'page:<id>', depth 1)` rendered with React Flow, nodes clickable to open their editor; regenerates on save.
* Shortcuts: `Cmd/Ctrl+S` save, `Cmd/Ctrl+Shift+V` toggle Form and YAML, `Cmd/Ctrl+P` toggle preview, registered with PAP-151 when present, local fallback otherwise.
* Accessibility: tabs are proper `role="tablist"`, iframe has a title, width presets are radio buttons, diagnostics announced via a live region; PAP-152 focus management on tab switch.
* Telemetry: `spec_editor.preview_compile` duration event.

**Interface contract**

* Provides: `SpecPreview` component (`{ spec, width, theme, state }`), `useSubgraph(pageId)`, shortcut ids `specs.save`, `specs.toggleView`, `specs.togglePreview`, the PAP-83 flow file `flows/spec-editor.yaml`.
* Consumers: PAP-125 docs (preview screenshots), PAP-131 comments in preview later, PAP-113 reuses the subgraph viewer pattern.
* Requires: yaml child, PAP-120 templates, PAP-123 graph, PAP-151, PAP-152, PAP-83 recorder, prebuilt vendor bundle from PAP-69 build.

**Definition of done**

* Preview renders the three examples at 320, 768 and 1280 px presets in both themes (screenshots); compile time under 5 s (numbers).
* Graph tab shows neighbours and navigates on click.
* Keyboard-only flow recorded (open, edit, preview, save) and attached; axe clean on all tabs.
* Docs; changelog; Linear comment with video and screenshots.

**Test plan**

* Unit: width preset state, message protocol to the iframe, subgraph selection, shortcut registration fallback.
* Integration: worker compile of the example views against the vendor bundle; timeout path.
* e2e (Playwright): preview width switch, graph click navigation, keyboard flow at 1280 px.
* Visual: preview at 320, 768 and 1280 px presets in both themes through gate 3.

**Demo**

Open the Preview tab, switch to 320 px and dark, select the `empty` state and see the empty component; open Graph, click the neighbouring `invoice-detail` node and land in its editor. One minute.

**Edge cases**

* Component not in the vendor bundle: preview shows `<MissingComponent>`; outline fallback lists it.
* Compile over 5 s: outline fallback with a retry button.
* Graph has no neighbours: single node with a hint to add `events`.
* Shortcut conflicts with browser: registry warns; alternative shown in the tooltip.
* Reduced motion: preview transitions disabled (PAP-72).

**Dependencies**

Blocked by {{spec-builder/spec-editor-ui/yaml}}. Soft: PAP-120, PAP-123, PAP-151, PAP-152, PAP-83.

**Agent**

Built by Nova (Canvas Cartographer) with Iris on accessibility; reviewed by Sentinel (Visual Inspector).

**Size**

M
"""},
]


# FIX-5 (2026-09-17): folded into live issues as work packages; never create. See round2/folded-into-live-issues.json.
import json as _json, os as _os
_FOLDED = {f["key"] for f in _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "folded-into-live-issues.json")))["folded"]}
GAPS = [g for g in GAPS if g["key"] not in _FOLDED]
