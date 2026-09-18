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
