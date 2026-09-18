---
identifier: "PAP-667"
title: "Form layout and unsaved-changes guard: FormLayout, FormSection, FieldGroup, FormActions sticky bar, dirty-state indicator and useUnsavedChangesGuard with router and beforeunload blocking"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-70", "PAP-660"]
blocks: ["PAP-120", "PAP-124", "PAP-333"]
key: "r4/design-system/form-layout-and-unsaved-changes"
url: "https://linear.app/paperos/issue/PAP-667/form-layout-and-unsaved-changes-guard-formlayout-formsection"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:25.936Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-667: Form layout and unsaved-changes guard: FormLayout, FormSection, FieldGroup, FormActions sticky bar, dirty-state indicator and useUnsavedChangesGuard with router and beforeunload blocking

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-333 references a `FieldGroup`, every settings page needs a sticky save bar, and nothing stops a user navigating away from a half-edited form. Ship the layout pieces and the guard once so codegen and the record page get consistent forms and never lose edits silently.

**Scope**

In: `packages/ui/src/forms/{FormLayout,FormSection,FieldGroup,FormActions,DirtyIndicator,useUnsavedChangesGuard}.tsx` with `meta.ts` spec ids; router-agnostic `blocker` adapter injected by the shell (TanStack Router `useBlocker` in `apps/web`); `beforeunload` handling; stories.

Out: form state (PAP-233 child), autosave semantics (consumers), conflict UX (PAP-144).

**Spec**

* `FormLayout { columns: 1|2, gap }` with responsive collapse to one column under the `md` container width; `FormSection { title, description, collapsible? }` with `Heading` levels from the typography issue; `FieldGroup { label, description, orientation }` groups related fields under a `fieldset`/`legend` and is the shape PAP-333 uses for record field groups and PAP-161's `FieldDef.group`.
* `FormActions { primary, secondary, tertiary?, sticky }`: sticky bottom bar inside the nearest scroll container with a top shadow when content scrolls beneath, `padding-bottom` honouring `--pos-keyboard-inset` and safe areas, `DirtyIndicator` ("Unsaved changes") when the form is dirty, primary disabled while submitting with a `Spinner`.
* `useUnsavedChangesGuard(isDirty, { message })`: blocks in-app navigation through the injected router blocker with an `AlertDialog` (Stay, Discard, Save when `onSave` given), sets `beforeunload` while dirty, disarms on submit success, integrates with `useAppForm` via `formState.isDirty`; multi-window aware (PAP-145) so closing a detached window with a dirty form prompts.
* Accessibility: the dialog is the PAP-237 `AlertDialog` with initial focus on Stay; `DirtyIndicator` uses `role="status"` announced once; sticky bar never covers the last field (scroll padding).
* Codegen contract: PAP-120 wraps generated `form` layouts in `FormLayout` and emits `FormActions` with the spec's actions; `states.dirty` from the page spec maps to the guard.

**Interface contract**

Provides: components with spec ids `ui.formLayout`, `ui.formSection`, `ui.fieldGroup`, `ui.formActions`, `ui.dirtyIndicator`; `useUnsavedChangesGuard`; `NavigationBlockerProvider` adapter contract. Consumes: `useAppForm` (form adapters), `AlertDialog` (PAP-237), `Heading` (typography issue, soft), scroll containers and safe areas (PAP-70), keyboard inset (PAP-645, soft), window bus (PAP-145, soft). Consumed by PAP-333 record fields, PAP-120 codegen, PAP-124 spec editor save flow, the branding settings page.

**Definition of done**

* Components and guard merged with stories (two-column, collapsible sections, sticky actions with dirty state, guard dialog); `play` test for the guard dialog; `vitest-axe` clean.
* Screenshots at 375, 768, 1280 light and dark; `docs/design/forms-and-dates.md` layout and guard section; changelog; Linear comment on PAP-333 and PAP-120.

**Test plan**

* Unit: dirty detection wiring; guard arm and disarm sequence; `beforeunload` registration only while dirty; sticky shadow state from scroll position.
* Integration (apps/web): navigate away from a dirty form shows the dialog; Discard proceeds; Save calls `onSave` then proceeds; submit success disarms.
* E2E: edit the demo settings form, press the browser back button, choose Stay, save, then navigate freely.

**Demo**

Reviewer edits a field in the branding settings page, clicks a sidebar link, gets the Stay, Discard or Save dialog, saves and leaves. Under one minute.

**Edge cases**

* Form unmounts while dirty due to a route redirect from the server: guard disarms, no orphan dialog.
* Two dirty forms on one page: one combined prompt.
* Keyboard open on mobile: sticky bar rides above the inset.
* Print: sticky bar hidden.

**Dependencies**

PAP-660 (hard), PAP-70 (hard, scroll containers). Soft: typography issue, virtual keyboard issue, PAP-145. Blocks PAP-333, PAP-120 form layouts, PAP-124.

**Agent**

Builder: Iris (Component Crafter). Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/design-system/form-state-adapters` = PAP-660, `r4/input/virtual-keyboard-viewport` = PAP-645.
