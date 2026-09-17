---
identifier: "PAP-378"
title: "Spec editor: live preview at selectable widths, flow-graph tab, keyboard shortcuts and accessibility polish"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Developer", "Staff"]
milestone: "Spec editor UI"
state: "Backlog"
parent: "PAP-124"
children: []
blockedBy: ["PAP-376"]
blocks: []
key: "spec-builder/spec-editor-ui/preview"
url: "https://linear.app/paperos/issue/PAP-378/spec-editor-live-preview-at-selectable-widths-flow-graph-tab-keyboard"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:43.282Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-378: Spec editor: live preview at selectable widths, flow-graph tab, keyboard shortcuts and accessibility polish

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Complete the editor: a live preview that compiles the PAP-120 view template in-memory with `esbuild-wasm` inside an iframe at a selectable width and theme, a Graph tab showing the page's neighbourhood from the PAP-123 flow graph, command-registry shortcuts, and the accessibility pass with a recorded keyboard-only flow.

**Scope**

* In: Preview tab (width presets 320 to 1920, theme toggle, state selector), Graph tab (React Flow mini view via `subgraph()`), shortcuts through PAP-151, focus order and axe fixes, PAP-83 flow file and video, `docs/spec/editor.md`.
* Out: YAML and form editing (sibling children), canvas interactions beyond viewing (PAP-132).

**Spec**

* Preview: on valid spec, run `generatePage()` templates in a worker, bundle with `esbuild-wasm` against the design-system package externals resolved from a prebuilt vendor bundle, render in a sandboxed iframe with `postMessage` for width and theme; compile capped at 5 s with an outline fallback (component tree with slots); state selector forces `dataStates` via mocked hooks.
* Graph: `subgraph(graph, 'page:<id>', depth 1)` rendered with React Flow, nodes clickable to open their editor; regenerates on save.
* Shortcuts: `Cmd/Ctrl+S` save, `Cmd/Ctrl+Shift+V` toggle Form and YAML, `Cmd/Ctrl+P` toggle preview, registered with PAP-151 when present, local fallback otherwise.
* Accessibility: tabs are proper `role="tablist"`, iframe has a title, width presets are radio buttons, diagnostics announced via a live region; PAP-152 focus management on tab switch.
* Telemetry: `spec_editor.preview_compile` duration event.

**Interface contract**

* Provides: `SpecPreview` component (`{ spec, width, theme, state }`), `useSubgraph(pageId)`, shortcut ids `specs.save`, `specs.toggleView`, `specs.togglePreview`, the PAP-83 flow file `flows/spec-editor.yaml`.
* Consumers: PAP-125 docs (preview screenshots), PAP-131 comments in preview later, PAP-113 reuses the subgraph viewer pattern.
* Requires: yaml child, PAP-120 templates, PAP-123 graph, PAP-151, PAP-152, PAP-83 recorder, prebuilt vendor bundle from PAP-69 build.

**Definition of done**

* Preview renders the three examples at 320, 768 and 1280 px presets in both themes (screenshots); compile time under 5 s (numbers).
* Graph tab shows neighbours and navigates on click.
* Keyboard-only flow recorded (open, edit, preview, save) and attached; axe clean on all tabs.
* Docs; changelog; Linear comment with video and screenshots.

**Test plan**

* Unit: width preset state, message protocol to the iframe, subgraph selection, shortcut registration fallback.
* Integration: worker compile of the example views against the vendor bundle; timeout path.
* e2e (Playwright): preview width switch, graph click navigation, keyboard flow at 1280 px.
* Visual: preview at 320, 768 and 1280 px presets in both themes through gate 3.

**Demo**

Open the Preview tab, switch to 320 px and dark, select the `empty` state and see the empty component; open Graph, click the neighbouring `invoice-detail` node and land in its editor. One minute.

**Edge cases**

* Component not in the vendor bundle: preview shows `<MissingComponent>`; outline fallback lists it.
* Compile over 5 s: outline fallback with a retry button.
* Graph has no neighbours: single node with a hint to add `events`.
* Shortcut conflicts with browser: registry warns; alternative shown in the tooltip.
* Reduced motion: preview transitions disabled (PAP-72).

**Dependencies**

Blocked by PAP-376. Soft: PAP-120, PAP-123, PAP-151, PAP-152, PAP-83.

**Agent**

Built by Nova (Canvas Cartographer) with Iris on accessibility; reviewed by Sentinel (Visual Inspector).

**Size**

M
