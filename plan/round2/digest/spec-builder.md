# spec-builder — Spec Builder
PHASE P1 prio 1 dependsOn ['design-system', 'data-layer']
SUMMARY: A page.spec.yaml schema describing logic, access, data, integrations, layout, components and edge cases, with a validator, codegen, conformance tests and an editor UI.
DESC: Goal: every page in every app is specified before it is built, and the spec drives code, tests and diagrams. The schema captures purpose, logic, access rules, data queries and mutations, integrations, layout, component tree, states, events and edge cases; an app.spec.yaml holds shared audiences, navigation and entities. A validator CLI and CI check block unspecified pages. Codegen scaffolds layouts and typed data hooks from specs; conformance and permission tests are derived automatically; the canvas view is generated from spec transitions. A spec editor UI with form and YAML views lets Justin and agents edit specs in-app, and an authoring skill lets agents interview and draft specs. Non-goal: a full visual app builder.
MILESTONES: ['Spec schema and validator 2026-09-22: Schema, validator, access and app-level spec, authoring skill', 'Codegen and conformance tests 2026-09-26: Data hooks, layout codegen, integrations registry, conformance tests, canvas emit', 'Spec editor UI 2026-09-30: In-app editor and worked examples']


## PAP-114 [P0 Spec M prio1 Ready for Claude] Define the page.spec.yaml schema: purpose, logic, access, data, integrations, layout, components, states, events, edge cases
key=spec-builder/schema milestone=Spec schema and validator agent=Built by Quill (Page Spec Writer). Reviewed by Atlas for the
blockedBy=[] blocks=['PAP-132', 'PAP-124', 'PAP-123', 'PAP-121', 'PAP-120', 'PAP-119', 'PAP-117', 'PAP-116', 'PAP-115', 'PAP-85', 'PAP-74']
GOAL: Define the canonical `page.spec.yaml` format that every PaperOS page must have, as a Zod 4 schema in `packages/spec` with a generated JSON Schema for editors and TypeScript types for codegen. The validator, codegen, conformance tests, canvas and permission engine all read this contract, so it lands first and changes only through ADRs.
SCOPE: In:

* `packages/spec/src/schema/page.ts`: Zod 4 `PageSpec` with sections `meta` (`id`, `title`, `route`, `surface: customer|staff|developer|agent|public`, `owner` character, `status: draft|ready|built|deprecated`, `specVersion: 1`), `purpose` (paragraph plus `successMetric`), `logic` (named `actions` each with `steps[]`, `guard`, `effects[]`, `onError`), `access`, `data`, `integrations` (interim shapes; finalised by `spec-builder/access-section`, `spec-builder/data-section`, `spec-builder/integrations-section`), `layout` (`template: app|public|focus|kiosk`, `slots` map), `components` (tree of `{ id: ComponentRef, key, props, slot, events, children }`), `states` (`loading`, `empty`, `error`, `offline`, `denied` plus custom, each `{ copy, component? }`), `events` (transitions `{ on, to: RouteRef, guard?, kind: navigate|mutation|integration }`), `edgeCases[]` (`{ id, scenario, expected, te
SPEC(first 1200): * File location `specs/pages/<id>.spec.yaml`; `meta.id` must equal the filename stem; first line `# yaml-language-server: $schema=../../packages/spec/schema/page.spec.schema.json`.
* Minimal valid example:

  ```yaml
  specVersion: 1
  meta: { id: customer-invoices, title: Invoices, route: /_app/invoices, surface: customer, owner: Nova, status: draft }
  purpose: { summary: Customers review and pay invoices., successMetric: 90% of invoices paid in-app }
  access: { view: [customer.any] }
  layout: { template: app, slots: { main: ui.dataTable } }
  components: [{ id: ui.dataTable, key: invoiceTable, slot: main, props: { density: comfortable } }]
  states: { empty: { copy: No invoices yet. } }
  edgeCases: [{ id: no-tenant, scenario: user has no tenant, expected: redirect to onboarding, test: e2e }]
  ```
* `status: ready` requires `access`, `data` or `x-static: true`, at least three `edgeCases`, and every `events[].to` to be a `RouteRef`.
* Component `events` values must be `actions.<name>` referencing `logic.actions`.
* `migrations/v1-to-v2.ts` skeleton and `migrateSpec()` so future versions have a path.
DOD:
* Vitest: fixtures parse; each invalid fixture fails with the expected `code`, `line` and `col`; snapshot of the JSON Schema.
* `schema:build` idempotent; drift check wired into the `generated-drift` job of `quality/ci-gate1`.
* JSON Schema gives autocompletion in VS Code on the fixture files (screenshot in PR).
* `docs/spec/page-spec.md` generated with every field described; ADR `docs/adr/00NN-PAP-<n>-page-spec-format.md` registered in `collab/decision-log`.
* Types exported from `@paperos/spec` and consumed by `app-shell/router-layouts` `useSpec` (replace its interim type).
* CHANGELOG entry; Linear comment linking docs, schema file and the ADR.
EDGE:
* YAML anchors and merge keys (`<<: *base`) are allowed and resolved before validation; issues point at the merged line.
* Duplicate `components[].key` in one spec: error `SPEC_DUP_KEY` listing both lines.
* Route contains params (`/_app/invoices/$id`): `RouteRef` accepts TanStack `$param` syntax only, not `:param`.
* Spec 200 KB or larger: warn `SPEC_TOO_LARGE`, suggest splitting into sub-pages.
* Windows line endings and BOM: normalised before parsing, positions still correct.
* `specVersion` missing: treated as 1 with a warning until 2 exists.
DEPS: None hard. Soft: `design-system/component-spec-mapping` (interim `ComponentRef` regex agreed). Unblocks `spec-builder/validator`, `spec-builder/access-section`, `spec-builder/app-level-spec`, `spec-builder/data-section`, `spec-builder/layout-codegen`, `spec-builder/spec-to-canvas`, `collab/canvas-view`, `quality/edge-case-hunter`.


## PAP-115 [P0 Build M prio1 Backlog] Build the spec validator CLI and CI check that fails PRs whose pages lack or violate specs
key=spec-builder/validator milestone=Spec schema and validator agent=Built by Quill (Page Spec Writer) with Sentinel pairing on C
blockedBy=['PAP-114'] blocks=['PAP-125', 'PAP-122', 'PAP-118']
GOAL: Ship the `paperos-spec` CLI and CI job that make specs mandatory: every route in an app must have a valid `page.spec.yaml`, every reference inside a spec must resolve, and a PR that breaks either rule turns gate 1 red with a precise annotation. This is the enforcement point for the spec-first decision.
SCOPE: In:

* `packages/spec/src/cli.ts` (`cac` 6) exposing `paperos-spec validate [paths] [--format pretty|json|github] [--fix] [--baseline]`, `paperos-spec routes` (lists routes without specs), wired as `pnpm spec:validate`.
* Rule engine `packages/spec/src/rules/`: `defineRule({ id, severity: error|warn, check(ctx) })` with `ctx = { specs, app, routes, registry, git }`. Core rules: `SPEC_PARSE` (schema), `SPEC_ROUTE_UNCOVERED` (route file under `apps/web/src/routes/_app/**` or `_public/**` lacking `staticData.spec`), `SPEC_ORPHAN` (spec whose route file is missing when `status: built`), `SPEC_DUP_ID`, `SPEC_UNKNOWN_COMPONENT` and prop errors delegated to `design-system/component-spec-mapping`'s `registry.json`, `SPEC_UNKNOWN_ENTITY` and `SPEC_UNKNOWN_AUDIENCE` against `specs/app.spec.yaml` when present, `SPEC_DANGLING_TRANSITION` (`events[].to` not a known route), `SPEC_ACTION_UNBOUND` (comp
SPEC(first 1200): * Exit codes: 0 clean, 1 errors, 2 warnings with `--strict`, 3 internal failure.
* Route discovery reads the TanStack generated `routeTree.gen.ts` rather than globbing, so it matches the router exactly; `_public/auth/*` and `__root` are exempt via `specs/.validator-ignore`.
* Performance: 300 specs validated under 2 s; registry and app spec parsed once; results cached by content hash in `node_modules/.cache/paperos-spec`.
* Each issue includes `hint` (one sentence) and `docs` URL into `docs/spec/validator.md#<code>`.
* Watch mode `--watch` for the spec editor and authoring skill.
* Library API `validateSpecs(options): Promise<Report>` used by `spec-builder/spec-editor-ui` in a worker.
DOD:
* Vitest per rule with fixtures (pass and fail), CLI snapshot tests for all three formats, exit code tests.
* Seeded failing PR shows inline annotations on both GitHub and Forgejo runs (links in comment).
* Green run on paperos-template with the baseline; baseline expiry test fails the build after the date.
* `docs/spec/validator.md` with every code, hint and fix; CHANGELOG entry.
* `spec:validate` finishes under 2 s on 300 generated specs (timing pasted).
* Linear comment with green and red run links.
EDGE:
* Spec references a route in another app of the monorepo: allowed only via `x-external: true`, else `SPEC_DANGLING_TRANSITION`.
* `registry.json` missing (design system not built): skip component rules with a single warning, never crash.
* Two specs claim the same route: `SPEC_DUP_ROUTE` naming both files.
* Deleted route with spec still `status: built`: error with hint to set `deprecated`.
* Baseline file edited to add new entries in the same PR: rule `SPEC_BASELINE_GROWTH` fails unless PR has label `spec-baseline`.
* Symlinked spec folders in worktrees: resolve real paths before dedupe.
DEPS: `spec-builder/schema` (hard). Soft: `design-system/component-spec-mapping` (registry), `spec-builder/app-level-spec` (entity and audience rules activate when present), `quality/ci-gate1` (job slot). Unblocks `spec-builder/spec-authoring-skill`, `spec-builder/conformance-tests`, `spec-builder/spec-docs`.


## PAP-116 [P0 Spec M prio1 Backlog] Specify the access section format that compiles to permission-engine policies
key=spec-builder/access-section milestone=Spec schema and validator agent=Built by Quill (Page Spec Writer) with Forge (Schema Wright)
blockedBy=['PAP-114'] blocks=['PAP-64']
GOAL: Finalise the `access` section of a page spec so that "who can see this page and do what on it" is written once in YAML and compiled losslessly into `identity/rbac-abac` policies, SQL predicates and permission tests. Replace the draft adapter in the permission engine with this contract.
SCOPE: In:

* Zod 4 schema `AccessSection` in `packages/spec/src/schema/access.ts`:

  ```yaml
  access:
    public: false
    view: [customer.any, staff.support, staff.admin]
    actions:
      markPaid: { audiences: [staff.billing], condition: { path: resource.status, op: eq, value: open } }
      export:   { audiences: [staff.admin] }
    rows:
      invoice: { path: resource.customerId, op: eq, ref: actor.customerId }
    deny: [agent.*]
    fields:
      invoice.internalNotes: { view: [staff.*] }
  ```
* `Condition` type imported from `@paperos/permissions` (same `all|any|not` tree, ops `eq|neq|in|contains|gte|lte|isNull`) so nothing is duplicated.
* Compiler `packages/spec/src/access/compile.ts`: `toPolicies(page: PageSpec, app: AppSpec): Policy[]` producing `page.view`, `page.action:<name>`, `<entity>.<verb>` row policies and `field.view:<entity>.<field>` with `source: { specPath, line }
SPEC(first 1200): * Semantics: `deny` beats everything; `view` grants `page.view`; an action grants only its named action, never implied view (validator warns if an action audience lacks view).
* `rows` compile to predicates applied by generated data hooks (`spec-builder/data-section`) and by oRPC `authorize` middleware; one entry per entity in `data.entities`.
* `public: true` means `page.view` for the built-in `anonymous` audience; conflicts with `rows` referencing `actor.*` (error).
* Inheritance: `app.spec.yaml` may declare `defaults.access` (for example `deny: [agent.*]`) merged before compile; page can override with `inherit: false`.
* Output is deterministic and sorted so `policies.generated.json` diffs are readable; `pnpm spec gen:policies` writes `packages/permissions/src/generated/spec-policies.json`.
DOD:
* Vitest: compile fixtures to expected `Policy[]` (snapshot), wildcard expansion, inheritance, each validator rule pass and fail.
* Property test (`fast-check`): any valid `AccessSection` compiles and `can()` from `identity/rbac-abac` agrees with a naive reference evaluator on 500 random actor/action pairs.
* Draft adapter in `packages/permissions/src/from-spec.ts` replaced; its tests pass unchanged or with documented updates.
* `access-matrix` output committed for the three example pages of `spec-builder/spec-docs`.
* `docs/spec/access.md`; CHANGELOG entry; Linear comment with matrix and PR links.
EDGE:
* Audience renamed in `app.spec.yaml`: every page referencing it fails with file and line; `--fix` offers a rename when `x-renamedFrom` is set.
* Condition referencing `actor.customerId` for a staff audience with no such attribute: warn `ACCESS_ATTR_UNAVAILABLE`.
* Action name containing a dot or uppercase: rejected, actions are `^[a-z][a-zA-Z0-9]*$`.
* Circular `all/any` nesting deeper than 8: error, keeps SQL compilation bounded.
* Page with `public: true` and `actions`: allowed for anonymous flows such as pay-by-link; matrix marks them.
* Field rule for an entity not in `data.entities`: error.
DEPS: `spec-builder/schema` (hard), `identity/rbac-abac` (Policy and Condition types; if not merged, import from its branch and pin). `identity/audience-model` and `spec-builder/app-level-spec` for audience ids. Unblocks `identity/permission-tests`, `spec-builder/conformance-tests`.


## PAP-117 [P1 Spec S prio1 Backlog] Define app.spec.yaml (audiences, navigation, entities, integrations) that page specs inherit from
key=spec-builder/app-level-spec milestone=Spec schema and validator agent=Built by Quill (Page Spec Writer). Reviewed by Atlas and For
blockedBy=['PAP-114'] blocks=['PAP-126', 'PAP-28']
GOAL: Define `specs/app.spec.yaml`, the single app-wide file holding audiences, navigation, entities, integrations, defaults and theme that page specs inherit from, so page specs stay short and consistent and the router, permission engine, canvas and search have one place to read app structure.
SCOPE: In:

* Zod 4 `AppSpec` in `packages/spec/src/schema/app.ts`:

  ```yaml
  specVersion: 1
  app: { id: paperos-template, name: PaperOS, tenantModel: multi, defaultLocale: en-US }
  audiences:
    - { id: customer.any, kind: customer, label: Customer }
    - { id: customer.pro, kind: customer, extends: customer.any, segment: { plan: pro } }
    - { id: staff.support, kind: staff, label: Support }
    - { id: agent.builder, kind: agent }
  navigation:
    staff: [{ label: Dashboard, route: /_app/dashboard, icon: layout-dashboard, children: [] }]
    customer: [{ label: Invoices, route: /_app/invoices, icon: receipt }]
  entities:
    - { id: invoice, table: invoices, label: Invoice, plural: Invoices, searchable: true, owner: Ledger }
  integrations: [{ connector: stripe, mode: test }]
  defaults: { layout: { template: app }, access: { deny: [agent.*] }, states: { error: { copy: Something we
SPEC(first 1200): * Exactly one `specs/app.spec.yaml` per app; `paperos create` (`app-shell/create-cli`) writes it from the template with the app id filled in.
* Audience `kind` enum `customer|staff|partner|admin|agent|anonymous`; `segment` is a flat key/value map matched against actor attributes by the permission engine.
* Navigation items may carry `audiences` to hide items; codegen filters at render using `useCan('page.view')` rather than trusting the static list.
* `entities[].fields` optional summary `{ name, type, label }` used for docs and the canvas; the Drizzle schema remains the source of truth and a drift warning fires when names diverge.
* `integrations` entries reference `spec-builder/integrations-section` connector ids; page specs can only use connectors listed here.
* `theme` resolves to a token preset from `design-system/theming`.
DOD:
* Vitest: parse fixture, merge precedence (page beats app defaults, `inherit: false` clears), audience expansion, each validator rule.
* `gen:app` outputs committed and drift-checked; router nav renders from generated navigation (screenshot at 375 and 1280 for staff and customer audiences).
* Template repo ships a populated `app.spec.yaml`; `paperos-spec validate` passes.
* `docs/spec/app-spec.md`; CHANGELOG entry; Linear comment with screenshots and generated files.
* Type `AudienceId` imported by `identity/rbac-abac` compiles.
EDGE:
* Navigation item route with params (`/_app/invoices/$id`): rejected in nav, only static routes allowed.
* Two audiences with the same label but different ids: allowed with a warning.
* Entity table renamed in a migration: `APP_ENTITY_TABLE_MISSING` blocks the PR until the spec is updated.
* Empty `navigation` for an audience with pages granting view: warn `APP_NAV_ORPHAN_PAGES` listing routes.
* App declares `tenantModel: single`: pages with `rows` conditions on `tenantId` warn as redundant.
* Very large app (500 entities): merge runs under 100 ms; memoised by file hash.
DEPS: `spec-builder/schema` (hard). Soft: `data-layer/drizzle-schema` (table existence check), `identity/audience-model` (kinds), `app-shell/router-layouts` (nav consumer). Unblocks `spec-builder/access-section` wildcard expansion, `spec-builder/spec-to-canvas`, `collab/knowledge-search` entity registration.


## PAP-118 [P1 Build M prio1 Backlog] Write the agent skill: interview -> draft page spec -> validate -> open Linear issue
key=spec-builder/spec-authoring-skill milestone=Spec schema and validator agent=Built by Quill (Page Spec Writer) with Atlas (Decomposer) on
blockedBy=['PAP-105', 'PAP-115'] blocks=[]
GOAL: Give every character a repeatable way to turn a request into a validated page spec and a Linear issue: interview the requester (or read a brief), draft `page.spec.yaml`, run the validator until clean, commit on a branch and open a spec-complete issue. This is how hundreds of specs get written without Justin editing YAML.
SCOPE: In:

* `.claude/skills/author-spec/SKILL.md` (under 1500 words, frontmatter per `agents/skills-library` lint) with `references/question-bank.md`, `templates/page.spec.yaml`, and scripts in `scripts/` run with `tsx`.
* Flow: (1) `scripts/context.ts` prints `app.spec.yaml` audiences, entities, existing page ids and routes so the model never invents names; (2) interview of at most 12 questions from the bank, grouped by surface (customer, staff, agent), skipped when a brief answers them; (3) draft YAML from `templates/page.spec.yaml`; (4) `paperos-spec validate --format json` and up to three fix rounds; (5) `scripts/commit.ts` writes `specs/pages/<id>.spec.yaml` on branch `spec/<id>` with commit `spec(<id>): add page spec` plus `Linear:` and `Character:` trailers (`forge/branch-policy`), pushes and opens a PR using `forge/pr-templates`; (6) `scripts/open-issue.ts` creates the Linear issue "B
SPEC(first 1200): * Question bank covers purpose and metric, audiences and actions, data read/written, integrations, layout template and slots, states copy, transitions, edge cases (at least five prompted categories: empty, huge, offline, denied, concurrent edit).
* Drafting rules in SKILL.md: prefer existing components from `registry.json`; every action gets an access entry; every entity in `data` must exist in `app.spec.yaml`; no prose longer than two sentences per field.
* `open-issue.ts` is idempotent: searches Linear for an issue with `spec:<id>` in the description and updates instead of duplicating.
* Budget guard: the skill aborts after 40 turns and leaves a `draft` status spec with a comment, so a runaway interview cannot burn credits.
* Output on the last line of every script is JSON `{ ok, specPath, prUrl?, issueUrl?, issues: [] }`.
DOD:
* Dry run transcript: a session invokes the skill on a brief ("customers list and pay invoices") and produces a spec that validates first or second round, a PR and a Linear issue (links in comment).
* Second dry run from a live interview with Justin's answers pasted as a brief.
* Vitest for scripts: context output, commit trailer format, issue body matches `pm-linear/issue-contract` schema, idempotent re-run.
* Lint passes (`agents/skills-library` word and frontmatter rules); listed in `skills.json` for Quill, Atlas and Nova.
* `docs/agents/skills.md` updated; CHANGELOG entry; Linear comment with both transcripts.
EDGE:
* Brief asks for an entity that does not exist: skill stops and proposes a `data-layer` issue instead of inventing a table.
* Validator unavailable (package not built): skill runs `pnpm --filter spec build` once, then fails loudly rather than skipping validation.
* Page id already exists: skill offers to update it and bumps `status` back to `draft` with a changelog note in `x-history`.
* Linear rate limit: `linear-update` writes to `artifacts/pending-comments/` for the orchestrator to flush.
* Requester answers in another language: spec copy fields stay in the app default locale; original answers stored under `x-interview`.
* Interview reveals the page should be two pages: skill drafts both and cross-links via `events`.
DEPS: `spec-builder/validator` (hard), `agents/skills-library` (`linear-update`, lint, `skills.json`) (hard). Soft: `pm-linear/issue-contract`, `forge/pr-templates`, `spec-builder/app-level-spec`.


## PAP-119 [P1 Build L prio1 Backlog] Specify the data section (entities, queries, mutations, sync mode) and generate typed hooks from it
key=spec-builder/data-section milestone=Codegen and conformance tests agent=Built by Forge (Schema Wright) for the generator with Quill 
blockedBy=['PAP-35', 'PAP-114'] blocks=[]
GOAL: Finalise the `data` section of a page spec so pages declare the entities, queries and mutations they need together with a sync mode, and a generator turns that declaration into typed React hooks backed by oRPC or Electric shapes. Agents stop hand-writing data plumbing and the spec stays the truth about what a page reads and writes.
SCOPE: In:

* Zod 4 `DataSection` in `packages/spec/src/schema/data.ts`:

  ```yaml
  data:
    entities: [invoice, customer]
    queries:
      invoices:
        entity: invoice
        filter: { all: [{ field: status, op: in, value: [open, overdue] }, { field: customerId, op: eq, param: route.customerId }] }
        sort: [{ field: dueAt, dir: asc }]
        fields: [id, number, total, status, dueAt, customer.name]
        sync: live          # live (Electric shape) | local (PGlite first) | server (oRPC only)
        page: 50
    mutations:
      markPaid: { entity: invoice, action: update, input: { id: uuid, paidAt: datetime }, optimistic: true, audit: true }
  ```
* Filter grammar shared with `tables/view-model-spec` (import its `FilterTree` type once it lands; until then identical shape in `packages/spec/src/schema/filter.ts` with a TODO).
* Generator `pnpm spec gen:data [id]` writing `app
SPEC(first 1200): * Access rows from `spec-builder/access-section` are merged into every query filter at generation time as an `all` node, so a page cannot request rows it may not see; server still enforces.
* Relation fields (`customer.name`) allowed one level deep; generator emits an oRPC `include` or a joined shape.
* `optimistic: true` requires the mutation input to include the entity id; generator emits a typed updater.
* `audit: true` sets the `reason` field requirement on the mutation input per `data-layer/audit-log`.
* Hook names are `use<PascalCase(queryName)>`; collisions with existing exports fail generation.
* Loading, empty and error states from `states` are exported as `dataStates` for codegen.
DOD:
* Vitest: schema fixtures, each validator rule, generator snapshot for `server`, `live` and `local` modes, optimistic rollback behaviour with a mocked client.
* Example page `customer-invoices` generated hooks render a list from seeded Postgres in Playwright at 375 and 1280, with a mutation reflected in a second browser context within 1 s (live mode).
* Offline test: mutation queued with network off, applied on reconnect (Playwright `context.setOffline`).
* `docs/spec/data.md` with grammar and hook usage; CHANGELOG entry; Linear comment with screenshots and the generated file.
* Drift check passes in gate 1.
EDGE:
* Query with no filter on a multi-tenant table: generator injects tenant scope; validator warns `DATA_UNSCOPED` if the entity is tenant-scoped and no access row exists.
* `page` above 200: capped at 200 with a warning (API limit is 100 per request, hook paginates).
* Field renamed in Drizzle: generation fails at the field check, not at runtime.
* Two queries share a name across pages: fine, hooks are per file.
* `sync: live` on an entity without an Electric shape registered: generator falls back to `server` and warns.
* Route param type mismatch (uuid vs number): validator error using route `validateSearch` types.
DEPS: `spec-builder/schema` (hard), `data-layer/api-layer` (hard for `server` mode). Soft: `data-layer/local-first-sync` (live and local modes), `spec-builder/access-section` (row merge), `tables/view-model-spec` (shared filter type). Unblocks `spec-builder/layout-codegen` state wiring and `spec-builder/conformance-tests`.


## PAP-120 [P1 Build L prio1 Backlog] Generate page scaffolds (layout, component tree, loading/empty/error states) from specs
key=spec-builder/layout-codegen milestone=Codegen and conformance tests agent=Built by Nova with Iris (Component Crafter) on component emi
blockedBy=['PAP-74', 'PAP-114'] blocks=[]
GOAL: Turn a validated page spec into a working page skeleton: the TanStack route file, the layout slot wiring, the component tree as JSX bound to real design-system components, and loading, empty, error, offline and denied states. An agent building a page starts from a rendering scaffold and only writes logic.
SCOPE: In:

* `pnpm spec gen:page <id> [--all] [--check]` in `packages/spec/src/codegen/page.ts` producing for `meta.route = /_app/invoices`:
  * `apps/web/src/routes/_app/invoices.tsx` (created once, never overwritten): exports `Route = createFileRoute('/_app/invoices')({ component: InvoicesPage, validateSearch, staticData: { spec: 'customer-invoices' } })` and imports the generated view.
  * `apps/web/src/generated/pages/customer-invoices.view.tsx` (always regenerated): `<InvoicesView>` rendering the component tree, slots via `useLayout()` from `app-shell/router-layouts`, and a `states` switch using `ui.skeleton`, `ui.emptyState`, `ui.errorState`, `ui.offlineBanner` from `design-system/data-display`, and a `DeniedState` when `useCan('page.view')` is false.
  * `apps/web/src/pages/customer-invoices.logic.ts` (created once): typed stubs for every `logic.actions` entry (`export const actions = {
SPEC(first 1200): * Templates are TypeScript functions in `packages/spec/src/codegen/templates/` using tagged strings, not a template language, so they are type-checked; a `Printer` helper handles indentation and import dedupe.
* Two-file pattern is the rule: `*.view.tsx` is owned by the generator, route and logic files are owned by humans and agents; the generator refuses to touch them unless `--force`.
* Layout template `app|public|focus|kiosk` maps to the shell layouts of `app-shell/router-layouts`; unknown slot names fail generation.
* Unknown component in dev renders `<MissingComponent id>`; in `--check` mode it is an error.
* Search params from `data.queries[].filter[].param: search.*` generate a Zod 4 `validateSearch` schema.
* Generation is deterministic: same spec and registry produce byte-identical output; verified by generating twice in CI.
DOD:
* Vitest: template snapshots for minimal and maximal fixtures, slot mapping, event binding, `--check` drift detection, refusal to overwrite owned files.
* The three example specs from `spec-builder/spec-docs` generate, typecheck and render; Playwright screenshots of each state at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
* Storybook stories appear in the `design-system/storybook` deploy (link).
* Generating a page then running `spec-builder/conformance-tests` passes with zero manual edits.
* `docs/spec/codegen.md` including the two-file pattern; CHANGELOG entry; Linear comment with screenshots and story links.
EDGE:
* Spec changes a component `key`: view regenerates; logic file keeps old handler with a `// TODO(unused)` marker rather than silent deletion.
* Route file already exists with a different `staticData.spec`: generation aborts with the conflict.
* Component tree deeper than 12 levels: warning, still generated.
* Props containing a value the schema marks as default: omitted from JSX to keep output short.
* Spec `layout.template: kiosk` before `app-shell/linux-kiosk` exists: falls back to `focus` with a warning.
* Biome unavailable: emit unformatted with a warning; drift check formats before comparing.
DEPS: `spec-builder/schema` (hard), `design-system/component-spec-mapping` (hard, resolver and registry). Soft: `spec-builder/data-section` (hooks; stubs otherwise), `app-shell/router-layouts` (slot API), `design-system/data-display` (state components; plain fallbacks otherwise). Consumed by `agents/skills-library` `page-from-spec`.


## PAP-121 [P1 Spec M prio2 Backlog] Specify the integrations section (Stripe, Linear, Notion, Drive, Webflow, Miro, Gamma) backed by a connector registry
key=spec-builder/integrations-section milestone=Codegen and conformance tests agent=Built by Quill (Page Spec Writer) with Scout (Library Evalua
blockedBy=['PAP-210', 'PAP-114'] blocks=['PAP-174']
GOAL: Finalise the `integrations` section so a page declares which external systems and capabilities it touches, backed by a connector registry that knows each connector's auth, env vars, MCP server, modes and limits. Validation catches pages using connectors the app has not enabled, env-config knows which secrets to require, and the canvas can draw external systems.
SCOPE: In:

* Zod 4 `IntegrationsSection` in `packages/spec/src/schema/integrations.ts`:

  ```yaml
  integrations:
    - connector: stripe
      capabilities: [billing.readSubscription, checkout.createSession]
      mode: test        # live | test | mock
      onFailure: degrade   # degrade | block | queue
  ```
* Connector registry `packages/spec/src/integrations/registry.ts` (typed, generated from `packages/spec/integrations/*.connector.yaml`): `{ id, name, docsUrl, mcpServer, auth: { kind: apiKey|oauth|webhook, envVars[] }, capabilities: { id, description, scope, rateLimit }, modes: [live, test, mock], webhooks[], owner character }` seeded for `stripe`, `linear`, `notion`, `google-drive`, `webflow`, `miro`, `gamma`, `resend`, `twilio`, `github`, `forgejo`, sourced from `libraries/mcp-servers`.
* Validator rules: `INT_UNKNOWN_CONNECTOR`, `INT_UNKNOWN_CAPABILITY`, `INT_NOT_ENABLED` (not in `a
SPEC(first 1200): * Capability ids are `<area>.<verbNoun>` in camelCase; each maps to a concrete SDK call or MCP tool named in the connector file so reviewers can trace it.
* `mode: mock` requires the connector to declare a mock module path (`packages/integrations/<id>/mock.ts`); Playwright and conformance tests run pages in mock mode by default.
* `onFailure` drives generated state wiring: `degrade` renders the page with the integration block replaced by `ui.integrationUnavailable`; `block` shows the error state; `queue` defers via the offline queue (`realtime/offline-queue`) and shows a pending badge.
* App-level `integrations[].mode` is the default; a page may only narrow (`live` app allows `test` page, not the reverse).
* Registry build validates every connector YAML against `ConnectorSchema` and fails on duplicate capability ids.
DOD:
* Vitest: schema fixtures, registry build from YAML, each validator rule, mode narrowing logic, generated JSON snapshot.
* Eleven connector files committed with capabilities cross-checked against `libraries/mcp-servers` catalogue (reviewer confirms in comment).
* `env-config` boot check fails with a named missing variable when a page enables `stripe` in `live` mode without `STRIPE_SECRET_KEY` (test in CI).
* Example `customer-invoices` page runs in `mock` mode in Playwright with a mocked Stripe checkout; screenshot at 375 and 1280.
* `docs/spec/integrations.md`; CHANGELOG entry; Linear comment with catalogue link.
EDGE:
* Connector deprecated (for example a social platform API sunset): `deprecated: { since, replaceWith }` in the connector file produces a warning; error after the date.
* Page needs a capability the connector lacks (Notion write when only read is catalogued): validator error with a hint to open a `libraries/mcp-servers` issue.
* Same connector listed twice on one page: merged with a warning.
* Live mode in a preview deploy: `app-shell/gh-pages-demo` forces `mock` at build time via env, recorded in the generated JSON.
* Connector env var names collide across connectors: registry build fails.
* Webhook-only connectors (Stripe events) declared on a page: allowed, canvas draws an inbound edge.
DEPS: `spec-builder/schema` (hard), `libraries/mcp-servers` (catalogue content; start from the plan's list if not merged). Soft: `agents/tool-scopes`, `app-shell/env-config`, `spec-builder/app-level-spec`. Consumed by `spec-builder/spec-to-canvas`, `business-core/stripe-billing`, `growth/landing-forms`.


## PAP-122 [P1 Build M prio1 Backlog] Generate conformance tests from specs (access matrix, required components, states) into CI gate 1
key=spec-builder/conformance-tests milestone=Codegen and conformance tests agent=Built by Sentinel (Code Reviewer sub-agent as builder) with 
blockedBy=['PAP-78', 'PAP-115'] blocks=['PAP-64']
GOAL: Derive tests from specs automatically so a page that drifts from its spec fails gate 1 without anyone writing a test: the access matrix is checked against the permission engine, required components and states are asserted in a render, and edge cases become tracked test stubs. Spec drift becomes a red build, not a review comment.
SCOPE: In:

* `pnpm spec gen:tests [id] [--all]` in `packages/spec/src/codegen/tests.ts` writing `apps/web/src/generated/__tests__/<id>.conformance.test.tsx` (Vitest 3 + Testing Library 16, jsdom) and `apps/web/e2e/generated/<id>.routes.spec.ts` (Playwright).
* Unit-level assertions per page: (a) render `<Id View>` with mocked data hooks for every entry of `states` and assert the state component and copy appear; (b) every `components[].key` with `data-spec-key` is present in the success state; (c) every `events[].to` route exists in `routeTree.gen.ts`; (d) access matrix: for each audience in `app.spec.yaml` and each of `page.view` plus `page.action:<name>`, call `can(actorFixture(audience), action, page)` from `identity/rbac-abac` with policies from `spec-builder/access-section` and assert the expected boolean from the compiled matrix; (e) each `edgeCases[]` with `test: unit` becomes `it.todo('
SPEC(first 1200): * Actor fixtures come from `packages/permissions/fixtures/<audience>.json`, generated from `app.spec.yaml` audiences with attributes filled from `segment`.
* Data hooks are mocked with `vi.mock('../generated/<id>.data')` returning state-specific values (`status: 'pending'`, empty array, `error`).
* Denied state test also asserts no data hook was called (no data leakage on denied pages).
* Generated test files are not edited by hand; page-specific tests live beside the logic file.
* `it.todo` count per page is tracked; a page may not move to `status: built` with more than zero todos of `test: unit` (validator rule `SPEC_EDGE_TODO`).
DOD:
* Vitest snapshots of generated tests for minimal and maximal fixtures; a mutated spec (removed component, changed audience) makes the generated test fail (demonstrated in CI with a seeded PR).
* Three example pages produce green conformance suites; total runtime under 20 s.
* Playwright route suite runs for two audiences per page in the matrix at 375 and 1280.
* `reports/spec-conformance.json` appears in a Linear comment through the webhook pipeline.
* `docs/spec/conformance.md`; CHANGELOG entry; Linear comment with green and red run links.
EDGE:
* Page with `public: true`: anonymous actor fixture used; login skipped in Playwright.
* Component conditionally rendered by logic (only when data exists): mark `optional: true` in the spec to exclude it from the presence assertion.
* Access condition depends on resource attributes (`resource.status`): matrix evaluates with a representative fixture per condition branch, both true and false.
* Hundreds of pages: generated Vitest sharded by the CI matrix; each file independent.
* Spec `status: draft`: tests generated but skipped with `describe.skip` and a reason, so drafts do not block gate 1.
* Edge-case id renamed: the imported test no longer matches and becomes a todo; validator warns about orphaned edge tests.
DEPS: `spec-builder/validator` (hard), `quality/ci-gate1` (hard, test job and drift). `spec-builder/access-section` and `identity/rbac-abac` for the matrix; `spec-builder/layout-codegen` for `data-spec-key`; `quality/playwright-matrix` for login fixtures. Consumed by `quality/review-agents` spec-conformance reviewer.


## PAP-123 [P1 Build M prio2 Backlog] Emit the UX-flow graph (pages, transitions, roles) from specs for the canvas view
key=spec-builder/spec-to-canvas milestone=Codegen and conformance tests agent=Built by Nova (Canvas Cartographer). Reviewed by Quill for s
blockedBy=['PAP-132', 'PAP-114'] blocks=[]
GOAL: Compile every page spec plus `app.spec.yaml` into one UX-flow graph (pages, transitions, audiences, entities, external systems) with deterministic layout positions, so the canvas view opens an accurate map of the whole app and updates whenever specs change. Specs draw the map; nobody maintains a diagram by hand.
SCOPE: In:

* `buildFlowGraph(specs: ResolvedPageSpec[], app: AppSpec): FlowGraph` in `packages/spec/src/graph/build.ts` with Zod 4 `FlowGraph` schema:
  `nodes: [{ id, type: page|external|entity|start, label, route?, surface?, audiences[], layoutTemplate?, status, specPath, thumbnail? }]`,
  `edges: [{ id, from, to, kind: navigate|mutation|integration|reads|writes, on?, guard?, audiences[] }]`,
  `groups: [{ id, kind: surface|navSection, label, nodeIds[] }]`, `meta: { app, generatedAt, specHash }`.
* Edge derivation: `events[]` produce `navigate` edges; `data.queries` produce `reads` edges to entity nodes; `data.mutations` produce `writes`; `integrations[]` produce `integration` edges to external nodes; `navigation` roots produce `start` node edges per audience.
* Layout with `elkjs` 0.9 (layered, direction right, groups as compound nodes) run in Node; positions stored in the graph so the canv
SPEC(first 1200): * Node ids are stable: `page:<specId>`, `entity:<entityId>`, `ext:<connector>`, `start:<audience>`; positions are keyed by id so manual overrides in the canvas survive regeneration.
* Audience filtering is precomputed: each node and edge lists audiences that can reach it, computed from `access.view` and edge guards, so the canvas can filter without re-evaluating policies.
* Unreachable pages (no incoming navigate edge and not in navigation) get `flags: [unreachable]`; dead transitions to deprecated pages get `flags: [deadEnd]`; both listed in the PR comment.
* Layout is deterministic given the same input (ELK options fixed, node order sorted); verified by generating twice.
* Graph for 300 pages builds and lays out under 5 s.
DOD:
* Vitest: edge derivation for each kind, audience reachability, flags, stable ids, layout determinism (two runs equal), diff output.
* Graph generated for paperos-template examples and rendered in `collab/canvas-view` (screenshot at 1280 and 1920) or, if the canvas is not merged, in a temporary React Flow dev route.
* PR comment shows the diff summary on a seeded spec change (link).
* `docs/spec/flow-graph.md` documents the schema; CHANGELOG entry; Linear comment with screenshots.
* Drift job in gate 1 fails when specs change without regenerating.
EDGE:
* Cyclic navigation (A to B to A): ELK handles cycles; edges marked `back: true` for styling.
* Page reachable by many audiences (50): audiences stored as ids, not expanded labels, to keep the file small.
* Spec with `x-external` transition to another app: external node of type `external` labelled with the app id.
* Entity referenced by no page: included with `flags: [orphan]` so the data team sees it.
* Thousands of edges: `reads` and `writes` edges collapsed per page-entity pair with counts.
* Thumbnail artifact expired (30-day retention): field omitted, canvas shows a placeholder.
DEPS: `spec-builder/schema` and `spec-builder/app-level-spec` (hard). `collab/canvas-view` for the loader contract (agree node and edge types in a shared file `packages/collab/canvas/types.ts` first). Soft: `quality/playwright-matrix` thumbnails, `spec-builder/integrations-section` external nodes. Consumed by `agents/org-chart-ui` for the same graph loader pattern.


## PAP-124 [P2 Build L prio2 Backlog] Build the spec editor UI with form and YAML views and live preview
key=spec-builder/spec-editor-ui milestone=Spec editor UI agent=Built by Nova with Iris (Component Crafter) on forms. Review
blockedBy=['PAP-70', 'PAP-114'] blocks=[]
GOAL: Let Justin and agents edit page specs inside PaperOS with a form view for people who do not want YAML, a YAML view with live validation for those who do, and a preview of the generated page and its place in the flow graph. Saving opens a PR, so the repo stays the source of truth.
SCOPE: In:

* Routes `/_app/dev/specs` (list) and `/_app/dev/specs/$id` (editor) in `apps/web`, surface `developer|staff`, access `staff.admin` and `agent.*` read, `staff.admin` write.
* List: grid from `tables/grid-view` if merged, else a simple table: id, title, route, surface, owner, status, validation status, last commit; filters by status and surface.
* Editor layout via `design-system/layout-components`: `SplitPane` with a tabbed left pane (Form, YAML) and right pane (Preview, Graph, Issues).
* Form view: section forms built with `react-hook-form` 7 and `@hookform/resolvers` zod adapter over the `PageSpec` Zod 4 schema; component tree editor as a nested list with add-from-registry (searchable list from `registry.json` with prop forms generated from each component's JSON Schema, enums as selects, defaults shown); access editor with audience multiselect and condition builder reusing the fil
SPEC(first 1200): * Optimistic locking: save sends the base commit SHA; server returns `CONFLICT` if the file changed; UI offers a three-way diff (`diff` 7) and rebase.
* Validation issues render in the Issues tab and as gutter markers in YAML and inline messages in Form, keyed by `path`.
* Keyboard: `Cmd/Ctrl+S` save, `Cmd/Ctrl+Shift+V` toggle view, registered with `input/command-registry` when present.
* Unsaved changes guard on navigation.
* Telemetry: `spec_editor.save` audit event with spec id and PR URL (`data-layer/audit-log`).
DOD:
* Playwright: open example spec, edit title in Form, see YAML update, introduce an error in YAML, see diagnostic, fix, save, PR link appears (mocked Forgejo in CI); screenshots at 768, 1024, 1280, 1536 and 1920 in light and dark; 320 and 375 show a read-only YAML view with a "desktop recommended" notice.
* Vitest: form to YAML round trip preserves comments and `x-*` keys (uses `yaml` document API), lock conflict handling, worker validation.
* axe clean on both tabs; keyboard-only completion of the flow recorded as video (`quality/video-replays` flow file).
* `docs/spec/editor.md`; CHANGELOG entry; Linear comment with Pages preview link and video.
* Justin edits one real spec and the PR merges (comment with the PR).
EDGE:
* YAML with comments and anchors: Form edits patch the `yaml` Document rather than re-serialising, so comments survive.
* Registry component removed after the spec referenced it: Form shows the node with a warning and a replace action.
* Very large spec (300 components): component tree virtualised; preview compile capped at 5 s with a fallback outline.
* Offline: editing continues, save disabled with a reason, draft kept locally.
* Two people edit the same spec: second saver gets the conflict flow; presence indicator from `realtime/presence` shows who else has it open.
* Worker crash: diagnostics show "validation unavailable" and saving requires an explicit confirm.
DEPS: `spec-builder/schema` (hard), `design-system/layout-components` (hard). `spec-builder/validator` library API, `spec-builder/layout-codegen` templates, `forge/in-app-git` or direct Forgejo API for save, `design-system/component-spec-mapping` registry. Soft: `tables/grid-view`, `tables/filter-sort-group-ui`, `spec-builder/spec-to-canvas`.


## PAP-125 [P1 Docs M prio2 Backlog] Document the spec builder with three fully specified example pages (customer list, staff dashboard, agent console)
key=spec-builder/spec-docs milestone=Spec editor UI agent=Built by Quill (Page Spec Writer, Changelog Scribe). Reviewe
blockedBy=['PAP-115'] blocks=[]
GOAL: Document the spec builder end to end and ship three fully specified, generated and screenshotted example pages (customer invoice list, staff dashboard, agent console) that agents copy when writing new specs. The examples are executable: they validate, generate, pass conformance and render in the template app.
SCOPE: In:

* `specs/pages/examples/customer-invoices.spec.yaml` (surface customer, `data` live query on `invoice`, `markPaid`-style mutation replaced by `payInvoice` integration with Stripe in mock mode, five edge cases), `specs/pages/examples/staff-dashboard.spec.yaml` (surface staff, `ui.dashboardBlocks` from `tables/dashboard-blocks` or `ui.responsiveGrid` fallback, three queries with aggregates, access with `staff.*` wildcards and a condition), `specs/pages/examples/agent-console.spec.yaml` (surface agent, lists prompt sessions from `collab/prompt-log-store`, actions restricted to `agent.builder` and `staff.admin`, `deny` for customers, offline and denied states).
* Each example annotated with `#` comments explaining every section, kept under 150 lines.
* Generated artifacts committed: route, view, logic stubs, data hooks, conformance tests, flow graph, access matrix (`docs/spec/examples/<
SPEC(first 1200): * Pages use the docs engine frontmatter (`title`, `owner: Quill`, `audience: developer`, `tags: [spec]`, `updated`).
* Every code block referencing a file is included via the docs engine `<FileRef path=... lines=...>` component so it never goes stale; a docs lint (`pnpm docs:lint`) fails on missing paths.
* Screenshots are pulled from the Playwright artifacts of the examples and stored in `docs/spec/examples/<id>/*.png` with light and dark variants.
* Reading order and sidebar defined in `docs/spec/_meta.yaml`.
* Language rules: second person, short sentences, one concept per heading, no unexplained acronyms; a glossary section defines spec, surface, audience, slot, state, transition.
DOD:
* Three examples pass `paperos-spec validate --strict`, `gen:page`, `gen:data`, `gen:tests` and their conformance suites in CI.
* Playwright screenshots of each example in success, empty and denied states at 375 and 1280, light and dark, embedded in the docs.
* Docs render in the in-app docs engine (or GitHub Pages fallback if it is not merged) with working `FileRef` includes and no lint errors; link in comment.
* A fresh Claude Code session given only `docs/spec/workflow.mdx` writes a valid spec for a fourth page in one attempt (transcript linked).
* CHANGELOG entry; Linear comment with docs link, screenshots and the transcript.
EDGE:
* A dependency the example uses is not merged (dashboard blocks): example falls back to the listed alternative component and notes it in a callout with the blocking issue key.
* Generated files drift when generators change: examples are part of the drift job, so generator PRs must regenerate them.
* Docs engine unavailable: the same MDX builds with a minimal Vite MDX setup to Pages.
* Example ids collide with real app pages later: examples live under `examples/` namespace and route prefix `/_app/examples/*`, excluded from production navigation.
* Screenshots flake between runs (timestamps in seeded data): seeds use fixed dates.
* FAQ answers become wrong after schema changes: each FAQ entry cites the spec version it applies to.
DEPS: `spec-builder/validator` (hard). Soft but expected: `spec-builder/layout-codegen`, `spec-builder/data-section`, `spec-builder/conformance-tests`, `spec-builder/access-section`, `collab/docs-engine`, `quality/playwright-matrix`. Consumed by `agents/skills-library` `page-from-spec`, `spec-builder/spec-authoring-skill`, `app-shell/template-docs`.


## PAP-126 [P2 Spec M prio2 Backlog] Define the business profile section of app.spec.yaml: industry, audiences, terminology map, locale, currency and tax regime, enabled modules; codegen, templates and the migration agent read it
key=spec-builder/business-profile milestone=Spec editor UI agent=Written by Quill (Page Spec Writer) with Scout for the taxon
blockedBy=['PAP-27', 'PAP-28', 'PAP-117'] blocks=[]
GOAL: "One-size-fits-all software that then adapts to every single type of business" needs a place where the adaptation is declared. Today that knowledge would be scattered across seed packs (`migration/business-templates`), tenant settings and page copy. This issue adds a `business:` section to `app.spec.yaml`, a vocabulary of industries and their defaults, and a terminology map that renames core concepts (customer becomes patient, guest, client, member, student) consistently across UI strings, navigation, table names in views, notification templates and agent prompts. The migration agent's interview fills it in; codegen and templates read it.
SCOPE: In:

* Schema addition in `packages/spec/src/app-spec.ts`: `business: { industry: <taxonomy id>, subtype?, audiences: [{ id, kind: customer|staff|partner|agent, label, plural }], terminology: { customer: 'Patient', order: 'Appointment', ... }, locale: { default, enabled[], timezone }, currency: { default, enabled[] }, taxRegime: 'us-sales-tax' | 'vat' | 'gst' | 'none', modules: [...] (delegates to app-shell/feature-modules), compliance: ['hipaa'|'pci'|'gdpr'|...] flags for future gates }`.
* Industry taxonomy `packages/spec/src/industries.yaml`: 40 top-level industries with subtypes derived from NAICS sectors and the five business templates, each with default terminology, default modules, default audiences and example entities; ADR explains the choice of a small internal taxonomy over full NAICS.
* Terminology resolution: `t.term('customer', { plural: true })` helper in `packages/i18n` t
SPEC(first 1200): * Terminology keys are a closed set of 30 core concepts (`customer`, `order`, `product`, `service`, `staff`, `location`, `appointment`, `invoice`, `project`, `task`, ...) documented with definitions; unknown keys fail validation.
* Every term has singular and plural in the source locale; translations follow catalogs.
* Changing `terminology` is a spec change that regenerates pages (`spec-builder/layout-codegen`) and is reviewed by the spec-conformance reviewer like any spec change.
* The profile is available at runtime as `useBusinessProfile()` for conditional UI (for example show tax fields only under `vat`).
* Templates and the taxonomy are data, not code; adding an industry is a YAML PR.
DOD:
* Template app switched between the clinic and agency profiles by editing `app.spec.yaml` alone: navigation labels, table headers, empty states and notification templates change accordingly (before and after screenshots at 1280 and 375, both locales `en` and `es`).
* Validator catches an unknown audience, an unknown term, an invalid currency (tests).
* `pnpm spec business:apply clinic` produces a valid profile; the migration agent interview writes an equivalent one in a recorded run.
* The five seed packs declare their industry and are selected automatically.
* Docs, ADR, `CHANGELOG.md`, Linear comment. Justin reviews the industry list and terminology defaults for business realism in the same Needs Justin item that `migration/business-templates` already files (one item, not two).
EDGE:
* A business that fits two industries (a gym with a cafe): `industry` plus `secondaryIndustries[]` merging modules and terminology with explicit conflict resolution in the profile.
* Term collisions after renaming (`customer` and `member` both mapped to "Member"): validator warns; codegen disambiguates in labels.
* Plural forms in languages where the term changes by case: the map stores the base term; catalogs carry full forms per message.
* Tax regime `none` for a non-profit: finance module hides tax fields but keeps the ledger.
* Apps generated before this issue: `pnpm spec business:apply generic` fills a neutral profile so validation passes unchanged.
DEPS: `spec-builder/app-level-spec` (the file this extends), `app-shell/feature-modules` (`modules:` semantics), `app-shell/i18n-l10n` (term localisation). Soft: `spec-builder/layout-codegen`, `spec-builder/spec-editor-ui`, `migration/business-templates`, `migration/migration-agent`, `business-core/finance-data-model`, `business-core/tax-compliance`.
