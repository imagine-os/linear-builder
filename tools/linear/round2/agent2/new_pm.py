"""New issues for pm-linear: 3 gap issues and 6 children (PAP-96, PAP-101)."""
P = "pm-linear"
GAPS = []
CHILDREN = {}

GAPS.append({
"key": "pm-linear/workspace-reconcile",
"title": "Reconcile the live Linear workspace with the round-1 import: Character label group, `Files:` scope lines, estimates vs Size, Surface multi-label rule; align PAP-91 and PAP-93 to it",
"phase": "P0", "type": "Infra", "priority": 1, "surfaces": ["Agent"],
"milestone": "Linear configured for the pipeline", "state": "Ready for Claude",
"blockedBy": [], "blocks": ["PAP-93"],
"description": """**Goal**

Make the plan's Linear rules match the Linear that exists. The round-1 import kept `Todo`, created `Ready for Claude` beside it, left surface labels ungrouped, created no `Character` group and left estimation off. PAP-91 and PAP-93 were written for a different configuration; a validator built from them would bounce all 206 issues. This issue produces the reconciliation report, decides each mismatch explicitly and records the decisions where PAP-91 and PAP-93 read them.

**Scope**

* In: `ops/linear/reconcile.ts` (`--check` and `--apply`) in the orchestrator repo, `docs/pm/workspace-decisions.md`, the `Files:` line convention, the Size-in-description rule, the Surface multi-label rule, a bulk comment-free annotation pass that adds `Files:` lines to Build issues whose Scope names paths.
* Out: creating the `Character` group (PAP-91 does it from the decisions here), the validator code (PAP-93), any state changes or deletions.

**Spec**

* Decisions recorded as a table `(topic, live state, decision, consumer)`: `Todo` stays as human parking, never polled; surfaces stay ungrouped and one or more are required; `Character/*` becomes a group with nine children and is optional until 2026-09-22; Size lives in the description and `issueEstimationType` stays `notUsed`; the empty `Surface` group label stays; PAP-6..PAP-12 stay `Duplicate` and are excluded from every audit query.
* `--check` reads `round2/linear-snapshot.json` (or a fresh snapshot with `--live`, one paginated query per 100 issues) and prints per-issue findings: missing sections, Size not parseable, no surface label, Build issue with path mentions but no `Files:` line.
* `--apply` limits itself to `issueUpdate({ description })` that appends a `Files:` line inside Scope for Build issues where globs can be derived from backticked paths (for example `packages/ui/**`); it never touches labels, states, titles or issues outside PAP-13..PAP-218 and round-2 creations; dry-run diff first; batched with aliases, 300 ms apart.
* Output `reconcile-report.md` posted as a comment on this issue and stored in `docs/pm/`.

**Interface contract**

* Provides: `docs/pm/workspace-decisions.md` (the single source PAP-91 and PAP-93 cite), `parseSizeFromDescription(md): "S" | "M" | "L" | null`, `deriveFilesGlobs(scopeMd): string[]`, `reconcile-report.md`.
* Consumers: PAP-91 (what to create and what to leave), PAP-93 (metadata rules), PAP-99 (`Files:` lines), {{pm-linear/weekly-reaudit}} (reuses the check as its structural pass).
* Requires: the snapshot file or Linear read access; nothing else.

**Definition of done**

* Decisions document merged and linked from PAP-91 and PAP-93 (comments on both).
* `--check` report on the live team attached: counts of issues per finding.
* `--apply` adds `Files:` lines to every Build issue where derivation succeeded; a second `--check` shows the remaining ones with a reason.
* Zero labels, states or titles changed (asserted by a post-run diff of the snapshot fields).
* Changelog entry; Linear comment with the report.

**Test plan**

* Unit: `parseSizeFromDescription` on all 206 descriptions from the snapshot (expect 206 parsed); `deriveFilesGlobs` on ten fixtures including specs-only issues (expect none).
* Integration: `--apply --dry-run` against the snapshot plans only description updates; mutation count equals the report count.
* Live: `--check` before and after `--apply`.
* No UI.

**Demo**

Run `pnpm linear:reconcile --check` and read the finding table, then open `docs/pm/workspace-decisions.md` and follow the `Todo` row to the PAP-91 sentence that now says "keep". One minute.

**Edge cases**

* Description edited by a human since the snapshot: `--live` refetch before apply; skip if `updatedAt` moved.
* Scope names files without backticks: derivation fails; listed with reason `no-derivable-globs`.
* Rate limit: sleep 60 s and retry.
* Issue in `Duplicate`: skipped.
* Two globs overlap: deduped to the broader one.

**Dependencies**

None (`readyNow`). Blocks PAP-93. Informs PAP-91.

**Agent**

Built by Atlas (Decomposer sub-agent); reviewed by Sentinel.

**Size**

S
"""})

GAPS.append({
"key": "pm-linear/weekly-reaudit",
"title": "Run a weekly plan re-audit: snapshot Linear, detect dependency drift, cycles, stale In Progress sessions, issues without specs; post the report to Linear",
"phase": "P1", "type": "Review", "priority": 2, "surfaces": ["Agent", "Staff"],
"milestone": "Orchestrator claims and ships issues", "state": "Backlog",
"blockedBy": ["PAP-93", "PAP-105", "PAP-99"], "blocks": [],
"description": """**Goal**

Keep the plan honest while twenty sessions change it daily: every Monday an Atlas skill snapshots Linear, checks structure (cycles, phase inversions, milestone date inversions, orphan issues, missing relations stated in prose), health (stale `In Progress` sessions, issues bounced three times, budget vs plan) and quality (issues failing the contract, L issues that should split), then posts a Markdown report and files fixes as Backlog issues.

**Scope**

* In: skill `.claude/skills/plan-audit/` (SKILL.md plus `scripts/snapshot.ts`, `scripts/checks.ts`, `scripts/report.ts`), scheduled workflow `.github/workflows/plan-audit.yml` (Monday 05:00 UTC and `workflow_dispatch`), the pinned `Plan audit` issue, auto-filed fix issues capped at five per run.
* Out: fixing structure automatically (only proposes), the one-off audit this round produced, per-PR review (quality project).

**Spec**

* Snapshot: same query shape as `round2/snapshot.py`, stored under `docs/pm/audits/YYYY-MM-DD/snapshot.json` (issues, relations, projects, milestones, states, labels).
* Checks reuse `buildGraph` from PAP-99 and `validateIssue` from PAP-93: `CYCLE`, `PHASE_INVERSION` (P0 blocked by P1/P2), `MILESTONE_INVERSION`, `ORPHAN` (no project or milestone), `PROSE_DEP` (description names `PAP-n` as hard dependency without a relation), `STALE_SESSION` (`In Progress` with no heartbeat for 2 hours per {{agents/session-observability}}), `BOUNCED` (three `retry-*` labels), `CONTRACT_FAIL`, `SPLIT_CANDIDATE` (Size L and blocks three or more), `BUDGET_DRIFT` (area spend off plan share by 10 points, from PAP-98).
* Report `docs/pm/audits/YYYY-MM-DD/report.md`: counts, deltas since last week, top ten findings with links, under 4000 characters in the Linear comment with the full report linked.
* Fixes: up to five Backlog issues per run in contract format (Type Review, Character Atlas), deduped by finding hash; anything needing Justin goes as one decision card (PAP-94).

**Interface contract**

* Provides: `docs/pm/audits/<date>/{snapshot.json, report.md, findings.json}`, `Finding = { code, issues[], severity, suggestion }`, the `plan-audit` skill id in `skills.json`.
* Consumers: Justin (report), PAP-113 (finding badges optional), PAP-112 handbook links the latest report, PAP-29 drill reads `BUDGET_DRIFT`.
* Requires: PAP-93 validator, PAP-99 graph, PAP-105 skill format and `linear-update`, PAP-98 spend, {{agents/session-observability}} heartbeats, Linear read access.

**Definition of done**

* Skill lint passes; workflow runs on schedule and on dispatch.
* First report posted covers every check with real numbers and finds the known-good state clean after round 2 (zero cycles, zero inversions).
* A seeded cycle on a `rehearsal` pair of issues is detected and a fix issue filed, then the pair is cleaned up.
* Docs section in the playbook; changelog; Linear comment with the report.

**Test plan**

* Unit: each check against the round-2 snapshot fixture with injected faults (cycle, inversion, prose dep, stale session).
* Integration: report renderer snapshot; dedupe of fix issues across two runs.
* e2e: dispatch run on staging with the rehearsal cycle.
* Visual: report comment at 375 px in the Linear mobile app.

**Demo**

Trigger `workflow_dispatch`, wait for the comment on the `Plan audit` issue, open the linked report and click one finding to its issue. Two minutes.

**Edge cases**

* Snapshot fails midway (rate limit): resume from cursor; partial report labelled `partial`.
* More than five fixes: file five, list the rest.
* Finding already has an open fix issue: comment on it instead of a new one.
* Justin marks a finding `wontfix` via reply grammar: suppressed for four weeks.
* PAP-6..PAP-12 strays: excluded.

**Dependencies**

Blocked by PAP-93, PAP-105, PAP-99. Soft: PAP-98, {{agents/session-observability}}.

**Agent**

Built by Atlas (lead); reviewed by Sentinel.

**Size**

M
"""})

GAPS.append({
"key": "pm-linear/inbound-triage",
"title": "Build inbound triage: convert Justin's freeform issues and comments into contract-valid issues via the Decomposer sub-agent, wired to the Triage view",
"phase": "P1", "type": "Build", "priority": 2, "surfaces": ["Staff", "Agent"],
"milestone": "Orchestrator claims and ships issues", "state": "Backlog",
"blockedBy": ["PAP-93", "PAP-97", "PAP-118"], "blocks": [],
"description": """**Goal**

The contract (PAP-93) bounces non-conforming issues, but the only human should be able to type one line and get a buildable issue. When Justin creates an issue in `Todo` or `Backlog` without contract sections, or comments `triage:` on any issue, the Decomposer sub-agent drafts Goal, Scope, Spec, Definition of done, Edge cases, Dependencies, Agent and Size, links or requests a spec, asks at most one question and leaves the issue for him to move to `Ready for Claude`.

**Scope**

* In: webhook handler on `Issue.create` and `Comment.create` (human author, team PAP), the triage session prompt, the `triaged` label, a decision-free `ask:` flow, `docs/pm/triage.md`, and a saved filter definition documented for the existing `Triage` view (the view itself is not modified).
* Out: acting on the issue, moving it to `Ready for Claude`, changing states, creating projects.

**Spec**

* Trigger: issue created by a human with fewer than three contract sections, or a human comment whose first line is `triage:`; ignore agent authors and issues already labelled `triaged`.
* Session: Atlas (Decomposer) read-only plan mode, `maxTurns` 12, cost cap $4 (PAP-111); inputs are the issue text, the plan blueprint document, `linear-workspace.json`, the project list with descriptions and the twenty most similar issue titles (substring and label match).
* Output: `issueUpdate` with the full contract description (original text preserved under `Original request`), labels Phase, Type and surfaces inferred with confidence noted, a project and milestone proposal, `parentId` when it is clearly a sub-task, and one comment: either "Drafted, move to Ready for Claude when happy" or a single `ask:` question rendered as a PAP-94 card without occupying a `Needs Justin` slot.
* Spec requirement: if Type is Build and a route is named, call PAP-118 `author-spec open-issue` mode to draft the spec branch or add a `needs-spec` line.
* Every drafted issue passes `validateIssue` before the update is sent.

**Interface contract**

* Provides: handler registered through PAP-97 `registerWebhookHandler`, `triage(issueId): TriageResult = { ok, sectionsAdded[], labels[], project?, question? }`, label `triaged`, the `triage:` comment grammar, view filter `label = triaged AND state in (Backlog, Todo)`.
* Consumers: Justin; {{pm-linear/weekly-reaudit}} counts `triaged` issues waiting; PAP-112 handbook documents `triage:`.
* Requires: PAP-93 `validateIssue`, PAP-97 webhooks, PAP-118 scripts, PAP-104 Decomposer definition, PAP-111 cap.

**Definition of done**

* Five real one-line issues from Justin's style ("we need dark mode on the invoice page") triaged in staging; four of five pass the contract without edits; results table attached.
* Original text preserved in every case.
* `ask:` flow demonstrated once with a reply that completes the draft.
* No state changes performed by the handler (asserted in tests); docs; changelog; Linear comment.

**Test plan**

* Unit: trigger detection (sections count, author kind, grammar), label inference from fixture titles, `Original request` preservation, validator gate.
* Integration: recorded webhooks through the handler with a mocked SDK session returning a fixture draft.
* e2e: five staging issues.
* Visual: the drafted issue in Linear mobile at 375 px.

**Demo**

Create an issue titled "customers should get an SMS when an invoice is overdue" with no body; within two minutes it has all sections, labels, a proposed project and one comment; move it to `Ready for Claude` and watch PAP-93 stay silent. Two minutes.

**Edge cases**

* Request spans two projects: draft the smaller one and propose the second as a child list.
* Duplicate of an existing issue: comment with the match and label `possible-duplicate`, still draft.
* Justin edits during triage: session result is discarded if `updatedAt` moved; retry once.
* Cost cap hit: partial draft with a `TODO` marker, never silence.
* Non-English request: draft in English, keep the original.

**Dependencies**

Blocked by PAP-93, PAP-97, PAP-118. Uses PAP-111, PAP-104.

**Agent**

Built by Atlas (Decomposer sub-agent); reviewed by Quill for prose and Sentinel.

**Size**

M
"""})

CHILDREN["PAP-96"] = [
{
"key": "pm-linear/orchestrator/claims", "title": "Orchestrator: Linear polling, atomic claim and state transitions", "type": "Build", "size": "M",
"blockedBy": [], "blocks": ["pm-linear/orchestrator/sessions", "pm-linear/orchestrator/deploy"],
"description": """**Goal**

Build the half of the orchestrator that talks to Linear: the poll loop that reads `Ready for Claude`, the atomic claim that assigns and moves an issue, the state transitions to `In Review`, `Ready for Claude` (retry) and `Needs Justin`, the `linearComment()` helper and the database tables everything else records into.

**Scope**

* In: repo skeleton `imagine-os/paperos-orchestrator` (Node 22, pnpm, Biome, Vitest, Drizzle), `src/linear/`, `src/db/` with migrations, `src/loop.ts` with a pluggable `pickNext()` (FIFO by priority then age until PAP-99), `linearComment()`, config loading.
* Out: worktrees and sessions ({{pm-linear/orchestrator/sessions}}), HTTP and deployment ({{pm-linear/orchestrator/deploy}}), webhooks (PAP-97).

**Spec**

* Poll every `pollIntervalMs` (30 s): `issues(filter: { team: { key: { eq: "PAP" } }, state: { name: { eq: "Ready for Claude" } }, assignee: { null: true } })` ordered by priority, then `createdAt`; also callable by `loop.wake()` from webhooks.
* Claim: insert `claims(issue_id, session_id, updated_at_seen)` inside `SELECT ... FOR UPDATE SKIP LOCKED`; then `issueUpdate({ assigneeId: botUser(character), stateId: IN_PROGRESS })`; re-read and compare `updatedAt` to `updated_at_seen`; on mismatch release the claim.
* Transitions: `toInReview(issue, prUrl)` adds the attachment; `retry(issue, n)` sets `Ready for Claude` and label `retry-<n>` (max two); `escalate(issue, reason)` sets `Needs Justin` with a PAP-94 card.
* Tables: `sessions`, `claims`, `events`; SQLite in dev, Postgres schema `orchestrator` in production; ids from `linear-workspace.json` (PAP-91).
* `linearComment(issueId, body, footer)` appends the PAP-92 footer, dedupes on `(issue_id, sha256(body))` in `comments_sent`, retries on `RATELIMITED` after 60 s.

**Interface contract**

* Provides: `claimNext(character?): Claim | null`, `release(claim)`, `toInReview`, `retry`, `escalate`, `linearComment`, `linear.ids` (typed `WorkspaceIds`), tables above, `events.emit("issue.claimed" | "issue.released")`.
* Consumers: {{pm-linear/orchestrator/sessions}} (claims to launch), PAP-97 (`linearComment`, events), PAP-99 (replaces `pickNext`), PAP-108 (assignee switch), PAP-111 (`release` on hold).
* Requires: PAP-91 ids, PAP-92 footer schema, bot user ids (single default bot until PAP-48).

**Definition of done**

* Claim atomicity test: 20 concurrent `claimNext()` on one issue yields one winner.
* `updatedAt` guard test releases the claim when the issue moved.
* Transition tests against a mocked SDK; comment dedupe test; migrations apply on SQLite and Postgres.
* Live: an issue moved to `Ready for Claude` on the team is claimed within one poll and shows the bot assignee and `In Progress`; recording.
* Changelog; Linear comment.

**Test plan**

* Unit: query builder, priority ordering, footer append, dedupe hash, retry counter cap.
* Integration: Postgres via testcontainers for `SKIP LOCKED`; mocked SDK for transitions.
* e2e: live claim on a `rehearsal` issue, then release.
* No UI.

**Demo**

Run `pnpm dev`, move a rehearsal issue to `Ready for Claude`, watch the log print `claimed PAP-n` and Linear show `In Progress` with the bot assignee; stop the process and the claim row is released on restart. One minute.

**Edge cases**

* Linear down: pause claiming, exponential backoff, no crash.
* Issue reassigned by a human during claim: guard fails, skip.
* Two replicas: `SKIP LOCKED` ensures one winner.
* Comment body identical to a previous one: skipped silently, logged.
* Bot user missing: fall back to the default bot and warn.

**Dependencies**

Blocked by PAP-91, PAP-92 (through the parent). Blocks the two sibling children.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel.

**Size**

M
"""},
{
"key": "pm-linear/orchestrator/sessions", "title": "Orchestrator: worktree lifecycle and Claude session launch", "type": "Build", "size": "M",
"blockedBy": ["pm-linear/orchestrator/claims"], "blocks": ["pm-linear/orchestrator/deploy"],
"description": """**Goal**

Turn a claim into a running Claude Code session: create or reuse the git worktree, render the prompt, launch through the Agent SDK with the character's bundle, stream messages to storage, capture the footer and detect the PR so the parent can move the issue to `In Review`.

**Scope**

* In: `src/git/worktree.ts`, `src/session/{prompt,launch,stream}.ts`, prompt template `prompts/issue.md`, PR detection, retry handoff of the previous footer.
* Out: claiming ({{pm-linear/orchestrator/claims}}), HTTP and deploy ({{pm-linear/orchestrator/deploy}}), sandboxing ({{agents/runtime-sandbox}}, which wraps `launch`).

**Spec**

* Worktree: `git -C /srv/repos/<repo> fetch origin && git worktree add /srv/worktrees/<PAP-key> -b <branch> origin/main` with the PAP-46 branch name; `pnpm i --frozen-lockfile`; reuse when branch matches; dirty crash leftovers stashed to `crash/<timestamp>`.
* Prompt: issue body, playbook pointer, character, branch, memory block (PAP-109 when available), previous footer on retry, required footer instruction.
* Launch: `query()` from `@anthropic-ai/claude-agent-sdk` with `cwd`, `permissionMode`, `allowedTools`, `disallowedTools`, `mcpServers` from the PAP-106 bundle (default allowlist until it lands), `agents` from `.claude/agents`, `maxTurns` from PAP-111 (default 200), `model` from `roster.json`, `settingSources: ["project"]`, abort controller exposed.
* Stream: every message to `sessions/<id>.ndjson` and `events`; `result` forwarded to PAP-98; last assistant text parsed for the footer and stored in `sessions.footer_json`.
* Completion: `gh pr list --head <branch>` and Forgejo API; PR found calls `toInReview`; none found calls `retry` with the footer in the next prompt.

**Interface contract**

* Provides: `ensureWorktree(repo, key): Worktree`, `renderPrompt(claim, ctx): string`, `launchSession(claim, opts): { sessionId, abort, done: Promise<Footer> }`, `detectPr(branch): PrRef | null`, events `session.started`, `session.message`, `session.ended`.
* Consumers: PAP-98 (`result`), PAP-107 (NDJSON handoff), PAP-111 (`abort`, wrap-up injection through `opts.onProgress`), PAP-110 eval runner reuses `launchSession` with a throwaway worktree, {{agents/session-observability}} heartbeats from `session.message`.
* Requires: sibling claims module, PAP-46 branch policy, PAP-92 footer, PAP-104 roster, PAP-106 bundles (soft).

**Definition of done**

* Worktree tests on a temp repo: create, reuse, crash recovery, existing remote branch rebase.
* Prompt snapshot test; footer parsing test on three transcripts.
* Integration with a mocked SDK stream (assistant, tool_use, result).
* Live: one rehearsal issue produces a worktree, a session, a PR; footer stored; recording.
* Changelog; Linear comment.

**Test plan**

* Unit: branch naming, prompt rendering with and without memory, footer regex, PR mapping.
* Integration: temp git remote plus mocked SDK; `max_turns` stop marks `partial` and pushes `wip:`.
* e2e: live toy issue on staging.
* No UI.

**Demo**

With claims running, watch `/srv/worktrees/PAP-n` appear, tail `sessions/<id>.ndjson` to see tool calls stream, and see the PR open on the forge when the session ends. Two minutes.

**Edge cases**

* `stop_reason: max_turns` or budget: commit `wip:`, push, footer `partial`.
* Refusal stop: record category, escalate, no retry.
* Worktree path exists but wrong branch: `-2` suffix.
* `pnpm i` fails (lockfile drift): comment and retry once after `git pull`.
* PR opened by the session under a different branch name: fallback to `Closes PAP-n` search.

**Dependencies**

Blocked by {{pm-linear/orchestrator/claims}}. Soft: PAP-106, PAP-109, {{agents/runtime-sandbox}}.

**Agent**

Built by Atlas (Dispatcher sub-agent); reviewed by Sentinel.

**Size**

M
"""},
{
"key": "pm-linear/orchestrator/deploy", "title": "Orchestrator: deployment on Coolify, `/status` endpoint and runbook", "type": "Infra", "size": "S",
"blockedBy": ["pm-linear/orchestrator/claims", "pm-linear/orchestrator/sessions", "PAP-25"], "blocks": [],
"description": """**Goal**

Run the orchestrator as a service: a Docker image deployed through Coolify on the VPS with the repos cloned, `/healthz` and `/status`, structured logs, graceful shutdown and restart semantics that never lose a claim, plus the runbook a human or Atlas follows to start, stop, drain and inspect.

**Scope**

* In: `Dockerfile`, Coolify service definition, `src/http.ts` (Hono) with `/healthz` and `/status`, pino logs, shutdown handling, `README.md` runbook, secrets wiring through sops (PAP-17 conventions).
* Out: webhooks routes (PAP-97 adds them to the same Hono app), sandbox containers ({{agents/runtime-sandbox}}), the org chart (PAP-113 reads `/status`).

**Spec**

* Image: Node 22 slim with git, gh CLI, pnpm; volumes `/srv/repos`, `/srv/worktrees`, `/srv/sessions`; env from Coolify secrets; non-root user.
* `/status` JSON: `{ version, uptime, slots: { max, used }, queueDepth, sessions: SessionStatus[], scheduler?, limits?, paused }` where `SessionStatus` is the {{agents/session-observability}} shape (interim fields `issue`, `character`, `state`, `startedAt`, `lastMessageAt` until it lands).
* Shutdown on SIGTERM: stop claiming, wait up to `drainSeconds` (default 600) for sessions, then mark remaining `interrupted`, release claims and exit; on start, `interrupted` sessions re-queue their issues with the last footer.
* `pnpm orchestrator drain | resume | inspect <sessionId>` CLI over the HTTP API with an admin token.
* Logs: JSON lines with `sessionId`, `issue`, `character`; log level from env.

**Interface contract**

* Provides: `GET /healthz`, `GET /status`, `POST /admin/drain`, `POST /admin/resume` (admin token), the Coolify service `paperos-orchestrator`, the runbook sections Start, Stop, Drain, Inspect, Rotate secrets, Recover from crash.
* Consumers: PAP-113 (`/status`), PAP-111 (`paused` flag and `/kill` mounted here), PAP-97 (mounts webhook routes), PAP-99 (`scheduler` block), Coolify health checks.
* Requires: PAP-25 VPS and Coolify, the two sibling children, PAP-17 secrets conventions.

**Definition of done**

* Coolify deploy green; `/healthz` returns 200; `/status` screenshot at 1280 px.
* Restart mid-session marks it `interrupted` and re-queues the issue (recording).
* Drain test: no new claims after `drain`, running session finishes, process exits 0.
* Runbook reviewed by Forge; changelog; Linear comment with screenshot and recording.

**Test plan**

* Unit: `/status` serializer snapshot; shutdown state machine with fake timers.
* Integration: container build and smoke run in CI (`docker run` then `curl /healthz`).
* e2e: staging restart and drain.
* Visual: `/status` JSON viewed at 1280 px only.

**Demo**

Open `/status` on staging, run `pnpm orchestrator drain`, watch `slots.used` fall to zero and `paused: true`, then `resume` and see claims restart. One minute.

**Edge cases**

* Volume missing on first boot: clone repos from config, log duration.
* Coolify health check during drain: `/healthz` stays 200 with `draining: true`.
* Two replicas by accident: claims stay safe (SKIP LOCKED); `/status` shows `replica` id.
* Disk full from worktrees: alert in logs; `pnpm orchestrator gc` removes worktrees of `Done` issues.
* Secrets rotated: restart picks new env; runbook step.

**Dependencies**

Blocked by {{pm-linear/orchestrator/claims}}, {{pm-linear/orchestrator/sessions}}, PAP-25.

**Agent**

Built by Forge (Ops Runner sub-agent); reviewed by Sentinel (Security Auditor).

**Size**

S
"""},
]

CHILDREN["PAP-101"] = [
{
"key": "pm-linear/linear-sync/inbound", "title": "Linear sync: backfill and inbound webhook upsert into pm_* tables", "type": "Build", "size": "M",
"blockedBy": [], "blocks": ["pm-linear/linear-sync/outbound", "pm-linear/linear-sync/conflicts"],
"description": """**Goal**

Bring Linear into PaperOS: a resumable backfill of team PAP and an incremental inbound path that upserts every webhook payload into the `pm_*` tables through `pm_external_ref`, so PaperOS always has a faithful read-only mirror before any outbound writes exist.

**Scope**

* In: `packages/pm-sync/src/{backfill,inbound,mapping-apply}.ts`, `pm_sync_cursor` table, principal mapping by email and bot account, `pm.sync.backfill()` procedure, handler registration on the PAP-97 receiver.
* Out: outbound writes ({{pm-linear/linear-sync/outbound}}), conflict resolution and status page ({{pm-linear/linear-sync/conflicts}}).

**Spec**

* Backfill: paginated `issues(first: 100, after, includeArchived: true, orderBy: updatedAt)` plus teams, states, projects, milestones, cycles, labels, comments, attachments and relations; cursor per entity type in `pm_sync_cursor(entity_type, cursor, last_updated_at)`; resumable; full PAP backfill under five minutes at 300 ms between requests.
* Inbound: on `Issue | Comment | Project | ProjectMilestone | IssueLabel | Cycle | IssueRelation | Attachment` events, map `data` through `mapping.ts` (PAP-100), upsert by `(system: "linear", external_id)`, set `external_updated_at`, `source: "linear"`; `updatedFrom` records changed fields into `pm_sync_change(entity, field, at)` for the conflict child; `remove` and archive set `archived_at`.
* Users: `pm_external_ref` for Linear users to principals by email; unknown users become placeholder external principals (PAP-60 `kind: external`); the nine bot accounts map to agent principals.
* Unknown fields stored in `extra` jsonb; nothing dropped.

**Interface contract**

* Provides: `backfill({ since? })`, `applyInbound(event)`, `pm.sync.backfill()`, table `pm_sync_cursor`, `pm_sync_change`, event `pm.sync.inbound.applied { entity, id }`.
* Consumers: sibling children; PAP-102 renders mirrored data; PAP-204 reuses `applyInbound` mapping helpers for ClickUp shapes.
* Requires: PAP-100 tables and `mapping.ts`, PAP-97 receiver and event bus, PAP-60 principal kinds, PAP-43 jobs for the backfill worker.

**Definition of done**

* Backfill of PAP completes; counts of issues, comments, labels and relations equal Linear's (printed).
* Replaying 100 recorded webhooks upserts idempotently (second replay changes nothing).
* Cross-tenant RLS still holds on `pm_*` after sync writes.
* Changelog; Linear comment with counts.

**Test plan**

* Unit: mapping of every Linear field in the snapshot fixture; placeholder principal creation; archive mirroring.
* Integration: `nock` fixtures for the paginated backfill including a mid-run `RATELIMITED`; webhook replay idempotency.
* e2e: staging backfill.
* No UI.

**Demo**

Run `pnpm pm-sync backfill`, watch the progress log, then `pnpm api call pm.issues.list --limit 5` and see live PAP issues with states and labels. Two minutes.

**Edge cases**

* Rate limit mid-backfill: sleep 60 s, resume from cursor.
* Webhook for an entity not yet backfilled (parent project missing): fetch the parent on demand.
* Issue moved to another team: keep with `external_team` in `extra`, archive locally.
* Duplicate deliveries: `webhookId` dedupe from PAP-97.
* Strays PAP-6..PAP-12: mirrored as `Duplicate` state, nothing special.

**Dependencies**

Blocked by PAP-100, PAP-97 (through the parent). Blocks both sibling children.

**Agent**

Built by Nova (lead); reviewed by Forge (Schema Wright).

**Size**

M
"""},
{
"key": "pm-linear/linear-sync/outbound", "title": "Linear sync: transactional outbox, outbound worker and loop prevention", "type": "Build", "size": "M",
"blockedBy": ["pm-linear/linear-sync/inbound"], "blocks": ["pm-linear/linear-sync/conflicts"],
"description": """**Goal**

Let PaperOS write to Linear: every PM mutation records an outbox row in the same transaction, a worker drains it with batched, rate-aware `@linear/sdk` mutations, stores returned ids and never echoes its own changes back in, so a board drag in PaperOS lands in Linear within seconds without ping-pong.

**Scope**

* In: `pm_outbox` table, oRPC middleware that enqueues on `pm.*` mutations, `packages/pm-sync/src/outbound.ts` worker (PAP-43 job), loop prevention, retry and dead-letter, `pm.sync.retry(id)`.
* Out: conflict detection ({{pm-linear/linear-sync/conflicts}}), inbound ({{pm-linear/linear-sync/inbound}}).

**Spec**

* `pm_outbox(id, tenant_id, entity_type, entity_id, op: create | update | archive | comment | relation | label, payload, idempotency_key, attempts, next_attempt_at, last_error, state: pending | sent | dead, created_at)`; written by the mutation transaction unless the write has `source: "linear"`.
* Worker: every 2 s take up to 10 pending rows `FOR UPDATE SKIP LOCKED`, group by op, send one aliased mutation request, store Linear ids into `pm_external_ref`, mark `sent`; respect `X-RateLimit-Requests-Remaining` and pause at 10 percent; backoff 1 s to 10 min, eight attempts, then `dead`.
* Loop prevention: mutations use the sync API key whose `actor.id` PAP-97 recognises and skips on inbound; the description footer or attachment metadata carries `idempotency_key` so an early inbound echo matches the pending row instead of creating a duplicate.
* Ordering: rows for one entity are sent in `id` order; a `create` must be `sent` before its `update`s.

**Interface contract**

* Provides: `enqueueOutbox(tx, row)`, worker job `pm-sync.outbound`, `pm.sync.retry(id)`, `pm.sync.dead()` list, event `pm.sync.outbound.sent { entity, id, linearId }`, metric `outboxDepth`.
* Consumers: PAP-102 (drag to state), PAP-204 (imported issues flow out), sibling conflicts child (reads `sent` timestamps), PAP-98 optional Linear request budget accounting.
* Requires: inbound child (`pm_external_ref` ids for updates), PAP-43 jobs, PAP-35 middleware hook, PAP-60 sync principal.

**Definition of done**

* Create, update, comment, label and relation ops round-trip to Linear in staging with correct ids stored.
* Loop test: 1000 synthetic PaperOS edits produce exactly 1000 outbox rows and zero echo rows.
* Rate-limit pause and dead-letter exercised with mocked headers.
* Changelog; Linear comment with results.

**Test plan**

* Unit: enqueue middleware (skips `source: linear`), ordering per entity, backoff schedule, alias batching of mixed ops.
* Integration: `nock` Linear with `RATELIMITED` and 429 responses; idempotency-key echo match.
* e2e: staging round trip of each op.
* No UI.

**Demo**

Call `pnpm api call pm.issues.update --id <id> --state "In Progress"`, watch the worker log send the mutation, and see the Linear issue change within five seconds; run `pm.sync.dead` and see an empty list. One minute.

**Edge cases**

* Linear rejects a label not existing there: create it, flag `source: paperos`.
* Entity has no `pm_external_ref` yet (create still pending): later ops wait.
* Worker crash mid-batch: rows stay `pending` with `attempts` incremented.
* Description exceeds Linear limits: truncate with a link back to PaperOS.
* Tenant other than the PAP mirror tenant: outbox disabled per tenant setting.

**Dependencies**

Blocked by {{pm-linear/linear-sync/inbound}}. Uses PAP-43, PAP-60.

**Agent**

Built by Forge (Schema Wright) with Nova; reviewed by Sentinel.

**Size**

M
"""},
{
"key": "pm-linear/linear-sync/conflicts", "title": "Linear sync: conflict rule (Linear wins), sync status page and runbook", "type": "Build", "size": "S",
"blockedBy": ["pm-linear/linear-sync/inbound", "pm-linear/linear-sync/outbound"], "blocks": [],
"description": """**Goal**

Make the two-way sync safe and observable: when both sides changed the same field, Linear wins and PaperOS records a conflict with an in-app notice; a status page shows lag, outbox depth, dead letters and conflicts; and a runbook explains backfill, retry, dead-letter handling and key rotation.

**Scope**

* In: conflict detection in the inbound path, `pm_sync_conflict` table, `specs/pm/sync-status.spec.yaml` page at `/pm/sync`, `pm.sync.status()` procedure, `docs/pm/linear-sync.md`.
* Out: cutover tooling (flipping the winner), notification delivery beyond the event (PAP-136).

**Spec**

* Rule: on inbound `update`, for each field in `updatedFrom`, if a `pm_outbox` row for the same entity touching that field is `pending` or was `sent` after `external_updated_at` of the last applied inbound change, discard the local value, apply Linear's, and insert `pm_sync_conflict(entity_type, entity_id, field, local_value, remote_value, resolved: "linear", at)`; emit `pm.sync.conflict`.
* Status: `{ lagSeconds (now minus last inbound applied), outboxDepth, deadCount, conflicts24h, lastWebhookAt, backfillState }`; page renders cards plus a table of dead rows with a `Retry` action and conflicts with a link to the entity; refresh every 10 s.
* Runbook: first backfill, resuming, retrying dead rows, rotating the API key and webhook secret, what "Linear wins" means for board users.

**Interface contract**

* Provides: `pm.sync.status()`, `pm.sync.conflicts({ since })`, table `pm_sync_conflict`, event `pm.sync.conflict { entity, id, field }`, page `/pm/sync` (staff.admin), the "changed in Linear" toast hook consumed by PAP-102.
* Consumers: PAP-102 toast and banner, PAP-136 notification kind `pm.sync.conflict`, {{pm-linear/weekly-reaudit}} (dead count and lag in its health section).
* Requires: both sibling children, PAP-114 spec schema for the page, PAP-71 data display components.

**Definition of done**

* Simultaneous edit test: edit a title in both systems within the same second; Linear's value wins locally and one conflict row exists.
* Status page screenshots at 375, 768 and 1280 px in light and dark; Playwright coverage through gate 3.
* Runbook reviewed by Nova; changelog; Linear comment with screenshots.

**Test plan**

* Unit: conflict rule matrix (pending, sent-before, sent-after, disjoint fields).
* Integration: staged race with recorded webhook and outbox timestamps.
* e2e (Playwright): status page renders, `Retry` re-queues a dead row; run at 375 and 1280 px.
* Visual: three widths, two themes.

**Demo**

Rename an issue in PaperOS and, within a second, in Linear; refresh PaperOS to see Linear's title and a conflict entry on `/pm/sync`; retry a dead row from the same page. Ninety seconds.

**Edge cases**

* Same value on both sides: not a conflict.
* Conflict on a field PaperOS does not surface (cycle): recorded, not notified.
* Clock skew: compare Linear timestamps only.
* Thousands of conflicts (bad script): table paginated; banner shows count.
* Status called while backfill runs: `backfillState: running` with progress.

**Dependencies**

Blocked by {{pm-linear/linear-sync/inbound}}, {{pm-linear/linear-sync/outbound}}. Soft: PAP-136.

**Agent**

Built by Nova (Views Engineer sub-agent); reviewed by Sentinel (Visual Inspector).

**Size**

S
"""},
]


# FIX-6 (2026-09-17): pm-linear/workspace-reconcile is obsolete (PAP-91 and PAP-93 treat the live workspace as correct); never create it.
MERGED = {"pm-linear/workspace-reconcile": "PAP-91"}
GAPS = [g for g in GAPS if g["key"] not in MERGED]
