---
identifier: "PAP-663"
title: "Specialised inputs: NumberInput, PasswordInput, OTPInput, SearchInput, ColorPicker, FileUpload with progress and crop, TagInput and RatingInput"
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
blockedBy: ["PAP-37", "PAP-238"]
blocks: ["PAP-339", "PAP-658"]
key: "r4/design-system/specialised-inputs"
url: "https://linear.app/paperos/issue/PAP-663/specialised-inputs-numberinput-passwordinput-otpinput-searchinput"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:24.124Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-663: Specialised inputs: NumberInput, PasswordInput, OTPInput, SearchInput, ColorPicker, FileUpload with progress and crop, TagInput and RatingInput

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

The nine form controls in PAP-236 cover text and toggles; auth pages need OTP and password fields, the branding page needs a colour picker, attachments need an upload control with progress, select editors need chips. Build the eight specialised inputs the benchmark systems ship so no page hand-rolls one.

**Scope**

In: `packages/ui/src/inputs/{NumberInput,PasswordInput,OTPInput,SearchInput,ColorPicker,FileUpload,TagInput,RatingInput}.tsx` with `meta.ts` spec ids, stories, `Field` integration and `useAppForm` compatibility.

Out: date and time (PAP-233 children), rich text (PAP-142), combobox internals (PAP-238), drag-and-drop sensors (PAP-329; `FileUpload` uses native drop with an optional `DropZone` upgrade).

**Spec**

* `NumberInput`: locale-aware parsing and formatting via `Intl.NumberFormat` (`de-DE` `1.234,5`), stepper buttons and `ArrowUp|Down` with `step` and `shift` ×10, `min|max|precision`, `inputmode="decimal"`, optional unit or currency adornment, minor-unit mode for `Money` (string in and out).
* `PasswordInput`: reveal toggle with `aria-pressed`, optional strength meter (zxcvbn-ts, lazy), caps-lock hint; `OTPInput`: n boxes (default 6), paste of a full code distributes, auto-advance and backspace, `autocomplete="one-time-code"`, single hidden input for screen readers, `onComplete`.
* `SearchInput`: leading icon, clear button, `Escape` clears, optional `shortcut` hint (`Kbd`), `loading` state, debounced `onSearch`; `RatingInput`: stars or custom icon, `max`, half steps, keyboard arrows, `aria-valuetext` ("3 of 5").
* `ColorPicker`: OKLCH-aware picker with hue and lightness planes, hex and OKLCH text inputs, swatches from the token ramps, eyedropper when `EyeDropper` exists, live contrast readout against `bg.surface` using PAP-66's `tokens:check` maths; value is a hex string.
* `FileUpload`: click or drop (native `dragover`), `accept`, `multiple`, `maxSize`, per-file progress from PAP-37 `uploadFile`, retry, remove, image preview with an optional crop step (`react-easy-crop`, aspect presets for avatars and logos) producing a Blob; `TagInput`: chips with remove, `Combobox` suggestions (PAP-238), `allowCustom`, paste splitting on commas, max tags, chips reorder by keyboard.
* All controls forward refs, expose `data-invalid|data-disabled`, work inside `Field`, and follow the 44 px coarse-pointer rule.

**Interface contract**

Provides: components with spec ids `ui.numberInput`, `ui.passwordInput`, `ui.otpInput`, `ui.searchInput`, `ui.colorPicker`, `ui.fileUpload`, `ui.tagInput`, `ui.ratingInput`; `parseLocaleNumber`, `formatLocaleNumber`. Consumes: Field, Input, Button (PAP-236), Combobox (PAP-238), Popover (PAP-237), `Icon` (PAP-68), uploads and variants (PAP-37), contrast maths (PAP-66), `Kbd` (PAP-661, soft). Consumed by the branding page, PAP-224 auth pages (OTP, password), PAP-339 `multiSelect` editor (`TagInput`) and attachment editor (`FileUpload`), PAP-338 number and rating editors, PAP-58 avatars.

**Definition of done**

* Eight controls merged with stories for every state and RTL; `play` tests for OTP paste, NumberInput stepping, TagInput keyboard and FileUpload progress with a mocked uploader; `vitest-axe` clean.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark; `docs/design/forms-and-dates.md` inputs section; changelog; Linear comment on PAP-224 and PAP-339.

**Test plan**

* Unit: locale number parse and format for five locales; OTP paste distribution; rating half steps and `aria-valuetext`; colour conversions and contrast readout; tag paste splitting; file size and type validation.
* Interaction: reveal password; OTP auto-advance and backspace; NumberInput shift-step; crop step produces a blob of the requested aspect.
* E2E: none (Storybook; consumers cover flows).

**Demo**

Reviewer opens Storybook `Inputs/Gallery`, pastes a six-digit code into OTPInput, steps a NumberInput in `de-DE`, picks a colour and reads the contrast badge, drops an image into FileUpload and crops it. Under two minutes.

**Edge cases**

* Paste of `1,234.56` into a `de-DE` NumberInput: parsed with a preview of the interpretation before commit.
* `EyeDropper` unsupported: button hidden.
* Upload fails mid-way: retry keeps the queue order; removed files abort their request.
* OTP on iOS: `autocomplete="one-time-code"` autofill fills all boxes.

**Dependencies**

PAP-238 (hard), PAP-37 (hard for real uploads; mocked uploader in stories). Soft: navigation `Kbd`. Blocks the branding page (ColorPicker, FileUpload) and PAP-339 (TagInput, FileUpload); PAP-224 swaps in `OTPInput` when it lands (soft).

**Agent**

Builder: Iris (Component Crafter). Reviewer: Sentinel (Code Reviewer, Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/design-system/navigation-components` = PAP-661.
