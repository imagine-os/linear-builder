---
identifier: "PAP-19"
title: "Add Tauri 2 desktop target for Linux, macOS and Windows sharing the web bundle"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: ["PAP-255", "PAP-257", "PAP-256"]
blockedBy: ["PAP-13"]
blocks: ["PAP-20", "PAP-21", "PAP-24", "PAP-262"]
key: "app-shell/tauri-desktop"
url: "https://linear.app/paperos/issue/PAP-19/add-tauri-2-desktop-target-for-linux-macos-and-windows-sharing-the-web"
source: "plan/specs/bucket-0.json (round-1 canonical spec JSON)"
---

# PAP-19: Add Tauri 2 desktop target for Linux, macOS and Windows sharing the web bundle

**Goal**

Wrap the same web bundle in Tauri 2 so PaperOS apps ship as signed, auto-updating native desktop apps on Linux, macOS and Windows with real OS windows, menus and file access. This is the foundation `app-shell/breakpoints-windows` and `app-shell/linux-kiosk` build on.

**Scope**

In:
- `apps/desktop/` Tauri 2.x project (`src-tauri/` Cargo crate in the root Cargo workspace) pointing `frontendDist` at `apps/web/dist` and `devUrl` at Vite.
- Capabilities (`src-tauri/capabilities/*.json`) with least privilege: `core:window`, `core:event`, `shell:open` (allowlist https), `dialog`, `fs` scoped to app data dir, `updater`, `notification`, `os`, `process`.
- Plugins: `tauri-plugin-window-state`, `tauri-plugin-updater`, `tauri-plugin-dialog`, `tauri-plugin-fs`, `tauri-plugin-shell`, `tauri-plugin-os`, `tauri-plugin-single-instance`, `tauri-plugin-deep-link` (`paperos://` scheme).
- Native menu (File, Edit, View, Window, Help) and tray icon with Show/Quit.
- CI workflow `ops/ci/desktop.yml` building `.deb`, `.rpm`, `.AppImage`, `.dmg`, `.msi`/`.nsis` via `tauri-apps/tauri-action`, signing with keys from secrets, uploading to a GitHub Release draft and `latest.json` for the updater.
- `packages/core/src/native/` bridge: `isTauri()`, `invoke` wrappers, `openExternal()`, `getVersion()`, typed events.

Out: mobile (`app-shell/tauri-mobile`), multi-window manager (`app-shell/breakpoints-windows`), app-store submission, notarised macOS build if Apple credentials are absent (document the step).

**Spec**

- `tauri.conf.json`: `identifier: os.imagine.paperos.<app>`, `bundle.active`, `windows[0]` 1280x800 min 960x600, `decorations` native, `titleBarStyle: 'Overlay'` on macOS, CSP `default-src 'self'; connect-src https: wss: <API>; img-src 'self' data: blob: https:`.
- Updater: pubkey in config, endpoints `https://github.com/imagine-os/<repo>/releases/latest/download/latest.json`; check on launch and every 6 h; UI via `<UpdateToast/>` from `app-shell/pwa` reused.
- Rust commands: `app_info`, `secret_*` (from `app-shell/env-config`), `open_path`. Commands live in `src-tauri/src/commands/`.
- Single instance: second launch focuses existing window and forwards deep link.
- Deep link `paperos://open/<route>` navigates the router.
- Dev script `pnpm dev:desktop` runs Vite and `tauri dev` concurrently; `pnpm build:desktop`.
- Rust toolchain pinned in `rust-toolchain.toml` (stable 1.8x); `cargo clippy -D warnings` and `cargo fmt --check` in CI.
- Linux deps documented (`libwebkit2gtk-4.1`, `libappindicator3`).

**Definition of done**

- CI produces installers for all three OSes on a tag; artifacts attached to a draft release; `latest.json` valid.
- App launches, loads the web bundle, shows the version from `getVersion()` in `<BuildInfo/>`.
- Updater tested by publishing 0.0.1 then 0.0.2 and observing the prompt (recording attached).
- Vitest for the TS bridge; Rust tests for commands; capability files pass `tauri` schema validation.
- Screenshots at window sizes 960x600, 1280x800, 1920x1080 on Linux and macOS (Windows via CI screenshot step if available).
- `docs/shell/desktop.md` covers prerequisites, signing, releasing; CHANGELOG entry; Linear comment with release-draft link.

**Edge cases**

- Unsigned macOS build shows Gatekeeper warning: document `xattr -d` workaround and the notarisation TODO.
- Wayland vs X11 differences in window placement and tray (tray may be absent on GNOME without extension).
- Corporate proxy blocking updater endpoint: fail silently, log, retry later.
- Web bundle expects `/pr/<n>/` base path: desktop build must use `BASE_PATH=/`.
- Window closed while a background task runs: intercept `CloseRequested`, confirm if dirty.
- User has no write access to install dir on Windows: NSIS per-user install mode.

**Dependencies**

`app-shell/monorepo-scaffold` (hard). `app-shell/env-config` for keychain commands (can merge in either order). Unblocks `app-shell/tauri-mobile`, `app-shell/breakpoints-windows`, `app-shell/template-docs`, `realtime/multi-window-sync`.

**Agent**

Built by Forge (Tauri Smith sub-agent). Reviewed by Sentinel (Security Auditor for capabilities and CSP, Code Reviewer for Rust).

**Size**

L: three OS toolchains, signing and an updater that must work first time in CI.
