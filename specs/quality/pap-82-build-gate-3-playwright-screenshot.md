---
identifier: "PAP-82"
title: "Build gate 3: Playwright screenshot suite across the 7-width breakpoint matrix, all themes and key pages with baseline diffs"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: null
children: ["PAP-246", "PAP-248", "PAP-247"]
blockedBy: ["PAP-14", "PAP-78", "PAP-239", "PAP-240"]
blocks: ["PAP-83", "PAP-84", "PAP-88", "PAP-253", "PAP-446", "PAP-532"]
key: "quality/playwright-matrix"
url: "https://linear.app/paperos/issue/PAP-82/build-gate-3-playwright-screenshot-suite-across-the-7-width-breakpoint"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T12:56:54.862Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-25"
cycle: null
---

# PAP-82: Build gate 3: Playwright screenshot suite across the 7-width breakpoint matrix, all themes and key pages with baseline diffs

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Build Gate 3's screenshot suite: Playwright renders every `visual`-tagged story and every key page across seven widths and three themes, compares against LFS baselines, fails the PR on unexpected change and makes intended change a one-label update. The images feed PAP-83 and PAP-84. Umbrella for three children; stories ship in P0 without authentication, pages follow once PAP-240 provides seeding and login.

**Children**

1. PAP-246 Playwright project matrix, deterministic fixtures and Storybook story capture (M) - blocks the other two.
2. PAP-247 Page capture with authenticated audiences and baseline update workflow (M) - also blocked by PAP-240.
3. PAP-248 Contact-sheet reporter, 4-way sharding and the `visual.json` artifact (S).

**Scope**

* In (across children): `apps/web/playwright.visual.config.ts` and projects, determinism fixtures, story and page capture, LFS baselines, `update-baselines` workflow, reporter, sharding, `visual.json`, Pages report upload, sticky comment, status.
* Out: video (PAP-83), vision inspection (PAP-84), functional e2e (PAP-86), seeding and login (PAP-240).

**Spec**

Details live in the children. Cross-child rules:

* Project names `xs-320, sm-375, md-768, lg-1024, xl-1280, 2xl-1536, 3xl-1920` are the canonical width keys used by PAP-83, PAP-84, PAP-87 and PAP-89.
* Screenshot IDs `story:<storyId>` and `page:<routeId>`; baselines under `__screenshots__/<project>/<theme>/<id>.png` in LFS; thresholds `maxDiffPixelRatio: 0.002`, `threshold: 0.2`.
* Runs only inside the pinned Playwright Docker image against `web-dist` from Gate 1 and `storybook-static`; never rebuilds.
* Baseline changes land only through the `update-baselines` label workflow with the bot signature.

**Interface contract**

* Provides: `visualTest` fixture, project names, ID grammar, `reports/visual.json` (`GateReport<'visual'>` with `data.images`), contact sheets, Pages URLs `/pr/<n>/visual/`, status `gate/3-visual`, scripts `pnpm shots`, `shots:update`, `shots:report`, spec keys `screenshot: true | false | fullScroll` and `screenshot.as`, story tag `visual`.
* Requires: PAP-78 `web-dist` and comment action, PAP-14 `breakpoints.json`, PAP-69 `index.json`, PAP-240 seed and `loginAs`, PAP-239 schema, PAP-48 bot, PAP-45 LFS, PAP-15 hosting (soft), PAP-75 theme attribute (soft).
* Consumers: PAP-83, PAP-84, PAP-87, PAP-88, PAP-89, PAP-137, PAP-64 UI suite, PAP-62 and PAP-63 DoDs.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §5 (`packages/contracts` is owned by quality through PAP-239: every `reports/*.json` named above is a `GateReport<kind>` validated by `validateArtifact()`, JSON Schema generated from Zod 4 per §1); §3 (gate results reach the bus as `review.gate_failed` and `review.ready` through PAP-97; artifact `version` bumps keep a reader for 30 days); §6 row "Gate artifacts" (provider PAP-239; consumers PAP-78 to PAP-90, PAP-97, PAP-137, PAP-110). Until PAP-239 merges, write the shape exactly as its Interface contract states and import the schema when it lands. `reports/visual.json` is `GateReport<'visual'>` with `data.images`; screenshot naming `screenshots/<page>/<width>.png` is consumed by PAP-97 status comments.

**Definition of done**

* All three children Done.
* Integration run below green; links to the red run, the label-update run and the green run in the Linear comment.
* `docs/quality/visual-testing.md` complete; changelog entry.

**Test plan**

Umbrella run on a PR:

* Suite covers all `visual` stories and all example, portal and console pages at 21 combinations across 4 shards in under 8 minutes; sticky comment shows contact sheets.
* Seeded 2 px padding change on Button and a heading colour change on `/portal` fail with visible diffs; `update-baselines` label commits new baselines and the gate turns green.
* Flake check: 10 consecutive `main` runs with zero diffs.
* `visual.json` validates and a PAP-84 stub lists the diff images from it.
* Direct baseline push without the bot signature fails Gate 1.

**Demo**

Open the PR "Visual" comment, click the `/portal` contact sheet (7 widths × 3 themes, one red badge), then the Pages report; add the `update-baselines` label and watch the bot commit land. Under two minutes of watching.

**Edge cases**

Cross-child: fonts differ outside Docker (warning, informational); renamed story or route leaves a `missing` baseline that must be deleted explicitly; LFS conflicts between two baseline PRs are resolved by rerunning the label workflow after rebase; count cap 600 images.

**Dependencies**

PAP-78, PAP-14, PAP-239 (hard); PAP-240 (hard for PAP-247 only). Soft: PAP-69, PAP-15, PAP-48, PAP-45, PAP-75.

**Agent**

Sentinel (Visual Inspector) builds all children; Iris consults on story tagging. Reviewed by Forge (CI, LFS, image) and Iris.

**Size**

L, split into 3 children (M, M, S).
