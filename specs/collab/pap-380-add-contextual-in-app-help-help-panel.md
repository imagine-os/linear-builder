---
identifier: "PAP-380"
title: "Add contextual in-app help: help panel bound to page spec `purpose` and docs deep links, first-visit product tour, keyboard hint overlay"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Customer", "Staff"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-128"]
blocks: []
key: "collab/in-app-help"
url: "https://linear.app/paperos/issue/PAP-380/add-contextual-in-app-help-help-panel-bound-to-page-spec-purpose-and"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:14.622Z"
---

# PAP-380: Add contextual in-app help: help panel bound to page spec `purpose` and docs deep links, first-visit product tour, keyboard hint overlay

**Goal**

Connect the docs engine to the page the user is on: a help panel that shows the page spec's `purpose`, linked docs and related commands; a first-visit tour built from spec annotations; and a keyboard hint overlay from the command manifest. Part of the onboarding golden path for PAP-5.

**Scope**

In:

* `HelpPanel` in the inspector slot (`?` or `help.open` command): page `purpose` from the spec (PAP-114), `docs[]` links resolved through PAP-128 (repo or tenant pages), related commands from `commands.manifest.json` (PAP-151) with effective chords (PAP-153), "Ask a question" that opens a comment thread on the page (PAP-131).
* Tour: spec section `tour: [{ target: specKey, title, body }]` rendered with popovers anchored to `data-spec-key`; shown once per user per page version (`user_tour_seen`), replayable from the panel.
* Keyboard hint overlay: hold `alt` for 600 ms to show chord badges on visible `CommandButton`s; `help.shortcuts` opens the full sheet (PAP-151).
* Spec validator rule (PAP-115): `docs[]` paths must exist; warn when `purpose` is missing.

Out: chat assistant, video tutorials, third-party tour libraries.

**Spec**

* Panel content cached per route; tour steps limited to 7; overlay excluded under reduced motion (static badges instead).
* Tour respects `FocusScope` (PAP-152) and is keyboard navigable.
* Customer pages show only `customer` audience docs.

**Interface contract**

Exposes: `HelpPanel`, `useHelpForRoute()`, `TourProvider`, spec fields `help.docs[]`, `help.tour[]` (added to PAP-114 schema), table `user_tour_seen(user_id, route, version, seen_at)`, command `help.open`. Consumes: spec loader and `purpose` (PAP-114, PAP-120), docs resolution and `renderMdx` (PAP-128), manifest and `CommandButton` (PAP-151), chords (PAP-153), `Popover` (PAP-237), `Inspector` slot (PAP-70), comments (PAP-131), audience (PAP-55).

**Definition of done**

* Template pages show purpose and docs in the panel; the sample page's tour runs once and replays; `alt` overlay shows chords.
* Screenshots at 375, 1024 and 1440 in light and dark; axe clean; `docs/collab/in-app-help.md`; CHANGELOG entry; Linear comment.

**Test plan**

* Vitest: docs path resolution (repo, tenant, missing), tour step limit, seen-state versioning, chord badge mapping.
* Integration: validator fails a spec with a missing doc path.
* Playwright: first visit shows the tour, complete it, reload shows nothing, replay from the panel; press `?` and open a linked doc; hold `alt` and assert badges; customer context sees only customer docs; run at 375 and 1440.
* Visual: Gate 3 baselines for panel, tour popover and overlay.

**Demo**

Open the records page as a new user, step through the three-step tour, press `?` to read the purpose and open the linked doc, hold `alt` to see shortcut badges, click “Ask a question” and post it. Under two minutes.

**Edge cases**

* Tour target missing after a layout change: step skipped with a console warning.
* Page without spec: panel shows the app-level help doc.
* Overlay while a Dialog is open: badges only inside the dialog.

**Dependencies**

PAP-128 (hard). Soft: PAP-114, PAP-151, PAP-153, PAP-131, PAP-152, PAP-115, runtime docs store.

**Agent**

Built by Quill (Page Spec Writer) with Iris on the panel and tour. Reviewed by Sentinel (Visual Inspector).

**Size**

S: panel, tour and overlay over existing data.
