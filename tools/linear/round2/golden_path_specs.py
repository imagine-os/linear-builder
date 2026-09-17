import json, os

R2 = os.path.dirname(os.path.abspath(__file__))
ISSUES = []

def issue(key, project, milestone, phase, type_, surfaces, priority, size, title, blocked_by, blocks, body):
    ISSUES.append({"key": key, "project": project, "milestone": milestone, "phase": phase, "type": type_,
                   "surfaces": surfaces, "priority": priority, "size": size,
                   "state": "Ready for Claude" if not blocked_by else "Backlog",
                   "title": title, "blockedBy": blocked_by, "blocks": blocks, "description": body.strip() + "\n"})

# ---------------------------------------------------------------- spec-builder
issue("gp/spec-builder/app-interview", "spec-builder", "Codegen and conformance tests", "P1", "Build", ["Developer", "Agent"], 1, "M",
      "Write the app interview skill: one paragraph idea to `app.spec.yaml` (business profile, audiences, entities, navigation, modules) in at most six questions with `--yes` defaults",
      ["PAP-117", "PAP-118"], [], r"""
**Goal**

Turn a one-paragraph idea into a validated `specs/app.spec.yaml` in under ninety seconds, asking at most six questions and none when `--yes` is passed. PAP-118 interviews for one page; this skill interviews for the whole app and is checkpoint C1 of the golden path (document "New App in Ten Minutes"). Quill runs it; `paperos create --idea` invokes it.

**Scope**

In:

* `.claude/skills/app-interview/SKILL.md` (under 1500 words, frontmatter per PAP-105 lint) with `references/question-bank.md` (exactly six questions, each with a proposal rule), `templates/app.spec.yaml`, and `scripts/` run with `tsx`: `propose.ts` (paragraph to draft), `ask.ts` (renders the six questions with proposals through `@clack/prompts` or answers them from the paragraph when `--yes`), `write.ts` (writes and validates), `issues.ts` (open questions to Backlog issues in the new Linear project).
* Proposal rules: audiences from actor nouns as PAP-55 ids (`customer.<noun>`, `staff.<noun>`, always `agent.builder`); entities from object nouns with `name`, `status` (select) and `owner` (relation user) fields plus fields the paragraph names, typed with the PAP-164 field type union; first verb per audience becomes the landing route; modules proposed from the PAP-264 registry keywords (money mentions enable `payments`, dates enable `scheduling`); business profile per PAP-126 with defaults `en-US`, `USD`, no tax regime.
* Output: `specs/app.spec.yaml` valid against PAP-117 with zero validator warnings, `x-open-questions` for anything unresolved, and `.paperos/interview.json` (questions, proposals, answers, elapsed ms) for the golden path report.
* Non-interactive mode `--yes` and `--answers <file>` for the acceptance test; interactive mode caps each question at one screen.
* Skill tests in `packages/agents/skills-tests/app-interview/` with the three canned ideas (clinic, agency, retail) and snapshot outputs.

Out: page-level interviews (PAP-118), writing page specs (entity-derived page specs issue), the spec editor (PAP-124), translating copy (PAP-27).

**Spec**

* The model call is one `claude-fable-5-1` request with the paragraph, the question bank and the PAP-117 JSON Schema as a tool schema; output is the draft `AppSpec` plus one proposal string per question; a second call is allowed only to repair validator errors; total budget 0.50 USD per run, enforced by the skill wrapper.
* Question order and ids are fixed: `audiences`, `entities`, `firstVerbs`, `modules`, `profile`, `neverHappen`; `--answers` maps id to value; unknown ids fail with exit 2.
* Entity naming: singular kebab id, `table` plural snake_case, `label`/`plural` Title Case; collisions with template entities (`tenant`, `user`, `workspace`, `file`, `audit_event`) are renamed with a `-record` suffix and reported.
* Audiences always include `agent.builder` with `kind: agent`; `defaults.access.deny: [agent.*]` stays from the template so agents get explicit grants only.
* `navigation` gets one item per entity per audience that may read it plus the settings item for staff; icons from the PAP-72 icon set by keyword map, `layout-grid` fallback.
* `neverHappen` answers are stored verbatim under `x-open-questions[].text` with `kind: constraint` and copied into `edgeCaseSeeds` for PAP-85.
* Elapsed time from invocation to written file is stamped as checkpoint `C1` in `.paperos/golden-path.json` when the driver is present.

**Interface contract**

Provides: `runAppInterview({ idea, name, yes, answers, cwd }): Promise<{ specPath, interviewPath, openQuestions, elapsedMs }>` from `packages/cli/src/interview.ts` (thin wrapper around the skill scripts so the driver can call it without a shell), and the six question ids as `INTERVIEW_QUESTIONS`. Consumes: `AppSpec` schema and `validateAppSpec` (PAP-117), question grouping conventions and `context.ts` from PAP-118, `FieldType` union (PAP-164, soft: string until it merges), module registry keywords (PAP-264, soft: static list), `BusinessProfile` (PAP-126, soft: defaults only). Consumed by: golden path driver, golden path acceptance test, PAP-29.

**Test plan**

* Unit: `propose.ts` on the three canned ideas produces the snapshot `AppSpec`s; entity collision renaming; module keyword mapping; `--answers` with an unknown id exits 2.
* Contract: every output validates against PAP-117 with zero warnings; `x-open-questions` schema.
* Skill test: mocked model response fixture drives `ask.ts --yes` end to end in under 5 s without network; real-model run recorded once per week by PAP-110 eval harness with a golden score.
* Budget: wrapper aborts on a third model call; test asserts the abort.

**Definition of done**

* Skill merged with the six scripts, question bank and templates; `pnpm skills:lint` clean.
* `pnpm tsx scripts/ask.ts --idea "<clinic paragraph>" --yes` writes a valid `app.spec.yaml` in under 90 s wall clock on the CI runner (timed in the test).
* Three canned ideas committed as fixtures with snapshots; snapshots reviewed by Sentinel for sensible audiences and entities.
* Docs page `docs/spec/app-interview.mdx` with the six questions and examples; CHANGELOG entry; Linear comment with the fixture outputs.

**Edge cases**

* Paragraph names no staff audience (a pure consumer app): staff audience is still created with `staff.admin` because settings pages require it; noted in `x-open-questions`.
* Paragraph is in another language: proposals are made in that language for labels, ids stay English; `defaultLocale` set from detected language.
* Paragraph mentions more than twelve entities: the first eight by mention count are created, the rest become one Backlog issue "Add remaining entities" listing them.
* Model returns invalid YAML or a schema violation twice: skill writes the last draft with `status: draft`, exits 3, and the driver stops at C1 with the validator output.
* Reserved app names or entity ids equal to a route segment (`settings`, `docs`): renamed with a suffix and reported.

**Dependencies**

Hard: PAP-117 (`AppSpec` and `gen:app`), PAP-118 (skill conventions, `context.ts`). Soft: PAP-164 field types, PAP-264 module registry, PAP-126 business profile, PAP-105 skill lint. Blocks the golden path driver.

**Agent**

Built by Quill (Spec Author) with Forge for the CLI wrapper; reviewed by Sentinel (spec-conformance reviewer) and Atlas for question quality.

**Size**

M: one skill, six scripts, three fixtures, one model prompt to tune.

**Demo**

Terminal recording: paragraph in, six proposals shown, `--yes`, `app.spec.yaml` printed and validated in under 90 seconds; attached to the PR and the Linear comment.
""")

issue("gp/spec-builder/entity-pages", "spec-builder", "Codegen and conformance tests", "P1", "Build", ["Developer", "Customer", "Staff"], 1, "M",
      "Build entity-derived page specs: `pnpm spec gen:entity-pages` derives list, detail, form and settings pages per entity and audience with view specs, comment anchors and access rules",
      ["PAP-117", "PAP-116", "PAP-161"], [], r"""
**Goal**

Give every entity in `app.spec.yaml` a complete, spec-first CRUD surface without anyone writing YAML: a list page (grid view), a detail page (fields, comments, activity) and a form page (create and edit) per audience that may read or write it, plus the staff settings pages. These generated specs are ordinary `page.spec.yaml` files that PAP-120 and PAP-119 then turn into code, so the golden path produces real pages, not placeholders.

**Scope**

In:

* `pnpm spec gen:entity-pages [--entity <id>] [--check]` in `packages/spec/src/codegen/entity-pages.ts` writing `specs/pages/<surface>/<entity>-list.spec.yaml`, `<entity>-detail.spec.yaml`, `<entity>-form.spec.yaml` for each `(entity, audience kind)` pair where the access rules grant `read` (list, detail) or `create|update` (form).
* Derivation rules from `entities[]` and `audiences[]` in PAP-117: fields to columns, `status` select to kanban option, date range to calendar option, `owner` relation to ownership filter for customers, `searchable` to the search slot.
* Per generated page: `meta` with `generated: entity-pages` and the entity hash, `access` in the PAP-116 format (`customer.*` read own rows via `owner = actor.id`, `staff.*` read and write all, `agent.builder` read), `data` section referencing PAP-119 queries (`list`, `byId`, `create`, `update`, `archive`), `layout.template: app`, `components` using registered ids only (`ui.dataGrid`, `ui.recordHeader`, `ui.fieldList`, `ui.commentThread`, `ui.activityFeed`, `ui.form`), `states` copy from `defaults`, `edgeCases` seeded with empty, huge (10k rows), offline, denied and concurrent edit.
* A `ViewSpec` per list page in `packages/views/src/generated/views.ts` per PAP-161 (`kind: grid`, fields from entity, default sort `updated_at desc`, `visibility: shared`, permissions from the audience), plus kanban and calendar variants when the option fields exist.
* Comment anchors: every detail page declares `comments: { anchor: entity:<type>:<id> }` matching the PAP-131 anchor grammar; every list row carries `data-spec-key` for pins.
* Staff settings pages `settings-members`, `settings-roles`, `settings-branding`, `settings-modules`, `settings-audit`, `settings-api-keys` emitted once from templates in `packages/spec/templates/settings/` (only when the module is enabled, PAP-264).
* Ownership: generated specs are rewritten on every run unless a file has `meta.generated: false`, which detaches it (the two-file rule of PAP-120 applied to specs).

Out: the code generation itself (PAP-120, PAP-119), the landing page and demo seed (default surfaces starter kit), non-CRUD pages, dashboards (PAP-172).

**Spec**

* Deterministic output: same `app.spec.yaml` yields byte-identical specs; keys sorted per the PAP-114 canonical order; `--check` exits 1 on drift (wired into gate 1 alongside PAP-120's drift job).
* Page ids: `<audienceKind>-<entity>-<view>`; routes `/_app/<plural>`, `/_app/<plural>/$id`, `/_app/<plural>/new` and `/_app/<plural>/$id/edit` with the staff surface under `/_staff/...` per PAP-16 route conventions.
* Field to component map lives in `packages/spec/src/codegen/field-components.ts` and is shared with PAP-164 cell renderers; unknown field types render `ui.textField` and warn.
* Customer detail pages hide fields marked `internal: true` in the entity definition; forms omit `computed` and `owner` (set server-side).
* `edgeCases` include the `neverHappen` seeds from the app interview when present.
* Generation of 20 entities times 3 audiences completes in under 5 s.

**Interface contract**

Provides: `generateEntityPages(app: AppSpec, opts): { written: string[], views: ViewSpec[], warnings: Warning[] }` from `@paperos/spec/codegen`, the `field-components.ts` map, and the settings page templates. Consumes: `AppSpec` and `resolvePageSpec` (PAP-117), access section grammar (PAP-116), `ViewSpec` and `FieldDef` (PAP-161), anchor grammar (PAP-131, soft: string format only), component ids from the PAP-74 registry (soft: static list of the six ids until the registry exists). Consumed by: default surfaces starter kit, `paperos gen` pipeline, PAP-125 examples (may replace hand-written list pages), PAP-29.

**Test plan**

* Unit: derivation rules per field type; access output for customer (own rows), staff (all), agent (read); kanban/calendar options only when fields exist.
* Golden: the three canned apps produce snapshot spec trees; snapshots validated with PAP-115 at zero warnings.
* Drift: modify an entity field, run `--check`, expect exit 1 naming the stale file.
* Integration (after PAP-120): generated specs for `clinic-booking` render three routes in Storybook with mocked hooks; conformance tests from PAP-122 pass.

**Definition of done**

* Generator merged; the three canned apps generate and validate with zero warnings; snapshots committed.
* `ViewSpec`s parse with the PAP-161 Zod schema; one kanban and one calendar variant present in the clinic fixture.
* `docs/spec/entity-pages.md` documents the rules and the detach mechanism; CHANGELOG entry; Linear comment with the generated tree for the clinic app.
* Runtime under 5 s for the 60-page stress fixture (timed in CI).

**Edge cases**

* Entity without a `name` field: list uses the first text field, or the id, and warns.
* Two entities with the same plural (`person`/`people`, `staff`/`staff`): route collision fails generation with both ids named.
* Audience with no read grant on any entity: no pages generated, a warning suggests reviewing access.
* Entity relation to an entity the audience may not read: detail shows the relation as an opaque label, never a link; recorded in the access matrix for PAP-64.
* A detached spec (`generated: false`) whose entity was removed: left in place, flagged by the validator as orphaned.

**Dependencies**

Hard: PAP-117, PAP-116, PAP-161. Soft: PAP-131 anchor grammar, PAP-74 component registry, PAP-164 field types, PAP-16 routes. Blocks the default surfaces starter kit and the `paperos gen` pipeline.

**Agent**

Built by Forge (Spec Tooling sub-agent); reviewed by Sentinel (spec-conformance) and Iris for the default component choices.

**Size**

M: one generator with rule tables, settings templates, fixtures.

**Demo**

Screenshot of the generated `specs/pages` tree for the clinic app and one generated list spec side by side with its `app.spec.yaml` entity; Storybook link once PAP-120 lands.
""")

issue("gp/spec-builder/gen-pipeline", "spec-builder", "Codegen and conformance tests", "P1", "Build", ["Developer", "Agent"], 1, "M",
      "Build `paperos gen`: the whole-app generation pipeline that runs every generator in dependency order with a manifest, incremental cache, deterministic output and a `--check` drift mode",
      ["PAP-115", "PAP-119", "PAP-120", "PAP-122", "PAP-123"], [], r"""
**Goal**

One command regenerates everything derived from specs: `paperos gen` runs the app generator (PAP-117), entity-derived page specs, data hooks (PAP-119), page scaffolds (PAP-120), conformance tests (PAP-122), access policies (PAP-116 to PAP-59), the flow graph (PAP-123), i18n catalogs (PAP-27) and the seed, in dependency order, incrementally, deterministically, and reports drift in CI. It is checkpoint C3 of the golden path and the thing every agent runs after editing a spec.

**Scope**

In:

* `packages/spec/src/pipeline/` with `registry.ts` (generators declare `id`, `inputs` globs, `outputs` globs, `dependsOn`), `runner.ts` (topological order, parallel where independent, per-generator timing), `manifest.ts` (`.paperos/gen-manifest.json` with input hashes, output hashes and generator versions), `check.ts` (`--check`: run in a temp dir and diff against the tree).
* CLI `paperos gen [--only <id>] [--check] [--force] [--json]` in `packages/cli` and `pnpm gen` script; `--json` prints the per-generator timing table used by the golden path report.
* Generators registered in this issue: `app`, `entity-pages`, `data-hooks`, `page-scaffolds`, `conformance`, `access-policies`, `flow-graph`, `i18n`, `seed`; each existing generator gets a ten-line adapter file, no rewrites.
* Incremental mode: a generator runs only when an input hash or its own version changed; `--force` ignores the manifest.
* Post-emit: Biome format on all outputs (as PAP-120 does), banner with spec hash, `generated/` folders listed in `.gitattributes` as `linguist-generated` and in CODEOWNERS for Sentinel.
* Gate 1 job `gen-check` (PAP-78) replacing the per-generator drift jobs of PAP-120 and entity-pages.

Out: the generators' own templates, watch mode (later), remote caching.

**Spec**

* Determinism contract: two runs on the same inputs produce byte-identical outputs; a determinism test runs the pipeline twice in CI and diffs.
* Order is derived, not configured: `app` before `entity-pages` before `data-hooks` and `page-scaffolds` before `conformance` and `flow-graph`; `i18n` and `seed` after `page-scaffolds`; a cycle in `dependsOn` fails at startup.
* Errors from one generator stop dependents but not siblings; the exit code is 1 with a table of failed generators; partial outputs are rolled back from a temp dir so the tree is never half-written.
* Timing: full run for the 60-page stress fixture under 20 s warm and under 60 s cold on the CI runner; each generator's ms is written to the manifest and, when present, stamped as sub-steps of checkpoint `C3` in `.paperos/golden-path.json`.
* Generator version bump invalidates its outputs only; the manifest schema is versioned and a mismatch triggers `--force` with a notice.
* `--check` output lists stale files and the generator that owns each, ready to paste into a PR comment.

**Interface contract**

Provides: `defineGenerator({ id, version, inputs, outputs, dependsOn, run(ctx) })`, `runPipeline(opts): PipelineReport` and the `PipelineReport` Zod schema (`{ generators: { id, status, ms, outputs }[], totalMs, drift: string[] }`) from `@paperos/spec/pipeline`; the `gen-check` CI job. Consumes: PAP-117 `gen:app`, entity-derived page specs generator, PAP-119 `gen:data`, PAP-120 `gen:page`, PAP-122 conformance generator, PAP-123 flow graph, PAP-116 policy compiler (soft: skipped when absent), PAP-27 extraction (soft), PAP-115 validator (runs first, aborts on errors). Consumed by: golden path driver, golden path acceptance test, `paperos upgrade`, PAP-29, every agent session via `pnpm gen`.

**Test plan**

* Unit: topological order with a fixture registry; cycle detection; incremental skip when hashes match; version bump reruns exactly one generator.
* Determinism: run twice, `git diff --exit-code` between outputs.
* Failure isolation: a generator that throws leaves the tree untouched (temp dir rollback) and marks dependents `skipped`.
* Integration: full run on the clinic fixture produces a tree that passes `pnpm check`; `--check` after touching one spec names exactly the outputs that changed.
* Performance: stress fixture timed in CI with a 20 s warm budget.

**Definition of done**

* Pipeline merged with the nine adapters; `pnpm gen` and `pnpm gen --check` documented in CLAUDE.md as the post-spec-edit command.
* `gen-check` job green on the template repo and the three canned apps; old per-generator drift jobs removed.
* Determinism and rollback tests in CI; stress fixture under budget.
* `docs/spec/codegen.md` extended with the pipeline section and the manifest format; CHANGELOG; Linear comment with the timing table.

**Edge cases**

* A generator writes outside its declared `outputs`: detected by diffing the temp dir, fails with the offending path (prevents accidental overwrites of human files).
* Manifest missing or corrupt: treated as `--force` with a notice, never an error.
* Two generators declare the same output path: startup error naming both.
* Spec validator warnings but no errors: pipeline runs and prints warnings once, not per generator.
* Running on Windows: paths normalised in hashes so manifests are portable across contributors.

**Dependencies**

Hard: PAP-115, PAP-119, PAP-120, PAP-122, PAP-123. Soft: PAP-116/PAP-59 policy compiler, PAP-27 i18n extraction, PAP-78 gate 1 job slot, entity-derived page specs (adapter added when it merges). Blocks the golden path driver.

**Agent**

Built by Forge (Spec Tooling sub-agent); reviewed by Sentinel (correctness) and Atlas for the CLAUDE.md wording.

**Size**

M: a runner, manifest, nine thin adapters and CI wiring; the generators already exist.

**Demo**

Terminal recording of `paperos gen --json` on the clinic app showing the ordered timing table, then a spec edit and `paperos gen --check` naming the stale files.
""")

# ---------------------------------------------------------------- app-shell
issue("gp/app-shell/starter-surfaces", "app-shell", "Multi-monitor and PWA polish", "P1", "Build", ["Customer", "Staff", "Developer"], 1, "M",
      "Build the default surfaces starter kit: customer portal and staff console page specs, a seeded demo tenant per audience and a first-run checklist for every generated app",
      ["PAP-117", "PAP-240", "PAP-55", "gp/spec-builder/entity-pages"], [], r"""
**Goal**

A generated app must be a product on minute ten, not an empty shell: a landing page, a customer portal, a staff console with dashboard and settings, demo users for each audience, and demo data so the grid, comments and docs have something to show. This issue ships the fixed surfaces that entity-derived page specs do not cover, the deterministic demo tenant, and the first-run checklist that tells the next agent what to do.

**Scope**

In:

* Starter page specs in `packages/cli/templates/starter/specs/pages/`: `public/landing` (name, one sentence from the idea, sign in, sign up, layout `public`), `customer/home` (first verb card, recent records, notifications placeholder), `customer/account` (profile, sessions per PAP-220, export per PAP-221, locale per PAP-27), `staff/dashboard` (`ui.dashboardBlocks` with fallback `ui.responsiveGrid`: counts per entity, last ten audit events from PAP-38), `staff/agents` (agent principals and sessions per PAP-60 and PAP-113), `staff/docs` (in-app docs from PAP-128); settings pages come from the entity-derived generator.
* Copy interpolation: `{{app.name}}`, `{{idea.sentence}}`, `{{audience.label}}` resolved by the driver at creation time from `app.spec.yaml`; no other templating.
* Demo tenant seed `packages/db/seed/demo-tenant.ts` generated per app: tenant `demo`, one user per audience (`customer@demo.<app>.test`, `staff@...`, `owner@...`) with passkey-less magic-link sign-in in preview, 25 records per entity with realistic values by field type (faker seeded with the app id), three comment threads, five audit events; shapes follow the PAP-240 test-mode fixtures so gate 3 and gate 4 reuse them.
* `paperos seed demo [--reset]` command and the `/__test/seed` hook (PAP-240) both call the same function.
* First-run checklist `docs/app/README.mdx` generated from a template: URLs, demo accounts, what was generated, the six interview answers, the next five issues in the Linear project, how to add a page (`author-spec` skill, PAP-118), how to regenerate (`paperos gen`).
* Storybook stories for the six starter pages in the template app so Iris reviews them once.

Out: the entity CRUD pages (entity-derived page specs), notifications inbox (PAP-136), theming beyond `tenant.branding` (PAP-75), marketing site.

**Spec**

* Starter specs validate against PAP-114 with zero warnings and use only PAP-74 registered ids; they reference no entity by name, only `app.entities` iteration in `ui.dashboardBlocks` props.
* Landing page is the only anonymous route; everything else has `access.deny: [anonymous]` and the audience grants from PAP-55.
* Demo users are created with `attributes.demo: true` and cannot be promoted to owner of a non-demo tenant; preview environments only (`PUBLIC_ENV=preview|dev`), the seed refuses to run when `PUBLIC_ENV=production`.
* Records honour field types and constraints (unique fields distinct, relations resolve, dates within the last 90 days); comment bodies are two sentences without lorem ipsum.
* Seed idempotent: rerun without `--reset` upserts; with `--reset` truncates the demo tenant only (RLS scoped, PAP-34).
* README generation is a pure function of `app.spec.yaml`, `.paperos/golden-path.json` and `.paperos/interview.json`.

**Interface contract**

Provides: starter spec templates, `seedDemoTenant(db, app: AppSpec, opts): Promise<{ users, counts }>`, `renderFirstRun(app, goldenPath, interview): string`, and the demo account convention `<audience>@demo.<app>.test`. Consumes: `AppSpec` (PAP-117), fixture shapes and `/__test/seed` (PAP-240), audience ids (PAP-55), entity-derived page specs (routes to link from home and dashboard), auth sign-in flows (PAP-57, soft: magic link only), `ui.dashboardBlocks` (PAP-172, soft: `ui.responsiveGrid` fallback). Consumed by: golden path driver (copies templates, runs seed), golden path acceptance test (signs in as demo users), PAP-29, PAP-82 and PAP-85 (fixtures).

**Test plan**

* Unit: copy interpolation; README rendering snapshot for the clinic fixture; seed value generators per field type honour constraints.
* Integration (PAP-42 stack): seed the clinic app, assert 25 rows per entity, three threads, demo users can sign in via magic link through PAP-57 test mode, `--reset` leaves other tenants untouched.
* Visual: Storybook stories at 375 and 1280 pass gate 3 baselines.
* Safety: seed with `PUBLIC_ENV=production` exits 2 without touching the database.

**Definition of done**

* Six starter specs merged and validating; Storybook stories reviewed by Iris; screenshots at 375 and 1280 attached.
* Seed produces the documented counts for the three canned apps in under 10 s each.
* `docs/app/README.mdx` renders in-app for the clinic fixture with live URLs.
* Template guide (PAP-24) links the starter kit section; CHANGELOG; Linear comment with screenshots and seed timing.

**Edge cases**

* App with no customer audience: landing shows staff sign-in only; `customer/*` specs are skipped, not generated empty.
* Entity with a unique email field: seeded values are unique per row and per audience domain.
* Seed run while Electric shapes (PAP-36) are subscribed: writes go through the API so sync clients see them; direct SQL only for `--reset`.
* Idea sentence longer than 160 characters: truncated at a sentence boundary for the landing hero, full text in README.
* Preview database claimed from the warm pool already has a demo tenant: `--reset` runs automatically at C6.

**Dependencies**

Hard: PAP-117, PAP-240, PAP-55, entity-derived page specs. Soft: PAP-57, PAP-172, PAP-38, PAP-128, PAP-24. Blocks the golden path driver.

**Agent**

Built by Forge (Platform Engineer) with Iris (Interface Designer) for the six starter pages and Quill for the README template; reviewed by Sentinel.

**Size**

M: six specs, one seed module, one renderer, stories.

**Demo**

Preview URL of the clinic app signed in as `customer@demo` and as `staff@demo`, side by side at 1280, plus the rendered first-run README.
""")

issue("gp/app-shell/driver", "app-shell", "Multi-monitor and PWA polish", "P1", "Build", ["Developer", "Agent"], 1, "M",
      "Build the golden path driver: `paperos create --idea` runs interview, app spec, generation, seed, push, provisioning and preview in one command with checkpoint stamps",
      ["PAP-22", "gp/spec-builder/app-interview", "gp/spec-builder/gen-pipeline", "gp/app-shell/starter-surfaces"], [], r"""
**Goal**

Make the ten-minute promise executable: `paperos create <name> --idea "<paragraph>"` chains the app interview, `paperos gen`, the starter kit and seed, PAP-22 provisioning, the first pull request and the preview deploy, overlapping independent stages and stamping checkpoints C0 to C6 into `.paperos/golden-path.json` so the acceptance test and PAP-29 have numbers instead of impressions. This issue is the orchestration layer over PAP-22; it adds no provisioning calls of its own.

**Scope**

In:

* `packages/cli/src/golden-path/` with `driver.ts` (stage graph and scheduler), `checkpoints.ts` (schema, stamping, durations), `stages/*.ts` (`interview`, `clone`, `generate`, `starter`, `check`, `commit`, `provision`, `pr`, `gates`, `preview`, `verify`), `report.ts` (terminal summary, JSON, Markdown for the PR body and the Linear project's first issue).
* `paperos create` gains `--idea <text>|--idea-file <path>`, `--spec <app.spec.yaml>` (skip the interview), `--answers <file>`, `--budget <minutes>` (default 10), `--no-wait` (return after push), `--report <path>`; without `--idea` or `--spec` the PAP-22 behaviour is unchanged.
* Stage overlap: `clone` and `provision` (repo-side steps that do not need the spec) start with `interview`; `generate` waits for `interview` and `clone`; `pr` waits for `check` and `provision`; `gates` and `preview` are awaited by polling the gate artifact contract (PAP-239) and `/__version`.
* Verification stage: `tests/golden-path/smoke.spec.ts` runs against the preview (sign in per demo audience, create a record, post a comment, grid shows the record) via Playwright.
* Checkpoint schema `GoldenPathReport` and the Markdown table posted as PR #1 description and as a Linear comment on the project's first starter issue.
* Failure handling: a failed stage marks its checkpoint `failed` with the error, keeps the repo and `.paperos/create.state.json` for `--resume`, and prints the exact resume command.

Out: the provisioning steps themselves (PAP-22 and the golden path provisioning issue), the interview (app interview skill), generators (`paperos gen`), the nightly acceptance workflow (golden path acceptance test), realistic drills (PAP-29).

**Spec**

* Stage graph is declared data (`{ id, dependsOn, run, checkpoint? }`) run by the same scheduler shape as the `paperos gen` runner; stages are idempotent and read `.paperos/create.state.json` from PAP-22 to skip completed work.
* Checkpoints: `C0 start`, `C1 spec`, `C2 repo`, `C3 generated`, `C4 provisioned`, `C5 gates`, `C6 live`; each has `at` (ISO), `ms` since C0, `status ok|warn|failed`, `budgetMs` and `details`; total budget breach sets `report.status = 'over-budget'` but does not abort.
* Budgets default to the table in the golden path document (1:30, 3:00, 5:00, 6:00, 9:00, 10:00) and can be overridden in `templates/golden-path.budgets.json`.
* Credit spend: reads the interview and gate 2 costs from their JSON outputs (PAP-113 metering when present) and records `costUsd` per stage.
* Gates polling: waits for `gate1.json`, `security.json`, `visual.json` and `edgecases.json` artifacts with the PAP-239 paths, at most `budget - elapsed`, then verifies all `status: pass`; when PAP-85 is unavailable the `edgecases` gate is recorded `skipped`, not `failed`.
* Preview verification: `/healthz` 200 and `/__version.sha` equals the pushed commit; retries every 5 s within budget.
* Terminal output: one line per stage with elapsed time, then the six URLs and the checkpoint table; `--json` prints the report only.
* Runs unattended in CI with `--yes --idea-file` and no TTY.

**Interface contract**

Provides: `runGoldenPath(opts): Promise<GoldenPathReport>`, the `GoldenPathReport` Zod schema (also exported as JSON Schema for the acceptance test and the docs badge), and the `paperos create --idea` flags. Consumes: `createApp` steps and `create.state.json` (PAP-22), `runAppInterview` (app interview skill), `runPipeline` (`paperos gen`), starter templates and `seedDemoTenant` (starter kit), preview URL convention and `/__version` (PAP-26), Pages URL (PAP-15), gate artifact paths (PAP-239), `forge bootstrap` (PAP-47, PAP-48 via PAP-22). Consumed by: golden path acceptance test, PAP-29, Atlas when decomposing a new app, docs.

**Test plan**

* Unit: scheduler ordering and overlap with fake stages; checkpoint math; budget breach marks `over-budget`; resume skips completed stages.
* Contract: `GoldenPathReport` fixture validates; Markdown table renderer snapshot.
* Integration with fakes: all external clients faked (as PAP-22 does), full run completes in under 30 s and produces the report; a failing `provision` stage leaves a resumable state and the printed command resumes to completion.
* End-to-end: one real run of the clinic idea in a `gp-` repo recorded in the PR (this is the first acceptance run; the nightly workflow is the acceptance issue).

**Definition of done**

* `paperos create clinic-booking --idea-file fixtures/clinic.txt --yes` completes C0 to C6 on the CI runner in under 10 minutes warm at least once, with the report and the six URLs attached to the PR and the Linear comment.
* `--resume` proven by killing the run during `provision` and resuming.
* Report Markdown posted as PR #1 description of the generated app and as a comment on its first starter issue.
* `docs/cli/create.md` documents the flags and checkpoints; CHANGELOG; template guide (PAP-24) links it.

**Edge cases**

* No TTY and no `--yes`: exit 2 with the message to pass `--yes` or `--answers`.
* Interview fails validation twice: stop at C1, keep the draft, exit 3; nothing pushed.
* Gate 2 is slow (model queue): C5 goes `warn` at budget, the driver keeps polling until the total budget, then records `over-budget` and still prints URLs.
* Preview slot unavailable (warm pool empty): C6 marked `failed` with the pool message; report still written; provisioning issue owns the fix.
* `paperos create` invoked inside an existing generated app: refuses unless `--resume`.
* Idea contains secrets or credentials (regex for tokens): redacted from `.paperos/interview.json` and the README with a warning.

**Dependencies**

Hard: PAP-22, app interview skill, `paperos gen` pipeline, default surfaces starter kit. Soft: PAP-26 preview URL, PAP-15 Pages, PAP-239 gate artifacts, PAP-113 metering, golden path provisioning (needed for the budget, not for correctness). Blocks the golden path acceptance test.

**Agent**

Built by Forge (Platform Engineer); Atlas reviews the stage graph and the report wording; Sentinel reviews correctness and the redaction rule.

**Size**

M: a scheduler, eleven thin stages, a report; the heavy lifting lives in the consumed issues.

**Demo**

Ten-minute terminal recording (asciinema) of the clinic idea reaching C6, cut to 90 seconds, with the checkpoint table and the preview URL opened at the end.
""")

issue("gp/app-shell/provisioning", "app-shell", "Multi-monitor and PWA polish", "P1", "Infra", ["Developer"], 2, "M",
      "Build golden path provisioning: parallel idempotent steps, warm pools for preview slots, databases and mirror repos, `--resume` and per-step time budgets in `paperos create`",
      ["PAP-22", "PAP-26", "PAP-15"], [], r"""
**Goal**

Provisioning is where the ten minutes go: GitHub, Forgejo, Linear, Pages and Coolify calls run serially in PAP-22 and each can take a minute. This issue turns the step list into a DAG run in parallel with per-step budgets, adds a nightly warm pool so preview slots, databases and mirror repos are claimed rather than created, and makes every step resumable. Target: checkpoint C4 within 60 seconds of C2 and C6 within 60 seconds of C5.

**Scope**

In:

* `packages/cli/src/provision/` with `steps.ts` (each PAP-22 step declared as `{ id, dependsOn, budgetMs, run, verify }`), `runner.ts` (parallel execution, retries with backoff, `create.state.json` persistence per step, `--resume`, `--dry-run` printing the DAG), `pool.ts` (claim and release).
* Warm pool job `ops/pool/warm-pool.ts` run nightly by `.github/workflows/warm-pool.yml` and by `paperos pool fill`: keeps N (default 5) of each resource ready: Coolify preview applications `gp-slot-<n>` pointed at the staging API (PAP-26), Postgres databases `app_slot_<n>` on the VPS with roles and RLS baseline migrations applied (PAP-30, PAP-32), Forgejo mirror repos `imagine-os/slot-<n>` (PAP-47). Pool state in `ops/pool/pool.json` in `paperos-infra`, locked with a Forgejo issue comment as the mutex.
* Claim at C4: rename the slot to the app name, write secrets, point the mirror at the new GitHub repo; release on `gp-` repo cleanup returns the slot to the pool after a reset.
* Step verification: every step has a `verify()` that checks the external state (repo exists, mirror configured, Pages enabled, Linear project exists) so `--resume` skips by truth, not by the state file alone.
* Budgets: per-step `budgetMs` with the provisioning total capped at 60 s; a step over budget is `warn`; a failed step after three retries is `failed` and stops dependents only.
* Reporting: step timings into `.paperos/golden-path.json` as sub-steps of C4 and C6 when the driver is present; otherwise printed.

Out: new external systems, production databases (PAP-30 owns production), Coolify blue/green, the driver's stage graph (driver issue).

**Spec**

* DAG: `github.repoCheck` and `forgejo.mirror` and `linear.project` and `pages.enable` and `coolify.claim` and `db.claim` are independent after `git.push`; `ci.secrets` depends on `forgejo.mirror` and `db.claim`; `linear.starterIssues` depends on `linear.project`.
* Concurrency limit 6; per-provider limits (Linear 2 concurrent, GitHub 4) to respect rate limits; 429 and `RATELIMITED` handled with the header-driven wait.
* Pool sizing: `pool.json` records `size`, `min`, `claimed[]`, `free[]`; `warm-pool.yml` refills to `size` and alerts (Linear issue in app-shell, label Infra) when `free < min` two nights running.
* Database slots: created with `CREATE DATABASE ... TEMPLATE app_slot_template` where the template has the PAP-32 baseline migrations applied, so a claim is a rename plus role grant under 2 s; app migrations run at first deploy (PAP-26 pre-deploy command).
* Coolify slots: preview applications pre-created from `ops/coolify/preview-slot.json`; claim sets the image repository and env vars and triggers the first deploy; the preview URL follows `pr-<n>.preview.<domain>` (PAP-26) with the slot's stable hostname aliased.
* Mirror slots: empty Forgejo repos with push mirroring pre-authorised; claim renames and sets the GitHub remote (PAP-47 mirror semantics).
* `--dry-run` prints the DAG as a table with budgets and pool availability without external calls beyond reads.

**Interface contract**

Provides: `provision(plan, opts): ProvisionReport`, `claimSlot(kind: 'preview'|'db'|'mirror', appName)`, `releaseSlot(kind, appName)`, the `pool.json` schema and the `warm-pool` workflow; the PAP-22 step list is re-expressed as `steps.ts` without changing its external behaviour. Consumes: PAP-22 clients (`GitHubClient`, `ForgejoClient`, `LinearClient`), Coolify preview definitions and deploy webhook (PAP-26), Pages repo settings checklist (PAP-15), Postgres provisioning (PAP-30) and baseline migrations (PAP-32), mirror configuration (PAP-47), bot accounts (PAP-48) for the pool job. Consumed by: golden path driver, golden path acceptance test, PAP-29, forge cleanup runbook (PAP-273).

**Test plan**

* Unit: DAG scheduler with fake steps (parallelism, dependents stop on failure, budgets); `verify()`-driven resume skips completed real state even when the state file is deleted.
* Pool: claim and release round trip against the fakes; `free < min` alert path; mutex contention test with two concurrent claimers (second waits, both succeed with distinct slots).
* Integration: one real claim of each slot kind in the staging environment recorded in CI logs with timings; total C2 to C4 under 60 s warm.
* Rate limit: fake provider returning 429 once; runner waits and succeeds within budget.

**Definition of done**

* `paperos create` provisioning runs through the DAG runner with identical external results to PAP-22 (its tests still pass) and C2 to C4 under 60 s on the CI runner with a warm pool.
* Warm pool workflow live in `paperos-infra`, `pool.json` shows five free slots of each kind, alert path proven once by draining the pool in staging.
* `--dry-run` and `--resume` documented in `docs/cli/create.md`; runbook `docs/runbooks/warm-pool.md` (fill, drain, reclaim leaked slots).
* CHANGELOG; Linear comment with the timing table and pool status.

**Edge cases**

* Pool empty: provisioning falls back to creating the resource live (slower), stamps `warn` with reason `pool-empty`, and the nightly job refills.
* Slot leaked (claimed by a deleted repo): weekly reconcile compares `claimed[]` with existing repos and releases orphans after a reset.
* Two `paperos create` runs claim simultaneously: mutex via Forgejo issue comment with a 30 s lease; on lease expiry the claim is retried once.
* Coolify API down: `coolify.claim` fails after retries, C6 cannot complete; everything else finishes and the report says exactly what to resume.
* Database template drift (new baseline migration merged): the nightly job rebuilds the template and recreates free slots; claimed slots migrate at deploy.
* GitHub repo not pre-provisioned (PAP-22 convention): `github.repoCheck` fails fast at C2 with the exact `gh repo create` command.

**Dependencies**

Hard: PAP-22, PAP-26, PAP-15. Soft: PAP-30, PAP-32, PAP-47, PAP-48, PAP-273. Blocks the golden path acceptance test.

**Agent**

Built by Forge (Platform Engineer, Infra sub-agent); reviewed by Sentinel (security reviewer for the pool secrets) and Atlas for budgets.

**Size**

M: a DAG runner, three slot kinds, one nightly job and a runbook.

**Demo**

`paperos create --dry-run` DAG table, then a real run's C2 to C4 timing table under 60 s and `pool.json` before and after the claim.
""")

issue("gp/app-shell/acceptance", "app-shell", "Multi-monitor and PWA polish", "P2", "Review", ["Developer", "Agent"], 2, "M",
      "Build the golden path acceptance test: nightly CI runs three canned ideas from paragraph to preview URL, asserts gates 1 to 4 and under ten minutes, publishes `golden-path.json`, badge and friction issues",
      ["gp/app-shell/driver", "gp/app-shell/provisioning", "PAP-239"], ["PAP-29"], r"""
**Goal**

Prove the ten-minute claim every night and keep it true: a workflow in `paperos-template` runs `paperos create --idea` for three canned ideas in throwaway repos, asserts the acceptance criterion from the golden path document ("a new app passes gates 1 to 4 and deploys to a preview URL in under 10 minutes of wall clock"), publishes the report and a README badge, and files one Linear issue per failing checkpoint in the owning project. PAP-29 starts its human-realistic drill from a passing golden path; this issue makes that starting line dependable.

**Scope**

In:

* `.github/workflows/golden-path.yml` (nightly 04:00 UTC after the warm pool refill, `workflow_dispatch` with an `idea` input, and on PRs touching `packages/cli` or `packages/spec` in a reduced one-idea mode), matrix over `fixtures/golden-path/{clinic-booking,agency-retainers,retail-inventory}.txt`.
* Runner script `ops/golden-path/run.ts`: pre-provisions a `gp-<idea>-<date>` GitHub repo, runs the driver with `--yes --json --budget 10`, collects `.paperos/golden-path.json`, runs the assertions, uploads the report as a workflow artifact and to `reports/golden-path/<date>-<idea>.json` in `paperos-infra`.
* Assertions: total C0 to C6 under 600 s warm (cold runs are recorded with `cache: cold` and not asserted until two consecutive warm passes exist); every checkpoint status `ok` or `warn`; gates 1 to 3 `pass` and gate 4 `pass|skipped`; smoke test passed; `paperos gen --check` clean; validator zero warnings; `costUsd` under 5.
* Friction issues: one Linear issue per failing checkpoint in the owning project (mapping table in `ops/golden-path/owners.json`), labels Build and `drill-finding`, deduplicated by a `golden-path:<checkpoint>:<idea>` marker in the description; reopened by comment when it recurs.
* Badge: `reports/golden-path/latest.json` with median duration over the last seven runs rendered by shields.io endpoint syntax into the README.
* Cleanup: repos deleted and pool slots released at the end of each run through the PAP-273 runbook script, after the report is archived; kept for 24 hours when the run failed.
* Trend page `docs/drills/golden-path.mdx` (PAP-128) with a per-checkpoint chart over time (static SVG until PAP-172).

Out: the driver, provisioning and generators (their issues), human drills (PAP-29), load testing (PAP-146), release certification (PAP-88).

**Spec**

* Report contract: consumes `GoldenPathReport` from the driver and wraps it in the PAP-239 artifact envelope (`kind: golden-path`, finding ids `GP-<checkpoint>-<n>`) so gate tooling and the Justin digest can read it.
* Warm cache definition: pnpm store, Docker build cache and Turbo cache restored from the previous nightly run via `actions/cache`; `cache: cold` when any restore missed.
* Three ideas are fixed text files; changing them requires updating the snapshot specs in the app interview and entity-pages fixtures (the same files).
* Time source is the runner clock; checkpoint budgets are read from the driver report, not duplicated here.
* Concurrency: the three matrix jobs run in parallel and each claims its own pool slots; the pool must hold at least three free slots of each kind or the job fails early with `pool-empty`.
* Workflow total runtime capped at 25 minutes; the `pull_request` mode runs only `clinic-booking` with `--no-wait` and asserts C0 to C4.

**Interface contract**

Provides: `reports/golden-path/*.json` in the PAP-239 envelope, `latest.json` for the badge, the `drill-finding` issue convention and owners mapping, and the `golden-path` workflow reusable by generated apps (`workflow_call`) to re-verify themselves after `paperos upgrade`. Consumes: golden path driver report and flags, provisioning pool and cleanup (`releaseSlot`), gate artifact contract (PAP-239), Linear issue creation through the `linear-update` skill (PAP-105) with the PAP-91 labels, docs engine (PAP-128), repo cleanup (PAP-273). Consumed by: PAP-29 (starting point and comparison), PAP-88 release train (golden path must be green for a release candidate), the Justin digest (PAP-97, informational).

**Test plan**

* Unit: assertion function over fixture reports (pass, over budget, gate failed, cold cache not asserted); owners mapping covers all six checkpoints; dedupe marker logic.
* Dry run: workflow executed with the driver in fake mode (all external clients faked) to validate the YAML, artifact upload and badge rendering in under 3 minutes.
* Real: three consecutive nightly runs recorded before this issue closes, at least two of them under 600 s warm for all three ideas.
* Friction path: force a failure (budget 1 minute) in `workflow_dispatch` and verify exactly one issue per failing checkpoint is created, then closed as duplicate-safe on rerun.

**Definition of done**

* Workflow merged and green for three nights; `latest.json` and README badge live; the trend page shows the runs.
* At least one friction issue was filed and linked by the workflow (from the forced-failure test or a real failure).
* Cleanup proven: no `gp-` repos older than 24 hours and pool `claimed[]` empty after runs.
* PAP-29 protocol document references this report as its C0 baseline; CHANGELOG; Linear comment on this issue and on PAP-5 with the first passing numbers.

**Edge cases**

* Nightly run collides with a template release merge: the workflow pins the template ref at start and records it in the report.
* One idea fails, two pass: matrix continues, the run is marked failed, friction issues filed only for the failing idea.
* Linear rate limited while filing issues: retries with the header wait; if still failing, the report stores `pendingIssues[]` and the next run files them.
* Preview URL passes `/healthz` but the smoke sign-in fails (mail provider outage in preview): C6 `failed` with the Playwright trace attached, owner mapped to identity.
* Warm pool refill still running at 04:00: workflow waits up to 5 minutes for `free >= 3`, then fails early with `pool-empty` rather than running cold.
* Cost over 5 USD because gate 2 retried: assertion fails with the per-stage cost table so the fix targets gate 2, not the interview.

**Dependencies**

Hard: golden path driver, golden path provisioning, PAP-239. Soft: PAP-105 `linear-update`, PAP-91 labels, PAP-128 docs engine, PAP-273 cleanup, PAP-88. Blocks PAP-29.

**Agent**

Run and owned by Sentinel (Quality Lead) with Forge for the workflow and Quill for the trend page; Atlas reads the nightly result in the digest. No Needs Justin item; the badge is the scoreboard.

**Size**

M: one workflow, one runner script, assertions, issue filing, badge and trend page.

**Demo**

Workflow run page showing three green matrix jobs, the checkpoint table per idea, the README badge reading the median duration, and the PAP-5 comment with the first passing numbers.
""")

issue("gp/app-shell/upgrade", "app-shell", "Multi-monitor and PWA polish", "P2", "Build", ["Developer", "Agent"], 2, "M",
      "Build `paperos upgrade`: apply template updates to generated apps with three-way merge, codemods, regeneration and an upgrade pull request",
      ["PAP-22", "gp/spec-builder/gen-pipeline"], [], r"""
**Goal**

An app created in ten minutes must keep receiving the template's fixes for years, or every generated app becomes a fork that drifts. `paperos upgrade` moves a generated app from its recorded template tag to a newer one: three-way merge of template-owned files, codemods for renamed APIs, regeneration of `generated/**` through `paperos gen`, migration hints, and one pull request that has to pass the same gates as any other. This closes the template-upgrade gap the round-2 audit found in forge and app-shell; `gap/forge/template-upgrade` was merged into this issue on 2026-09-17 (FIX-6), which adds the `@paperos/*` package registry below.

**Scope**

In:

* `paperos upgrade [--to <tag>] [--dry-run] [--no-pr]` in `packages/cli/src/upgrade/`: reads `.paperos/template.json` (`{ ref, tag, appliedAt, ownership }` written by PAP-22 at creation), fetches the template at the current and target tags, computes the diff of template-owned paths, applies it as a three-way merge (`git merge-file`) onto the app, runs codemods, runs `paperos gen --force`, runs `pnpm check`, commits on `upgrade/template-<tag>` and opens a PR with the template CHANGELOG (PAP-133) section between the two tags.
* Ownership manifest `templates/ownership.yaml` in the template: `template` (always merged: CI, ops, configs, `packages/ui` internals), `generated` (rewritten by `paperos gen`), `app` (never touched: specs, logic files, app schema), `shared` (three-way merged with conflict markers: CLAUDE.md, README, `app.spec.yaml` defaults). PAP-22's rename map is reused so renamed identifiers merge cleanly.
* Codemods in `templates/codemods/<from>-<to>/*.ts` (jscodeshift or ts-morph) shipped with each template release that renames an exported API; the upgrade runs those in range.
* Module awareness: paths belonging to modules the app removed with `--without` (PAP-266, PAP-264) are skipped.
* Conflict report `.paperos/upgrade-report.md` listing merged, regenerated, conflicted and skipped files; conflicted files keep markers and the PR is opened as draft.
* Template release hook: `forge/release-tags` (PAP-53) publishes `template-upgrade-notes.md` per tag; the upgrade PR embeds it.
* Package registry (from `gap/forge/template-upgrade`): publish `@paperos/*` on each template tag to the Forgejo npm registry (`git.PAPEROS_DOMAIN/api/packages/imagine-os/npm/`) with a GitHub Packages mirror; `.npmrc` template in generated apps; auth via the PAP-48 bot token in CI and the developer's Forgejo token locally; the upgrade PR bumps `@paperos/*` versions alongside the file merge.
* Package registry (from `gap/forge/template-upgrade`): publish `@paperos/*` on each template tag to the Forgejo npm registry (`git.PAPEROS_DOMAIN/api/packages/imagine-os/npm/`) with a GitHub Packages mirror; `.npmrc` template in generated apps; auth via the PAP-48 bot token in CI and the developer's Forgejo token locally; the upgrade PR bumps `@paperos/*` versions alongside the file merge.
* Fleet mode `paperos upgrade --fleet imagine-os` (dry-run by default) listing every generated app and its template tag from `.paperos/template.json` via the forge API (PAP-276), for Atlas to schedule upgrades.

Out: database data migrations (app migrations are ordinary Drizzle migrations reviewed in the PR), upgrading external services, automatic merging of conflicted PRs.

**Spec**

* Three-way merge base is the template at the app's recorded tag with the rename map applied, so the app's rename does not show as a conflict.
* Order: fetch, merge template-owned paths, apply codemods, `paperos gen --force`, `pnpm i --frozen-lockfile=false` (lockfile is `shared`), `pnpm check`; a failing `check` still opens the PR as draft with the failure log attached.
* `--dry-run` prints the file table and the codemods that would run, without writing.
* Idempotent: rerunning on an app already at the target tag exits 0 with "up to date"; a partially applied upgrade (crash) is resumed from `.paperos/upgrade.state.json`.
* Version policy: upgrades skip no minor tag; `--to` beyond the next minor applies tags in sequence so codemods compose.
* The upgrade PR uses the PAP-49 template with the `Linear:` trailer pointing at an issue the CLI creates in the app's Linear project ("Upgrade template to <tag>", Type Build) through the `linear-update` skill.

**Interface contract**

Provides: `upgradeApp(opts): UpgradeReport`, the `ownership.yaml` schema, the codemod folder convention, `.paperos/template.json` schema (co-owned with PAP-22, which writes it), and `--fleet` listing. Consumes: PAP-22 rename map and `template.json`, `paperos gen --force` (pipeline issue), module manifests (PAP-264, PAP-266), release tags and notes (PAP-53), PR template (PAP-49), changelog sections (PAP-133), forge client for fleet mode (PAP-276, soft). Consumed by: every generated app, Atlas fleet scheduling, the golden path acceptance workflow (`workflow_call` re-verification after an upgrade), PAP-24 template guide.

**Test plan**

* Unit: ownership classification for a fixture tree; three-way merge with rename map (no false conflicts); codemod range selection across three tags; idempotent rerun; resume after simulated crash.
* Integration: create the clinic app at tag `t1` (fixture template repo), release `t2` with a renamed API and a CI change, run `paperos upgrade --to t2`, assert the PR diff touches only template and generated paths and `pnpm check` passes; then a `t3` with a deliberate conflict in CLAUDE.md produces a draft PR with markers and a report.
* Fleet: fake forge listing three apps at mixed tags renders the table.

**Definition of done**

* Command merged; the fixture-template integration test runs in CI; one real upgrade PR opened on a `gp-` app from the acceptance workflow and merged green.
* `ownership.yaml` committed to the template and validated in gate 1 (every path in the repo classified).
* `docs/cli/upgrade.md` and a section in the template guide (PAP-24); `template-upgrade-notes.md` produced by the release process for the next tag.
* CHANGELOG; Linear comment with the fixture upgrade diff summary.

**Edge cases**

* App modified a `template` path (allowed but discouraged): merged three-way; conflict markers if incompatible; the report explains how to move the change into `app` space.
* Template removed a file the app still imports: `pnpm check` fails, PR opened as draft with the typecheck output.
* Codemod throws on one file: recorded in the report, other files continue, PR draft.
* App's `.paperos/template.json` missing (created before PAP-22 wrote it): `--from <tag>` required; the CLI suggests the tag by matching template file hashes.
* Upgrade across a `specVersion` bump (spec versioning pending issue): the spec codemods run first and the upgrade stops for review if any spec fails validation.
* Fleet mode without forge credentials: falls back to GitHub org listing (PAP-22 client) and warns.
* Template major bump: upgrade refuses without `--allow-major` and links the ADR.
* Registry down: `pnpm install` falls back to the GitHub Packages mirror.
* Template major bump: upgrade refuses without `--allow-major` and links the ADR.
* Registry down: `pnpm install` falls back to the GitHub Packages mirror.

**Dependencies**

Hard: PAP-22, `paperos gen` pipeline. Soft: PAP-264, PAP-266, PAP-53, PAP-49, PAP-133, PAP-276, PAP-24, PAP-45 (Forgejo packages), PAP-48 (bot token), PAP-52 (release feed); PAP-29's drill upgrades a drill app with this command. Blocks nothing in this round; every generated app depends on it operationally.

**Agent**

Built by Forge (Platform Engineer); reviewed by Sentinel (correctness, merge safety) and Atlas for fleet scheduling.

**Size**

M: merge logic, ownership manifest, codemod runner, fixture template, fleet listing.

**Demo**

Recording of `paperos upgrade --dry-run` then the real run on the clinic app producing a green PR, with the report and the fleet table for three `gp-` apps.
""")

if __name__ == "__main__":
    out = os.path.join(R2, "golden-path-issues.json")
    json.dump(ISSUES, open(out, "w"), indent=1)
    for it in ISSUES:
        print(it["key"], it["project"], it["milestone"], it["phase"], it["type"], it["priority"], it["state"], len(it["description"].split()), "words")
    print(len(ISSUES), "issues ->", out)
