# Pending issues (specified, not yet in Linear)

156 fully specified issues (Goal, Scope, Spec, Interface contract, Definition of done, Test plan, Demo, Size) that Linear refused with `USAGE_LIMIT_EXCEEDED`: the workspace is on the Free plan and team PAP holds 275 active issues. They wait on **PAP-91 / NJ-1** (upgrade the Linear workspace plan; Basic is enough). Until then the live plan runs on the 275 issues that exist and live issues cite these as `[project/key]`.

* **153 to create** once the plan is upgraded (`status: pending`).
* **3 folded** into live issues as work packages by round-2 FIX-5 (`status: folded`, `into:` names the live issue). Kept here for reference only; the create scripts skip them (`plan/round2/folded-into-live-issues.json`).
* Entries merged into another pending spec by FIX-6 were already removed from the source files; `plan/round2/pending-merged.json` lists them.

Each file has YAML frontmatter (key, title, project, parent, phase, type, priority, size, surfaces, milestone, intended state, blockedBy/blocks by key or PAP id, source script, the Linear "Round 2 pending issues" document that holds the same text, status) and the full description. `index.json` is the same metadata as one array. `{{project/key}}` references in the source text are resolved to PAP ids where the issue exists and left as `` `project/key` `` where it is itself pending.

## Create order (from PAP-91, Plan B)

On `/approve` of NJ-1 the session that reads the reply creates, in this order and nothing else first:

1. `agents/runtime-sandbox` (P0 safety) via `tools/linear/round2/agent2/create_new.py`
2. PAP-96's three children (`pm-linear/orchestrator/*`) via the same script
3. PAP-104's four children (`agents/roster-v1/*`) via the same script
4. `agents/session-observability` via the same script
5. then the rest by phase with `round2/agent3/create_issues.py`, `agent4/create_issues.py`, `agent5/create_issues.py`, `agent6/create_issues.py`, `apply_golden_path.py` and `create_contracts.py`, adding the `blocks` relations each document lists.

Run them only after FIX-6 (duplicate pending entries) is finished, which it is; every script is idempotent on title-in-project and skips the folded keys. Then move PAP-91 back to Ready for Claude. On `/reject`, the pending documents stay the spec of record and the builder of each parent builds its work packages on branches `<parent>/wp<n>-<slug>`.

## Index


### Universal App Shell & Repo Template (`app-shell`, 11)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`contracts/package-boundaries`](app-shell/contracts-package-boundaries.md) | Specify the monorepo package boundary map: package ownership table, allowed dependency graph, `packages/core` sub-folder owners, dependency-cruiser lint in Gate 1 and the `packages/pm` move |  | pending |
| [`gap/app-shell/client-errors`](app-shell/app-shell-client-errors.md) | Define the client error handling and crash reporting contract: error boundaries, error code catalogue, user-facing copy, browser and Tauri crash reports into observability |  | pending |
| [`gap/app-shell/code-signing`](app-shell/app-shell-code-signing.md) | Set up desktop and mobile code signing and notarisation (Apple Developer, Windows certificate, Android keystore) with one Needs Justin credential ask |  | pending |
| [`gap/app-shell/custom-domains`](app-shell/app-shell-custom-domains.md) | Add per-tenant custom domains: on-demand TLS in Caddy, host-based tenant resolution in api-layer, DNS verification UI |  | pending |
| [`gap/app-shell/onboarding-wizard`](app-shell/app-shell-onboarding-wizard.md) | Build the first-run tenant onboarding wizard: create organisation, choose business template, invite team, connect billing, land on a seeded dashboard |  | pending |
| [`gap/app-shell/runtime-flags`](app-shell/app-shell-runtime-flags.md) | Build runtime feature flags: per-tenant and per-audience flags with kill switches, segment targeting and page-spec `flags:` guards |  | pending |
| [`gp/app-shell/acceptance`](app-shell/gp-app-shell-acceptance.md) | Build the golden path acceptance test: nightly CI runs three canned ideas from paragraph to preview URL, asserts gates 1 to 4 and under ten minutes, publishes `golden-path.json`, badge and friction issues |  | pending |
| [`gp/app-shell/driver`](app-shell/gp-app-shell-driver.md) | Build the golden path driver: `paperos create --idea` runs interview, app spec, generation, seed, push, provisioning and preview in one command with checkpoint stamps |  | pending |
| [`gp/app-shell/provisioning`](app-shell/gp-app-shell-provisioning.md) | Build golden path provisioning: parallel idempotent steps, warm pools for preview slots, databases and mirror repos, `--resume` and per-step time budgets in `paperos create` |  | pending |
| [`gp/app-shell/starter-surfaces`](app-shell/gp-app-shell-starter-surfaces.md) | Build the default surfaces starter kit: customer portal and staff console page specs, a seeded demo tenant per audience and a first-run checklist for every generated app |  | pending |
| [`gp/app-shell/upgrade`](app-shell/gp-app-shell-upgrade.md) | Build `paperos upgrade`: apply template updates to generated apps with three-way merge, codemods, regeneration and an upgrade pull request |  | pending |

### Data Layer & Database (`data-layer`, 8)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`contracts/domain-events`](data-layer/contracts-domain-events.md) | Specify the domain event contract: envelope, topic catalogue, `defineTopic` registry, transactional outbox and subscriber delivery (`packages/core/events`) |  | pending |
| [`contracts/idempotency-rate-limits`](data-layer/contracts-idempotency-rate-limits.md) | Specify and build request idempotency and rate limiting: `Idempotency-Key` header, `idempotency_keys` table with replay semantics, `POST /api/v1/rpc/batch`, Postgres-backed token buckets per actor, API key and IP |  | pending |
| [`contracts/shared-value-types`](data-layer/contracts-shared-value-types.md) | Specify shared value types and wire encodings in `packages/core/types`: `Money` (bigint minor units, string on the wire), `ActorRef`, `EntityRef`, UUIDv7 ids, timestamps, signed cursors and the `ApiError` body |  | pending |
| [`gap/data-layer/email-package`](data-layer/data-layer-email-package.md) | Build the transactional email package (`packages/email`): React Email templates, provider adapter, sandbox allowlist mode, suppression list, DKIM/SPF/DMARC check, Mailpit in dev |  | pending |
| [`gap/data-layer/tenant-lifecycle`](data-layer/data-layer-tenant-lifecycle.md) | Build the tenant lifecycle: tenant states, deletion request and cancel flow with grace period, archive metadata, per-tenant storage and row quotas (the purge job itself is `security/retention-pii`) |  | pending |
| [`security/field-encryption`](data-layer/security-field-encryption.md) | Build server-side field encryption for stored secrets (OAuth tokens, SCIM and webhook secrets, connector credentials, TOTP seeds) with envelope keys, key rotation and a leak scanner |  | pending |
| [`security/platform-dr`](data-layer/security-platform-dr.md) | Add object-storage, Yjs, orchestrator and sops-key backups and a monthly platform-wide disaster-recovery drill restoring everything on a fresh host against RPO 1 h and RTO 4 h |  | pending |
| [`security/retention-pii`](data-layer/security-retention-pii.md) | Enforce data retention, PII classification and tenant hard-purge: `pii` column annotations driving redaction and OTel filters, per-table retention jobs, and the export-first purge after the grace period |  | pending |

### Version Control & Forge Independence (`forge`, 2)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`gap/forge/non-linux-runners`](forge/forge-non-linux-runners.md) | Provision non-Linux CI capacity: hosted macOS runners (Xcode, VoiceOver) and a Windows VM runner (NVDA, MSI signing) with cost caps and secrets |  | pending |
| [`security/supply-chain`](forge/security-supply-chain.md) | Add supply-chain integrity: lockfile and minimum-release-age policy, pinned actions by digest, SLSA provenance attestations and cosign signatures for container images and Tauri artifacts, verified before deploy and update |  | pending |

### Identity, Roles & Audiences (`identity`, 1)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`security/founder-break-glass`](identity/security-founder-break-glass.md) | Harden the founder root of trust: hardware-key MFA on every external account, an offline recovery age key with escrow, a one-command revoke-all, and the break-glass runbook filed as a single Needs Justin checklist |  | pending |

### Quality Pipeline (`quality`, 2)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`security/dast`](quality/security-dast.md) | Add dynamic security testing: nightly ZAP baseline and authenticated scan of staging plus a security regression suite (CSRF, IDOR across tenants, headers, rate limits, upload abuse, webhook replay) that blocks the release candidate |  | pending |
| [`security/security-telemetry`](quality/security-security-telemetry.md) | Build security telemetry and alerting: auth anomalies, RLS denials, agent policy and egress denials, canary hits, webhook signature failures and backup age routed to Linear with a weekly security digest |  | pending |

### Project Management & Claude Pipeline (`pm-linear`, 9)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`pm-linear/inbound-triage`](pm-linear/inbound-triage.md) | Build inbound triage: convert Justin's freeform issues and comments into contract-valid issues via the Decomposer sub-agent, wired to the Triage view |  | pending |
| [`pm-linear/linear-sync/conflicts`](pm-linear/linear-sync-conflicts.md) | Linear sync: conflict rule (Linear wins), sync status page and runbook | PAP-101 | pending |
| [`pm-linear/linear-sync/inbound`](pm-linear/linear-sync-inbound.md) | Linear sync: backfill and inbound webhook upsert into pm_* tables | PAP-101 | pending |
| [`pm-linear/linear-sync/outbound`](pm-linear/linear-sync-outbound.md) | Linear sync: transactional outbox, outbound worker and loop prevention | PAP-101 | pending |
| [`pm-linear/orchestrator/claims`](pm-linear/orchestrator-claims.md) | Orchestrator: Linear polling, atomic claim and state transitions | PAP-96 | pending |
| [`pm-linear/orchestrator/deploy`](pm-linear/orchestrator-deploy.md) | Orchestrator: deployment on Coolify, `/status` endpoint and runbook | PAP-96 | pending |
| [`pm-linear/orchestrator/sessions`](pm-linear/orchestrator-sessions.md) | Orchestrator: worktree lifecycle and Claude session launch | PAP-96 | pending |
| [`pm-linear/weekly-reaudit`](pm-linear/weekly-reaudit.md) | Run a weekly plan re-audit: snapshot Linear, detect dependency drift, cycles, stale In Progress sessions, issues without specs; post the report to Linear |  | pending |
| [`security/credential-broker`](pm-linear/security-credential-broker.md) | Build the credential broker: sessions hold no raw secrets; an egress proxy injects short-lived per-session tokens (GitHub App, Forgejo, Linear proxy, PaperOS agent keys, Anthropic) with usage logs and one-command revoke-all |  | pending |

### Agent Characters & Orgs (`agents`, 11)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`agents/eval-harness/judge`](agents/eval-harness-judge.md) | Eval harness: LLM judge, trend, regression issues, nightly schedule and report page | PAP-110 | pending |
| [`agents/eval-harness/runner`](agents/eval-harness-runner.md) | Eval harness: task format, SDK runner, deterministic graders and results table | PAP-110 | pending |
| [`agents/eval-harness/tasks`](agents/eval-harness-tasks.md) | Eval harness: golden task set (three per lead, one per sub) with fixture repos and answer keys | PAP-110 | pending |
| [`agents/roster-v1/build`](agents/roster-v1-build.md) | Roster: build `.claude/agents` generation, CI drift check and smoke tasks per lead | PAP-104 | pending |
| [`agents/roster-v1/lead-prompts`](agents/roster-v1-lead-prompts.md) | Roster: write the nine lead system prompts with shared fragments | PAP-104 | pending |
| [`agents/roster-v1/sub-prompts`](agents/roster-v1-sub-prompts.md) | Roster: write the 28 sub-character prompts and delegation descriptions | PAP-104 | pending |
| [`agents/roster-v1/yaml`](agents/roster-v1-yaml.md) | Roster: convert the plan.json roster to 37 validated character YAML files | PAP-104 | pending |
| [`agents/runtime-sandbox`](agents/runtime-sandbox.md) | Build the agent runtime sandbox: per-session container, worktree mount, CPU/RAM/time limits and network isolation with the credential broker's egress proxy as the only route |  | pending |
| [`agents/session-observability`](agents/session-observability.md) | Add agent session observability: heartbeats, stuck-session detection, per-session OTel spans and a `/status` contract shared by the org chart, board cards and cost controls |  | pending |
| [`security/agent-deny-list`](agents/security-agent-deny-list.md) | Define and enforce the agent destructive-action deny list: policy file, PreToolUse hook, MCP destructive-scope interception with Needs Justin escalation, and server-side backstops |  | pending |
| [`security/prompt-injection`](agents/security-prompt-injection.md) | Build prompt-injection defences for agent sessions: trust tiers for issues, comments and PRs, untrusted-content wrapping, actor-verified instructions, canary tokens and an injection eval suite |  | pending |

### Spec Builder (`spec-builder`, 13)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`gp/spec-builder/app-interview`](spec-builder/gp-spec-builder-app-interview.md) | Write the app interview skill: one paragraph idea to `app.spec.yaml` (business profile, audiences, entities, navigation, modules) in at most six questions with `--yes` defaults |  | pending |
| [`gp/spec-builder/entity-pages`](spec-builder/gp-spec-builder-entity-pages.md) | Build entity-derived page specs: `pnpm spec gen:entity-pages` derives list, detail, form and settings pages per entity and audience with view specs, comment anchors and access rules |  | pending |
| [`gp/spec-builder/gen-pipeline`](spec-builder/gp-spec-builder-gen-pipeline.md) | Build `paperos gen`: the whole-app generation pipeline that runs every generator in dependency order with a manifest, incremental cache, deterministic output and a `--check` drift mode |  | pending |
| [`spec-builder/data-section/example`](spec-builder/data-section-example.md) | Data section: `customer-invoices` end to end with live sync, second-context and offline tests | PAP-119 | pending |
| [`spec-builder/data-section/generator`](spec-builder/data-section-generator.md) | Data section: typed hook generator for server, live and local sync modes | PAP-119 | pending |
| [`spec-builder/data-section/schema`](spec-builder/data-section-schema.md) | Data section: Zod schema, shared FilterTree import and validator rules | PAP-119 | pending |
| [`spec-builder/layout-codegen/examples`](spec-builder/layout-codegen-examples.md) | Layout codegen: generate the three example specs, screenshot seven widths and pass conformance with zero manual edits | PAP-120 | pending |
| [`spec-builder/layout-codegen/templates`](spec-builder/layout-codegen-templates.md) | Layout codegen: Printer, route and view templates, two-file ownership and determinism | PAP-120 | pending |
| [`spec-builder/layout-codegen/wiring`](spec-builder/layout-codegen-wiring.md) | Layout codegen: state switch, layout slot mapping, action binding and search-param schema | PAP-120 | pending |
| [`spec-builder/spec-editor-ui/form`](spec-builder/spec-editor-ui-form.md) | Spec editor: form view, component tree editor and two-way sync with YAML preserving comments | PAP-124 | pending |
| [`spec-builder/spec-editor-ui/preview`](spec-builder/spec-editor-ui-preview.md) | Spec editor: live preview at selectable widths, flow-graph tab, keyboard shortcuts and accessibility polish | PAP-124 | pending |
| [`spec-builder/spec-editor-ui/yaml`](spec-builder/spec-editor-ui-yaml.md) | Spec editor: spec list, CodeMirror YAML editor with worker validation and save-to-PR flow | PAP-124 | pending |
| [`spec-builder/spec-i18n`](spec-builder/spec-i18n.md) | Add spec-level internationalisation: message IDs for spec copy fields, extraction into catalogs, pseudo-locale validation rule |  | pending |

### In-App Collaboration & Knowledge (`collab`, 11)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`collab/canvas/filters-export-perf`](collab/canvas-filters-export-perf.md) | Filters, deep links, export and 300-node performance run | PAP-132 | pending |
| [`collab/canvas/nodes-edges-loader`](collab/canvas-nodes-edges-loader.md) | Canvas node and edge types with graph loader | PAP-132 | pending |
| [`collab/canvas/yjs-overlay`](collab/canvas-yjs-overlay.md) | Collaborative overlay: notes, regions, overrides in Yjs | PAP-132 | pending |
| [`collab/comments/live-deeplinks-linear`](collab/comments-live-deeplinks-linear.md) | Live updates, deep links and Linear escalation | PAP-131 | pending |
| [`collab/comments/panel-pins-composer`](collab/comments-panel-pins-composer.md) | Comment panel, pins and composer UI | PAP-131 | pending |
| [`collab/comments/schema-rls-rpc`](collab/comments-schema-rls-rpc.md) | Comment schema, anchors, RLS and oRPC procedures | PAP-131 | pending |
| [`collab/in-app-help`](collab/in-app-help.md) | Add contextual in-app help: help panel bound to page spec `purpose` and docs deep links, first-visit product tour, keyboard hint overlay |  | pending |
| [`collab/notifications/digests-quiet-hours`](collab/notifications-digests-quiet-hours.md) | Digests, quiet hours and burst collapse | PAP-136 | pending |
| [`collab/notifications/inbox-preferences`](collab/notifications-inbox-preferences.md) | Inbox UI, bell badge and preferences page | PAP-136 | pending |
| [`collab/notifications/slack-channel`](collab/notifications-slack-channel.md) | Slack channel and tenant Slack configuration | PAP-136 | pending |
| [`collab/runtime-docs-store`](collab/runtime-docs-store.md) | Build a runtime docs store for tenant-authored documents: Yjs-backed pages in Postgres with the same routes, search registration and comment anchors as repo MDX |  | pending |

### Multiplayer & Realtime (`realtime`, 4)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`realtime/push-transport`](realtime/push-transport.md) | Build the push transport: server-to-client notification and job-progress channel (Electric shape or SSE) plus Web Push and Tauri mobile push (APNs/FCM) |  | pending |
| [`realtime/record-sync/live-hooks-registry`](realtime/record-sync-live-hooks-registry.md) | Live record hooks and shape registry additions | PAP-143 | pending |
| [`realtime/record-sync/reconciler`](realtime/record-sync-reconciler.md) | Reconciler for optimistic writes and conflict events | PAP-143 | pending |
| [`realtime/record-sync/resubscribe-lag`](realtime/record-sync-resubscribe-lag.md) | Permission-driven resubscribe and lag measurement | PAP-143 | pending |

### Multi-Input Control & Accessibility (`input`, 6)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`input/commands/agent-endpoint-defaults`](input/commands-agent-endpoint-defaults.md) | Agent execution endpoint, telemetry and default commands | PAP-151 | pending |
| [`input/commands/palette-help-ui`](input/commands-palette-help-ui.md) | Command palette and help sheet UI | PAP-151 | pending |
| [`input/commands/registry-core`](input/commands-registry-core.md) | Command registry core, scoping and chord matcher | PAP-151 | pending |
| [`input/dnd/kanban-grid-dropzone-crosswindow`](input/dnd-kanban-grid-dropzone-crosswindow.md) | KanbanDnd, SortableGrid, DropZone and cross-window drag | PAP-155 | pending |
| [`input/dnd/keyboard-announcements`](input/dnd-keyboard-announcements.md) | Keyboard alternative, announcements and focus restore | PAP-155 | pending |
| [`input/dnd/sensors-sortable-list`](input/dnd-sensors-sortable-list.md) | dnd-kit sensors on the input abstraction and SortableList | PAP-155 | pending |

### Table & Views Engine (`tables`, 24)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`gap/tables/bulk-trash`](tables/tables-bulk-trash.md) | Build bulk operations, trash and restore: multi-row edit and delete with server batching, soft-delete trash with 30-day restore, undo toast |  | pending |
| [`gap/tables/record-detail`](tables/tables-record-detail.md) | Build record-level features shared by every module: record detail page and panel routing, activity timeline, attachments tab, per-record comments and field history with undo |  | pending |
| [`gap/tables/schema-editor`](tables/tables-schema-editor.md) | Build the custom dataset schema editor: create tables and fields in-app, reorder, field type conversion with a lossiness report and background backfill |  | pending |
| [`tables/automations/actions`](tables/automations-actions.md) | Action catalogue with scope classes, template expressions, connector.call, agent.run, delay and branch | PAP-174 | pending |
| [`tables/automations/builder-log-templates`](tables/automations-builder-log-templates.md) | Automation builder page, test run, run log with replay, five starter templates and import hooks | PAP-174 | pending |
| [`tables/automations/model-triggers`](tables/automations-model-triggers.md) | Automation schema, trigger sources and the run runtime with idempotency, loop guard, limits and circuit breaker | PAP-174 | pending |
| [`tables/compiler/api-hook-bench`](tables/compiler-api-hook-bench.md) | oRPC procedures, useViewQuery hook and the 100k-row benchmark | PAP-163 | pending |
| [`tables/compiler/core`](tables/compiler-core.md) | Compiler core: dataset resolution, per-type filter ops, sorts and signed keyset cursors | PAP-163 | pending |
| [`tables/compiler/groups-shapes`](tables/compiler-groups-shapes.md) | Groups, aggregates and Electric shape eligibility | PAP-163 | pending |
| [`tables/dashboard/blocks-crossfilter`](tables/dashboard-blocks-crossfilter.md) | Block kinds, cross-filter bus, filter bar, params and deep links | PAP-173 | pending |
| [`tables/dashboard/model-grid`](tables/dashboard-model-grid.md) | Dashboard tables, layout engine, breakpoint layouts and drag or resize with keyboard moves | PAP-173 | pending |
| [`tables/dashboard/print-perf-spec`](tables/dashboard-print-perf-spec.md) | Lazy loading, error boundaries, print route, page-spec hook and permission tiles | PAP-173 | pending |
| [`tables/fields/choice-people-attachment`](tables/fields-choice-people-attachment.md) | Choice, people and attachment types (select, multiSelect, user, attachment) with FieldSettingsPanel | PAP-164 | pending |
| [`tables/fields/framework-primitives`](tables/fields-framework-primitives.md) | Field type framework and primitive types (text, number, currency, percent, date, checkbox, rating, url, email, phone) | PAP-164 | pending |
| [`tables/fields/relational-computed`](tables/fields-relational-computed.md) | Relational and computed types (relation, lookup, rollup, formula storage) and convertFieldType with lossiness report | PAP-164 | pending |
| [`tables/formula/evaluator-editor`](tables/formula-evaluator-editor.md) | TypeScript evaluator with function implementations and the CodeMirror formula editor | PAP-171 | pending |
| [`tables/formula/parser-typecheck`](tables/formula-parser-typecheck.md) | Lexer, Pratt parser, AST, type checker and the defineFunction catalogue | PAP-171 | pending |
| [`tables/formula/sql-cache`](tables/formula-sql-cache.md) | SQL compiler, formula_cache fallback job and the dependency graph | PAP-171 | pending |
| [`tables/grid/columns-groups-panel`](tables/grid-columns-groups-panel.md) | Column operations, grouping headers, aggregate footer and RecordPanel | PAP-165 | pending |
| [`tables/grid/core`](tables/grid-core.md) | Grid core: virtualisation, data binding, selection model and keyboard navigation | PAP-165 | pending |
| [`tables/grid/editing-clipboard-bulk`](tables/grid-editing-clipboard-bulk.md) | Inline editing with optimistic commit, TSV clipboard ranges and the bulk actions bar | PAP-165 | pending |
| [`tables/time/engine-calendar`](tables/time-engine-calendar.md) | TimeScale engine, range compilation, overlap packing and the calendar view (month, week, day, agenda) | PAP-168 | pending |
| [`tables/time/gantt`](tables/time-gantt.md) | Gantt view: frozen left grid, dependency arrows, critical path, progress and working days | PAP-168 | pending |
| [`tables/time/timeline`](tables/time-timeline.md) | Timeline view: two-axis virtualised canvas, lanes, zoom levels and bar editing | PAP-168 | pending |

### Business Core: Payments, Finance & Payroll (`business-core`, 12)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`business-core/invoicing/model-statemachine`](business-core/invoicing-model-statemachine.md) | Document model, lines, sequences, server-side totals, state machine, quote conversion, void and credit notes | PAP-180 | pending |
| [`business-core/invoicing/pdf-paypage`](business-core/invoicing-pdf-paypage.md) | Branded PDF rendering, public /pay and /doc pages, Stripe Checkout on platform or connected account, receipts | PAP-180 | pending |
| [`business-core/invoicing/postings-portal-emails`](business-core/invoicing-postings-portal-emails.md) | Posting rules invoice.*, manual payments, reminders job, customer portal invoice list and email templates | PAP-180 | pending |
| [`business-core/ledger/hashchain-reversal-close`](business-core/ledger-hashchain-reversal-close.md) | Hash chain with nightly verification, ledger.reverse and the period close and lock workflow | PAP-179 | pending |
| [`business-core/ledger/journal-constraints`](business-core/ledger-journal-constraints.md) | Journal tables, balance trigger, immutability trigger, gapless numbering and account balances | PAP-179 | pending |
| [`business-core/ledger/rules-ui-trialbalance`](business-core/ledger-rules-ui-trialbalance.md) | Posting rule registry with the first five rules, /finance/journal UI, trial balance and rebuildBalances | PAP-179 | pending |
| [`business-core/payroll/adapter-contract`](business-core/payroll-adapter-contract.md) | Finalised PayrollProvider interface, first adapter with idempotency keys, webhook route and the adapter contract test suite | PAP-184 | pending |
| [`business-core/payroll/onboarding-sync`](business-core/payroll-onboarding-sync.md) | Payroll tables, company and employee onboarding via provider links, employee sync from fin_employee and status polling | PAP-184 | pending |
| [`business-core/payroll/run-approve-post`](business-core/payroll-run-approve-post.md) | Payroll run flow, typed-total approval, webhook status transitions, ledger posting and the paystub portal page | PAP-184 | pending |
| [`gap/business-core/recurring-dunning`](business-core/business-core-recurring-dunning.md) | Build recurring tenant invoices and dunning: schedules, automatic reminders, late fees, payment retry for tenant-to-customer billing |  | folded into PAP-180 |
| [`gap/business-core/usage-metering`](business-core/business-core-usage-metering.md) | Build usage metering and metered billing: usage events (agent sessions, storage, seats, API calls) aggregated per tenant, Stripe usage records, limit warnings |  | pending |
| [`security/pci-posture`](business-core/security-pci-posture.md) | Document and enforce the PCI SAQ-A posture: Stripe-hosted card entry only, a Semgrep rule against card-data fields, restricted Stripe keys per service, live-key custody through Needs Justin, and the quarterly SAQ-A checklist |  | pending |

### Growth: Marketing, Outreach & CRM (`growth`, 13)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`gap/growth/consent-centre`](growth/growth-consent-centre.md) | Build the consent and marketing compliance centre: preference page, unsubscribe centre, double opt-in, suppression list shared by outreach, notifications and forms, GDPR/CAN-SPAM/TCPA rules |  | folded into PAP-187 |
| [`growth/outreach/compliance-warmup-replies`](growth/outreach-compliance-warmup-replies.md) | Consent and suppression checks, quiet hours, unsubscribe and STOP handling, warmup stages, bounce handling and reply detection | PAP-191 | pending |
| [`growth/outreach/model-worker`](growth/outreach-model-worker.md) | Outreach schema, provider interface with Resend and Twilio adapters, scheduler worker, template rendering and idempotency | PAP-191 | pending |
| [`growth/outreach/ui`](growth/outreach-ui.md) | Sequence builder, template editor with preview and test send, enrolments grid and domain setup wizard | PAP-191 | pending |
| [`growth/referral/codes-attribution`](growth/referral-codes-attribution.md) | Referral programs, codes, /r/{code} route, attribution window and the qualification worker | PAP-196 | pending |
| [`growth/referral/portal-console-ui`](growth/referral-portal-console-ui.md) | Portal referral page, console program and referral grids and the rewards approval queue | PAP-196 | pending |
| [`growth/referral/rewards-payouts-ledger`](growth/referral-rewards-payouts-ledger.md) | Reward rules, fraud rules, approval, Stripe Connect transfers, ledger postings and monthly statements | PAP-196 | pending |
| [`growth/social/adapter-mock-x`](growth/social-adapter-mock-x.md) | Adapter interface, mock adapter, X API v2 adapter and the pg-boss publishing worker | PAP-190 | pending |
| [`growth/social/adapters-review-gated`](growth/social-adapters-review-gated.md) | LinkedIn, Instagram, TikTok and YouTube adapters in dryRun with payload snapshots, OAuth connect flows and re-auth banners | PAP-190 | pending |
| [`growth/social/model-queue-calendar`](growth/social-model-queue-calendar.md) | Social schema, approval state machine, composer with per-platform variants, approval queue and calendar | PAP-190 | pending |
| [`growth/support/chat-notes`](growth/support-chat-notes.md) | Portal SupportChat widget with live sync and presence, unauthenticated email capture and internal notes on comment threads | PAP-197 | pending |
| [`growth/support/console-ui`](growth/support-console-ui.md) | Three-pane inbox on a saved list view, conversation view, contact sidebar, assignment, snooze, macros, shortcuts and metrics | PAP-197 | pending |
| [`growth/support/email-threading`](growth/support-email-threading.md) | Support schema, inbound email parsing, threading heuristics, HTML sanitising, contact matching and outbound replies | PAP-197 | pending |

### Migration & Import Tools (`migration`, 20)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`child/PAP-199/0`](migration/child-pap-199-0.md) | Connector interface, mapping model and import engine (`SourceConnector`, `import_mapping`, batching, resumability, fixture connector) | PAP-199 | pending |
| [`child/PAP-199/1`](migration/child-pap-199-1.md) | Dry run, commit and rollback semantics: transaction-rolled dry run, `import_run_item` before-state, exact rollback with conflict listing | PAP-199 | pending |
| [`child/PAP-199/2`](migration/child-pap-199-2.md) | Type inference, mapping wizard UI and run history with per-item drill-down and rollback button | PAP-199 | pending |
| [`child/PAP-202/0`](migration/child-pap-202-0.md) | Airtable connector: OAuth and PAT auth, metadata discovery, record streaming with 5 rps token bucket and expiring-attachment fetch | PAP-202 | pending |
| [`child/PAP-202/1`](migration/child-pap-202-1.md) | Airtable field mapping: every field type to PaperOS types, relations two-pass, lookups and rollups third pass, formula translation report | PAP-202 | pending |
| [`child/PAP-202/2`](migration/child-pap-202-2.md) | Airtable view mapping and wizard steps: filterByFormula parsing, kanban, calendar, gallery and form views, side-by-side review | PAP-202 | pending |
| [`child/PAP-203/0`](migration/child-pap-203-0.md) | Notion connector and database property mapping to tables (OAuth, search discovery, databases.query streaming at 3 rps, relations and rollups) | PAP-203 | pending |
| [`child/PAP-203/1`](migration/child-pap-203-1.md) | Notion block converter to MDX and Tiptap JSON: all block types, media upload before URL expiry, internal link rewriting | PAP-203 | pending |
| [`child/PAP-203/2`](migration/child-pap-203-2.md) | Notion hierarchy, page tree picker, docs placement and conversion report | PAP-203 | pending |
| [`child/PAP-205/0`](migration/child-pap-205-0.md) | Export archive format v1.0 and streaming export job: manifest, JSON Schemas, table, docs, files, comments, PM, CRM, ledger and audit writers | PAP-205 | pending |
| [`child/PAP-205/1`](migration/child-pap-205-1.md) | Export UI, weekly scheduling to S3 or Google Drive with encryption, signed download links, history and audit | PAP-205 | pending |
| [`child/PAP-205/2`](migration/child-pap-205-2.md) | Round-trip `paperos` connector: import a PaperOS archive into an empty tenant and verify counts and hashes table by table | PAP-205 | pending |
| [`child/PAP-206/0`](migration/child-pap-206-0.md) | Stripe connector and mapping: customers to CRM, catalog and subscriptions to billing, invoices, fees, tax, refunds and payouts to ledger postings | PAP-206 | pending |
| [`child/PAP-206/1`](migration/child-pap-206-1.md) | QuickBooks Online and Xero connectors: chart of accounts, opening balances on a conversion date, optional journal and invoice history | PAP-206 | pending |
| [`child/PAP-206/2`](migration/child-pap-206-2.md) | Finance import wizard: conversion date, account mapping review, duplicate customer resolution, trial balance gate and reversing rollback | PAP-206 | pending |
| [`child/PAP-207/0`](migration/child-pap-207-0.md) | Template pack format, Zod schema, lint, and the `template` applier connector with conflict strategies, composition and upgrade | PAP-207 | pending |
| [`child/PAP-207/1`](migration/child-pap-207-1.md) | Author the five business packs (agency, retail, SaaS, clinic, restaurant) with page specs, views, pipelines, charts of accounts, sample data and starter docs | PAP-207 | pending |
| [`child/PAP-207/2`](migration/child-pap-207-2.md) | Template gallery in onboarding and settings: cards with previews, dry-run diff, apply with or without sample data, remove sample data | PAP-207 | pending |
| [`migration/monday-hubspot-recipes`](migration/monday-hubspot-recipes.md) | Import Monday and HubSpot through guided CSV export recipes with preset mappings (no API connector in this build) |  | pending |
| [`migration/test-accounts`](migration/test-accounts.md) | Provision importer test accounts and fixture workspaces: Airtable demo base, Notion test workspace, ClickUp workspace, Stripe test account, QuickBooks sandbox, Xero demo, Google OAuth app; one Needs Justin item |  | folded into PAP-198 |

### Library Discovery & Integration (`libraries`, 9)

| Key | Title | Parent | Status |
|---|---|---|---|
| [`child/PAP-213/0`](libraries/child-pap-213-0.md) | Table library spike and ADR: TanStack Table plus Virtual, AG Grid Community, Glide Data Grid and react-data-grid at 100k rows | PAP-213 | pending |
| [`child/PAP-213/1`](libraries/child-pap-213-1.md) | Chart and map library spikes and ADRs: ECharts, visx, Recharts, Observable Plot, Nivo, Chart.js; MapLibre GL and Leaflet with self-hosted tiles | PAP-213 | pending |
| [`child/PAP-213/2`](libraries/child-pap-213-2.md) | Canvas and editor shortlist: tldraw, React Flow, Excalidraw, Konva; Tiptap, BlockNote, Lexical, Plate, handed to collab research | PAP-213 | pending |
| [`child/PAP-214/0`](libraries/child-pap-214-0.md) | Decide jobs, transactional email and PDF generation with Docker measurements: Inngest, Trigger.dev, BullMQ, pg-boss, Graphile Worker; Resend, Postmark, SES, Postal; Playwright PDF, react-pdf, Typst | PAP-214 | pending |
| [`child/PAP-214/1`](libraries/child-pap-214-1.md) | Decide search, observability, feature flags and object storage with a resource budget table under 6 GB | PAP-214 | pending |
| [`child/PAP-214/2`](libraries/child-pap-214-2.md) | Confirm validation and runtime, cross-link confirmed choices, consolidate ADRs, compose files and registry entries | PAP-214 | pending |
| [`child/PAP-215/0`](libraries/child-pap-215-0.md) | Spike tables and PM products: NocoDB, Baserow and Plane with compose, seeded flows, metrics and scorecards | PAP-215 | pending |
| [`child/PAP-215/1`](libraries/child-pap-215-1.md) | Spike growth products: Twenty CRM, Chatwoot, Listmonk and Postiz with compose, seeded flows, metrics and scorecards | PAP-215 | pending |
| [`child/PAP-215/2`](libraries/child-pap-215-2.md) | Spike Cal.com and Formbricks, then write the OSS products mode ADR, borrow reference docs and embed integration contracts | PAP-215 | pending |
