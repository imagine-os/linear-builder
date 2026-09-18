---
identifier: "PAP-760"
title: "Dependency health page: outdated versions, pending majors, advisories, license mix, bundle share and review-due entries rendered from the registry and CI reports"
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
blockedBy: ["PAP-216"]
blocks: []
key: "r4/libraries/dependency-health-page"
url: "https://linear.app/paperos/issue/PAP-760/dependency-health-page-outdated-versions-pending-majors-advisories"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:39.299Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-760: Dependency health page: outdated versions, pending majors, advisories, license mix, bundle share and review-due entries rendered from the registry and CI reports

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-216 lists what we use, PAP-217 mirrors Renovate's dashboard into a Linear issue, PAP-80 writes `security.json`, PAP-211 writes `licenses.json` and PAP-87 measures bundle weight. Justin and Scout have to read five artefacts to answer 'how healthy are our dependencies'. Render one page from those files.

**Scope**

In: `/_app/docs/registry/health` (MDX plus a small React table via PAP-128, like PAP-216's page) built from `registry.json`, `reports/licenses.json` (PAP-211), `reports/security.json` (PAP-80, soft), PAP-87's `size-limit` output and the `outdated` snapshot written by a nightly `pnpm outdated --json` job; sections: outdated (minor, major), advisories by severity, license mix pie (dataviz palette), top-20 bundle contributors, review-due and stale-facts entries, patches expiring (PAP-759); `pnpm lib health` CLI printing the same as a table; `health.json` artefact for PAP-89's digest. Out: fixing anything, Renovate configuration (PAP-217), the registry page itself.

**Spec**

* Data freshness stamped per source; a missing source renders a placeholder naming the owning issue (same pattern as PAP-732).
* Outdated job (PAP-43 cron nightly) writes `docs/.generated/outdated.json` from `pnpm outdated --json` and `cargo outdated` when `Cargo.lock` exists; diff against yesterday produces the 'new majors' list.
* Bundle share: per-dependency gzip attribution from the analyzer JSON PAP-87 already produces for key routes, top 20 with the route they weigh on.
* Thresholds: red when any critical advisory is open or more than five majors pending for over 30 days; amber for review-due; the summary line feeds PAP-89's release digest as one row.
* Page is `audience: [developer, staff]`; `pnpm lib health --json` is what PAP-306's weekly re-audit reads.

**Interface contract**

Provides: health page, `pnpm lib health`, `health.json`, nightly outdated job. Consumes: `registry.json` (PAP-216), `licenses.json` (PAP-211), `security.json` (PAP-80, soft), size-limit output (PAP-87, soft), facts (PAP-209), jobs (PAP-43), docs rendering (PAP-128), dataviz palette (PAP-170 guidance). Consumed by: PAP-89 digest, PAP-306 re-audit, PAP-217 (links from the dashboard issue), Justin.

**Definition of done**

* Page renders from real artefacts on `main` with placeholders for missing ones; thresholds proven with a seeded critical advisory; screenshots at 375, 1024 and 1920 in light and dark; axe clean.
* `health.json` consumed by a PAP-89 fixture; `docs/libraries/health.md`; CHANGELOG entry.

**Test plan**

* Unit: source merging, threshold logic, bundle attribution parsing, diff of outdated snapshots.
* Integration: nightly job writes the snapshot on the compose stack.
* E2E (Playwright): open the page, filter outdated to majors, click through to a registry entry.

**Demo**

Open `/_app/docs/registry/health`, read the summary line, expand pending majors, click `@tanstack/react-query` and land on its registry entry and note. Under one minute.

**Edge cases**

* No `Cargo.lock` yet: Rust section hidden with a notice.
* Analyzer JSON absent on a PR build: bundle section reads the last `main` artefact.
* Thousands of transitive advisories: grouped by direct dependency.

**Dependencies**

Hard: PAP-216. Soft: PAP-211, PAP-80, PAP-87, PAP-43, PAP-128, PAP-89, PAP-306, PAP-759.

**Agent**

Builder: Scout (Library Evaluator) with Nova on the table. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/collab/docs-reference-hub` = PAP-732, `r4/libraries/patch-fork-policy` = PAP-759.
