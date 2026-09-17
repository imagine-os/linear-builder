# pm-linear — Project Management & Claude Pipeline
PHASE P0 prio 1 dependsOn []
SUMMARY: Linear configured as the agent queue, an orchestrator that turns Ready for Claude issues into sessions and PRs, and a thin PM module that syncs with Linear.
DESC: Goal: Linear becomes the queue many parallel Claude Code sessions build from, and Justin's own queue stays tiny. We add the pipeline states, label groups and project templates to team PAP, define an issue contract enforced by a webhook validator, and build an orchestrator that claims issues, spawns sessions in git worktrees, posts PR status and screenshots back, and meters credit spend. Concurrency controls respect dependencies and file-lock hints. Inside PaperOS a PM data model mirrors Linear and a bidirectional sync keeps both in step, with boards rendered by the views engine. Non-goal: replacing Linear before Oct 1; the sync preserves the option. PAP-5 is decomposed into this plan and closed.
MILESTONES: ['Linear configured for the pipeline 2026-09-18: States, labels, projects, issue contract, Justin queue design, playbook', 'Orchestrator claims and ships issues 2026-09-22: Sessions spawn from Linear, webhooks round-trip, credits metered', 'PM module syncs both ways 2026-09-30: PM entities, Linear sync, board views']


## PAP-91 [P0 Infra S prio1 Ready for Claude] Add pipeline states (Ready for Claude, In Review, Needs Justin), label groups and project templates to Linear team PAP
key=pm-linear/configure-workspace milestone=Linear configured for the pipeline agent=Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel 
blockedBy=[] blocks=['PAP-96', 'PAP-95', 'PAP-94', 'PAP-93', 'PAP-22']
GOAL: Turn Linear team PAP into the queue the whole plan assumes: the six pipeline states, four label groups, one issue template per issue type and a project template, created idempotently by a script so any future `paperos create <app>` project gets the identical setup. After this issue every other issue key in plan.json can be created with the right state, labels and template without manual clicking.
SCOPE: In:

* Workflow states on team PAP: keep `Backlog`, `Todo` (renamed to `Ready for Claude`, type unstarted, color #5E6AD2), `In Progress`, add `In Review` (started, #F2994A) and `Needs Justin` (started, #EB5757, description from plan.json `states`), keep `Done`, `Canceled`, `Duplicate`. Order: Backlog, Ready for Claude, In Progress, In Review, Needs Justin, Done, Canceled, Duplicate.
* Label groups (parent labels with children) exactly as plan.json `labels.groups`: Phase (P0/P1/P2), Type (Research/Spec/Build/Review/Infra/Docs), Surface (Customer/Staff/Developer/Agent), plus a fourth group `Character` with one child per lead in `agents[]` (Atlas, Forge, Iris, Quill, Sentinel, Nova, Ledger, Beacon, Scout) so the orchestrator can route by label.
* Issue templates via `templateCreate` (type `issue`): one per Type label, body pre-filled with the section headings the issue contract (`pm-linear/
SPEC(first 1200): * Use the GraphQL mutations `workflowStateCreate`/`workflowStateUpdate`, `issueLabelCreate` (with `parentId` for groups, `isGroup: true` on parents), `templateCreate`, `teamUpdate` (`issueEstimationType: "tShirt"`, `defaultIssueStateId`).
* Renaming `Todo` preserves the state id, so no issues need moving; PAP-5 stays in Backlog.
* Script exits non-zero and prints a diff table (name, field, before, after) when run with `--check`; applies with `--apply`.
* Output a `linear-workspace.json` snapshot (ids of every state, label, template) committed to the orchestrator repo; every later issue reads ids from this file rather than hard-coding.
* Document the resulting configuration in `docs/pm/linear-setup.md` with a screenshot of the workflow settings page.
DOD:
* `pnpm linear:configure --check` reports no drift after `--apply` (idempotency proven by running twice).
* All six pipeline states exist in the listed order with the listed types and colors; verified via `team.states` query printed in CI log.
* Four label groups with all children exist; Bug/Feature/Improvement gone or archived.
* Issue templates appear in the Linear "New issue" template picker (screenshot attached at 1280 px and on the mobile web layout at 375 px).
* `linear-workspace.json` committed and referenced by `pm-linear/orchestrator` spec.
* `docs/pm/linear-setup.md` written; changelog entry added.
* Linear comment on this issue with the screenshot links and the snapshot file path.
EDGE:
* A state named `In Review` already exists with a different type: update in place, never create a duplicate.
* Label group parent exists but a child is missing: create only the child.
* Linear API rate limit (HTTP 429 or `RATELIMITED` error): back off with exponential retry up to 5 attempts.
* Renaming `Todo` fails because a Linear view filters on the name: log and continue; names in views are resolved by id.
* Running against the wrong team (key not `PAP`): refuse unless `--team` is passed explicitly.
* API key lacks admin scope: fail fast with a clear message before any mutation.
DEPS: None; this is the first issue in the plan and `readyNow: true`. Consumers: `pm-linear/issue-contract`, `pm-linear/orchestrator`, `app-shell/create-cli` (reuses the script for new projects).


## PAP-92 [P0 Docs S prio1 Ready for Claude] Write the session playbook: how a Claude session picks up an issue, what it must read, how it reports and ends
key=pm-linear/session-playbook milestone=Linear configured for the pipeline agent=Built by Quill (lead); reviewed by Atlas for operational fit
blockedBy=[] blocks=['PAP-96']
GOAL: Write the one document every Claude Code session reads first: how an issue is picked up, what must be read before code is written, how progress is reported to Linear, how the PR is opened, and how the session ends cleanly. It is the human-readable contract that `pm-linear/orchestrator` automates and `agents/roster-v1` embeds into every character's system prompt.
SCOPE: In:

* `docs/pm/session-playbook.md` (also copied into `.claude/rules/session-playbook.md` in `paperos-template` so it is loaded automatically) covering: claim, orient, plan, build, verify, report, hand off, end.
* Required reading order: the Linear issue body (contract sections), linked page specs under `specs/`, `CLAUDE.md`, the character's memory file (`agents/memory`), the two most recent Linear comments on the issue, and the project's ADRs in `docs/adr/` touched by the issue.
* Reporting cadence: a Linear comment at start (`Session started` with worktree, branch, character, model), at every meaningful milestone (max one per 30 minutes), and at end (`Session ended` with PR link, gates status, cost).
* Comment format: a fixed markdown template with a machine-readable footer block (```` ```paperos-session ```` fenced JSON with `sessionId`, `character`, `costUsd`, `turns`, `pr`, `status
SPEC(first 1200): * Document structure: Purpose, Lifecycle diagram (mermaid, states mirror Linear), Step-by-step with the exact commands (`git worktree add`, `pnpm i`, `pnpm check`, `gh pr create --template`), Comment templates, Stop conditions, FAQ.
* Reference the branch naming and commit conventions from `forge/branch-policy` by link rather than restating them.
* Include a worked example transcript for a small issue (adding a Storybook story) showing the three comments verbatim.
* Word budget 1500-2500; reading time under 10 minutes because every session pays the tokens to read it.
* Versioned: a `playbookVersion` field in the footer JSON so the orchestrator can flag sessions running an outdated playbook.
DOD:
* `docs/pm/session-playbook.md` and `.claude/rules/session-playbook.md` are identical (CI check compares them).
* A dry-run session (Claude Code, `-p` mode) given only the playbook and a toy issue produces the three comments in the correct format, verified by parsing the footer JSON with the schema committed at `packages/agents/src/session-footer.schema.json`.
* Reviewed by Sentinel for ambiguity: every "must" has a verifiable check.
* Rendered in the docs engine once `collab/docs-engine` exists; until then linked from the repo README.
* Changelog entry; Linear comment on this issue linking the document and the dry-run transcript.
EDGE:
* Issue has no linked spec: playbook says stop and comment `needs-spec` rather than inventing one.
* Two sessions claim the same issue (orchestrator race): playbook says check the assignee and the last `Session started` comment; the later session exits.
* Session context is compacted mid-task: the footer JSON of the last comment is the recovery point; playbook says re-read it.
* Worktree already exists from a crashed session: reuse if branch matches, else create `-2` suffix and note it.
* Justin comments mid-session: treat as highest priority instruction, acknowledge in the next comment.
* Budget cap hit with uncommitted work: commit as `wip:` on the branch, push, comment, stop.
DEPS: None to start (`readyNow: true`). Consumed by `pm-linear/orchestrator`, `agents/roster-v1`, `agents/handoffs`, `agents/skills-library` (the `linear-update` skill implements the comment templates).


## PAP-93 [P0 Spec M prio1 Backlog] Define the issue contract (spec link, acceptance criteria, surfaces, definition of done) enforced by a Linear webhook validator
key=pm-linear/issue-contract milestone=Linear configured for the pipeline agent=Built by Atlas (Decomposer sub-agent), reviewed by Sentinel 
blockedBy=['PAP-91'] blocks=[]
GOAL: Define what an issue must contain before a machine is allowed to build it, and enforce it: a Linear webhook validator moves non-conforming issues back out of `Ready for Claude` with a comment listing exactly what is missing. This keeps the orchestrator from spawning expensive sessions on vague issues and gives the Decomposer sub-agent a target format.
SCOPE: In:

* `docs/pm/issue-contract.md` specifying required description sections in order: `**Goal**`, `**Scope**`, `**Spec**`, `**Definition of done**`, `**Edge cases**`, `**Dependencies**`, `**Agent**`, `**Size**` (matching the format used across this plan).
* Required metadata: exactly one label from each of Phase, Type, Surface (one or more), Character; an estimate (S/M/L); a project; at least one link to a spec file (`specs/**/*.spec.yaml` path or a Linear document) for Build issues; dependencies expressed as Linear "blocked by" relations, not prose.
* Validator service module `src/contract/validate.ts` in `imagine-os/paperos-orchestrator`: pure function `validateIssue(issue): ContractResult` returning `{ok, violations: [{code, message, fix}]}`.
* Webhook handler: on `Issue` `update` where state becomes `Ready for Claude`, run the validator; on failure move the issue to `Backlog`, add la
SPEC(first 1200): * Parse the description with `remark` (unified) into an mdast; identify sections by bold paragraph headings to match the plan's format; also accept `##` headings.
* Validator is deterministic and has a fixture suite: 12 good issues, 20 bad ones, one per code.
* Comment template lives in `src/contract/templates/violations.md` with the footer JSON block from `pm-linear/session-playbook` (`status: "contract-failed"`).
* `BLOCKED_BY_OPEN` is a warning, not a failure, until `pm-linear/concurrency` takes over dependency scheduling; a `--strict` flag promotes it.
* Store results in the orchestrator's SQLite/Postgres table `contract_checks(issue_id, checked_at, ok, violations_json)` for the burn report.
DOD:
* Fixture suite passes in Vitest; coverage of `validate.ts` above 95 percent.
* Moving a bad issue to `Ready for Claude` in the real PAP team results in a bounce to `Backlog`, label and comment within 10 seconds (screen recording attached).
* Moving a good issue leaves it untouched; `needs-contract` label removed if present.
* `pnpm contract:audit` run on all current PAP issues; results posted as a comment on this issue.
* Contract doc published; issue templates from `pm-linear/configure-workspace` updated to match section names exactly.
* Changelog entry; Linear comment with the recording link.
EDGE:
* Description uses `##` headings instead of bold: accept both, normalise.
* Sections present but in a different order: warn, do not fail.
* Issue moved to `Ready for Claude` by the validator's own bot account: ignore to prevent loops (check `actor.id`).
* Webhook delivered twice (Linear retries): idempotent by `webhookId`; no duplicate comments.
* Very long description over 50k characters: validate only the first 50k and flag `DESCRIPTION_TOO_LONG`.
* Sub-issue of a parent with a spec link: inherit `NO_SPEC_LINK` satisfaction from the parent.
* Justin manually forces an issue to `Ready for Claude` after a bounce: a second bounce would be hostile; if the last mover is Justin, post the violations as a comment but do not move it.
DEPS: * `pm-linear/configure-workspace`: label groups, states and templates must exist.
* `pm-linear/webhooks`: shares the receiver; if this lands first, ship a minimal receiver here and let webhooks generalise it.


## PAP-94 [P0 Spec M prio1 Backlog] Design the Needs Justin queue: batched decisions, one-click approve/reject comments, max five open items rule
key=pm-linear/justin-queue milestone=Linear configured for the pipeline agent=Built by Atlas (lead), reviewed by Sentinel (Code Reviewer) 
blockedBy=['PAP-91'] blocks=[]
GOAL: Design and implement the rules that keep the single human reviewer's queue small and fast: `Needs Justin` holds at most five open items, every item is a batched, pre-digested decision with one-click approve/reject via comment keywords, and anything that does not need a human is refused entry. This is what makes the rest of the plan's autonomy safe.
SCOPE: In:

* `docs/pm/justin-queue.md`: what qualifies for `Needs Justin` (release-candidate approval, irreversible actions such as production deploys, spend above a threshold, external-facing communication, credential grants, hiring a new character), what does not (code review, test failures, library choices under the rubric).
* Decision card format for the issue description or comment: `Decision needed`, `Recommendation` (one sentence), `Options` (max 3, each with cost and risk), `Deadline` and `Default if no answer` (auto-applies after 48 hours unless marked `hard-block`), `Context links`.
* Reply grammar parsed by the webhook handler: a comment starting with `approve`, `reject`, `option 2`, `defer 3d`, or `ask: <question>`; the handler moves the issue (`Done`, `Backlog`, or back to `In Progress` with the chosen option recorded) and posts an acknowledgement.
* Queue governor in the orchestr
SPEC(first 1200): * Module `src/justin/` in `imagine-os/paperos-orchestrator`: `governor.ts` (slot accounting, uses Linear `issues(filter: {state: {name: {eq: "Needs Justin"}}})`), `replies.ts` (grammar parser, regex plus fallback to an LLM classification only when the regex fails), `digest.ts` (cron 14:00 UTC daily).
* Defaults execute through the same state transitions the orchestrator uses; every auto-applied default is logged with `appliedBy: "default"` and posted as a comment.
* Priority order for admission: Linear priority (Urgent first), then age.
* All comments carry the `paperos-session` footer JSON with `status: "decision-requested" | "decision-applied"`.
* Configuration in `orchestrator.config.yaml`: `justinQueue.maxOpen: 5`, `defaultTimeoutHours: 48`, `digestCronUtc: "0 14 * * *"`.
DOD:
* Doc published and linked from the session playbook.
* Governor tested: sixth item bounces with label; freeing a slot admits the highest-priority waiting item within one poll cycle (integration test against a Linear sandbox team or mocked SDK).
* Reply grammar has a fixture suite of 30 real-looking replies including typos (`aprove`) with expected outcomes.
* Default application after timeout tested with a fake clock.
* Digest posted to `PAP-JUSTIN-DIGEST` for three consecutive days in staging; screenshot at 375 px (Linear mobile) and 1280 px attached because Justin will read this on his phone.
* Changelog entry; Linear comment with screenshots.
EDGE:
* Justin replies with prose that matches none of the grammar: handler asks one clarifying question using the `ask:` template, does not guess.
* Two decisions batched in one comment (`approve PAP-40, reject PAP-41`): support multiple `key: verb` pairs.
* An `Urgent` item arrives when the queue is full: bump the oldest non-urgent item back to `queued-for-justin` and comment why.
* Default timeout passes on a `hard-block` item: never auto-apply; re-post reminder daily and escalate priority.
* Justin edits the issue instead of commenting: treat a state change by Justin as approval of the recommendation.
* Clock skew between orchestrator and Linear timestamps: compute deadlines from Linear `createdAt` of the decision comment.
DEPS: * `pm-linear/configure-workspace` (states and labels).
* Works with `pm-linear/webhooks` for comment events; can be built against the mock receiver first.


## PAP-95 [P0 Docs S prio2 Backlog] Decompose PAP-5 (startup procedure inefficiency) into this master plan's projects and close it with a summary comment
key=pm-linear/pap5-decompose milestone=Linear configured for the pipeline agent=Built by Quill (Changelog Scribe sub-agent), reviewed by Atl
blockedBy=['PAP-91'] blocks=[]
GOAL: Close the loop on the issue that started everything. PAP-5 ("the startup procedure for creating new apps on the fly is inefficient... how quickly do we get from blank screen to electrons") is restated as a measurable goal, linked to the projects and issues in this plan that answer it, and closed with a summary comment so the origin of the whole programme is traceable from Linear.
SCOPE: In:

* Rewrite the PAP-5 description (keep the original title text quoted at the top) into the contract format: Goal restated as "time from `paperos create <app>` to a running, reviewed page on web and desktop under 4 hours of wall-clock and under $150 of credits"; Scope pointing to the 17 projects.
* A "Decomposition" section: a table with one row per project (name, Linear project link, phase, what it contributes to the startup time), generated from plan.json by a script so it matches the created projects exactly.
* Linear relations: PAP-5 `related` to each of the 17 projects' first milestone issue; PAP-5 becomes the parent of a new tracking issue `Startup benchmark` (Type Review, P2) that measures the time-to-first-page metric at the end of P2.
* Close PAP-5 as `Done` with a final comment: the metric, where the plan lives (plan.json path in the orchestrator repo and the Linear projects
SPEC(first 1200): * Script `ops/linear/decompose-pap5.ts` in `imagine-os/paperos-orchestrator` reads `plan.json`, resolves project ids via `projects(filter: {name: {eq}})`, writes the description with `issueUpdate`, creates relations with `issueRelationCreate` (type `related`), creates the benchmark child with `issueCreate` (`parentId`), then `issueUpdate` state to Done using ids from `linear-workspace.json`.
* Description under 4000 characters so it renders fully in the Linear mobile app; the full table lives in `docs/pm/pap5-decomposition.md` and is linked.
* The benchmark issue's Definition of done: run `paperos create bench-app` on a clean machine, time each stage (clone, install, first page from spec, PR opened, gates green, demo URL), record in `docs/pm/startup-benchmark.md`, target under 4 hours.
* Idempotent: re-running updates rather than duplicates (relations checked before creation).
DOD:
* PAP-5 description matches the contract validator (`pnpm contract:check PAP-5` passes) while keeping the original title quoted.
* 17 `related` relations exist (verified by `issue.relations` query output pasted in the comment).
* Benchmark child issue exists in Backlog with a complete contract.
* PAP-5 is `Done`; closing comment includes the metric and links; screenshot of the closed issue at 1280 px attached.
* `docs/pm/pap5-decomposition.md` committed; changelog entry.
* Justin receives no `Needs Justin` item for this; it is informational (he can reopen by creating a new issue).
EDGE:
* A project from plan.json does not yet exist in Linear (Decomposer run incomplete): script lists missing ones and exits non-zero without partial updates.
* PAP-5 has been edited by Justin since planning: preserve any text he added under a `Original notes` section rather than overwriting.
* Linear rejects a relation because it already exists: treat as success.
* Closing an issue with an open child is allowed in Linear; confirm the team setting from `pm-linear/configure-workspace` does not auto-reopen it.
* Title exceeds Linear's limit if we append: do not touch the title.
DEPS: * `pm-linear/configure-workspace` (states, labels, ids).
* The Decomposer run that creates projects from plan.json must have completed (tracked under `pm-linear/orchestrator` prerequisites).


## PAP-96 [P0 Build L prio1 Backlog] Build the orchestrator that polls Ready for Claude, spawns one Claude Code session per issue in a git worktree and moves states
key=pm-linear/orchestrator milestone=Orchestrator claims and ships issues agent=Built by Atlas (Dispatcher sub-agent) with Forge (Ops Runner
blockedBy=['PAP-92', 'PAP-46', 'PAP-91'] blocks=['PAP-99', 'PAP-98', 'PAP-97']
GOAL: Build the engine that turns Linear into running agents: a long-lived service that polls `Ready for Claude`, claims one issue at a time per slot, creates a git worktree, launches a Claude Code session configured for the issue's character, streams its progress, and moves the issue through `In Progress` to `In Review` when a PR exists. Everything else in the pipeline (webhooks, metering, concurrency) plugs into this service.
SCOPE: In:

* Repo `imagine-os/paperos-orchestrator` (pre-provisioned): TypeScript, Node 22, pnpm, Biome, Vitest; deployed as a Docker service on the VPS via Coolify with the target repos cloned under `/srv/repos/<repo>` and worktrees under `/srv/worktrees/<PAP-key>`.
* Poll loop (every 30 s, also triggered by webhook) using `@linear/sdk`: `issues(filter: {team: {key: {eq: "PAP"}}, state: {name: {eq: "Ready for Claude"}}, assignee: {null: true}})` ordered by priority then `createdAt`.
* Claim: `issueUpdate` set assignee to the character's bot user (from `forge/bot-accounts` mapping) and state `In Progress`, atomically guarded by re-reading the issue and checking `updatedAt` matches.
* Worktree: `git -C /srv/repos/<repo> fetch origin && git worktree add /srv/worktrees/PAP-123 -b <branch> origin/main` with branch name from `forge/branch-policy`; `pnpm i --frozen-lockfile`.
* Session launch throug
SPEC(first 1200): * Package layout: `src/linear/` (client, queries, state ids from `linear-workspace.json`), `src/git/worktree.ts`, `src/session/launch.ts`, `src/session/prompt.ts`, `src/loop.ts`, `src/db/`, `src/http.ts`. Config via `orchestrator.config.yaml` validated with Zod: `maxParallel` (default 4), `pollIntervalMs`, `repos[]` (name, path, defaultBranch, linearProjectKeys\[\]), `characters` path.
* Character resolution: Character label on the issue; fallback to the project's default character; fail to `Needs Justin` if none.
* Session prompt must instruct the model to follow `.claude/rules/session-playbook.md` and end with the footer block; the orchestrator parses the last assistant text for it and stores `status`.
* Retries reuse the existing worktree; a new session gets the previous session's footer in its prompt.
* Everything the orchestrator posts to Linear goes through one `linearComment()` helper that adds the footer and dedupes by `(issueId, sha256(body))`.
DOD:
* Unit tests for claim atomicity (simulated concurrent poll), prompt rendering (snapshot), worktree lifecycle (temp git repo), footer parsing.
* Integration test with a mocked Agent SDK stream that emits assistant, tool_use and result messages.
* Live run: a real `Ready for Claude` issue on a toy repo produces a worktree, a session, a PR, `In Review` state and a PR attachment; recording attached.
* `/status` endpoint screenshot; Coolify deploy green; restart mid-session marks the session `interrupted` and re-queues the issue.
* README with runbook (start, stop, drain, inspect a session); changelog entry; Linear comment with the recording and PR link.
EDGE:
* Two orchestrator replicas: claims use `SELECT ... FOR UPDATE SKIP LOCKED` on `claims`; only one wins.
* Worktree directory exists but is dirty from a crash: stash to `crash/<timestamp>` branch, recreate.
* Session ends with `stop_reason` `max_turns` or budget exhaustion: commit `wip:`, push, comment, mark `partial`.
* Linear API down: keep running sessions, pause claiming, exponential backoff, alert in logs.
* Issue moved out of `Ready for Claude` between poll and claim: `updatedAt` guard fails, skip.
* Branch already exists on origin from a previous attempt: check out and rebase onto `main` instead of failing.
* Agent SDK throws a `refusal` stop: record `stop_details.category`, post to `Needs Justin` with the category, do not retry.
DEPS: * `pm-linear/configure-workspace` (states, labels, snapshot ids).
* `forge/branch-policy` (branch names, commit rules, worktree conventions).
* `pm-linear/session-playbook` (the prompt points sessions at it).
* Soft: `forge/bot-accounts` for per-character assignees (falls back to one bot user), `data-layer/postgres-provision` (falls back to SQLite via `better-sqlite3` in dev).


## PAP-97 [P0 Build M prio1 Backlog] Set up Linear webhooks into the orchestrator and PR status back to Linear as comments with screenshots and review verdicts
key=pm-linear/webhooks milestone=Orchestrator claims and ships issues agent=Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel 
blockedBy=['PAP-96'] blocks=['PAP-101']
GOAL: Make Linear the only window Justin needs: Linear events reach the orchestrator instantly, and every PR event, CI gate result, screenshot set and reviewer verdict is written back to the issue as a structured comment with images. Nobody should have to open GitHub or Forgejo to know how an issue is doing.
SCOPE: In:

* Inbound receiver `POST /webhooks/linear` (Hono on Node 22, inside `imagine-os/paperos-orchestrator`): verifies `Linear-Signature` (HMAC-SHA256 of the raw body with the webhook secret), rejects payloads whose `webhookTimestamp` is older than 60 s, dedupes by `webhookId`, then dispatches on `type` (`Issue`, `Comment`, `IssueLabel`, `Project`) and `action` (`create`, `update`, `remove`) to handlers registered by other modules (`issue-contract`, `justin-queue`, `orchestrator` fast-poll).
* Inbound `POST /webhooks/github` and `POST /webhooks/forgejo`: PR opened/synchronised/closed/merged, `check_suite`/`workflow_run` completed, `pull_request_review` submitted; signature verification per forge (`X-Hub-Signature-256`; Forgejo uses the same header format).
* Outbound to Linear: `attachmentCreate` for the PR (title, subtitle with state, icon), a single "PR status" comment that is edited in
SPEC(first 1200): * Event bus: in-process typed emitter `events.on("linear.issue.update", handler)`; every event also persisted to `orchestrator.events` for replay (`pnpm events:replay --since`).
* Status comment template `src/webhooks/templates/pr-status.md`; the comment id is stored in `sessions.status_comment_id`; body ends with the `paperos-session` footer including `status: "in-review"`.
* Screenshot policy: up to 7 images (one per breakpoint from `quality/playwright-matrix`) plus a link to the full set; each image under 2 MB, resized with `sharp` if larger.
* Mapping PR to issue: branch name contains the Linear key (from `forge/branch-policy`); fallback to `Closes PAP-123` in the PR body.
* All outbound Linear calls go through the rate-limited `linearComment()` helper from the orchestrator; comment edits are debounced 5 s so rapid CI events collapse into one update.
DOD:
* Signature verification tests for all three sources including tampered body and stale timestamp.
* Replaying 200 recorded events produces the same status comment (snapshot test).
* Live demo: open a PR on a toy repo, watch the Linear issue gain an attachment and a status comment with screenshots within 60 s of CI finishing; screen recording attached.
* Screenshots display inline in Linear web (1280 px) and the Linear mobile app (375 px); both screenshotted.
* Duplicate delivery test shows one comment, not two.
* Runbook section on rotating webhook secrets; changelog entry; Linear comment with recording.
EDGE:
* PR opened before the issue is claimed (a human or a stray session): still link it, set `In Review`, comment that no session record exists.
* One PR closes multiple issues: status comment on each.
* Screenshot upload fails (Linear file size or network): post comment with links only and retry uploads in the background.
* GitHub and Forgejo both fire for the same mirrored commit: dedupe by commit SHA and event kind.
* Comment edit fails because the comment was deleted: create a new one and update the stored id.
* Webhook secret rotation: accept the previous secret for 24 hours.
* Force-push rewrites history: mark previous gate results stale in the table.
DEPS: * `pm-linear/orchestrator` (service, DB, helpers).
* Interfaces with `quality/playwright-matrix` (artifact naming `screenshots/<page>/<width>.png`) and `quality/review-agents` (review body JSON block); coordinate names via a shared `packages/contracts` in the orchestrator repo.


## PAP-98 [P0 Build M prio2 Backlog] Track Claude credit spend per issue and project and post a daily burn report to Linear
key=pm-linear/credit-metering milestone=Orchestrator claims and ships issues agent=Built by Atlas (lead); reviewed by Sentinel (Code Reviewer) 
blockedBy=['PAP-96'] blocks=['PAP-111']
GOAL: Know at all times how much of the roughly $10,000 of Claude Fable 5.1 credit has been spent, by which issue, project and character, and whether the plan's 12/45/30/8/5 split is holding. A daily burn report lands in Linear so Justin can steer without opening a dashboard, and the numbers feed `agents/cost-controls`.
SCOPE: In:

* Metering table `orchestrator.usage_events(id, session_id, issue_id, project_key, character, model, input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens, cost_usd, turns, duration_ms, recorded_at, source)` populated from the Agent SDK `result` message (`total_cost_usd`, `usage`) and, for hook-based sessions, from transcript JSONL `usage` fields via `agents/prompt-logging-hook`.
* Price table `src/metering/prices.ts` with Fable 5.1 rates ($10 input, $50 output per million tokens; cache reads $0.25 per million; cache writes at the published multiplier) and a fallback for other models; used only to recompute when the SDK cost is absent, otherwise the SDK figure is authoritative.
* Budget ledger: `budgets(scope_type, scope_key, allocated_usd, spent_usd)` seeded from plan.json `budget[]` shares of a configurable `totalUsd` (default 10000) and per-project allocations.
* 
SPEC(first 1200): * Area classification: Type label maps to budget area (Spec/Research to planning, Build/Infra to building, Review to review, Docs to docs) with Research separated at 5 percent as in plan.json.
* Report rendered from `templates/burn-report.md` with a small ASCII sparkline of the last 14 days; keep under 3000 characters for mobile.
* Reconciliation: weekly job compares the metered total with the Anthropic Console usage export (CSV dropped in `ops/metering/console/`) and reports drift; drift above 10 percent flags the report.
* Idempotency: `usage_events` unique on `(session_id, source)`.
* Zod schemas for the result message subset used, so SDK shape changes fail loudly.
DOD:
* Unit tests: price recomputation matches SDK cost within 1 percent on 20 recorded sessions; area classification; cap detection.
* Three daily reports posted in staging, screenshots at 375 px and 1280 px.
* `pnpm burn` output for the current spend pasted in this issue.
* Reconciliation job run once against a real Console export.
* Docs: `docs/pm/credit-metering.md` explaining sources, prices, caps and how to change `totalUsd`; changelog entry; Linear comment with screenshots.
EDGE:
* Session crashes before the `result` message: sum `usage` from streamed assistant messages and mark `source: "partial"`.
* Same issue worked by three sessions (retries): cost aggregates; report shows attempts count.
* Model differs from Fable 5.1 (a Sonnet sub-agent): price by `model` field, never assume.
* Cache read tokens dominate: report cache hit ratio; low ratio is a prompt-design signal for Atlas.
* Console export lags a day: reconcile on a 48-hour delay window.
* Negative or missing `total_cost_usd` (SDK bug): recompute from tokens, flag.
* Budget total changed mid-programme: recompute shares, keep history of allocations.
DEPS: * `pm-linear/orchestrator` (sessions table and result stream).
* Feeds `agents/cost-controls`; consumes `agents/prompt-logging-hook` for non-SDK sessions when it lands.


## PAP-99 [P1 Build M prio1 Backlog] Implement concurrency controls: max parallel sessions, file-lock hints and dependency-aware scheduling from dependsOn
key=pm-linear/concurrency milestone=Orchestrator claims and ships issues agent=Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel 
blockedBy=['PAP-96'] blocks=[]
GOAL: Let twenty sessions run at once without merge storms or blocked work: the orchestrator schedules issues by dependency readiness, keeps sessions that touch the same files apart, and caps parallelism globally, per repo and per character. Throughput goes up while conflict rate stays near zero.
SCOPE: In:

* Dependency-aware scheduling: an issue is eligible only when every Linear `blockedBy` relation is `Done` (or the blocker is `In Review` and the issue is labelled `can-start-on-review`); build a DAG from relations each poll and detect cycles.
* File-lock hints: issues declare `Files:` glob lines in the `Scope` section (for example `packages/ui/**`); the scheduler will not start two sessions whose globs intersect on the same repo; hints are also learned by recording the paths each session's PR touched and warning when a new issue's globs miss them.
* Limits from `orchestrator.config.yaml`: `maxParallel` (global, default 12), `perRepo` (default 6), `perCharacter` (default 3, Sentinel 6 because review is cheap to parallelise), `perProject` optional.
* Priority scoring: `score = priorityWeight + ageHours*0.1 + unblocksCount*2 + phaseWeight`, where `unblocksCount` is the number of issues
SPEC(first 1200): * Module `src/scheduler/` with pure functions: `buildGraph(issues, relations)`, `eligible(graph, running, config)`, `score(issue, graph)`, `conflicts(globsA, globsB)` using `picomatch`; the loop from `pm-linear/orchestrator` calls `scheduler.next()` instead of taking the first issue.
* Globs parsed from the issue description by the contract parser (`pm-linear/issue-contract` adds an optional `Files` line; missing globs mean "unknown", which conflicts with nothing but is flagged in `/status` as a risk).
* Learned paths stored in `orchestrator.issue_paths(issue_id, path)` from `git diff --name-only origin/main...HEAD` at PR open.
* Cycle detection reports the cycle to `Needs Justin` once (deduped by cycle hash).
* Fairness: no project starves; if a project has had zero sessions in 6 hours while eligible, add a starvation bonus.
DOD:
* Property-based tests (fast-check) that `eligible()` never returns two issues with intersecting globs on one repo and never returns an issue with an open blocker.
* Simulation test: 200 synthetic issues from plan.json with its `dependsOn` edges scheduled with `maxParallel` 12 completes with zero conflicts and total makespan printed; result table attached.
* Live soak: 8 real issues in parallel on staging for 4 hours with conflict rate (PRs needing manual rebase) below 10 percent; report in comment.
* `/status` screenshot at 1280 px showing eligibility reasons.
* Docs section in the orchestrator README; changelog entry; Linear comment with the simulation and soak results.
EDGE:
* Blocker is `Canceled` or `Duplicate`: treat as satisfied but comment on the dependent issue so a human can confirm.
* Globs like `**` on one issue: it conflicts with everything; warn in `/status` and require it to run alone.
* Relations changed mid-run (Justin adds a blocker to an `In Progress` issue): do not kill the session; note it in the status comment.
* Two repos share a package via git submodule: treat globs as repo-scoped only; document the limitation.
* Priority `Urgent` set by Justin: bypass `perProject` and merge-queue pause but not global `maxParallel`.
* Scheduler exception: fall back to the simple FIFO from the orchestrator and log loudly rather than stall the queue.
DEPS: * `pm-linear/orchestrator` (loop, claims, config).
* Uses relation data created by the Decomposer and validated by `pm-linear/issue-contract`.


## PAP-100 [P1 Spec M prio2 Backlog] Model PM entities in PaperOS (project, issue, cycle, milestone, comment, label) mirroring Linear's schema
key=pm-linear/pm-data-model milestone=PM module syncs both ways agent=Built by Forge (Schema Wright sub-agent); reviewed by Sentin
blockedBy=['PAP-33'] blocks=['PAP-204', 'PAP-102', 'PAP-101']
GOAL: Give PaperOS its own project-management tables shaped like Linear's model so that issues, projects, cycles, milestones, comments and labels can be mirrored one-to-one today and owned outright later. This is a spec-plus-schema issue: it produces the Drizzle schema, the page specs for the PM entities and the mapping document, not UI.
SCOPE: In:

* Drizzle schema in `packages/core/src/pm/schema.ts` (paperos-template): `pm_team`, `pm_workflow_state`, `pm_project`, `pm_milestone`, `pm_cycle`, `pm_issue`, `pm_issue_relation`, `pm_label`, `pm_issue_label`, `pm_comment`, `pm_attachment`, `pm_external_ref`.
* Every table has `tenant_id` (RLS from `data-layer/rls-tenancy`), `id` (uuid v7), `created_at`, `updated_at`, `archived_at`, `created_by` (a principal id, human or agent from `identity/agent-principals`).
* `pm_issue` fields mirror Linear: `identifier` (`PAP-123`, unique per team), `number`, `title`, `description` (markdown), `priority` (0-4), `estimate`, `state_id`, `assignee_id`, `parent_id`, `project_id`, `cycle_id`, `milestone_id`, `due_date`, `sort_order`, `started_at`, `completed_at`, `canceled_at`.
* `pm_external_ref(entity_type, entity_id, system, external_id, external_url, synced_at, external_updated_at)` unique on `(
SPEC(first 1200): * Invariants enforced in DB: `identifier` unique per `(tenant_id, team_id)`; `parent_id` cannot equal `id`; relation types enum `blocks|blocked_by|related|duplicate`; a completed state sets `completed_at` via trigger.
* Comments support `body` markdown, `parent_comment_id` for threads, and `anchor` jsonb for future `collab/comments` element anchoring.
* Labels: `parent_id` for groups, `is_group` boolean, mirrors Linear label groups.
* Seeds: `pnpm db:seed pm` inserts team PAP, the six states, four label groups and three sample issues for Storybook and tests.
* Migration `0xx_pm.sql` generated by `drizzle-kit`; RLS policies added in the same migration using the tenant helper from `data-layer/rls-tenancy`.
DOD:
* Migration applies and rolls back cleanly on a fresh Postgres 17; `pnpm db:check` passes.
* Cross-tenant test from the RLS harness proves issues of tenant A are invisible to tenant B.
* oRPC procedures have Vitest tests for create, update, archive, list with filters (state, assignee, label, project) and cursor pagination.
* Three page specs validate with `spec-builder/validator`.
* `docs/pm/data-model.md` reviewed by Quill; ER diagram renders; data dictionary entries appear once `data-layer/data-dictionary` runs.
* Changelog entry; Linear comment with the mapping table and migration name.
EDGE:
* Linear identifiers collide after a team key rename: `identifier` is derived from `team.key + number` at write time and stored; renames keep old identifiers as aliases in `pm_external_ref`.
* Issue moved between projects: allowed; `pm_milestone` must belong to the new project or be nulled (check constraint via trigger).
* Deleting a label in use: soft-delete only; `pm_issue_label` rows retained for history.
* Very large descriptions (over 1 MB): store as `text`, but API rejects above 200 KB with a clear error.
* Assignee is an agent principal that is later disabled: keep the reference; UI shows the disabled badge.
* Cycles disabled for a team: `cycle_id` nullable and all cycle procedures return empty.
DEPS: * `data-layer/core-entities` (tenant, user, membership tables and id conventions).
* Uses `data-layer/rls-tenancy` helpers and `data-layer/api-layer` for procedures; `spec-builder/schema` for the page specs (if not yet merged, write specs against its draft and mark them `draft: true`).


## PAP-101 [P2 Build L prio2 Backlog] Build bidirectional Linear sync (GraphQL + webhooks) with conflict rule: Linear wins until cutover
key=pm-linear/linear-sync milestone=PM module syncs both ways agent=Built by Nova (lead) with Forge (Schema Wright) for the outb
blockedBy=['PAP-97', 'PAP-100'] blocks=[]
GOAL: Keep the PaperOS PM tables and Linear team PAP in step both ways so the same issues are visible in either tool, with one rule that removes all ambiguity until cutover: when both sides changed, Linear wins. Edits made in PaperOS boards (`pm-linear/board-views`) reach Linear within seconds, and everything the orchestrator does in Linear appears in PaperOS.
SCOPE: In:

* Sync service `packages/pm-sync` in paperos-template (runs inside the API process or as a worker): initial backfill, incremental inbound via Linear webhooks (reusing the receiver from `pm-linear/webhooks`), and outbound on PaperOS mutations via an outbox table.
* Entities: teams, workflow states, projects, milestones, cycles, issues, relations, labels, comments, attachments; users mapped to principals by email, agents mapped by bot account.
* Inbound: webhook `data` upserted into `pm_*` tables using `pm_external_ref`; `updatedFrom` used to detect which fields changed; deletions and archives mirrored as `archived_at`.
* Outbound: `pm_outbox(id, entity_type, entity_id, op, payload, attempts, next_attempt_at, last_error)` written in the same transaction as the PaperOS mutation; a worker drains it with `@linear/sdk` mutations (`issueCreate`, `issueUpdate`, `commentCreate`, `issueLabelC
SPEC(first 1200): * Backfill uses paginated `issues(first: 100, after)` with `includeArchived: true`, ordered by `updatedAt`, resumable via a `pm_sync_cursor` table; full PAP backfill (a few hundred issues) must finish under 5 minutes.
* Field mapping table lives in `packages/pm-sync/src/mapping.ts`, shared with `pm-linear/pm-data-model` docs; unknown Linear fields are stored in `pm_issue.extra` jsonb so nothing is lost.
* Rate limiting: Linear's complexity-based limits; the worker respects `X-RateLimit-Requests-Remaining` headers, batches label updates and pauses at 10 percent remaining.
* Retry policy: exponential backoff 1 s to 10 min, 8 attempts, then `dead` state visible on the status page.
* Every sync write carries `created_by` = the sync principal from `identity/agent-principals`.
DOD:
* Round-trip tests with a Linear sandbox team (or recorded fixtures via `nock`): create in PaperOS appears in Linear with correct state, labels, assignee; edit in Linear appears in PaperOS; simultaneous edit resolves with Linear winning and a conflict row.
* Backfill of PAP completes and counts match (`issues`, `comments`, `labels`) printed in the comment.
* Loop test: 1000 synthetic edits produce no echo writes (outbox count equals user edits).
* Sync status page screenshot at 375, 768 and 1280 px; Playwright coverage in `quality/playwright-matrix`.
* Runbook `docs/pm/linear-sync.md` (backfill, retry, dead-letter, key rotation); changelog entry; Linear comment with test results.
EDGE:
* Webhook arrives before the outbox write that caused it is committed (our own create): match by an `idempotencyKey` we embed in the Linear description footer or `attachment` metadata, not just by id.
* Linear user with no PaperOS principal: create a placeholder external principal rather than dropping the assignee.
* Label group missing in PaperOS: create it on the fly, flagged `source: linear`.
* Issue deleted permanently in Linear (not archived): keep the PaperOS row, set `archived_at`, add `deleted_externally` flag.
* Description contains Linear-specific markup (mentions `@user`, issue embeds): store raw; render with a fallback formatter.
* Webhook outage for hours: backfill by `updatedAt > last cursor` on reconnect closes the gap.
* Cycle changes on a team where PaperOS has cycles disabled: store but do not surface.
DEPS: * `pm-linear/pm-data-model` (tables, procedures).
* `pm-linear/webhooks` (verified receiver and event bus).
* Uses `identity/agent-principals` for the sync principal.


## PAP-102 [P2 Build M prio2 Backlog] Render PM board, list and timeline views using the tables/views engine
key=pm-linear/board-views milestone=PM module syncs both ways agent=Built by Nova (Views Engineer sub-agent); reviewed by Sentin
blockedBy=['PAP-167', 'PAP-100'] blocks=[]
GOAL: Show project management inside the product: the PM entities from `pm-linear/pm-data-model` rendered as a kanban board grouped by workflow state, a filterable list and a timeline of projects and milestones, all built as configurations of the table and views engine rather than bespoke components. Dragging a card between columns changes state and (through sync) moves the issue in Linear.
SCOPE: In:

* Route `/pm` in `apps/web` with sub-routes `/pm/board`, `/pm/list`, `/pm/timeline` and `/pm/issues/:identifier`, declared through page specs `specs/pm/board.spec.yaml`, `list.spec.yaml`, `timeline.spec.yaml` (detail spec from the data-model issue).
* Board: `tables/kanban-view` configured with data source `pm_issue`, group by `state_id` ordered by `pm_workflow_state.position`, swimlanes optional by `project_id` or assignee, card fields (identifier, title, priority icon, assignee avatar, labels, estimate), WIP limit on `In Review` and `Needs Justin` (5) with a visual warning, drag to change state via `pm.issues.update`.
* List: `tables/grid-view` with columns identifier, title, state, priority, assignee, labels, project, updated; inline edit for state, priority, assignee; filter builder and multi-sort from `tables/filter-sort-group-ui`; saved views "My issues", "Ready for Claude", "
SPEC(first 1200): * Views are stored as `view` records per `tables/view-model-spec`, seeded by `pnpm db:seed pm-views`; no hard-coded column configs in components.
* Components come only from `packages/ui` and `packages/views`; the PM feature adds `apps/web/src/features/pm/` with cell renderers for priority, state and character badge registered in the views cell registry.
* Optimistic updates through the local-first layer (`data-layer/local-first-sync`) so drag feels instant; failures roll back with a toast.
* Responsive: at widths under 768 px the board becomes a single-column state picker with horizontal swipe between columns; list hides secondary columns; timeline switches to a vertical milestone list.
* Empty, loading and error states declared in the page specs and implemented.
DOD:
* Three page specs validate; conformance tests from `spec-builder/conformance-tests` pass.
* Playwright screenshots of board, list, timeline and detail at 320, 375, 768, 1024, 1280, 1920 and 2560 px in light and dark themes, attached to the PR and Linear comment.
* Drag a card on staging and see the Linear issue change state within 10 s (screen recording).
* Vitest for cell renderers; Playwright e2e for filter, sort, drag, keyboard shortcuts.
* axe passes on all four pages; keyboard-only drag alternative works (from `input/drag-drop`).
* GitHub Pages demo link with seeded data; changelog entry; Linear comment with demo and screenshots.
EDGE:
* 2000 issues in one column: virtualised column; group counts computed server-side.
* Drag to `Needs Justin` when five are already open: block with an explanation, mirroring the governor in `pm-linear/justin-queue`.
* Sync conflict after a drag (Linear wins): card snaps back with a "changed in Linear" toast.
* Issue with no project on the timeline: shown in an "Unscheduled" lane.
* User lacks permission to change state (permission engine): drag handle disabled, tooltip explains.
* Offline: drag queues locally with a pending badge; resolved on reconnect.
* Character badge for a session that died without ending: indicator times out after 15 minutes of no heartbeat.
DEPS: * `pm-linear/pm-data-model` (tables, procedures, detail spec).
* `tables/kanban-view` (and through it `tables/query-compiler`, `input/drag-drop`); also uses `tables/grid-view`, `tables/filter-sort-group-ui`, `tables/calendar-timeline-gantt`.
* Live Linear reflection requires `pm-linear/linear-sync`; the views work without it against local data.
