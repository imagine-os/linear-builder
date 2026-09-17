# Blueprint page builder

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
