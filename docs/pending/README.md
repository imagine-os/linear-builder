# Pending issues (all created in Linear on 2026-09-17)

Historical spec text of the 156 round-2 issues that Linear refused with `USAGE_LIMIT_EXCEEDED` while the workspace was on the Free plan (275-issue cap). Justin upgraded the workspace to **Linear Basic** on 2026-09-17 (~12:50 UTC, NJ-1 / PAP-91 approved) and the create run finished at 2026-09-17T13:07:30Z: **all 153 pending issues now exist as PAP-280..PAP-432** with 379 `blocks` relations, 79 live issues updated to cite them by identifier, and 37 comments. The 3 folded entries stay work packages of their live issues. Team PAP holds 428 issues; 28 are Ready for Claude with zero open blockers; PAP-91 is back in Ready for Claude.

**Linear is the system of record.** The live spec of each issue is `../../specs/<project>/<identifier>-<slug>.md` (regenerated from Linear); the files here keep the text as it was specified in round 2 and are not refreshed. Each file's frontmatter now carries `identifier` (the PAP id it became) and `status: created` (or `status: folded` with `into:`); `index.json` has the same fields. Cross-references written as `[project/key]` in older text resolve through the table below.

## Key to identifier

| Key | Identifier | Parent |
|---|---|---|
| `agents/runtime-sandbox` | [PAP-280](https://linear.app/paperos/issue/PAP-280/build-the-agent-runtime-sandbox-per-session-container-worktree-mount) |  |
| `pm-linear/orchestrator/claims` | [PAP-281](https://linear.app/paperos/issue/PAP-281/orchestrator-linear-polling-atomic-claim-and-state-transitions) | PAP-96 |
| `pm-linear/orchestrator/sessions` | [PAP-282](https://linear.app/paperos/issue/PAP-282/orchestrator-worktree-lifecycle-and-claude-session-launch) | PAP-96 |
| `pm-linear/orchestrator/deploy` | [PAP-283](https://linear.app/paperos/issue/PAP-283/orchestrator-deployment-on-coolify-status-endpoint-and-runbook) | PAP-96 |
| `agents/roster-v1/yaml` | [PAP-284](https://linear.app/paperos/issue/PAP-284/roster-convert-the-planjson-roster-to-37-validated-character-yaml) | PAP-104 |
| `agents/roster-v1/lead-prompts` | [PAP-285](https://linear.app/paperos/issue/PAP-285/roster-write-the-nine-lead-system-prompts-with-shared-fragments) | PAP-104 |
| `agents/roster-v1/sub-prompts` | [PAP-286](https://linear.app/paperos/issue/PAP-286/roster-write-the-28-sub-character-prompts-and-delegation-descriptions) | PAP-104 |
| `agents/roster-v1/build` | [PAP-287](https://linear.app/paperos/issue/PAP-287/roster-build-claudeagents-generation-ci-drift-check-and-smoke-tasks) | PAP-104 |
| `agents/session-observability` | [PAP-288](https://linear.app/paperos/issue/PAP-288/add-agent-session-observability-heartbeats-stuck-session-detection-per) |  |
| `input/commands/registry-core` | [PAP-289](https://linear.app/paperos/issue/PAP-289/command-registry-core-scoping-and-chord-matcher) | PAP-151 |
| `input/commands/palette-help-ui` | [PAP-290](https://linear.app/paperos/issue/PAP-290/command-palette-and-help-sheet-ui) | PAP-151 |
| `input/commands/agent-endpoint-defaults` | [PAP-291](https://linear.app/paperos/issue/PAP-291/agent-execution-endpoint-telemetry-and-default-commands) | PAP-151 |
| `child/PAP-213/0` | [PAP-292](https://linear.app/paperos/issue/PAP-292/table-library-spike-and-adr-tanstack-table-plus-virtual-ag-grid) | PAP-213 |
| `child/PAP-213/1` | [PAP-293](https://linear.app/paperos/issue/PAP-293/chart-and-map-library-spikes-and-adrs-echarts-visx-recharts-observable) | PAP-213 |
| `child/PAP-213/2` | [PAP-294](https://linear.app/paperos/issue/PAP-294/canvas-and-editor-shortlist-tldraw-react-flow-excalidraw-konva-tiptap) | PAP-213 |
| `child/PAP-214/0` | [PAP-295](https://linear.app/paperos/issue/PAP-295/decide-jobs-transactional-email-and-pdf-generation-with-docker) | PAP-214 |
| `child/PAP-214/1` | [PAP-296](https://linear.app/paperos/issue/PAP-296/decide-search-observability-feature-flags-and-object-storage-with-a) | PAP-214 |
| `child/PAP-214/2` | [PAP-297](https://linear.app/paperos/issue/PAP-297/confirm-validation-and-runtime-cross-link-confirmed-choices) | PAP-214 |
| `security/agent-deny-list` | [PAP-298](https://linear.app/paperos/issue/PAP-298/define-and-enforce-the-agent-destructive-action-deny-list-policy-file) |  |
| `security/prompt-injection` | [PAP-299](https://linear.app/paperos/issue/PAP-299/build-prompt-injection-defences-for-agent-sessions-trust-tiers-for) |  |
| `security/credential-broker` | [PAP-300](https://linear.app/paperos/issue/PAP-300/build-the-credential-broker-sessions-hold-no-raw-secrets-an-egress) |  |
| `security/founder-break-glass` | [PAP-301](https://linear.app/paperos/issue/PAP-301/harden-the-founder-root-of-trust-hardware-key-mfa-on-every-external) |  |
| `contracts/shared-value-types` | [PAP-302](https://linear.app/paperos/issue/PAP-302/specify-shared-value-types-and-wire-encodings-in-packagescoretypes) |  |
| `contracts/domain-events` | [PAP-303](https://linear.app/paperos/issue/PAP-303/specify-the-domain-event-contract-envelope-topic-catalogue-definetopic) |  |
| `contracts/idempotency-rate-limits` | [PAP-304](https://linear.app/paperos/issue/PAP-304/specify-and-build-request-idempotency-and-rate-limiting-idempotency) |  |
| `contracts/package-boundaries` | [PAP-305](https://linear.app/paperos/issue/PAP-305/specify-the-monorepo-package-boundary-map-package-ownership-table) |  |
| `pm-linear/weekly-reaudit` | [PAP-306](https://linear.app/paperos/issue/PAP-306/run-a-weekly-plan-re-audit-snapshot-linear-detect-dependency-drift) |  |
| `pm-linear/inbound-triage` | [PAP-307](https://linear.app/paperos/issue/PAP-307/build-inbound-triage-convert-justins-freeform-issues-and-comments-into) |  |
| `agents/eval-harness/runner` | [PAP-308](https://linear.app/paperos/issue/PAP-308/eval-harness-task-format-sdk-runner-deterministic-graders-and-results) | PAP-110 |
| `agents/eval-harness/tasks` | [PAP-309](https://linear.app/paperos/issue/PAP-309/eval-harness-golden-task-set-three-per-lead-one-per-sub-with-fixture) | PAP-110 |
| `agents/eval-harness/judge` | [PAP-310](https://linear.app/paperos/issue/PAP-310/eval-harness-llm-judge-trend-regression-issues-nightly-schedule-and) | PAP-110 |
| `spec-builder/data-section/schema` | [PAP-311](https://linear.app/paperos/issue/PAP-311/data-section-zod-schema-shared-filtertree-import-and-validator-rules) | PAP-119 |
| `spec-builder/data-section/generator` | [PAP-312](https://linear.app/paperos/issue/PAP-312/data-section-typed-hook-generator-for-server-live-and-local-sync-modes) | PAP-119 |
| `spec-builder/data-section/example` | [PAP-313](https://linear.app/paperos/issue/PAP-313/data-section-customer-invoices-end-to-end-with-live-sync-second) | PAP-119 |
| `spec-builder/layout-codegen/templates` | [PAP-314](https://linear.app/paperos/issue/PAP-314/layout-codegen-printer-route-and-view-templates-two-file-ownership-and) | PAP-120 |
| `spec-builder/layout-codegen/wiring` | [PAP-315](https://linear.app/paperos/issue/PAP-315/layout-codegen-state-switch-layout-slot-mapping-action-binding-and) | PAP-120 |
| `spec-builder/layout-codegen/examples` | [PAP-316](https://linear.app/paperos/issue/PAP-316/layout-codegen-generate-the-three-example-specs-screenshot-seven) | PAP-120 |
| `collab/comments/schema-rls-rpc` | [PAP-317](https://linear.app/paperos/issue/PAP-317/comment-schema-anchors-rls-and-orpc-procedures) | PAP-131 |
| `collab/comments/panel-pins-composer` | [PAP-318](https://linear.app/paperos/issue/PAP-318/comment-panel-pins-and-composer-ui) | PAP-131 |
| `collab/comments/live-deeplinks-linear` | [PAP-319](https://linear.app/paperos/issue/PAP-319/live-updates-deep-links-and-linear-escalation) | PAP-131 |
| `collab/canvas/nodes-edges-loader` | [PAP-320](https://linear.app/paperos/issue/PAP-320/canvas-node-and-edge-types-with-graph-loader) | PAP-132 |
| `collab/canvas/yjs-overlay` | [PAP-321](https://linear.app/paperos/issue/PAP-321/collaborative-overlay-notes-regions-overrides-in-yjs) | PAP-132 |
| `collab/canvas/filters-export-perf` | [PAP-322](https://linear.app/paperos/issue/PAP-322/filters-deep-links-export-and-300-node-performance-run) | PAP-132 |
| `collab/notifications/inbox-preferences` | [PAP-323](https://linear.app/paperos/issue/PAP-323/inbox-ui-bell-badge-and-preferences-page) | PAP-136 |
| `collab/notifications/digests-quiet-hours` | [PAP-324](https://linear.app/paperos/issue/PAP-324/digests-quiet-hours-and-burst-collapse) | PAP-136 |
| `collab/notifications/slack-channel` | [PAP-325](https://linear.app/paperos/issue/PAP-325/slack-channel-and-tenant-slack-configuration) | PAP-136 |
| `realtime/record-sync/live-hooks-registry` | [PAP-326](https://linear.app/paperos/issue/PAP-326/live-record-hooks-and-shape-registry-additions) | PAP-143 |
| `realtime/record-sync/reconciler` | [PAP-327](https://linear.app/paperos/issue/PAP-327/reconciler-for-optimistic-writes-and-conflict-events) | PAP-143 |
| `realtime/record-sync/resubscribe-lag` | [PAP-328](https://linear.app/paperos/issue/PAP-328/permission-driven-resubscribe-and-lag-measurement) | PAP-143 |
| `input/dnd/sensors-sortable-list` | [PAP-329](https://linear.app/paperos/issue/PAP-329/dnd-kit-sensors-on-the-input-abstraction-and-sortablelist) | PAP-155 |
| `input/dnd/keyboard-announcements` | [PAP-330](https://linear.app/paperos/issue/PAP-330/keyboard-alternative-announcements-and-focus-restore) | PAP-155 |
| `input/dnd/kanban-grid-dropzone-crosswindow` | [PAP-331](https://linear.app/paperos/issue/PAP-331/kanbandnd-sortablegrid-dropzone-and-cross-window-drag) | PAP-155 |
| `gap/tables/schema-editor` | [PAP-332](https://linear.app/paperos/issue/PAP-332/build-the-custom-dataset-schema-editor-create-tables-and-fields-in-app) |  |
| `gap/tables/record-detail` | [PAP-333](https://linear.app/paperos/issue/PAP-333/build-record-level-features-shared-by-every-module-record-detail-page) |  |
| `gap/tables/bulk-trash` | [PAP-334](https://linear.app/paperos/issue/PAP-334/build-bulk-operations-trash-and-restore-multi-row-edit-and-delete-with) |  |
| `tables/compiler/core` | [PAP-335](https://linear.app/paperos/issue/PAP-335/compiler-core-dataset-resolution-per-type-filter-ops-sorts-and-signed) | PAP-163 |
| `tables/compiler/groups-shapes` | [PAP-336](https://linear.app/paperos/issue/PAP-336/groups-aggregates-and-electric-shape-eligibility) | PAP-163 |
| `tables/compiler/api-hook-bench` | [PAP-337](https://linear.app/paperos/issue/PAP-337/orpc-procedures-useviewquery-hook-and-the-100k-row-benchmark) | PAP-163 |
| `tables/fields/framework-primitives` | [PAP-338](https://linear.app/paperos/issue/PAP-338/field-type-framework-and-primitive-types-text-number-currency-percent) | PAP-164 |
| `tables/fields/choice-people-attachment` | [PAP-339](https://linear.app/paperos/issue/PAP-339/choice-people-and-attachment-types-select-multiselect-user-attachment) | PAP-164 |
| `tables/fields/relational-computed` | [PAP-340](https://linear.app/paperos/issue/PAP-340/relational-and-computed-types-relation-lookup-rollup-formula-storage) | PAP-164 |
| `tables/grid/core` | [PAP-341](https://linear.app/paperos/issue/PAP-341/grid-core-virtualisation-data-binding-selection-model-and-keyboard) | PAP-165 |
| `tables/grid/editing-clipboard-bulk` | [PAP-342](https://linear.app/paperos/issue/PAP-342/inline-editing-with-optimistic-commit-tsv-clipboard-ranges-and-the) | PAP-165 |
| `tables/grid/columns-groups-panel` | [PAP-343](https://linear.app/paperos/issue/PAP-343/column-operations-grouping-headers-aggregate-footer-and-recordpanel) | PAP-165 |
| `tables/time/engine-calendar` | [PAP-344](https://linear.app/paperos/issue/PAP-344/timescale-engine-range-compilation-overlap-packing-and-the-calendar) | PAP-168 |
| `tables/time/timeline` | [PAP-345](https://linear.app/paperos/issue/PAP-345/timeline-view-two-axis-virtualised-canvas-lanes-zoom-levels-and-bar) | PAP-168 |
| `tables/time/gantt` | [PAP-346](https://linear.app/paperos/issue/PAP-346/gantt-view-frozen-left-grid-dependency-arrows-critical-path-progress) | PAP-168 |
| `child/PAP-199/0` | [PAP-347](https://linear.app/paperos/issue/PAP-347/connector-interface-mapping-model-and-import-engine-sourceconnector) | PAP-199 |
| `child/PAP-199/1` | [PAP-348](https://linear.app/paperos/issue/PAP-348/dry-run-commit-and-rollback-semantics-transaction-rolled-dry-run) | PAP-199 |
| `child/PAP-199/2` | [PAP-349](https://linear.app/paperos/issue/PAP-349/type-inference-mapping-wizard-ui-and-run-history-with-per-item-drill) | PAP-199 |
| `child/PAP-215/0` | [PAP-350](https://linear.app/paperos/issue/PAP-350/spike-tables-and-pm-products-nocodb-baserow-and-plane-with-compose) | PAP-215 |
| `child/PAP-215/1` | [PAP-351](https://linear.app/paperos/issue/PAP-351/spike-growth-products-twenty-crm-chatwoot-listmonk-and-postiz-with) | PAP-215 |
| `child/PAP-215/2` | [PAP-352](https://linear.app/paperos/issue/PAP-352/spike-calcom-and-formbricks-then-write-the-oss-products-mode-adr) | PAP-215 |
| `security/field-encryption` | [PAP-353](https://linear.app/paperos/issue/PAP-353/build-server-side-field-encryption-for-stored-secrets-oauth-tokens) |  |
| `security/platform-dr` | [PAP-354](https://linear.app/paperos/issue/PAP-354/add-object-storage-yjs-orchestrator-and-sops-key-backups-and-a-monthly) |  |
| `security/retention-pii` | [PAP-355](https://linear.app/paperos/issue/PAP-355/enforce-data-retention-pii-classification-and-tenant-hard-purge-pii) |  |
| `security/security-telemetry` | [PAP-356](https://linear.app/paperos/issue/PAP-356/build-security-telemetry-and-alerting-auth-anomalies-rls-denials-agent) |  |
| `security/dast` | [PAP-357](https://linear.app/paperos/issue/PAP-357/add-dynamic-security-testing-nightly-zap-baseline-and-authenticated) |  |
| `security/supply-chain` | [PAP-358](https://linear.app/paperos/issue/PAP-358/add-supply-chain-integrity-lockfile-and-minimum-release-age-policy) |  |
| `security/pci-posture` | [PAP-359](https://linear.app/paperos/issue/PAP-359/document-and-enforce-the-pci-saq-a-posture-stripe-hosted-card-entry) |  |
| `gp/spec-builder/app-interview` | [PAP-360](https://linear.app/paperos/issue/PAP-360/write-the-app-interview-skill-one-paragraph-idea-to-appspecyaml) |  |
| `gp/spec-builder/entity-pages` | [PAP-361](https://linear.app/paperos/issue/PAP-361/build-entity-derived-page-specs-pnpm-spec-genentity-pages-derives-list) |  |
| `gp/spec-builder/gen-pipeline` | [PAP-362](https://linear.app/paperos/issue/PAP-362/build-paperos-gen-the-whole-app-generation-pipeline-that-runs-every) |  |
| `gp/app-shell/starter-surfaces` | [PAP-363](https://linear.app/paperos/issue/PAP-363/build-the-default-surfaces-starter-kit-customer-portal-and-staff) |  |
| `gp/app-shell/driver` | [PAP-364](https://linear.app/paperos/issue/PAP-364/build-the-golden-path-driver-paperos-create-idea-runs-interview-app) |  |
| `gp/app-shell/provisioning` | [PAP-365](https://linear.app/paperos/issue/PAP-365/build-golden-path-provisioning-parallel-idempotent-steps-warm-pools) |  |
| `gap/app-shell/runtime-flags` | [PAP-366](https://linear.app/paperos/issue/PAP-366/build-runtime-feature-flags-per-tenant-and-per-audience-flags-with) |  |
| `gap/app-shell/onboarding-wizard` | [PAP-367](https://linear.app/paperos/issue/PAP-367/build-the-first-run-tenant-onboarding-wizard-create-organisation) |  |
| `gap/app-shell/client-errors` | [PAP-368](https://linear.app/paperos/issue/PAP-368/define-the-client-error-handling-and-crash-reporting-contract-error) |  |
| `gap/app-shell/code-signing` | [PAP-369](https://linear.app/paperos/issue/PAP-369/set-up-desktop-and-mobile-code-signing-and-notarisation-apple) |  |
| `gap/data-layer/email-package` | [PAP-370](https://linear.app/paperos/issue/PAP-370/build-the-transactional-email-package-packagesemail-react-email) |  |
| `gap/forge/non-linux-runners` | [PAP-371](https://linear.app/paperos/issue/PAP-371/provision-non-linux-ci-capacity-hosted-macos-runners-xcode-voiceover) |  |
| `pm-linear/linear-sync/inbound` | [PAP-372](https://linear.app/paperos/issue/PAP-372/linear-sync-backfill-and-inbound-webhook-upsert-into-pm-tables) | PAP-101 |
| `pm-linear/linear-sync/outbound` | [PAP-373](https://linear.app/paperos/issue/PAP-373/linear-sync-transactional-outbox-outbound-worker-and-loop-prevention) | PAP-101 |
| `pm-linear/linear-sync/conflicts` | [PAP-374](https://linear.app/paperos/issue/PAP-374/linear-sync-conflict-rule-linear-wins-sync-status-page-and-runbook) | PAP-101 |
| `spec-builder/spec-i18n` | [PAP-375](https://linear.app/paperos/issue/PAP-375/add-spec-level-internationalisation-message-ids-for-spec-copy-fields) |  |
| `spec-builder/spec-editor-ui/yaml` | [PAP-376](https://linear.app/paperos/issue/PAP-376/spec-editor-spec-list-codemirror-yaml-editor-with-worker-validation) | PAP-124 |
| `spec-builder/spec-editor-ui/form` | [PAP-377](https://linear.app/paperos/issue/PAP-377/spec-editor-form-view-component-tree-editor-and-two-way-sync-with-yaml) | PAP-124 |
| `spec-builder/spec-editor-ui/preview` | [PAP-378](https://linear.app/paperos/issue/PAP-378/spec-editor-live-preview-at-selectable-widths-flow-graph-tab-keyboard) | PAP-124 |
| `collab/runtime-docs-store` | [PAP-379](https://linear.app/paperos/issue/PAP-379/build-a-runtime-docs-store-for-tenant-authored-documents-yjs-backed) |  |
| `collab/in-app-help` | [PAP-380](https://linear.app/paperos/issue/PAP-380/add-contextual-in-app-help-help-panel-bound-to-page-spec-purpose-and) |  |
| `realtime/push-transport` | [PAP-381](https://linear.app/paperos/issue/PAP-381/build-the-push-transport-server-to-client-notification-and-job) |  |
| `tables/formula/parser-typecheck` | [PAP-382](https://linear.app/paperos/issue/PAP-382/lexer-pratt-parser-ast-type-checker-and-the-definefunction-catalogue) | PAP-171 |
| `tables/formula/evaluator-editor` | [PAP-383](https://linear.app/paperos/issue/PAP-383/typescript-evaluator-with-function-implementations-and-the-codemirror) | PAP-171 |
| `tables/formula/sql-cache` | [PAP-384](https://linear.app/paperos/issue/PAP-384/sql-compiler-formula-cache-fallback-job-and-the-dependency-graph) | PAP-171 |
| `tables/dashboard/model-grid` | [PAP-385](https://linear.app/paperos/issue/PAP-385/dashboard-tables-layout-engine-breakpoint-layouts-and-drag-or-resize) | PAP-173 |
| `tables/dashboard/blocks-crossfilter` | [PAP-386](https://linear.app/paperos/issue/PAP-386/block-kinds-cross-filter-bus-filter-bar-params-and-deep-links) | PAP-173 |
| `tables/dashboard/print-perf-spec` | [PAP-387](https://linear.app/paperos/issue/PAP-387/lazy-loading-error-boundaries-print-route-page-spec-hook-and) | PAP-173 |
| `tables/automations/model-triggers` | [PAP-388](https://linear.app/paperos/issue/PAP-388/automation-schema-trigger-sources-and-the-run-runtime-with-idempotency) | PAP-174 |
| `tables/automations/actions` | [PAP-389](https://linear.app/paperos/issue/PAP-389/action-catalogue-with-scope-classes-template-expressions-connectorcall) | PAP-174 |
| `tables/automations/builder-log-templates` | [PAP-390](https://linear.app/paperos/issue/PAP-390/automation-builder-page-test-run-run-log-with-replay-five-starter) | PAP-174 |
| `gap/business-core/usage-metering` | [PAP-391](https://linear.app/paperos/issue/PAP-391/build-usage-metering-and-metered-billing-usage-events-agent-sessions) |  |
| `business-core/ledger/journal-constraints` | [PAP-392](https://linear.app/paperos/issue/PAP-392/journal-tables-balance-trigger-immutability-trigger-gapless-numbering) | PAP-179 |
| `business-core/ledger/hashchain-reversal-close` | [PAP-393](https://linear.app/paperos/issue/PAP-393/hash-chain-with-nightly-verification-ledgerreverse-and-the-period) | PAP-179 |
| `business-core/ledger/rules-ui-trialbalance` | [PAP-394](https://linear.app/paperos/issue/PAP-394/posting-rule-registry-with-the-first-five-rules-financejournal-ui) | PAP-179 |
| `business-core/invoicing/model-statemachine` | [PAP-395](https://linear.app/paperos/issue/PAP-395/document-model-lines-sequences-server-side-totals-state-machine-quote) | PAP-180 |
| `business-core/invoicing/pdf-paypage` | [PAP-396](https://linear.app/paperos/issue/PAP-396/branded-pdf-rendering-public-pay-and-doc-pages-stripe-checkout-on) | PAP-180 |
| `business-core/invoicing/postings-portal-emails` | [PAP-397](https://linear.app/paperos/issue/PAP-397/posting-rules-invoice-manual-payments-reminders-job-customer-portal) | PAP-180 |
| `business-core/payroll/adapter-contract` | [PAP-398](https://linear.app/paperos/issue/PAP-398/finalised-payrollprovider-interface-first-adapter-with-idempotency) | PAP-184 |
| `business-core/payroll/onboarding-sync` | [PAP-399](https://linear.app/paperos/issue/PAP-399/payroll-tables-company-and-employee-onboarding-via-provider-links) | PAP-184 |
| `business-core/payroll/run-approve-post` | [PAP-400](https://linear.app/paperos/issue/PAP-400/payroll-run-flow-typed-total-approval-webhook-status-transitions) | PAP-184 |
| `growth/social/model-queue-calendar` | [PAP-401](https://linear.app/paperos/issue/PAP-401/social-schema-approval-state-machine-composer-with-per-platform) | PAP-190 |
| `growth/social/adapter-mock-x` | [PAP-402](https://linear.app/paperos/issue/PAP-402/adapter-interface-mock-adapter-x-api-v2-adapter-and-the-pg-boss) | PAP-190 |
| `growth/social/adapters-review-gated` | [PAP-403](https://linear.app/paperos/issue/PAP-403/linkedin-instagram-tiktok-and-youtube-adapters-in-dryrun-with-payload) | PAP-190 |
| `growth/outreach/model-worker` | [PAP-404](https://linear.app/paperos/issue/PAP-404/outreach-schema-provider-interface-with-resend-and-twilio-adapters) | PAP-191 |
| `growth/outreach/compliance-warmup-replies` | [PAP-405](https://linear.app/paperos/issue/PAP-405/consent-and-suppression-checks-quiet-hours-unsubscribe-and-stop) | PAP-191 |
| `growth/outreach/ui` | [PAP-406](https://linear.app/paperos/issue/PAP-406/sequence-builder-template-editor-with-preview-and-test-send-enrolments) | PAP-191 |
| `growth/referral/codes-attribution` | [PAP-407](https://linear.app/paperos/issue/PAP-407/referral-programs-codes-rcode-route-attribution-window-and-the) | PAP-196 |
| `growth/referral/rewards-payouts-ledger` | [PAP-408](https://linear.app/paperos/issue/PAP-408/reward-rules-fraud-rules-approval-stripe-connect-transfers-ledger) | PAP-196 |
| `growth/referral/portal-console-ui` | [PAP-409](https://linear.app/paperos/issue/PAP-409/portal-referral-page-console-program-and-referral-grids-and-the) | PAP-196 |
| `growth/support/email-threading` | [PAP-410](https://linear.app/paperos/issue/PAP-410/support-schema-inbound-email-parsing-threading-heuristics-html) | PAP-197 |
| `growth/support/chat-notes` | [PAP-411](https://linear.app/paperos/issue/PAP-411/portal-supportchat-widget-with-live-sync-and-presence-unauthenticated) | PAP-197 |
| `growth/support/console-ui` | [PAP-412](https://linear.app/paperos/issue/PAP-412/three-pane-inbox-on-a-saved-list-view-conversation-view-contact) | PAP-197 |
| `migration/monday-hubspot-recipes` | [PAP-413](https://linear.app/paperos/issue/PAP-413/import-monday-and-hubspot-through-guided-csv-export-recipes-with) |  |
| `child/PAP-202/0` | [PAP-414](https://linear.app/paperos/issue/PAP-414/airtable-connector-oauth-and-pat-auth-metadata-discovery-record) | PAP-202 |
| `child/PAP-202/1` | [PAP-415](https://linear.app/paperos/issue/PAP-415/airtable-field-mapping-every-field-type-to-paperos-types-relations-two) | PAP-202 |
| `child/PAP-202/2` | [PAP-416](https://linear.app/paperos/issue/PAP-416/airtable-view-mapping-and-wizard-steps-filterbyformula-parsing-kanban) | PAP-202 |
| `child/PAP-203/0` | [PAP-417](https://linear.app/paperos/issue/PAP-417/notion-connector-and-database-property-mapping-to-tables-oauth-search) | PAP-203 |
| `child/PAP-203/1` | [PAP-418](https://linear.app/paperos/issue/PAP-418/notion-block-converter-to-mdx-and-tiptap-json-all-block-types-media) | PAP-203 |
| `child/PAP-203/2` | [PAP-419](https://linear.app/paperos/issue/PAP-419/notion-hierarchy-page-tree-picker-docs-placement-and-conversion-report) | PAP-203 |
| `child/PAP-205/0` | [PAP-420](https://linear.app/paperos/issue/PAP-420/export-archive-format-v10-and-streaming-export-job-manifest-json) | PAP-205 |
| `child/PAP-205/1` | [PAP-421](https://linear.app/paperos/issue/PAP-421/export-ui-weekly-scheduling-to-s3-or-google-drive-with-encryption) | PAP-205 |
| `child/PAP-205/2` | [PAP-422](https://linear.app/paperos/issue/PAP-422/round-trip-paperos-connector-import-a-paperos-archive-into-an-empty) | PAP-205 |
| `child/PAP-206/0` | [PAP-423](https://linear.app/paperos/issue/PAP-423/stripe-connector-and-mapping-customers-to-crm-catalog-and) | PAP-206 |
| `child/PAP-206/1` | [PAP-424](https://linear.app/paperos/issue/PAP-424/quickbooks-online-and-xero-connectors-chart-of-accounts-opening) | PAP-206 |
| `child/PAP-206/2` | [PAP-425](https://linear.app/paperos/issue/PAP-425/finance-import-wizard-conversion-date-account-mapping-review-duplicate) | PAP-206 |
| `child/PAP-207/0` | [PAP-426](https://linear.app/paperos/issue/PAP-426/template-pack-format-zod-schema-lint-and-the-template-applier) | PAP-207 |
| `child/PAP-207/1` | [PAP-427](https://linear.app/paperos/issue/PAP-427/author-the-five-business-packs-agency-retail-saas-clinic-restaurant) | PAP-207 |
| `child/PAP-207/2` | [PAP-428](https://linear.app/paperos/issue/PAP-428/template-gallery-in-onboarding-and-settings-cards-with-previews-dry) | PAP-207 |
| `gp/app-shell/acceptance` | [PAP-429](https://linear.app/paperos/issue/PAP-429/build-the-golden-path-acceptance-test-nightly-ci-runs-three-canned) |  |
| `gp/app-shell/upgrade` | [PAP-430](https://linear.app/paperos/issue/PAP-430/build-paperos-upgrade-apply-template-updates-to-generated-apps-with) |  |
| `gap/app-shell/custom-domains` | [PAP-431](https://linear.app/paperos/issue/PAP-431/add-per-tenant-custom-domains-on-demand-tls-in-caddy-host-based-tenant) |  |
| `gap/data-layer/tenant-lifecycle` | [PAP-432](https://linear.app/paperos/issue/PAP-432/build-the-tenant-lifecycle-tenant-states-deletion-request-and-cancel) |  |
| `migration/test-accounts` | folded into PAP-198 (work package 2) | |
| `gap/growth/consent-centre` | folded into PAP-187 (work package 0) | |
| `gap/business-core/recurring-dunning` | folded into PAP-180 (work package 4) | |
| `spec-builder/spec-versioning` | folded into PAP-114 (work package out of scope; migrate/ skeleton only) | |

## Index


### Universal App Shell & Repo Template (`app-shell`, 11)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`contracts/package-boundaries`](app-shell/contracts-package-boundaries.md) | Specify the monorepo package boundary map: package ownership table, allowed dependency graph, `packages/core` sub-folder owners, dependency-cruiser lint in Gate 1 and the `packages/pm` move |  | [PAP-305](https://linear.app/paperos/issue/PAP-305/specify-the-monorepo-package-boundary-map-package-ownership-table) |
| [`gap/app-shell/client-errors`](app-shell/app-shell-client-errors.md) | Define the client error handling and crash reporting contract: error boundaries, error code catalogue, user-facing copy, browser and Tauri crash reports into observability |  | [PAP-368](https://linear.app/paperos/issue/PAP-368/define-the-client-error-handling-and-crash-reporting-contract-error) |
| [`gap/app-shell/code-signing`](app-shell/app-shell-code-signing.md) | Set up desktop and mobile code signing and notarisation (Apple Developer, Windows certificate, Android keystore) with one Needs Justin credential ask |  | [PAP-369](https://linear.app/paperos/issue/PAP-369/set-up-desktop-and-mobile-code-signing-and-notarisation-apple) |
| [`gap/app-shell/custom-domains`](app-shell/app-shell-custom-domains.md) | Add per-tenant custom domains: on-demand TLS in Caddy, host-based tenant resolution in api-layer, DNS verification UI |  | [PAP-431](https://linear.app/paperos/issue/PAP-431/add-per-tenant-custom-domains-on-demand-tls-in-caddy-host-based-tenant) |
| [`gap/app-shell/onboarding-wizard`](app-shell/app-shell-onboarding-wizard.md) | Build the first-run tenant onboarding wizard: create organisation, choose business template, invite team, connect billing, land on a seeded dashboard |  | [PAP-367](https://linear.app/paperos/issue/PAP-367/build-the-first-run-tenant-onboarding-wizard-create-organisation) |
| [`gap/app-shell/runtime-flags`](app-shell/app-shell-runtime-flags.md) | Build runtime feature flags: per-tenant and per-audience flags with kill switches, segment targeting and page-spec `flags:` guards |  | [PAP-366](https://linear.app/paperos/issue/PAP-366/build-runtime-feature-flags-per-tenant-and-per-audience-flags-with) |
| [`gp/app-shell/acceptance`](app-shell/gp-app-shell-acceptance.md) | Build the golden path acceptance test: nightly CI runs three canned ideas from paragraph to preview URL, asserts gates 1 to 4 and under ten minutes, publishes `golden-path.json`, badge and friction issues |  | [PAP-429](https://linear.app/paperos/issue/PAP-429/build-the-golden-path-acceptance-test-nightly-ci-runs-three-canned) |
| [`gp/app-shell/driver`](app-shell/gp-app-shell-driver.md) | Build the golden path driver: `paperos create --idea` runs interview, app spec, generation, seed, push, provisioning and preview in one command with checkpoint stamps |  | [PAP-364](https://linear.app/paperos/issue/PAP-364/build-the-golden-path-driver-paperos-create-idea-runs-interview-app) |
| [`gp/app-shell/provisioning`](app-shell/gp-app-shell-provisioning.md) | Build golden path provisioning: parallel idempotent steps, warm pools for preview slots, databases and mirror repos, `--resume` and per-step time budgets in `paperos create` |  | [PAP-365](https://linear.app/paperos/issue/PAP-365/build-golden-path-provisioning-parallel-idempotent-steps-warm-pools) |
| [`gp/app-shell/starter-surfaces`](app-shell/gp-app-shell-starter-surfaces.md) | Build the default surfaces starter kit: customer portal and staff console page specs, a seeded demo tenant per audience and a first-run checklist for every generated app |  | [PAP-363](https://linear.app/paperos/issue/PAP-363/build-the-default-surfaces-starter-kit-customer-portal-and-staff) |
| [`gp/app-shell/upgrade`](app-shell/gp-app-shell-upgrade.md) | Build `paperos upgrade`: apply template updates to generated apps with three-way merge, codemods, regeneration and an upgrade pull request |  | [PAP-430](https://linear.app/paperos/issue/PAP-430/build-paperos-upgrade-apply-template-updates-to-generated-apps-with) |

### Data Layer & Database (`data-layer`, 8)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`contracts/domain-events`](data-layer/contracts-domain-events.md) | Specify the domain event contract: envelope, topic catalogue, `defineTopic` registry, transactional outbox and subscriber delivery (`packages/core/events`) |  | [PAP-303](https://linear.app/paperos/issue/PAP-303/specify-the-domain-event-contract-envelope-topic-catalogue-definetopic) |
| [`contracts/idempotency-rate-limits`](data-layer/contracts-idempotency-rate-limits.md) | Specify and build request idempotency and rate limiting: `Idempotency-Key` header, `idempotency_keys` table with replay semantics, `POST /api/v1/rpc/batch`, Postgres-backed token buckets per actor, API key and IP |  | [PAP-304](https://linear.app/paperos/issue/PAP-304/specify-and-build-request-idempotency-and-rate-limiting-idempotency) |
| [`contracts/shared-value-types`](data-layer/contracts-shared-value-types.md) | Specify shared value types and wire encodings in `packages/core/types`: `Money` (bigint minor units, string on the wire), `ActorRef`, `EntityRef`, UUIDv7 ids, timestamps, signed cursors and the `ApiError` body |  | [PAP-302](https://linear.app/paperos/issue/PAP-302/specify-shared-value-types-and-wire-encodings-in-packagescoretypes) |
| [`gap/data-layer/email-package`](data-layer/data-layer-email-package.md) | Build the transactional email package (`packages/email`): React Email templates, provider adapter, sandbox allowlist mode, suppression list, DKIM/SPF/DMARC check, Mailpit in dev |  | [PAP-370](https://linear.app/paperos/issue/PAP-370/build-the-transactional-email-package-packagesemail-react-email) |
| [`gap/data-layer/tenant-lifecycle`](data-layer/data-layer-tenant-lifecycle.md) | Build the tenant lifecycle: tenant states, deletion request and cancel flow with grace period, archive metadata, per-tenant storage and row quotas (the purge job itself is `security/retention-pii`) |  | [PAP-432](https://linear.app/paperos/issue/PAP-432/build-the-tenant-lifecycle-tenant-states-deletion-request-and-cancel) |
| [`security/field-encryption`](data-layer/security-field-encryption.md) | Build server-side field encryption for stored secrets (OAuth tokens, SCIM and webhook secrets, connector credentials, TOTP seeds) with envelope keys, key rotation and a leak scanner |  | [PAP-353](https://linear.app/paperos/issue/PAP-353/build-server-side-field-encryption-for-stored-secrets-oauth-tokens) |
| [`security/platform-dr`](data-layer/security-platform-dr.md) | Add object-storage, Yjs, orchestrator and sops-key backups and a monthly platform-wide disaster-recovery drill restoring everything on a fresh host against RPO 1 h and RTO 4 h |  | [PAP-354](https://linear.app/paperos/issue/PAP-354/add-object-storage-yjs-orchestrator-and-sops-key-backups-and-a-monthly) |
| [`security/retention-pii`](data-layer/security-retention-pii.md) | Enforce data retention, PII classification and tenant hard-purge: `pii` column annotations driving redaction and OTel filters, per-table retention jobs, and the export-first purge after the grace period |  | [PAP-355](https://linear.app/paperos/issue/PAP-355/enforce-data-retention-pii-classification-and-tenant-hard-purge-pii) |

### Version Control & Forge Independence (`forge`, 2)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`gap/forge/non-linux-runners`](forge/forge-non-linux-runners.md) | Provision non-Linux CI capacity: hosted macOS runners (Xcode, VoiceOver) and a Windows VM runner (NVDA, MSI signing) with cost caps and secrets |  | [PAP-371](https://linear.app/paperos/issue/PAP-371/provision-non-linux-ci-capacity-hosted-macos-runners-xcode-voiceover) |
| [`security/supply-chain`](forge/security-supply-chain.md) | Add supply-chain integrity: lockfile and minimum-release-age policy, pinned actions by digest, SLSA provenance attestations and cosign signatures for container images and Tauri artifacts, verified before deploy and update |  | [PAP-358](https://linear.app/paperos/issue/PAP-358/add-supply-chain-integrity-lockfile-and-minimum-release-age-policy) |

### Identity, Roles & Audiences (`identity`, 1)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`security/founder-break-glass`](identity/security-founder-break-glass.md) | Harden the founder root of trust: hardware-key MFA on every external account, an offline recovery age key with escrow, a one-command revoke-all, and the break-glass runbook filed as a single Needs Justin checklist |  | [PAP-301](https://linear.app/paperos/issue/PAP-301/harden-the-founder-root-of-trust-hardware-key-mfa-on-every-external) |

### Quality Pipeline (`quality`, 2)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`security/dast`](quality/security-dast.md) | Add dynamic security testing: nightly ZAP baseline and authenticated scan of staging plus a security regression suite (CSRF, IDOR across tenants, headers, rate limits, upload abuse, webhook replay) that blocks the release candidate |  | [PAP-357](https://linear.app/paperos/issue/PAP-357/add-dynamic-security-testing-nightly-zap-baseline-and-authenticated) |
| [`security/security-telemetry`](quality/security-security-telemetry.md) | Build security telemetry and alerting: auth anomalies, RLS denials, agent policy and egress denials, canary hits, webhook signature failures and backup age routed to Linear with a weekly security digest |  | [PAP-356](https://linear.app/paperos/issue/PAP-356/build-security-telemetry-and-alerting-auth-anomalies-rls-denials-agent) |

### Project Management & Claude Pipeline (`pm-linear`, 9)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`pm-linear/inbound-triage`](pm-linear/inbound-triage.md) | Build inbound triage: convert Justin's freeform issues and comments into contract-valid issues via the Decomposer sub-agent, wired to the Triage view |  | [PAP-307](https://linear.app/paperos/issue/PAP-307/build-inbound-triage-convert-justins-freeform-issues-and-comments-into) |
| [`pm-linear/linear-sync/conflicts`](pm-linear/linear-sync-conflicts.md) | Linear sync: conflict rule (Linear wins), sync status page and runbook | PAP-101 | [PAP-374](https://linear.app/paperos/issue/PAP-374/linear-sync-conflict-rule-linear-wins-sync-status-page-and-runbook) |
| [`pm-linear/linear-sync/inbound`](pm-linear/linear-sync-inbound.md) | Linear sync: backfill and inbound webhook upsert into pm_* tables | PAP-101 | [PAP-372](https://linear.app/paperos/issue/PAP-372/linear-sync-backfill-and-inbound-webhook-upsert-into-pm-tables) |
| [`pm-linear/linear-sync/outbound`](pm-linear/linear-sync-outbound.md) | Linear sync: transactional outbox, outbound worker and loop prevention | PAP-101 | [PAP-373](https://linear.app/paperos/issue/PAP-373/linear-sync-transactional-outbox-outbound-worker-and-loop-prevention) |
| [`pm-linear/orchestrator/claims`](pm-linear/orchestrator-claims.md) | Orchestrator: Linear polling, atomic claim and state transitions | PAP-96 | [PAP-281](https://linear.app/paperos/issue/PAP-281/orchestrator-linear-polling-atomic-claim-and-state-transitions) |
| [`pm-linear/orchestrator/deploy`](pm-linear/orchestrator-deploy.md) | Orchestrator: deployment on Coolify, `/status` endpoint and runbook | PAP-96 | [PAP-283](https://linear.app/paperos/issue/PAP-283/orchestrator-deployment-on-coolify-status-endpoint-and-runbook) |
| [`pm-linear/orchestrator/sessions`](pm-linear/orchestrator-sessions.md) | Orchestrator: worktree lifecycle and Claude session launch | PAP-96 | [PAP-282](https://linear.app/paperos/issue/PAP-282/orchestrator-worktree-lifecycle-and-claude-session-launch) |
| [`pm-linear/weekly-reaudit`](pm-linear/weekly-reaudit.md) | Run a weekly plan re-audit: snapshot Linear, detect dependency drift, cycles, stale In Progress sessions, issues without specs; post the report to Linear |  | [PAP-306](https://linear.app/paperos/issue/PAP-306/run-a-weekly-plan-re-audit-snapshot-linear-detect-dependency-drift) |
| [`security/credential-broker`](pm-linear/security-credential-broker.md) | Build the credential broker: sessions hold no raw secrets; an egress proxy injects short-lived per-session tokens (GitHub App, Forgejo, Linear proxy, PaperOS agent keys, Anthropic) with usage logs and one-command revoke-all |  | [PAP-300](https://linear.app/paperos/issue/PAP-300/build-the-credential-broker-sessions-hold-no-raw-secrets-an-egress) |

### Agent Characters & Orgs (`agents`, 11)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`agents/eval-harness/judge`](agents/eval-harness-judge.md) | Eval harness: LLM judge, trend, regression issues, nightly schedule and report page | PAP-110 | [PAP-310](https://linear.app/paperos/issue/PAP-310/eval-harness-llm-judge-trend-regression-issues-nightly-schedule-and) |
| [`agents/eval-harness/runner`](agents/eval-harness-runner.md) | Eval harness: task format, SDK runner, deterministic graders and results table | PAP-110 | [PAP-308](https://linear.app/paperos/issue/PAP-308/eval-harness-task-format-sdk-runner-deterministic-graders-and-results) |
| [`agents/eval-harness/tasks`](agents/eval-harness-tasks.md) | Eval harness: golden task set (three per lead, one per sub) with fixture repos and answer keys | PAP-110 | [PAP-309](https://linear.app/paperos/issue/PAP-309/eval-harness-golden-task-set-three-per-lead-one-per-sub-with-fixture) |
| [`agents/roster-v1/build`](agents/roster-v1-build.md) | Roster: build `.claude/agents` generation, CI drift check and smoke tasks per lead | PAP-104 | [PAP-287](https://linear.app/paperos/issue/PAP-287/roster-build-claudeagents-generation-ci-drift-check-and-smoke-tasks) |
| [`agents/roster-v1/lead-prompts`](agents/roster-v1-lead-prompts.md) | Roster: write the nine lead system prompts with shared fragments | PAP-104 | [PAP-285](https://linear.app/paperos/issue/PAP-285/roster-write-the-nine-lead-system-prompts-with-shared-fragments) |
| [`agents/roster-v1/sub-prompts`](agents/roster-v1-sub-prompts.md) | Roster: write the 28 sub-character prompts and delegation descriptions | PAP-104 | [PAP-286](https://linear.app/paperos/issue/PAP-286/roster-write-the-28-sub-character-prompts-and-delegation-descriptions) |
| [`agents/roster-v1/yaml`](agents/roster-v1-yaml.md) | Roster: convert the plan.json roster to 37 validated character YAML files | PAP-104 | [PAP-284](https://linear.app/paperos/issue/PAP-284/roster-convert-the-planjson-roster-to-37-validated-character-yaml) |
| [`agents/runtime-sandbox`](agents/runtime-sandbox.md) | Build the agent runtime sandbox: per-session container, worktree mount, CPU/RAM/time limits and network isolation with the credential broker's egress proxy as the only route |  | [PAP-280](https://linear.app/paperos/issue/PAP-280/build-the-agent-runtime-sandbox-per-session-container-worktree-mount) |
| [`agents/session-observability`](agents/session-observability.md) | Add agent session observability: heartbeats, stuck-session detection, per-session OTel spans and a `/status` contract shared by the org chart, board cards and cost controls |  | [PAP-288](https://linear.app/paperos/issue/PAP-288/add-agent-session-observability-heartbeats-stuck-session-detection-per) |
| [`security/agent-deny-list`](agents/security-agent-deny-list.md) | Define and enforce the agent destructive-action deny list: policy file, PreToolUse hook, MCP destructive-scope interception with Needs Justin escalation, and server-side backstops |  | [PAP-298](https://linear.app/paperos/issue/PAP-298/define-and-enforce-the-agent-destructive-action-deny-list-policy-file) |
| [`security/prompt-injection`](agents/security-prompt-injection.md) | Build prompt-injection defences for agent sessions: trust tiers for issues, comments and PRs, untrusted-content wrapping, actor-verified instructions, canary tokens and an injection eval suite |  | [PAP-299](https://linear.app/paperos/issue/PAP-299/build-prompt-injection-defences-for-agent-sessions-trust-tiers-for) |

### Spec Builder (`spec-builder`, 13)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`gp/spec-builder/app-interview`](spec-builder/gp-spec-builder-app-interview.md) | Write the app interview skill: one paragraph idea to `app.spec.yaml` (business profile, audiences, entities, navigation, modules) in at most six questions with `--yes` defaults |  | [PAP-360](https://linear.app/paperos/issue/PAP-360/write-the-app-interview-skill-one-paragraph-idea-to-appspecyaml) |
| [`gp/spec-builder/entity-pages`](spec-builder/gp-spec-builder-entity-pages.md) | Build entity-derived page specs: `pnpm spec gen:entity-pages` derives list, detail, form and settings pages per entity and audience with view specs, comment anchors and access rules |  | [PAP-361](https://linear.app/paperos/issue/PAP-361/build-entity-derived-page-specs-pnpm-spec-genentity-pages-derives-list) |
| [`gp/spec-builder/gen-pipeline`](spec-builder/gp-spec-builder-gen-pipeline.md) | Build `paperos gen`: the whole-app generation pipeline that runs every generator in dependency order with a manifest, incremental cache, deterministic output and a `--check` drift mode |  | [PAP-362](https://linear.app/paperos/issue/PAP-362/build-paperos-gen-the-whole-app-generation-pipeline-that-runs-every) |
| [`spec-builder/data-section/example`](spec-builder/data-section-example.md) | Data section: `customer-invoices` end to end with live sync, second-context and offline tests | PAP-119 | [PAP-313](https://linear.app/paperos/issue/PAP-313/data-section-customer-invoices-end-to-end-with-live-sync-second) |
| [`spec-builder/data-section/generator`](spec-builder/data-section-generator.md) | Data section: typed hook generator for server, live and local sync modes | PAP-119 | [PAP-312](https://linear.app/paperos/issue/PAP-312/data-section-typed-hook-generator-for-server-live-and-local-sync-modes) |
| [`spec-builder/data-section/schema`](spec-builder/data-section-schema.md) | Data section: Zod schema, shared FilterTree import and validator rules | PAP-119 | [PAP-311](https://linear.app/paperos/issue/PAP-311/data-section-zod-schema-shared-filtertree-import-and-validator-rules) |
| [`spec-builder/layout-codegen/examples`](spec-builder/layout-codegen-examples.md) | Layout codegen: generate the three example specs, screenshot seven widths and pass conformance with zero manual edits | PAP-120 | [PAP-316](https://linear.app/paperos/issue/PAP-316/layout-codegen-generate-the-three-example-specs-screenshot-seven) |
| [`spec-builder/layout-codegen/templates`](spec-builder/layout-codegen-templates.md) | Layout codegen: Printer, route and view templates, two-file ownership and determinism | PAP-120 | [PAP-314](https://linear.app/paperos/issue/PAP-314/layout-codegen-printer-route-and-view-templates-two-file-ownership-and) |
| [`spec-builder/layout-codegen/wiring`](spec-builder/layout-codegen-wiring.md) | Layout codegen: state switch, layout slot mapping, action binding and search-param schema | PAP-120 | [PAP-315](https://linear.app/paperos/issue/PAP-315/layout-codegen-state-switch-layout-slot-mapping-action-binding-and) |
| [`spec-builder/spec-editor-ui/form`](spec-builder/spec-editor-ui-form.md) | Spec editor: form view, component tree editor and two-way sync with YAML preserving comments | PAP-124 | [PAP-377](https://linear.app/paperos/issue/PAP-377/spec-editor-form-view-component-tree-editor-and-two-way-sync-with-yaml) |
| [`spec-builder/spec-editor-ui/preview`](spec-builder/spec-editor-ui-preview.md) | Spec editor: live preview at selectable widths, flow-graph tab, keyboard shortcuts and accessibility polish | PAP-124 | [PAP-378](https://linear.app/paperos/issue/PAP-378/spec-editor-live-preview-at-selectable-widths-flow-graph-tab-keyboard) |
| [`spec-builder/spec-editor-ui/yaml`](spec-builder/spec-editor-ui-yaml.md) | Spec editor: spec list, CodeMirror YAML editor with worker validation and save-to-PR flow | PAP-124 | [PAP-376](https://linear.app/paperos/issue/PAP-376/spec-editor-spec-list-codemirror-yaml-editor-with-worker-validation) |
| [`spec-builder/spec-i18n`](spec-builder/spec-i18n.md) | Add spec-level internationalisation: message IDs for spec copy fields, extraction into catalogs, pseudo-locale validation rule |  | [PAP-375](https://linear.app/paperos/issue/PAP-375/add-spec-level-internationalisation-message-ids-for-spec-copy-fields) |

### In-App Collaboration & Knowledge (`collab`, 11)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`collab/canvas/filters-export-perf`](collab/canvas-filters-export-perf.md) | Filters, deep links, export and 300-node performance run | PAP-132 | [PAP-322](https://linear.app/paperos/issue/PAP-322/filters-deep-links-export-and-300-node-performance-run) |
| [`collab/canvas/nodes-edges-loader`](collab/canvas-nodes-edges-loader.md) | Canvas node and edge types with graph loader | PAP-132 | [PAP-320](https://linear.app/paperos/issue/PAP-320/canvas-node-and-edge-types-with-graph-loader) |
| [`collab/canvas/yjs-overlay`](collab/canvas-yjs-overlay.md) | Collaborative overlay: notes, regions, overrides in Yjs | PAP-132 | [PAP-321](https://linear.app/paperos/issue/PAP-321/collaborative-overlay-notes-regions-overrides-in-yjs) |
| [`collab/comments/live-deeplinks-linear`](collab/comments-live-deeplinks-linear.md) | Live updates, deep links and Linear escalation | PAP-131 | [PAP-319](https://linear.app/paperos/issue/PAP-319/live-updates-deep-links-and-linear-escalation) |
| [`collab/comments/panel-pins-composer`](collab/comments-panel-pins-composer.md) | Comment panel, pins and composer UI | PAP-131 | [PAP-318](https://linear.app/paperos/issue/PAP-318/comment-panel-pins-and-composer-ui) |
| [`collab/comments/schema-rls-rpc`](collab/comments-schema-rls-rpc.md) | Comment schema, anchors, RLS and oRPC procedures | PAP-131 | [PAP-317](https://linear.app/paperos/issue/PAP-317/comment-schema-anchors-rls-and-orpc-procedures) |
| [`collab/in-app-help`](collab/in-app-help.md) | Add contextual in-app help: help panel bound to page spec `purpose` and docs deep links, first-visit product tour, keyboard hint overlay |  | [PAP-380](https://linear.app/paperos/issue/PAP-380/add-contextual-in-app-help-help-panel-bound-to-page-spec-purpose-and) |
| [`collab/notifications/digests-quiet-hours`](collab/notifications-digests-quiet-hours.md) | Digests, quiet hours and burst collapse | PAP-136 | [PAP-324](https://linear.app/paperos/issue/PAP-324/digests-quiet-hours-and-burst-collapse) |
| [`collab/notifications/inbox-preferences`](collab/notifications-inbox-preferences.md) | Inbox UI, bell badge and preferences page | PAP-136 | [PAP-323](https://linear.app/paperos/issue/PAP-323/inbox-ui-bell-badge-and-preferences-page) |
| [`collab/notifications/slack-channel`](collab/notifications-slack-channel.md) | Slack channel and tenant Slack configuration | PAP-136 | [PAP-325](https://linear.app/paperos/issue/PAP-325/slack-channel-and-tenant-slack-configuration) |
| [`collab/runtime-docs-store`](collab/runtime-docs-store.md) | Build a runtime docs store for tenant-authored documents: Yjs-backed pages in Postgres with the same routes, search registration and comment anchors as repo MDX |  | [PAP-379](https://linear.app/paperos/issue/PAP-379/build-a-runtime-docs-store-for-tenant-authored-documents-yjs-backed) |

### Multiplayer & Realtime (`realtime`, 4)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`realtime/push-transport`](realtime/push-transport.md) | Build the push transport: server-to-client notification and job-progress channel (Electric shape or SSE) plus Web Push and Tauri mobile push (APNs/FCM) |  | [PAP-381](https://linear.app/paperos/issue/PAP-381/build-the-push-transport-server-to-client-notification-and-job) |
| [`realtime/record-sync/live-hooks-registry`](realtime/record-sync-live-hooks-registry.md) | Live record hooks and shape registry additions | PAP-143 | [PAP-326](https://linear.app/paperos/issue/PAP-326/live-record-hooks-and-shape-registry-additions) |
| [`realtime/record-sync/reconciler`](realtime/record-sync-reconciler.md) | Reconciler for optimistic writes and conflict events | PAP-143 | [PAP-327](https://linear.app/paperos/issue/PAP-327/reconciler-for-optimistic-writes-and-conflict-events) |
| [`realtime/record-sync/resubscribe-lag`](realtime/record-sync-resubscribe-lag.md) | Permission-driven resubscribe and lag measurement | PAP-143 | [PAP-328](https://linear.app/paperos/issue/PAP-328/permission-driven-resubscribe-and-lag-measurement) |

### Multi-Input Control & Accessibility (`input`, 6)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`input/commands/agent-endpoint-defaults`](input/commands-agent-endpoint-defaults.md) | Agent execution endpoint, telemetry and default commands | PAP-151 | [PAP-291](https://linear.app/paperos/issue/PAP-291/agent-execution-endpoint-telemetry-and-default-commands) |
| [`input/commands/palette-help-ui`](input/commands-palette-help-ui.md) | Command palette and help sheet UI | PAP-151 | [PAP-290](https://linear.app/paperos/issue/PAP-290/command-palette-and-help-sheet-ui) |
| [`input/commands/registry-core`](input/commands-registry-core.md) | Command registry core, scoping and chord matcher | PAP-151 | [PAP-289](https://linear.app/paperos/issue/PAP-289/command-registry-core-scoping-and-chord-matcher) |
| [`input/dnd/kanban-grid-dropzone-crosswindow`](input/dnd-kanban-grid-dropzone-crosswindow.md) | KanbanDnd, SortableGrid, DropZone and cross-window drag | PAP-155 | [PAP-331](https://linear.app/paperos/issue/PAP-331/kanbandnd-sortablegrid-dropzone-and-cross-window-drag) |
| [`input/dnd/keyboard-announcements`](input/dnd-keyboard-announcements.md) | Keyboard alternative, announcements and focus restore | PAP-155 | [PAP-330](https://linear.app/paperos/issue/PAP-330/keyboard-alternative-announcements-and-focus-restore) |
| [`input/dnd/sensors-sortable-list`](input/dnd-sensors-sortable-list.md) | dnd-kit sensors on the input abstraction and SortableList | PAP-155 | [PAP-329](https://linear.app/paperos/issue/PAP-329/dnd-kit-sensors-on-the-input-abstraction-and-sortablelist) |

### Table & Views Engine (`tables`, 24)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`gap/tables/bulk-trash`](tables/tables-bulk-trash.md) | Build bulk operations, trash and restore: multi-row edit and delete with server batching, soft-delete trash with 30-day restore, undo toast |  | [PAP-334](https://linear.app/paperos/issue/PAP-334/build-bulk-operations-trash-and-restore-multi-row-edit-and-delete-with) |
| [`gap/tables/record-detail`](tables/tables-record-detail.md) | Build record-level features shared by every module: record detail page and panel routing, activity timeline, attachments tab, per-record comments and field history with undo |  | [PAP-333](https://linear.app/paperos/issue/PAP-333/build-record-level-features-shared-by-every-module-record-detail-page) |
| [`gap/tables/schema-editor`](tables/tables-schema-editor.md) | Build the custom dataset schema editor: create tables and fields in-app, reorder, field type conversion with a lossiness report and background backfill |  | [PAP-332](https://linear.app/paperos/issue/PAP-332/build-the-custom-dataset-schema-editor-create-tables-and-fields-in-app) |
| [`tables/automations/actions`](tables/automations-actions.md) | Action catalogue with scope classes, template expressions, connector.call, agent.run, delay and branch | PAP-174 | [PAP-389](https://linear.app/paperos/issue/PAP-389/action-catalogue-with-scope-classes-template-expressions-connectorcall) |
| [`tables/automations/builder-log-templates`](tables/automations-builder-log-templates.md) | Automation builder page, test run, run log with replay, five starter templates and import hooks | PAP-174 | [PAP-390](https://linear.app/paperos/issue/PAP-390/automation-builder-page-test-run-run-log-with-replay-five-starter) |
| [`tables/automations/model-triggers`](tables/automations-model-triggers.md) | Automation schema, trigger sources and the run runtime with idempotency, loop guard, limits and circuit breaker | PAP-174 | [PAP-388](https://linear.app/paperos/issue/PAP-388/automation-schema-trigger-sources-and-the-run-runtime-with-idempotency) |
| [`tables/compiler/api-hook-bench`](tables/compiler-api-hook-bench.md) | oRPC procedures, useViewQuery hook and the 100k-row benchmark | PAP-163 | [PAP-337](https://linear.app/paperos/issue/PAP-337/orpc-procedures-useviewquery-hook-and-the-100k-row-benchmark) |
| [`tables/compiler/core`](tables/compiler-core.md) | Compiler core: dataset resolution, per-type filter ops, sorts and signed keyset cursors | PAP-163 | [PAP-335](https://linear.app/paperos/issue/PAP-335/compiler-core-dataset-resolution-per-type-filter-ops-sorts-and-signed) |
| [`tables/compiler/groups-shapes`](tables/compiler-groups-shapes.md) | Groups, aggregates and Electric shape eligibility | PAP-163 | [PAP-336](https://linear.app/paperos/issue/PAP-336/groups-aggregates-and-electric-shape-eligibility) |
| [`tables/dashboard/blocks-crossfilter`](tables/dashboard-blocks-crossfilter.md) | Block kinds, cross-filter bus, filter bar, params and deep links | PAP-173 | [PAP-386](https://linear.app/paperos/issue/PAP-386/block-kinds-cross-filter-bus-filter-bar-params-and-deep-links) |
| [`tables/dashboard/model-grid`](tables/dashboard-model-grid.md) | Dashboard tables, layout engine, breakpoint layouts and drag or resize with keyboard moves | PAP-173 | [PAP-385](https://linear.app/paperos/issue/PAP-385/dashboard-tables-layout-engine-breakpoint-layouts-and-drag-or-resize) |
| [`tables/dashboard/print-perf-spec`](tables/dashboard-print-perf-spec.md) | Lazy loading, error boundaries, print route, page-spec hook and permission tiles | PAP-173 | [PAP-387](https://linear.app/paperos/issue/PAP-387/lazy-loading-error-boundaries-print-route-page-spec-hook-and) |
| [`tables/fields/choice-people-attachment`](tables/fields-choice-people-attachment.md) | Choice, people and attachment types (select, multiSelect, user, attachment) with FieldSettingsPanel | PAP-164 | [PAP-339](https://linear.app/paperos/issue/PAP-339/choice-people-and-attachment-types-select-multiselect-user-attachment) |
| [`tables/fields/framework-primitives`](tables/fields-framework-primitives.md) | Field type framework and primitive types (text, number, currency, percent, date, checkbox, rating, url, email, phone) | PAP-164 | [PAP-338](https://linear.app/paperos/issue/PAP-338/field-type-framework-and-primitive-types-text-number-currency-percent) |
| [`tables/fields/relational-computed`](tables/fields-relational-computed.md) | Relational and computed types (relation, lookup, rollup, formula storage) and convertFieldType with lossiness report | PAP-164 | [PAP-340](https://linear.app/paperos/issue/PAP-340/relational-and-computed-types-relation-lookup-rollup-formula-storage) |
| [`tables/formula/evaluator-editor`](tables/formula-evaluator-editor.md) | TypeScript evaluator with function implementations and the CodeMirror formula editor | PAP-171 | [PAP-383](https://linear.app/paperos/issue/PAP-383/typescript-evaluator-with-function-implementations-and-the-codemirror) |
| [`tables/formula/parser-typecheck`](tables/formula-parser-typecheck.md) | Lexer, Pratt parser, AST, type checker and the defineFunction catalogue | PAP-171 | [PAP-382](https://linear.app/paperos/issue/PAP-382/lexer-pratt-parser-ast-type-checker-and-the-definefunction-catalogue) |
| [`tables/formula/sql-cache`](tables/formula-sql-cache.md) | SQL compiler, formula_cache fallback job and the dependency graph | PAP-171 | [PAP-384](https://linear.app/paperos/issue/PAP-384/sql-compiler-formula-cache-fallback-job-and-the-dependency-graph) |
| [`tables/grid/columns-groups-panel`](tables/grid-columns-groups-panel.md) | Column operations, grouping headers, aggregate footer and RecordPanel | PAP-165 | [PAP-343](https://linear.app/paperos/issue/PAP-343/column-operations-grouping-headers-aggregate-footer-and-recordpanel) |
| [`tables/grid/core`](tables/grid-core.md) | Grid core: virtualisation, data binding, selection model and keyboard navigation | PAP-165 | [PAP-341](https://linear.app/paperos/issue/PAP-341/grid-core-virtualisation-data-binding-selection-model-and-keyboard) |
| [`tables/grid/editing-clipboard-bulk`](tables/grid-editing-clipboard-bulk.md) | Inline editing with optimistic commit, TSV clipboard ranges and the bulk actions bar | PAP-165 | [PAP-342](https://linear.app/paperos/issue/PAP-342/inline-editing-with-optimistic-commit-tsv-clipboard-ranges-and-the) |
| [`tables/time/engine-calendar`](tables/time-engine-calendar.md) | TimeScale engine, range compilation, overlap packing and the calendar view (month, week, day, agenda) | PAP-168 | [PAP-344](https://linear.app/paperos/issue/PAP-344/timescale-engine-range-compilation-overlap-packing-and-the-calendar) |
| [`tables/time/gantt`](tables/time-gantt.md) | Gantt view: frozen left grid, dependency arrows, critical path, progress and working days | PAP-168 | [PAP-346](https://linear.app/paperos/issue/PAP-346/gantt-view-frozen-left-grid-dependency-arrows-critical-path-progress) |
| [`tables/time/timeline`](tables/time-timeline.md) | Timeline view: two-axis virtualised canvas, lanes, zoom levels and bar editing | PAP-168 | [PAP-345](https://linear.app/paperos/issue/PAP-345/timeline-view-two-axis-virtualised-canvas-lanes-zoom-levels-and-bar) |

### Business Core: Payments, Finance & Payroll (`business-core`, 12)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`business-core/invoicing/model-statemachine`](business-core/invoicing-model-statemachine.md) | Document model, lines, sequences, server-side totals, state machine, quote conversion, void and credit notes | PAP-180 | [PAP-395](https://linear.app/paperos/issue/PAP-395/document-model-lines-sequences-server-side-totals-state-machine-quote) |
| [`business-core/invoicing/pdf-paypage`](business-core/invoicing-pdf-paypage.md) | Branded PDF rendering, public /pay and /doc pages, Stripe Checkout on platform or connected account, receipts | PAP-180 | [PAP-396](https://linear.app/paperos/issue/PAP-396/branded-pdf-rendering-public-pay-and-doc-pages-stripe-checkout-on) |
| [`business-core/invoicing/postings-portal-emails`](business-core/invoicing-postings-portal-emails.md) | Posting rules invoice.*, manual payments, reminders job, customer portal invoice list and email templates | PAP-180 | [PAP-397](https://linear.app/paperos/issue/PAP-397/posting-rules-invoice-manual-payments-reminders-job-customer-portal) |
| [`business-core/ledger/hashchain-reversal-close`](business-core/ledger-hashchain-reversal-close.md) | Hash chain with nightly verification, ledger.reverse and the period close and lock workflow | PAP-179 | [PAP-393](https://linear.app/paperos/issue/PAP-393/hash-chain-with-nightly-verification-ledgerreverse-and-the-period) |
| [`business-core/ledger/journal-constraints`](business-core/ledger-journal-constraints.md) | Journal tables, balance trigger, immutability trigger, gapless numbering and account balances | PAP-179 | [PAP-392](https://linear.app/paperos/issue/PAP-392/journal-tables-balance-trigger-immutability-trigger-gapless-numbering) |
| [`business-core/ledger/rules-ui-trialbalance`](business-core/ledger-rules-ui-trialbalance.md) | Posting rule registry with the first five rules, /finance/journal UI, trial balance and rebuildBalances | PAP-179 | [PAP-394](https://linear.app/paperos/issue/PAP-394/posting-rule-registry-with-the-first-five-rules-financejournal-ui) |
| [`business-core/payroll/adapter-contract`](business-core/payroll-adapter-contract.md) | Finalised PayrollProvider interface, first adapter with idempotency keys, webhook route and the adapter contract test suite | PAP-184 | [PAP-398](https://linear.app/paperos/issue/PAP-398/finalised-payrollprovider-interface-first-adapter-with-idempotency) |
| [`business-core/payroll/onboarding-sync`](business-core/payroll-onboarding-sync.md) | Payroll tables, company and employee onboarding via provider links, employee sync from fin_employee and status polling | PAP-184 | [PAP-399](https://linear.app/paperos/issue/PAP-399/payroll-tables-company-and-employee-onboarding-via-provider-links) |
| [`business-core/payroll/run-approve-post`](business-core/payroll-run-approve-post.md) | Payroll run flow, typed-total approval, webhook status transitions, ledger posting and the paystub portal page | PAP-184 | [PAP-400](https://linear.app/paperos/issue/PAP-400/payroll-run-flow-typed-total-approval-webhook-status-transitions) |
| [`gap/business-core/recurring-dunning`](business-core/business-core-recurring-dunning.md) | Build recurring tenant invoices and dunning: schedules, automatic reminders, late fees, payment retry for tenant-to-customer billing |  | folded into PAP-180 |
| [`gap/business-core/usage-metering`](business-core/business-core-usage-metering.md) | Build usage metering and metered billing: usage events (agent sessions, storage, seats, API calls) aggregated per tenant, Stripe usage records, limit warnings |  | [PAP-391](https://linear.app/paperos/issue/PAP-391/build-usage-metering-and-metered-billing-usage-events-agent-sessions) |
| [`security/pci-posture`](business-core/security-pci-posture.md) | Document and enforce the PCI SAQ-A posture: Stripe-hosted card entry only, a Semgrep rule against card-data fields, restricted Stripe keys per service, live-key custody through Needs Justin, and the quarterly SAQ-A checklist |  | [PAP-359](https://linear.app/paperos/issue/PAP-359/document-and-enforce-the-pci-saq-a-posture-stripe-hosted-card-entry) |

### Growth: Marketing, Outreach & CRM (`growth`, 13)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`gap/growth/consent-centre`](growth/growth-consent-centre.md) | Build the consent and marketing compliance centre: preference page, unsubscribe centre, double opt-in, suppression list shared by outreach, notifications and forms, GDPR/CAN-SPAM/TCPA rules |  | folded into PAP-187 |
| [`growth/outreach/compliance-warmup-replies`](growth/outreach-compliance-warmup-replies.md) | Consent and suppression checks, quiet hours, unsubscribe and STOP handling, warmup stages, bounce handling and reply detection | PAP-191 | [PAP-405](https://linear.app/paperos/issue/PAP-405/consent-and-suppression-checks-quiet-hours-unsubscribe-and-stop) |
| [`growth/outreach/model-worker`](growth/outreach-model-worker.md) | Outreach schema, provider interface with Resend and Twilio adapters, scheduler worker, template rendering and idempotency | PAP-191 | [PAP-404](https://linear.app/paperos/issue/PAP-404/outreach-schema-provider-interface-with-resend-and-twilio-adapters) |
| [`growth/outreach/ui`](growth/outreach-ui.md) | Sequence builder, template editor with preview and test send, enrolments grid and domain setup wizard | PAP-191 | [PAP-406](https://linear.app/paperos/issue/PAP-406/sequence-builder-template-editor-with-preview-and-test-send-enrolments) |
| [`growth/referral/codes-attribution`](growth/referral-codes-attribution.md) | Referral programs, codes, /r/{code} route, attribution window and the qualification worker | PAP-196 | [PAP-407](https://linear.app/paperos/issue/PAP-407/referral-programs-codes-rcode-route-attribution-window-and-the) |
| [`growth/referral/portal-console-ui`](growth/referral-portal-console-ui.md) | Portal referral page, console program and referral grids and the rewards approval queue | PAP-196 | [PAP-409](https://linear.app/paperos/issue/PAP-409/portal-referral-page-console-program-and-referral-grids-and-the) |
| [`growth/referral/rewards-payouts-ledger`](growth/referral-rewards-payouts-ledger.md) | Reward rules, fraud rules, approval, Stripe Connect transfers, ledger postings and monthly statements | PAP-196 | [PAP-408](https://linear.app/paperos/issue/PAP-408/reward-rules-fraud-rules-approval-stripe-connect-transfers-ledger) |
| [`growth/social/adapter-mock-x`](growth/social-adapter-mock-x.md) | Adapter interface, mock adapter, X API v2 adapter and the pg-boss publishing worker | PAP-190 | [PAP-402](https://linear.app/paperos/issue/PAP-402/adapter-interface-mock-adapter-x-api-v2-adapter-and-the-pg-boss) |
| [`growth/social/adapters-review-gated`](growth/social-adapters-review-gated.md) | LinkedIn, Instagram, TikTok and YouTube adapters in dryRun with payload snapshots, OAuth connect flows and re-auth banners | PAP-190 | [PAP-403](https://linear.app/paperos/issue/PAP-403/linkedin-instagram-tiktok-and-youtube-adapters-in-dryrun-with-payload) |
| [`growth/social/model-queue-calendar`](growth/social-model-queue-calendar.md) | Social schema, approval state machine, composer with per-platform variants, approval queue and calendar | PAP-190 | [PAP-401](https://linear.app/paperos/issue/PAP-401/social-schema-approval-state-machine-composer-with-per-platform) |
| [`growth/support/chat-notes`](growth/support-chat-notes.md) | Portal SupportChat widget with live sync and presence, unauthenticated email capture and internal notes on comment threads | PAP-197 | [PAP-411](https://linear.app/paperos/issue/PAP-411/portal-supportchat-widget-with-live-sync-and-presence-unauthenticated) |
| [`growth/support/console-ui`](growth/support-console-ui.md) | Three-pane inbox on a saved list view, conversation view, contact sidebar, assignment, snooze, macros, shortcuts and metrics | PAP-197 | [PAP-412](https://linear.app/paperos/issue/PAP-412/three-pane-inbox-on-a-saved-list-view-conversation-view-contact) |
| [`growth/support/email-threading`](growth/support-email-threading.md) | Support schema, inbound email parsing, threading heuristics, HTML sanitising, contact matching and outbound replies | PAP-197 | [PAP-410](https://linear.app/paperos/issue/PAP-410/support-schema-inbound-email-parsing-threading-heuristics-html) |

### Migration & Import Tools (`migration`, 20)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`child/PAP-199/0`](migration/child-pap-199-0.md) | Connector interface, mapping model and import engine (`SourceConnector`, `import_mapping`, batching, resumability, fixture connector) | PAP-199 | [PAP-347](https://linear.app/paperos/issue/PAP-347/connector-interface-mapping-model-and-import-engine-sourceconnector) |
| [`child/PAP-199/1`](migration/child-pap-199-1.md) | Dry run, commit and rollback semantics: transaction-rolled dry run, `import_run_item` before-state, exact rollback with conflict listing | PAP-199 | [PAP-348](https://linear.app/paperos/issue/PAP-348/dry-run-commit-and-rollback-semantics-transaction-rolled-dry-run) |
| [`child/PAP-199/2`](migration/child-pap-199-2.md) | Type inference, mapping wizard UI and run history with per-item drill-down and rollback button | PAP-199 | [PAP-349](https://linear.app/paperos/issue/PAP-349/type-inference-mapping-wizard-ui-and-run-history-with-per-item-drill) |
| [`child/PAP-202/0`](migration/child-pap-202-0.md) | Airtable connector: OAuth and PAT auth, metadata discovery, record streaming with 5 rps token bucket and expiring-attachment fetch | PAP-202 | [PAP-414](https://linear.app/paperos/issue/PAP-414/airtable-connector-oauth-and-pat-auth-metadata-discovery-record) |
| [`child/PAP-202/1`](migration/child-pap-202-1.md) | Airtable field mapping: every field type to PaperOS types, relations two-pass, lookups and rollups third pass, formula translation report | PAP-202 | [PAP-415](https://linear.app/paperos/issue/PAP-415/airtable-field-mapping-every-field-type-to-paperos-types-relations-two) |
| [`child/PAP-202/2`](migration/child-pap-202-2.md) | Airtable view mapping and wizard steps: filterByFormula parsing, kanban, calendar, gallery and form views, side-by-side review | PAP-202 | [PAP-416](https://linear.app/paperos/issue/PAP-416/airtable-view-mapping-and-wizard-steps-filterbyformula-parsing-kanban) |
| [`child/PAP-203/0`](migration/child-pap-203-0.md) | Notion connector and database property mapping to tables (OAuth, search discovery, databases.query streaming at 3 rps, relations and rollups) | PAP-203 | [PAP-417](https://linear.app/paperos/issue/PAP-417/notion-connector-and-database-property-mapping-to-tables-oauth-search) |
| [`child/PAP-203/1`](migration/child-pap-203-1.md) | Notion block converter to MDX and Tiptap JSON: all block types, media upload before URL expiry, internal link rewriting | PAP-203 | [PAP-418](https://linear.app/paperos/issue/PAP-418/notion-block-converter-to-mdx-and-tiptap-json-all-block-types-media) |
| [`child/PAP-203/2`](migration/child-pap-203-2.md) | Notion hierarchy, page tree picker, docs placement and conversion report | PAP-203 | [PAP-419](https://linear.app/paperos/issue/PAP-419/notion-hierarchy-page-tree-picker-docs-placement-and-conversion-report) |
| [`child/PAP-205/0`](migration/child-pap-205-0.md) | Export archive format v1.0 and streaming export job: manifest, JSON Schemas, table, docs, files, comments, PM, CRM, ledger and audit writers | PAP-205 | [PAP-420](https://linear.app/paperos/issue/PAP-420/export-archive-format-v10-and-streaming-export-job-manifest-json) |
| [`child/PAP-205/1`](migration/child-pap-205-1.md) | Export UI, weekly scheduling to S3 or Google Drive with encryption, signed download links, history and audit | PAP-205 | [PAP-421](https://linear.app/paperos/issue/PAP-421/export-ui-weekly-scheduling-to-s3-or-google-drive-with-encryption) |
| [`child/PAP-205/2`](migration/child-pap-205-2.md) | Round-trip `paperos` connector: import a PaperOS archive into an empty tenant and verify counts and hashes table by table | PAP-205 | [PAP-422](https://linear.app/paperos/issue/PAP-422/round-trip-paperos-connector-import-a-paperos-archive-into-an-empty) |
| [`child/PAP-206/0`](migration/child-pap-206-0.md) | Stripe connector and mapping: customers to CRM, catalog and subscriptions to billing, invoices, fees, tax, refunds and payouts to ledger postings | PAP-206 | [PAP-423](https://linear.app/paperos/issue/PAP-423/stripe-connector-and-mapping-customers-to-crm-catalog-and) |
| [`child/PAP-206/1`](migration/child-pap-206-1.md) | QuickBooks Online and Xero connectors: chart of accounts, opening balances on a conversion date, optional journal and invoice history | PAP-206 | [PAP-424](https://linear.app/paperos/issue/PAP-424/quickbooks-online-and-xero-connectors-chart-of-accounts-opening) |
| [`child/PAP-206/2`](migration/child-pap-206-2.md) | Finance import wizard: conversion date, account mapping review, duplicate customer resolution, trial balance gate and reversing rollback | PAP-206 | [PAP-425](https://linear.app/paperos/issue/PAP-425/finance-import-wizard-conversion-date-account-mapping-review-duplicate) |
| [`child/PAP-207/0`](migration/child-pap-207-0.md) | Template pack format, Zod schema, lint, and the `template` applier connector with conflict strategies, composition and upgrade | PAP-207 | [PAP-426](https://linear.app/paperos/issue/PAP-426/template-pack-format-zod-schema-lint-and-the-template-applier) |
| [`child/PAP-207/1`](migration/child-pap-207-1.md) | Author the five business packs (agency, retail, SaaS, clinic, restaurant) with page specs, views, pipelines, charts of accounts, sample data and starter docs | PAP-207 | [PAP-427](https://linear.app/paperos/issue/PAP-427/author-the-five-business-packs-agency-retail-saas-clinic-restaurant) |
| [`child/PAP-207/2`](migration/child-pap-207-2.md) | Template gallery in onboarding and settings: cards with previews, dry-run diff, apply with or without sample data, remove sample data | PAP-207 | [PAP-428](https://linear.app/paperos/issue/PAP-428/template-gallery-in-onboarding-and-settings-cards-with-previews-dry) |
| [`migration/monday-hubspot-recipes`](migration/monday-hubspot-recipes.md) | Import Monday and HubSpot through guided CSV export recipes with preset mappings (no API connector in this build) |  | [PAP-413](https://linear.app/paperos/issue/PAP-413/import-monday-and-hubspot-through-guided-csv-export-recipes-with) |
| [`migration/test-accounts`](migration/test-accounts.md) | Provision importer test accounts and fixture workspaces: Airtable demo base, Notion test workspace, ClickUp workspace, Stripe test account, QuickBooks sandbox, Xero demo, Google OAuth app; one Needs Justin item |  | folded into PAP-198 |

### Library Discovery & Integration (`libraries`, 9)

| Key | Title | Parent | Linear issue |
|---|---|---|---|
| [`child/PAP-213/0`](libraries/child-pap-213-0.md) | Table library spike and ADR: TanStack Table plus Virtual, AG Grid Community, Glide Data Grid and react-data-grid at 100k rows | PAP-213 | [PAP-292](https://linear.app/paperos/issue/PAP-292/table-library-spike-and-adr-tanstack-table-plus-virtual-ag-grid) |
| [`child/PAP-213/1`](libraries/child-pap-213-1.md) | Chart and map library spikes and ADRs: ECharts, visx, Recharts, Observable Plot, Nivo, Chart.js; MapLibre GL and Leaflet with self-hosted tiles | PAP-213 | [PAP-293](https://linear.app/paperos/issue/PAP-293/chart-and-map-library-spikes-and-adrs-echarts-visx-recharts-observable) |
| [`child/PAP-213/2`](libraries/child-pap-213-2.md) | Canvas and editor shortlist: tldraw, React Flow, Excalidraw, Konva; Tiptap, BlockNote, Lexical, Plate, handed to collab research | PAP-213 | [PAP-294](https://linear.app/paperos/issue/PAP-294/canvas-and-editor-shortlist-tldraw-react-flow-excalidraw-konva-tiptap) |
| [`child/PAP-214/0`](libraries/child-pap-214-0.md) | Decide jobs, transactional email and PDF generation with Docker measurements: Inngest, Trigger.dev, BullMQ, pg-boss, Graphile Worker; Resend, Postmark, SES, Postal; Playwright PDF, react-pdf, Typst | PAP-214 | [PAP-295](https://linear.app/paperos/issue/PAP-295/decide-jobs-transactional-email-and-pdf-generation-with-docker) |
| [`child/PAP-214/1`](libraries/child-pap-214-1.md) | Decide search, observability, feature flags and object storage with a resource budget table under 6 GB | PAP-214 | [PAP-296](https://linear.app/paperos/issue/PAP-296/decide-search-observability-feature-flags-and-object-storage-with-a) |
| [`child/PAP-214/2`](libraries/child-pap-214-2.md) | Confirm validation and runtime, cross-link confirmed choices, consolidate ADRs, compose files and registry entries | PAP-214 | [PAP-297](https://linear.app/paperos/issue/PAP-297/confirm-validation-and-runtime-cross-link-confirmed-choices) |
| [`child/PAP-215/0`](libraries/child-pap-215-0.md) | Spike tables and PM products: NocoDB, Baserow and Plane with compose, seeded flows, metrics and scorecards | PAP-215 | [PAP-350](https://linear.app/paperos/issue/PAP-350/spike-tables-and-pm-products-nocodb-baserow-and-plane-with-compose) |
| [`child/PAP-215/1`](libraries/child-pap-215-1.md) | Spike growth products: Twenty CRM, Chatwoot, Listmonk and Postiz with compose, seeded flows, metrics and scorecards | PAP-215 | [PAP-351](https://linear.app/paperos/issue/PAP-351/spike-growth-products-twenty-crm-chatwoot-listmonk-and-postiz-with) |
| [`child/PAP-215/2`](libraries/child-pap-215-2.md) | Spike Cal.com and Formbricks, then write the OSS products mode ADR, borrow reference docs and embed integration contracts | PAP-215 | [PAP-352](https://linear.app/paperos/issue/PAP-352/spike-calcom-and-formbricks-then-write-the-oss-products-mode-adr) |
