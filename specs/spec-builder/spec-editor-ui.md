---
identifier: "PAP-124"
title: "Build the spec editor UI with form and YAML views and live preview"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Developer", "Staff"]
milestone: "Spec editor UI"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-114", "PAP-70"]
blocks: []
key: "spec-builder/spec-editor-ui"
url: "https://linear.app/paperos/issue/PAP-124/build-the-spec-editor-ui-with-form-and-yaml-views-and-live-preview"
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-124: Build the spec editor UI with form and YAML views and live preview

**Goal**

Let Justin and agents edit page specs inside PaperOS with a form view for people who do not want YAML, a YAML view with live validation for those who do, and a preview of the generated page and its place in the flow graph. Saving opens a PR, so the repo stays the source of truth.

**Scope**

In:
- Routes `/_app/dev/specs` (list) and `/_app/dev/specs/$id` (editor) in `apps/web`, surface `developer|staff`, access `staff.admin` and `agent.*` read, `staff.admin` write.
- List: grid from `tables/grid-view` if merged, else a simple table: id, title, route, surface, owner, status, validation status, last commit; filters by status and surface.
- Editor layout via `design-system/layout-components`: `SplitPane` with a tabbed left pane (Form, YAML) and right pane (Preview, Graph, Issues).
- Form view: section forms built with `react-hook-form` 7 and `@hookform/resolvers` zod adapter over the `PageSpec` Zod 4 schema; component tree editor as a nested list with add-from-registry (searchable list from `registry.json` with prop forms generated from each component's JSON Schema, enums as selects, defaults shown); access editor with audience multiselect and condition builder reusing the filter builder from `tables/filter-sort-group-ui` when available.
- YAML view: CodeMirror 6 with `@codemirror/lang-yaml`, JSON Schema completion via `codemirror-json-schema` (YAML mode), diagnostics from `validateSpecs()` running in a Web Worker (`spec-builder/validator` library API), two-way sync with the form on debounce with a conflict banner if YAML is invalid.
- Preview: renders `spec-builder/layout-codegen` output in-memory using the same templates compiled with `esbuild-wasm` inside an iframe at a selectable width (320 to 1920) and theme; falls back to a static component-tree outline when compile fails.
- Graph tab: this page's neighbourhood from `spec-builder/spec-to-canvas` in a small React Flow.
- Save: oRPC `specs.save({ id, yaml, message })` writes the file on branch `spec/<id>` via the Forgejo API (`forge/in-app-git` client), commits with trailers and opens or updates a PR; the UI shows the PR link and validation state. Drafts autosave to `localStorage` per user.

Out: multiplayer editing of one spec, a visual drag-and-drop page builder, editing `app.spec.yaml` (read-only viewer only).

**Spec**

- Optimistic locking: save sends the base commit SHA; server returns `CONFLICT` if the file changed; UI offers a three-way diff (`diff` 7) and rebase.
- Validation issues render in the Issues tab and as gutter markers in YAML and inline messages in Form, keyed by `path`.
- Keyboard: `Cmd/Ctrl+S` save, `Cmd/Ctrl+Shift+V` toggle view, registered with `input/command-registry` when present.
- Unsaved changes guard on navigation.
- Telemetry: `spec_editor.save` audit event with spec id and PR URL (`data-layer/audit-log`).

**Definition of done**

- Playwright: open example spec, edit title in Form, see YAML update, introduce an error in YAML, see diagnostic, fix, save, PR link appears (mocked Forgejo in CI); screenshots at 768, 1024, 1280, 1536 and 1920 in light and dark; 320 and 375 show a read-only YAML view with a "desktop recommended" notice.
- Vitest: form to YAML round trip preserves comments and `x-*` keys (uses `yaml` document API), lock conflict handling, worker validation.
- axe clean on both tabs; keyboard-only completion of the flow recorded as video (`quality/video-replays` flow file).
- `docs/spec/editor.md`; CHANGELOG entry; Linear comment with Pages preview link and video.
- Justin edits one real spec and the PR merges (comment with the PR).

**Edge cases**

- YAML with comments and anchors: Form edits patch the `yaml` Document rather than re-serialising, so comments survive.
- Registry component removed after the spec referenced it: Form shows the node with a warning and a replace action.
- Very large spec (300 components): component tree virtualised; preview compile capped at 5 s with a fallback outline.
- Offline: editing continues, save disabled with a reason, draft kept locally.
- Two people edit the same spec: second saver gets the conflict flow; presence indicator from `realtime/presence` shows who else has it open.
- Worker crash: diagnostics show "validation unavailable" and saving requires an explicit confirm.

**Dependencies**

`spec-builder/schema` (hard), `design-system/layout-components` (hard). `spec-builder/validator` library API, `spec-builder/layout-codegen` templates, `forge/in-app-git` or direct Forgejo API for save, `design-system/component-spec-mapping` registry. Soft: `tables/grid-view`, `tables/filter-sort-group-ui`, `spec-builder/spec-to-canvas`.

**Agent**

Built by Nova with Iris (Component Crafter) on forms. Reviewed by Quill (spec semantics), Sentinel (Code Reviewer, Visual Inspector).

**Size**

L: two synchronised editors, in-browser compile preview and a git-backed save flow.
