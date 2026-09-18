---
identifier: "PAP-124"
title: "Build the spec editor UI with form and YAML views and live preview"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Spec editor UI"
state: "Backlog"
parent: null
children: ["PAP-377", "PAP-376", "PAP-378"]
blockedBy: ["PAP-70", "PAP-114", "PAP-667"]
blocks: []
key: "spec-builder/spec-editor-ui"
url: "https://linear.app/paperos/issue/PAP-124/build-the-spec-editor-ui-with-form-and-yaml-views-and-live-preview"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:48:01.772Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-30"
cycle: null
---

# PAP-124: Build the spec editor UI with form and YAML views and live preview

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Let Justin and agents edit page specs inside PaperOS: a form view for people who do not want YAML, a YAML view with live validation for those who do, and a preview of the generated page and its place in the flow graph. Saving opens a PR, so the repo stays the source of truth. Umbrella for three children.

**Scope**

* Children (build in order, 2 and 3 can run in parallel after 1):
  * PAP-376: spec list, YAML editor with worker validation, and save-to-PR flow.
  * PAP-377: form view, component tree editor and two-way sync.
  * PAP-378: preview, graph tab, keyboard and accessibility polish.
* Out: multiplayer editing of one spec, a drag-and-drop page builder, editing `app.spec.yaml` (read-only viewer).

**Spec**

* Routes `/_app/dev/specs` and `/_app/dev/specs/$id`, surface `developer | staff`, access `staff.admin` write, `agent.*` read.
* Layout via PAP-70 `SplitPane`: left tabs Form and YAML, right tabs Preview, Graph, Issues.
* Save: oRPC `specs.save({ id, yaml, message, baseSha })` writes on branch `spec/<id>` through the Forgejo API, commits with trailers and opens or updates a PR; optimistic locking returns `CONFLICT` with a three-way diff; drafts autosave to `localStorage`.
* Diagnostics keyed by `path` render in Issues, as YAML gutter markers and as inline form messages.
* Keyboard `Cmd/Ctrl+S` save, `Cmd/Ctrl+Shift+V` toggle view via PAP-151; unsaved-changes guard; `spec_editor.save` audit event (PAP-38).

**Interface contract**

* Provides: page specs `specs/dev/spec-list.spec.yaml`, `spec-editor.spec.yaml`; procedures `specs.list()`, `specs.get(id)`, `specs.save(...)`, `specs.validate(yaml)` (server fallback for the worker); component `SpecForm` in `apps/web/src/features/specs/`; event `spec.saved { id, prUrl }`.
* Consumers: Justin; Quill sessions for spec edits; PAP-126 business profile editing later; PAP-131 comments anchor on `data-spec-key` in the preview.
* Requires: PAP-114 schema, PAP-70 layout (hard), PAP-115 `validateSpecs` library API, PAP-120 templates for preview, PAP-74 registry, Forgejo API client (PAP-276 or direct), PAP-123 subgraph, PAP-151, PAP-165 grid (soft).

**Definition of done**

* All three children Done.
* Umbrella e2e: open example spec, edit title in Form, YAML updates, break YAML, see diagnostic, fix, save, PR link appears (mocked Forgejo in CI); screenshots at 768, 1024, 1280, 1536 and 1920 px in light and dark; 320 and 375 px show read-only YAML with a "desktop recommended" notice.
* axe clean on both tabs; keyboard-only flow recorded (PAP-83 flow file).
* Justin edits one real spec and the PR merges; docs; changelog; Linear comment with preview link and video.

**Test plan**

* Umbrella e2e (Playwright) as above at 375, 768 and 1280 px.
* Round-trip test: Form edits patch the `yaml` Document so comments and `x-*` keys survive (child 2).
* Visual: five desktop widths plus two phone widths through gate 3.

**Demo**

Open `/_app/dev/specs/customer-invoices`, change the title in the form and watch the YAML tab update, type an invalid `surface` in YAML and see the gutter error, fix it, press `Cmd+S` and click the PR link. Two minutes.

**Edge cases**

* YAML with comments and anchors: Document patching preserves them.
* Registry component removed: node shows a warning with a replace action.
* 300-component spec: virtualised tree; preview compile capped at 5 s with an outline fallback.
* Offline: editing continues, save disabled with reason, draft kept.
* Worker crash: "validation unavailable", saving requires explicit confirm.

**Dependencies**

Blocked by PAP-114, PAP-70. Soft: PAP-115, PAP-120, PAP-123, PAP-74, PAP-151, PAP-165, PAP-276.

**Agent**

Built by Nova with Iris (Component Crafter) on forms; reviewed by Sentinel (Visual Inspector) and Quill.

**Size**

L (umbrella; children M, M, M)
