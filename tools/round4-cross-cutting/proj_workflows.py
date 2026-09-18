from gen_common import trio

K = 'workflows'
MS = ['Workflow contract and approvals', 'Forms builder and document templates', 'E-signature, canvas editor and swap']

PROJECT = {
    'key': K,
    'name': 'Workflows, Approvals, Forms, Documents & E-Signature',
    'lead': 'Nova',
    'phase': 'P2',
    'description': 'The cross-module process layer: a durable workflow engine triggered by any domain event with human tasks and approvals, one approvals framework every module reuses, a standalone forms builder with logic, payments and public embeds, document templates that merge tenant data into PDF and DOCX, and e-signature with an audit certificate.',
    'content': """Goal: table automations (PAP-174, PAP-388 to PAP-390) give one table reactions; businesses run processes that cross tables, modules and people: an expense over $500 needs a manager's approval, a signed proposal creates a project and an invoice, a new patient intake form creates a record, a booking and a consent document. Today five issues each build their own approval step (PAP-94 Needs Justin, PAP-401 social queue, PAP-408 referral rewards, PAP-185 expenses, PAP-400 payroll typed-total), forms exist only as a single-page record-entry view (PAP-169) and a Webflow embed (PAP-193), documents exist only as invoices (PAP-180, PAP-235), and nothing signs anything. This project adds one module for all of it: a workflow model and durable run engine on pg-boss (PAP-43) triggered by the event bus (PAP-303), a step catalogue that reuses the PAP-389 action catalogue and the assistant `ActionPort`, a generic approvals framework with policies and an inbox, a forms builder (multi-page, conditional logic, uploads, payments, anti-spam, embeds) whose submissions land in any dataset or start any workflow, document templates with merge fields rendered through the PAP-235 print kit to PDF and DOCX, and e-signature (own ceremony first, Documenso embed evaluated) with a tamper-evident audit certificate. Table automations remain the simple path and can call a workflow; workflows never re-implement filters, actions or field types. Non-goals: BPMN import, a general scripting language, external RPA, qualified electronic signatures (QES) in v0.2.

## Contract

**Provides**

* `@paperos/contract-workflows`: `WorkflowDefinition`, `StepDefinition`, `WorkflowRun`, `Task` schemas; `WorkflowPort` (`define`, `publish`, `start`, `signal`, `cancel`, `listRuns`), `StepKindRegistry` (`defineStepKind`), `ApprovalPort` (`request`, `decide`, `delegate`, `policies`), `TaskPort` (`assign`, `complete`, `inbox`), `FormPort` (`define`, `publish`, `submit`, `submissions`), `DocumentTemplatePort` (`define`, `render`, `generate`), `SignaturePort` (`request`, `sign`, `certificate`, `verify`); slots `record.panel.tabs.workflows`, `shell.settings.sections.workflows`, `portal.forms`, `dashboard.blocks.tasks`.
* Events: `workflow.run.started|completed|failed|cancelled`, `workflow.task.created|completed`, `approval.requested|approved|rejected|expired`, `form.submitted`, `document.generated`, `signature.requested|signed|declined|completed`.
* Notification kinds registered with PAP-136: `task.assigned`, `approval.requested`, `approval.decided`, `signature.requested`, `signature.completed`, `form.submitted`.

**Requires**

* data-layer: jobs (PAP-43), event bus and outbox (PAP-303), idempotency (PAP-304), files (PAP-37), audit (PAP-38), email (PAP-370), field encryption (PAP-353), retention (PAP-355).
* tables: `FilterTree` (PAP-279), field types (PAP-338 to PAP-340), action catalogue and expressions (PAP-389), automation runtime hooks (PAP-388), views for inboxes (PAP-161, PAP-169), record surface (PAP-333), dry-run transactions (PAP-348 pattern).
* identity: permission engine and audiences (PAP-59, PAP-55), portal shell (PAP-62), delegation of authority is a role attribute (PAP-227).
* collab: comments on tasks (PAP-131), notifications (PAP-136), canvas node types (PAP-320), editor (PAP-142).
* business-core: Checkout and pay pages for form payments (PAP-396), documents and numbering (PAP-395), ledger postings for signed quotes (PAP-394), hash chain pattern (PAP-393).
* design-system: print and email kit (PAP-235), form controls and pickers (PAP-233, PAP-236), state components (PAP-234). input: drag-and-drop for builders (PAP-329 to PAP-331).
* assistant: `ActionPort` for the `agent` step (optional). realtime: live task updates (PAP-381).

**Consumed by**

* pm-linear (Needs Justin decisions through `ApprovalPort`, PAP-94), growth (social approval queue PAP-401, referral rewards PAP-408, landing forms PAP-193), business-core (expense approvals PAP-185, payroll typed-total PAP-400, quotes signed → invoice PAP-395), commerce (purchase approvals, work-order checklists, signed estimates), engagement (intake forms, surveys on the forms runtime, consent documents), migration (business packs ship workflows and forms in `pack.yaml`).

**Owner**: Nova leads and builds the engine, forms and canvas; Ledger builds documents; Sentinel (Security Auditor) reviews approvals and signatures. Milestones: Workflow contract and approvals (2026-10-01), Forms builder and document templates (2026-10-09, deferred v0.2), E-signature, canvas editor and swap (2026-10-16, deferred v0.2).""",
    'milestones': [
        {'name': MS[0], 'targetDate': '2026-10-01', 'description': 'Workflow model, contract v0.1, the approvals framework that existing approval steps adopt, and the task inbox.'},
        {'name': MS[1], 'targetDate': '2026-10-09', 'description': 'Deferred (v0.2). Durable run engine and step catalogue, forms builder runtime and publishing, document templates and generation.'},
        {'name': MS[2], 'targetDate': '2026-10-16', 'description': 'Deferred (v0.2). E-signature core and audit certificate, workflow canvas editor, conformance suite and kernel wiring.'},
    ],
}

ISSUES = [
 {
  'key': f'r4/{K}/workflow-model', 'title': 'Specify the workflow model: definitions, versions, steps, runs, tasks and waits; event-bus triggers; the boundary with table automations',
  'type': 'Spec', 'tier': 'fable', 'size': 'M', 'priority': 2, 'surfaces': ['Developer', 'Staff'], 'milestone': MS[0], 'deferred': False,
  'blockedBy': ['PAP-303', 'PAP-388', 'PAP-389', 'PAP-279', 'PAP-302'], 'blocks': [f'r4/{K}/contract-publish', f'r4/{K}/run-engine', f'r4/{K}/approvals-framework'],
  'goal': "Write the one document that keeps workflows, table automations and approvals from becoming three engines: the workflow definition and run model, how a run is triggered by any PAP-303 event or by an automation action, what a step is, how human tasks and waits pause a run durably, how versions coexist, and the rule that a workflow orchestrates existing actions and never re-implements them.",
  'scope_in': [
    "`docs/workflows/model.md` (ADR style) and Zod schemas in the contract package: `WorkflowDefinition` (`id`, `tenant_id`, `name`, `version`, `trigger: { kind: 'event'|'manual'|'schedule'|'automation'|'form'|'api', topic?, filter: FilterTree }`, `steps: StepDefinition[]`, `inputs` schema, `status draft|published|retired`), `StepDefinition` (`id`, `kind`, `config`, `next`, `onError`, `timeout`), `WorkflowRun` (`definition_version`, `status`, `context jsonb`, `current_steps[]`, `started_by ActorRef`, `correlation EntityRef?`), `RunStep` (attempt log), `Task` (`kind human|approval`, `assignees`, `due`, `form?`, `decision`)",
    "Trigger semantics: exactly-once run creation per `(definition, event id)` through the outbox consumer with an idempotency key; schedule triggers use the recurrence engine (`r4/data-layer/recurrence-engine`) and PAP-43 cron; `automation` trigger means a PAP-389 action `workflow.start`",
    "Boundary rule with PAP-174: automations are single-table, stateless reactions; anything with a wait, a human, a branch across modules or more than five actions is a workflow; the automation builder offers 'convert to workflow'",
    "Versioning: runs pin the definition version; publishing a new version affects new runs only; `migrateRuns` is an explicit, logged operation with a step-id map",
  ],
  'scope_out': ['Engine implementation', 'UI', 'Forms, documents and signatures (own issues; the model only defines the step kinds that reference them)'],
  'spec': [
    'Every step kind is declared with `defineStepKind({ kind, config: zod, execute | suspend, resume?, compensate? })`; suspending kinds (human task, approval, wait, signature) persist a `RunStep` with a resume token; no step blocks a worker',
    'Context is a JSON document under a size limit (256 KB) with `EntityRef`s, never row copies; expressions use the PAP-389 template language over context and trigger payload',
    'Errors: per-step retry policy inherits PAP-43 defaults; `onError: fail | continue | compensate | goto`; compensation runs registered `compensate` handlers in reverse order',
    'Permissions: a definition runs with the identity of its `runAs` (the starter, a service principal, or a named role) declared at publish and checked by PAP-59; steps that write records are audited with `reason = workflow:<runId>`',
    'Observability: every run has a timeline (steps, attempts, waits, decisions) exposed through `workflows.runs.get` and rendered on the record panel tab',
  ],
  'provides': "`docs/workflows/model.md`, schemas `WorkflowDefinition`, `StepDefinition`, `WorkflowRun`, `RunStep`, `Task`, the trigger and versioning rules, the automation boundary rule (also appended to PAP-174)",
  'consumes': "event envelope and topics (PAP-303), automation runtime and actions (PAP-388, PAP-389), `FilterTree` (PAP-279), `Money` and `EntityRef` (PAP-302)",
  'consumed_by': f"every issue in this project; PAP-174 (convert-to-workflow), PAP-94 (approval semantics), migration packs (`workflows[]` in `pack.yaml`)",
  'dod': [
    'Document merged with ADR; schemas exported; the boundary paragraph added to PAP-174 by comment; migration for the five tables with RLS and harness enrolment',
    'Three worked examples in the doc: expense approval, proposal-to-project, patient intake, each as a definition JSON that validates',
  ],
  'tests': {
    'Unit': 'schema fixtures (valid and invalid per table); trigger idempotency key derivation; version pinning rules',
    'Review': 'Sentinel checks the `runAs` model against PAP-59 and the threat model (a workflow is a way to act with borrowed authority)',
  },
  'demo': "Walk through the proposal-to-project example: event `signature.completed` starts a run that creates a project, drafts an invoice, waits for a manager approval and posts a comment; show the definition JSON validating.",
  'edge': [
    'Trigger event replayed after an outage: idempotency on `(definition, eventId)` prevents a second run; the replay is logged',
    'Definition retired while runs are suspended: suspended runs finish on their pinned version; new triggers are ignored with a warning event',
  ],
  'deps': 'PAP-303 (hard), PAP-388 and PAP-389 (hard: reuse), PAP-279 and PAP-302 (hard), `r4/data-layer/recurrence-engine` (soft: schedule triggers).',
  'builder': 'Nova', 'reviewer': 'Sentinel (Security Auditor)', 'tenant_data': False, 'module_edge': False,
 },
 {
  'key': f'r4/{K}/approvals-framework', 'title': 'Build the approvals framework: approval requests, policies (thresholds, roles, quorum), delegation, SLA escalation and adoption by the five existing approval steps',
  'type': 'Build', 'tier': 'opus', 'size': 'M', 'priority': 2, 'surfaces': ['Staff', 'Developer'], 'milestone': MS[0], 'deferred': False,
  'blockedBy': [f'r4/{K}/workflow-model', f'r4/{K}/contract-publish', 'PAP-59', 'PAP-136', 'PAP-43', 'PAP-38'], 'blocks': [f'r4/{K}/task-inbox', f'r4/{K}/run-engine'],
  'goal': "Replace five bespoke approval steps with one: an `approval_request` entity with a policy (who may approve, thresholds by `Money`, quorum, order), decisions with reasons, delegation while away, SLA escalation through notifications, and adapters so PAP-94 Needs Justin, PAP-401 social posts, PAP-408 referral rewards, PAP-185 expenses and PAP-400 payroll totals all become approval requests with the same inbox and audit shape.",
  'scope_in': [
    "`packages/workflows/src/approvals/`: tables `approval_policy` (`subjectType`, `rules: [{ when: FilterTree, approvers: RoleRef|PrincipalRef[]|'manager-of:<field>', quorum, order: parallel|sequence, sla }]`), `approval_request` (`subject EntityRef`, `policy_version`, `status pending|approved|rejected|expired|cancelled`, `amount Money?`, `summary`, `preview jsonb`), `approval_decision` (`approver`, `decision`, `reason`, `on_behalf_of?`)",
    "`ApprovalPort.request(subject, { policyKey, amount, summary, preview })` resolves approvers now (snapshot) and emits `approval.requested`; `decide` enforces quorum and order; `delegate(from, to, range)` with PAP-227 attribute check; `expire` job with escalation chain",
    "Adapters: `pm.needs-justin` (PAP-94 `/approve` comment grammar becomes a decision), `social.post` (PAP-401 queue reads `approval_request`), `referral.reward` (PAP-408), `expense` (PAP-185 threshold policy), `payroll.run` (PAP-400 typed-total as a `confirmation` field on the decision)",
    "Console page `/console/approvals` as a saved list view (PAP-169) with decision drawer, preview rendering (diff, document, post), bulk approve within policy limits",
  ],
  'scope_out': ['Workflow engine (this framework works standalone and as a step kind)', 'Portal customer approvals (v0.3: customers approving quotes is a signature)'],
  'spec': [
    'Segregation of duties: the requester can never be an approver of their own request even if a role matches; policies can require `distinctFrom: [requester, creator]`',
    'Money thresholds compare in the tenant reporting currency using `r4/business-core/fx-rates` when present, else refuse cross-currency policies at publish',
    'Decisions are immutable rows; changing one\'s mind is a new decision that supersedes within the window the policy allows; the audit trail (PAP-38) shows both',
    'SLA: `sla.hours` then escalate to `escalateTo` (manager-of, role) with notification kind `approval.escalated`; a second breach auto-rejects or auto-approves only when the policy says so explicitly',
    'Everything decided through Slack (PAP-325) or email links uses signed one-time tokens bound to the approver principal; no anonymous approval',
  ],
  'provides': "`ApprovalPort` default adapter, tables and `approvals.*` procedures, the five adapters, `/console/approvals` page, notification kinds `approval.*`, `<ApprovalCard/>` component",
  'consumes': "permission engine and attribute policies (PAP-59, PAP-227), notifications (PAP-136), jobs (PAP-43), audit (PAP-38), list view (PAP-169), Slack channel (PAP-325), `Money` (PAP-302)",
  'consumed_by': "PAP-94, PAP-401, PAP-408, PAP-185, PAP-400 (adopters), commerce purchasing, assistant `send|money` tool classes, engagement (refund approvals)",
  'dod': [
    'The five adopters open and decide through the framework in the demo tenant; each adopter issue receives a comment naming the adapter file and the removed bespoke code',
    'Quorum, sequence, delegation, expiry and escalation each covered by an integration test; segregation-of-duties fuzzed',
  ],
  'tests': {
    'Unit': 'policy resolution over 20 fixture policies; quorum math; supersede window; token binding',
    'Integration': 'expense over threshold → request → manager approves via email token → ledger posting (PAP-394) proceeds; below threshold auto-approves; SLA breach escalates',
    'E2E': 'approvals page bulk approve, keyboard-only decision drawer, screenshots',
  },
  'demo': "Submit a $700 expense as staff; the manager gets a Slack message, approves with a reason; the approvals page shows the trail; a second request is delegated to a colleague while the manager is on leave.",
  'edge': [
    'Approver leaves the organisation (membership removed, PAP-58): pending requests re-resolve approvers from the policy and note the change',
    'Policy edited while requests are pending: pending requests keep `policy_version`; the page marks them "under a previous policy"',
  ],
  'deps': f"`r4/{K}/workflow-model` and `r4/{K}/contract-publish` (hard), PAP-59 and PAP-227 (hard), PAP-136, PAP-43, PAP-38 (hard), PAP-325 (soft), `r4/business-core/fx-rates` (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Security Auditor)',
 },
 {
  'key': f'r4/{K}/task-inbox', 'title': 'Build the My Tasks inbox: human tasks and approvals across workflows as a saved view with SLAs, bulk actions, live updates and a dashboard block',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'medium', 'size': 'S', 'priority': 3, 'surfaces': ['Staff', 'Customer'], 'milestone': MS[0], 'deferred': False,
  'blockedBy': [f'r4/{K}/approvals-framework', 'PAP-169', 'PAP-172', 'PAP-381', 'PAP-386'], 'blocks': [],
  'goal': "Give every person one list of what is waiting on them: human tasks and approval requests from every workflow and module, as a saved list view with due dates and SLA badges, live updates, bulk complete, a portal variant for customer-facing tasks (sign this, upload that) and a dashboard block.",
  'scope_in': [
    "Dataset `tasks` registered with PAP-161 unifying `task` and `approval_request` rows assigned to the principal (or their roles); route `/tasks` on the list view (PAP-169) with default sort by due, group by kind; `?r=` opens the task drawer with the form or decision UI",
    "Portal route `/portal/tasks` limited to `audience: customer` tasks (signature requests, form completions, document uploads) with the PAP-62 shell",
    "Live updates via `useLiveEvents('workflow.task.*')` (PAP-381); bulk complete for tasks without required fields; snooze (re-due) with a reason",
    "Dashboard block `tasks.mine` for PAP-386 with count and next due; notification kinds `task.assigned`, `task.due_soon` (24 h) through PAP-136",
  ],
  'scope_out': ['Task creation UI beyond workflows and the assistant', 'PM issues (PAP-100 remain separate; a workflow step may create one)'],
  'spec': [
    'A task is visible to its assignees, the run starter and roles with `tasks.manage`; completing requires the assignee or a delegate; every completion writes the `Task.decision` or form payload to the run context',
    'SLA badge states: on track, due soon (25 percent of SLA left), overdue; colours from PAP-66 semantic tokens with text labels for a11y',
    'Bulk complete never applies to approvals above the policy\'s `bulkLimit` or to tasks with required form fields',
    'Reassignment is allowed to anyone the policy would have allowed; the run timeline records it',
  ],
  'provides': "`tasks` dataset and `/tasks`, `/portal/tasks` pages, task drawer, dashboard block, notification kinds `task.*`",
  'consumes': "approvals framework, list view and saved views (PAP-169, PAP-172), live events (PAP-381), dashboard blocks (PAP-386), notifications (PAP-136), portal shell (PAP-62)",
  'consumed_by': "workflows run engine (human task step), commerce (work-order tasks), engagement (customer signature and intake tasks), assistant (notes to tasks)",
  'dod': ['Demo tenant shows mixed tasks and approvals for a manager; portal shows a signature task for a customer; live update proven across two windows'],
  'tests': {
    'Unit': 'SLA state math across timezones; bulk eligibility; visibility predicate',
    'E2E': 'complete a task with a required form, snooze another, approve from the drawer; phone width list and drawer',
  },
  'demo': "As a manager, open `/tasks`, approve one expense and complete an onboarding checklist task; open the portal as a customer and see the signature task waiting.",
  'edge': ['Task assigned to a role with no current members: shown to `tasks.manage` holders with an "unassigned" badge and escalated after the SLA'],
  'deps': f"`r4/{K}/approvals-framework` (hard), PAP-169 and PAP-172 (hard), PAP-381 and PAP-386 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Visual Inspector)',
 },
 {
  'key': f'r4/{K}/run-engine', 'title': 'Build the durable workflow run engine on pg-boss: step executor, suspend and resume, timers, retries, compensation, run log and replay',
  'type': 'Build', 'tier': 'opus', 'size': 'L', 'priority': 4, 'surfaces': ['Developer', 'Staff'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': [f'r4/{K}/workflow-model', f'r4/{K}/approvals-framework', 'PAP-43', 'PAP-303', 'PAP-304', 'PAP-388'], 'blocks': [f'r4/{K}/step-catalogue', f'r4/{K}/canvas-editor'],
  'goal': "Run the model durably: an engine that consumes trigger events from the outbox, executes steps as pg-boss jobs, suspends on human tasks, approvals, waits and signatures without holding a worker, resumes from signals, retries and compensates per the definition, and records a replayable run log, sharing the PAP-388 limits, loop guard and circuit breaker so a runaway workflow cannot exhaust a tenant.",
  'scope_in': [
    "`packages/workflows/src/engine/`: `Scheduler` (outbox consumer per trigger topic, PAP-303) creating runs idempotently; `StepRunner` job `workflow.step` with `singletonKey = runId` so one step per run executes at a time; `Resumer` for `signal(runId, stepId, payload)`; `Timer` using pg-boss `startAfter` for waits and timeouts; `Compensator`",
    "Run log: `run_step` attempts with input/output hashes, durations and errors; `workflows.runs.replay(runId, fromStep)` re-executes in a dry-run transaction (PAP-348 pattern) for debugging; live progress via PAP-381 `job.progress`",
    "Guards from PAP-388 reused: daily run limit per tenant, loop guard (a run cannot trigger itself more than 3 deep through events), circuit breaker per definition after 20 consecutive failures with a notification",
    "Admin page `/console/workflows/runs` (grid view) with status filters, timeline drawer, cancel, retry step, and the `X-PaperOS-Impl` shown for shadow runs",
  ],
  'scope_out': ['Step kinds beyond `noop`, `wait`, `branch` used for tests (step catalogue)', 'Editor'],
  'spec': [
    'Exactly-once step effects: every step execution carries `Idempotency-Key = <runId>:<stepId>:<attempt>` into the actions it calls (PAP-304); a retried step that already produced its effect returns the stored result',
    'Suspension writes the resume token and releases the worker within 50 ms; resume is a new job; a suspended run costs nothing while waiting',
    'Concurrency: 8 step workers per API replica, fair-shared across tenants by pg-boss priority derived from tenant plan and recent usage',
    'Timeouts: per step `timeout` then `onError`; whole-run `maxDuration` default 90 days for suspended runs, after which the run expires with a notification',
    'Compensation runs in reverse order of completed steps with their own retry policy; a failed compensation lands in the DLQ (PAP-43) and pings `workflows.manage`',
  ],
  'provides': "`WorkflowPort` default adapter (`start`, `signal`, `cancel`, `listRuns`, `replay`), `workflow.step` job, run log tables, `/console/workflows/runs` page, `workflow.run.*` events",
  'consumes': "jobs and DLQ (PAP-43), outbox and topics (PAP-303), idempotency (PAP-304), automation guards (PAP-388), dry-run transactions (PAP-348), live progress (PAP-381), grid view (PAP-165)",
  'consumed_by': f"`r4/{K}/step-catalogue`, `r4/{K}/canvas-editor`, forms (`form` trigger), signatures (`signature.completed` resume), commerce and engagement processes, migration packs",
  'dod': [
    'The three model examples run end to end on the compose stack with a forced worker crash mid-run and recover; 1,000 concurrent suspended runs cost zero worker time (measured)',
    'k6 scenario (PAP-242): 200 runs per minute with p95 step latency under 500 ms; loop guard and circuit breaker demonstrated',
  ],
  'tests': {
    'Unit': 'state machine transitions; idempotency key derivation; compensation order; timer scheduling across DST',
    'Integration': 'crash between effect and log write is recovered by the idempotent replay; signal for an unknown token is rejected; run expiry',
    'Chaos': 'kill the worker container during a 20-step run three times; the run completes with exactly one effect per step',
  },
  'demo': "Start 50 expense-approval runs, kill the worker, restart it, and show every run completing with one ledger posting each; open one run's timeline and replay it in dry-run.",
  'edge': [
    'Tenant module disabled while runs are suspended: runs pause with status `blocked:module_disabled` and resume when re-enabled; nothing is lost',
    'Event storm (10k events in a minute): the scheduler batches run creation and the fair-share priority keeps other tenants\' steps flowing',
  ],
  'deps': f"`r4/{K}/workflow-model` and `r4/{K}/approvals-framework` (hard), PAP-43, PAP-303, PAP-304 (hard), PAP-388 (hard: shared guards), PAP-348, PAP-381 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Edge Case Hunter)',
 },
 {
  'key': f'r4/{K}/step-catalogue', 'title': 'Build the step catalogue: human task, approval, wait, branch, for-each, sub-workflow, automation action, agent step, webhook, notify, generate document, request signature',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'high', 'size': 'M', 'priority': 4, 'surfaces': ['Developer', 'Staff'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': [f'r4/{K}/run-engine', 'PAP-389', 'PAP-291', 'PAP-136'], 'blocks': [f'r4/{K}/canvas-editor'],
  'goal': "Give workflows their vocabulary: twelve step kinds built with `defineStepKind`, each with a Zod config, an execute or suspend handler, a compensation where meaningful and a config form, reusing the PAP-389 action catalogue for anything that touches records or connectors so a workflow step and an automation action are the same code.",
  'scope_in': [
    "Kinds: `human.task` (assignees, form ref, due), `approval` (policy key, amount expression), `wait.duration|until|event` (event with `FilterTree` match), `branch` (conditions), `forEach` (over a context array or a view query, parallel with limit), `subWorkflow`, `action` (any PAP-389 action by id), `agent` (assistant `ActionPort` with a prompt, tool allow-list and confirmation policy; optional module), `webhook.send` (signed, PAP-389), `notify` (kind + recipients), `document.generate` (template id → file into context), `signature.request` (suspends until signed)",
    "Config forms generated from the Zod schemas with PAP-233 adapters and expression fields with autocomplete over the run context",
    "Compensations: `action` delegates to the action's undo when present; `document.generate` deletes the generated file; `notify` sends a retraction only when configured",
  ],
  'scope_out': ['Custom code steps (never in v0.2; the `action` step and connectors are the extension points)', 'Editor'],
  'spec': [
    '`forEach` fan-out is bounded (default 500 items, plan-limited) and each item is its own idempotent step attempt; partial failure policy `continue | stopAll`',
    '`agent` steps never execute `send` or `money` tools; those produce approval requests through the approvals framework automatically',
    '`wait.event` registers a lightweight subscription row so the engine wakes only the runs that match, evaluated with the PAP-279 in-memory evaluator',
    'Every kind ships a fixture pair (valid, invalid config) and a conformance case; the docs generator (PAP-445) lists kinds per module',
    '`subWorkflow` passes a mapped input and receives a mapped output; recursion depth capped at 5',
  ],
  'provides': "the twelve step kinds registered in `StepKindRegistry`, config forms, compensation handlers, fixtures",
  'consumes': "run engine, action catalogue and template expressions (PAP-389), agent execution and assistant `ActionPort` (PAP-291, optional), notifications (PAP-136), forms and documents and signatures ports (own issues, soft)",
  'consumed_by': f"`r4/{K}/canvas-editor`, business packs, commerce and engagement processes",
  'dod': ['Each kind exercised in an integration test; the three model examples rebuilt from catalogue kinds only; docs page lists every kind with its config schema'],
  'tests': {
    'Unit': 'config validation per kind; expression resolution with missing context keys; forEach bounds',
    'Integration': 'agent step proposing a `money` tool produces an approval request, never an execution; wait.event wakes exactly the matching run',
  },
  'demo': "Compose \"new signed proposal → create project → for each line item create a task → notify owner → wait 7 days → if unpaid send reminder\" from catalogue kinds and run it against the demo tenant.",
  'edge': ['Action removed from the catalogue after publish: the step fails with `ACTION_GONE` at execute time and the definition is flagged in the editor'],
  'deps': f"`r4/{K}/run-engine` (hard), PAP-389 (hard), PAP-291 (soft), PAP-136 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Code Reviewer)',
 },
 {
  'key': f'r4/{K}/canvas-editor', 'title': 'Build the workflow canvas editor on React Flow: node palette from the step catalogue, validation, versions and diff, test runs with fixture events, convert from automation',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'high', 'size': 'M', 'priority': 4, 'surfaces': ['Staff'], 'milestone': MS[2], 'deferred': True,
  'blockedBy': [f'r4/{K}/step-catalogue', 'PAP-320', 'PAP-321', 'PAP-390', 'PAP-331'], 'blocks': [],
  'goal': "Let a staff user draw a process: a canvas editor reusing the PAP-320 node and edge types and the PAP-321 collaborative overlay, a palette from the step catalogue, inline config forms, validation that blocks publishing broken graphs, versions with a visual diff, test runs against fixture events, and a one-click conversion from a table automation (PAP-390).",
  'scope_in': [
    "Route `/console/workflows/:id/edit` (spec) with the canvas engine from PAP-320 (`workflow.step` node type, `workflow.edge` with condition labels), Yjs-backed layout and notes (PAP-321) so two people can edit together, keyboard-accessible node operations (PAP-330)",
    "Palette and inspector: drag from the catalogue (PAP-331 `DropZone`), inspector shows the step config form; validation panel (unreachable steps, missing `next`, cycles without a wait, unknown expressions) blocks publish",
    "Versions: publish creates a version; version list with a graph diff (added, removed, changed nodes); rollback republishes an older version",
    "Test run: pick a fixture event (or a recent real event from PAP-303) and run in dry-run mode with the run engine's replay; timeline shown beside the canvas; `Convert to workflow` from the PAP-390 automation page maps trigger, conditions and actions",
  ],
  'scope_out': ['Freeform drawing beyond notes', 'BPMN import/export'],
  'spec': [
    'The canvas is generated from the definition and writes back to it; layout is a separate document so a definition diff never contains coordinates',
    'Autolayout (dagre) on demand; manual positions persist per version',
    'Large graphs (300 nodes) stay at 60 fps with the PAP-322 virtualisation techniques; minimap and search',
    'Validation messages deep-link to the node and are announced to screen readers; publish is disabled with the reasons listed',
  ],
  'provides': "editor page, `workflow.step|edge` node types, version diff component, test run panel, convert-from-automation action",
  'consumes': "canvas node types and overlay (PAP-320, PAP-321), performance techniques (PAP-322), automation builder (PAP-390), drag-and-drop (PAP-331), keyboard alternative (PAP-330), step catalogue and engine",
  'consumed_by': "business packs (workflows authored and exported as pack content), assistant (\"build me a workflow\" drafts open here in v0.3)",
  'dod': ['Two users co-edit a workflow; publish blocked by validation then succeeds; test run shows a timeline; conversion from a starter automation produces a valid definition; screenshots at 1024 and 1920 (phones show read-only)'],
  'tests': {
    'Unit': 'graph validation rules over 15 fixture graphs; diff algorithm; autolayout determinism',
    'E2E': 'drag a node, configure, connect, publish, roll back; keyboard-only node insertion (PAP-330); two contexts co-editing',
  },
  'demo': "Convert the \"notify on overdue invoice\" automation into a workflow, add an approval and a wait, publish, and test-run it with last week's real event.",
  'edge': ['Definition edited by API while open in the editor: the Yjs overlay shows a stale banner (PAP-144) and offers reload; the editor never silently overwrites'],
  'deps': f"`r4/{K}/step-catalogue` (hard), PAP-320, PAP-321 (hard), PAP-390, PAP-331, PAP-330 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Visual Inspector)',
 },
 {
  'key': f'r4/{K}/forms-schema-runtime', 'title': 'Build the forms builder schema and runtime: multi-page forms, conditional logic, field types from the tables engine, validation, uploads, submissions to a dataset or a workflow',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'high', 'size': 'M', 'priority': 4, 'surfaces': ['Staff', 'Customer'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': [f'r4/{K}/workflow-model', 'PAP-169', 'PAP-338', 'PAP-339', 'PAP-37', 'PAP-233'], 'blocks': [f'r4/{K}/forms-publishing'],
  'goal': "Grow the PAP-169 form view into a real forms product without a second field system: a `FormDefinition` with pages, sections and logic over the tables field types, a renderer that works in the portal, in public pages and embedded, server-side validation, uploads through PAP-37, and a submission pipeline that writes to any dataset, starts a workflow, or both.",
  'scope_in': [
    "`packages/workflows/src/forms/`: `FormDefinition` (`pages[]`, `blocks[]` of `field | text | image | divider | payment | signature`, `logic[]` rules `when FilterTree → show|hide|require|jumpTo`, `submitTo: { dataset?, mapping, workflow? }`, `settings` for confirmations, limits, languages), `form_submission` (`payload`, `files[]`, `status received|processed|failed|spam`, `source`, `submitter`)",
    "Renderer `<FormRunner/>` on PAP-233 form-state adapters and the PAP-338/339 field editors in `form` mode; autosave drafts for signed-in users; progress bar; i18n through PAP-27 with per-language copy fields (PAP-375 pattern)",
    "Builder page `/console/forms/:id/edit`: page list, block palette, field settings panel (shared `FieldSettingsPanel` PAP-339), logic editor on the PAP-166 filter builder, preview at widths",
    "Submission pipeline: server validation against the definition, PAP-37 file completion, mapping into `records.create` (PAP-342 path) or `workflows.start` with `form` trigger; `form.submitted` event",
  ],
  'scope_out': ['Publishing, embeds, anti-spam and payments (next issue)', 'Survey analytics (engagement)'],
  'spec': [
    'Logic evaluates client-side for UX and server-side for truth with the PAP-279 in-memory evaluator; a hidden required field is never required',
    'Mapping supports constant values, submitter identity, UTM and referrer (PAP-194) and expression transforms; unmapped fields stay in `payload`',
    'Uploads: presigned direct upload, per-form size and type limits, files attached to the created record (PAP-339 attachment type) and scanned by `r4/data-layer/file-scanning-previews` when present',
    'Accessibility: one question per focus, error summary at the top, labels bound, keyboard and screen reader tested (PAP-156)',
    'Drafts for signed-in submitters persist 30 days; anonymous drafts stay in `localStorage` only',
  ],
  'provides': "`FormPort.define|submit|submissions`, `FormDefinition` and `form_submission` schemas, `<FormRunner/>`, builder page, `form` workflow trigger, `form.submitted` event",
  'consumes': "form view baseline (PAP-169), field types and settings panel (PAP-338, PAP-339), files (PAP-37), form adapters (PAP-233), filter builder and evaluator (PAP-166, PAP-279), i18n (PAP-27, PAP-375), record create path (PAP-342)",
  'consumed_by': f"`r4/{K}/forms-publishing`, engagement surveys and intake, commerce work-order checklists, growth landing forms (PAP-193 migrates to `FormRunner`), human task forms",
  'dod': ['A three-page intake form with logic creates a patient record and starts a workflow in the demo tenant; the builder round-trips the definition; axe clean; screenshots at 375 and 1024'],
  'tests': {
    'Unit': 'logic evaluation parity client/server over 30 rule fixtures; mapping transforms; draft expiry',
    'E2E': 'fill with a screen reader script (PAP-156), upload two files, submit, verify record and run; resume a draft after reload',
  },
  'demo': "Build a clinic intake form with a conditional allergies page, publish internally, fill it on a phone with two photo uploads, and watch the record and workflow appear.",
  'edge': ['Definition changed after a draft was saved: the runner migrates the draft by field id and shows what was dropped', 'Dataset field type converted (PAP-340) after mapping: submission fails validation visibly and the builder flags the mapping'],
  'deps': f"`r4/{K}/workflow-model` (hard), PAP-169, PAP-338, PAP-339 (hard), PAP-37, PAP-233 (hard), PAP-27, PAP-375 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Edge Case Hunter)',
 },
 {
  'key': f'r4/{K}/forms-publishing', 'title': 'Build form publishing: public routes, embeds, anti-spam, rate limits, payment step via Stripe Checkout, partial saves, notifications and submission views',
  'type': 'Build', 'tier': 'opus', 'size': 'M', 'priority': 4, 'surfaces': ['Customer', 'Staff'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': [f'r4/{K}/forms-schema-runtime', 'PAP-172', 'PAP-304', 'PAP-396', 'PAP-193', 'PAP-136'], 'blocks': [],
  'goal': "Put forms in front of the public safely: `/f/:token` public routes and a `form.js` embed (shared with PAP-193), anti-spam (Turnstile port, honeypot, timing, PAP-304 rate limits), a payment block that collects money through PAP-396 Checkout before the submission completes, partial saves with resume links, notifications to owners and submitters, and submission grids and charts as saved views.",
  'scope_in': [
    "Publishing: `form_publication` (`token`, `mode public|portal|internal`, `expires`, `maxSubmissions`, `password?`, `allowedOrigins[]`) reusing PAP-172 token semantics; `/f/:token` route on the public layout with tenant branding (PAP-75) and custom domains (PAP-431); embed script `form.js` (iframe with resize messaging, under 6 KB) replacing PAP-193's",
    "Anti-spam: `CaptchaPort` (Cloudflare Turnstile adapter, `noop` for tests), honeypot field, minimum fill time, per-IP and per-form limits (PAP-304), disposable-email heuristic; suspected spam lands in `status: spam` for review",
    "Payment block: creates a PAP-396 Checkout session (platform or connected account) for a fixed or computed amount; submission completes on the webhook; unpaid submissions expire after 24 h",
    "Notifications: kinds `form.submitted` to owners with a summary, confirmation email to submitter through PAP-370 with the receipt when paid; submission views: grid, chart and a per-form dashboard (PAP-173) auto-created",
  ],
  'scope_out': ['Survey logic and NPS (engagement)', 'Payment methods beyond Checkout'],
  'spec': [
    'Public submissions never create principals; the submitter is an `ActorRef { kind: anonymous }` with a hashed IP; PII stays in `payload` under PAP-355 rules',
    'Money never touches the API: amounts are computed server-side from the definition and the payload, then sent to Stripe; the webhook is the only completion path (PCI SAQ-A, PAP-359)',
    'Resume links are signed, single-use per save and expire with the publication; partial payloads are encrypted at rest (PAP-353) because they may hold PII before consent is complete',
    'Embeds refuse origins not on `allowedOrigins`; CSP frame-ancestors is set per publication',
    'Rate limits: 10 submissions per IP per hour by default, per-form override, 429 with retry copy in the runner',
  ],
  'provides': "`FormPort.publish`, `/f/:token`, `form.js`, `CaptchaPort`, payment block, notification kinds, auto-created submission views and dashboard",
  'consumes': "forms runtime, token semantics (PAP-172), rate limits (PAP-304), Checkout and webhooks (PAP-396), landing forms (PAP-193, superseded embed), notifications (PAP-136), email (PAP-370), branding and domains (PAP-75, PAP-431), field encryption (PAP-353)",
  'consumed_by': "growth landing pages (PAP-193), engagement surveys and booking intake, commerce order forms, migration packs",
  'dod': ['A public paid registration form completes end to end in Stripe test mode with a receipt; spam fixtures are quarantined; embed works on a Webflow test page; submission dashboard renders'],
  'tests': {
    'Unit': 'origin allow-list; amount computation; resume link signing and single use; spam scoring',
    'Integration': 'Checkout webhook completes the submission once even when delivered twice; expired unpaid submission cleanup',
    'E2E': 'public form on a phone with Turnstile in test mode; embed resize; 429 path',
  },
  'demo': "Publish a workshop registration form with a $25 fee, embed it on the demo landing page, register and pay in test mode, then open the auto-created dashboard showing registrations and revenue.",
  'edge': ['Publication expired mid-fill: submit returns `FORM_CLOSED` with the tenant\'s closing message; drafts are kept for the resume window', 'Stripe webhook late by hours: submission shows `awaiting payment` and completes when it arrives; owner notified once'],
  'deps': f"`r4/{K}/forms-schema-runtime` (hard), PAP-172, PAP-304 (hard), PAP-396 (hard: payments), PAP-193 (soft: supersedes its embed), PAP-136, PAP-370 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Security Auditor)',
 },
 {
  'key': f'r4/{K}/document-templates', 'title': 'Build document templates: template model with merge fields, conditional sections and repeating rows over datasets, a Tiptap template editor and versioning',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'medium', 'size': 'M', 'priority': 4, 'surfaces': ['Staff'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': [f'r4/{K}/workflow-model', 'PAP-142', 'PAP-235', 'PAP-395', 'PAP-389'], 'blocks': [f'r4/{K}/document-generation', f'r4/{K}/esign-core'],
  'goal': "Let tenants write proposals, contracts, letters and certificates once and fill them from data: a `DocumentTemplate` edited in the PAP-142 editor with merge fields bound to a dataset and its relations, conditional sections, repeating rows for line items, branding from PAP-235, and versions, so PAP-395 invoices stay the specialised case while everything else uses this.",
  'scope_in': [
    "`document_template` (`name`, `dataset`, `body: Tiptap JSON`, `variables`, `version`, `status`, `pageSettings`), Tiptap extensions `mergeField` (`{{ contact.name }}` with picker over dataset fields and one-hop relations), `conditionalSection` (FilterTree on the record), `repeatingTable` (over a relation or view query), `signatureField` placeholder (consumed by e-sign), `pageBreak`",
    "Editor page `/console/documents/templates/:id` with the field picker, sample-record preview (renders with a chosen record), branding preview from PAP-235 `PdfLayout`, version history and diff",
    "Expression support through the PAP-389 template language for formatting (`money`, `date`, `upper`) and computed values; locale-aware via PAP-27",
    "Template gallery seeded per business pack (PAP-427 `documents[]`): proposal, service agreement, consent, letter, certificate",
  ],
  'scope_out': ['Rendering and generation (next issue)', 'Invoice layouts (PAP-396 owns)'],
  'spec': [
    'Merge fields resolve with the generating user\'s permissions; a field the user cannot read renders as a redaction marker, and the generation report lists them',
    'Repeating tables are bounded (1,000 rows) and paginate with header repeat in print',
    'Templates are immutable per version; generated documents record `template_version`',
    'The editor validates every merge path against the dataset schema on save; a renamed or converted field (PAP-340) marks the template `needs review`',
  ],
  'provides': "`DocumentTemplatePort.define`, template schema and editor, Tiptap extensions, pack `documents[]` schema and five seed templates",
  'consumes': "editor (PAP-142), print kit and branding (PAP-235), document numbering pattern (PAP-395), template expressions (PAP-389), locale helpers (PAP-27), dataset schema (PAP-161, PAP-340)",
  'consumed_by': f"`r4/{K}/document-generation`, `r4/{K}/esign-core`, commerce (estimates, work orders), engagement (consent forms, certificates), business packs",
  'dod': ['Five seed templates render with sample records; a renamed field flags the template; editor screenshots at 1024 and 1920'],
  'tests': {
    'Unit': 'merge path validation; conditional and repeating evaluation; redaction marker for unreadable fields',
    'E2E': 'edit a template, insert a repeating table over invoice lines, preview with a record, publish a version, diff against the previous one',
  },
  'demo': "Open the proposal template, add a repeating table of quote lines and a conditional discount paragraph, preview with a real quote, publish.",
  'edge': ['Record missing a relation (no company on a contact): sections referencing it collapse cleanly and the preview lists the empty paths'],
  'deps': f"`r4/{K}/workflow-model` (soft: shares the module), PAP-142 (hard), PAP-235 (hard: layout kit; if still deferred, a minimal `PdfLayout` is built here and handed back), PAP-395, PAP-389 (soft).",
  'builder': 'Ledger', 'reviewer': 'Sentinel (Code Reviewer)',
 },
 {
  'key': f'r4/{K}/document-generation', 'title': 'Build document generation: render templates to PDF and DOCX, a generated documents library on the file entity, bulk generation jobs, attach to records and share links',
  'type': 'Build', 'tier': 'sonnet', 'effort': 'medium', 'size': 'M', 'priority': 4, 'surfaces': ['Staff', 'Customer'], 'milestone': MS[1], 'deferred': True,
  'blockedBy': [f'r4/{K}/document-templates', 'PAP-235', 'PAP-37', 'PAP-43', 'PAP-172'], 'blocks': [f'r4/{K}/esign-core'],
  'goal': "Turn a template plus a record into a file people can send: PDF through the PAP-235 `renderPdf` and DOCX through `docx` so tenants can edit offline, a generated documents library backed by the `file` entity with versions and metadata, bulk generation as a job with progress, attachment to the source record, and share links with the PAP-172 token rules.",
  'scope_in': [
    "`DocumentTemplatePort.render(templateId, recordRef, { format: 'pdf'|'docx'|'html' })` and `generate` (persisting a `generated_document` row: `template_version`, `record`, `file_id`, `format`, `hash`, `generated_by`); PDF via headless Chromium (PAP-235), DOCX via `docx` 9.x mapping the Tiptap JSON; HTML for email bodies",
    "Library page `/console/documents` (grid view on the `generated_document` dataset) with preview (PDF viewer), regenerate, download, share; record panel tab `documents` (PAP-333 slot) listing documents for a record",
    "Bulk: `documents.generateBulk(templateId, viewId)` as a PAP-43 job with progress over PAP-381, a zip download and per-record attachment; used by the `document.generate` step kind",
    "Share links `/d/:token` (PAP-172 token semantics, expiry, password) with a download audit row",
  ],
  'scope_out': ['Signing (next issue)', 'Editing generated DOCX back into templates'],
  'spec': [
    'Generation is deterministic for a given template version, record snapshot and locale; the `hash` lets e-sign prove what was signed',
    'Fonts: the print kit\'s font set plus a CJK fallback; PDF/A-2b output flag for archival templates',
    'Bulk jobs respect the tenant storage entitlement (PAP-178 `storageGb`) and stop with a clear message when exceeded',
    'Generated documents inherit the record\'s permissions for viewing; sharing outside requires `documents.share`',
  ],
  'provides': "`DocumentTemplatePort.render|generate|generateBulk`, `generated_document` dataset and library page, record tab, `/d/:token`, `document.generated` event",
  'consumes': "templates, print kit (PAP-235), files (PAP-37), jobs and progress (PAP-43, PAP-381), share tokens (PAP-172), record panel tabs (PAP-333), entitlements (PAP-178)",
  'consumed_by': f"`r4/{K}/esign-core`, step kind `document.generate`, commerce estimates and packing slips, engagement certificates, scheduled view delivery (`r4/tables/scheduled-view-delivery`)",
  'dod': ['PDF and DOCX generated for the five seed templates with identical content; bulk run over 200 records finishes under 3 minutes on staging with progress; share link audited'],
  'tests': {
    'Unit': 'Tiptap → DOCX mapping for every node type; hash stability; entitlement stop',
    'Integration': 'bulk job resumes after a worker restart without duplicates; share token expiry; record permission inheritance',
  },
  'demo': "Generate a proposal PDF from a quote, download the DOCX, run a bulk generation of 50 renewal letters from a saved view, and share one with an expiring link.",
  'edge': ['Template version retired between bulk start and finish: the job pins the version at start and finishes consistently', 'Chromium crash mid-render: the job retries the item once, then marks it failed with the error in the run log'],
  'deps': f"`r4/{K}/document-templates` (hard), PAP-235 (hard), PAP-37, PAP-43 (hard), PAP-172, PAP-333, PAP-381 (soft).",
  'builder': 'Ledger', 'reviewer': 'Sentinel (Code Reviewer)',
 },
 {
  'key': f'r4/{K}/esign-core', 'title': 'Build e-signature core: signature requests, signer identity (email OTP, portal login), fields, sequential signing, the signing ceremony UI and the sealed PDF',
  'type': 'Build', 'tier': 'opus', 'size': 'L', 'priority': 4, 'surfaces': ['Customer', 'Staff'], 'milestone': MS[2], 'deferred': True,
  'blockedBy': [f'r4/{K}/document-generation', f'r4/{K}/document-templates', 'PAP-220', 'PAP-370', 'PAP-353', 'PAP-352'], 'blocks': [f'r4/{K}/esign-audit-compliance'],
  'goal': "Let tenants get things signed inside PaperOS: a signature request over a generated document with placed fields (signature, initials, date, text, checkbox), one or more signers in parallel or sequence, signer identity by email one-time code or portal login, a signing ceremony that works on a phone, and a sealed PDF with embedded signature images and a hash, built in-house after the PAP-352 Documenso evaluation records the mode.",
  'scope_in': [
    "`signature_request` (`document_id`, `status draft|sent|partially_signed|completed|declined|expired|voided`, `signers[]` with order, `expires`, `reminders`), `signature_field` (type, page, coordinates in PDF points, signer, required), `signature_event` (viewed, otp_sent, otp_verified, signed, declined, with IP hash, user agent, timestamp)",
    "Field placement UI on the PDF preview (drag from a palette, PAP-331) or from template `signatureField` placeholders (auto-placed); request composer with message, order, expiry, reminders schedule",
    "Signing ceremony `/sign/:token`: identity step (email OTP through PAP-370 or portal session), review document, fill fields (draw, type in a script font, upload), consent checkbox to sign electronically, submit; phone-first layout; accessibility with keyboard and screen reader (PAP-156)",
    "Sealing: on completion, stamp signature images and a completion page into the PDF (`pdf-lib`), compute SHA-256, store as a new `file` version, notify all parties with the sealed copy; `signature.completed` event resumes workflows",
  ],
  'scope_out': ['Audit certificate, legal disclosures, verification page (next issue)', 'Qualified signatures, digital certificates (v0.3)', 'In-person signing on a shared device (v0.3)'],
  'spec': [
    'Tokens are single-signer, single-use per session, bound to the signer email and expire with the request; every view and action writes a `signature_event`',
    'OTP: 6 digits, 10 minutes, 5 attempts then lockout for an hour; portal signers skip OTP when their session email matches the signer',
    'The document cannot change after `sent`: the request pins `generated_document.hash`; voiding creates a new request',
    'Sequential signing notifies the next signer only after the previous completes; parallel requests seal once all sign',
    'Declines capture a reason and notify the requester; expired requests can be extended once before expiry only',
  ],
  'provides': "`SignaturePort.request|sign|status|void`, tables, field placement UI, `/sign/:token` ceremony, sealed PDF version, events `signature.requested|signed|declined|completed`",
  'consumes': "generated documents and templates, session and OTP primitives (PAP-220), email (PAP-370), encryption for signature images at rest (PAP-353), OSS mode decision (PAP-352), drag-and-drop (PAP-331), files (PAP-37)",
  'consumed_by': f"`r4/{K}/esign-audit-compliance`, step kind `signature.request`, commerce estimates and contracts, engagement consent and membership agreements, business-core quote acceptance (PAP-395 gains a signed path)",
  'dod': ['Two-signer sequential request completes on phone and desktop in the demo tenant; sealed PDF opens in three viewers with visible signatures; workflow resumes on completion; screenshots of the ceremony at 375 and 1024'],
  'tests': {
    'Unit': 'token binding and single use; OTP limits; hash pinning; sequential order',
    'Integration': 'seal idempotency when the completion job runs twice; void after partial signing; reminder schedule',
    'E2E': 'draw, type and upload signatures; decline path; screen reader ceremony (PAP-156)',
  },
  'demo': "Send a service agreement to two signers; sign the first on a phone with an OTP, the second from the portal; open the sealed PDF and watch the workflow create the project.",
  'edge': ['Signer email bounces (PAP-370 suppression): requester notified immediately with a fix action; the request stays `sent`', 'Same person is two signers (owner and witness): each role gets its own token and field set'],
  'deps': f"`r4/{K}/document-generation` and `r4/{K}/document-templates` (hard), PAP-220, PAP-370, PAP-353 (hard), PAP-352 (hard: mode decision), PAP-331 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Security Auditor)',
 },
 {
  'key': f'r4/{K}/esign-audit-compliance', 'title': 'Add the e-signature audit certificate, tamper-evident hash chain, public verification page, legal disclosures (ESIGN, eIDAS simple), reminders and retention',
  'type': 'Build', 'tier': 'opus', 'size': 'M', 'priority': 4, 'surfaces': ['Customer', 'Staff'], 'milestone': MS[2], 'deferred': True,
  'blockedBy': [f'r4/{K}/esign-core', 'PAP-393', 'PAP-355', 'PAP-221', 'PAP-136'], 'blocks': [],
  'goal': "Make signatures defensible: a completion certificate appended to the sealed PDF listing every event with hashes, a per-tenant hash chain over signature events (PAP-393 pattern) verified nightly, a public verification page where anyone with the document can confirm it is unaltered, the consumer disclosures ESIGN and eIDAS simple electronic signatures expect, reminder and expiry jobs, and retention aligned with PAP-355.",
  'scope_in': [
    "Certificate page generator (PAP-235 `PdfLayout`): request id, document hash before and after sealing, per-signer identity method, events with timestamps (UTC and signer timezone), IP hash, user agent, consent text version; appended as the final pages and stored separately as `signature_certificate`",
    "Hash chain: `signature_event.prev_hash` per tenant, `pnpm esign:verify` and nightly job reusing the PAP-393 verifier; `/verify/:hash` public page: upload or paste a hash → status, signer count, completion time (no PII)",
    "Disclosures: consent-to-electronic-records text with versioning and tenant-editable jurisdiction addenda (PAP-221 legal pages), shown before signing and recorded per signer; paper-copy request path",
    "Jobs: reminders per the request schedule (PAP-136 kind `signature.reminder`), expiry, retention (certificates immutable 7 years by default per PAP-355 profile; documents follow the record\'s retention)",
  ],
  'scope_out': ['Qualified/advanced signatures with certificates (v0.3)', 'Legal advice: the disclosure texts are templates Justin approves (Needs Justin item)'],
  'spec': [
    'The certificate is generated from stored events only, never from request-time memory; regenerating it yields byte-identical output for the same events',
    'Verification page rate-limited (PAP-304) and returns the same shape for unknown and known hashes with a timing guard',
    'Chain verification failure raises an S0 security event (PAP-356) and locks new requests for the tenant until reviewed',
    'Disclosure acceptance stores text version, timestamp, signer token and locale; a changed text creates a new version, never edits',
  ],
  'provides': "certificate generator, `signature_certificate`, hash chain and verifier, `/verify/:hash`, disclosure versions, reminder and expiry jobs",
  'consumes': "e-sign core, hash chain and verifier pattern (PAP-393), retention (PAP-355), legal pages (PAP-221), notifications (PAP-136), print kit (PAP-235), rate limits (PAP-304), security events (PAP-356)",
  'consumed_by': "commerce and engagement signed documents, platform-ops compliance evidence (signature integrity as a control)",
  'dod': ['Certificate appended and verifiable for the demo agreements; a tampered PDF fails verification; nightly chain verification green; disclosure texts filed to Needs Justin for approval'],
  'tests': {
    'Unit': 'certificate determinism; chain hash; disclosure versioning',
    'Integration': 'tamper a stored file byte → verification fails and S0 path fires; reminders honour quiet hours (PAP-324)',
  },
  'demo': "Open a completed agreement, show the certificate pages, paste its hash into `/verify`, then alter one byte in a copy and show the failure.",
  'edge': ['Signer timezone unknown (no portal account): certificate shows UTC only and says so', 'Tenant purge (PAP-355) with signed documents under legal retention: documents move to the archive tier, not deleted, per the retention profile'],
  'deps': f"`r4/{K}/esign-core` (hard), PAP-393 (hard: pattern), PAP-355, PAP-221 (soft), PAP-136, PAP-235 (soft).",
  'builder': 'Nova', 'reviewer': 'Sentinel (Security Auditor)',
 },
]

TRIO = trio({
    'key': K, 'lead': 'Nova', 'owner': 'Nova', 'kind': 'runtime', 'swapRisk': 'high', 'impl': 'packages/workflows, apps/web/src/workflows',
    'milestones': MS, 'impl_keys': [f'r4/{K}/approvals-framework', f'r4/{K}/run-engine', f'r4/{K}/forms-schema-runtime', f'r4/{K}/document-generation'],
    'publish_blockedBy': [f'r4/{K}/workflow-model'],
    'ports': ['`WorkflowPort` (`define`, `publish`, `start`, `signal`, `cancel`, `listRuns`, `replay`) with `WorkflowDefinition`, `StepDefinition`, `WorkflowRun`, `RunStep`', '`StepKindRegistry` (`defineStepKind`) and the twelve step kind ids', '`ApprovalPort` (`request`, `decide`, `delegate`, `policies`) with `ApprovalPolicy`, `ApprovalRequest`, `ApprovalDecision`', '`TaskPort` (`assign`, `complete`, `snooze`, `inbox`) with `Task`', '`FormPort` (`define`, `publish`, `submit`, `submissions`) with `FormDefinition`, `FormSubmission`, `CaptchaPort`', '`DocumentTemplatePort` (`define`, `render`, `generate`, `generateBulk`) with `DocumentTemplate`, `GeneratedDocument`', '`SignaturePort` (`request`, `sign`, `status`, `void`, `certificate`, `verify`) with `SignatureRequest`, `SignatureField`, `SignatureEvent`', 'slots `record.panel.tabs.workflows`, `record.panel.tabs.documents`, `shell.settings.sections.workflows`, `portal.forms`, `dashboard.blocks.tasks`'],
    'events': ['workflow.run.started', 'workflow.run.completed', 'workflow.run.failed', 'workflow.task.created', 'workflow.task.completed', 'approval.requested', 'approval.approved', 'approval.rejected', 'approval.expired', 'form.submitted', 'document.generated', 'signature.requested', 'signature.signed', 'signature.completed', 'signature.declined'],
    'requires': ['`@paperos/contract-data-layer` ^0.1 (jobs, outbox, idempotency, files, audit, email)', '`@paperos/contract-tables` ^0.1 (`FilterTree`, `FieldDef`, action catalogue, views)', '`@paperos/contract-identity` ^0.1 (`Principal`, `can`, audiences)', '`@paperos/contract-collab` ^0.1 (notification kinds, comments, canvas node types)', '`@paperos/contract-business-core` ^0.1 (Checkout, `Money`, document numbering; optional)', '`@paperos/contract-design-system` ^0.1 (print kit, form controls)', '`@paperos/contract-assistant` ^0.1 (`ActionPort`; optional, for the `agent` step)'],
    'fixtures': 'three workflow definitions (expense approval, proposal-to-project, patient intake) with run traces, twelve step configs (valid and invalid), four approval policies, two forms with logic and a paid submission, three document templates with sample records, two signature requests across the status machine',
    'consumers': 'pm-linear (PAP-94 decisions), growth (PAP-401, PAP-408, PAP-193), business-core (PAP-185, PAP-400, PAP-395), commerce (purchasing, work orders, estimates), engagement (intake, surveys, consent), migration (pack content)',
})

ISSUES = [TRIO[0]] + ISSUES + TRIO[1:]
