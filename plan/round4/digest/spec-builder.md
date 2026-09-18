# Round 4 digest: Spec Builder (`spec-builder`)

Features: 58 (36 covered, 8 partial, 14 gap). New issues: 14 (0 children, 14 gaps, 2 deferred to v0.2). Amendments: 8. Cross-project suggestions: 5.

Benchmarks: OpenAPI and AsyncAPI (oasdiff, generators); Storybook stories and autodocs as specs; Figma dev mode; Cucumber and Gherkin scenarios; Amplication, Plasmic and Retool page schemas; Backstage software templates; JSON Schema and Zod; Permission policy DSLs (Cedar, OPA); Spec diffing and versioning tools; Prisma and Drizzle schema-first codegen; Next.js metadata, sitemap and OG generation; Lighthouse CI budgets.

## What was missing and why it matters

1. The golden path (§4) promises Drizzle tables, a reviewed migration, oRPC entity routers and shape registrations at checkpoint C3; PAP-362 registers nine generators and none writes a table or a router. An Opus L issue owns the backend generators, otherwise generated hooks call procedures that do not exist.
2. PAP-117 leaves `entities[].fields` untyped while PAP-360 writes fields, PAP-361 derives columns and forms, and the backend generator needs column types. One field grammar (types, constraints, relations, `internal`, `computed`, `pii`) aligned with PAP-164 is now the P0 spec they all import.
3. Four issues write spec keys the v1 unknown-key rule rejects: `help` (PAP-380), `comments` (PAP-361), `flags` and `modules` (PAP-366, PAP-467). A v1.1 additive extension with `seo` and `budgets` fixes the schema once; three small Build issues compile the new sections.
4. Mutation `input` is `Record<string, ScalarType>`, so generated forms cannot validate and servers re-derive rules; input constraints generate one Zod schema shared by hook, router and `ui.form`. A semantic spec diff on PRs gives the spec-conformance reviewer an `oasdiff`-style input.
5. Five DoDs benchmark against fixtures nobody generates (300 specs, 60-page apps, 300-component spec); a Haiku corpus generator ships them. Reverse codegen, page templates and generated MSW mocks reduce the blank-file starts an agent otherwise faces; versioning tooling and analytics events are filed honestly as v0.2.

## New issues

| Key | Title | Parent | Size | Model / effort | Priority | Milestone | Deferred |
|---|---|---|---|---|---|---|---|
| `r4/spec-builder/entity-field-grammar` | Define the entity field grammar in app.spec.yaml: field types, constraints, relations, `internal` and `computed` flags shared by entity pages, forms and backend codegen | - | S (2) | Opus 5 / high | 1 | Spec schema and validator |  |
| `r4/spec-builder/schema-v1-1-extensions` | Page spec v1.1 sections: `flags`, `modules`, `comments`, `help`, `seo`, `budgets` with codemod stub, JSON Schema and validator rules | - | M (3) | Opus 5 / high | 2 | Spec schema and validator |  |
| `r4/spec-builder/entity-backend-codegen` | Generate the backend from entities: Drizzle tables with RLS, a reviewed migration, oRPC entity routers and Electric shape registrations as `paperos gen` plugins | - | L (5) | Opus 5 / high | 1 | Codegen and conformance tests |  |
| `r4/spec-builder/mutation-input-constraints` | Mutation input constraints and form derivation: typed `input` fields with validation rules, generated Zod for client and server, `ui.form` field lists | - | M (3) | Sonnet 5 / high | 2 | Codegen and conformance tests |  |
| `r4/spec-builder/spec-diff-pr-comment` | Semantic spec diff: section-level changes, access matrix delta and breaking flags posted as a PR comment and consumed by the spec-conformance reviewer | - | M (3) | Sonnet 5 / medium | 2 | Codegen and conformance tests |  |
| `r4/spec-builder/flags-modules-compile` | Compile `flags` and `modules` sections: route guards through the flag service, `MODULE_DISABLED` handling in codegen, flag-gated nodes on the flow graph | - | S (2) | Sonnet 5 / medium | 3 | Codegen and conformance tests |  |
| `r4/spec-builder/seo-public-metadata` | Public page metadata from specs: `seo` section to `<head>` tags, Open Graph image route, sitemap and robots generation per app | - | S (2) | Sonnet 5 / medium | 3 | Codegen and conformance tests |  |
| `r4/spec-builder/page-budgets` | Per-page performance budgets from specs: `budgets` section compiled into Lighthouse CI assertions, `size-limit` entries and k6 p95 thresholds | - | S (2) | Sonnet 5 / medium | 3 | Codegen and conformance tests |  |
| `r4/spec-builder/msw-fixtures-from-data` | Generate MSW handlers and fixture rows from the data section for Storybook stories, the editor preview and Gate 3 story capture | - | S (2) | Sonnet 5 / medium | 3 | Codegen and conformance tests |  |
| `r4/spec-builder/spec-fixture-corpus` | Synthetic spec corpus generator: 300 valid page specs and 60-page stress apps for validator, pipeline, editor and diff benchmarks | - | S (2) | Haiku 4.5 / low | 2 | Spec schema and validator |  |
| `r4/spec-builder/reverse-codegen-infer` | Reverse codegen: `paperos-spec infer <route>` drafts a page spec from an existing route file, component tree and data hooks for retrofitting unspecced pages | - | M (3) | Sonnet 5 / medium | 3 | Spec editor UI |  |
| `r4/spec-builder/page-spec-templates` | Page spec templates: `paperos-spec new --template dashboard|wizard|report|settings|kiosk|landing|detail-tabs` with filled examples and a template lint | - | S (2) | Sonnet 5 / medium | 3 | Spec editor UI |  |
| `r4/spec-builder/spec-versioning-tooling` | Spec versioning tooling: version registry, codemod helpers, `paperos-spec migrate --dry-run`, `x-deprecated` metadata with `SPEC_DEPRECATED` and the weekly 300-fixture rehearsal | - | M (3) | Sonnet 5 / medium | 4 | Spec editor UI | yes |
| `r4/spec-builder/analytics-events-section` | Spec `analytics` section: product events per action and view compiled into the privacy-first event pipeline with a generated event catalogue | - | S (2) | Sonnet 5 / medium | 4 | Spec editor UI | yes |

## Feature matrix

| Feature | Status | Covered by | Note |
|---|---|---|---|
| Page spec schema (meta, purpose, logic, access, data, integrations, layout, components, states, events, edge cases) | covered | PAP-114 | Keystone, Ready for Claude. |
| App spec (audiences, navigation, entities, integrations, defaults, theme) | covered | PAP-117 |  |
| Entity field grammar (types, constraints, relations, internal/computed) | gap | r4/spec-builder/entity-field-grammar | PAP-117 leaves fields untyped; three consumers. |
| Business profile (industry, terminology, locale, currency, tax, modules) | covered | PAP-126 |  |
| Access section compiled to policies, SQL and matrix | covered | PAP-116 |  |
| Data section (queries, mutations, sync mode) and typed hooks | covered | PAP-311, PAP-312, PAP-313 |  |
| Mutation input constraints and form derivation | gap | r4/spec-builder/mutation-input-constraints | input is Record<string, ScalarType>. |
| Integrations section and connector registry | covered | PAP-121 |  |
| Feature-flag guards and module requirements per page | gap | r4/spec-builder/schema-v1-1-extensions, r4/spec-builder/flags-modules-compile | PAP-366 and PAP-467 name `flags`; PAP-114 lacks it. |
| Comments anchor declaration per page | gap | r4/spec-builder/schema-v1-1-extensions | PAP-361 writes `comments:`; v1 rejects it. |
| Help, tour and shortcuts declaration | gap | r4/spec-builder/schema-v1-1-extensions | PAP-380 needs it. |
| Public page SEO metadata, sitemap, robots, OG images | gap | r4/spec-builder/seo-public-metadata |  |
| Per-page performance budgets | gap | r4/spec-builder/page-budgets | PAP-87 and PAP-242 hand-maintain lists. |
| Product analytics events declared in specs | gap | r4/spec-builder/analytics-events-section | Deferred v0.2. |
| Spec i18n: message ids, extraction, pseudo-locale | covered | PAP-375 |  |
| Logic as executable DSL or state machine | partial | PAP-114, PAP-314 | Stubs by design (non-goal: visual app builder). Not issued. |
| Notification kinds emitted per action | partial | PAP-114 | logic.effects prose only; not issued. |
| Validator CLI, rules, baseline, CI annotations | covered | PAP-115 | Props validation amendment proposed. |
| Route coverage report | covered | PAP-115 | `paperos-spec routes`. |
| Semantic spec diff on PRs (oasdiff analogue) | gap | r4/spec-builder/spec-diff-pr-comment |  |
| Spec versioning, codemods, deprecations, rehearsal | partial | PAP-114, r4/spec-builder/spec-versioning-tooling | Skeleton only by FIX-5; tooling deferred v0.2. |
| Layout and component tree codegen with two-file ownership | covered | PAP-314, PAP-315, PAP-316 |  |
| State switch, slot mapping, action binding, search params | covered | PAP-315 |  |
| Storybook stories per state | covered | PAP-314 |  |
| Generated MSW handlers and fixture rows for stories and preview | gap | r4/spec-builder/msw-fixtures-from-data | Three consumers mock differently. |
| Conformance tests (access matrix, components, states) in Gate 1 | covered | PAP-122 |  |
| Permission matrix tests at policy, HTTP and UI levels | covered | PAP-64 | identity. |
| Edge-case scenarios derived from specs (Gate 4) | covered | PAP-85, PAP-249 | quality. |
| UX-flow graph with ELK layout and diff | covered | PAP-123 | Relation edges amendment proposed. |
| Entity-derived CRUD page specs and ViewSpecs | covered | PAP-361 | Needs field grammar and `comments` key. |
| Backend from entities: Drizzle tables, RLS, migration, oRPC routers, shapes | gap | r4/spec-builder/entity-backend-codegen | Golden path §4 promises it; no owner. |
| Whole-app pipeline with manifest, cache, determinism, drift | covered | PAP-362 | Needs backend adapters. |
| Seed generator for demo tenants | covered | PAP-362, PAP-363 | app-shell owns the starter kit seed. |
| Navigation generation with runtime `useCan` | covered | PAP-117 |  |
| OpenAPI from generated routers | covered | PAP-269 | data-layer. |
| Reverse codegen: infer a spec from an existing route | gap | r4/spec-builder/reverse-codegen-infer | Retrofit path for SPEC_ROUTE_UNCOVERED. |
| Page spec templates for non-CRUD pages | gap | r4/spec-builder/page-spec-templates | Backstage-style starting points. |
| Three executable example pages and workflow docs | covered | PAP-125 |  |
| Synthetic fixture corpus for benchmarks | gap | r4/spec-builder/spec-fixture-corpus | Five DoDs cite unbuilt fixtures. |
| Authoring skill: interview to page spec to issue | covered | PAP-118 |  |
| App interview: paragraph to app.spec.yaml | covered | PAP-360 |  |
| Spec editor: list, YAML, worker validation, save to PR | covered | PAP-376 |  |
| Spec editor: form view, component tree, two-way sync | covered | PAP-377 |  |
| Spec editor: live preview, graph tab, keyboard, a11y | covered | PAP-378 |  |
| Multiplayer editing of one spec | partial | PAP-124 | Out of scope by PAP-124; PRs are the merge point. Not issued. |
| Comments on specs in the editor | covered | PAP-377, PAP-131 | Anchors on data-spec-key. |
| Spec approval workflow | covered | PAP-376, PAP-49 | PR review is the approval. |
| VS Code completion via JSON Schema | covered | PAP-114 |  |
| Spec status dashboard | covered | PAP-376 | List with validation status. |
| Component id registry with props schemas | covered | PAP-74 | design-system. |
| Props validation against component schemas at validate time | partial | PAP-115, PAP-74 | Amendment: SPEC_BAD_PROPS. |
| Business templates and seed packs | covered | PAP-207, PAP-427 | migration, deferred. |
| Template upgrade with spec migration | covered | PAP-430 | app-shell; consumes versioning CLI. |
| Contract package, conformance suite, kernel wiring | covered | PAP-467, PAP-470, PAP-473 |  |
| Generator plugin interface | covered | PAP-467, PAP-362 |  |
| Spec-conformance reviewer agent input | partial | PAP-244, r4/spec-builder/spec-diff-pr-comment | Reviewer exists; gets a semantic diff input. |
| Accessibility requirements per component in specs | partial | PAP-73, PAP-82 | Enforced at component level; not per spec. Not issued. |
| Watch mode for `paperos gen` | partial | PAP-362 | Explicitly later. Not issued. |

## Amendments to existing specs

- **PAP-114** (Spec): Reserved for v1.1 (additive, `r4/spec-builder/schema-v1-1-extensions`): top-level keys `flags`, `modules`, `comments`, `help`, `seo`, `budgets`. In v1 they parse as `z.unknown().optional()` with warning `SPEC_RESERVED_KEY` so consumers that already write them (PAP-380, PAP-361, PAP-366) are not rejected by the unknown-key rule.
- **PAP-115** (Spec): Rule `SPEC_BAD_PROPS`: component `props` are validated against the PAP-74 registry JSON Schema for that id (Ajv, strict); skipped with one warning when the registry is absent. Rule `SPEC_TEMPLATE_PLACEHOLDER`: any `{{...}}` left in a spec is an error (templates issue).
- **PAP-117** (Spec): `entities[].fields` is typed by `r4/spec-builder/entity-field-grammar` (`FieldSchema`); until it merges, `fields` parses as `z.array(z.unknown())` with warning `APP_FIELDS_UNTYPED`. The implicit columns (`id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at`, `created_by`) are never declared.
- **PAP-123** (Spec): Derive `relation` edges between `entity` nodes from `entities[].fields[].relation` (field grammar) labelled with the field id and `one|many`; self-relations render as loops; entity nodes with zero pages and zero relations are the `orphan` flag. Nodes carry `flags[]` from the page `flags` section when present.
- **PAP-361** (Dependencies): Hard on `r4/spec-builder/entity-field-grammar` for column, option and `owner` derivation. The `comments: { anchor }` key requires `r4/spec-builder/schema-v1-1-extensions`; until it lands emit `x-comments` and let the codemod promote it.
- **PAP-362** (Scope): Register the `db-schema`, `db-migration`, `routers` and `shapes` generators from `r4/spec-builder/entity-backend-codegen`, plus `forms` (mutation constraints), `mocks`, `sitemap` and `budgets`, each as a ten-line adapter; order: `app` before `db-schema` before `routers` before `data-hooks`. The determinism test and `gen-check` cover them.
- **PAP-360** (Spec): Fields proposed by the interview use the `Field` grammar (`r4/spec-builder/entity-field-grammar`): money nouns become `currency` with `format.currency` from the profile, dates become `date` or `dateTime` by phrasing, people nouns become `relation(user)`, and every `email|phone` field gets `pii: high`.
- **PAP-378** (Edge cases): Preview of a page with `sync: live` queries must not open Electric shapes inside the iframe: it uses the generated MSW handlers and shape snapshot from `r4/spec-builder/msw-fixtures-from-data`; until that lands, `live` hooks are stubbed with an empty snapshot and a banner in the preview.

## Cross-project suggestions

- **data-layer**: Review generated Drizzle tables, RLS policies and routers from `r4/spec-builder/entity-backend-codegen` against PAP-32, PAP-34 and PAP-268 conventions. The generator writes into data-layer-owned packages through their registration APIs; Forge should co-own the templates and add the generated app schema to `pnpm db:check`.
- **design-system**: Mark text-bearing props `i18n: true` and expose `ui.featureUnavailable` and `ui.form` field-list props in the PAP-74 registry. PAP-375 wraps only flagged props; the flags compile issue needs a feature-unavailable state; mutation constraints emit a field list `ui.form` must accept.
- **quality**: PAP-244 spec-conformance reviewer consumes `spec-diff.json` and blocks on `breaking: true` without a Breaking section. r4/spec-builder/spec-diff-pr-comment produces the artefact; the reviewer is where it turns into a verdict.
- **app-shell**: PAP-366 exposes `useFlags(ids)` and a server-side evaluator the generated route guard can call; reserve `page.*` flag family. r4/spec-builder/flags-modules-compile compiles the `flags` section against it.
- **identity**: PAP-64 records flag-gated actions as `conditional` in the permission matrix. Pages behind flags otherwise appear as denied or granted depending on the fixture tenant.
