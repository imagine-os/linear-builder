# input — Multi-Input Control & Accessibility
PHASE P1 prio 2 dependsOn ['design-system']
SUMMARY: Keyboard, mouse, touch, pen, gamepad and voice through one command registry and input abstraction, with focus management and screen-reader conformance.
DESC: Goal: every app is controllable by every input method and usable by every person. A global command registry powers keyboard shortcuts, a command palette and per-page scoping, with user-customizable keymaps. A unified input abstraction lets components handle mouse, touch, pen and gamepad uniformly; touch gestures and haptics work on mobile, pen pressure on the canvas, spatial focus for TV and kiosk. Voice commands and dictation route through the same registry. Focus management, accessible drag-and-drop and screen-reader testing across NVDA, VoiceOver and TalkBack complete it, with an accessibility statement per app. Non-goal: eye tracking or BCI in this build.
MILESTONES: ['Keyboard and command system 2026-09-23: Command registry, input abstraction, focus management', 'Touch, pen, gamepad 2026-09-27: Keymaps, touch gestures, drag-and-drop, screen reader fixes', 'Voice and accessibility certification 2026-09-30: Voice, pen, gamepad, accessibility statement']


## PAP-150 [P0 Spec S prio2 Ready for Claude] Design a unified input event abstraction so components handle mouse, touch, pen and gamepad uniformly
key=input/input-abstraction milestone=Keyboard and command system agent=Builder: Nova (Product Systems Engineer, owner of multi-inpu
blockedBy=[] blocks=['PAP-157', 'PAP-155', 'PAP-154']
GOAL: Define one input model that every PaperOS component uses so that mouse, touch, pen and gamepad behave consistently without each component re-implementing device checks. The output is a spec plus a small typed core in `packages/input` that later issues (gestures, drag-and-drop, pen, gamepad) build on; it decides the vocabulary (press, move, release, cancel, modifiers, pointer type, pressure) once.
SCOPE: In:

* Spec `docs/platform/input/abstraction.md`: event vocabulary, coordinate spaces, capture semantics, device capability detection, how the model maps to DOM Pointer Events, Touch Events fallback, Gamepad API and keyboard.
* `packages/input/src/core/`: `InputEvent` union (`press | move | release | cancel | wheel | key | gamepad`), `Pointer` (`id, type: 'mouse'|'touch'|'pen'|'gamepad-cursor', x, y, pressure, tilt, twist, buttons, isPrimary`), `Modifiers`, `usePointerSurface(ref, handlers, { capture, passive })` hook translating `pointerdown/move/up/cancel` and `lostpointercapture` into the union with pointer capture handled centrally.
* Capability detection `useInputCapabilities()` → `{ coarsePointer, finePointer, hover, touchPoints, penSeen, gamepadConnected, keyboardSeen }` from media queries (`pointer`, `hover`, `any-pointer`) plus observed events; exposed as `data-input-*` attribut
SPEC(first 1200): * Coordinates: every pointer carries `client`, `page` and `surface` (relative to the hooked element, in CSS pixels, scaled by `devicePixelRatio` only where the consumer asks) coordinates.
* Capture: on `press` the hook calls `setPointerCapture`; `release`/`cancel` always fire once per pointer id; `cancel` fires on `pointercancel`, window blur, and `visibilitychange` hidden.
* Multi-pointer: handlers receive the full active pointer map for pinch/rotate consumers.
* Keyboard: `key` events normalised to a `Key` (`code`, `key`, modifiers, `repeat`) and a portable chord string `mod+shift+k` shared with `input/command-registry` (`mod` = Cmd on macOS, Ctrl elsewhere).
* Gamepad: a polling loop (`requestAnimationFrame`) emits `gamepad` events with normalised sticks and buttons (standard mapping) and a synthetic `gamepad-cursor` pointer when cursor mode is enabled by `input/gamepad`.
* Pen: `pressure`, `tiltX/Y`, `twist` pass through; `pointerType === 'pen'` with barrel button maps to `buttons` bit 2; palm rejection rule: while a pen is active, touch presses on the same surface are ignored for 300 ms.
* Component contract: all `packages/ui` interactive components must use `usePointerSurface
DOD:
* Spec merged and linked from `design-system/guidelines-docs`.
* `packages/input` core with Vitest tests using synthetic `PointerEvent`s for capture, cancel-on-blur, slop thresholds and chord normalisation on macOS and Linux `navigator.platform` mocks.
* Storybook "Input Playground" story visualising active pointers, pressure and capabilities at 375 (touch emulation) and 1280 px, screenshots attached.
* Biome rule enabled with zero violations in `packages/ui`.
* `data-input-*` attributes documented and used by at least the Button primitive for coarse hit targets.
* Changelog entry (developer) and Linear comment with the playground link.
EDGE:
* Touch-then-mouse devices (Surface): capabilities update live when a new pointer type is observed; do not freeze on first paint.
* `pointercancel` on scroll: consumers must treat `cancel` like release without action; document `touch-action` requirements.
* Right-click on touch (long-press context menu): suppress native menu only when a handler claims the long-press.
* iOS Safari missing `pointerrawupdate` and gamepad quirks: polling handles both.
* High pressure values > 1 from some drivers: clamp to \[0, 1\].
* Windows with pen hover: `move` with `buttons === 0` must be distinguishable (hover) from a drag.
DEPS: * None to start (readyNow). Informs `design-system/primitives` (hit targets), `input/command-registry` (chord format), `input/touch-gestures`, `input/drag-drop`, `input/pen`, `input/gamepad`, `collab/canvas-view`.


## PAP-151 [P0 Build L prio1 Backlog] Build the global command registry with keyboard shortcuts, command palette and per-page scoping
key=input/command-registry milestone=Keyboard and command system agent=Builder: Nova. Reviewer: Sentinel (Code Reviewer, Security A
blockedBy=['PAP-67'] blocks=['PAP-159', 'PAP-153']
GOAL: Make everything in a PaperOS app a command: a single registry knows every action, its label, shortcut, scope and permission, and powers keyboard shortcuts, the command palette, menus, toolbars, voice and gamepad. Discoverability comes for free (the palette lists what you can do here), and agents can invoke the same commands programmatically.
SCOPE: In:

* `packages/input/src/commands/`: `defineCommand({ id, title, description?, icon?, keywords?, scope: 'global'|'page'|'component', shortcut?: Chord | Chord[], when?: (ctx) => boolean, permission?: string, run: (ctx, args?) => void|Promise, argsSchema?: Zod })`, `CommandRegistry` with `register/unregister/execute/list(ctx)`, and React hooks `useCommand(def)` (registers for the component's lifetime), `useCommands(scopeId)`, `useShortcut(chord, handler)`.
* Scoping: scope stack (`global` → page route id → focused component scope) managed by `CommandScopeProvider`; the innermost matching command wins; page specs declare `commands:` (`spec-builder/schema`) and `spec-builder/layout-codegen` registers them.
* Keyboard: chord parser and matcher using the `mod+shift+k` format from `input/input-abstraction`, sequences (`g i`, 1 s timeout), platform display (`⌘⇧K` vs `Ctrl+Shift+K`), conflict d
SPEC(first 1200): * IDs are dot-namespaced (`nav.goToInbox`, `record.duplicate`, `editor.bold`); a Vitest test fails on duplicate IDs across the registry at build time via a generated `commands.manifest.json` (`pnpm commands:manifest`) that also feeds docs and `input/keymaps`.
* `when` receives `{ route, selection, focusedScope, permissions, capabilities, isEditing }`; `permission` is checked with `packages/permissions` `can()` and hidden commands never appear in the palette.
* Execution telemetry: `command.executed { id, source: 'keyboard'|'palette'|'menu'|'voice'|'gamepad'|'api' }` to `data-layer/observability`; failures toast with the error and are logged.
* Palette renders at most 50 results, virtualised; results update under 16 ms for 2,000 commands (benchmark test).
* Accessibility: palette input `role="combobox"`, results `role="listbox"`, `aria-activedescendant`; help sheet is a Dialog; shortcuts announced via `aria-keyshortcuts` on buttons that expose a command (`<CommandButton commandId />`).
* Default global commands shipped: `nav.*` for spec-declared navigation, `ui.toggleSidebar`, `ui.toggleInspector`, `ui.toggleTheme`, `edit.undo/redo`, `help.shortcuts`, `search.open`.
DOD:
* Palette opens with `mod+k` on every page, lists page-scoped commands from a sample spec, executes with keyboard only; Playwright tests at 375 (full-screen sheet) and 1280 px, screenshots attached.
* Vitest tests: chord parsing (incl. sequences, macOS/Linux), scope precedence, `when` guards, duplicate-ID detection, permission hiding.
* Manifest generated in CI and committed; docs page lists all commands from it.
* Agent execution endpoint tested with an agent key (allowed and denied cases) and audit rows.
* Storybook stories for palette (empty, results, argument prompt) in three themes, axe clean.
* Changelog entry and Linear comment with demo link.
EDGE:
* Shortcut typed while focus is in a Tiptap editor: only `allowInInput` commands fire; `mod+b` goes to the editor.
* Two components register the same chord in sibling scopes: focused one wins; unfocused registrations are inert.
* Browser-reserved chords (`mod+w`, `mod+t`): warn at registration; never claim them.
* Non-Latin keyboard layouts: match on `event.code` for letters, `event.key` for symbols; document the trade-off.
* Palette opened while a Dialog is open: stacks above it and returns focus correctly.
* Command `run` throws asynchronously: palette closes, toast shows, error logged; registry stays healthy.
DEPS: * `design-system/primitives` and `design-system/layout-components` (CommandBar, Dialog), `input/input-abstraction` (chord format), `identity/rbac-abac` (`can()`), `data-layer/api-layer` (execute endpoint), `spec-builder/schema` (`commands:` section, may land after; registry works without it).


## PAP-152 [P1 Build M prio1 Backlog] Implement robust focus management, roving tabindex and skip links across all layouts
key=input/focus-management milestone=Keyboard and command system agent=Builder: Iris (Motion and Input Stylist sub-agent) for regio
blockedBy=['PAP-70'] blocks=['PAP-158', 'PAP-156']
GOAL: Guarantee that keyboard users never lose their place: a predictable focus order through nav, sidebar, main content and inspector; roving tabindex inside composite widgets; skip links; focus restoration after dialogs, route changes and live updates. This is the base that screen-reader conformance, gamepad spatial navigation and the command system all rely on.
SCOPE: In:

* `packages/input/src/focus/`: `FocusRegion` (landmark-level region with an id, entry point and `F6` cycling), `useRovingTabIndex(items, { orientation, loop, typeahead })`, `FocusScope` (trap and restore, built on `@radix-ui/react-focus-scope` or Base UI's equivalent chosen in `design-system/primitives`), `useFocusRestore(key)` for route changes, `FocusRing` styles from `design-system/tokens`.
* Skip links: "Skip to main content", "Skip to navigation", "Skip to inspector" rendered by `AppFrame` (`design-system/layout-components`), visible on focus.
* Region cycling: `F6` / `shift+F6` move between regions (registered as commands `focus.nextRegion` / `focus.prevRegion` in `input/command-registry`); `Escape` inside a region returns to its entry point.
* Route-change policy: on navigation, focus the page `h1` (or `[data-focus-entry]`) and announce the page title via a live region; back 
SPEC(first 1200): * Roving tabindex: one item `tabindex=0`, others `-1`; arrows move per orientation, `Home/End` jump, typeahead over `aria-label`/text with 500 ms buffer; disabled items skipped unless `focusableWhenDisabled`; works with virtualised lists via `getItemElement(index)` and `scrollIntoView`.
* `FocusScope` options: `trap`, `restoreFocus`, `autoFocus: 'first'|'container'|selector`; nested scopes form a stack; the top scope owns `Tab`.
* Focus visibility: `:focus-visible` ring only; programmatic focus after keyboard interaction shows the ring (track last input modality via `input/input-abstraction` capabilities); after pointer interaction it does not.
* Regions registered by `AppFrame` slots (`nav`, `sidebar`, `main`, `inspector`, `commandbar`, `statusbar`) with `aria-label`s; detached Tauri windows (`app-shell/breakpoints-windows`) form their own region set.
* Tables: grid navigation (`role="grid"`, arrow keys across cells, `Enter` edits, `Escape` cancels) is provided as `useGridFocus` for `tables/grid-view`.
* Announcements: one shared `LiveAnnouncer` (`polite` and `assertive` regions) with de-duplication, exported for all packages.
* Tests run in Playwright with `page.keyboard.press('T
DOD:
* Skip links, `F6` cycling and route-change focus work in the template app; Playwright tests at 375 (collapsed drawers) and 1280 px; focus-order strips attached for both.
* Vitest tests for roving tabindex (orientation, loop, typeahead, virtualised), scope stack and restore.
* `useGridFocus` demo with a 1,000-row virtual grid keeps focus after scrolling and remote row insertion.
* axe rules `focus-order-semantics`, `skip-link`, `tabindex` pass on all Storybook stories.
* Docs `docs/platform/input/focus.md` with the policy table (route change, dialog, live update, deletion).
* Changelog entry and Linear comment with demo link and focus strips.
EDGE:
* Focused row deleted by another user mid-typeahead: focus moves to the next row and announces "Row removed by Ada".
* Dialog opened from a menu item that unmounts: restore target gone → fall back to the menu trigger, then region entry.
* Drawer collapse at narrow widths moves the sidebar into a `Drawer`; region order stays nav → main → drawer.
* Tauri detached inspector: `F6` cycles within that window only; `mod+shift+]` (from `app-shell/breakpoints-windows`) switches windows.
* iframes (embedded views from `tables/view-sharing`): treat as a single stop; do not trap.
* Autofocus fights: only the top `FocusScope` may autofocus; nested autofocus logs a dev warning.
DEPS: * `design-system/layout-components` (AppFrame slots), `design-system/primitives` (focus scope primitive), `design-system/tokens` (ring), `input/command-registry` (F6 commands), `input/input-abstraction` (modality). Consumed by `input/screen-reader`, `input/gamepad`, `input/drag-drop`, `tables/grid-view`.


## PAP-153 [P1 Build M prio2 Backlog] Support user-customizable keymaps with presets (default, Vim-style, Linear-like) synced per user
key=input/keymaps milestone=Touch, pen, gamepad agent=Builder: Nova. Reviewer: Sentinel (Code Reviewer, Edge Case 
blockedBy=['PAP-151'] blocks=[]
GOAL: Let power users bring their habits: choose a keymap preset (Default, Vim-style, Linear-like), rebind any command, and have those bindings follow them to every device and window. Keymaps are a layer over the command registry, so no command changes and conflicts are detected before they bite.
SCOPE: In:

* `packages/input/src/keymaps/`: `Keymap = { id, name, base?: presetId, bindings: Record<commandId, Chord[] | null> }`; resolver merges preset → user overrides → page-scope overrides and feeds the registry's matcher (`input/command-registry` exposes `setBindingsResolver`).
* Presets shipped in `presets/`: `default` (registry defaults), `vim` (`j/k` list navigation, `g g`/`G`, `/` search, `:` palette, `h/l` collapse/expand, Escape semantics), `linear` (`c` create, `e` edit, `x` select, `s` status, `a` assign, `g i` inbox, `g b` board), documented with a comparison table.
* Settings UI at `/settings/keyboard`: preset picker, searchable command list with current chords, click-to-record binding (captures next chord, shows conflicts inline, allows two chords per command), reset per command and per keymap, import/export JSON.
* Persistence: `user_preferences.keymap jsonb` via `identity/be
SPEC(first 1200): * Resolver output is memoised per scope stack; rebinding updates in under one frame; `input/command-registry` help sheet and palette hints read effective chords from the resolver, never from `defineCommand` defaults.
* Vim preset implements a tiny modal layer: `normal` (default in lists and read views) and `insert` (any editable focused); `Escape` returns to normal without blurring; mode shown in the status bar when the vim preset is active.
* Recording UI uses `input/input-abstraction` key normalisation; ignores lone modifiers; supports sequences by pausing 1 s.
* Export format is the `Keymap` JSON, validated by Zod on import; unknown command IDs are kept but greyed out ("not available in this app").
* Manifest-driven: the settings list is built from `commands.manifest.json` so every app's commands appear automatically; page-scoped commands are grouped by page title from the spec.
* Copy in `packages/input/src/copy/keymaps.ts`; all controls from `design-system/primitives`.
DOD:
* Switching to the Linear preset makes `c` open create on a sample list page and `g i` navigate; Playwright tests for all three presets on key flows at 768 and 1440 px, screenshots of the settings page.
* Vitest tests: merge precedence, conflict detection, import validation, vim mode transitions.
* Preference persists across reload and to a second browser within 2 s (sync test).
* Storybook story of the settings page (empty search, conflict state, recording state) in three themes; axe clean.
* Docs `docs/platform/input/keymaps.md` with the preset comparison table.
* Changelog entry and Linear comment with demo link.
EDGE:
* User rebinds `mod+k` away from the palette: allow, but require a replacement binding for `palette.open` before saving.
* Chord uses a key missing on the current layout (`§`): shows a warning and still stores it.
* Preset updated in a later release adds a binding that conflicts with a user override: user override wins; changelog notes it.
* Vim normal mode and a customer-facing page with text-heavy forms: vim layer only applies where `role` is list, grid or tree; forms stay insert.
* Import file from another app with 40 unknown commands: imports the rest, lists unknowns.
* Two windows change bindings simultaneously: last write wins; both windows re-resolve on the sync event.
DEPS: * `input/command-registry` (resolver hook, manifest), `input/input-abstraction` (key normalisation), `identity/better-auth` or `data-layer/core-entities` (preference storage), `realtime/record-sync` and `realtime/multi-window-sync` (propagation), `design-system/primitives`.


## PAP-154 [P1 Build M prio2 Backlog] Implement a touch gesture system (swipe, pinch, long-press) with haptics on mobile targets
key=input/touch-gestures milestone=Touch, pen, gamepad agent=Builder: Nova with Forge (Tauri Smith) for the haptics plugi
blockedBy=['PAP-150', 'PAP-20'] blocks=[]
GOAL: Make PaperOS feel native on phones and tablets: swipe to reveal row actions, pinch to zoom canvases and images, long-press for context menus, pull to refresh, edge swipe for navigation, all with haptic feedback on Tauri mobile. Gestures are recognised through the shared input abstraction so they compose with mouse and pen without device-specific code in components.
SCOPE: In:

* `packages/input/src/gestures/`: recognisers `useTap`, `useLongPress`, `useSwipe` (direction, velocity, threshold), `usePinch` (scale, origin, rotation), `usePan` with momentum and rubber-banding, `usePullToRefresh`, `useEdgeSwipe`; all built on `usePointerSurface` from `input/input-abstraction`, with `@use-gesture/react` 10.x used only for pinch/wheel maths if the abstraction ADR chose it.
* Gesture arbitration: a `GestureArena` decides ownership when several recognisers see the same pointers (scroll vs swipe vs pan), following the thresholds table (tap slop, long-press 500 ms, drag start 10 px coarse).
* Components in `packages/ui`: `SwipeableRow` (leading/trailing actions, snap points, keyboard and menu fallback), `PinchZoomView`, `PullToRefresh`, `BottomSheet` (drag handle, snap points, dismiss by swipe, falls back to Dialog on desktop).
* Haptics: `packages/input/src/haptics.t
SPEC(first 1200): * Recogniser API returns handlers to spread and a state object; every gesture emits `start/move/end/cancel` with `{ pointers, delta, velocity, scale, center }`.
* `touch-action` is set per surface (`pan-y` for lists with horizontal swipes, `none` for canvases) and documented; the arena cancels a recogniser when the browser takes over scrolling (`pointercancel`).
* `SwipeableRow`: actions revealed at 30% width, committed at 60% or velocity > 0.5 px/ms, `Escape` or tap elsewhere closes; actions also available via the row's overflow `Menu` so no function is touch-only; announces "Actions revealed" via `LiveAnnouncer`.
* `PinchZoomView`: scale clamp 0.5–8, double-tap toggles 1×/2×, wheel+ctrl zoom on desktop, transform via CSS `transform` on a single layer for 60 fps; emits `viewport` for `collab/canvas-view` and `realtime/presence` viewport sharing.
* `BottomSheet`: snap points as fractions (`[0.4, 0.9]`), backdrop dismiss, `role="dialog"`, focus trap from `input/focus-management`, safe-area insets (`env(safe-area-inset-bottom)`).
* Haptics fire only on gesture commits (snap, threshold crossed), never on every move; at most 10 per second.
* Storybook stories use touch emulation (`view
DOD:
* Tauri Android and iOS builds (from `app-shell/tauri-mobile`) demonstrate swipe, pinch, long-press, pull-to-refresh with haptics; video attached from a device or emulator.
* Playwright touch tests at 320, 375 and 768 px using `page.touchscreen` and CDP `Input.dispatchTouchEvent` for multi-touch pinch; screenshots attached.
* Vitest tests for arena arbitration, thresholds and velocity math with synthetic pointer sequences.
* Touch-target audit passes on all `packages/ui` stories.
* Docs `docs/platform/input/gestures.md` with the arbitration table and `touch-action` guidance.
* Changelog entry and Linear comment with video and Storybook links.
EDGE:
* Swipe starts vertically then turns horizontal: arena locks direction after 10 px; no mid-gesture switch.
* Pinch with a third finger resting: use the two most recent pointers; ignore extras.
* Long-press on a link opens the native context menu: suppress only when a long-press handler is attached.
* Pull-to-refresh inside a nested scroll container: only the outermost at scroll top may claim it.
* Haptics API missing or denied: silent no-op, feature still works.
* Landscape phones with 320 px height: bottom sheet minimum snap adapts to viewport height.
DEPS: * `input/input-abstraction` (pointer surface, thresholds), `app-shell/tauri-mobile` (targets, haptics plugin), `design-system/primitives` (Menu, Dialog), `input/focus-management` (trap). Consumed by `collab/canvas-view`, `tables/grid-view`, `tables/kanban-view`, `identity/customer-portal-shell`.


## PAP-155 [P1 Build L prio2 Backlog] Build accessible drag-and-drop (dnd-kit) for tables, kanban and canvas with a keyboard alternative
key=input/drag-drop milestone=Touch, pen, gamepad agent=Builder: Nova (Views Engineer sub-agent). Reviewer: Sentinel
blockedBy=['PAP-150'] blocks=['PAP-173', 'PAP-167']
GOAL: Give every list, table, kanban board and canvas one accessible drag-and-drop system: pointer dragging with smooth previews, a full keyboard alternative (pick up, move, drop with arrow keys), screen-reader announcements, touch and pen support, and cross-window drags between detached panels. Reordering and moving items must work for everyone, and the engine must be the same in every view so agents implement it once.
SCOPE: In:

* `packages/input/src/dnd/` wrapping `@dnd-kit/core` 6.x and `@dnd-kit/sortable` with PaperOS sensors built on `input/input-abstraction` (`PointerSurfaceSensor` handling mouse, touch and pen with the shared thresholds) and dnd-kit's `KeyboardSensor` customised for grid movement.
* High-level components in `packages/ui`: `SortableList`, `SortableGrid` (2D), `KanbanDnd` (columns and cards, cross-column, WIP limit checks via a `canDrop` callback), `DropZone` (files and items), `DragHandle` (visible on hover/focus, always present for keyboard), `DragOverlay` preview with count badge for multi-select drags.
* Keyboard alternative: `Space`/`Enter` on a handle picks up, arrows move (with `PageUp/PageDown` for columns, `Home/End`), `Space` drops, `Escape` cancels; instructions announced on pickup; movement announced ("Moved Task A to position 3 of 8 in Doing").
* Multi-select drag: selected
SPEC(first 1200): * API: `<SortableList items getId onReorder renderItem strategy />`; `onReorder({ from, to, item, items })` is optimistic and reverts on rejected promise; ordering uses fractional indexing (`fractional-indexing` 3.x) helper `between(a, b)` exported for consumers storing `sort_key`.
* Announcements go through the shared `LiveAnnouncer` from `input/focus-management`; strings in `packages/input/src/copy/dnd.ts` templated with item label, position and container.
* `canDrop(source, target)` returns `true | { reason }`; a denied target renders a "not allowed" cursor and the reason in a tooltip and in the announcement.
* Touch: drag starts after 250 ms long-press with a haptic (`input/touch-gestures`) so lists still scroll; pen drags immediately with the barrel button or after 4 px.
* Performance: dragging within a virtualised 10,000-row `tables/grid-view` keeps 60 fps; only overlay and two neighbours re-render (React Profiler assertion in a test).
* Focus: after drop, focus returns to the moved item's handle; after cancel, to the original handle (`useFocusRestore`).
* Every component registers commands `dnd.pickUp`, `dnd.drop`, `dnd.cancel` in `input/command-registry` so keymaps and voic
DOD:
* `SortableList`, `KanbanDnd` and `DropZone` used in the template's sample pages; Playwright tests for pointer, touch and keyboard paths at 375, 1024 and 1440 px, screenshots of overlay and denied states attached.
* Screen-reader announcement text snapshot-tested; NVDA and VoiceOver spot check recorded for `input/screen-reader`.
* Cross-window drag demonstrated on Tauri Linux with video.
* Vitest tests for fractional indexing, `canDrop` handling, multi-select payloads and revert on failure.
* Storybook stories in three themes with reduced motion variant; axe clean.
* Docs `docs/platform/input/drag-drop.md`; changelog entry; Linear comment with demo and video links.
EDGE:
* Item list changes remotely during a drag (`realtime/record-sync`): keep the drag alive; recompute positions on drop; if the item was deleted, cancel with an announcement.
* Drop onto a column at its WIP limit: denied with reason "Doing is at its limit (5)".
* Dragging across a scroll boundary in a nested scroll container: auto-scroll the innermost container first.
* Keyboard drag while the list is virtualised and the target is off-screen: scroll target into view before announcing.
* Window loses focus mid-drag (alt-tab): cancel and restore.
* RTL layouts: arrow semantics flip; test with `dir="rtl"`.
DEPS: * `input/input-abstraction` (sensor), `input/focus-management` (announcer, restore), `input/touch-gestures` (long-press, haptics), `input/command-registry`, `realtime/multi-window-sync` (cross-window transfer), `design-system/primitives`. Consumed by `tables/grid-view`, `tables/kanban-view`, `tables/dashboard-blocks`, `collab/canvas-view`, `pm-linear/board-views`.


## PAP-156 [P1 Review M prio1 Backlog] Test and fix the screen reader experience (NVDA, VoiceOver, TalkBack) for core flows
key=input/screen-reader milestone=Touch, pen, gamepad agent=Builder: Sentinel (Visual Inspector sub-agent runs the proto
blockedBy=['PAP-152'] blocks=['PAP-160']
GOAL: Verify with real assistive technology, not only axe, that the core PaperOS flows are usable with NVDA on Windows, VoiceOver on macOS and iOS, and TalkBack on Android, then fix what breaks. The deliverable is a repeatable test protocol, recorded results, and merged fixes across primitives, focus management and the shell, so every later app inherits a working screen-reader experience.
SCOPE: In:

* Test protocol `docs/platform/a11y/screen-reader-protocol.md`: environment setup per AT (NVDA 2025.x with Firefox and Chrome, VoiceOver with Safari on macOS 15 and iOS 18, TalkBack with Chrome on Android 15), the flow scripts, what to record (spoken output transcript, pass/fail, severity per `quality/review-rubrics`).
* Core flows from `quality/e2e-flows`: sign in (passkey and magic link), tenant switch, navigate via skip links and `F6`, create/edit/delete a record in the grid, filter and sort a view, post a comment with a mention, open the command palette and run a command, receive a live update, complete a drag with the keyboard.
* Automated layer: Playwright with `@guidepup/playwright` (VoiceOver and NVDA driver) running the flows on macOS and Windows runners nightly, asserting the spoken phrase snapshots; TalkBack remains manual on a device or emulator with a recorded video.
* 
SPEC(first 1200): * Snapshot format for automated runs: JSON `{ flow, at, browser, steps: [{ action, spoken, expected, pass }] }` stored under `apps/web/e2e/a11y/snapshots/`; phrases matched with normalisation (case, punctuation, trailing "button"/"link" role words allowed).
* Conformance targets: every interactive element has an accessible name; roles and states match visual state; live regions announce remote changes at the agreed cadence (`realtime/presence`, `realtime/conflict-ux`); virtualised grids expose `aria-rowcount`/`aria-rowindex`; tables of over 50 columns provide a column picker reachable by keyboard; dialogs announce their title on open; toasts are `role="status"`.
* Windows runner: self-hosted GitHub/Forgejo runner (`forge/actions-runner`) VM with NVDA installed; macOS runner uses the hosted `macos-15` image with VoiceOver enabled via `guidepup` setup.
* Severity: Sev-1 blocks a flow, Sev-2 requires workaround, Sev-3 cosmetic; Sev-1/2 must be fixed before the milestone `Touch, pen, gamepad` closes.
* Each fix includes a regression snapshot so the nightly run guards it.
DOD:
* Protocol document merged and linked from `quality/review-rubrics`.
* Nightly `a11y-sr` job runs NVDA and VoiceOver flows green for three nights; failures post to Linear via `pm-linear/webhooks`.
* TalkBack manual run recorded (video) for all flows on a Pixel emulator or device, results in the report.
* Results report shows zero open Sev-1 and Sev-2 across the matrix; Sev-3 items filed as issues.
* At least the following fixes merged if found: grid row/col semantics, palette `aria-activedescendant`, live-region cadence, dialog titles, drag announcements.
* Changelog entry and Linear comment with the report link and one screenshot of the matrix.
EDGE:
* VoiceOver on iOS in a Tauri webview (WKWebView) differs from Safari: run the iOS flows in the Tauri app too, not only Safari.
* NVDA browse vs focus mode switching in the grid: ensure `role="application"` is never used and arrow keys work in focus mode.
* Speech output includes dynamic numbers (row counts, timestamps): snapshot normaliser replaces digits with `#`.
* Flaky AT startup on runners: retry once and quarantine per `quality/flake-quarantine`, never silently pass.
* Non-English locale on a runner: force `en-US` speech for stable snapshots; note localisation as a follow-up.
* Reduced-motion and high-contrast themes (`design-system/theming`): run one flow per theme to catch state-only-by-colour regressions.
DEPS: * `input/focus-management`, `design-system/primitives`, `design-system/a11y-audit` (component-level baseline), `quality/e2e-flows` (flow scripts), `forge/actions-runner` (Windows runner), `quality/flake-quarantine`, `input/drag-drop` (keyboard drag flow). Feeds `input/a11y-statement`.


## PAP-157 [P2 Build M prio3 Backlog] Support pen and stylus input with pressure for canvas and annotation
key=input/pen milestone=Voice and accessibility certification agent=Builder: Nova (Canvas Cartographer sub-agent). Reviewer: Sen
blockedBy=['PAP-150', 'PAP-132'] blocks=[]
GOAL: Make tablets with a stylus first-class for sketching and annotation: pressure-sensitive strokes on the canvas, palm rejection, barrel-button eraser, hover previews, and pen-based markup on screenshots and documents. Pen input flows through the shared abstraction so the canvas, screenshot annotation and any future whiteboard get identical behaviour.
SCOPE: In:

* `packages/input/src/pen/`: `usePenStroke(surface, { smoothing, pressureCurve, minWidth, maxWidth })` producing stroke points `{ x, y, pressure, tiltX, tiltY, t }`, with `perfect-freehand` 1.x for outline generation and a Catmull-Rom smoother; `usePenHover` for hover cursor previews; `usePenButtons` mapping barrel button → eraser, secondary → lasso.
* Palm rejection and pen priority (from `input/input-abstraction`): while a pen is down, touch presses on the same surface are ignored; two-finger touch still pans/zooms.
* Canvas integration: a tldraw (or React Flow, per `collab/collab-research`) tool `PaperOSPenTool` in `collab/canvas-view` that uses `usePenStroke`, stores strokes as a Yjs-synced shape (`type: 'ink'`, points compressed with delta encoding), and renders via SVG path at up to 240 Hz input sampling using `getCoalescedEvents`.
* Annotation layer `InkAnnotationLayer` in `p
SPEC(first 1200): * Pressure curve `f(p) = minWidth + (maxWidth − minWidth) × curve(p)`; presets as functions; tilt modulates width by up to 30% when `tiltShading` is on.
* Sampling: use `PointerEvent.getCoalescedEvents()` where available, `getPredictedEvents()` for the live preview segment only (never stored).
* Stroke storage: `{ id, tool, color token, width, points: Int16Array deltas (0.1 px units), pressures: Uint8Array }`; a 5,000-point stroke stays under 20 KB; strokes over 20,000 points are split.
* Rendering: live stroke on a dedicated `<canvas>` layer for latency; committed strokes as SVG paths; target under 16 ms from pen sample to paint (measured with `PerformanceObserver` in the Playwright test using CDP-synthesised pen events).
* Eraser: barrel button or tool switch; whole-stroke erase by default, segment erase with `alt`.
* Undo/redo through `y-undo-manager` scoped to the local user (`realtime/collab-text` pattern) and registry commands `edit.undo/redo`.
* Accessibility: ink is decorative unless the author adds an alt text via the annotation panel; the annotation list is navigable by keyboard and exposes each stroke group as a list item with its alt text.
DOD:
* Drawing with a pen on a Windows Surface or Android tablet (Tauri build) shows pressure-varying strokes, palm rejection and eraser; video attached.
* Playwright tests using CDP `Input.dispatchMouseEvent` with `pointerType: 'pen'` and pressure values assert width variation and latency budget; screenshots at 768 and 1280 px (tablet widths).
* Vitest tests for pressure curves, delta encoding round-trip, stroke splitting and palm-rejection timing.
* Annotation layer used by `collab/screenshot-annotations` demo to mark up a screenshot and export PNG+SVG.
* Two browsers see each other's strokes live via Yjs within 100 ms on localhost.
* Docs `docs/platform/input/pen.md`; changelog entry; Linear comment with video and demo link.
EDGE:
* Pen leaves the digitiser mid-stroke (`pointerleave` without `up`): commit the stroke on `pointercancel` or 500 ms timeout.
* Pressure always 0.5 (unsupported hardware): detect constant pressure over 20 samples and switch to fixed width.
* Mouse users on the ink tool: constant pressure, `shift` for straight lines so the tool is not pen-only.
* 100k-point document (a long session): render committed strokes into a cached bitmap tile layer; SVG only for the last 200 strokes.
* Left-handed users: hover preview offset mirrors; setting persists per user.
* Zoomed canvas at 8×: widths scale with zoom; minimum on-screen width 1 px.
DEPS: * `input/input-abstraction` (pen fields, palm rule), `collab/canvas-view` (tool host), `realtime/yjs-server` (stroke sync), `collab/screenshot-annotations` (consumer), `input/touch-gestures` (two-finger pan while drawing), `design-system/tokens` (ink colours).


## PAP-158 [P2 Build M prio3 Backlog] Add gamepad and TV-remote navigation for kiosk and TV modes with spatial focus
key=input/gamepad milestone=Voice and accessibility certification agent=Builder: Nova, with Iris (Motion and Input Stylist) on the T
blockedBy=['PAP-152'] blocks=[]
GOAL: Make the 10-foot UI work: a PaperOS app running in kiosk or TV mode (from `app-shell/linux-kiosk`) can be driven entirely with a gamepad, TV remote or the arrow keys of a keyboard, using spatial focus that moves to the geometrically nearest element instead of DOM order. This also gives motor-impaired users who rely on switch or D-pad devices a working path through every page.
SCOPE: In:

* `packages/input/src/spatial/`: `SpatialNavigationProvider` implementing 2D focus search over registered focusable elements (weighted by distance and axis alignment, with "sticky" columns), `useFocusable({ group, onEnter, onLongEnter })`, `FocusGroup` (grid/list/menu semantics, memory of last focused child), `enableSpatialNavigation({ trigger: 'gamepad'|'always' })`.
* Gamepad layer: polling from `input/input-abstraction` (`gamepad` events, standard mapping) mapped to actions: D-pad/left stick → move, `A` → activate, `B` → back, `X` → context menu, `Y` → command palette, bumpers → region cycling (`F6` equivalent), triggers → page scroll, `Start` → help overlay; stick repeat with acceleration; deadzone 0.25.
* TV remote and keyboard: arrow keys plus `Enter`/`Escape`/`Backspace` map to the same actions when spatial mode is active; `input/command-registry` commands `spatial.move.*`, `
SPEC(first 1200): * Search algorithm: candidates are visible focusables in the current group, then parent groups; score = Euclidean distance to the exit edge centre + 3× off-axis offset; ties break by DOM order; `data-spatial-priority` can pin an element.
* Groups expose `enterFrom(direction)` returning the child to focus (last-focused, first, or nearest), and `onExit(direction)` may block (e.g., a horizontal carousel swallows left/right at its ends).
* Scroll handling: focusing an element scrolls it into view with a 10% margin using `scrollIntoView({ block: 'nearest' })`; virtualised lists expose `scrollToIndex` for off-screen movement.
* Activation dispatches a real `click` on the focused element so existing components need no changes; long-press `A` (600 ms) fires `contextmenu`.
* Overlays: a `Dialog` or `BottomSheet` becomes the active root group; `B` closes it (through the component's `onClose`).
* Detection: spatial mode enables automatically on the first gamepad input or when `?input=tv`/kiosk config is set; a small controller glyph appears in the status bar; mouse movement disables cursor lock but keeps spatial mode until a preference changes it.
* Help overlay lists controller mappings with
DOD:
* Kiosk build (`app-shell/linux-kiosk`) drives the template app end to end (sign in with PIN, navigate, open record, edit a select field, run a palette command) using an Xbox controller; video attached.
* Playwright tests with a mocked `navigator.getGamepads` at 1280 and 1920 px asserting focus paths through a grid, a sidebar and a dialog; screenshots of the TV theme focus ring.
* Vitest tests for the scoring function (deterministic fixtures), group entry memory and deadzone/repeat timing.
* `SpatialKeyboard` enters text into an input and a Tiptap comment field.
* Docs `docs/platform/input/spatial-and-gamepad.md` with the mapping table and a guide to grouping pages.
* Changelog entry and Linear comment with video and demo links.
EDGE:
* Two controllers connected: the last one used is active; input from the other is ignored until it moves.
* Focusable element appears under the current focus after a live update: no jump; the next move re-evaluates.
* Grid with ragged rows: moving down from the last cell of a longer row lands on the nearest cell, not nothing.
* Disconnected controller mid-interaction: spatial mode stays, keyboard arrows keep working; a toast notes the disconnect.
* Elements with `visibility: hidden` or inside `inert` containers are excluded from search.
* Hold-to-repeat on a stick while a dialog opens: repeat cancels to avoid skipping through the dialog.
DEPS: * `input/focus-management` (focus ring, regions, announcer), `input/input-abstraction` (gamepad events, cursor pointer), `input/command-registry`, `app-shell/linux-kiosk` and `app-shell/device-matrix-research` (TV breakpoint), `design-system/theming` (TV theme), `design-system/primitives` (Dialog `onClose`).


## PAP-159 [P2 Build M prio2 Backlog] Integrate voice commands and dictation (Web Speech with Whisper fallback) routed through the command registry
key=input/voice milestone=Voice and accessibility certification agent=Builder: Nova, with Forge (Ops Runner) deploying the Whisper
blockedBy=['PAP-151'] blocks=[]
GOAL: Let people talk to the app: say a command ("open inbox", "assign to Bo", "mark done") and it runs through the command registry; dictate into any text field with punctuation; and do it privately, using the browser's Web Speech API when available and a self-hosted Whisper endpoint when it is not (Linux WebKitGTK, Firefox, kiosk). Voice is another input to the same command surface, not a separate assistant.
SCOPE: In:

* `packages/input/src/voice/`: `VoiceProvider` with a `SpeechBackend` interface (`start/stop/onPartial/onFinal/onError`) and two implementations: `WebSpeechBackend` (`SpeechRecognition` with `continuous`, `interimResults`) and `WhisperBackend` streaming 16 kHz PCM chunks over WebSocket to `apps/voice-server/` (Python `faster-whisper` 1.x, `small.en` default, running on the VPS behind Caddy at `wss://voice.<domain>`, auth via Better Auth session).
* Intent matching over the command manifest (`input/command-registry`): normalise transcript → match against command titles, keywords and user keymap aliases with a fuzzy scorer; disambiguate with a spoken/visible chooser when top two scores are close; argument extraction for simple slots (person names via the mention source, status values, numbers, dates via `chrono-node` 2.x).
* Dictation mode: inserts text at the caret in any `<input>`, 
SPEC(first 1200): * Backend selection: `WebSpeech` if `window.SpeechRecognition || webkitSpeechRecognition` exists and the tenant allows cloud recognition (Chrome sends audio to Google); otherwise or if the tenant sets `voice.backend: 'self-hosted'`, use Whisper. Setting lives in tenant settings (`data-layer/core-entities`).
* Command matching: score = 0.6 × token similarity (Jaro-Winkler on normalised title/keywords) + 0.4 × phonetic match (`double-metaphone`); threshold 0.75; exactly one candidate above threshold runs immediately; several within 0.05 open the chooser; none → toast "Did not catch a command" with the transcript.
* Registry contract: commands opt in with `voice: { phrases?: string[], confirm?: boolean }`; destructive commands (`confirm: true`) require "yes" or a click.
* Whisper protocol: `{ type: 'start', lang, sampleRate }`, binary PCM frames every 250 ms, `{ type: 'partial'|'final', text, ts }`; server VAD (Silero) segments utterances; end-to-end partial latency under 800 ms on the VPS CPU with `small.en`.
* Audio capture via `AudioWorklet` at 16 kHz mono; Tauri mobile needs microphone entitlements added in `app-shell/tauri-mobile` capabilities.
* Accessibility: listening state an
DOD:
* "Open inbox", "create record", "assign to Bo" and "mark done" run correctly on the sample pages in Chrome (Web Speech) and Firefox (Whisper); demo video attached.
* Dictation into a form field and a Tiptap comment with spoken punctuation works; Playwright tests inject transcripts through a `MockBackend` at 375 and 1280 px, screenshots of indicator and chooser attached.
* Vitest tests for normalisation, scoring thresholds, slot extraction and punctuation handling.
* `apps/voice-server` deployed with `/healthz`, metrics, and a load check of 20 concurrent streams.
* Security review confirms no audio persistence and correct auth on the WebSocket.
* Docs `docs/platform/input/voice.md` (backend matrix, privacy statement text); changelog; Linear comment with links.
EDGE:
* Noisy environment yields garbage partials: only finals trigger commands; partials are display-only.
* Homophones ("Bo" vs "Beau" among members): chooser lists both with avatars.
* Microphone permission denied: button shows a disabled state with instructions; never re-prompt in a loop.
* Network drops mid-dictation with Whisper: buffered audio up to 10 s is sent on reconnect; beyond that, the user is told what was lost.
* Web Speech stops after \~60 s silence in Chrome: auto-restart while push-to-talk is held.
* Command matched while a Dialog is open but the command is out of scope: refused with "Not available here".
DEPS: * `input/command-registry` (manifest, execution, `voice` contract), `realtime/collab-text` (dictation target), `identity/better-auth` (WebSocket auth), `app-shell/tauri-mobile` (mic entitlements), `data-layer/core-entities` (tenant settings), `input/keymaps` (aliases). Deployed by Forge patterns from `realtime/yjs-server`.


## PAP-160 [P2 Docs S prio3 Backlog] Publish an accessibility statement and conformance report template per app
key=input/a11y-statement milestone=Voice and accessibility certification agent=Builder: Quill (Changelog Scribe sub-agent for the templates
blockedBy=['PAP-156'] blocks=[]
GOAL: Give every PaperOS app compliance evidence out of the box: a public accessibility statement page and a conformance report (WCAG 2.2 AA, in VPAT 2.5 / ACR structure) generated from real test results rather than written by hand, updated on every release so it never drifts from the product. Customers asking "is this accessible?" get a link, and Justin gets a one-page view of remaining gaps.
SCOPE: In:

* Templates in `packages/spec/templates/a11y/`: `statement.mdx` (commitment, conformance status, known limitations, feedback channel, compatibility list, assessment method, date) and `acr.mdx` (WCAG 2.2 A/AA criteria table with Supports / Partially Supports / Does Not Support / Not Applicable and remarks), with placeholders filled from app.spec.yaml (`spec-builder/app-level-spec`: name, contact, audiences) and from test data.
* Generator `pnpm a11y:report` in `packages/input/scripts/` that reads: axe results from `design-system/a11y-audit` and `quality/playwright-matrix`, screen-reader matrix from `input/screen-reader`, focus-order audit from `input/focus-management`, contrast results from `quality/screenshot-annotation`, and open Linear issues labelled `a11y` (via `pm-linear/linear-sync` read API); it maps each data source to WCAG success criteria through `criteria-map.json` and wr
SPEC(first 1200): * `criteria-map.json` entries: `{ criterion: '2.1.1', sources: [{ type: 'axe', rules: ['keyboard'] }, { type: 'sr-matrix', flows: ['*'] }, { type: 'manual', note }], defaultStatus: 'Not Evaluated' }`; status resolution: any failing automated rule → Partially Supports (or Does Not Support if all fail), all pass and manual confirmed → Supports, no data → Not Evaluated (shown, never hidden).
* Every non-Supports row must link the tracking Linear issue; the generator fails if a failing criterion has no issue, forcing one to be filed.
* Known limitations section is generated from open `a11y` issues with customer-facing summaries (field `publicSummary` in the issue contract from `pm-linear/issue-contract`).
* Statement page itself must pass axe, have a plain-language reading level (Flesch-Kincaid grade ≤ 9, checked with `text-readability`), and be translatable (strings in MDX frontmatter).
* Versioning: report files carry `generatedAt`, app version from `forge/release-tags`, and a hash; the page shows "Last reviewed" and "Next review by" (90 days).
* A template app with no test data renders a statement marked "Not yet assessed" instead of failing the build.
DOD:
* `pnpm a11y:report` runs in CI on the template app and commits `docs/a11y/*`; all 55 WCAG 2.2 A/AA criteria appear with a status and source.
* `/accessibility` renders in the customer portal at 320, 768 and 1280 px; screenshots attached; axe clean; readability check passes.
* ACR PDF export attached to the PR.
* Release-train integration shown in one RC digest with a conformance delta section.
* Feedback form creates a labelled Linear issue (test issue linked, then closed).
* Docs `docs/platform/a11y/statement-and-acr.md` explaining how to keep the map current; changelog entry; Linear comment with the page link, routed to Needs Justin for wording approval.
EDGE:
* A criterion covered only by manual testing with no record yet: shown as Not Evaluated with an owner, not silently Supports.
* Tenant white-labels the app (`design-system/theming`): statement uses the tenant's name and contact but the same test data; theming contrast results are per-tenant, so contrast criteria are evaluated per theme and the worst status is shown.
* Test suite skipped in a hotfix release: the generator reuses the last full results and marks the report "based on version X".
* Linear API unavailable during generation: fall back to the last cached issue list with a warning banner in the report.
* Criteria not applicable (no audio/video content): `Not Applicable` requires a justification string in the map.
* Very long known-limitations list (over 20): grouped by area with a collapsed view.
DEPS: * `input/screen-reader` (matrix), `design-system/a11y-audit`, `quality/playwright-matrix`, `quality/screenshot-annotation`, `input/focus-management` (focus audit), `spec-builder/app-level-spec`, `collab/docs-engine`, `quality/release-train`, `quality/review-report`, `pm-linear/linear-sync`, `pm-linear/issue-contract`, `forge/release-tags`.
