R = {}

R["PAP-150"] = {
"Goal": "Define one input model every PaperOS component uses so mouse, touch, pen and gamepad behave consistently without per-component device checks. Output: a spec plus a small typed core in `packages/input` that gestures (PAP-154), drag-and-drop (PAP-155), pen (PAP-157) and gamepad (PAP-158) build on, fixing the vocabulary once.",
"Scope": """In:

* Spec `docs/platform/input/abstraction.md`: event vocabulary, coordinate spaces, capture semantics, capability detection, mapping to Pointer Events, Touch fallback, Gamepad API and keyboard.
* `packages/input/src/core/`: `InputEvent` union (`press | move | release | cancel | wheel | key | gamepad`), `Pointer`, `Modifiers`, `usePointerSurface(ref, handlers, { capture, passive })` translating `pointerdown/move/up/cancel` and `lostpointercapture` with capture handled centrally.
* `useInputCapabilities()` → `{ coarsePointer, finePointer, hover, touchPoints, penSeen, gamepadConnected, keyboardSeen }` from media queries plus observed events, mirrored as `data-input-*` on `<html>`.
* Thresholds table as exported constants: tap slop 8 px fine / 12 px coarse, long-press 500 ms, double-press 300 ms, drag start 4 px / 10 px.
* Library decision: `@use-gesture/react` vs standalone (default: thin standalone layer over Pointer Events; `@use-gesture` only for pinch and wheel maths in PAP-154).

Out: recognisers, drag-and-drop, spatial focus, voice, the command registry.""",
"Spec": """* Every pointer carries `client`, `page` and `surface` coordinates in CSS pixels.
* `press` calls `setPointerCapture`; `release` or `cancel` fires exactly once per pointer id; `cancel` on `pointercancel`, window blur and hidden tab.
* Keyboard: `key` normalised to `Key { code, key, modifiers, repeat }` and portable chord string `mod+shift+k` (`mod` = Cmd on macOS, Ctrl elsewhere).
* Gamepad: `requestAnimationFrame` polling emits `gamepad` events (standard mapping) and a synthetic `gamepad-cursor` pointer when PAP-158 enables cursor mode.
* Pen: `pressure`, `tiltX/Y`, `twist`, barrel button as `buttons` bit 2; while a pen is active, touch presses on the same surface are ignored for 300 ms.
* Biome rule `no-raw-touch-handlers` flags `onTouchStart`/`onMouseDown` in `packages/ui` and `packages/views`.""",
"Interface contract": """Exposes (package `@paperos/input`): types `InputEvent`, `Pointer { id, type: 'mouse'|'touch'|'pen'|'gamepad-cursor', client, page, surface, pressure, tiltX, tiltY, twist, buttons, isPrimary }`, `Modifiers`, `Key`, `Chord` (string) with `parseChord()`, `formatChord(platform)`, `matchChord(event, chord)` used verbatim by PAP-151 and PAP-153; `usePointerSurface`, `useInputCapabilities`, `useLastInputModality()` (keyboard vs pointer, used by PAP-152 focus rings); constants `THRESHOLDS`; CSS hooks `[data-input-coarse]`, `[data-input-hover]`; lint rule. Consumes: nothing at runtime; `breakpoints.json` device classes from PAP-14 for the capability playground.""",
"Definition of done": """* Spec merged and linked from PAP-76 guidelines.
* Storybook "Input Playground" showing active pointers, pressure and capabilities at 375 (touch emulation) and 1280; screenshots attached.
* Biome rule enabled with zero violations; `data-input-*` used by the Button primitive for coarse hit targets (PAP-236).
* Developer changelog entry; Linear comment with the playground link.""",
"Test plan": """* Vitest with synthetic `PointerEvent`s: capture set on press, exactly one release or cancel per pointer, cancel on blur and hidden tab, slop thresholds by pointer type, palm-rejection window, pressure clamp to [0, 1], hover (`buttons === 0`) distinguished from drag.
* Chord tests: `parseChord('mod+shift+k')` on macOS and Linux `navigator.platform` mocks, non-Latin layout matching by `code`, sequence tokens.
* Gamepad: mocked `navigator.getGamepads` yields normalised sticks with deadzone and standard buttons.
* Visual: playground story captured at 375 and 1280 in both themes; axe on the story.
* Lint: fixture file with `onTouchStart` fails `biome check`.""",
"Demo": "Open Storybook Input Playground at 1280, move the mouse and read the pointer panel; switch to iPhone emulation and tap with two fingers to see two pointers and `coarsePointer: true`; press `mod+shift+k` and see the normalised chord. Under two minutes.",
"Edge cases": """* Touch-then-mouse devices: capabilities update live.
* `pointercancel` on scroll: treated as release without action; `touch-action` documented.
* Long-press context menu: suppressed only when a handler claims it.
* iOS Safari missing `pointerrawupdate`: polling covers it.""",
"Dependencies": "None hard (Ready). Informs PAP-67 hit targets. Blocks PAP-151, PAP-154, PAP-155, PAP-157, PAP-158; consumed by PAP-152, PAP-132.",
"Agent": "Builder: Nova (Product Systems Engineer, owner of multi-input). Reviewer: Iris (Motion and Input Stylist) for the component contract; Sentinel (Code Reviewer).",
"Size": "S: a spec and a thin core; the value is deciding the vocabulary early.",
}

R["PAP-151"] = {
"Goal": "Umbrella: make everything in a PaperOS app a command. One registry knows every action, its label, shortcut, scope and permission, and powers shortcuts, the palette, menus, toolbars, voice and gamepad; agents invoke the same commands through an audited endpoint. Planned as three work packages; the umbrella owns the manifest, docs and integration test.",
"Scope": """Work packages (build in order; each becomes a child issue once the Linear issue limit is lifted, see the pinned comment):

1. **Command registry core, scoping and chord matcher** — `defineCommand`, `CommandRegistry`, `CommandScopeProvider` scope stack (global → page → component), chord and sequence matching on PAP-150's `Chord`, `when` guards, conflict warnings, `pnpm commands:manifest` with duplicate-ID failure.
2. **Command palette and help sheet UI** — `CommandPalette` on PAP-70 `CommandBar` with `fuse.js` scoring, grouped results, virtualised list (max 50), argument prompts from `argsSchema`, recents; `?` help sheet; `CommandButton`.
3. **Agent execution endpoint, telemetry and default commands** — oRPC `commands.execute` for `commands:execute` scope limited to `agentCallable` commands with `can()` and audit rows; `command.executed` telemetry; defaults `nav.*`, `ui.toggleSidebar|toggleInspector|toggleTheme`, `edit.undo|redo`, `help.shortcuts`, `search.open`.

Parent owns `docs/platform/input/commands.md` generated from the manifest, Storybook stories, integration test.

Out: keymaps (PAP-153), voice (PAP-159), gamepad mapping (PAP-158), menu rendering.""",
"Spec": """* IDs dot-namespaced (`record.duplicate`); innermost scope wins; page specs declare `commands:` (PAP-114) registered by PAP-120.
* `when(ctx)` receives `{ route, selection, focusedScope, permissions, capabilities, isEditing }`; hidden commands never appear.
* Palette `role="combobox"` with `aria-activedescendant`; results update under 16 ms for 2,000 commands.
* Browser-reserved chords warned and never claimed; `allowInInput` gates firing inside editable text.""",
"Interface contract": """Exposes (owned by the work packages): `defineCommand({ id, title, description?, icon?, keywords?, scope, shortcut?, when?, permission?, argsSchema?, agentCallable?, voice?, run })`, `CommandRegistry { register, unregister, execute(id, args, source), list(ctx), setBindingsResolver(fn) }` (resolver hook for PAP-153), hooks `useCommand`, `useCommands`, `useShortcut`, components `CommandPalette`, `CommandButton`, `ShortcutHint`, `commands.manifest.json` `{ commands: [{ id, title, scope, shortcut, keywords, permission, agentCallable, page? }] }` consumed by PAP-153, PAP-159 and docs; oRPC `commands.execute({ id, args }) -> { ok, result | error }`; telemetry event `command.executed { id, source }`. Consumes: `Chord` utilities and modality (PAP-150), `CommandBar`, `Dialog`, `Combobox` (PAP-70, PAP-237, PAP-238), `can()` (PAP-227), oRPC and audit (PAP-267, PAP-38), spec `commands:` section (PAP-114).""",
"Definition of done": """* All three work packages merged; palette opens with `mod+k` on every page and lists page-scoped commands from a sample spec.
* Manifest generated in CI and committed; docs page lists every command from it.
* Storybook palette stories (empty, results, argument prompt) in three themes, axe clean; changelog; Linear comment with demo link.""",
"Test plan": """* Integration (parent): Playwright at 375 (full-screen sheet) and 1280: `mod+k`, type "inbox", `Enter` navigates; `g i` sequence navigates; inside a Tiptap field `mod+b` bolds instead of firing a global command; a customer session does not see a staff-only command; agent key executes an `agentCallable` command and is denied on a non-callable one with an audit row.
* Unit tests per work package (chord parsing, scope precedence, `when` guards, duplicate IDs, permission hiding, scorer ranking, endpoint allow/deny).
* Performance: bench with 2,000 registered commands, palette filter under 16 ms.
* Visual: Gate 3 captures of palette and help sheet at 375 and 1280, three themes.""",
"Demo": "Press `mod+k`, type “theme”, run “Toggle theme”; press `?` to read the shortcuts sheet; press `g i` to jump to the inbox; from a terminal call `commands.execute` with an agent key and watch the audit row appear. Under two minutes.",
"Edge cases": """* Same chord in sibling scopes: focused one wins.
* Palette over an open Dialog: stacks and restores focus.
* Async `run` throws: palette closes, toast, registry healthy.
* Non-Latin layouts: letters by `code`, symbols by `key`.""",
"Dependencies": "PAP-67, PAP-150 (hard, encoded). Soft: PAP-70, PAP-59, PAP-35, PAP-114. Blocks PAP-153, PAP-159, PAP-155; consumed by PAP-142, PAP-138, PAP-152, PAP-158, PAP-149.",
"Agent": "Builder: Nova. Reviewer: Sentinel (Code Reviewer, Security Auditor for the endpoint); Iris reviews palette visuals.",
"Size": "L, planned as three M/S work packages (child issues pending the issue limit).",
}

R["PAP-152"] = {
"Goal": "Guarantee keyboard users never lose their place: predictable focus order through nav, sidebar, main and inspector, roving tabindex in composite widgets, skip links, and focus restoration after dialogs, route changes and live updates. Screen-reader conformance (PAP-156), spatial navigation (PAP-158) and drag-and-drop (PAP-155) rely on it.",
"Scope": """In:

* `packages/input/src/focus/`: `FocusRegion` (landmark region with entry point and `F6` cycling), `useRovingTabIndex(items, { orientation, loop, typeahead })`, `FocusScope` (trap and restore on the PAP-67 focus-scope primitive), `useFocusRestore(key)`, `FocusRing` styles from PAP-66, `useGridFocus` for PAP-165, shared `LiveAnnouncer`.
* Skip links rendered by `AppFrame` (PAP-70); `F6`/`shift+F6` as commands `focus.nextRegion|prevRegion` (PAP-151).
* Route-change policy: focus the `h1` or `[data-focus-entry]`, announce the title; back navigation restores by `data-focus-key`.
* Live-update policy: remote changes never steal focus; removed element → nearest sibling → region entry.
* Audit `pnpm a11y:focus-order <url>` writing JSON and a screenshot strip for PAP-82.

Out: real AT testing (PAP-156), 2D spatial focus (PAP-158), component keyboard behaviour in primitives.""",
"Spec": """* Roving: one item `tabindex=0`; arrows per orientation, `Home/End`, 500 ms typeahead, virtualised lists via `getItemElement(index)`.
* `FocusScope { trap, restoreFocus, autoFocus: 'first'|'container'|selector }`; nested scopes form a stack; top scope owns `Tab`.
* Ring only on `:focus-visible`; programmatic focus shows the ring after keyboard modality (PAP-150).
* Regions registered by `AppFrame` slots `nav`, `sidebar`, `main`, `inspector`, `commandbar`, `statusbar`; detached windows (PAP-262) form their own region set.
* Grid: `role="grid"`, arrows across cells, `Enter` edits, `Escape` cancels.""",
"Interface contract": """Exposes: `FocusRegion`, `useFocusRegions()`, `useRovingTabIndex`, `FocusScope`, `useFocusRestore`, `useGridFocus({ rows, cols, getCell })`, `LiveAnnouncer` with `announce(text, { politeness, dedupeKey })` and `useAnnounce()` (single shared instance; PAP-155, PAP-141, PAP-144 and PAP-158 must use it), DOM contracts `data-focus-entry`, `data-focus-key`, `data-focus-region`, commands `focus.*`, CLI `a11y:focus-order` output `{ url, width, order: [{ selector, label, region }] }`. Consumes: `AppFrame` slot names (PAP-70), focus-scope primitive and `Dialog` (PAP-236, PAP-237), ring tokens (PAP-66), `defineCommand` (PAP-151), `useLastInputModality` (PAP-150), `WindowManager` window ids (PAP-262).""",
"Definition of done": """* Skip links, `F6` cycling and route-change focus work in the template app; focus-order strips at 375 and 1280 attached.
* `useGridFocus` demo keeps focus in a 1,000-row virtual grid across scrolling and remote row insertion.
* `docs/platform/input/focus.md` with the policy table; changelog; Linear comment with demo link and strips.""",
"Test plan": """* Vitest (jsdom): roving orientation, loop, typeahead buffer, disabled skipping, virtualised `getItemElement`; scope stack push/pop and restore target fallback chain; `LiveAnnouncer` dedupe within 10 s.
* Playwright: `Tab` sequences with `document.activeElement` assertions through nav → main → inspector at 1280 and nav → main → drawer at 375; `F6` cycles; route change focuses `h1` and the live region text equals the title; remote row deletion (via `/__test`, PAP-240) moves focus to the next row with the announcement; dialog close restores to the trigger or falls back to region entry.
* axe: `focus-order-semantics`, `skip-link`, `tabindex` on all Storybook stories.
* Visual: focus-ring states captured in three themes (Gate 3).""",
"Demo": "Load the template app, press `Tab` once and use “Skip to main content”, press `F6` three times to cycle regions, open a record dialog and `Escape` back to the same row, navigate to another page and hear the title announced (screen reader or the live-region devtools panel). Under two minutes.",
"Edge cases": """* Focused row deleted mid-typeahead: next row, announced.
* Menu trigger unmounted: fall back to region entry.
* Detached inspector: `F6` cycles within that window only.
* iframes: single stop, no trap.
* Nested autofocus: only the top scope wins; dev warning.""",
"Dependencies": "PAP-70 (hard, encoded). Soft: PAP-67, PAP-66, PAP-151, PAP-150, PAP-262, PAP-240. Blocks PAP-156, PAP-158, PAP-155; consumed by PAP-165, PAP-142.",
"Agent": "Builder: Iris (Motion and Input Stylist) for regions and ring styling with Nova for hooks. Reviewer: Sentinel (Code Reviewer, Visual Inspector).",
"Size": "M: many small behaviours that must agree; testing is the bulk.",
}

R["PAP-153"] = {
"Goal": "Let power users bring their habits: pick a keymap preset (Default, Vim-style, Linear-like), rebind any command, and have bindings follow them to every device and window. Keymaps layer over the command registry; conflicts are detected before they bite.",
"Scope": """In:

* `packages/input/src/keymaps/`: `Keymap = { id, name, base?, bindings: Record<commandId, Chord[] | null> }`; resolver merging preset → user overrides → page-scope overrides, plugged into PAP-151's `setBindingsResolver`.
* Presets: `default`, `vim` (`j/k`, `g g`/`G`, `/`, `:`, `h/l`, modal normal/insert layer), `linear` (`c`, `e`, `x`, `s`, `a`, `g i`, `g b`) with a comparison table.
* Settings `/settings/keyboard`: preset picker, searchable command list from `commands.manifest.json`, click-to-record binding with inline conflicts, two chords per command, reset, import and export JSON.
* Persistence: `user_preferences.keymap jsonb` (PAP-33 user extension), synced through PAP-143 and across windows through PAP-145; `localStorage` cache for first paint.
* Conflict detection: overlapping scopes, browser-reserved chords, `when`-guard explanations.

Out: per-tenant keymaps, macros, mouse buttons, Tiptap internals.""",
"Spec": """* Resolver memoised per scope stack; rebinding applies within one frame; help sheet and palette hints read effective chords from the resolver.
* Vim layer only where `role` is list, grid or tree; `Escape` returns to normal without blurring; mode shown in the status bar.
* Recording ignores lone modifiers; sequences by pausing 1 s.
* Import validated by Zod; unknown command IDs kept and greyed.""",
"Interface contract": """Exposes: `Keymap` Zod schema and JSON export format, `resolveBindings(scopeStack) -> Map<commandId, Chord[]>`, `useKeymap()`, `useEffectiveChord(commandId)` (used by PAP-151 hints and PAP-159 aliases), preset files `presets/*.json`, `KeymapSettingsPage`, window message type `keymap.changed` (PAP-145), oRPC `preferences.keymap.get|set`. Consumes: `setBindingsResolver`, `commands.manifest.json` (PAP-151), `parseChord`/`formatChord` (PAP-150), `user_preferences` column (PAP-33), shape on `user_preferences` (PAP-143), `WindowBus` (PAP-145), primitives (PAP-67).""",
"Definition of done": """* Linear preset makes `c` open create and `g i` navigate on the sample list page; preference persists across reload and reaches a second browser within 2 s.
* Storybook settings stories (empty search, conflict, recording) in three themes, axe clean; screenshots at 768 and 1440.
* `docs/platform/input/keymaps.md` with the comparison table; changelog; Linear comment with demo link.""",
"Test plan": """* Vitest: merge precedence (preset < user < page), conflict detection across overlapping scopes, reserved-chord block, import validation with unknown IDs, vim mode transitions, `palette.open` replacement rule.
* Integration: `preferences.keymap.set` through `callAs` persists and RLS scopes to the user.
* Playwright: switch presets and run key flows for all three at 768 and 1440; record a new chord for `record.duplicate` and see the conflict warning; second context receives the change within 2 s.
* Visual: Gate 3 captures of the settings page states at 768 and 1440, three themes.""",
"Demo": "Open `/settings/keyboard`, choose Linear, go to a list and press `c`, then `g i`; return, search “duplicate”, click record, press `mod+d`, see the conflict note, save; reload and confirm it stuck. Under two minutes.",
"Edge cases": """* Rebinding `mod+k` requires a replacement for `palette.open`.
* Key missing on the layout (`§`): warning, still stored.
* Preset update conflicts with a user override: override wins.
* Two windows rebind at once: last write wins, both re-resolve.""",
"Dependencies": "PAP-151 (hard, encoded). Soft: PAP-150, PAP-33, PAP-143, PAP-145, PAP-67. Consumed by PAP-159, PAP-158.",
"Agent": "Builder: Nova. Reviewer: Sentinel (Code Reviewer, Edge Case Hunter for conflict rules); Iris reviews the settings UI.",
"Size": "M: resolver is small; presets and settings UI carry the bulk.",
}

R["PAP-154"] = {
"Goal": "Make PaperOS feel native on phones and tablets: swipe to reveal row actions, pinch to zoom, long-press for context menus, pull to refresh and edge swipe, with haptics on Tauri mobile. Gestures are recognised through the shared abstraction so they compose with mouse and pen.",
"Scope": """In:

* `packages/input/src/gestures/`: `useTap`, `useLongPress`, `useSwipe`, `usePinch`, `usePan` (momentum, rubber-band), `usePullToRefresh`, `useEdgeSwipe`, all on `usePointerSurface` (PAP-150); `@use-gesture/react` only for pinch and wheel maths if the ADR chose it.
* `GestureArena` arbitrating ownership (scroll vs swipe vs pan) with the PAP-150 thresholds.
* `packages/ui`: `SwipeableRow`, `PinchZoomView`, `PullToRefresh`, `BottomSheet` (snap points, focus trap from PAP-152, falls back to `Dialog` on desktop).
* `haptic('selection'|'impact-light'|'impact-medium'|'success'|'warning'|'error')` mapped to `@tauri-apps/plugin-haptics` (PAP-260), `navigator.vibrate`, else no-op; respects preference and reduced motion.
* Touch-target audit: interactive elements at least 44 × 44 CSS px under `pointer: coarse`.

Out: pen behaviour (PAP-157), reordering (PAP-155), OS webview navigation gestures.""",
"Spec": """* Recognisers return spreadable handlers and state; every gesture emits `start/move/end/cancel` with `{ pointers, delta, velocity, scale, center }`.
* `touch-action` per surface (`pan-y` for lists, `none` for canvases); arena cancels when the browser scrolls.
* `SwipeableRow`: reveal at 30 percent, commit at 60 percent or velocity over 0.5 px/ms; actions also in the overflow `Menu`; announces "Actions revealed".
* `PinchZoomView`: scale 0.5 to 8, double-tap toggles 1× and 2×, `ctrl`+wheel on desktop, single transform layer; emits `viewport` for PAP-132 and PAP-141.
* Haptics only on commits, at most 10 per second.""",
"Interface contract": """Exposes: recogniser hooks above with `GestureState` type, `GestureArena` and `useGestureArena()`, components above (`BottomSheet` `snapPoints`, `onDismiss`; `SwipeableRow` `leading`, `trailing`, `onCommit`), `haptic()` and `HapticKind`, `viewport` event `{ scale, x, y }`, Playwright fixture `touchTargets(page)` for PAP-82. Consumes: `usePointerSurface`, `THRESHOLDS`, capabilities (PAP-150), haptics plugin and safe-area insets (PAP-259, PAP-260), `Menu` and `Dialog` (PAP-237), focus trap (PAP-152), `LiveAnnouncer` (PAP-152).""",
"Definition of done": """* Tauri Android and iOS builds demonstrate swipe, pinch, long-press and pull-to-refresh with haptics; device or emulator video attached.
* Touch-target audit passes on all `packages/ui` stories.
* `docs/platform/input/gestures.md` with the arbitration table; changelog; Linear comment with video and Storybook links.""",
"Test plan": """* Vitest: arena arbitration with synthetic pointer sequences (vertical then horizontal locks direction, third finger ignored, nested pull-to-refresh claimed only at outer scroll top), thresholds and velocity maths, haptic rate limit and no-op path.
* Playwright with `hasTouch: true` at 320, 375 and 768: `page.touchscreen` swipe reveals and commits; CDP `Input.dispatchTouchEvent` two-finger pinch scales the view; long-press opens the context menu and suppresses the native one; bottom sheet snaps and dismisses; screenshots attached.
* Storybook: stories under `iphone14` and `ipad` viewports with axe; reduced-motion variant.
* Visual: Gate 3 captures of the four components at 320, 375 and 768, both themes.""",
"Demo": "On the Android emulator build, swipe a row left to reveal Archive and feel the tick, long-press a card for its menu, pinch the canvas, pull the list down to refresh; on desktop the same row exposes the actions in its overflow menu. Under two minutes.",
"Edge cases": """* Swipe that turns: direction locks after 10 px.
* Haptics denied: silent no-op.
* Landscape 320 px height: sheet minimum snap adapts.
* Long-press on a link: native menu kept unless a handler exists.""",
"Dependencies": "PAP-150, PAP-20 (hard, encoded; children PAP-258 to PAP-260). Soft: PAP-67, PAP-152. Consumed by PAP-132, PAP-165, PAP-167, PAP-62, PAP-155.",
"Agent": "Builder: Nova with Forge (Tauri Smith) for haptics and device builds. Reviewer: Sentinel (Visual Inspector on device videos, Edge Case Hunter).",
"Size": "M: recognisers are standard; device testing and arbitration take the time.",
}

R["PAP-155"] = {
"Goal": "Umbrella: one accessible drag-and-drop system for lists, tables, kanban and canvas: pointer dragging with previews, a full keyboard alternative, screen-reader announcements, touch and pen support, and cross-window drags between detached panels. Planned as three work packages; the umbrella owns the integration test, docs and the screen-reader spot check hand-off to PAP-156.",
"Scope": """Work packages (build in order; each becomes a child issue once the Linear issue limit is lifted, see the pinned comment):

1. **dnd-kit sensors on the input abstraction and `SortableList`** — `@dnd-kit/core` 6.x wrapper, `PointerSurfaceSensor` (mouse, touch with 250 ms long-press and haptic, pen) on PAP-150, `SortableList` with `onReorder`, fractional indexing helper `between(a, b)`, optimistic revert.
2. **Keyboard alternative, announcements and focus restore** — customised `KeyboardSensor` (`Space`/`Enter` pick up, arrows and `PageUp/PageDown` move, `Space` drop, `Escape` cancel), `LiveAnnouncer` strings in `packages/input/src/copy/dnd.ts`, `useFocusRestore` after drop or cancel, commands `dnd.pickUp|drop|cancel`.
3. **`KanbanDnd`, `SortableGrid`, `DropZone` and cross-window drag** — cross-column moves with `canDrop` reasons and WIP limits, multi-select overlay with count, `DropZone` for files and items, `dnd.transfer` over PAP-145 with target drop hint, auto-scroll and collision strategies.

Parent owns `docs/platform/input/drag-drop.md`, Storybook stories, integration test, template sample pages.

Out: tldraw's own shape dragging (bridge only), upload logic (PAP-37), order persistence (consumers).""",
"Spec": """* `canDrop(source, target)` returns `true | { reason }`; denied targets show a not-allowed cursor, tooltip and announcement.
* Dragging inside a virtualised 10,000-row grid stays at 60 fps; only overlay and two neighbours re-render.
* Collision `closestCenter` for lists, `rectIntersection` for canvas; reduced-motion variants.""",
"Interface contract": """Exposes (owned by the work packages): `<SortableList items getId onReorder renderItem strategy />`, `<SortableGrid />`, `<KanbanDnd columns cards onMove canDrop />`, `<DropZone accept onDrop />`, `DragHandle`, `DragOverlay`, `onReorder({ from, to, item, items })`, `between(a, b)` from `fractional-indexing`, `CanDropResult`, announcement copy keys, window message `dnd.transfer { payload, sourceWindowId }`, commands `dnd.*`. Consumes: `usePointerSurface` and `THRESHOLDS` (PAP-150), `LiveAnnouncer`, `useFocusRestore` (PAP-152), long-press and `haptic()` (PAP-154), `defineCommand` (PAP-151), `WindowBus` (PAP-145), primitives (PAP-67), grid selection state (PAP-165).""",
"Definition of done": """* All three work packages merged; `SortableList`, `KanbanDnd` and `DropZone` used in template sample pages.
* Cross-window drag on Tauri Linux recorded; NVDA and VoiceOver spot check recorded and handed to PAP-156.
* Storybook stories in three themes with reduced motion, axe clean; screenshots at 375, 1024 and 1440; docs; changelog; Linear comment with demo and video links.""",
"Test plan": """* Integration (parent): Playwright at 375, 1024 and 1440: pointer drag reorders and persists via mocked `onReorder`; touch long-press drag on a `hasTouch` context while a plain swipe still scrolls; keyboard path picks up a card, moves it two columns with `PageDown`, drops, and the announcement text matches the snapshot; drop onto a full column is denied with the reason; detach a panel (Tauri or web pop-out fallback) and drag across windows.
* Unit tests per work package (fractional indexing ordering and precision, `canDrop` handling, multi-select payload, revert on rejected promise, keyboard grammar state machine, announcement templates).
* Performance: React Profiler assertion that a drag in a 10,000-row virtual grid re-renders at most three items per frame.
* Visual: Gate 3 captures of overlay, denied state and handles, three themes.""",
"Demo": "On the kanban sample, drag a card between columns with the mouse; press `Tab` to a handle, `Space`, `PageDown`, `Space` and hear “Moved Task A to position 3 of 8 in Doing”; drop a file on the `DropZone`; detach the inspector and drag a row into it. Under two minutes.",
"Edge cases": """* List changes remotely mid-drag: keep alive, recompute on drop; deleted item cancels with announcement.
* WIP limit: "Doing is at its limit (5)".
* Off-screen keyboard target: scroll into view before announcing.
* Alt-tab mid-drag: cancel and restore.
* RTL: arrow semantics flip.""",
"Dependencies": "PAP-150, PAP-152 (hard, encoded). Soft: PAP-154, PAP-151, PAP-145, PAP-67, PAP-165. Blocks PAP-167, PAP-173; consumed by PAP-165, PAP-132, PAP-102.",
"Agent": "Builder: Nova (Views Engineer). Reviewer: Sentinel (Code Reviewer, Edge Case Hunter); Iris reviews handle and overlay styling.",
"Size": "L, planned as three M work packages (child issues pending the issue limit).",
}

R["PAP-156"] = {
"Goal": "Verify with real assistive technology, not only axe, that core flows work with NVDA on Windows, VoiceOver on macOS and iOS, and TalkBack on Android, then fix what breaks. This issue is the single owner of manual AT testing (PAP-73 covers automated component audits). Deliverables: a repeatable protocol, recorded results, merged fixes, and a nightly job once the runners exist.",
"Scope": """In:

* Protocol `docs/platform/a11y/screen-reader-protocol.md`: setup per AT (NVDA 2025.x, VoiceOver macOS 15 and iOS 18, TalkBack Android 15), flow scripts, recording format, severity per PAP-79.
* Flows from PAP-86: sign in (passkey, magic link), tenant switch, skip links and `F6`, create, edit and delete a record, filter and sort, comment with a mention, palette command, receive a live update, keyboard drag (PAP-155).
* Automated layer: `@guidepup/playwright` running VoiceOver and NVDA flows nightly, asserting normalised spoken snapshots under `apps/web/e2e/a11y/snapshots/`; TalkBack manual on a Pixel emulator with video.
* Tier 1 (runs today on Linux): ARIA snapshot (`toMatchAriaSnapshot`) and accessible-name audit for every flow, so most Sev-1 findings surface before any AT runner exists.
* Fix pass: Sev-1 and Sev-2 fixed here or filed with the `a11y` label; results report `docs/platform/a11y/screen-reader-results-<date>.md`.

Out: switch access, third-party widgets, the statement (PAP-160).""",
"Spec": """* Snapshot JSON `{ flow, at, browser, steps: [{ action, spoken, expected, pass }] }`; normaliser lowercases, strips punctuation and trailing role words, replaces digits with `#`.
* Conformance: every interactive element has a name; roles and states match visuals; live regions announce at the agreed cadence (PAP-141, PAP-144); grids expose `aria-rowcount`/`aria-rowindex`; dialogs announce titles; toasts `role="status"`; `role="application"` never used.
* Runners: the Windows NVDA VM and hosted `macos-15` runner are provisioned by the planned forge non-Linux runners issue; until they exist the nightly job runs Tier 1 only and is marked `partial` in the report, never green.
* Sev-1 and Sev-2 must close before the milestone.""",
"Interface contract": """Exposes: protocol doc, snapshot format above (consumed by PAP-160's `criteria-map.json` `sr-matrix` source), `a11y-sr` workflow with artifact `sr-results.json` `{ date, tier, matrix: [{ flow, at, browser, status, severity? }] }`, `@guidepup` helper `speakAndAssert(page, action, expected)`, the `a11y` label convention and fix PR trailer `A11y-Fixes: PAP-156`. Consumes: e2e flow scripts and test-mode login (PAP-86, PAP-240), primitives (PAP-67), focus utilities (PAP-152), drag flows (PAP-155), rubric severities (PAP-79), quarantine rules (PAP-90), Linear comment posting (PAP-97), non-Linux runners (forge gap; hard for Tier 2).""",
"Definition of done": """* Protocol merged and linked from PAP-79.
* Tier 1 job green nightly for three nights; Tier 2 (NVDA, VoiceOver) green for three nights once runners exist, failures posting to Linear.
* TalkBack manual run recorded for all flows; report shows zero open Sev-1 and Sev-2; Sev-3 filed.
* Changelog; Linear comment with the report link and one matrix screenshot.""",
"Test plan": """* Unit: snapshot normaliser (digits, punctuation, role words, locale forced to `en-US`); matrix builder from result files marks missing cells `not run`, never `pass`.
* Tier 1 Playwright (Linux, every PR on `a11y` label, nightly otherwise): ARIA snapshots per flow step at 375 and 1280; accessible-name audit fails on any unnamed control; dialog title announced via live region assertion.
* Tier 2 nightly: guidepup VoiceOver on `macos-15`, NVDA on the Windows VM (Firefox, Chrome), one flow per theme and one in the Tauri iOS webview; TalkBack videos attached manually.
* Flakes: retry once, then quarantine per PAP-90 with a visible `partial` flag.""",
"Demo": "Open the latest `screen-reader-results` report and read the matrix; run `pnpm e2e:a11y --tier 1 --flow create-record` locally and watch the ARIA snapshot diff; play the 30-second TalkBack clip of creating a record. Under two minutes.",
"Edge cases": """* iOS Tauri webview differs from Safari: run flows in both.
* NVDA browse versus focus mode in grids: arrows must work in focus mode.
* Non-English runner locale: force `en-US`.
* Runner never provisioned before 10-01: report ships as `partial` with Tier 1 results and the risk stated; not silently green.""",
"Dependencies": "PAP-152, PAP-86, PAP-73 (hard, encoded). Soft: PAP-67, PAP-155, PAP-90, PAP-240, planned forge non-Linux runners issue (Tier 2). Blocks PAP-160.",
"Agent": "Builder: Sentinel (Visual Inspector runs the protocol; Code Reviewer prepares fixes) with Iris fixing `packages/ui`. Reviewer: Nova for `packages/input` fixes; Justin sees only the final matrix in the release digest.",
"Size": "M: protocol and automation are bounded; the fix list is capped by severity rules.",
}

R["PAP-157"] = {
"Goal": "Make tablets with a stylus first-class for sketching and annotation: pressure-sensitive strokes on the canvas, palm rejection, barrel-button eraser, hover previews and pen markup on screenshots. Pen flows through the shared abstraction so canvas, screenshot annotation and future whiteboards behave identically.",
"Scope": """In:

* `packages/input/src/pen/`: `usePenStroke(surface, { smoothing, pressureCurve, minWidth, maxWidth })` producing `{ x, y, pressure, tiltX, tiltY, t }` points with `perfect-freehand` outlines and Catmull-Rom smoothing; `usePenHover`; `usePenButtons` (barrel → eraser, secondary → lasso).
* Palm rejection and pen priority from PAP-150; two-finger touch still pans.
* Canvas tool `PaperOSPenTool` in PAP-132 storing strokes as a Yjs shape `type: 'ink'` with delta encoding; live stroke on a `<canvas>` layer, committed strokes as SVG; `getCoalescedEvents` up to 240 Hz.
* `InkAnnotationLayer` in `packages/ui` for images and screenshots (PAP-137): draw, highlight (multiply), erase, undo and redo, export SVG overlay and flattened PNG.
* Pen settings `/settings/input`: pressure presets, widths, "pen only draws", left-handed offset.

Out: handwriting or shape recognition, ink text input, driver-specific features.""",
"Spec": """* Width `f(p) = min + (max − min) × curve(p)`; tilt modulates up to 30 percent when enabled.
* `getPredictedEvents` for the preview segment only, never stored.
* Stroke `{ id, tool, color, width, points: Int16Array deltas (0.1 px), pressures: Uint8Array }`; 5,000 points under 20 KB; split over 20,000.
* Under 16 ms sample to paint; eraser whole-stroke by default, segment with `alt`.
* Undo via `y-undo-manager` scoped to the user; ink decorative unless alt text is added; annotation list keyboard navigable.""",
"Interface contract": """Exposes: `usePenStroke`, `usePenHover`, `usePenButtons`, `InkStroke` type and `encodeStroke()`/`decodeStroke()`, `InkAnnotationLayer` (`onChange(strokes)`, `exportSvg()`, `exportPng()`), canvas node type `ink` registered through PAP-132's `registerNodeType`, `PressureCurve` presets, settings keys `input.pen.*` in `user_preferences`. Consumes: pen fields, palm rule and `getCoalescedEvents` plumbing (PAP-150), canvas tool host and overlay doc (PAP-132), room persistence (PAP-140), two-finger pan (PAP-154), annotation viewer slot (PAP-137), ink colour tokens (PAP-66), y-undo pattern (PAP-142).""",
"Definition of done": """* Pen on a Windows Surface or Android tablet (Tauri) shows pressure-varying strokes, palm rejection and eraser; video attached.
* Two browsers see each other's strokes within 100 ms on localhost; PAP-137 demo marks up a screenshot and exports PNG and SVG.
* Screenshots at 768 and 1280; `docs/platform/input/pen.md`; changelog; Linear comment with video and demo link.""",
"Test plan": """* Vitest: pressure curves at p = 0, 0.5, 1 for each preset, delta encoding round-trip, stroke splitting at 20,000 points, palm-rejection timing window, constant-pressure detection over 20 samples.
* Playwright: CDP `Input.dispatchMouseEvent` with `pointerType: 'pen'` and varying `force` asserts width variation in the SVG path; `PerformanceObserver` latency budget under 16 ms p95; mouse on the ink tool draws constant width and `shift` makes a straight line; run at 768 and 1280.
* Integration: two contexts on a canvas room converge on the ink shape within 100 ms.
* Visual: Gate 3 captures of strokes in light and dark and the settings page; axe on the annotation list.""",
"Demo": "Open the canvas on a tablet, pick the pen, draw with varying pressure, rest your palm, flip to the barrel button and erase; open a QA screenshot, highlight a region and export PNG. Under two minutes.",
"Edge cases": """* Pen leaves mid-stroke: commit on `pointercancel` or 500 ms.
* Constant pressure hardware: fixed width.
* 100k-point session: bitmap tiles for old strokes, SVG for the last 200.
* 8× zoom: widths scale, minimum 1 px.""",
"Dependencies": "PAP-150, PAP-132 (hard, encoded). Soft: PAP-140, PAP-154, PAP-137, PAP-66.",
"Agent": "Builder: Nova (Canvas Cartographer). Reviewer: Sentinel (Visual Inspector, Code Reviewer); Iris for settings UI.",
"Size": "M: rendering and encoding are contained; device testing adds time.",
}

R["PAP-158"] = {
"Goal": "Make the 10-foot UI work: a PaperOS app in kiosk or TV mode (PAP-23) driven entirely by gamepad, TV remote or arrow keys, using spatial focus that moves to the geometrically nearest element. This also gives motor-impaired users on switch or D-pad devices a working path through every page.",
"Scope": """In:

* `packages/input/src/spatial/`: `SpatialNavigationProvider` (2D search over registered focusables), `useFocusable({ group, onEnter, onLongEnter })`, `FocusGroup` (grid, list, menu semantics with last-child memory), `enableSpatialNavigation({ trigger: 'gamepad'|'always' })`.
* Gamepad mapping on PAP-150 events: D-pad and left stick move, `A` activate, `B` back, `X` context menu, `Y` palette, bumpers cycle regions (PAP-152), triggers scroll, `Start` help; stick repeat with acceleration, deadzone 0.25.
* Arrow keys, `Enter`, `Escape`, `Backspace` map to the same actions; commands `spatial.move.*`, `spatial.activate`, `spatial.back` (PAP-151).
* Cursor mode: hold `LB` for a virtual pointer (`gamepad-cursor`) on canvases.
* TV theme with Iris: 4 px focus ring, 48 px targets, 24 px type at the `tv` breakpoint (PAP-14); idle return to home; `SpatialKeyboard` on-screen keyboard.

Out: vibration beyond `haptic()`, remap UI (PAP-153), native TV apps.""",
"Spec": """* Score = distance to the exit edge centre + 3 × off-axis offset; ties by DOM order; `data-spatial-priority` pins.
* Groups expose `enterFrom(direction)` and `onExit(direction)`; overlays become the active root; `B` calls `onClose`.
* Activation dispatches a real `click`; long `A` (600 ms) fires `contextmenu`; focus scrolls into view with a 10 percent margin.
* Spatial mode enables on first gamepad input or `?input=tv`; a controller glyph appears in the status bar.""",
"Interface contract": """Exposes: `SpatialNavigationProvider`, `useFocusable`, `FocusGroup`, `useSpatialMode()`, `scoreCandidates(from, direction, candidates)` (pure, tested), DOM attributes `data-spatial-group`, `data-spatial-priority`, gamepad mapping table JSON per controller family, commands `spatial.*`, `SpatialKeyboard` with `DictationTarget`-compatible insertion (shared with PAP-159), help overlay component. Consumes: `gamepad` events and `gamepad-cursor` pointer (PAP-150), `FocusRegion` list and `LiveAnnouncer` (PAP-152), `defineCommand` (PAP-151), kiosk config and TV breakpoint (PAP-23, PAP-14), theme tokens (PAP-75), `Dialog` and `BottomSheet` `onClose` (PAP-237, PAP-154).""",
"Definition of done": """* Kiosk build drives the template app end to end (PIN sign-in, navigate, open record, edit a select, run a palette command) with an Xbox controller; video attached.
* `SpatialKeyboard` enters text into an input and a Tiptap comment.
* Screenshots of the TV focus ring at 1280 and 1920; `docs/platform/input/spatial-and-gamepad.md` with mapping table; changelog; Linear comment with video and demo links.""",
"Test plan": """* Vitest: `scoreCandidates` on fixture layouts (ragged grid lands on nearest cell, sticky column, priority pin, hidden and `inert` excluded), group entry memory, deadzone and repeat timing with fake timers, two-controller arbitration.
* Playwright with mocked `navigator.getGamepads` at 1280 and 1920: focus path through a grid, sidebar and dialog matches the expected selector sequence; `B` closes the dialog; disconnect mid-interaction keeps keyboard arrows working and shows a toast; `?input=tv` enables spatial mode without a controller.
* Integration: kiosk compose build boots with `?input=tv` and the smoke flow passes headless.
* Visual: Gate 3 captures of the TV theme ring and help overlay at 1280 and 1920.""",
"Demo": "Load the template with `?input=tv` at 1920, use the arrow keys to move through the sidebar and grid, `Enter` a record, `Escape` back, hold `Start` (or `?`) for the mapping overlay; plug in a controller and repeat with the D-pad. Under two minutes.",
"Edge cases": """* Element appears under focus after a live update: no jump.
* Repeat while a dialog opens: repeat cancels.
* Two controllers: last used wins.
* Carousel ends: `onExit` swallows left and right.""",
"Dependencies": "PAP-152, PAP-150 (hard, encoded). Soft: PAP-151, PAP-23, PAP-14, PAP-75, PAP-67, PAP-154. Consumed by PAP-159 (hold-space in TV mode).",
"Agent": "Builder: Nova with Iris (Motion and Input Stylist) on the TV theme. Reviewer: Sentinel (Visual Inspector, Edge Case Hunter); Forge (Ops Runner) verifies the kiosk build.",
"Size": "M: the algorithm is compact; grouping every layout correctly is the work.",
}

R["PAP-159"] = {
"Goal": "Let people talk to the app: say a command (“open inbox”, “assign to Bo”) and it runs through the command registry; dictate into any text field with punctuation. This build uses the browser's Web Speech API only; a self-hosted Whisper backend is recorded as a reopen criterion, not built (keeps the TypeScript-only monorepo and the VPS RAM budget from PAP-214).",
"Scope": """In:

* `packages/input/src/voice/`: `VoiceProvider` with a `SpeechBackend` interface (`start/stop/onPartial/onFinal/onError`) and one implementation `WebSpeechBackend` (`SpeechRecognition`, `continuous`, `interimResults`); a `MockBackend` for tests.
* Intent matching over `commands.manifest.json` (PAP-151): normalise transcript, fuzzy match titles, keywords and PAP-153 aliases, chooser when the top two are close, slot extraction (people via `MentionSource`, status values, numbers, dates via `chrono-node` 2.x).
* Dictation into `<input>`, `<textarea>` and `RichTextEditor` (PAP-142) via a `DictationTarget` adapter: spoken punctuation, auto-capitalisation, undo last utterance.
* UI: `VoiceButton` (push-to-talk `mod+shift+v`, hold-space in TV mode), listening indicator with waveform, partial transcript chip, confirmation toast; palette entry "Start dictation".
* Privacy: permission flow with explanation, visible capture indicator, no audio stored, transcripts logged only with tenant setting `voice.logTranscripts`; tenant setting `voice.enabled` (Chrome sends audio to Google, so tenants can disable).
* ADR note: Whisper backend reopens when a tenant requires on-premise recognition or when Firefox and WebKitGTK usage exceeds 20 percent.

Out: Whisper server, wake words, text-to-speech, natural-language questions, non-English beyond configuration.""",
"Spec": """* Score = 0.6 × Jaro-Winkler token similarity + 0.4 × double-metaphone; threshold 0.75; one candidate runs, several within 0.05 open the chooser, none → toast with transcript.
* Commands opt in with `voice: { phrases?, confirm? }`; `confirm: true` requires "yes" or a click.
* Only finals trigger commands; partials are display only.
* Unsupported browser: button disabled with a tooltip naming the supported browsers; everything voice does is possible by keyboard.
* Listening state announced; indicator uses icon, text and motion (motion off under reduced motion).""",
"Interface contract": """Exposes: `SpeechBackend` interface (the seam a future Whisper backend implements), `VoiceProvider`, `useVoice()`, `matchCommand(transcript, manifest, aliases) -> { command, score, args }[]`, `DictationTarget { insert(text), deleteLast(n), getContext() }` with adapters for inputs and Tiptap (PAP-158's `SpatialKeyboard` reuses it), command extension `voice` on `defineCommand`, tenant settings keys `voice.enabled`, `voice.logTranscripts`. Consumes: manifest, `execute(id, args, 'voice')` and `voice` option (PAP-151), effective aliases (PAP-153), `RichTextEditor` insertion API (PAP-142), `MentionSource` (PAP-142), tenant settings (PAP-33), microphone entitlement for Tauri mobile (PAP-260), palette registration (PAP-151).""",
"Definition of done": """* "Open inbox", "create record", "assign to Bo" and "mark done" run on the sample pages in Chrome; demo video attached.
* Dictation into a form field and a Tiptap comment with spoken punctuation works; screenshots of indicator and chooser at 375 and 1280.
* Security review confirms no audio persistence and settings gating; `docs/platform/input/voice.md` with the browser matrix, privacy statement text and the Whisper reopen criteria; changelog; Linear comment with links.""",
"Test plan": """* Vitest: transcript normalisation, scoring thresholds with fixtures (exact, near, homophones "Bo"/"Beau", none), slot extraction for people, status, numbers and dates, punctuation and capitalisation rules, undo of last utterance.
* Component: `VoiceButton` states (idle, listening, denied, unsupported) with axe; reduced-motion story has no waveform animation.
* Playwright with `MockBackend` injected via `window.__paperosVoice.inject(transcript)` at 375 and 1280: commands run and toast, chooser appears for near ties, dictation inserts into an input and a Tiptap comment, out-of-scope command refused with "Not available here".
* Manual: Chrome desktop and Android Chrome real microphone run recorded.""",
"Demo": "In Chrome, hold `mod+shift+v`, say “open inbox”, release, watch it navigate and toast “Ran: Open inbox”; click into a comment, choose “Start dictation” from the palette and dictate a sentence with “comma” and “new line”. Under two minutes.",
"Edge cases": """* Noisy finals: only finals trigger; low score → toast.
* Permission denied: disabled state with instructions, no re-prompt loop.
* Chrome stops after ~60 s silence: auto-restart while held.
* Tenant disables voice: button hidden, command unregistered.""",
"Dependencies": "PAP-151 (hard, encoded). Soft: PAP-153, PAP-142, PAP-33, PAP-260, PAP-158.",
"Agent": "Builder: Nova. Reviewer: Sentinel (Security Auditor for privacy gating, Edge Case Hunter for noisy input).",
"Size": "M: one backend plus matching and dictation; the matching logic is testable offline.",
}

R["PAP-160"] = {
"Goal": "Give every PaperOS app compliance evidence out of the box: a public accessibility statement and a WCAG 2.2 AA conformance report (VPAT 2.5 / ACR structure) generated from real test results and refreshed every release, so it never drifts. Customers get a link; Justin gets a one-page view of remaining gaps.",
"Scope": """In:

* Templates `packages/spec/templates/a11y/statement.mdx` and `acr.mdx` filled from `app.spec.yaml` (PAP-117: name, contact, audiences) and test data.
* Generator `pnpm a11y:report` reading axe results (PAP-73, PAP-82), the screen-reader matrix (PAP-156 `sr-results.json`), focus-order audit (PAP-152), contrast results (PAP-84) and open `a11y` Linear issues (PAP-101 read API); maps sources to criteria via `criteria-map.json`; writes `docs/a11y/statement.mdx`, `acr.mdx`, `report.json`.
* Rendering at `/accessibility` in portal and console via PAP-128; ACR PDF via PAP-235's `renderPdf()`.
* Release hook: PAP-88 runs the generator per RC; PAP-89 digest shows the conformance delta.
* Feedback form (PAP-169 form view) creating an `a11y` issue through PAP-97.

Out: legal wording (Justin), EN 301 549 and Section 508 chapters (stubbed), third-party audits.""",
"Spec": """* Map entry `{ criterion, sources: [{ type: axe|sr-matrix|focus|contrast|manual, ... }], defaultStatus: 'Not Evaluated' }`; resolution: any failing automated rule → Partially Supports (Does Not Support if all fail); all pass plus manual confirmed → Supports; no data → Not Evaluated, shown never hidden.
* Every non-Supports row links a tracking issue or the generator fails.
* Known limitations generated from open `a11y` issues' `publicSummary` (PAP-93 contract).
* Statement passes axe and Flesch-Kincaid grade ≤ 9 (`text-readability`); report carries `generatedAt`, version (PAP-52) and hash; "Next review by" 90 days.""",
"Interface contract": """Exposes: `report.json` `{ generatedAt, version, criteria: [{ id, level, status, sources[], issueUrl?, remarks }] }` consumed by PAP-89; `criteria-map.json` schema; MDX templates with frontmatter strings for i18n; routes `/accessibility` and `/accessibility/acr.pdf`; CLI `a11y:report [--from-cache]`. Consumes: `a11y-report.json` (PAP-73), `visual.json` axe section (PAP-82, PAP-239), `sr-results.json` (PAP-156), focus-order JSON (PAP-152), `vision.json` contrast findings (PAP-84), Linear read API (PAP-101), `publicSummary` field (PAP-93), app spec (PAP-117), `renderMdx` (PAP-128), `renderPdf` (PAP-235), release hooks (PAP-88, PAP-89), form view (PAP-169), webhook issue creation (PAP-97).""",
"Definition of done": """* `pnpm a11y:report` runs in CI on the template and commits `docs/a11y/*`; all 55 WCAG 2.2 A and AA criteria appear with status and source.
* `/accessibility` renders at 320, 768 and 1280; axe clean; readability passes; ACR PDF attached.
* One RC digest shows a conformance delta; feedback form creates a labelled issue (linked, then closed).
* `docs/platform/a11y/statement-and-acr.md`; changelog; Linear comment with the page link, routed to Needs Justin for wording approval only.""",
"Test plan": """* Vitest: status resolution matrix (all pass + manual → Supports, one fail → Partially, all fail → Does Not, none → Not Evaluated), missing issue link fails the run, `Not Applicable` requires a justification, cache fallback when Linear is unreachable produces a warning banner, readability check on the template text.
* Integration: generator over fixture result files for all sources writes `report.json` matching a snapshot; per-theme contrast takes the worst status.
* Playwright: `/accessibility` at 320, 768 and 1280 as anonymous in the portal and as staff in the console; ACR table scrolls horizontally at 320; feedback form submits and the mocked webhook receives an `a11y`-labelled issue.
* Visual: Gate 3 captures of statement and ACR at the three widths, both themes.""",
"Demo": "Run `pnpm a11y:report`, open `/accessibility`, scroll the ACR to 2.1.1 and follow its tracking issue link, download the PDF, submit the feedback form and open the created Linear issue. Under two minutes.",
"Edge cases": """* Manual-only criterion without a record: Not Evaluated with owner.
* Hotfix release skips tests: reuse last full results, "based on version X".
* White-labelled tenant: tenant name and contact, worst-theme contrast.
* Over 20 limitations: grouped and collapsed.""",
"Dependencies": "PAP-156, PAP-117 (hard, encoded). Soft: PAP-73, PAP-82, PAP-84, PAP-152, PAP-128, PAP-235, PAP-88, PAP-89, PAP-101, PAP-93, PAP-52, PAP-169, PAP-97.",
"Agent": "Builder: Quill (Changelog Scribe for templates, Page Spec Writer for the docs page) with Sentinel providing data sources. Reviewer: Sentinel (Visual Inspector) verifies the mapping; Justin approves wording.",
"Size": "S: templates and a generator over existing data; the discipline is in the criteria map.",
}
