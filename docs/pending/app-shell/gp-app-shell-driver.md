---
key: "gp/app-shell/driver"
title: "Build the golden path driver: `paperos create --idea` runs interview, app spec, generation, seed, push, provisioning and preview in one command with checkpoint stamps"
project: "app-shell"
parent: null
phase: "P1"
type: "Build"
priority: 1
size: "M"
surfaces: ["Developer", "Agent"]
milestone: "Multi-monitor and PWA polish"
intendedState: "Backlog"
blockedBy: ["PAP-22", "gp/spec-builder/app-interview", "gp/spec-builder/gen-pipeline", "gp/app-shell/starter-surfaces"]
blocks: []
source: "round2/pending-issues-golden-path.json (Golden Path)"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-golden-path-8-98e27ab16f4f"
identifier: "PAP-364"
status: "created"
createdAt: "2026-09-17"
---

# Build the golden path driver: `paperos create --idea` runs interview, app spec, generation, seed, push, provisioning and preview in one command with checkpoint stamps

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
