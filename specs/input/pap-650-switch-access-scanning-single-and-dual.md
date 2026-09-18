---
identifier: "PAP-650"
title: "Switch access scanning: single and dual switch auto-scan over focusables and groups with highlight, timing and an on-screen action menu"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Voice and accessibility certification"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-152", "PAP-158", "PAP-647"]
blocks: []
key: "r4/input/switch-access-scanning"
url: "https://linear.app/paperos/issue/PAP-650/switch-access-scanning-single-and-dual-switch-auto-scan-over"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:22.803Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-650: Switch access scanning: single and dual switch auto-scan over focusables and groups with highlight, timing and an on-screen action menu

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 (NJ-19 scope freeze; reinstate via NJ-14). The brief names accessibility switch input. Users with one or two switches (mapped to `Space` and `Enter`, a Bluetooth switch interface or a gamepad button) need scanning: the app highlights groups then items in turn and the switch selects. Build it on the focus regions and spatial groups already planned.

**Scope**

In: `packages/input/src/switch/{ScanController,ScanHighlight,ActionMenu}.ts`; modes `auto` (timer advances) and `step` (switch 1 advances, switch 2 selects); group scanning (regions → groups → items) using PAP-152 regions and PAP-158 `FocusGroup`s; `ActionMenu` after selection (activate, long-press, scroll, back, palette); settings in `/settings/accessibility` (PAP-647).

Out: hardware drivers (OS maps switches to keys), eye tracking, text entry beyond PAP-158's `SpatialKeyboard`.

**Spec**

* Scan order: regions in `F6` order, then `FocusGroup`s, then focusable items inside the group; `auto` interval 500 to 5,000 ms with a visible countdown ring; loop count before returning to region level (default 2).
* Highlight is a high-contrast overlay (4 px ring from PAP-158's TV theme) plus `aria-live` announcement of the item's accessible name; the scanned item receives real focus only on selection so screen readers are not flooded.
* Selection opens `ActionMenu` for elements with more than one action (links, editable cells); single-action elements activate directly with a `click`; `ActionMenu` itself is scanned.
* Switch inputs: keyboard `Space` and `Enter` by default, remappable to gamepad buttons through PAP-158's mapping or any chord via PAP-153; a gamepad button press works even without spatial mode.
* Exit: hold switch 1 for 3 s or the `ActionMenu` "Turn off scanning"; state persists per user.

**Interface contract**

Provides: `ScanController`, `useSwitchScanning()`, `ScanHighlight`, `ActionMenu`, settings keys `switch.*`, commands `switch.toggle`. Consumes: regions and announcer (PAP-152), `FocusGroup` and TV ring (PAP-158), preferences page (PAP-647), keymap chords (PAP-153), gamepad events (PAP-150).

**Definition of done**

* Template app operable end to end (navigate, open a record, edit a select, run a palette command) with a single switch in auto mode and two switches in step mode; recording attached; screenshots at 1024 and 1920; `docs/platform/a11y/switch-access.md`; changelog.

**Test plan**

* Unit: scan order construction from fixtures; timer and loop maths with fake timers; action menu decision per element kind.
* Integration: scanning across a virtualised grid loads rows as it advances.
* E2E: enable scanning, auto-scan into the sidebar, select Inbox, scan into the list, open a record, exit with a long press.

**Demo**

Reviewer enables single-switch scanning at 1,000 ms and drives the demo app with the space bar only. Under two minutes.

**Edge cases**

* Element scrolled out of view: scrolled in before highlight.
* Dialog opens: scan restarts at the dialog root.

**Dependencies**

PAP-152 (hard), PAP-647 (hard), PAP-158 (hard, groups; deferred too). Deferred; nothing waits on it.

**Agent**

Builder: Iris (Motion and Input Stylist) with Nova. Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/input/accessibility-input-preferences` = PAP-647.
