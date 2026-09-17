---
identifier: "PAP-247"
title: "Page capture with authenticated audiences and baseline update workflow"
project: "quality"
projectName: "Quality Pipeline"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Gates 1 and 2 on every PR"
state: "Backlog"
parent: "PAP-82"
children: []
blockedBy: ["PAP-240", "PAP-246"]
blocks: ["PAP-248"]
key: "quality/playwright-matrix/pages-auth-baselines"
url: "https://linear.app/paperos/issue/PAP-247/page-capture-with-authenticated-audiences-and-baseline-update-workflow"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:04:42.069Z"
---

# PAP-247: Page capture with authenticated audiences and baseline update workflow

**Goal**

Extend the suite from stories to real pages: derive the page list from route files and specs, log in per audience through test mode, seed deterministic data, and give agents a one-label baseline update workflow with bot commits.

**Scope**

* In: `apps/web/e2e/visual/pages.ts` (routes with `staticData.spec` plus specs with `screenshot: true`), per-audience storage state via `loginAs` and `seed('portal' | 'console')`, full-page capture rules, `update-baselines` label workflow committing with the bot account, guard flagging baseline pushes without the label, `screenshot: false` opt-out with reason.
* Out: matrix and fixtures (sibling), reporter (sibling).

**Spec**

* Page IDs `page:<routeId>`; `fullPage: true` capped at 4 000 px; `screenshot: fullScroll` for scrolling capture; `data-ready` attribute awaited.
* Audience per page from the spec `access.view` (first audience) unless `screenshot.as` overrides; anonymous pages skip login.
* Workflow `.github/workflows/update-baselines.yml`: on label, run the suite with `--update-snapshots`, commit via PAP-48 bot with message `test(visual): update baselines for #<pr>`, remove the label, comment the diff count; a Gate 1 check fails when `__screenshots__` changes without that commit signature.
* Test-mode dependence stated: without the seed issue the suite runs stories only and posts "pages skipped: test mode unavailable".

**Interface contract**

* Provides: page list module used by PAP-83 flows and PAP-87 URLs, `screenshot` spec keys (`true | false | fullScroll`, `as`), `update-baselines` label contract for agents (PAP-92 playbook).
* Requires: sibling matrix child, test-mode seed and `loginAs`, PAP-48 bot, PAP-16 routes, PAP-115 spec keys (soft).

**Definition of done**

* All example routes and portal/console pages captured for their audiences at 21 combinations; baselines committed.
* Label workflow turns a red gate green in one run (links to both).
* Direct baseline push without the signature fails Gate 1 (seeded).
* Docs sections "Pages", "Audiences", "Updating baselines".

**Test plan**

* Unit: page list derivation and opt-out handling.
* Integration: login state caching per shard; anonymous versus customer captures differ on `/portal`.
* Workflow: rehearsal on the sandbox repo.

**Demo**

Change a portal heading colour, push, watch `gate/3-visual` fail with a contact sheet; add the `update-baselines` label and watch the bot commit land and the gate pass. Under two minutes of watching after CI runs.

**Edge cases**

* Two baseline PRs conflict in LFS: rerun the label workflow after rebase (documented).
* Renamed route: old baseline `missing` requires explicit deletion.
* Page needs data the fixture lacks: `screenshot.fixture` key selects another fixture.

**Dependencies**

Sibling matrix child, test-mode seed issue (hard). Soft: PAP-48, PAP-115.

**Agent**

Built by Sentinel (Visual Inspector). Reviewed by Forge (workflow) and Quill (spec keys).

**Size**

M.
