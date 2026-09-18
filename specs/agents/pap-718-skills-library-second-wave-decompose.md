---
identifier: "PAP-718"
title: "Skills library second wave: `decompose-brief`, `edge-case-plan`, `threat-model`, `flake-triage`, `context-pack`, `evidence-attach` and `plan-audit` as `.claude/skills` with lint, tests and `skills.json` entries"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Agent"]
milestone: "Sub-agents, skills and evals live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-79", "PAP-105"]
blocks: ["PAP-249", "PAP-306"]
key: "r4/agents/skills-library-second-wave"
url: "https://linear.app/paperos/issue/PAP-718/skills-library-second-wave-decompose-brief-edge-case-plan-threat-model"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:31.267Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-718: Skills library second wave: `decompose-brief`, `edge-case-plan`, `threat-model`, `flake-triage`, `context-pack`, `evidence-attach` and `plan-audit` as `.claude/skills` with lint, tests and `skills.json` entries

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

The character sheets promise skills no issue builds: Atlas's `decompose-brief`, Sentinel's `edge-case-plan`, `threat-model` and `flake-triage`, plus the round-4 helpers `context-pack` and `evidence-attach`, and PAP-306 assumes a `plan-audit` skill exists in the PAP-105 format. This issue writes the second wave in the same format, lint and test discipline as the first five, so every procedure a sheet names is a file a session can load.

**Scope**

* In: seven skills under `.claude/skills/<name>/` (`SKILL.md`, `scripts/`, `templates/`, `references/`), `skills.json` entries with `allowedCharacters`, script tests with the recorded fixtures kit, dry-run transcripts, `docs/agents/skills.md` update.
* Out: the first five skills (PAP-105), `author-spec` (PAP-118), the Scout scan routine (PAP-218), `request-approval` (deny-list child), skill discovery UI (PAP-134).

**Spec**

* `decompose-brief` (Atlas Decomposer): brief or epic to contract-valid issues with the eleven sections, sizes, `blocks` relations, Model and Effort labels from the cost rule and estimates from Size; `scripts/validate.ts` calls PAP-93 `validateIssue` before creating; refuses to create umbrellas without children.
* `edge-case-plan` (Sentinel Edge Case Hunter): the PAP-249 scenario classes and corpora as a procedure for a builder to pre-plan edge cases before Gate 4 runs; outputs a `ScenarioPlan` JSON the executor accepts.
* `threat-model` (Sentinel Security Auditor): STRIDE per trust boundary from PAP-219, emits a controls delta against `controls.yaml` and a `SEC-*` test list for the security regression suite.
* `flake-triage` (Sentinel): reads `flakes-delta.json` and `qa_flakes`, classifies `test-bug` versus `product-bug` with evidence, drafts the `Flaky:` issue body (PAP-90).
* `context-pack`: regenerates and checks a project's pack (round-4 issue) and prints the "read in full when" table; `evidence-attach`: wraps `pnpm evidence attach` (pm-linear round-4 issue) with the DoD evidence checklist parsed from the issue; `plan-audit`: the PAP-306 procedure with `scripts/snapshot.ts`, `checks.ts`, `report.ts` stubs the PAP-306 builder fills.
* Format rules from PAP-105: frontmatter with verb-first `description` and trigger phrases, body under 1500 words, deep detail in `references/`, last stdout line JSON `{ ok }`.

**Interface contract**

* Provides: seven skill folders, `skills.json` entries, scripts with the CLI contract, dry-run transcripts as PAP-110 fixtures.
* Consumes: PAP-105 format and lint, PAP-93 validator, PAP-249 classes, PAP-219 controls, PAP-90 flake shapes, PAP-239 findings, recorded fixtures kit for script tests.

**Definition of done**

* Seven skills pass `pnpm skills lint`; `skills.json` regenerated; every sheet-named skill now exists (table sheet to skill).
* Script tests green with recorded fixtures; dry-run transcripts on the toy repo show each skill loaded and followed; `decompose-brief` produces three issues that pass `contract:audit` (recording).
* Docs; changelog; Linear comment with transcript links.

**Test plan**

* Unit: lint per skill, `decompose-brief` validator gate, `flake-triage` classification on fixtures, JSON last-line contract.
* E2E: dry runs on the sandbox repo; `decompose-brief` against a rehearsal brief in Linear.

**Demo**

In a toy worktree run `pnpm skill decompose-brief fixtures/brief.md --dry-run` and read three contract-valid issue drafts with sizes and relations; run `pnpm skill flake-triage FL-12` and read the classification. Ninety seconds.

**Edge cases**

* Skill needs a character that is not allowed (`flake-triage` by Beacon): `skills.json` `allowedCharacters` refuses.
* `decompose-brief` output exceeds the Linear description limit: splits into children with an umbrella and says so.
* `threat-model` on a project without boundaries defined: emits a `boundaries missing` finding for PAP-219 rather than inventing controls.
* Skill body drifts past 1500 words: lint fails; content moves to `references/`.

**Dependencies**

Hard: PAP-105, PAP-79. Soft: PAP-93, PAP-249, PAP-219, PAP-90, PAP-239, PAP-683.

**Agent**

Builder: Quill (Page Spec Writer) with Sentinel and Atlas on their own skills. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/quality/recorded-http-fixtures-kit` = PAP-683.
