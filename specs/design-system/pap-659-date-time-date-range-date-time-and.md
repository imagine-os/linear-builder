---
identifier: "PAP-659"
title: "Date, time, date-range, date-time and relative-date pickers on @internationalized/date with locale, zone and DST correctness"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: "PAP-233"
children: []
blockedBy: ["PAP-67", "PAP-212", "PAP-236", "PAP-237", "PAP-238"]
blocks: ["PAP-338", "PAP-344", "PAP-617", "PAP-660"]
key: "r4/design-system/date-time-pickers"
url: "https://linear.app/paperos/issue/PAP-659/date-time-date-range-date-time-and-relative-date-pickers-on"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:30.611Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-659: Date, time, date-range, date-time and relative-date pickers on @internationalized/date with locale, zone and DST correctness

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

First half of PAP-233 and the part the field types (PAP-338) and filter builder wait on: six date and time pickers whose values never pass through a JS `Date`, correct across locales, zones, DST and leap days, with the relative-date shape the shared filter grammar stores.

**Scope**

In: `packages/ui/src/pickers/{Calendar,DatePicker,DateRangePicker,TimeField,DateTimeField,RelativeDatePicker}.tsx` on the PAP-212 primitive's date components or `react-aria-components` (`DateField`, `Calendar`, `RangeCalendar`) as fallback; `@internationalized/date` values; `meta.ts` spec ids; stories at seven widths.

Out: form adapters (sibling), recurring-schedule editors, natural-language date parsing (`chrono-node` lives in voice), non-Gregorian beyond `Intl` support.

**Spec**

* Values are `CalendarDate`, `Time`, `CalendarDateTime` or `ZonedDateTime` from `@internationalized/date`; serialised as ISO strings at the boundary (`toISODate`, `toISOTime`, `toAbsoluteString`); date-only values never shift across zones.
* `DatePicker { value, onChange, min, max, granularity: 'day'|'minute', locale?, timeZone?, presets?, isDateUnavailable? }`: typed input with segment editing (arrow keys change segments, typing advances), `Popover` (PAP-237) calendar with ARIA APG grid keyboard model, month and year quick jump, today button; under 768 px the calendar opens in a full-screen sheet.
* `DateRangePicker`: two-month calendar on wide viewports, start and end segments, presets (today, last 7 days, this month, last quarter, custom); `TimeField`: 12 or 24 hour by locale, seconds by `granularity`; `DateTimeField`: date plus time plus a zone badge when user and tenant zones differ.
* `RelativeDatePicker` emits `{ kind: 'relative', unit, amount, anchor }` or an absolute range, matching PAP-279's relative-date shape exactly (fixture round trip) so PAP-166 filters and PAP-195 segments store one shape.
* Validation: min and max clamp with messages; unavailable dates skip on keyboard; invalid typed segments keep the field invalid with `aria-invalid` and a message; reduced motion disables popover transitions.

**Interface contract**

Provides: components with spec ids `ui.datePicker`, `ui.dateRangePicker`, `ui.timeField`, `ui.dateTimeField`, `ui.relativeDatePicker`, `ui.calendar`; types `DateValue`, `RelativeRange`; helpers `toISODate`, `parseISODate`. Consumes: Popover, Field, Input, Button (PAP-237, PAP-236), primitive library decision (PAP-212; React Aria fallback), tokens (PAP-66), `LocaleProvider` (PAP-27, soft), relative-date fixture (PAP-279). Consumed by PAP-338 date type, filter builder, PAP-344 calendar navigation, PAP-180 invoices, PAP-58 invitation expiry, the sibling adapters.

**Definition of done**

* Six components merged with stories for every state and RTL; `vitest-axe` clean; formatting and parsing tests for en-US, en-GB, de-DE, ja-JP, ar-EG with DST boundaries and leap day; `RelativeRange` round-trips through the PAP-279 fixture.
* Screenshots of `Pickers` stories at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark; `docs/design/forms-and-dates.md` pickers section; changelog; Linear comment on PAP-338 and PAP-166.

**Test plan**

* Unit: segment editing; min and max clamping; unavailable date skipping; preset resolution at quarter and year boundaries; DST (`America/Los_Angeles`, `Europe/Berlin`) and leap day; 12 and 24 hour parsing.
* Interaction (`play`): open picker, arrow to a date, Enter selects, Escape closes returning focus; range selection by keyboard; segment typing advances.
* E2E: none (Storybook).

**Demo**

Reviewer opens Storybook `Pickers/DatePicker`, types a date by keyboard only, opens the calendar with `Alt+Down`, picks "last quarter" in the range story, switches locale to `de-DE` and RTL `ar-EG`. Under two minutes.

**Edge cases**

* Paste of `2026-13-01`: rejected segment, field stays invalid with message.
* Locale with non-Gregorian calendar (`fa-IR`): calendar follows `Intl` calendar; documented limits.
* User and tenant zones differ: `DateTimeField` shows the zone badge; storage in UTC with zone recorded.
* Reduced motion: no popover transitions.

**Dependencies**

PAP-237 (hard, Popover), PAP-236 (hard, Field and Input), PAP-212 (soft, dated fallback to React Aria if not merged by 09-22). Soft: PAP-27, PAP-279. Blocks PAP-338, the filter builder, PAP-344 and the sibling.

**Agent**

Builder: Iris (Component Crafter). Reviewer: Sentinel (Code Reviewer, Visual Inspector).

**Size**

M: one session.
