---
identifier: "PAP-376"
title: "Spec editor: spec list, CodeMirror YAML editor with worker validation and save-to-PR flow"
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
blockedBy: ["PAP-70", "PAP-114"]
blocks: ["PAP-377", "PAP-378"]
key: "spec-builder/spec-editor-ui/yaml"
url: "https://linear.app/paperos/issue/PAP-376/spec-editor-spec-list-codemirror-yaml-editor-with-worker-validation"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:42.809Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-376: Spec editor: spec list, CodeMirror YAML editor with worker validation and save-to-PR flow

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Ship the first usable editor: a list of specs with validation status, a YAML editor with schema completion and live diagnostics from the validator running in a Web Worker, and a save flow that commits to a `spec/<id>` branch through the Forgejo API and opens or updates a PR with optimistic locking.

**Scope**

* In: routes `/_app/dev/specs` and `/_app/dev/specs/$id` with page specs, `specs.list | get | save | validate` procedures, CodeMirror 6 YAML editor, worker validation, Issues tab, save and conflict flow, localStorage drafts.
* Out: form view (PAP-377), preview and graph (PAP-378).

**Spec**

* List: PAP-165 grid if merged, else a simple table: id, title, route, surface, owner, status, validation, last commit; filters status and surface.
* Editor: `@codemirror/lang-yaml`, JSON Schema completion via `codemirror-json-schema` in YAML mode, diagnostics from `validateSpecs()` (PAP-115 library API) in a worker with 300 ms debounce; gutter markers keyed by `path`; Issues tab lists them with hints.
* Save: `specs.save({ id, yaml, message, baseSha })` writes the file on `spec/<id>`, commits with PAP-46 trailers, opens or updates a PR (PAP-49 template) via the Forgejo API client (PAP-276 if merged, else a thin client here); `CONFLICT` when `baseSha` moved returns the current content; UI shows a three-way diff (`diff` 7) and a rebase button.
* Drafts autosave per user and spec in `localStorage` with a restore banner; unsaved-changes guard on navigation; `spec_editor.save` audit event (PAP-38).
* Access: `staff.admin` write, `agent.*` read (PAP-116 section on the page spec).

**Interface contract**

* Provides: page specs `spec-list.spec.yaml`, `spec-editor.spec.yaml`; procedures `specs.list()`, `specs.get(id): { yaml, sha }`, `specs.save(...)`, `specs.validate(yaml)`; component `YamlEditor` with `onDiagnostics`; event `spec.saved { id, prUrl }`.
* Consumers: form child (shares the document model), preview child (reads editor state), Quill sessions, PAP-126 later.
* Requires: PAP-114, PAP-70 `SplitPane`, PAP-115 library API, Forgejo API access, PAP-46, PAP-49, PAP-38, PAP-165 (soft).

**Definition of done**

* Playwright: open example, introduce a YAML error, see gutter marker and Issues entry, fix, save, PR link appears (mocked Forgejo); conflict flow with a concurrent change.
* Worker validation under 300 ms for a 300-line spec (timing in comment).
* Screenshots at 768, 1024, 1280, 1536 and 1920 px light and dark; 320 and 375 px show read-only YAML with the notice.
* axe clean; changelog; Linear comment with screenshots.

**Test plan**

* Unit: diagnostics mapping from `SpecIssue` to CodeMirror ranges, draft restore, conflict state machine.
* Integration: `specs.save` against a mocked Forgejo API including `CONFLICT`.
* e2e (Playwright): the save and conflict flows at 375 (read-only) and 1280 px.
* Visual: seven widths through gate 3.

**Demo**

Open `/_app/dev/specs/customer-invoices`, type an invalid `surface`, watch the gutter error and Issues entry, fix it, press `Cmd+S` and click the PR link that appears. One minute.

**Edge cases**

* Worker crash: "validation unavailable", save requires confirm.
* Offline: editing continues, save disabled with reason, draft kept.
* Spec deleted upstream: save offers to recreate on the branch.
* Very large spec: editor virtualised by CodeMirror; validation still in worker.
* Agent user: read-only editor with a copy button.

**Dependencies**

Blocked by PAP-114, PAP-70 (through the parent). Soft: PAP-115, PAP-165, PAP-276.

**Agent**

Built by Nova; reviewed by Sentinel (Visual Inspector).

**Size**

M
