# Round 4 digest: Multi-Input Control & Accessibility (`input`)

Benchmarks: Figma (shortcuts, context menus, multi-window); Linear (command palette, keymaps, sequences); VS Code (command registry, keybindings, macros, native menus); Raycast (global hotkey); Superhuman; Excel and Google Sheets (grid keyboard, fill, clipboard); macOS Accessibility (Switch Control, Sticky Keys, Dwell); Windows Ease of Access; iOS and Android accessibility (VoiceOver, TalkBack, Switch Access); WCAG 2.2 AA (2.1.4, 2.2.1, 2.5.7, 2.5.8).

Feature matrix: 45 rows, 27 covered, 4 partial, 14 gap. New issues: 14 (4 with a parent, 10 standalone gaps, 1 deferred to v0.2). Amendments: 8. Cross-project suggestions: 4.

## Feature matrix

| Feature | Status | Covered by | Note |
|---|---|---|---|
| Unified input event abstraction (mouse, touch, pen, gamepad) | covered | PAP-150, PAP-476 |  |
| Wheel and trackpad normalisation, mouse buttons back/forward | partial | PAP-150 | Amendment |
| IME composition safety in matcher and editors | partial | PAP-289 | Amendment |
| Command registry, scopes, chord and sequence matcher | covered | PAP-289 |  |
| Command palette and help sheet | covered | PAP-290 |  |
| Agent execution endpoint and default commands | covered | PAP-291 |  |
| Context menus from the registry (right-click, long-press, Shift+F10) | gap | r4/input/command-context-menus | Linear/Figma/VS Code pattern |
| Native desktop menu bar from the command manifest | gap | r4/input/native-menu-from-command-manifest |  |
| OS-level global hotkey and tray | partial | PAP-255 | Tray Show/Quit in PAP-255; global hotkey owned by app-shell r4/app-shell/desktop-os-integration (v0.2) |
| Keymap presets (default, Vim, Linear) and rebinding | covered | PAP-153 |  |
| Macros / recorded command chains | gap | r4/input/macros-and-command-chains | Named in the brief |
| Undo/redo manager shared by grid, canvas, docs | gap | r4/input/undo-manager | edit.undo|redo commands exist without a stack |
| Clipboard port with typed payloads | gap | r4/input/clipboard-port | Grid, canvas, cross-window drags |
| Focus regions, roving tabindex, skip links, F6 | covered | PAP-152 |  |
| Live announcer | covered | PAP-152 |  |
| Multi-window command and focus routing | gap | r4/input/multi-window-command-and-focus-routing | Brief: multi-monitor |
| Touch gesture recognisers and arena | covered | r4/input/gesture-recognisers-and-arena | Split from PAP-154 |
| Mobile components: swipe row, pinch zoom, pull to refresh, bottom sheet | covered | r4/input/mobile-gesture-components-and-haptics | Split from PAP-154 |
| Haptics | covered | r4/input/mobile-gesture-components-and-haptics, PAP-260 |  |
| Virtual keyboard inset and focused-field visibility | gap | r4/input/virtual-keyboard-viewport | Forms unusable on phones otherwise |
| Touch targets 44px audit | covered | r4/input/mobile-gesture-components-and-haptics, PAP-73 |  |
| Drag-and-drop sensors and SortableList | covered | PAP-329 |  |
| Keyboard drag alternative and announcements | covered | PAP-330 |  |
| Kanban DnD, grid DnD, drop zones, cross-window drag | covered | PAP-331 |  |
| Native OS file drop (Tauri) | partial | PAP-331 | Amendment |
| Pen and stylus with pressure | covered | PAP-157 | Deferred |
| Gamepad and TV spatial navigation | covered | PAP-158 | Deferred |
| Switch access scanning | gap | r4/input/switch-access-scanning | Deferred; named in the brief |
| Voice backend seam and intent matching | covered | r4/input/voice-backend-and-intent-matching | Split from PAP-159 |
| Dictation into fields and voice UI | covered | r4/input/dictation-targets-and-voice-ui | Split from PAP-159 |
| Text-to-speech / read aloud | gap | — | wontdo v0.1; screen readers cover |
| Screen reader testing NVDA/VoiceOver/TalkBack | covered | PAP-156, PAP-371 |  |
| Accessibility statement and ACR | covered | PAP-160 |  |
| WCAG 2.1.4 single-key shortcut disable/remap | gap | r4/input/accessibility-input-preferences | Conformance requirement |
| Sticky-key chords, key repeat, dwell click, timing extensions | gap | r4/input/accessibility-input-preferences |  |
| Always-visible focus ring and font scale preference | gap | r4/input/accessibility-input-preferences |  |
| Reduced motion preference | covered | PAP-72 | Design system |
| High contrast theme | covered | PAP-75 | Design system |
| Zoom and reflow | covered | r4/design-system/reflow-zoom-text-spacing-audit | Design system |
| Playwright input fixtures (chords, gestures, gamepad, drag) | gap | r4/input/playwright-input-fixtures | Every e2e re-implements them |
| Input telemetry by modality | covered | PAP-291 |  |
| Keyboard hint overlay and onboarding | covered | PAP-380, PAP-290 | Collab owns the overlay |
| Spreadsheet-style grid keyboard (F2, Tab, Enter) | covered | PAP-341, PAP-342 |  |
| Eye tracking / BCI | gap | — | Non-goal per project description |
| Module contract, conformance, wiring | covered | PAP-476, PAP-479, PAP-482 |  |

## New issues

| Key | Title | Parent | Milestone | Size | Model / effort | Priority | Deferred |
|---|---|---|---|---|---|---|---|
| `r4/input/undo-manager` | Global undo manager: scoped undo and redo stacks, coalescing, Yjs UndoManager bridge, toast integration and the edit.undo|redo commands | — | Keyboard and command system | M (3) | Opus 5 / high | 2 |  |
| `r4/input/command-context-menus` | Command-driven context menus: right-click, long-press and the ContextMenu key render scoped commands for records, cells, cards, nodes and selections | — | Keyboard and command system | S (2) | Sonnet 5 / medium | 2 |  |
| `r4/input/clipboard-port` | Clipboard port: typed copy and paste with a PaperOS MIME payload, plain-text and TSV fallbacks, Tauri clipboard plugin and permission handling | — | Keyboard and command system | S (2) | Sonnet 5 / medium | 2 |  |
| `r4/input/playwright-input-fixtures` | Shared Playwright input fixtures: pressChord, sequence, touch gestures, pen, gamepad mock, drag helpers and input-modality assertions for every e2e and gate | — | Keyboard and command system | S (2) | Sonnet 5 / medium | 2 |  |
| `r4/input/virtual-keyboard-viewport` | Virtual keyboard handling on mobile: visualViewport tracking, keyboard-inset CSS, focused-field scroll-into-view and bottom-sheet and toolbar repositioning | — | Touch, pen, gamepad | S (2) | Sonnet 5 / medium | 2 |  |
| `r4/input/multi-window-command-and-focus-routing` | Multi-window command and focus routing: per-window scope roots, global command forwarding over the WindowBus, focus.nextWindow and palette in detached panels | — | Voice and accessibility certification | M (3) | Sonnet 5 / high | 2 |  |
| `r4/input/accessibility-input-preferences` | Accessibility input preferences: /settings/accessibility with single-key shortcut disable (WCAG 2.1.4), sticky-key chords, key repeat, hover and dwell delays, always-visible focus, timing extensions | — | Voice and accessibility certification | M (3) | Sonnet 5 / high | 2 |  |
| `r4/input/macros-and-command-chains` | Macros: record a sequence of commands into a named macro, bind it to a chord or palette entry, share per workspace and expose it to agents | — | Voice and accessibility certification | M (3) | Sonnet 5 / medium | 3 |  |
| `r4/input/native-menu-from-command-manifest` | Native menu and tray items generated from the command manifest with keymap-synced accelerators, routed through the command registry | — | Touch, pen, gamepad | S (2) | Sonnet 5 / medium | 3 |  |
| `r4/input/switch-access-scanning` | Switch access scanning: single and dual switch auto-scan over focusables and groups with highlight, timing and an on-screen action menu | — | Voice and accessibility certification | M (3) | Sonnet 5 / medium | 4 | yes |
| `r4/input/gesture-recognisers-and-arena` | Gesture recognisers and arena: useTap, useLongPress, useSwipe, usePinch, usePan, usePullToRefresh, useEdgeSwipe on the pointer surface with ownership arbitration | PAP-154 | Touch, pen, gamepad | M (3) | Sonnet 5 / high | 2 |  |
| `r4/input/mobile-gesture-components-and-haptics` | Mobile gesture components and haptics: SwipeableRow, PinchZoomView, PullToRefresh, BottomSheet, haptic() over the Tauri plugin and the touch-target audit | PAP-154 | Touch, pen, gamepad | M (3) | Sonnet 5 / high | 2 |  |
| `r4/input/voice-backend-and-intent-matching` | Voice backend and intent matching: SpeechBackend interface, WebSpeechBackend and MockBackend, transcript normalisation, fuzzy command matching and slot extraction | PAP-159 | Voice and accessibility certification | M (3) | Sonnet 5 / high | 2 |  |
| `r4/input/dictation-targets-and-voice-ui` | Dictation targets and voice UI: DictationTarget adapters for inputs and Tiptap, spoken punctuation, VoiceButton with push-to-talk, listening indicator, chooser and confirmation | PAP-159 | Voice and accessibility certification | M (3) | Sonnet 5 / high | 2 |  |

## Amendments to existing specs

| Issue | Section | Summary |
|---|---|---|
| PAP-150 | Spec | * Round 4: `wheel` events are normalised to `{ deltaX, deltaY, deltaMode: 'pixel', isTrackpad, ctrlKey }` (line and page modes converted with 16 px and viewport… |
| PAP-289 | Spec | * Round 4: the matcher ignores `keydown` while `event.isComposing` is true and the 229 keyCode, and resets pending sequences on composition start. The registry … |
| PAP-331 | Spec | * Round 4: `DropZone` also accepts native OS file drops in Tauri through `getCurrentWebview().onDragDropEvent` (paths converted with `convertFileSrc` and read t… |
| PAP-153 | Spec | * Round 4: the resolver gains two fixed layers between presets and user overrides: `a11y` (written by `r4/input/accessibility-input-preferences`: with `singleKe… |
| PAP-159 | Edge cases | * Round 4: WebKitGTK (Tauri Linux desktop) and Firefox expose no `SpeechRecognition`; `capabilities.supported` is false, the button renders the unsupported stat… |
| PAP-156 | Test plan | * Round 4: the protocol runs each flow twice on Tier 1, once with default input preferences and once with `singleKeyShortcuts: 'off'` and `focusRing: 'always'` … |
| PAP-154 | Definition of done | * Round 4: this issue is an umbrella for `r4/input/gesture-recognisers-and-arena` and `r4/input/mobile-gesture-components-and-haptics`. Device video is required… |
| PAP-160 | Spec | * Round 4: the statement links `/settings/accessibility` (`r4/input/accessibility-input-preferences`) as the mechanism for criteria 2.1.4 (character key shortcu… |

## Cross-project suggestions

| Target | Title | Why |
|---|---|---|
| collab | PAP-380 keyboard hint overlay reads `commands.manifest.json` and effective chords from the PAP-153 resolver instead of a static list | Otherwise the overlay drifts from keymaps and macros; the input project exposes `useEffectiveChord` for exactly this. |
| quality | Gate 3 records a keyboard-only replay of each critical flow using `@paperos/input/testing` | The brief asks for video replays across sizes; a keyboard-only track proves 2.1.1 per flow and feeds PAP-160's ACR. |
| app-shell | Tauri capabilities for `menu`, `tray` and `clipboard-manager` plugin calls in PAP-255 and PAP-260 with per-platform notes | `r4/input/native-menu-from-command-manifest` and `r4/input/clipboard-port` need the capabilities declared in the shell's Tauri config, which app-shell owns; the global shortcut stays with `r4/app-shell/desktop-os-integration`. |
| realtime | WindowBus message catalogue entries for `command.forward|result`, `focus.request`, `clipboard.sync` and `a11y.prefs.changed` in PAP-145 | The input project defines the payload schemas; PAP-145 should register them so the bus validates and documents them. |

## What was missing and why it matters

1. `edit.undo|redo` exist as default commands (PAP-291) but four issues each invent their own undo; a shared `UndoManager` with scoped stacks and a Yjs bridge is the missing keystone that the grid, canvas, docs and bulk actions all plug into.
2. Justin's brief puts multi-monitor first, yet nothing defined what `mod+k`, `F6` or a page command does in a detached window; multi-window command and focus routing is now specified (placed in the 09-30 milestone because it needs the WindowBus, PAP-145, dated 09-28).
3. WCAG conformance items that the accessibility statement (PAP-160) must cite had no owner: single-key shortcut disable or remap (2.1.4), timing extensions (2.2.1), sticky-key chords, dwell click and font scale; `/settings/accessibility` now owns them, and switch-access scanning is specified as v0.2.
4. Cross-cutting plumbing that every consumer would otherwise re-implement is now shared: a typed clipboard port (grid ranges, canvas nodes, cross-window transfer), command-driven context menus, Playwright input fixtures for chords, gestures and gamepads, and virtual-keyboard inset handling so phone forms stay usable.
5. Macros (named in the brief) and a command-manifest-driven native menu (on top of PAP-255's scaffold; the global hotkey stays with app-shell) give the multi-input story its power-user and desktop-app feel; PAP-154 and PAP-159 were split so the offline-testable halves (recognisers, intent matching) are not held hostage by device videos and Chrome microphones.
