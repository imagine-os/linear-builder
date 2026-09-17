---
key: "spec-builder/spec-editor-ui/form"
title: "Spec editor: form view, component tree editor and two-way sync with YAML preserving comments"
project: "spec-builder"
parent: "PAP-124"
phase: "P2"
type: "Build"
priority: null
size: "M"
surfaces: ["Developer", "Staff"]
milestone: null
intendedState: "Backlog"
blockedBy: ["spec-builder/spec-editor-ui/yaml"]
blocks: []
source: "round2/agent2/new_spec.py"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-spec-builder-11-c314e290076b"
identifier: "PAP-377"
status: "created"
createdAt: "2026-09-17"
---

# Spec editor: form view, component tree editor and two-way sync with YAML preserving comments

**Goal**

Let people who do not want YAML edit specs: section forms generated from the `PageSpec` Zod schema, a component tree editor that adds components from the registry with prop forms from each component's JSON Schema, an access editor with audience multiselect and condition builder, and two-way sync with the YAML tab that patches the `yaml` Document so comments and `x-*` keys survive.

**Scope**

* In: `SpecForm` with `react-hook-form` 7 and the zod resolver, section panels (meta, purpose, access, data, layout, components, states, events, edge cases), component tree editor, access editor, sync engine, inline diagnostics keyed by `path`.
* Out: YAML editor and save (`spec-builder/spec-editor-ui/yaml`), preview and graph (`spec-builder/spec-editor-ui/preview`).

**Spec**

* Forms derived from `PageSpecSchema` field metadata (labels, descriptions, enums as selects, defaults shown); arrays as sortable lists (PAP-155 drag with keyboard alternative).
* Component tree: nested list with add-from-registry (searchable list from PAP-74 `registry.json`), prop form per component from its JSON Schema, `slot` picker limited to the layout template's slots, `events` picker limited to `logic.actions`.
* Access editor: audiences from the app spec (PAP-117) as multiselect; condition builder reusing PAP-166 filter UI when merged, else a minimal `all | any | not` tree editor over the PAP-279 grammar.
* Sync: form edits produce JSON patches applied to the `yaml` Document (`yaml` 2.x `Document` API) at the mapped path; YAML edits reparse into the form on debounce; invalid YAML shows a banner and freezes the form until fixed.
* Diagnostics from the yaml child's worker map to form fields by `path`.

**Interface contract**

* Provides: `SpecForm` component, `applyFormPatch(doc, path, value)`, `docToForm(doc)`, `ComponentTreeEditor`, `AccessEditor` (reusable by PAP-126 for the business profile).
* Consumers: PAP-126 (profile editing), PAP-118 skill may open a prefilled form link, PAP-131 comments anchor on `data-spec-key` in the tree editor.
* Requires: yaml child document model, PAP-74 registry, PAP-117 audiences, PAP-279 grammar, PAP-155 (soft), PAP-166 (soft), PAP-233 form adapters.

**Definition of done**

* Round-trip test: load a spec with comments and anchors, change a title and add a component in the form, serialise; comments, anchors and `x-*` keys intact; only the edited paths changed.
* Playwright: edit title in Form, see YAML update; add a component from the registry; toggle an audience; diagnostics appear inline on an invalid value.
* Screenshots at 1024, 1280 and 1920 px light and dark; axe clean.
* Changelog; Linear comment.

**Test plan**

* Unit: patch mapping for nested arrays, enum selects, prop schema rendering for three registry components, invalid-YAML freeze.
* Integration: two-way sync with a debounce clock.
* e2e (Playwright) at 1280 px; 768 px shows stacked panels.
* Visual: three widths through gate 3.

**Demo**

Open the Form tab, change the page title, switch to YAML and see it changed with the comments still there; add `ui.badge` from the registry into the `main` slot and watch the YAML gain the node. One minute.

**Edge cases**

* Registry component removed: node shows a warning with a replace action.
* 300 components: tree virtualised.
* Prop schema with `oneOf`: rendered as a variant selector.
* Form and YAML edited within the same debounce window: YAML wins, form re-derives.
* Anchored value edited in the form: alias updated at all sites, user informed.

**Dependencies**

Blocked by `spec-builder/spec-editor-ui/yaml`. Soft: PAP-166, PAP-155, PAP-233.

**Agent**

Built by Iris (Component Crafter) with Nova; reviewed by Sentinel.

**Size**

M
