---
identifier: "PAP-552"
title: "Port usage tracking: derive `requires[].ports` from static analysis of `kernel.resolve` and `usePort` calls, compare with runtime `kernel.describe()` counters, and fail on manifest drift"
project: "module-system"
projectName: "Module System & Swap Tooling"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Shell swap drill passes"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-434", "PAP-439", "PAP-537"]
blocks: []
key: "r4/module-system/port-usage-tracking"
url: "https://linear.app/paperos/issue/PAP-552/port-usage-tracking-derive-requiresports-from-static-analysis-of"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:06.422Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-10-01"
cycle: null
---

# PAP-552: Port usage tracking: derive `requires[].ports` from static analysis of `kernel.resolve` and `usePort` calls, compare with runtime `kernel.describe()` counters, and fail on manifest drift

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

The compatibility matrix (PAP-440) can only say "which port change breaks whom" if `requires[].ports` is accurate, and today it is hand-maintained. Pact-style consumer contracts record what consumers actually use; here the code already says it. This issue derives the port list from the code, checks the manifest against it, and adds runtime counters so unused declarations are removed and undeclared usage is caught before a swap.

**Scope**

In:

* `tools/port-usage/scan.ts`: `ts-morph` scan of each module package for `port<...>("<contract>", "<Port>")` tokens, `kernel.resolve(<token>)`, `usePort(<token>)` and `describePort` references; emits `port-usage.json` `{ module: { contract: [ports] } }`.
* Manifest check `PORTS_DRIFT` in `pnpm modules:validate` (PAP-433 extension): declared but unused ports are warnings with an expiry; used but undeclared ports are errors with the manifest line to add; `--fix` writes the manifest.
* Runtime: `kernel.describe().usage` counters per `(consumer, contract, port)` since boot, exposed in `/dev/modules` (PAP-549) and exported nightly from staging (PAP-253) to `reports/port-usage/<date>.json` for the weekly re-audit (PAP-306).
* Matrix integration: PAP-440 per-port cells read `port-usage.json` when `requires[].ports` is absent.

Out: the matrix (PAP-440), the lint rules (PAP-439), dynamic resolution by string (refused by lint).

**Spec**

* Static scan is the source of truth for CI; runtime counters are advisory and never fail a build.
* Tokens must be constructed with literal strings; a computed token is a lint error (`PORT_TOKEN_DYNAMIC`) so the scan stays sound.
* Runtime under 10 s for the template.

**Interface contract**

Provides: `port-usage.json`, `PORTS_DRIFT`, `--fix`, runtime usage counters and nightly report; consumed by PAP-440 (per-port cells), PAP-306 (drift report), PAP-442 (step 3 lists real consumers), PAP-549.

Consumes: dependency lint infrastructure (PAP-439), kernel describe (PAP-434), validator (PAP-433), nightly staging (PAP-253, soft).

**Definition of done**

* Template scan produces the usage map; every manifest passes `PORTS_DRIFT` after `--fix`; a fixture module resolving an undeclared port fails validation with the line.
* Nightly report committed once; `docs/platform/manifest.md` ports section; Linear comment.

**Test plan**

* Unit: token extraction over fixture sources; drift classification; `--fix` idempotency; dynamic token lint.
* E2E: Gate 1 on a PR adding an undeclared `resolve` fails with `PORTS_DRIFT`.

**Demo**

Reviewer adds `kernel.resolve(LedgerPort)` to the CRM module, runs `pnpm modules:validate` and reads `PORTS_DRIFT crm requires @paperos/contract-business-core.LedgerPort (undeclared) — add to module.ts line 14`; `--fix` writes it. Under a minute.

**Edge cases**

* Port used only in tests: excluded (R11 test paths) and not required in the manifest.
* Port resolved through a helper in `@paperos/core`: the scan follows one level of re-export inside the same package.
* Runtime shows a port used by a consumer the static scan missed: reported as `SCAN_GAP` for the tool, never as a module error.

**Dependencies**

Hard: PAP-439, PAP-434. Soft: PAP-433, PAP-440, PAP-253, PAP-306.

**Agent**

Builder: Forge (Platform Engineer). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/module-system/kernel-devtools` = PAP-549.
