---
identifier: "PAP-233"
title: "Build date, time, date-range and calendar pickers plus form-state adapters (react-hook-form Field, arrays, async validation)"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: null
children: ["PAP-659", "PAP-660"]
blockedBy: ["PAP-67", "PAP-238"]
blocks: ["PAP-164", "PAP-166", "PAP-338", "PAP-617", "PAP-627", "PAP-854"]
key: "design-system/date-pickers-forms"
url: "https://linear.app/paperos/issue/PAP-233/build-date-time-date-range-and-calendar-pickers-plus-form-state"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:32.608Z"
model: null
effort: null
estimate: null
dueDate: "2026-09-25"
cycle: null
---

# PAP-233: Build date, time, date-range and calendar pickers plus form-state adapters (react-hook-form Field, arrays, async validation)

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Fill the two holes every data-entry page hits first: date and time pickers (single, range, time, relative presets) that the field types, filter builder and finance pages need, and the form-state adapters that connect `Field` to `react-hook-form` with Zod, arrays and async validation. PAP-67 excluded both deliberately; PAP-164 and PAP-166 require them.

**Scope**

* In: `Calendar`, `DatePicker`, `DateRangePicker`, `TimeField`, `DateTimeField`, `RelativeDatePicker` (presets like "last 30 days", "this quarter") on the chosen primitive library's date components or React Aria (`react-aria-components` `DateField`, `Calendar`, `RangeCalendar`) as fallback; `Form`, `FormField`, `FieldArray`, `useAppForm` adapters over `react-hook-form` 7.x with `@hookform/resolvers/zod`; async validators with debounce; `meta.ts` spec IDs.
* Out: recurring-schedule editors, natural-language date parsing, form layout guidelines (PAP-76).

**Spec**

* Values are `Temporal`-like plain objects via `@internationalized/date` (`CalendarDate`, `Time`, `ZonedDateTime`); never JS `Date` at the API boundary; serialised as ISO strings; date-only fields never shift across zones.
* `DatePicker` props: `{ value, onChange, min, max, granularity: 'day' | 'minute', locale?, timeZone?, presets?, isDateUnavailable? }`; keyboard grid per ARIA APG; typed input with segment editing; `Popover` from PAP-67.
* `RelativeDatePicker` emits `{ kind: 'relative', unit, amount, anchor }` or absolute ranges, matching the shared filter grammar (data-layer spec) so PAP-166 filters and PAP-195 segments store the same shape.
* Forms: `useAppForm(schema, { defaultValues, mode: 'onBlur' })` returns typed `register`, `Field` binding, `errors` mapped to `Field.error`; `FieldArray` with add, remove, reorder (keyboard) rows; async rule helper `asyncRule(fn, { debounceMs: 400 })` sets `validating` state on the Field.
* Validation timing follows guideline `DS-FORM-03`: on blur, then on submit; server errors mapped by path via `setServerErrors(errorMap)`.

**Interface contract**

* Provides: components above with spec IDs `ui.datePicker`, `ui.dateRangePicker`, `ui.timeField`, `ui.dateTimeField`, `ui.relativeDatePicker`, `ui.form`, `ui.fieldArray`; types `DateValue`, `RelativeRange`; `useAppForm`, `setServerErrors`.
* Requires: PAP-67 Popover, Field, Input; PAP-66 tokens; PAP-27 `LocaleProvider`; shared filter grammar types (data-layer) for `RelativeRange`.
* Consumers: PAP-164 date fields, PAP-166 filter builder, PAP-168 calendar view, PAP-180 invoices, PAP-58 invitation expiry.

**Definition of done**

* Six components and the form adapters merged with stories for every state and RTL; `vitest-axe` zero violations.
* Formatting and parsing tests for en-US, en-GB, de-DE, ja-JP, ar-EG with DST boundaries and leap day.
* `RelativeRange` round-trips through the filter grammar fixture from data-layer.
* Screenshots of the "Pickers" and "Forms" stories at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark.
* Docs `docs/design/forms-and-dates.md`; changelog under "Design system".

**Test plan**

* Unit: segment editing, min/max clamping, unavailable dates, preset resolution at quarter boundaries, `FieldArray` reorder.
* Interaction (`play`): open picker, arrow to a date, Enter selects, Escape closes returning focus; range selection with keyboard; async validator shows `validating` then error.
* Visual: seven widths, mobile picker as full-screen sheet under 768.

**Demo**

Open Storybook "Forms/Invoice example": fill a due date with the keyboard only, pick "last quarter" in the range filter, add two line items with FieldArray, submit with an invalid email and watch the on-blur error. Under two minutes.

**Edge cases**

* Time zone differs between user and tenant: `DateTimeField` shows the zone badge; storage in UTC with zone recorded.
* Locale with non-Gregorian calendar (`fa-IR`): Calendar follows `Intl` calendar; documented limits.
* 10 000-row `FieldArray`: virtualised rows over 200.
* Paste of `2026-13-01`: rejected segment, field stays invalid with message.
* Reduced motion: no popover transitions.

**Dependencies**

PAP-67 (hard). Soft: PAP-27, PAP-212 (library choice), data-layer filter grammar spec.

**Agent**

Built by Iris (Component Crafter). Reviewed by Sentinel (Code Reviewer, Visual Inspector) and Nova (field-type contract).

**Size**

M: pickers are mostly library wiring; locale and zone correctness is the risk.
