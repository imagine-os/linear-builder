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
children: ["PAP-255", "PAP-256", "PAP-257"]
blockedBy: ["PAP-13"]
blocks: ["PAP-20", "PAP-21", "PAP-24", "PAP-262"]
key: "app-shell/tauri-desktop"
url: "https://linear.app/paperos/issue/PAP-19/add-tauri-2-desktop-target-for-linux-macos-and-windows-sharing-the-web"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:12:04.882Z"
---

# PAP-19: Add Tauri 2 desktop target for Linux, macOS and Windows sharing the web bundle

**Goal**

Umbrella: wrap the same web bundle in Tauri 2 so PaperOS apps ship as native, auto-updating desktop apps on Linux, macOS and Windows. Work is split into three children that can run in parallel after the first merges; this issue closes when the integration test below passes on a tagged build.

**Scope**

Children:

1. **PAP-255** — Tauri desktop scaffold, capabilities and plugins (`apps/desktop`, least-privilege capability files, menu, tray, dev scripts).
2. **PAP-256** — Desktop CI installers for Linux, macOS and Windows (`ops/ci/desktop.yml`, tauri-action, draft release, Rust lint).
3. **PAP-257** — Updater, single instance and deep links (`latest.json`, 0.0.1 to 0.0.2 proof, `paperos://` routing).

Out of the whole tree: code signing and notarisation (separate app-shell signing issue), mobile (PAP-20), window manager (PAP-21).

**Spec**

* `apps/desktop/src-tauri` is the single Cargo crate in the root workspace; `frontendDist` points at `apps/web/dist`, `devUrl` at Vite; desktop builds always use `BASE_PATH=/`.
* `identifier: os.imagine.paperos.<app>`; window 1280x800, min 960x600; `titleBarStyle: 'Overlay'` on macOS; CSP `default-src 'self'; connect-src https: wss:; img-src 'self' data: blob: https:`.
* Rust toolchain pinned in `rust-toolchain.toml`; `cargo clippy -D warnings` and `cargo fmt --check` in CI.
* Commands live in `src-tauri/src/commands/` (`app_info`, `open_path`, `secret_*` from PAP-17).
* Children own the detailed specs; this issue owns `docs/shell/desktop.md` and the integration test.

**Interface contract**

Provides:

* Tauri commands `app_info`, `open_path`, `list_displays` (stub, completed by PAP-21), `secret_*`; TS bridge `@paperos/core/native/desktop` exporting `isDesktop()`, `getVersion()`, `onDeepLink(cb)`.
* Deep-link scheme `paperos://open/<route>` handled by the router (PAP-57 uses `paperos://auth/callback`).
* Release artifacts on a draft GitHub release: `.deb`, `.rpm`, `.AppImage`, `.dmg`, `.msi`, `.nsis`, plus `latest.json` (Tauri updater format).
* Capability files under `src-tauri/capabilities/` that PAP-20 extends with `mobile.json`.

Consumes: `SecretStore` Rust commands (PAP-17), `UpdateToast` and `paperos:sw-updated` (PAP-18), CI secrets `TAURI_SIGNING_PRIVATE_KEY` (updater key, not OS signing) from PAP-25 sops.

**Definition of done**

* All three children Done.
* Integration test: tag `v0.0.2-test` produces installers for three OSes; a 0.0.1 install on Linux and macOS prompts to update to 0.0.2 and relaunches (recording).
* `docs/shell/desktop.md` covers prerequisites, dev loop, release; CHANGELOG; Linear comment with the release-draft link.
* Unsigned builds documented with the Gatekeeper and SmartScreen workaround until the signing issue lands.

**Test plan**

* Unit: Vitest for the TS bridge; `cargo test` for commands; `tauri` schema validation of capability files.
* Integration: `pnpm build:desktop` on ubuntu, macos and windows runners; installer smoke (`--version` output) on each.
* E2E: updater proof 0.0.1 to 0.0.2; single-instance test launching twice and asserting one process; deep-link test via `xdg-open paperos://open/settings`.
* Visual: window screenshots at 960x600, 1280x800, 1920x1080 on Linux and macOS.

**Demo**

Reviewer downloads the AppImage from the draft release, runs it, sees the web bundle with the version in `<BuildInfo/>`, runs `xdg-open paperos://open/settings` and watches the running instance navigate. Under 2 minutes.

**Edge cases**

* Wayland versus X11 tray and placement differences (tray may be absent on GNOME).
* Corporate proxy blocks the updater: log and retry silently.
* Close requested during a background task: intercept and confirm if dirty.
* Windows without install-dir write access: NSIS per-user mode.
* Hosted macOS runner minutes are billed at 10x: CI builds macOS only on tags and `workflow_dispatch`.

**Dependencies**

PAP-13 (hard). PAP-17 either order. Unblocks PAP-20, PAP-21, PAP-24, PAP-145, the signing issue.

**Agent**

Built by Forge (Tauri Smith). Reviewed by Sentinel (Security Auditor for capabilities and CSP, Code Reviewer for Rust).

**Size**

L as an umbrella; children are M, M, M.
