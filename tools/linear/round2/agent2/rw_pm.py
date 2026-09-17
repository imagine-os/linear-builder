"""Rewritten descriptions for pm-linear (PAP-91..PAP-102). Placeholders {{key}} resolve to identifiers of issues created in round 2."""
DESCRIPTIONS = {}

DESCRIPTIONS["PAP-91"] = """**Goal**

Turn the Linear configuration of team PAP into code: one idempotent script that reads the live workspace, prints the diff against the plan and applies only what is missing, so every future `paperos create <app>` project gets the same states, labels and templates. The live team already has most of it from the round-1 import; this issue must never "fix" what exists.

**Scope**

* In: `ops/linear/configure-workspace.ts` in `imagine-os/paperos-orchestrator` (`@linear/sdk`, `--check` and `--apply`), the committed snapshot `linear-workspace.json`, a `Character` label group with nine children (Atlas, Forge, Iris, Quill, Sentinel, Nova, Ledger, Beacon, Scout), the `PaperOS Spec` issue template updated to the contract sections of PAP-93, a project template with three milestones, `docs/pm/linear-setup.md`.
* Out: reconciling issue bodies and estimates (not needed: this issue treats the live workspace as correct), the contract validator (PAP-93), deleting or renaming anything.

**Spec**

* Live facts the script treats as correct: states `Backlog`, `Todo`, `Ready for Claude` (unstarted), `In Progress`, `In Review`, `Needs Justin` (started), `Done`, `Canceled`, `Duplicate`; groups `Phase` (P0/P1/P2) and `Type` (Research/Spec/Build/Review/Infra/Docs); ungrouped `Customer`, `Staff`, `Developer`, `Agent` because Linear allows one label per group and 53 issues carry several surfaces; the empty `Surface` group label; `issueEstimationType: notUsed`. `Todo` stays and is documented as "human parking, never polled".
* Desired additions: `Character` group via `issueLabelCreate` with `parentId`; template body from `docs/pm/issue-contract.md`; `workflowStateUpdate` only for description and color, never name or type.
* `--check` exits 1 with a table `(kind, name, field, live, wanted)`; `--apply` creates or updates, then re-runs `--check` and must print no drift. Refuses to run unless `team.key === "PAP"` or `--team` is explicit.
* Writes `linear-workspace.json` with ids of every state, label, template and project; later scripts import ids from it.

**Interface contract**

* Provides: `linear-workspace.json` (`{ states: Record<StateName, id>, labels: Record<"Phase/P0" | ... | "Character/Atlas", id>, templates, projects }`), TypeScript type `WorkspaceIds` exported from `src/linear/workspace.ts`; `pnpm linear:configure --check|--apply`.
* Consumers: PAP-93 (label and state ids), PAP-96 (state ids for claims), PAP-99 (Character routing), PAP-22 (`paperos create` reuses the script).
* Requires: Linear API key with admin scope (already configured through the proxy).

**Definition of done**

* `--check` on the live team reports only the `Character` group and template drift before `--apply`, nothing after; two consecutive `--apply` runs are no-ops.
* Nine `Character` labels exist under one group; no existing label, state or issue changed name, type or state.
* `linear-workspace.json` committed and imported by the orchestrator repo's `src/linear/`.
* `docs/pm/linear-setup.md` documents the live configuration including why `Todo` and ungrouped surfaces stay; screenshot of the workflow settings at 1280 px.
* Changelog entry and a Linear comment with the diff table before and after.

**Test plan**

* Unit (Vitest): diff engine against fixtures of the live snapshot (`round2/linear-snapshot.json` reduced), asserting zero destructive operations are ever planned; name matching is case-insensitive.
* Integration: mocked SDK proving `--apply` issues only `issueLabelCreate`, `templateUpdate`, `workflowStateUpdate({description,color})`.
* Live: `--check` output pasted in the issue before and after.
* No visual checks beyond the settings screenshot.

**Demo**

Run `pnpm linear:configure --check` (drift table), `--apply`, `--check` again (empty), then open Linear labels and show the `Character` group. Ninety seconds.

**Edge cases**

* A `Character` child already exists ungrouped: move it under the group with `issueLabelUpdate({parentId})`, do not create a duplicate.
* Label with the same name in another team: filter by `team.id`.
* Rate limit (`RATELIMITED` or 429): sleep 60 s and retry up to five times.
* Someone renamed a state since the snapshot: report as drift with `manual` marker, never rename back.
* API key without admin scope: fail before the first mutation.

**Dependencies**

None (`readyNow`). Blocks PAP-93, PAP-94, PAP-95, PAP-96, PAP-22.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel (Code Reviewer).

**Size**

S
"""

DESCRIPTIONS["PAP-92"] = """**Goal**

Write the one document every Claude Code session reads first: how an issue is claimed, what must be read before code is written, how progress is reported to Linear, how the PR is opened and how the session ends. It is the human-readable contract that PAP-96 automates and PAP-104 embeds in every character's prompt.

**Scope**

* In: `docs/pm/session-playbook.md`, mirrored to `.claude/rules/session-playbook.md` in `paperos-template`; the comment templates; the footer JSON schema `packages/agents/src/session-footer.schema.json`; a worked example transcript.
* Out: branch and commit rules (PAP-46, linked), handoff semantics (PAP-108), character prompts (PAP-104).

**Spec**

* Structure: Purpose; lifecycle diagram (mermaid, states mirror Linear); steps claim, orient, plan, build, verify, report, hand off, end with exact commands (`git worktree add`, `pnpm i --frozen-lockfile`, `pnpm check`, `gh pr create --template`); comment templates; stop conditions; FAQ. 1500-2500 words, under ten minutes of reading.
* Required reading order: issue body sections, linked `specs/**` files, `CLAUDE.md`, character memory (PAP-109), last two Linear comments, ADRs touched.
* Reporting: one `Session started` comment (worktree, branch, character, model), progress comments at most every 30 minutes, one `Session ended` comment (PR, gates, cost). Every comment ends with a fenced ```` ```paperos-session ```` JSON block.
* Footer schema: `{ playbookVersion: 1, sessionId, character, issue, status: "started" | "progress" | "ended" | "partial" | "contract-failed" | "handoff", costUsd, turns, pr?, branch, handoff? }`. `handoff` is defined by PAP-108 and referenced by `$ref`.
* Stop conditions: no linked spec (comment `needs-spec`), claimed by another session, budget warning from PAP-111, Justin comment (acknowledge first).

**Interface contract**

* Provides: `session-footer.schema.json` and type `SessionFooter` (`packages/agents/src/session-footer.ts`), the comment templates `templates/session-{started,progress,ended}.md`, `playbookVersion` constant.
* Consumers: PAP-96 parses the footer to set state; PAP-97 and PAP-98 read `status` and `costUsd`; PAP-105 `linear-update` renders the templates; PAP-104 prompts point at `.claude/rules/session-playbook.md`; PAP-93 validator accepts `status: "contract-failed"`.
* Requires: nothing at runtime.

**Definition of done**

* Both copies identical (CI diff check in gate 1).
* A `claude -p` dry run given only the playbook and a toy issue produces three comments whose footers validate against the schema.
* Every "must" sentence has a check named beside it (Sentinel review).
* Linked from the repo README until the docs engine (PAP-128) renders it; changelog entry; Linear comment with the transcript.

**Test plan**

* Unit: `ajv` validation of the schema against 10 valid and 10 invalid footers; word-count test 1500-2500.
* Integration: script `scripts/playbook-dryrun.ts` runs the toy session and asserts three comments parse.
* Docs lint: every relative link resolves; mermaid renders in Storybook docs page.
* No visual breakpoints; the document is read in Linear and the repo.

**Demo**

Open the playbook, run `pnpm playbook:dryrun`, watch three comments appear on the toy issue and `pnpm footer:validate` print `ok` for each. Under two minutes.

**Edge cases**

* Context compacted mid-task: the last footer is the recovery point; playbook says re-read it.
* Two sessions claim one issue: check assignee and last `Session started`; later session exits with `status: "ended", reason: "duplicate-claim"`.
* Crashed worktree exists: reuse if branch matches, else suffix `-2`.
* Budget cap with uncommitted work: commit `wip:`, push, comment `partial`, stop.
* Justin comments mid-session: highest priority, acknowledged in the next comment.

**Dependencies**

None (`readyNow`). Blocks PAP-96. Consumed by PAP-104, PAP-105, PAP-108.

**Agent**

Built by Quill (lead); reviewed by Atlas for operational fit.

**Size**

S
"""

DESCRIPTIONS["PAP-93"] = """**Goal**

Define what an issue must contain before a machine may build it, and enforce it with a webhook validator that bounces non-conforming issues out of `Ready for Claude` with a comment listing exactly what is missing. The rules must match the live workspace, so the 206 issues already in the queue pass unchanged.

**Scope**

* In: `docs/pm/issue-contract.md`; pure validator `src/contract/validate.ts` in the orchestrator repo; webhook handler; fixtures; `pnpm contract:audit` over the whole team.
* Out: workspace configuration (PAP-91), bulk fixes of existing issues (none planned: PAP-91 treats the live workspace as correct), drafting help for humans ({{pm-linear/inbound-triage}}).

**Spec**

* Required sections, bold headings or `##`, any order (order mismatch warns): Goal, Scope, Spec, Definition of done, Edge cases, Dependencies, Agent, Size. Recommended, warn if absent: Interface contract, Test plan, Demo. Optional `Files:` glob lines in Scope for PAP-99.
* Metadata rules aligned with reality: exactly one `Phase/*`, exactly one `Type/*`, at least one surface label from `Customer | Staff | Developer | Agent`, `Character/*` optional until PAP-91 lands then warning, Size read from the description (`S | M | L`), Linear estimate not required, project required. Spec link (`specs/**/*.spec.yaml` or a Linear document) required only for `Type/Build` issues whose Scope names a route; warning until 2026-09-22, error after (`--strict` date in config).
* `validateIssue(issue): ContractResult = { ok, violations: [{ code, severity: "error" | "warn", message, fix }] }`. Codes: `MISSING_SECTION`, `EMPTY_SECTION`, `BAD_SIZE`, `LABEL_PHASE`, `LABEL_TYPE`, `LABEL_SURFACE`, `NO_PROJECT`, `NO_SPEC_LINK`, `BLOCKED_BY_OPEN` (warn), `DESCRIPTION_TOO_LONG`.
* Handler on `Issue.update` to `Ready for Claude`: errors move the issue to `Backlog`, add label `needs-contract`, post the violations comment; warnings comment only. If the last actor is Justin, comment but never move.
* Results stored in `contract_checks(issue_id, checked_at, ok, violations_json)`.

**Interface contract**

* Provides: `validateIssue`, `parseSections(markdown): Record<Section, string>`, `parseFilesGlobs(scope): string[]`, type `ContractResult`, the `needs-contract` label id, comment template `templates/violations.md` with footer `status: "contract-failed"`.
* Consumers: PAP-96 re-validates before claiming; PAP-99 uses `parseFilesGlobs`; PAP-118 and {{pm-linear/inbound-triage}} call `validateIssue` before creating issues; {{pm-linear/weekly-reaudit}} runs `contract:audit`.
* Requires: state and label ids from `linear-workspace.json` (PAP-91), webhook receiver from PAP-97 (minimal receiver shipped here if PAP-97 is later).

**Definition of done**

* Fixture suite of 12 good and 20 bad issues passes; `validate.ts` coverage above 95 percent.
* `pnpm contract:audit` on all live PAP issues reports zero errors (warnings allowed) and the table is posted here.
* Live bounce of a deliberately bad issue within 10 seconds, recording attached; a good issue is untouched.
* Contract doc published; `PaperOS Spec` template matches the section names.
* Changelog entry; Linear comment with the audit table and recording.

**Test plan**

* Unit: each violation code has a pass and fail fixture; heading normalisation (`**Goal**` vs `## Goal`); 50 k character truncation.
* Integration: replay of 30 recorded webhook payloads including duplicate deliveries yields one comment each.
* e2e: live bounce on a `contract-test` labelled issue, then cleanup by moving it back.
* No visual breakpoints; comment rendering checked in Linear web and mobile app screenshots.

**Demo**

Move a fixture issue with a missing Definition of done to `Ready for Claude`; within ten seconds it returns to `Backlog` with a comment naming `MISSING_SECTION` and the fix. Then add the section and move it again: silence. One minute.

**Edge cases**

* Validator's own bot moves an issue: ignore by `actor.id`.
* Sub-issue whose parent has a spec link: inherits `NO_SPEC_LINK` satisfaction.
* Sections in a foreign heading style (`Goal:` plain): `MISSING_SECTION` with a fix pointing to the template.
* Size given as `Small`: normalise to `S`.
* Webhook delivered twice: idempotent by `webhookId`.

**Dependencies**

Blocked by PAP-91. Soft: PAP-97. Consumed by PAP-96, PAP-99, PAP-118.

**Agent**

Built by Atlas (Decomposer sub-agent); reviewed by Sentinel.

**Size**

M
"""

DESCRIPTIONS["PAP-94"] = """**Goal**

Keep the only human reviewer's queue small and fast: `Needs Justin` holds at most five open items, each is a pre-digested decision card with one-word replies, defaults apply when he is silent, and anything a machine can decide is refused entry. This is what makes the rest of the plan safe to run unattended.

**Scope**

* In: `docs/pm/justin-queue.md` (admission rules), the decision card format, the reply grammar, the queue governor and daily digest in the orchestrator, the `queued-for-justin` overflow label.
* Out: the notification transport (PAP-136 delivers the digest later; until then the digest is a Linear comment), release-train specifics (PAP-88 consumes the grammar).

**Spec**

* Admission: release-candidate approval, irreversible actions (production deploy, data deletion), spend above `justinQueue.spendThresholdUsd` (default 500), external communication, credential grants, new characters. Refused: code review, test failures, library choices under the rubric.
* Decision card (issue description or comment): `Decision needed`, `Recommendation` (one sentence), `Options` (max 3 with cost and risk), `Deadline`, `Default if no answer` (applied after `defaultTimeoutHours: 48` unless `hard-block`), `Context links`.
* Reply grammar (first line of a comment by Justin): `approve`, `reject`, `option <n>`, `defer <n>d`, `ask: <question>`, multiple `PAP-123: approve` pairs. Regex first, LLM classification only on regex miss and only to ask a clarifying question, never to act.
* Governor in `src/justin/governor.ts`: counts open `Needs Justin`; the sixth item gets `queued-for-justin` and stays in its previous state; freeing a slot admits by priority then age. Digest `src/justin/digest.ts` at 14:00 UTC posted to a pinned `Justin digest` issue, under 3000 characters.
* Config in `orchestrator.config.yaml`: `justinQueue.maxOpen: 5`, `defaultTimeoutHours`, `digestCronUtc`, `spendThresholdUsd`.

**Interface contract**

* Provides: `requestDecision(card: DecisionCard): Promise<DecisionHandle>` and `onDecision(handle, cb)` from `src/justin/index.ts`; type `DecisionCard`, `Decision = { verb: "approve" | "reject" | "option" | "defer" | "ask", option?, days?, question? }`; `parseReply(text): Decision[]`; footer statuses `decision-requested | decision-applied`.
* Consumers: PAP-88 release approval, PAP-108 `escalate` handoffs, PAP-111 reserve release, PAP-96 refusal stops, {{pm-linear/inbound-triage}} single-question asks.
* Requires: comment webhooks from PAP-97 (poll fallback every 30 s reads comments on open `Needs Justin` issues), state ids from PAP-91.

**Definition of done**

* Doc published and linked from the playbook (PAP-92).
* Governor bounces the sixth item and admits on free slot within one poll (test with mocked SDK).
* Grammar fixture suite of 30 replies including typos (`aprove`) passes.
* Default application with fake clock tested; `hard-block` never auto-applies.
* Digest posted three consecutive days in staging; screenshots at 375 px (Linear mobile) and 1280 px.
* Changelog entry; Linear comment with screenshots.

**Test plan**

* Unit: `parseReply` table test (30 cases), governor slot arithmetic, deadline computed from the card comment's `createdAt`.
* Integration: end-to-end with `nock`-recorded Linear responses: request, reply, state transition, acknowledgement comment.
* e2e: one real decision card on a `rehearsal` issue answered by Justin; timing recorded.
* Visual: digest rendering in Linear mobile at 375 px and web at 1280 px.

**Demo**

`pnpm justin:request fixtures/deploy-decision.yaml` creates a card in `Needs Justin`; reply `option 2` in Linear; within 30 seconds the issue moves to `In Progress` with an acknowledgement naming option 2. Ninety seconds.

**Edge cases**

* Prose that matches nothing: reply with one `ask:` clarifying question, do not guess.
* `Urgent` item arriving at a full queue: bump the oldest non-urgent item to `queued-for-justin` with a comment.
* Justin edits the issue state instead of commenting: treat the state change as approval of the recommendation.
* Two cards for the same subject: dedupe by `card.key`.
* Reply on a closed card: acknowledge and ignore.

**Dependencies**

Blocked by PAP-91. Soft: PAP-97. Blocks PAP-88 (grammar).

**Agent**

Built by Atlas (lead); reviewed by Sentinel (Code Reviewer).

**Size**

M
"""

DESCRIPTIONS["PAP-95"] = """**Goal**

Close the loop on the issue that started everything without contradicting PAP-29: PAP-5 ("how quickly do we get from blank screen to electrons") is rewritten into a measurable scoreboard issue that links every project of this plan and stays open as the standing benchmark record; PAP-29 owns the weekly measurement and the eventual closure. Nothing is created twice and nothing is closed early.

**Scope**

* In: rewrite of the PAP-5 description (original title untouched, original text preserved in `Original notes`), a generated Decomposition table, `related` relations from PAP-5 to the first issue of each of the 17 projects, `docs/pm/pap5-decomposition.md`.
* Out: closing PAP-5, creating a benchmark child (PAP-29 records results directly on PAP-5), any project edits.

**Spec**

* New PAP-5 body in contract format: Goal restated as "time from `paperos create <app>` to a reviewed page on web and desktop under 4 hours wall-clock and under $150 of credits"; Scope: the 17 projects; Spec: how PAP-29 measures; Definition of done: PAP-29 reports three consecutive weekly runs under target; `Scoreboard` table appended by PAP-29 (date, stage timings, cost).
* Script `ops/linear/decompose-pap5.ts` reads `plan.json`, resolves projects by id from `linear-workspace.json`, renders the table (project, link, phase, contribution to startup time), updates PAP-5 with `issueUpdate`, creates `related` relations to each project's first milestone issue by `createdAt` (for example PAP-13 for app-shell) only if absent. Idempotent.
* Description under 4000 characters; the full table lives in the docs file and is linked.
* PAP-5 stays in `Backlog`, labelled `Phase/P2`, `Type/Review`, `Developer`, project app-shell (unchanged).

**Interface contract**

* Provides: `docs/pm/pap5-decomposition.md`, the `Scoreboard` table format `| date | clone | install | first page | PR | gates | demo URL | total | cost |` that PAP-29 appends to, the list `pap5.relatedIssues` in `linear-workspace.json`.
* Consumers: PAP-29 (writes scoreboard rows and closes PAP-5 when the target holds), PAP-112 handbook (links the origin story), the blueprint document.
* Requires: PAP-91 ids; plan.json in the orchestrator repo.

**Definition of done**

* PAP-5 passes `pnpm contract:audit PAP-5` with warnings only (PAP-93) while keeping the original title.
* 17 `related` relations exist; `issue.relations` output pasted in the comment.
* `Original notes` section preserves Justin's text verbatim.
* Docs file committed; changelog entry; screenshot of PAP-5 at 1280 px.
* No `Needs Justin` item raised; informational comment on PAP-5 explains that PAP-29 owns closure.

**Test plan**

* Unit: table rendering from a plan fixture; idempotency (second run plans zero mutations); character limit check.
* Integration: mocked SDK run creating relations only for missing pairs.
* e2e: live run, then `--check` prints no drift.
* No visual breakpoints beyond the Linear screenshot.

**Demo**

Run `pnpm pap5:decompose --check` (shows planned changes), `--apply`, then open PAP-5 in Linear and click two project links from the table. One minute.

**Edge cases**

* A project from plan.json is missing in Linear: exit non-zero before any update, list the missing names.
* Justin edited PAP-5 since the snapshot: diff and keep his additions under `Original notes`.
* Relation already exists: success, no duplicate.
* First issue of a project is in `Duplicate` state (PAP-6..12 strays): skip strays, choose the first canonical issue.
* Title over the Linear limit: never touched.

**Dependencies**

Blocked by PAP-91. Coordinates with PAP-29 (scoreboard owner).

**Agent**

Built by Quill (Changelog Scribe sub-agent); reviewed by Atlas.

**Size**

S
"""

DESCRIPTIONS["PAP-96"] = """**Goal**

Build the engine that turns Linear into running agents: a long-lived service that polls `Ready for Claude`, claims one issue per free slot, creates a git worktree, launches a Claude Code session configured for the issue's character, streams progress and moves the issue to `In Review` when a PR exists. This is the umbrella; the work is split into three children so cold sessions can finish each in one context window.

**Scope**

* Children (build in order):
  * {{pm-linear/orchestrator/claims}}: Linear polling, atomic claim and state transitions.
  * {{pm-linear/orchestrator/sessions}}: worktree lifecycle and Claude session launch.
  * {{pm-linear/orchestrator/deploy}}: deployment, `/status` endpoint and runbook.
* Out: webhook receiver (PAP-97), metering (PAP-98), scheduling beyond fixed `maxParallel` (PAP-99), the PM data model (PAP-100), sandboxing ({{agents/runtime-sandbox}}).

**Spec**

* Repo `imagine-os/paperos-orchestrator`: TypeScript, Node 22, pnpm, Biome, Vitest; Postgres schema `orchestrator` (SQLite via `better-sqlite3` in dev); config `orchestrator.config.yaml` validated with Zod (`maxParallel` default 4, `pollIntervalMs` 30000, `repos[]`, `characters` path).
* Package layout: `src/linear/`, `src/git/worktree.ts`, `src/session/{launch,prompt}.ts`, `src/loop.ts`, `src/db/`, `src/http.ts`.
* Everything posted to Linear goes through `linearComment()` which appends the PAP-92 footer and dedupes by `(issueId, sha256(body))`.
* Character resolution: `Character/*` label, else project default from `roster.json`, else `Needs Justin`.
* Completion: PR detected on the branch sets `In Review` with an attachment; no PR after the session ends re-queues with `retry-<n>` up to two times, then `Needs Justin`.

**Interface contract**

* Provides: tables `sessions(id, issue_id, character, model, worktree, branch, status, started_at, ended_at, footer_json)`, `claims(issue_id, session_id, claimed_at, updated_at_seen)`, `events(id, session_id, kind, payload, at)`; module API `claimNext()`, `launchSession(claim)`, `linearComment(issueId, body, footer)`; HTTP `GET /healthz`, `GET /status` returning `SessionStatus[]` as defined by {{agents/session-observability}}; typed event emitter `events.on("session.started" | "session.ended" | "issue.claimed" | "pr.detected")`.
* Consumers: PAP-97 (event bus, sessions table), PAP-98 (`result` messages), PAP-99 (`scheduler.next()` replaces FIFO), PAP-111 (abort controller and pre-flight hook), PAP-113 (`/status`).
* Requires: PAP-91 ids, PAP-92 playbook path, PAP-46 branch policy, PAP-25 VPS, bundles from PAP-106 (falls back to default allowlist), bot users from PAP-48 (falls back to one bot user).

**Definition of done**

* All three children Done and their DoDs met.
* Integration test across children: a `Ready for Claude` issue on a toy repo produces a worktree, a session, a PR, `In Review` and an attachment; restart mid-session marks `interrupted` and re-queues; recording attached.
* `roster.json` dry run consumes PAP-104 output.
* README runbook; changelog entry; Linear comment with recording and PR link.

**Test plan**

* Umbrella integration test `test/e2e/orchestrator.e2e.ts` with a mocked Agent SDK stream and a temp git remote: claim, launch, PR, state transitions, restart recovery. Runs in CI nightly.
* Live soak: two issues in parallel on staging for one hour, zero duplicate claims.
* `/status` visual check at 1280 px.

**Demo**

Move a toy issue to `Ready for Claude`; within a minute `/status` shows a session, a branch appears on the forge, and after the session ends the issue is `In Review` with a PR attachment. Two minutes.

**Edge cases**

* Linear API down: keep running sessions, pause claiming, back off exponentially.
* Issue leaves `Ready for Claude` between poll and claim: `updatedAt` guard fails, skip.
* SDK refusal stop: record category, route to `Needs Justin`, do not retry.
* Two replicas: `SELECT ... FOR UPDATE SKIP LOCKED` on `claims`.
* Branch exists on origin: check out and rebase rather than fail.

**Dependencies**

Blocked by PAP-91, PAP-92, PAP-46, PAP-25. Blocks PAP-97, PAP-98, PAP-99, {{agents/session-observability}}.

**Agent**

Built by Atlas (Dispatcher sub-agent) with Forge (Ops Runner) for deployment; reviewed by Sentinel.

**Size**

L (umbrella; children are M, M, S)
"""

DESCRIPTIONS["PAP-97"] = """**Goal**

Make Linear the only window Justin needs: Linear events reach the orchestrator instantly, and every PR event, gate result, screenshot set and reviewer verdict is written back to the issue as one structured, edited-in-place status comment with images. Nobody opens GitHub or Forgejo to know how an issue is doing.

**Scope**

* In: inbound receivers `POST /webhooks/linear`, `/webhooks/github`, `/webhooks/forgejo` in the orchestrator (Hono); the persisted event bus; outbound PR attachment and status comment; screenshot upload policy.
* Out: contract decisions (PAP-93), decision replies (PAP-94), the gate artifacts themselves (PAP-239 defines them).

**Spec**

* Linear: verify `Linear-Signature` (HMAC-SHA256 of raw body), reject `webhookTimestamp` older than 60 s, dedupe by `webhookId`, dispatch on `type` and `action` to handlers registered with `events.on("linear.issue.update")`.
* GitHub and Forgejo: `X-Hub-Signature-256`; events `pull_request`, `check_suite`, `workflow_run`, `pull_request_review`; map PR to issue by the key in the branch name (PAP-46) or `Closes PAP-123` in the body.
* Outbound: `attachmentCreate` once per PR; a single status comment (id in `sessions.status_comment_id`) rendered from `templates/pr-status.md` and edited with 5 s debounce; up to seven screenshots (one per breakpoint from PAP-82), each resized under 2 MB with `sharp`, plus a link to the full set; reviewer verdicts from `security.json` and the review JSON block (PAP-239).
* Every event persisted to `orchestrator.events` with `source`, `delivery_id`, `payload`; `pnpm events:replay --since` re-renders comments.

**Interface contract**

* Provides: `registerWebhookHandler(source, type, action, handler)`, `events` emitter, `postPrStatus(issueId, PrStatus)` with `PrStatus = { pr: { url, number, state }, gates: Record<"gate1" | "gate2" | "gate3" | "gate4", "pending" | "pass" | "fail" | "skipped">, screenshots: { width, url }[], verdicts: Finding[] }`, `verifySignature(source, headers, rawBody)`.
* Consumers: PAP-93 and PAP-94 register handlers; PAP-101 reuses the Linear receiver; PAP-112 `@character` mentions; {{pm-linear/inbound-triage}} listens to `Issue.create` and `Comment.create`.
* Requires: PAP-96 service, sessions table and `linearComment()`; artifact schemas from PAP-239 (`gate1.json`, `visual.json`, `security.json`); screenshot naming `screenshots/<page>/<width>.png` from PAP-82.

**Definition of done**

* Signature tests for all three sources, including tampered body and stale timestamp.
* Replaying 200 recorded events yields byte-identical status comments (snapshot).
* Live: open a PR on a toy repo, see attachment and status comment with screenshots within 60 s of CI finishing; recording attached.
* Duplicate delivery test shows one comment.
* Runbook section on secret rotation; changelog entry; Linear comment with recording.

**Test plan**

* Unit: signature verification, PR-to-issue mapping, debounce collapsing five events into one edit, image resize.
* Integration: recorded fixtures for each event kind through the bus into a mocked Linear client; idempotency on redelivery.
* e2e: toy repo PR on staging with gate artifacts uploaded by a stub workflow.
* Visual: status comment rendered in Linear web at 1280 px and Linear mobile at 375 px, both screenshotted.

**Demo**

Push a commit to a toy PR whose branch carries the issue key; within a minute the Linear issue shows the PR attachment and a status comment with gate badges and seven thumbnails. Ninety seconds.

**Edge cases**

* PR opened before any claim: link it, set `In Review`, note "no session record".
* One PR closes several issues: status comment on each.
* Upload fails: post links only, retry uploads in the background.
* GitHub and Forgejo fire for the same mirrored commit: dedupe by SHA and event kind.
* Comment deleted by a human: create a new one and store the id.
* Secret rotation: accept the previous secret for 24 hours.

**Dependencies**

Blocked by PAP-96 and PAP-239. Blocks PAP-101, {{pm-linear/inbound-triage}}.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel.

**Size**

M
"""

DESCRIPTIONS["PAP-98"] = """**Goal**

Know at all times how much of the roughly $10,000 of credit has been spent, by which issue, project and character, and whether the 12/45/30/8/5 split holds. A daily burn report lands in Linear so Justin steers from his phone, and the live totals feed PAP-111.

**Scope**

* In: `usage_events` and `budgets` tables, the price table, area classification, `pnpm burn`, the daily report, weekly reconciliation against the Anthropic Console export, `docs/pm/credit-metering.md`.
* Out: enforcement (PAP-111), per-character daily pools (PAP-111), the org chart display (PAP-113).

**Spec**

* `usage_events(id, session_id, issue_id, project_key, character, model, input_tokens, output_tokens, cache_creation_tokens, cache_read_tokens, cost_usd, turns, duration_ms, recorded_at, source: "sdk" | "hook" | "partial")`, unique on `(session_id, source)`; populated from the Agent SDK `result` message and from PAP-107 transcripts for hook-based sessions.
* `prices.ts`: per-model rates keyed by model id with `effectiveFrom`; the SDK `total_cost_usd` is authoritative, prices only recompute when it is missing. Unknown model: recompute impossible, flag `PRICE_UNKNOWN`.
* `budgets(scope_type: "area" | "project" | "character", scope_key, allocated_usd, spent_usd, updated_at)` seeded from plan.json shares of `totalUsd` (default 10000); area from Type label (Spec and Research to planning with Research split at 5 percent, Build and Infra to building, Review to review, Docs to docs).
* Report from `templates/burn-report.md`: totals, per area vs share, top ten issues, cache hit ratio, 14-day ASCII sparkline, under 3000 characters; posted daily 06:00 UTC to the pinned `Burn report` issue.
* Reconciliation job compares with CSV in `ops/metering/console/` on a 48 h window; drift above 10 percent flags the report.

**Interface contract**

* Provides: `recordUsage(event)`, `spent({ scope })`, `remaining({ scope })`, `liveTotal(sessionId)` (running sum from streamed messages), Zod `UsageEvent`, the `budgets` table, `pnpm burn [--json]`.
* Consumers: PAP-111 pre-flight and in-flight checks, PAP-113 (`spentTodayUsd`, `dailyCapUsd`), PAP-110 (`cost_usd` per eval run), {{pm-linear/weekly-reaudit}} (spend per project).
* Requires: PAP-96 sessions table and SDK stream; PAP-107 spool format for hook sessions.

**Definition of done**

* Recomputed price matches SDK cost within 1 percent on 20 recorded sessions.
* Three daily reports posted in staging; screenshots at 375 px and 1280 px.
* `pnpm burn` output for current spend pasted here.
* One reconciliation run against a real Console export with drift printed.
* Docs page; changelog entry; Linear comment with screenshots.

**Test plan**

* Unit: price recomputation, area classification for every Type label, share arithmetic when `totalUsd` changes mid-programme (history kept), partial-session summation.
* Integration: 20 recorded SDK result messages through `recordUsage` into SQLite; idempotent re-ingest.
* e2e: staging report job for three days.
* Visual: report in Linear mobile at 375 px shows the sparkline without wrapping.

**Demo**

Run `pnpm burn` and read the area table against the 12/45/30/8/5 shares, then `pnpm burn:report --post` and open the pinned issue on a phone. One minute.

**Edge cases**

* Session crashes before `result`: sum streamed `usage`, mark `partial`.
* Three attempts on one issue: costs aggregate; report shows attempt count.
* Sonnet sub-agent inside a Fable session: SDK cost already includes it; hook sessions price by `model`.
* Negative or missing `total_cost_usd`: recompute and flag.
* Console export lags: reconcile on the 48 h window only.

**Dependencies**

Blocked by PAP-96. Blocks PAP-111. Soft: PAP-107.

**Agent**

Built by Atlas (lead); reviewed by Sentinel (Code Reviewer).

**Size**

M
"""

DESCRIPTIONS["PAP-99"] = """**Goal**

Let twenty sessions run at once without merge storms or blocked work: the orchestrator picks issues by dependency readiness, keeps sessions that touch the same files apart, caps parallelism globally, per repo and per character, and never starves a project.

**Scope**

* In: `src/scheduler/` pure functions, `Files:` glob parsing through PAP-93, learned paths from PRs, limits in config, priority scoring, cycle detection, fairness bonus.
* Out: claiming and launching (PAP-96), budget checks (PAP-111 runs before `scheduler.next()` returns), release tagging (PAP-52).

**Spec**

* Eligibility: every `blockedBy` relation is `Done`, `Canceled` or `Duplicate` (the last two comment once), or the blocker is `In Review` and the issue carries `can-start-on-review`.
* Conflicts: two issues conflict when their `Files:` globs intersect on the same repo (`picomatch` on a shared sample path set plus literal prefix comparison); missing globs mean unknown, which conflicts with nothing but is shown as a risk in `/status`; `**` conflicts with everything and runs alone.
* Learned paths: at PR open, `git diff --name-only origin/main...HEAD` stored in `issue_paths(issue_id, path)`; a new issue whose globs miss a learned path of a sibling gets a warning comment.
* Limits: `maxParallel` 12, `perRepo` 6, `perCharacter` 3 (Sentinel 6), optional `perProject`. `Urgent` bypasses `perProject` but not `maxParallel`.
* Score: `priorityWeight + ageHours * 0.1 + unblocksCount * 2 + phaseWeight + starvationBonus`; `starvationBonus` when a project has been eligible six hours without a session.
* Cycle detection on every poll; a cycle is reported once to `Needs Justin` deduped by cycle hash.

**Interface contract**

* Provides: `buildGraph(issues, relations): Graph`, `eligible(graph, running, config): Issue[]`, `score(issue, graph): number`, `conflicts(globsA, globsB): boolean`, `next(): Issue | null`; `/status.scheduler` block `{ eligible: [{ issue, score, reasons[] }], blocked: [{ issue, waitingOn[] }], risks[] }`.
* Consumers: PAP-96 loop, PAP-113 (blocked reasons on cards), {{pm-linear/weekly-reaudit}} (cycle and drift detection reuses `buildGraph`).
* Requires: PAP-93 `parseFilesGlobs`; relations and states from the Linear client in PAP-96; config schema extension.

**Definition of done**

* Property tests: `eligible()` never returns two conflicting issues on one repo, never an issue with an open blocker, never more than the caps.
* Simulation over the live plan graph (from `linear-snapshot.json`, 206 issues, 284 edges) at `maxParallel` 12 completes with zero conflicts; makespan table attached.
* Live soak: eight issues in parallel on staging for four hours, manual-rebase rate under 10 percent.
* `/status` screenshot at 1280 px with eligibility reasons; README section; changelog; Linear comment with results.

**Test plan**

* Unit: glob intersection cases (`packages/ui/**` vs `packages/ui/button.tsx`, disjoint, `**`), scoring, caps per dimension, cycle reporting once.
* Property (`fast-check`): random DAGs and glob sets, invariants above.
* Simulation test committed as a Vitest snapshot of makespan and order.
* e2e: soak report generated by `pnpm scheduler:soak-report`.
* Visual: `/status` page at 1280 px only.

**Demo**

Run `pnpm scheduler:simulate --snapshot round2/linear-snapshot.json --parallel 12` and watch the Gantt-like text output show waves of non-conflicting issues; then open `/status` and read why one issue is blocked. One minute.

**Edge cases**

* Relations changed mid-run: never kill a session; note it in the status comment.
* Submodule shared between repos: globs are repo-scoped; documented.
* Scheduler throws: fall back to FIFO, log loudly.
* Blocker `Canceled`: eligible, one explanatory comment.
* Character over budget (PAP-111): excluded from eligibility with reason `budget-hold`.

**Dependencies**

Blocked by PAP-96. Uses PAP-93 parsing. Soft: PAP-111.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel.

**Size**

M
"""

DESCRIPTIONS["PAP-100"] = """**Goal**

Give PaperOS its own project-management tables shaped like Linear's model so issues, projects, cycles, milestones, comments and labels can be mirrored one-to-one today and owned outright after cutover. Output is a Drizzle schema in its own package, oRPC procedures, three page specs and a mapping document, not UI.

**Scope**

* In: `packages/pm` (schema, migrations, seeds, procedures, mapping doc); page specs `specs/pm/issue-detail.spec.yaml`, `issue-list.spec.yaml`, `project.spec.yaml`; `docs/pm/data-model.md`.
* Out: sync (PAP-101), views (PAP-102), anything in `packages/core` (the audit moved PM out of core; `packages/core` stays owned by app-shell).

**Spec**

* Tables: `pm_team`, `pm_workflow_state`, `pm_project`, `pm_milestone`, `pm_cycle`, `pm_issue`, `pm_issue_relation`, `pm_label`, `pm_issue_label`, `pm_comment`, `pm_attachment`, `pm_external_ref`, each with `tenant_id`, uuid v7 `id`, `created_at`, `updated_at`, `archived_at`, `created_by` (principal id from PAP-60).
* `pm_issue`: `identifier` unique per `(tenant_id, team_id)`, `number`, `title`, `description`, `priority 0-4`, `estimate`, `state_id`, `assignee_id`, `parent_id`, `project_id`, `cycle_id`, `milestone_id`, `due_date`, `sort_order`, `started_at`, `completed_at`, `canceled_at`, `extra jsonb`.
* `pm_external_ref(entity_type, entity_id, system, external_id, external_url, synced_at, external_updated_at)` unique on `(system, external_id)`.
* Invariants: `parent_id <> id`; relation type enum `blocks | related | duplicate`; trigger sets `completed_at` on completed state; milestone must belong to the issue's project.
* Procedures `pm.issues.{list,get,create,update,archive}`, `pm.projects.*`, `pm.comments.*` via the oRPC layer (PAP-35), cursor pagination, filters state, assignee, label, project.
* Seeds: team PAP, nine states, label groups and three sample issues.

**Interface contract**

* Provides: `@paperos/pm` exporting the Drizzle tables, Zod `PmIssue`, `PmProject`, `PmComment`, the `pm.*` router, and `mapping.ts` (Linear field to column table shared with PAP-101).
* Consumers: PAP-101 upserts through `pm_external_ref`; PAP-102 reads via the views engine data source `pm_issue`; PAP-204 (ClickUp import) writes `pm_issue` rows; PAP-113 links character badges to `assignee_id`.
* Requires: PAP-33 core entities, PAP-34 RLS helpers, PAP-35 procedures, PAP-114 spec schema (draft allowed with `status: draft`).

**Definition of done**

* Migration applies and rolls back on fresh Postgres 17; `pnpm db:check` passes.
* Cross-tenant RLS test proves tenant A issues invisible to B.
* Procedure tests for create, update, archive, list with filters and pagination.
* Three page specs validate (PAP-115).
* `docs/pm/data-model.md` with ER diagram; changelog; Linear comment with the mapping table.

**Test plan**

* Unit: Zod schemas, identifier derivation, mapping table completeness against Linear's `Issue` type fields.
* Integration (PGlite and Postgres): migrations, triggers, RLS harness from PAP-34, procedures with `callAs` from PAP-35.
* e2e: none; no UI in this issue.
* Visual: ER diagram renders in the docs page at 1280 px.

**Demo**

Run `pnpm db:migrate && pnpm db:seed pm`, then `pnpm api call pm.issues.list --as staff` and see the three seeded issues with states and labels; call as another tenant and get an empty list. One minute.

**Edge cases**

* Team key renamed: old identifiers kept as aliases in `pm_external_ref`.
* Issue moved between projects: milestone nulled by trigger if it belongs elsewhere.
* Label deleted while in use: soft delete, history retained.
* Description over 200 KB: API rejects with a clear error.
* Cycles disabled: `cycle_id` nullable, procedures return empty.

**Dependencies**

Blocked by PAP-33. Soft: PAP-34, PAP-35, PAP-114. Blocks PAP-101, PAP-102, PAP-204.

**Agent**

Built by Forge (Schema Wright sub-agent); reviewed by Sentinel and Quill (docs).

**Size**

M
"""

DESCRIPTIONS["PAP-101"] = """**Goal**

Keep the PaperOS PM tables and Linear team PAP in step both ways with one rule that removes ambiguity until cutover: when both sides changed, Linear wins. Edits on PaperOS boards reach Linear within seconds and everything the orchestrator does in Linear appears in PaperOS. Umbrella for three children.

**Scope**

* Children (build in order):
  * {{pm-linear/linear-sync/inbound}}: backfill and inbound webhook upsert.
  * {{pm-linear/linear-sync/outbound}}: outbox, outbound worker and loop prevention.
  * {{pm-linear/linear-sync/conflicts}}: conflict rule, sync status page and runbook.
* Out: cutover tooling (flipping the winner), ClickUp import (PAP-204), Linear fields PaperOS lacks (stored in `extra`).

**Spec**

* Package `packages/pm-sync` running as a worker in the API process; entities: teams, states, projects, milestones, cycles, issues, relations, labels, comments, attachments; users mapped to principals by email, agents by bot account.
* Field mapping in `@paperos/pm` `mapping.ts`; unknown fields to `pm_issue.extra`.
* Every sync write carries `created_by` = the sync principal (PAP-60) and `source: "linear"` so no outbox row is enqueued.
* Rate limiting respects `X-RateLimit-Requests-Remaining`, batches label updates with aliases and pauses at 10 percent remaining; retry 1 s to 10 min, eight attempts, then `dead`.

**Interface contract**

* Provides: `pm.sync.status()` returning `{ lagSeconds, outboxDepth, deadCount, conflicts24h, lastWebhookAt }`, `pm.sync.backfill()`, `pm.sync.retry(id)`; tables `pm_outbox`, `pm_sync_cursor`, `pm_sync_conflict`; event `pm.sync.conflict` for PAP-136.
* Consumers: PAP-102 (status banner and "changed in Linear" toast), PAP-204 (writes flow out through the same outbox), PAP-113 (assignee mirrors).
* Requires: PAP-100 tables and mapping, PAP-97 verified Linear receiver and event bus, PAP-60 sync principal, PAP-43 jobs queue for the worker.

**Definition of done**

* All three children Done.
* Umbrella round trip: create in PaperOS appears in Linear with state, labels and assignee; edit in Linear appears in PaperOS; simultaneous edit resolves with Linear winning and one conflict row.
* Backfill of PAP completes under five minutes with matching counts for issues, comments and labels printed in the comment.
* Loop test: 1000 synthetic edits produce no echo writes.
* Runbook `docs/pm/linear-sync.md`; changelog; Linear comment with results.

**Test plan**

* Integration suite `packages/pm-sync/test/roundtrip.test.ts` against `nock` fixtures recorded from PAP, covering the three children together.
* e2e on staging against the real PAP team using a `sync-test` label namespace, cleaned up afterwards.
* Visual: sync status page at 375, 768 and 1280 px (child 3).

**Demo**

Drag a card on the PaperOS board (PAP-102) or call `pm.issues.update`, open the Linear issue and watch the state change within ten seconds; edit the title in Linear and see it in PaperOS. Then run `pm.sync.status` and read lag zero. Two minutes.

**Edge cases**

* Webhook arrives before our own outbox write commits: match by the `idempotencyKey` embedded in the Linear description footer.
* Linear user without a principal: placeholder external principal, assignee kept.
* Permanent deletion in Linear: keep the row, set `archived_at` and `deleted_externally`.
* Webhook outage for hours: backfill by `updatedAt > cursor` on reconnect.
* Cycles disabled locally: store, do not surface.

**Dependencies**

Blocked by PAP-97, PAP-100. Soft: PAP-60, PAP-43.

**Agent**

Built by Nova (lead) with Forge (Schema Wright) for the outbox; reviewed by Sentinel.

**Size**

L (umbrella; children M, M, S)
"""

DESCRIPTIONS["PAP-102"] = """**Goal**

Show project management inside the product: the PM entities rendered as a kanban board grouped by workflow state, a filterable list and a timeline of projects and milestones, all as configurations of the views engine rather than bespoke components. Dragging a card changes state and, through sync, moves the Linear issue.

**Scope**

* In: routes `/pm`, `/pm/board`, `/pm/list`, `/pm/timeline`, `/pm/issues/:identifier` with page specs; view records seeded; cell renderers for priority, state and character badge; keyboard-only drag; character heartbeat badge.
* Out: the sync itself (PAP-101), custom views UI beyond saved filters (PAP-166), comments on issues (PAP-131).

**Spec**

* Board: `tables/kanban-view` (PAP-167) with data source `pm_issue`, group by `state_id` ordered by `pm_workflow_state.position`, optional swimlanes by project or assignee, card fields identifier, title, priority, assignee, labels, estimate; WIP limit 5 on `In Review` and `Needs Justin` mirroring PAP-94; drag calls `pm.issues.update`.
* List: `tables/grid-view` columns identifier, title, state, priority, assignee, labels, project, updated; inline edit for state, priority, assignee; saved views "My issues", "Ready for Claude", "Needs Justin", "Blocked".
* Timeline: `tables/calendar-timeline-gantt` with projects as rows, milestones as markers, an "Unscheduled" lane.
* Character badge reads `SessionStatus` from {{agents/session-observability}}; `working` when `lastHeartbeat` is under 15 minutes old, else `stale`.
* Responsive: under 768 px the board is a single-column state picker with swipe; the list hides secondary columns; the timeline becomes a vertical milestone list. Optimistic updates through PAP-36 with rollback toast.

**Interface contract**

* Provides: view seeds `pnpm db:seed pm-views`, cell renderers `pm.priority`, `pm.state`, `pm.character` registered in the views cell registry (PAP-71), page specs consumed by PAP-122 conformance tests, route `/pm/issues/:identifier` used by PAP-113 drawer links.
* Consumers: PAP-113 (deep links), PAP-136 (notification links), PAP-204 (import preview reuses the list).
* Requires: PAP-100 tables and procedures, PAP-167 kanban, PAP-165 grid, PAP-166 filter UI, PAP-155 drag-drop keyboard alternative, PAP-101 for live Linear reflection (works locally without it), {{agents/session-observability}} for the badge.

**Definition of done**

* Three page specs validate; conformance tests pass.
* Screenshots of board, list, timeline and detail at 320, 375, 768, 1024, 1280, 1920 and 2560 px in light and dark attached.
* Drag on staging changes the Linear issue within 10 s (recording).
* axe passes on all four pages; keyboard-only drag works.
* Pages demo with seeded data; changelog; Linear comment with demo and screenshots.

**Test plan**

* Unit: cell renderers, WIP-limit guard, badge staleness computation with a fake clock.
* Integration: `pm.issues.update` optimistic path and rollback with a failing mock.
* e2e (Playwright): filter, sort, drag with mouse and keyboard, offline drag queued then applied on reconnect, at 375 and 1280 px.
* Visual: seven-width matrix in both themes through gate 3 (PAP-82); the 768 px breakpoint switch is asserted explicitly.

**Demo**

Open `/pm/board` on a phone-width window, swipe to `Ready for Claude`, drag a card to `In Progress`, then open the same issue in Linear and see the state changed. Ninety seconds.

**Edge cases**

* 2000 issues in one column: virtualised; counts computed server-side.
* Drag into a full `Needs Justin`: blocked with explanation.
* Sync conflict after drag: card snaps back with "changed in Linear" toast.
* No permission to change state: handle disabled with tooltip.
* Orchestrator status unreachable: badge shows "unknown", not spinner.

**Dependencies**

Blocked by PAP-100, PAP-167, {{agents/session-observability}}. Soft: PAP-101, PAP-155.

**Agent**

Built by Nova (Views Engineer sub-agent); reviewed by Sentinel (Visual Inspector).

**Size**

M
"""
