# Blueprint page builder

`build_blueprint.js` renders `site/index.html` from `plan.json`, `linear-ids.json` and `round2/blueprint-r2-numbers.json`. It reads them from `PAPEROS_PLAN_DIR` (default `.`), laid out as the original planning directory (`plan.json` at the root, `round2/` beside it). Run with Node 20+: `PAPEROS_PLAN_DIR=/path/to/plan node build_blueprint.js`.
