---
key: "input/dnd/keyboard-announcements"
title: "Keyboard alternative, announcements and focus restore"
project: "input"
parent: "PAP-155"
phase: "P1"
type: "Build"
priority: 2
size: null
surfaces: ["Customer", "Staff"]
milestone: "Touch, pen, gamepad"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent3/pending-issues.json"
linearDocument: null
identifier: "PAP-330"
status: "created"
createdAt: "2026-09-17"
---

# Keyboard alternative, announcements and focus restore

**Goal**

Make drag-and-drop (PAP-155) work for everyone: a keyboard grammar to pick up, move and drop, screen-reader announcements through the shared announcer, focus restored after drop or cancel, and registry commands so keymaps and voice can trigger the same moves.

**Scope**

In:

* Customised `KeyboardSensor`: `Space`/`Enter` pick up, arrows move, `PageUp/PageDown` change container, `Home/End`, `Space` drops, `Escape` cancels; instructions announced on pickup.
* Announcement templates in `packages/input/src/copy/dnd.ts` ("Moved Task A to position 3 of 8 in Doing", denied reasons) via `LiveAnnouncer` (PAP-152).
* `useFocusRestore` to the moved item's handle after drop, original handle after cancel.
* Commands `dnd.pickUp|drop|cancel` (PAP-151).
* Snapshot tests of every announcement string.

Out: sensors (sibling 1), high-level components (sibling 3).

**Spec**

* Off-screen targets in virtualised lists scroll into view before announcing.
* RTL flips arrow semantics.

**Interface contract**

Exposes `KeyboardSensor`, `announceDnd(event)`, copy keys, commands. Consumes `LiveAnnouncer`, `useFocusRestore` (PAP-152), `defineCommand` (PAP-151), sibling 1's provider.

**Definition of done**

* Keyboard-only reorder and cross-container move work on the sample pages; announcement snapshots committed; NVDA and VoiceOver spot check recorded for PAP-156; Linear comment.

**Test plan**

* Vitest: grammar state machine (pick up, move, drop, cancel, invalid keys ignored), announcement templates incl. plurals and RTL, focus restore targets.
* Playwright: `Tab` to a handle, `Space`, arrows, `Space`, assert order and `aria-live` text; `Escape` restores focus to the original handle; virtualised off-screen target scrolls into view.

**Demo**

Tab to a card handle, press `Space`, `ArrowDown` twice, `Space`, and read the live region text in the devtools a11y panel; press `Escape` on another pickup and see focus return. Under two minutes.

**Edge cases**

* Item deleted during a keyboard drag: cancel with announcement.
* Screen reader in browse mode: handle exposes instructions via `aria-describedby`.

**Dependencies**

Sibling 1, PAP-152 (hard). PAP-151 (soft). Blocks sibling 3; feeds PAP-156.

**Agent**

Built by Iris (Motion and Input Stylist) with Nova. Reviewed by Sentinel (Edge Case Hunter).

**Size**

S: grammar, strings and focus handling.
