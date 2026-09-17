# Blueprint site

`index.html` is a copy of the PaperOS Core Platform blueprint page published as a Claude artifact at https://claude.ai/artifact/M8PdehTznioG49QJUnkWTU (architecture diagram, org chart, timeline, budget chart, full project and issue index, round-2 numbers). It mirrors the artifact; the artifact is where edits are made, this copy is refreshed from it.

The workflow in `.github/workflows/pages.yml` publishes this folder to the `gh-pages` branch on every push to `main`, so GitHub Pages (source: `gh-pages` branch, root) serves it at `https://imagine-os.github.io/linear-builder/`. `.nojekyll` keeps Pages from running Jekyll over the file.

`tools/blueprint/build_blueprint.js` is the script that generated the page from `plan/plan.json` and the round-2 numbers.
