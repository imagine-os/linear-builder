# Round 4 digest: Project Management & Claude Pipeline (`pm-linear`)

Benchmarks: Linear (issues, sub-issues, projects, milestones, initiatives, cycles, estimates, triage, SLAs, customer requests, views, insights, templates, automations, webhooks, GitHub and Slack integrations, project updates); Jira (sprints, story points, automation rules, dependency reports); Shortcut (iterations, epics, health); Plane (self-hosted cycles and modules); Height (auto-triage, chat intake); GitHub Projects (merge-driven status); Temporal-style orchestration (watchdog, retries).

## Feature matrix (63 rows: 39 covered, 6 partial, 18 gap)

| Feature | Status | Covered by | Note |
|---|---|---|---|
| Issues with typed sections enforced by a validator | covered | PAP-93 |  |
| Sub-issues and umbrella rule | covered | PAP-93, PAP-96 | UMBRELLA_NOT_CLAIMABLE |
| Projects with Contract sections and milestones | covered | PAP-91 | 18 projects, 54 milestones |
| Milestones with target dates | covered | PAP-91 |  |
| Initiatives and roadmap roll-up | gap | r4/pm-linear/linear-initiatives-rollup | zero initiatives in the workspace |
| Cycles (sprints) with burndown and carry-over | gap | r4/pm-linear/linear-cycles-weekly-and-auto-assignment | cycles disabled |
| Estimates (points) and progress by points | gap | r4/pm-linear/linear-estimates-and-size-labels | estimation notUsed; Size only in prose |
| Due dates and overdue indicators | gap | r4/pm-linear/due-dates-slack-and-risk-alerts | zero due dates |
| Critical path and slack computation feeding claim order | partial | r4/pm-linear/due-dates-slack-and-risk-alerts, PAP-99 | PAP-99 scores; slack lived only in the schedule document |
| Priority | covered | PAP-91, PAP-93 |  |
| Label groups: Phase, Type, Model, Effort, surfaces, Character | covered | PAP-91 | Character group pending in PAP-91 |
| Workflow states for the agent pipeline | covered | PAP-91 |  |
| Triage inbox with accept, decline, duplicate, snooze | gap | r4/pm-linear/linear-triage-enable-and-intake-state-machine | triage disabled; PAP-307 listens on Todo and Backlog |
| Freeform to contract-valid drafting (Decomposer) | covered | PAP-307 |  |
| Slack voice memo and message intake | gap | r4/pm-linear/slack-voice-memo-intake | Justin sends voice memos |
| Customer requests (Linear Business feature) | gap | - | cross-project suggestion to growth support inbox (PAP-412) |
| SLAs and stale-issue automations | gap | r4/pm-linear/pipeline-sla-timers | Basic plan lacks SLAs; timers scattered across PAP-94, PAP-288, PAP-306 |
| Saved views as code for the pipeline | gap | r4/pm-linear/pipeline-views-as-code | six generic views; deny list forbids editing existing ones |
| Insights and reporting | partial | r4/pm-linear/pipeline-views-as-code, r4/pm-linear/project-updates-and-health-by-atlas | Insights is UI-only; documented charts |
| Issue templates per type, child template, decision card template, project template | gap | r4/pm-linear/issue-templates-per-type-and-card | one template today |
| Project updates and project health, lead, priority | gap | r4/pm-linear/project-updates-and-health-by-atlas | zero project updates |
| Issue attachments for PR and evidence | partial | r4/pm-linear/issue-attachments-and-evidence-bundle, PAP-97 | PAP-97 attaches the PR only; zero attachments today |
| Comments as the status channel with edited-in-place PR status | covered | PAP-97 |  |
| Relations: blocks, related, duplicate | covered | PAP-93, PAP-306 | 1215 blocks relations |
| GitHub integration: autolink, merge-to-Done, branch format | gap | r4/pm-linear/linear-github-integration-and-state-automation | unconfigured; would fight the orchestrator |
| Forgejo integration | covered | PAP-97 | custom receiver |
| Slack integration for notifications | covered | PAP-325, PAP-136 | collab project |
| Webhooks inbound with signature and dedupe | covered | PAP-97 |  |
| Workspace as code with drift check | covered | PAP-91 | extended this round for estimates, cycles, triage, initiatives, templates, views |
| Automations: auto-close, auto-archive | partial | PAP-91 | never archive (deny list); auto-close via merge integration only |
| Orchestrator: poll, atomic claim, transitions | covered | PAP-281 |  |
| Orchestrator: worktree and session launch | covered | PAP-282 |  |
| Orchestrator: deployment, /status, runbook | covered | PAP-283 |  |
| Orchestrator: Backlog to Ready promotion (branch-start rule) | covered | r4/pm-linear/orchestrator-promotion-pass | lifted out of PAP-281 as its own child |
| Concurrency: caps, file-lock hints, dependency-aware scheduling | covered | PAP-99 | eligibility rule needs alignment; amendment |
| Model and effort routing per issue with fallback chain | gap | r4/pm-linear/session-model-and-effort-routing | CLAUDE.md, PAP-282 and PAP-243 disagree |
| Credit metering and daily burn report | covered | PAP-98 |  |
| Cost per $2,500 chunk and top-up decision | gap | r4/pm-linear/chunk-progress-report | chunks.json planned but never joined to spend |
| Budgets, caps and kill switch | covered | PAP-111 | agents project |
| 24/7 operations: watchdog, capacity curve, night mode, morning report | gap | r4/pm-linear/always-on-operations-and-morning-report | Justin asked for AI running 24/7 |
| Session playbook and footer | covered | PAP-92 |  |
| Needs Justin queue, decision cards, reply grammar | covered | PAP-94 |  |
| Weekly plan re-audit | covered | PAP-306 | gains cycle and SLA checks |
| Credential broker and Linear write proxy | covered | PAP-300 |  |
| Prompt-injection actor verification for replies | covered | PAP-299 | agents project |
| PM data model mirroring Linear | covered | PAP-100 | extension deferred |
| PM model: initiatives, updates, health, cycle rules, roll-ups, SLA fields | gap | r4/pm-linear/pm-model-initiatives-updates-cycles-rollups | deferred v0.2 |
| Linear sync: backfill and inbound | covered | PAP-372 |  |
| Linear sync: outbox and loop prevention | covered | PAP-373 |  |
| Linear sync: conflict rule and status page | covered | PAP-374 |  |
| Linear sync: new entities and fields | gap | r4/pm-linear/pm-sync-initiatives-cycles-attachments | deferred v0.2 |
| PM board, list, timeline views in-app | covered | PAP-102 |  |
| Import from Linear and ClickUp | covered | PAP-204 | migration project, deferred |
| Gantt and dependency graph view | partial | PAP-102, PAP-132 | timeline exists; dependency graph rendered by the blueprint site and canvas |
| Time tracking | gap | - | not planned; session duration in PAP-98 is the proxy |
| Custom fields | partial | PAP-100 | `extra` jsonb |
| Audit log of PM changes | covered | PAP-38, PAP-300 | proxy log plus audit table |
| Contract package, conformance and kernel wiring | covered | PAP-465, PAP-468, PAP-471 | module system |
| Recorded API fixtures for pipeline tests | covered | r4/quality/recorded-http-fixtures-kit | quality project, round 4 |
| Handoff protocol and assignee switching | covered | PAP-108 | agents project |
| Session observability and stuck detection | covered | PAP-288 | agents project |
| Linear rate-limit handling | covered | PAP-281, PAP-373 |  |
| PAP-5 scoreboard and drill | covered | PAP-95, PAP-29 |  |

## New issues (18: 2 children, 16 gaps, 2 deferred to v0.2)

| Key | Title | Parent | Type / Phase | Prio | Size (est.) | Model / effort | Milestone (due) | Blocked by |
|---|---|---|---|---|---|---|---|---|
| `r4/pm-linear/orchestrator-promotion-pass` | Orchestrator: Backlog to Ready for Claude promotion pass under the branch-start rule, `promotions` table, `BASE_BRANCHES` and `pnpm linear:promote` | PAP-96 | Build P0 | 1 | M (3) | Opus 5 / high | Orchestrator claims and ships issues (2026-09-22) | PAP-281, PAP-93 |
| `r4/pm-linear/linear-estimates-and-size-labels` | Enable Fibonacci estimates on team PAP and backfill every issue's estimate from its Size (S=2, M=3, L=5) with roll-up on umbrellas and projects | - | Infra P0 | 1 | S (2) | Sonnet 5 / medium | Linear configured for the pipeline (2026-09-20) | PAP-91 |
| `r4/pm-linear/linear-cycles-weekly-and-auto-assignment` | Enable one-week cycles on team PAP, assign every scheduled issue to the cycle of its execution-schedule start day, and make claim ordering prefer the active cycle | - | Infra P0 | 2 | S (2) | Sonnet 5 / medium | Linear configured for the pipeline (2026-09-20) | PAP-91, r4/pm-linear/linear-estimates-and-size-labels |
| `r4/pm-linear/due-dates-slack-and-risk-alerts` | Set due dates from milestone targets, compute remaining critical path and slack per issue nightly, and post due-date risk comments and a Slack-at-risk view for chains that will miss | - | Build P0 | 2 | M (3) | Opus 5 / high | Orchestrator claims and ships issues (2026-09-22) | PAP-91, PAP-99 |
| `r4/pm-linear/linear-initiatives-rollup` | Create Linear initiatives for the v0.1.0 release, the v0.2 deferred set and the four brief themes; attach the eighteen projects and let Atlas post initiative updates | - | Infra P0 | 2 | S (2) | Sonnet 5 / low | Linear configured for the pipeline (2026-09-20) | PAP-91 |
| `r4/pm-linear/linear-triage-enable-and-intake-state-machine` | Enable Linear Triage on team PAP with a `Triage` state, make PAP-307 draft from the triage inbox, and define accept, decline, merge-as-duplicate and snooze outcomes with a ten-minute drafting SLA | - | Infra P1 | 2 | S (2) | Sonnet 5 / medium | PM module syncs both ways (2026-09-30) | PAP-91, PAP-307 |
| `r4/pm-linear/slack-voice-memo-intake` | Slack voice memo and message intake: transcribe audio posted in `#paperos-inbox`, create a Triage issue with the transcript and audio attachment, and reply in the thread with the drafted issue link | - | Build P1 | 2 | M (3) | Sonnet 5 / high | PM module syncs both ways (2026-09-30) | PAP-97, r4/pm-linear/linear-triage-enable-and-intake-state-machine, PAP-325 |
| `r4/pm-linear/project-updates-and-health-by-atlas` | Atlas posts a Linear project update every Monday per project with health (on track, at risk, off track) computed from slack, cycle completion and spend, and sets project lead, priority and target dates | - | Build P1 | 2 | S (2) | Sonnet 5 / medium | PM module syncs both ways (2026-09-30) | PAP-306, PAP-98, r4/pm-linear/due-dates-slack-and-risk-alerts |
| `r4/pm-linear/issue-attachments-and-evidence-bundle` | Attach PRs, gate reports, screenshots, recordings and the digest to Linear issues as native attachments, and give sessions `pnpm evidence attach` to satisfy Definition-of-done evidence | - | Build P0 | 2 | S (2) | Sonnet 5 / medium | Orchestrator claims and ships issues (2026-09-22) | PAP-97, PAP-239 |
| `r4/pm-linear/issue-templates-per-type-and-card` | Linear issue templates per Type (Build, Spec, Research, Review, Infra, Docs), a child template, a Needs Justin card template and a project template, all generated from `docs/pm/templates/` | - | Infra P1 | 3 | S (2) | Haiku 4.5 / low | Linear configured for the pipeline (2026-09-20) | PAP-91, PAP-93 |
| `r4/pm-linear/pipeline-views-as-code` | Workspace views as code: create the pipeline views (ready by slack, in review awaiting gates, stuck sessions, per character, at risk, triage inbox, deferred v0.2, critical path) with the `Pipeline:` prefix, create-only | - | Infra P1 | 3 | S (2) | Sonnet 5 / low | Linear configured for the pipeline (2026-09-20) | PAP-91 |
| `r4/pm-linear/linear-github-integration-and-state-automation` | Configure Linear's GitHub integration for `imagine-os`: branch-name format, PR autolinking, merge-to-Done as the only automatic transition, and reconciliation with the orchestrator's own state moves | - | Infra P0 | 2 | S (2) | Sonnet 5 / medium | Orchestrator claims and ships issues (2026-09-22) | PAP-91, PAP-47, PAP-97 |
| `r4/pm-linear/pipeline-sla-timers` | Pipeline SLA timers in the orchestrator: Needs Justin default deadline, In Review without gate results, Ready but unclaimed, Triage undrafted and stuck sessions, each with an escalation and a label | - | Build P1 | 3 | S (2) | Sonnet 5 / medium | PM module syncs both ways (2026-09-30) | PAP-281, PAP-288, PAP-94 |
| `r4/pm-linear/session-model-and-effort-routing` | Session model and effort routing: read the issue's Model and Effort labels, map to SDK options with a documented fallback chain on overload or refusal, record the served model in the footer and `usage_events` | - | Build P0 | 1 | S (2) | Opus 5 / high | Orchestrator claims and ships issues (2026-09-22) | PAP-281, PAP-282 |
| `r4/pm-linear/chunk-progress-report` | Chunk progress in the burn report: which $2,500 chunk is active, issues landed versus planned per chunk from `plan/chunks.json`, forecast of chunk completion and a Needs Justin top-up card | - | Build P1 | 2 | S (2) | Sonnet 5 / medium | Orchestrator claims and ships issues (2026-09-22) | PAP-98 |
| `r4/pm-linear/always-on-operations-and-morning-report` | 24/7 operations: watchdog and auto-restart for the orchestrator, capacity curve by time of day and phase, night mode for Needs Justin escalations, and a 07:00 morning report of what ran overnight | - | Build P1 | 2 | S (2) | Sonnet 5 / medium | Orchestrator claims and ships issues (2026-09-22) | PAP-283, PAP-98, PAP-288 |
| `r4/pm-linear/pm-model-initiatives-updates-cycles-rollups` | Extend the PM data model with initiatives, project updates and health, cycle assignment rules, estimate roll-ups and SLA fields so the native PM module can replace every Linear feature the pipeline now uses | - | Build P2 | 4 deferred | M (3) | Sonnet 5 / high | PM module syncs both ways (2026-09-30) | PAP-100 |
| `r4/pm-linear/pm-sync-initiatives-cycles-attachments` | Linear sync: mirror initiatives, project updates and health, cycles, estimates, due dates, triage state and attachments both ways with the Linear-wins rule | PAP-101 | Build P2 | 4 deferred | S (2) | Sonnet 5 / medium | PM module syncs both ways (2026-09-30) | PAP-372, PAP-373, r4/pm-linear/pm-model-initiatives-updates-cycles-rollups |

## Amendments to existing specs (8)

* **PAP-281** (Scope): * Round 4: the promotion work package moves out of this issue into its own child of PAP-96, `Orchestrator: Backlog to Ready for Claude promotion pass` (`r4/pm-l…
* **PAP-96** (Scope): * Round 4: children are PAP-281 (poll, claim, transitions), PAP-282 (worktree and launch), PAP-283 (deployment, `/status`, runbook) and the new promotion child…
* **PAP-282** (Spec): * Model selection (round 4, aligns with CLAUDE.md): `launchSession` calls `resolveModel(issue, character, 'builder')` from `src/session/model-routing.ts`; prece…
* **PAP-99** (Spec): * Eligibility rule alignment (round 4): the branch-start rule is not opt-in. A blocker counts as satisfied when it is `Done`, `Canceled`, `Duplicate`, or `In Re…
* **PAP-91** (Spec): * Round 4 additions managed by the same `--check|--apply` script and recorded in `linear-workspace.json`: team settings `issueEstimationType: fibonacci`, `cycle…
* **PAP-97** (Spec): * Attachments (round 4): besides the PR attachment, every gate artefact posted through this receiver is attached to the issue once through `attach()` (`r4/pm-li…
* **PAP-98** (Spec): * Round 4 fields: `usage_events.model` is the served model from `resolveModel()` (labels first), and `usage_events.estimate` carries the issue's Linear estimate…
* **PAP-100** (Edge cases): * Round 4 (Linear features enabled): `estimate`, `due_date` and `cycle_id` are now populated on the Linear side for every issue, so the mapping document marks t…

## Cross-project suggestions (4)

* **collab**: Slack decision cards with approve, reject and option buttons for Needs Justin, posting replies back as T1 Linear comments through the orchestrator
* **growth**: Customer requests intake: link support-inbox conversations (PAP-412) to PM issues as request counts and notify requesters on Done
* **forge**: Branch-name format setting shared by Linear's GitHub integration, PAP-46 policy and the orchestrator's `ensureWorktree`
* **app-shell**: `paperos create` wires the new Linear project with estimates, one-week cycles, triage, templates and the `Pipeline:` views from `linear-workspace.json`

## What was missing and why it matters

1. The workspace used none of Linear's planning features (estimates off, cycles off, triage off, zero due dates, initiatives, project updates or attachments); nine issues turn each on from the same workspace-as-code script and make the orchestrator and PM module mirror them.
2. The promotion pass that refills Ready for Claude was folded into PAP-281 on the zero-slack orchestrator chain; it is now its own child so the poll loop stays one session.
3. CLAUDE.md, PAP-282 and PAP-243 disagreed on where a session's model comes from; one routing issue reads the Model and Effort labels, applies the 4b reviewer rule and handles overload fallback, which is what Justin's per-job model switching and chunk costing need.
4. Justin asked for cost per $2,500 chunk and for AI running 24/7: the chunk progress report joins `plan/chunks.json` to metered spend with a top-up card, and the always-on issue adds a watchdog, capacity curve, night mode and a morning report.
5. Voice memos and one-line requests now have an intake path (Slack channel to Triage state to Decomposer) with a ten-minute SLA, and SLA timers replace the three separate clocks in PAP-94, PAP-288 and PAP-306.
