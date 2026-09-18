---
identifier: "PAP-649"
title: "Native menu and tray items generated from the command manifest with keymap-synced accelerators, routed through the command registry"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Touch, pen, gamepad"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-153", "PAP-255", "PAP-291"]
blocks: []
key: "r4/input/native-menu-from-command-manifest"
url: "https://linear.app/paperos/issue/PAP-649/native-menu-and-tray-items-generated-from-the-command-manifest-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:22.590Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-27"
cycle: null
---

# PAP-649: Native menu and tray items generated from the command manifest with keymap-synced accelerators, routed through the command registry

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-255 ships a static Tauri menu (File, Edit, View, Window, Help) and a tray with Show and Quit. A desktop app whose menu does not know the app's commands feels like a website in a frame. Generate the menu items from `commands.manifest.json`, keep accelerators in sync with the user's keymap, and route activation through the registry so the menu, the palette and the shortcut sheet never disagree. The OS-level global hotkey is owned by PAP-513 (v0.2) and is out of scope here.

**Scope**

In: `packages/input/src/native/{menuModel,menuBridge}.ts`; Rust side `apps/desktop/src-tauri/src/menu.rs` extended to rebuild from a JSON model sent over `invoke('set_menu_model')`; `buildMenuModel(manifest, effectiveBindings, platform)`; `menu.activate` event routed to `registry.execute(id, {}, 'menu')`; tray quick actions (`record.new`, `sync.pause|resume`) appended to PAP-255's tray; capability entries; docs.

Out: global shortcut and OS notifications (PAP-513), base menu and tray scaffold (PAP-255), macOS Services and Touch Bar, Windows jump lists, mobile (no menus), web (no-op adapter).

**Spec**

* `buildMenuModel` produces `{ label, items: [{ id, label, accelerator?, enabled, checked?, submenu? }] }` from commands whose `menu.showIn` (PAP-289 amendment) includes `native`; `menu.group` maps to a top-level menu (`file|edit|view|go|window|help`); `Edit` keeps the native `undo|redo|cut|copy|paste|selectAll` items, routed to `edit.*` commands when a PaperOS surface is focused and left to the webview otherwise.
* Accelerators come from PAP-153's `resolveBindings` formatted per platform (`CmdOrCtrl+K`), rebuilt on `keymap.changed`; conflicts with reserved OS accelerators are dropped with a dev warning; items whose `when(ctx)` is false are disabled, never removed (stable layout), re-evaluated on Tauri's `menu-will-open` with a 300 ms cache.
* Activation: Rust emits `menu.activate { id }`; the focused window's scope root (PAP-646, soft: main window until it lands) runs the command; results and errors surface as the same toasts the palette uses; telemetry `command.executed { source: 'menu' }` (PAP-291).
* Tray: two quick actions appended to PAP-255's Show and Quit, built from `agentCallable: false` commands flagged `menu.showIn: ['tray']`; clicking the icon toggles the main window (PAP-255 behaviour unchanged).
* Web and mobile adapters are no-ops with a test asserting they never call `invoke`; accessibility relies on native menus being screen-reader native, and every item mirrors a palette command so the web build loses nothing.

**Interface contract**

Provides: `buildMenuModel`, `NativeMenuAdapter` (Tauri and no-op), `set_menu_model` command, `menu.activate` event schema, tray action registration, `MenuPort` in `contract-input`. Consumes: manifest and execute endpoint (PAP-291), effective bindings (PAP-153), `menu` metadata (PAP-289 amendment, PAP-642), Tauri menu and tray scaffold (PAP-255), window routing (soft), sync status (PAP-272, soft). Consumed by PAP-257 (deep-link actions, soft), the app-shell desktop OS integration.

**Definition of done**

* Desktop build on Linux and macOS shows a Go menu whose accelerators change when the keymap preset changes; View → Toggle theme runs through the registry; recordings attached; Windows via PAP-371 or documented as untested.
* `docs/platform/input/native-menus.md`; changelog; Linear comment on PAP-255 and PAP-257.

**Test plan**

* Unit: menu model generation per platform (`Cmd` vs `Ctrl` labels, macOS app menu placement); `enabled` cache; reserved accelerator drop; tray action filter.
* Integration: `tauri-driver` smoke on Linux activates View → Toggle theme and asserts the DOM theme; `keymap.changed` triggers exactly one `set_menu_model` call.
* E2E: none on web (no-op adapter test only).

**Demo**

Reviewer opens the desktop build, switches the keymap to Linear and watches the Go menu accelerators change, picks Edit → Undo after a grid edit, and pauses sync from the tray. Under two minutes.

**Edge cases**

* Command hidden by `when`: item disabled, layout stable.
* Two windows: the menu targets the focused window; the Window menu lists them via PAP-262.
* Manifest changes at runtime (module enabled): menu rebuilt within one frame.
* Tray unsupported (some Linux desktops): quick actions hidden, PAP-255 fallback applies.

**Dependencies**

PAP-291 (hard), PAP-153 (hard), PAP-255 (hard, menu and tray scaffold). Soft: PAP-642, PAP-646, PAP-272, PAP-257. Blocks nothing.

**Agent**

Builder: Nova (Product Systems Engineer) with Forge (Tauri Smith) on Rust. Reviewer: Sentinel (Code Reviewer).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/app-shell/desktop-os-integration` = PAP-513, `r4/input/command-context-menus` = PAP-642, `r4/input/multi-window-command-and-focus-routing` = PAP-646.
