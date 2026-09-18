---
identifier: "PAP-755"
title: "Extend `lib-facts` with OpenSSF Scorecard, deps.dev advisories, `publint` and `arethetypeswrong` checks feeding a `security` and a `packaging` rubric extra"
project: "libraries"
projectName: "Library Discovery & Integration"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Developer"]
milestone: "Core adoptions decided"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-209"]
blocks: []
key: "r4/libraries/facts-security-quality"
url: "https://linear.app/paperos/issue/PAP-755/extend-lib-facts-with-openssf-scorecard-depsdev-advisories-publint-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:38.844Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-755: Extend `lib-facts` with OpenSSF Scorecard, deps.dev advisories, `publint` and `arethetypeswrong` checks feeding a `security` and a `packaging` rubric extra

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-209's facts collector reads downloads, stars, license, types and size. It does not read what the OpenSSF Scorecard, [deps.dev](<http://deps.dev>) and the packaging linters already know: dangerous workflows, unpinned dependencies, known advisories, broken `exports` maps and wrong type resolution. Add those facts and two optional rubric extras so Scout rejects fragile packages before a spike is written.

**Scope**

In: `scripts/lib-facts.ts` collectors `scorecard` ([api.securityscorecards.dev](<http://api.securityscorecards.dev>)), `depsdev` (advisories, dependents, OpenSSF score mirror), `publint` and `attw` (run against the fetched tarball in a temp dir); `facts.json` gains `security { scorecard, checks{}, advisories[] }` and `packaging { publint[], attw: { node16, bundler, esm } }`; rubric extras `security` and `packaging` in `rubric.yaml` (weight 0 by default, enabled per scorecard with `extras`); hard gate `openAdvisory: critical` added to PAP-209's gates; `docs/libraries/rubric.md` section. Out: our own SBOM and audit (PAP-80), supply-chain policy (PAP-358).

**Spec**

* Scorecard facts: overall score and the checks `Dangerous-Workflow`, `Pinned-Dependencies`, `Maintained`, `Vulnerabilities`, `Code-Review`, `Signed-Releases`; anchors: 4 at or above 7.0, 0 below 3.0 or `Dangerous-Workflow` failing.
* Packaging anchors: 4 when `publint` has no errors and `attw` resolves in all three modes; 2 with warnings; 0 when types fail in `bundler` mode (the mode Vite uses).
* Cache per package version for 7 days in `.cache/lib-facts/`; rate limits respected with backoff; unavailable APIs mark facts `stale` and never fail the CLI (matches PAP-209's rule).
* `pnpm lib score` prints the two extras only when present; the ADR Alternatives table gains optional columns.
* Non-npm candidates (crates, images): `security` from [deps.dev](<http://deps.dev>) where indexed, `packaging` `n/a`.

**Interface contract**

Provides: extended `facts.json` shape (Zod bump, additive), extras `security` and `packaging`, gate `openAdvisory`, collectors. Consumes: `lib-facts` and `RubricSchema` (PAP-209), `GITHUB_TOKEN` handling from PAP-209, license tiers for advisories context (PAP-211). Consumed by: PAP-212 to PAP-215 scorecards (re-run `--facts-only` is enough), PAP-216 `lib add` (facts filled), PAP-218 pre-scores, PAP-760.

**Definition of done**

* Facts for the worked example (TanStack Table vs AG Grid) regenerated with the new fields; a fixture package with a critical advisory fails the gate; `publint` warnings appear in the rendered table.
* `docs/libraries/rubric.md` updated; comment on PAP-209; CHANGELOG entry.

**Test plan**

* Unit: collectors against recorded HTTP fixtures, anchor mapping, cache expiry, stale handling.
* Integration: `pnpm lib score docs/libraries/examples/*.yaml` in Gate 1 still exits 0.
* E2E: none.

**Demo**

Run `pnpm lib facts @tanstack/react-table` and read the Scorecard score, then run it on a package with a known advisory and see the `openAdvisory` gate fail. Under one minute.

**Edge cases**

* Package not on GitHub: Scorecard `n/a`, extra drops and rescales per PAP-209.
* Monorepo package: Scorecard of the repo, packaging of the package.
* Advisory withdrawn: cache invalidated on the next run; scorecard re-rendered.

**Dependencies**

Hard: PAP-209. Soft: PAP-211, PAP-80.

**Agent**

Builder: Scout (Library Evaluator). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/libraries/dependency-health-page` = PAP-760.
