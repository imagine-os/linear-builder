---
identifier: "PAP-763"
title: "Adoption workflow CLI: `pnpm lib adopt <pkg>` chains facts, scorecard, ADR draft, registry entry, usage note and guardrails in one guided run"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Registry live"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-130", "PAP-209", "PAP-216", "PAP-757"]
blocks: []
key: "r4/libraries/adopt-workflow-cli"
url: "https://linear.app/paperos/issue/PAP-763/adoption-workflow-cli-pnpm-lib-adopt-pkg-chains-facts-scorecard-adr"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:39.804Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-763: Adoption workflow CLI: `pnpm lib adopt <pkg>` chains facts, scorecard, ADR draft, registry entry, usage note and guardrails in one guided run

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Borrow-before-build is five commands across four issues: `lib facts`, `lib score`, `adr new`, `lib add`, `lib notes scaffold`. An agent under a turn budget will skip two of them. One command that walks the steps in order, stops at the gates and leaves a PR-ready set of files is what makes the process the default rather than the exception.

**Scope**

In: `pnpm lib adopt <npm|crate:|image:> [--status trialing|adopted] [--issue PAP-n] [--yes]` in `tools/libraries/adopt.ts` (clack prompts) running: facts (PAP-209 plus PAP-755), scorecard scaffold with extras prompt and `pnpm lib score` validation, hard-gate check (license tier via PAP-211, advisories, types), ADR draft via `pnpm adr new` with the Alternatives table pre-filled, registry entry via `pnpm lib add`, usage note skeleton, guardrails rebuild, and a final `pnpm lib registry check`; `--yes` accepts defaults for agents; JSON last line `{ ok, files[], gates{}, nextSteps[] }`; skill `.claude/skills/adopt-library/SKILL.md` (PAP-105 format) wrapping it. Out: the underlying tools, decisions (the ADR still needs review).

**Spec**

* Gate behaviour: a failing hard gate stops the run before any file is written and prints the reason and the PAP-211 waiver path; `--force` writes with `status: candidate` and a `gatesFailed[]` note for review.
* Order is fixed; each step is idempotent so a re-run after fixing a gate continues from the first missing file.
* `adopted` requires an accepted ADR: the CLI can only write `trialing` or `candidate`; promotion to `adopted` stays with PAP-216's transition rule after ADR acceptance.
* Branch and commit: `lib/<id>` with PAP-46 trailers when `--issue` is given; the PR body lists the scorecard table (PAP-49 template).
* Budget: no model calls; under 60 s excluding network.

**Interface contract**

Provides: `pnpm lib adopt`, skill `adopt-library`, JSON result shape. Consumes: `lib facts|score` (PAP-209), tiers (PAP-211), `adr new` (PAP-130), `lib add|registry check` (PAP-216), `lib notes scaffold`, `lib guardrails build`, trailers and PR template (PAP-46, PAP-49), skill lint (PAP-105). Consumed by: Scout sessions, PAP-218 (candidate entries), PAP-118 and PAP-105 skills when a spec needs a new library, PAP-217 (major upgrade to a new package is an adoption).

**Definition of done**

* `pnpm lib adopt @tanstack/react-virtual --status trialing --yes` on a scratch branch writes scorecard, ADR draft, registry entry, note and guardrails and passes the registry check; an SSPL fixture stops at the gate.
* Skill listed for Scout in `skills.json`; `docs/libraries/adopting.md`; CHANGELOG entry.

**Test plan**

* Unit: step ordering and idempotency with a mocked filesystem, gate stop, JSON output.
* Integration: full run in a temp workspace against recorded facts.
* E2E: none.

**Demo**

Run the adopt command on a small package, watch the six steps, open the ADR draft with the pre-filled table, run `pnpm lib registry check`. Under two minutes.

**Edge cases**

* Package already in the registry: offers `update` (refresh facts and note) instead of duplicating.
* ADR numbering collision on a parallel branch: PAP-130's lint handles it at merge.
* Non-npm candidate: skips packaging checks, asks for the image or crate source.

**Dependencies**

Hard: PAP-209, PAP-216, PAP-130, PAP-757. Soft: PAP-211, PAP-755, PAP-758, PAP-46, PAP-49, PAP-105, PAP-218.

**Agent**

Builder: Scout (Library Evaluator). Reviewer: Sentinel (Code Reviewer) with Atlas on the process.

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/libraries/facts-security-quality` = PAP-755, `r4/libraries/library-guardrails-lint` = PAP-758, `r4/libraries/library-usage-notes` = PAP-757.
