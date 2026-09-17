# New App in Ten Minutes: the golden path

Status: v1, 2026-09-17. Owner: Universal App Shell & Repo Template (Forge builds, Quill owns the interview, Sentinel owns the gates, Atlas dispatches). This is the direct answer to PAP-5: the shortest documented path from a one-paragraph idea to a running, deployed, multi-device app with auth, database, design system, table views, comments, docs and the four quality gates already wired. PAP-29 measures the realistic four-hour drill with agents writing real pages; this document fixes the automated ten-minute path that the drill starts from. Companion documents: the Blueprint, the Interface & Data Contracts, the Execution Schedule.

## 1. The promise

One command, one paragraph, ten minutes of wall clock:

```
paperos create clinic-booking --idea "A small physiotherapy clinic. Patients book and
reschedule appointments and see their invoices; staff manage the schedule, patient
records and payments; the owner sees revenue per therapist."
```

At the end the terminal prints six URLs: GitHub repo, Forgejo mirror (PAP-47), preview URL on `pr-1.preview.<domain>` (PAP-26), GitHub Pages demo (PAP-15), Linear project (PAP-22), and the in-app docs page describing what was generated. The app signs in with passkey or magic link (PAP-57), has a customer portal and a staff console (PAP-55 audiences), a grid view per entity (PAP-165), comments on every record (PAP-131), a docs section (PAP-128), and has already passed gates 1 to 4 on its first pull request (PAP-78, PAP-81, PAP-82, PAP-85). Nothing is hand-edited during the ten minutes; the first thing a human or agent does afterwards is write the second page spec.

## 2. The flow, minute by minute

Checkpoints are stamped by the driver (golden-path driver issue) into `.paperos/golden-path.json` and the budgets below are asserted by the acceptance test. Times are cumulative wall clock on a GitHub-hosted runner or a developer laptop with warm caches; cold-cache runs get a separate budget column in the report but the same pass criterion.

| Checkpoint | What has happened | Budget | Owner issues |
|---|---|---|---|
| C0 start | `paperos create --idea` invoked; `paperos doctor` confirms tokens and tools in under 5 s | 0:00 | PAP-22 |
| C1 spec | Interview finished (at most six questions or `--yes`), `specs/app.spec.yaml` written and validated, entity-derived page specs written | 1:30 | app interview skill, entity-derived page specs, PAP-117, PAP-115 |
| C2 repo | Template cloned at pinned tag, renamed, `pnpm i` from the pnpm store cache, first commit on `main` | 3:00 | PAP-22, PAP-13 |
| C3 generated | `paperos gen` has emitted routes, views, hooks, policies, conformance tests, navigation, flow graph and seed; `pnpm check` green locally | 5:00 | `paperos gen` pipeline, PAP-119, PAP-120, PAP-122, PAP-123 |
| C4 provisioned | GitHub push, Forgejo mirror, CI secrets, Pages, Linear project with starter issues, preview slot and database claimed from the warm pool, all in parallel | 6:00 | PAP-22, golden path provisioning, PAP-47, PAP-48 |
| C5 gates | PR #1 opened from `golden-path/initial`; gate 1 (PAP-78), gate 2 (PAP-81), gate 3 at three widths (PAP-82) and gate 4 smoke plan (PAP-85) report green through the gate artifact contract (PAP-239) | 9:00 | Quality Pipeline issues |
| C6 live | Preview URL answers `/healthz` and `/__version` with the commit SHA, seeded demo tenant signs in as customer and as staff, Pages demo live | 10:00 | PAP-26, PAP-15, default surfaces starter kit |

The ten-minute budget is met by doing C2 and C4 while C1 runs (clone and install do not wait for the interview), by running gates on a pre-built image cache (PAP-26 build cache under 3 minutes), and by never provisioning anything at creation time that can be pre-provisioned (section 6).

## 3. What the CLI asks

The interview is the only place a human speaks. It is run by Quill through the app interview skill and reads the paragraph first, so every question already has a proposed answer and `--yes` accepts them all. The bank is fixed at six questions; an agent may ask fewer, never more.

1. Who are the audiences? Proposed from the paragraph as PAP-55 audience ids, for example `customer.patient`, `staff.therapist`, `staff.owner`. Defaults: one customer kind, one staff kind, `agent.builder`.
2. Which entities and their key fields? Proposed as `entities:` rows for PAP-117 with types from PAP-164 (`appointment { start: date, therapist: relation(user), status: select }`). Default: the nouns in the paragraph with a name, status and owner field each.
3. What does each audience do first? One verb per audience becomes the default landing page and the first item of `navigation:`.
4. Which modules? Read from the module registry (PAP-264); proposed from the paragraph (payments on when money is mentioned, scheduling when dates are). Everything else is created `--without` (PAP-266).
5. Locale, currency, tax regime and terminology overrides (PAP-126 business profile). Defaults `en-US`, `USD`, none.
6. Anything that must never happen? Free text stored under `x-open-questions` and as edge-case seeds for PAP-85.

The answers are written once into `specs/app.spec.yaml`; the CLI never keeps a second copy of the app model. Anything the interview could not decide becomes a Backlog issue in the new Linear project, not a question to Justin.

## 4. What gets generated

The generated repository is the template (PAP-13) plus these app-specific files, all produced by `paperos gen` from `app.spec.yaml` and the page specs, with the two-file ownership rule from PAP-120: `generated/**` is always rewritten, everything else is created once.

```
specs/app.spec.yaml                       audiences, entities, navigation, modules, business profile
specs/pages/<surface>/<entity>-list.spec.yaml   per entity and audience (entity-derived page specs)
specs/pages/<surface>/<entity>-detail.spec.yaml
specs/pages/<surface>/<entity>-form.spec.yaml
specs/pages/public/landing.spec.yaml      starter kit
specs/pages/staff/settings.spec.yaml      members, roles, branding, modules, audit log
packages/db/src/schema/app.ts             Drizzle tables from entities, RLS policies from PAP-34 and PAP-59
packages/db/migrations/0001_app.sql       generated, reviewed in PR #1
packages/db/seed/demo-tenant.ts           deterministic demo tenant per audience, PAP-240 shapes
apps/web/src/generated/**                 routes wiring, views, navigation.ts, audiences.ts, entities.ts, data hooks
apps/web/src/pages/**.logic.ts            action stubs, created once
apps/api/src/generated/routers.ts         oRPC procedures per entity (PAP-35, PAP-268)
packages/views/src/generated/views.ts     one grid ViewSpec per entity (PAP-161), kanban when a select field named status exists
tests/conformance/**                      access matrix and state tests (PAP-122, PAP-64)
tests/golden-path/smoke.spec.ts           sign in per audience, create, comment, view grid
docs/app/README.mdx                       what was generated and why, rendered in-app by PAP-128
docs/app/flow.json                        UX flow graph for the canvas (PAP-123, PAP-132)
.paperos/golden-path.json                 checkpoints, durations, URLs, credit spend
.github/workflows/*.yml, ops/**           unchanged template CI, deploy, preview, pages
```

Design tokens, themes and components are not generated; the app inherits `packages/ui` (PAP-66, PAP-75) and the interview's branding answer only sets `tenant.branding`. Comments, docs, command palette and the window manager come from the template unchanged and appear on generated pages because the layouts already mount them (PAP-16, PAP-131, PAP-151).

## 5. Default surfaces

Every generated app ships two products from minute one, both driven by the same specs and differing only in audience, layout template and navigation. Surfaces marked "kit" come from the default surfaces starter kit; "derived" come from entity-derived page specs.

Customer-facing (layout `public` for anonymous, `app` for signed-in customers):

- Landing page with the app name, one sentence from the idea, sign-in and sign-up (kit; PAP-57 flows).
- Portal home: the customer's first verb from question 3, for example "Book an appointment" (derived form page).
- One list and one detail page per entity the customer audience may read, filtered by ownership through PAP-59 policies (derived).
- Comments on every detail page, scoped to the customer's own records (PAP-131), and a notifications inbox once PAP-136 lands.
- Account page: profile, sessions and devices (PAP-220), data export (PAP-221), locale (PAP-27).
- Invoices and payments when the payments module is on (PAP-180 in mock mode until Stripe keys exist).

Staff-facing (layout `app` with the staff console shell, PAP-58 tenant switching):

- Dashboard: counts per entity and the last ten audit events (PAP-38) as `ui.dashboardBlocks` fallback grid.
- One grid view per entity with inline edit, filter builder, grouping and CSV export (PAP-165, PAP-166), a kanban when an entity has a `status` select field, a calendar when it has a date range.
- Record detail with comments, activity, files (PAP-37) and the flow-graph link to the canvas.
- Settings: members and invitations, roles, branding, enabled modules, API keys (PAP-222), audit log, docs.
- Agent console page listing the agent principals working the app and their sessions (PAP-60, PAP-113), because agents are first-class staff in PaperOS.

Agent-facing: `CLAUDE.md`, the skills library (PAP-105), the Linear project with starter issues, and `docs/app/README.mdx`. Justin sees exactly one thing: nothing. No Needs Justin item is created by the golden path; PR #1 is merged by Atlas when the gates are green, and the credential asks (Apple signing, Stripe live keys) stay in the standing Needs Justin batch.

## 6. Making ten minutes possible

Three design rules turn a plausible thirty-minute path into ten.

Parallel and idempotent provisioning. `paperos create` already records step completion in `.paperos/create.state.json` (PAP-22). The provisioning issue turns the linear step list into a DAG with per-step time budgets, runs GitHub, Forgejo, Linear, Pages and Coolify calls concurrently, and resumes any failed step with `--resume` without repeating the others.

Warm pools. Preview slots on Coolify, per-app Postgres databases on the VPS (PAP-30) and Forgejo mirror repos are pre-created nightly by a pool job and claimed at C4; claiming is a rename and a secret write, not a provisioning call. Pool size defaults to five; the acceptance test fails if the pool is empty.

Generation before pushing. `paperos gen` and `pnpm check` run locally before the first push so that PR #1 reaches gate 1 already green; the gates confirm, they do not discover. Codegen is deterministic, so the gate 1 drift job (`paperos gen --check`) passes on the first run.

## 7. Acceptance test

The acceptance test is a nightly workflow in `paperos-template` (`.github/workflows/golden-path.yml`, also on demand) that runs three canned ideas, `clinic-booking`, `agency-retainers` and `retail-inventory`, through the whole path in throwaway `gp-` repos, and asserts:

- A new app passes gates 1 to 4 and deploys to a preview URL in under 10 minutes of wall clock, measured from C0 to C6 with warm caches; cold-cache runs are reported, not asserted, until two consecutive warm runs pass.
- Each of C1 to C6 is within its budget from section 2; a checkpoint over budget is a warning, the total over ten minutes is a failure.
- The preview signs in as the customer and the staff demo users, creates one record, posts one comment, and the grid shows the record, via `tests/golden-path/smoke.spec.ts`.
- `paperos gen --check` reports no drift; `specs/` validates with zero warnings; every generated page has a conformance test.
- Credit spend for the run is under 5 USD (interview and gate 2 are the only model calls).
- The report `reports/golden-path/<date>.json` follows the gate artifact contract (PAP-239) and the README badge shows the latest median duration.

Failures open one Linear issue per failing checkpoint, labelled `Build` and `drill-finding`, in the owning project. The throwaway repos are deleted by the forge bootstrap cleanup (PAP-273 runbook) after the report is archived. PAP-29 runs the human-realistic drill on top of this: it starts from a passing golden path and measures how long agents take to add real pages.

## 8. Issues that make it real

New in this round:

- Universal App Shell & Repo Template: golden path driver (`paperos create --idea`) (pending, `gp/app-shell/driver`); golden path provisioning (parallel steps, warm pools, `--resume`) (pending, `gp/app-shell/provisioning`); default surfaces starter kit (pending, `gp/app-shell/starter-surfaces`); golden path acceptance test (pending, `gp/app-shell/acceptance`); `paperos upgrade` so a ten-minute app keeps receiving template fixes (pending, `gp/app-shell/upgrade`).
- Spec Builder: app interview skill (paragraph to `app.spec.yaml`) (pending, `gp/spec-builder/app-interview`); entity-derived page specs (pending, `gp/spec-builder/entity-pages`); `paperos gen` whole-app pipeline (pending, `gp/spec-builder/gen-pipeline`).
- Issues marked pending could not be created today (Linear `USAGE_LIMIT_EXCEEDED`, workspace issue cap); their full specs are in [Round 2 pending issues: golden path (8)](https://linear.app/paperos/document/round-2-pending-issues-golden-path-8-98e27ab16f4f) and in `round2/pending-issues-golden-path.json`.

Existing issues on the critical path, in order: PAP-13, PAP-16, PAP-17, PAP-114, PAP-115, PAP-117, PAP-118, PAP-119, PAP-120, PAP-122, PAP-22, PAP-15, PAP-26, PAP-78, PAP-81, PAP-82, PAP-239, PAP-240, PAP-55, PAP-57, PAP-59, PAP-161, PAP-165, PAP-131, PAP-128, PAP-264, PAP-266. Soft: PAP-126, PAP-136, PAP-85, PAP-29.

## 9. Out of the ten minutes

Desktop and mobile binaries (PAP-19, PAP-20) build from the same PR but are not awaited; signed builds wait on credentials. Live Stripe, payroll and social adapters run in mock mode. Custom domains, production promotion (PAP-88) and SSO (PAP-230) are day-two. Anything the interview cannot answer becomes an issue, never a blocker.
