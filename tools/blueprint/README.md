# Blueprint page builder

## v5 (round 4)

`build_v5.js` is the current builder: `node tools/blueprint/build_v5.js` renders `site/index.html`, `site/data.json` and,
with `PAPEROS_ARTIFACT_OUT`, the self-contained artifact body. It reads the round-4 snapshot written by
`tools/linear/round4/snapshot4.py` (estimates, due dates, cycles, initiatives, templates, views, team settings), the round-4
chunk plan `plan/round4/chunks-v2.json` (default since the closing pass of round 4; `CHUNKS=` points at another file such as
the round-3 `plan/chunks.json`; `canonicalMix`, `counts`, `wallClock` and `round3` are passed through to the chunks section
and the model / effort note), plus
`plan/round4/merge-report.md`, `plan/round4/verify.md`, `plan/round4/gaps/cross-cutting.json` (keys and phases of the five
new projects) and `docs/linear-features.md` (the Linear features table). On top of every v4 view it adds, in
`template_v5.html` and `v5/round4.js` + `v5/round4.css`: an **Initiatives** section (five cards with linked projects,
issues, points, ready count, progress = points done over points planned, state bar), a **Cycles** strip (C1/C2/C3 with
dates, points assigned versus points due inside the window, the "cycles hold in-flight work; planned timing is due dates
and Chunk labels" rule and the team settings), an **Estimates** view (points per project stacked by state with a table
view, burn-up of cumulative points due by date against points done, 0 today), a **Round 4** section (before/after
numbers from the snapshot, the 23 projects with new-issue counts, twelve gaps from the digests, the Linear features
table), **Triage** and **Needs Justin** tiles on the first screen (linking to the Linear views), cycle / points /
initiative / "new in round 4" / "in Triage" filters and due-date and points sorts in the shared filter bar, and
estimate, due date and cycle in the issue index. New project hues (`NEW_PROJECT_STYLE`) were checked with the dataviz
palette validator; Triage got its own state colour (`--st-triage`). `v5/views.js`, `modules.js` and `chunks.js` are the
v4 files with the filter extensions. The previous page is kept as `site/previous/index-v4.html`.

## v4

`build_v4.js` renders `site/index.html` (GitHub Pages) and `site/data.json` from the live Linear snapshot, and the
self-contained artifact body when `PAPEROS_ARTIFACT_OUT` is set. Run with Node 20+ from anywhere:

```
node tools/blueprint/build_v4.js
PAPEROS_ARTIFACT_OUT=/tmp/blueprint-v4.html node tools/blueprint/build_v4.js
```

Inputs (relative to the repo root, override with `PAPEROS_REPO`): `plan/linear-snapshot-live.json` (issues with state,
labels, Model and Effort, size in the description, project, milestone and date, parent/children, blocks relations,
Deferred flag; projects with milestones and URLs), `plan/plan.json` (projects, phases, budget, agents, decisions),
`plan/linear-ids.json` (fallback project URLs), `plan/chunks.json` (the $2,500 chunk plan from `round3/chunks.py`,
override with `CHUNKS`) and, when present, `plan/model-effort.json` (override with `MODEL_EFFORT`). The module table
(provides, requires, swap risk, owner) is transcribed from `docs/module-system.md` table 1.1 inside `build_v4.js`; the
per-module contract / conformance / wire issues are resolved from the snapshot by title.

Files: `template_v4.html` holds the page (CSS, markup and the v3 renderers: hero, dependency map, progress, timeline,
architecture, agents, budget, documents, risks, issue index). `v4/views.css`, `v4/views.js` (shared filter and sort bar,
objects map, lanes skill tree, radial tree, images, icons, objects 3D and radial 3D with static previews), `v4/modules.js`
(modules and plug points map, kernel pieces, swap playbook) and `v4/chunks.js` (chunk timeline and cards) are inlined by
the build. `architecture.svg` is the hand-drawn system diagram the page keeps.

Two outputs from one template: the Pages build loads `3d-force-graph` 1.80.0 from jsDelivr for the two WebGL views (the
same recipe as the graph-gallery Constellation demo) and falls back to a static projection when the CDN is unreachable;
the artifact build (`__MODE__` = `artifact`) has no external scripts and always shows the static preview with a link to
the Pages copy (`#objects-3d`, `#radial-3d`). Every other view is vanilla SVG and DOM. The visual ideas follow the demos
in `imagine-os/graph-gallery` (radial-tree-d3, lanes-skilltree, three-radial-3d, force3d-bloom), re-implemented without
their libraries.

`build_v3.js` + `template.html` (round 2/3) and `build_blueprint.js` (round 2) are kept for reference; their outputs are
`site/previous/index-v3.html` and `site/previous/index-v2.html`.
