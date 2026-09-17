---
key: "gp/spec-builder/app-interview"
title: "Write the app interview skill: one paragraph idea to `app.spec.yaml` (business profile, audiences, entities, navigation, modules) in at most six questions with `--yes` defaults"
project: "spec-builder"
parent: null
phase: "P1"
type: "Build"
priority: 1
size: "M"
surfaces: ["Developer", "Agent"]
milestone: "Codegen and conformance tests"
intendedState: "Backlog"
blockedBy: ["PAP-117", "PAP-118"]
blocks: []
source: "round2/pending-issues-golden-path.json (Golden Path)"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-golden-path-8-98e27ab16f4f"
identifier: "PAP-360"
status: "created"
createdAt: "2026-09-17"
---

# Write the app interview skill: one paragraph idea to `app.spec.yaml` (business profile, audiences, entities, navigation, modules) in at most six questions with `--yes` defaults

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
