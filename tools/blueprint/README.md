# Blueprint page builder

`build_v3.js` renders `site/index.html` and `site/data.json` from the live Linear snapshot. Run with Node 20+ from anywhere:

```
node tools/blueprint/build_v3.js
```

Inputs (relative to the repo root, override with `PAPEROS_REPO`): `plan/linear-snapshot-live.json` (issues with state, phase, type, size in the description, project, milestone and date, parent/children, blocks relations, Deferred flag), `plan/plan.json` (projects, phases, budget, agents, decisions), `plan/linear-ids.json` (project URLs) and, when present, `plan/model-effort.json` from the cost estimate (override the path with `MODEL_EFFORT`). `template.html` holds the page (CSS, markup and the client-side renderers); `architecture.svg` is the hand-drawn system diagram the page keeps. Set `PAPEROS_ARTIFACT_OUT` to also write the page body without the `<html>` wrapper, which is what the Claude Artifact tool publishes.

The page is one self-contained HTML file: no external scripts, fonts or images. The dependency map, progress bars, timeline and issue index are drawn in the browser from the embedded JSON with vanilla SVG and DOM code; the visual ideas (phase-column dependency graph with click-to-highlight, swimlane timeline, collapsible tree) follow the demos in `imagine-os/graph-gallery`, re-implemented without their libraries.

`build_blueprint.js` is the previous (round-2) generator, kept for reference; its output is `site/previous/index-v2.html`.
