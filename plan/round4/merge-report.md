# Round 4 merge report (2026-09-18)

Files merged: 18. New issues in files: 335. After title de-duplication: 335. Dropped: 0.
Deferred: 95. With parent: 100 (gaps without parent: 235). Parents that are new issues: 0.
Amendments: 143. Cross-project suggestions: 93.
Existing blocks edges: 1224. New edges after resolution: 947. Combined graph acyclic: True.

## Per project

| project | new | deferred | children | amendments |
|---|---|---|---|---|
| app-shell | 21 | 6 | 10 | 8 |
| forge | 18 | 2 | 8 | 8 |
| module-system | 18 | 1 | 5 | 8 |
| data-layer | 23 | 2 | 13 | 8 |
| identity | 21 | 1 | 10 | 8 |
| realtime | 14 | 0 | 8 | 8 |
| tables | 28 | 9 | 13 | 8 |
| input | 14 | 1 | 4 | 8 |
| design-system | 18 | 0 | 6 | 8 |
| quality | 18 | 5 | 5 | 8 |
| pm-linear | 18 | 2 | 2 | 8 |
| agents | 16 | 2 | 6 | 8 |
| collab | 14 | 4 | 1 | 8 |
| spec-builder | 14 | 2 | 0 | 8 |
| libraries | 12 | 1 | 0 | 7 |
| business-core | 25 | 20 | 1 | 8 |
| growth | 23 | 20 | 4 | 8 |
| migration | 20 | 17 | 4 | 8 |

## Drops

- none

## Edge resolutions

- inversion: dropped PAP-108 -> r4/agents/session-end-guard-hooks (2026-09-25 > 2026-09-24); soft note appended to r4/agents/session-end-guard-hooks
- inversion: dropped PAP-195 -> r4/growth/email-broadcast-campaigns (2026-10-01 > 2026-09-30); soft note appended to r4/growth/email-broadcast-campaigns
- inversion: dropped PAP-239 -> r4/pm-linear/issue-attachments-and-evidence-bundle (2026-09-25 > 2026-09-22); soft note appended to r4/pm-linear/issue-attachments-and-evidence-bundle
- inversion: dropped PAP-288 -> r4/pm-linear/always-on-operations-and-morning-report (2026-09-25 > 2026-09-22); soft note appended to r4/pm-linear/always-on-operations-and-morning-report
- inversion: dropped PAP-308 -> r4/agents/injection-eval-suite-and-canaries (2026-09-25 > 2026-09-24); soft note appended to r4/agents/injection-eval-suite-and-canaries
- inversion: dropped r4/agents/anthropic-rate-limit-governor -> PAP-99 (2026-09-25 > 2026-09-22); PAP-99 is existing, soft note appended to r4/agents/anthropic-rate-limit-governor Dependencies
- inversion: dropped r4/agents/character-linear-identity-and-attribution -> PAP-281 (2026-09-24 > 2026-09-22); PAP-281 is existing, soft note appended to r4/agents/character-linear-identity-and-attribution Dependencies
- inversion: dropped r4/agents/claude-code-plugin-packaging -> PAP-22 (2026-09-25 > 2026-09-24); PAP-22 is existing, soft note appended to r4/agents/claude-code-plugin-packaging Dependencies
- inversion: dropped r4/agents/request-approval-mcp-interception-and-backstops -> PAP-96 (2026-09-24 > 2026-09-22); PAP-96 is existing, soft note appended to r4/agents/request-approval-mcp-interception-and-backstops Dependencies
- inversion: dropped r4/business-core/vendor-bills-and-ap-payments -> PAP-183 (2026-10-01 > 2026-09-29); PAP-183 is existing, soft note appended to r4/business-core/vendor-bills-and-ap-payments Dependencies
- inversion: dropped r4/quality/recorded-http-fixtures-kit -> PAP-105 (2026-09-25 > 2026-09-24); PAP-105 is existing, soft note appended to r4/quality/recorded-http-fixtures-kit Dependencies
- inversion: dropped r4/quality/recorded-http-fixtures-kit -> PAP-93 (2026-09-25 > 2026-09-20); PAP-93 is existing, soft note appended to r4/quality/recorded-http-fixtures-kit Dependencies
- inversion: dropped r4/quality/recorded-http-fixtures-kit -> PAP-94 (2026-09-25 > 2026-09-20); PAP-94 is existing, soft note appended to r4/quality/recorded-http-fixtures-kit Dependencies
- inversion: dropped r4/quality/recorded-http-fixtures-kit -> PAP-97 (2026-09-25 > 2026-09-22); PAP-97 is existing, soft note appended to r4/quality/recorded-http-fixtures-kit Dependencies

## Cycles

- none

## Validation problems

- none

## Label note

Linear's `Surface` label group is exclusive (`issueLabelCreate` rejected the first attempt with `labelIds not exclusive child labels` / "The label 'Customer' is in the same group as 'Staff'. Only one label in a group can be applied to an issue."), and every existing issue carries exactly one Surface label, so each new issue received the first entry of its `surfaces` list only; the remaining surfaces stay in the description text. The rejected batches created nothing (team issue count stayed at 493) and are logged in `changes/create-issues.json`.

## Phase 2 (cross-cutting file, 2026-09-18)

- **Cycle side effect reverted**: 362 issues that were Backlog at 12:50Z and had been moved to Todo by joining a cycle were set back to Backlog with `cycleId: null`; PAP-176, PAP-188 and PAP-555 (Ready for Claude) were put in C1; `teamUpdate { cycleIssueAutoAssignStarted: true }`. Rule: cycles hold in-flight work only; planned timing lives in due dates and Chunk labels.
- **5 projects created** (Planned, lead Justin Massion, priority 2, 2026-09-18 -> 2026-10-01): Tenant AI Assistant & Business Agents, Workflows, Approvals, Forms, Documents & E-Signature, Scheduling, Messaging & Customer Engagement, Commerce, Operations & Vertical Packs, Platform Operations, Analytics & Compliance; 3 milestones, 3 resource links, 1 project update each. `ProjectCreateInput.description` is capped at 255 characters (first attempt refused with `description must be shorter than or equal to 255 characters`), so the description was shortened at a clause boundary and the full text prepended to `content`. Fifth initiative **Operate, measure and comply** created (owner Justin Massion, target 2026-10-01) for platform-ops; assistant and workflows linked to "Product surfaces for every audience", engagement and commerce to "Business-ready for any business".
- **81 issues created**: 75 in the new projects (14 assistant, 15 workflows, 15 engagement, 16 commerce, 15 platform-ops; 56 deferred) and 6 of the 12 cross-project suggestions. Six cross-project entries were dropped as duplicates of phase-1 issues: `r4/data-layer/file-scanning-previews` (PAP-574 + PAP-577), `r4/business-core/fx-rates` (PAP-766), `r4/business-core/bank-feeds-reconciliation` (PAP-770 + PAP-771), `r4/tables/scheduled-view-delivery` (PAP-639), `r4/tables/address-geo-field` (PAP-622 + PAP-640), `r4/growth/bulk-campaigns` (PAP-799). `r4/platform-ops/conformance` and `r4/platform-ops/wire` were deferred with priority 3 in the file; set to 4. No cycleId on any new issue.
- **479 relations created**; 9 edges dropped: 7 milestone inversions (5 `wire` issues -> PAP-266, recurrence-engine -> PAP-344, PAP-63/PAP-124 -> settings-registry) and 1 deferred -> scheduled (PAP-221 -> compliance-controls), with soft-dependency notes (PAP-266 and PAP-344 amended). No new parents, so no umbrella hygiene was needed.
- **21 round-3 edge violations softened**: relations deleted (`issueRelationDelete`) and notes appended to both ends; see `verify.md` for the per-edge decisions and relation ids.
- **Triage**: 91 unfiled suggestions -> 6 covered by issues created today, 3 merged into near-duplicates, 82 filed as Triage issues (priority 3, provisional Type and Surface labels, skeleton descriptions); mapping in `unfiled-suggestions.md`.
