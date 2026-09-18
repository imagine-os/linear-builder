---
identifier: "PAP-660"
title: "Form-state adapters: useAppForm over react-hook-form with Zod, Form and FormField bindings, FieldArray with keyboard reorder, async validation and server error mapping"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: "PAP-233"
children: []
blockedBy: ["PAP-236", "PAP-659"]
blocks: ["PAP-120", "PAP-164", "PAP-166", "PAP-338", "PAP-617", "PAP-620", "PAP-627", "PAP-667", "PAP-854"]
key: "r4/design-system/form-state-adapters"
url: "https://linear.app/paperos/issue/PAP-660/form-state-adapters-useappform-over-react-hook-form-with-zod-form-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:23.992Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-660: Form-state adapters: useAppForm over react-hook-form with Zod, Form and FormField bindings, FieldArray with keyboard reorder, async validation and server error mapping

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Second half of PAP-233: the thin layer that connects `Field` and every control to `react-hook-form` with Zod so codegen (PAP-120), the form view and settings pages write forms the same way, with arrays, async rules and server errors mapped by path.

**Scope**

In: `packages/ui/src/forms/{useAppForm,Form,FormField,FieldArray,asyncRule,serverErrors}.tsx`; `meta.ts` spec ids `ui.form`, `ui.fieldArray`; stories `Forms/Invoice example`.

Out: pickers (sibling), form layout components and unsaved-changes guard (PAP-667), validation copy guidelines (PAP-76 `DS-FORM-*`).

**Spec**

* `useAppForm(schema, { defaultValues, mode: 'onBlur' })` wraps `react-hook-form` 7.x with `@hookform/resolvers/zod` and returns typed `register`, `control`, `handleSubmit`, `errors` mapped to `Field.error`, `formState`, plus `setServerErrors(errorMap)` mapping `{ path, issue }[]` (PAP-267 `details` shape) onto fields and a form-level alert.
* `Form` renders `<form noValidate>` with `aria-describedby` to the form-level alert; `FormField name render` binds any control (`Input`, `Select`, `Combobox`, `DatePicker`, `Switch`) through `Controller` with `Field` label, description and error wiring; `disabled` while submitting.
* `FieldArray name` renders rows with add, remove and keyboard reorder (`Alt+Up|Down`, announced via PAP-152 when present), virtualised beyond 200 rows, per-row errors.
* `asyncRule(fn, { debounceMs: 400 })` sets `validating` on the Field, cancels stale calls, surfaces the result as an error or clears it; validation timing on blur then on submit per `DS-FORM-03`.
* Values for dates are the sibling's `DateValue` types; `Money` fields use minor-unit strings; the resolver never sees JS `Date`.

**Interface contract**

Provides: `useAppForm`, `Form`, `FormField`, `FieldArray`, `asyncRule`, `setServerErrors`, spec ids `ui.form`, `ui.fieldArray`, types `AppForm<T>`. Consumes: controls and `Field` (PAP-236, PAP-238), pickers (sibling), error body shape (PAP-267), announcer (PAP-152, soft). Consumed by PAP-120 codegen forms, PAP-620, PAP-667, PAP-75 settings page, PAP-224 auth pages.

**Definition of done**

* Adapters merged with the invoice example story (line items `FieldArray`, async email check, server error mapping); `vitest-axe` clean; screenshots at 375 and 1280 light and dark.
* `docs/design/forms-and-dates.md` forms section; changelog; Linear comment on PAP-120 naming the import path.

**Test plan**

* Unit: resolver mapping of nested paths; `setServerErrors` path matching including array indices; async rule debounce and cancellation with fake timers; `FieldArray` reorder maths.
* Interaction (`play`): submit with an invalid email shows the on-blur error; add two rows and reorder by keyboard; async validator shows `validating` then error.
* E2E: none (Storybook).

**Demo**

Reviewer opens Storybook `Forms/Invoice example`, adds two line items, reorders one by keyboard, submits with an invalid email and watches the on-blur error, then triggers a mocked server error mapped to the customer field. Under one minute.

**Edge cases**

* Server error path not in the form: shown in the form-level alert.
* 10,000-row `FieldArray`: virtualised rows over 200, reorder still announced.
* Schema with transforms: values passed to `onSubmit` are the transformed output.
* Submitting while an async rule is pending: waits, then proceeds or shows the error.

**Dependencies**

Sibling pickers (hard, date values), PAP-236 (hard). Soft: PAP-267, PAP-152. Blocks the form layout issue, the form view and PAP-120 forms.

**Agent**

Builder: Iris (Component Crafter). Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/design-system/form-layout-and-unsaved-changes` = PAP-667, `r4/tables/form-view-runtime-and-public-submit` = PAP-620.
