# Child issues for the L-sized parents. Each: parent, title, type, size, sections.
# Phase label and milestone are inherited from the parent. State: Backlog.
CHILDREN = []

def add(parent, title, type_, size, surfaces, **s):
    CHILDREN.append(dict(parent=parent, title=title, type=type_, size=size, surfaces=surfaces, sections=s))

# ---------------- PAP-19 Tauri desktop ----------------
add("PAP-19", "Tauri desktop scaffold, capabilities and plugins (apps/desktop, menu, tray, dev scripts)", "Build", "M", ["Developer"],
Goal="""Create `apps/desktop` as a Tauri 2 project wrapping `apps/web/dist`, with least-privilege capability files, the plugin set the shell needs, a native menu and tray, and dev scripts, so the other PAP-19 children and PAP-20 build on a running desktop app.""",
Scope="""In: `src-tauri` crate in the root Cargo workspace; `tauri.conf.json`; capabilities `main.json` (`core:window`, `core:event`, `shell:open` https allowlist, `dialog`, `fs` scoped to app data, `notification`, `os`, `process`); plugins `window-state`, `dialog`, `fs`, `shell`, `os`; menu (File, Edit, View, Window, Help); tray with Show and Quit; commands `app_info`, `open_path`; mount PAP-17 `secret_*`; `pnpm dev:desktop`, `pnpm build:desktop`; `rust-toolchain.toml`; Linux deps documented.

Out: CI installers (child 2), updater, single instance, deep links (child 3), signing.""",
Spec="""* `frontendDist: ../../web/dist`, `devUrl: http://localhost:5173`; desktop always builds the web bundle with `BASE_PATH=/`.
* Window 1280x800, min 960x600, native decorations, `titleBarStyle: 'Overlay'` on macOS.
* CSP `default-src 'self'; connect-src https: wss:; img-src 'self' data: blob: https:`.
* TS bridge `packages/core/src/native/desktop.ts`: `isDesktop()`, `getVersion()`, `appInfo()`.
* `<BuildInfo/>` shows `getVersion()` when running in Tauri.
* `cargo clippy -D warnings`, `cargo fmt --check` wired into Gate 1 for `apps/desktop`.""",
**{"Interface contract": """Provides: crate `paperos-desktop`, capability file layout, command names `app_info`, `open_path`, the TS bridge above, scripts `dev:desktop` and `build:desktop`. Consumes: web build (PAP-13), `secret_*` commands (PAP-17), `UpdateToast` (PAP-18). Children 2 and 3 and PAP-20 add to this crate without restructuring it."""},
**{"Definition of done": """* `pnpm dev:desktop` opens the app on Linux and macOS showing the web bundle and version.
* Capability files pass `tauri` schema validation; no wildcard permissions.
* Menu and tray work (recording); Rust and TS tests green; `docs/shell/desktop.md` dev section written."""},
**{"Test plan": """* Rust: `cargo test` for `app_info` and `open_path` (rejects non-https and paths outside app data).
* TS: Vitest for the bridge with mocked `__TAURI_INTERNALS__`.
* Static: capability JSON schema check; clippy and fmt.
* Manual recorded: menu items, tray Show and Quit on Linux and macOS.
* Visual: window at 960x600, 1280x800, 1920x1080."""},
Demo="""Reviewer runs `pnpm dev:desktop`, sees the app window with the web bundle and version badge, opens the Help menu and clicks the tray icon to hide and show the window. Under a minute after compile.""",
**{"Edge cases": """* GNOME without tray extension: app still runs; tray absence logged.
* Wayland placement limits documented.
* Missing `libwebkit2gtk-4.1`: dev script prints the install command."""},
Dependencies="""PAP-13 (hard), PAP-17 (either order). Blocks children 2 and 3.""",
Agent="""Built by Forge (Tauri Smith). Reviewed by Sentinel (Security Auditor).""",
Size="""M""")

add("PAP-19", "Desktop CI installers for Linux, macOS and Windows via tauri-action with draft release", "Infra", "M", ["Developer"],
Goal="""Produce `.deb`, `.rpm`, `.AppImage`, `.dmg`, `.msi` and `.nsis` installers from CI on tags and manual dispatch, attached to a draft GitHub release together with the updater's `latest.json`, so desktop releases are reproducible without a developer laptop.""",
Scope="""In: `ops/ci/desktop.yml` using `tauri-apps/tauri-action` on ubuntu-22.04, macos-14 and windows-2022; Rust cache; artifact upload; draft release creation; `latest.json` generation with the updater signing key from sops (this is the Tauri updater key, not OS code signing); Forgejo portability notes.

Out: OS code signing and notarisation (app-shell signing issue), updater client logic (child 3).""",
Spec="""* Trigger: `push` tags `desktop-v*` (PAP-52 format) and `workflow_dispatch`; macOS jobs only on these triggers to control minutes.
* Matrix builds `apps/web` once and shares `dist` as an artifact to the three OS jobs.
* Secrets `TAURI_SIGNING_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` from repository secrets set by PAP-51.
* `latest.json` includes platform entries for `linux-x86_64`, `darwin-aarch64`, `darwin-x86_64`, `windows-x86_64` with signatures.
* Job summary lists artifact names, sizes and sha256.
* Forgejo: workflow runs on Linux only there; macOS and Windows depend on the forge non-Linux runner issue and are `if`-guarded.""",
**{"Interface contract": """Provides: release asset names `<app>_<version>_<arch>.<ext>`, `latest.json` URL `https://github.com/imagine-os/<repo>/releases/latest/download/latest.json` consumed by child 3 and PAP-88; workflow `desktop.yml` copied by PAP-22. Consumes: crate (child 1), tag format (PAP-52), secrets (PAP-51, PAP-25), portability checker (PAP-50)."""},
**{"Definition of done": """* Tag `desktop-v0.0.1-test` yields all six installers on a draft release with valid `latest.json`; the tag is then deleted.
* Each installer launches on its OS (Linux and macOS recorded; Windows via CI smoke `--version`).
* No-change rebuild under 12 minutes on Linux; job summary with checksums."""},
**{"Test plan": """* Workflow: dispatch run on a branch; assert six assets and `latest.json` schema via a small script.
* Smoke: install `.deb` on ubuntu runner and run `paperos-desktop --version`; open `.dmg` on macOS runner; `msiexec /quiet` on Windows then run `--version`.
* Static: `check-workflow-portability.ts` passes with the OS jobs guarded.
* Size: installers under 30 MB compressed each."""},
Demo="""Reviewer opens the draft release, downloads the AppImage, `chmod +x` and runs it, then opens `latest.json` in the browser and matches the version. Under 2 minutes.""",
**{"Edge cases": """* Unsigned macOS build: Gatekeeper workaround documented until the signing issue lands.
* Rust cache miss on macOS: build under 25 minutes still passes.
* Draft release already exists for the tag: assets replaced, not duplicated."""},
Dependencies="""Child 1 (hard), PAP-52 tag format (soft), PAP-51 secrets (soft). Blocks child 3.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel.""",
Size="""M""")

add("PAP-19", "Desktop updater, single-instance guard and paperos:// deep links", "Build", "M", ["Developer", "Customer"],
Goal="""Make installed desktop apps update themselves from `latest.json`, refuse duplicate instances by focusing the running one, and open `paperos://` links inside the app, proven by a 0.0.1 to 0.0.2 update recording.""",
Scope="""In: `tauri-plugin-updater` with pubkey in config, check on launch and every 6 h, UI via `<UpdateToast/>` and the `paperos:sw-updated` event convention from PAP-18; `tauri-plugin-single-instance` forwarding argv to the first instance; `tauri-plugin-deep-link` registering `paperos://` on all three OSes; router integration `paperos://open/<route>`.

Out: OS signing, delta updates.""",
Spec="""* Updater endpoint from child 2; failure to reach it logs and retries later, never blocks launch.
* `UpdateToast` shows version and release notes summary (from `feed.json`, PAP-52) with Reload and Later.
* Single instance: second launch sends argv over the plugin channel; first instance focuses and handles any deep link in argv.
* Deep link handler in `packages/core/src/native/desktop.ts`: `onDeepLink(cb)`; router navigates to the path after `open/`; unknown hosts (`paperos://auth/*`) are dispatched to registered handlers (PAP-57 registers `auth`).
* Windows registry and macOS `Info.plist` scheme registration through the plugin; Linux `.desktop` `MimeType=x-scheme-handler/paperos`.""",
**{"Interface contract": """Provides: `onDeepLink(cb)` and `registerDeepLinkHost(host, handler)` used by PAP-57 for the auth callback; `checkForUpdate()` for a Settings button; event `paperos:update-available`. Consumes: `latest.json` (child 2), toast (PAP-18), release notes feed (PAP-52, soft)."""},
**{"Definition of done": """* Install 0.0.1, publish 0.0.2, relaunch: toast appears, Reload installs and restarts on 0.0.2 (recording on Linux and macOS).
* Launching twice yields one process; `xdg-open paperos://open/settings` navigates the running app (recording).
* Vitest and Rust tests green; `docs/shell/desktop.md` release and deep-link sections written."""},
**{"Test plan": """* Rust: argv forwarding test; scheme registration presence checks per OS in CI.
* TS: Vitest for deep-link parsing (`open/`, `auth/`, malformed) and update-state reducer.
* E2E: updater proof with two test releases; single-instance test counting processes; deep link via `xdg-open` on Linux and `open` on macOS.
* Negative: updater endpoint blocked by a proxy; app launches and logs the failure."""},
Demo="""Reviewer launches the installed 0.0.1 app, sees the update toast for 0.0.2, clicks Reload, and after restart runs `xdg-open paperos://open/settings` to watch the app navigate. Under 2 minutes.""",
**{"Edge cases": """* Update downloaded but user picks Later: installs on next quit.
* Deep link while window is minimised: restore and focus.
* Corrupt `latest.json` signature: update refused, logged."""},
Dependencies="""Child 1 and child 2 (hard). Feeds PAP-57 auth callback.""",
Agent="""Built by Forge (Tauri Smith). Reviewed by Sentinel (Security Auditor for signature verification).""",
Size="""M""")

# ---------------- PAP-20 Tauri mobile ----------------
add("PAP-20", "Tauri mobile project init and CI builds (Android debug APK, iOS simulator app)", "Build", "M", ["Developer"],
Goal="""Initialise iOS and Android targets inside the shared `src-tauri` crate, hold platform assets in `apps/mobile`, and build a debug APK and an iOS simulator app in CI so mobile work has an executable baseline.""",
Scope="""In: `tauri android init` and `tauri ios init`; Gradle wrapper pinned, `minSdk 26`, `targetSdk 35`, ABIs arm64-v8a and x86_64; iOS deployment target 15.0; Info.plist usage strings; `apps/mobile` with icons, splash and scripts `dev:android`, `dev:ios`; workflow `ops/ci/mobile.yml` (Android on ubuntu, iOS on macos-14, `if`-guarded until the forge non-Linux runner issue lands); ADR recording the single-crate decision.

Out: plugins and shims (children 2 and 3), store signing.""",
Spec="""* `applicationId` and bundle id from `identifier`.
* Vite dev server bound to `0.0.0.0`; scripts print LAN IP and a QR.
* CI uploads `app-debug.apk` and `PaperOS.app` as artifacts on PRs touching `apps/` or `packages/core/src/native`.
* `docs/shell/mobile.md` toolchain section (Android Studio, Xcode, simulators).""",
**{"Interface contract": """Provides: crate mobile features, artifact names, scripts. Consumes: crate (PAP-19 child 1), macOS runner capacity (forge non-Linux runner issue)."""},
**{"Definition of done": """* Debug APK and simulator app build in CI; artifacts attached.
* App runs on Pixel 8 emulator and iPhone 15 simulator showing the web bundle (recording).
* ADR merged; docs toolchain section written."""},
**{"Test plan": """* CI: both builds green; `apkanalyzer` asserts ABIs and `minSdk`.
* Emulator smoke: `adb install` then `adb shell am start` and a screenshot; `xcrun simctl` install and launch on iOS.
* Visual: 375x812 and 768x1024 portrait screenshots."""},
Demo="""Reviewer downloads the APK artifact, installs it on an emulator with `adb install`, launches and sees the PaperOS shell. Under 2 minutes with an emulator running.""",
**{"Edge cases": """* Gradle download blocked: wrapper cached in CI.
* No macOS runner yet: iOS job skipped with an explanatory summary line, not a failure."""},
Dependencies="""PAP-19 child 1 (hard), forge non-Linux runner issue (iOS CI). Blocks children 2 and 3.""",
Agent="""Built by Forge (Tauri Smith). Reviewed by Sentinel.""",
Size="""M""")

add("PAP-20", "Native capabilities shim (packages/core/native) with web fallbacks", "Build", "S", ["Developer"],
Goal="""Define the `Capabilities` interface and `useCapability()` hook with `NativeCapabilities` and `WebCapabilities` implementations selected by `getTarget()`, so app code calls one API for camera, haptics, biometrics, secure storage, share, geolocation and notifications and degrades gracefully on web.""",
Scope="""In: `packages/core/src/native/capabilities.ts`, `web.ts` (Web Share, `navigator.vibrate`, WebAuthn, MediaDevices, Geolocation API, Notification API), `native.ts` stubs wired by child 3, `useCapability(name)`, status model.

Out: plugin wiring (child 3), UI components.""",
Spec="""* `Capability = { available: boolean; status: 'granted'|'denied'|'prompt'|'unavailable'; request(): Promise<Status>; openSettings?(): Promise<void> }`.
* `useCapability('camera')` re-renders on status change; never throws on web.
* `secureStore` delegates to PAP-17 `SecretStore`.
* Selection by `getTarget()`; tests inject a fake target.""",
**{"Interface contract": """Provides: `Capabilities`, `CapabilityName`, `useCapability`, `getCapabilities()` from `@paperos/core/native`. Consumes: `getTarget()` and `SecretStore` (PAP-17). Consumed by PAP-154 (haptics), PAP-157, PAP-37 (camera uploads), PAP-57 (biometrics)."""},
**{"Definition of done": """* All seven capabilities implemented for web with correct `available` detection.
* Vitest covering each web fallback and target selection; Storybook story of a capability status panel.
* Types exported and documented in `docs/shell/mobile.md`."""},
**{"Test plan": """* Unit: per capability, mocked browser APIs present and absent; `request()` denial path; `useCapability` re-render on permission change.
* Type: `CapabilityName` exhaustive test.
* Visual: status panel story at 375 and 1280."""},
Demo="""Reviewer opens the Storybook capability panel in a browser, sees Share and Geolocation available, Biometrics unavailable, clicks Request on Geolocation and watches the status change. Under a minute.""",
**{"Edge cases": """* `navigator.share` exists but `canShare` false for files: `available:false` for file shares.
* Permissions API missing (Safari): status `prompt` until requested."""},
Dependencies="""PAP-17 (hard). Blocks child 3.""",
Agent="""Built by Forge. Reviewed by Sentinel.""",
Size="""S""")

add("PAP-20", "Mobile plugin wiring, safe areas and device proofs (camera, haptics, biometrics, secure storage, share)", "Build", "M", ["Customer", "Developer"],
Goal="""Wire the Tauri mobile plugins behind the `NativeCapabilities` implementation, map safe-area insets to tokens, handle the Android back button and keyboard, and record the device proofs the parent's integration test needs.""",
Scope="""In: plugins `barcode-scanner`, `haptics`, `biometric`, `secure-storage`, `share`, `geolocation`, `notification`; capability file `mobile.json`; `--safe-*` CSS variables from `env(safe-area-inset-*)`; viewport meta; back-button mapping; route restore from `sessionStorage`; demo route `/_app/native-demo`.

Out: gesture system (PAP-154), push transport.""",
Spec="""* Each plugin exposed only through `NativeCapabilities`; no direct plugin imports outside `packages/core/src/native`.
* `mobile.json` grants plugins to the main window only with the minimal permission set per plugin.
* Back button: `history.back()`; at root show a confirm-exit sheet.
* Keyboard: `interactive-widget=resizes-content` verified on both WebViews.
* Demo route exercises every capability with status badges.""",
**{"Interface contract": """Provides: `NativeCapabilities` implementation, `--safe-top|right|bottom|left` tokens (PAP-70, PAP-154), demo route. Consumes: crate with mobile targets (child 1), shim (child 2), `SecretStore` (PAP-17)."""},
**{"Definition of done": """* Recording on Android emulator and iOS simulator: navigate three routes, scan a QR, trigger haptics, store and read a secret, share a link.
* Safe areas verified on a notch device screenshot; back button and keyboard behaviours recorded.
* `clippy -D warnings` with mobile features; Vitest for capability wiring."""},
**{"Test plan": """* Rust: mobile feature build in CI.
* E2E: Maestro flow on the emulator for the demo route; biometrics skipped with a note when unavailable.
* Visual: 375x812, 390x844, 768x1024 portrait and landscape, light and dark.
* Permission: camera denied path shows the settings deep link."""},
Demo="""Reviewer opens `/_app/native-demo` on the emulator, taps Scan to read a QR from a second screen, taps Buzz for haptics, saves a secret, kills and relaunches the app and reads it back. Under 2 minutes.""",
**{"Edge cases": """* Low-memory kill restores the route.
* Camera denied: settings deep link.
* Android 14 notification permission prompt handled."""},
Dependencies="""Children 1 and 2 (hard), PAP-17. Feeds PAP-154, PAP-37.""",
Agent="""Built by Forge (Tauri Smith). Reviewed by Sentinel (Security Auditor for plugin permissions).""",
Size="""M""")

# ---------------- PAP-21 breakpoints and windows ----------------
add("PAP-21", "Container-query breakpoints and layout hooks from the device matrix", "Build", "S", ["Developer"],
Goal="""Turn `BREAKPOINTS` from PAP-14 into `@container` CSS, Tailwind v4 theme variables and React hooks, and replace the interim media queries in `AppShell` so layout decisions depend on the container, not the viewport (which matters once panels detach).""",
Scope="""In: `packages/core/src/layout/breakpoints.css` generated by `pnpm gen:breakpoints`; container names `shell`, `sidebar`, `main`, `inspector`, `panel`; Tailwind plugin for `cq-md:` utilities; `useBreakpoint()`, `useContainerSize(ref)`; `AppShell` collapse rules migrated.

Out: window manager (child 2), web pop-out (child 3).""",
Spec="""* CSS custom properties `--bp-xs..--bp-3xl`; `@container shell (min-width: 1024px)` rules.
* Hooks use `ResizeObserver`; SSR-free; return stable values.
* PAP-82 Playwright config switches to `breakpoints.json` in this child.""",
**{"Interface contract": """Provides: `useBreakpoint`, `useContainerSize`, Tailwind utilities, CSS variables. Consumes: `BREAKPOINTS` (PAP-14), `AppShell` (PAP-16). Consumed by PAP-70, PAP-165, PAP-82."""},
**{"Definition of done": """* `AppShell` collapses by container width (Testing Library test with a narrow container inside a wide viewport).
* Generated CSS snapshot-tested; screenshots at seven widths unchanged from PAP-16 baselines.
* `docs/shell/windows.md` breakpoint section written."""},
**{"Test plan": """* Unit: hook values across the seven widths; generator snapshot.
* Integration: narrow container in wide viewport yields drawer mode.
* Visual: seven widths compared with PAP-16 baselines (zero diff expected)."""},
Demo="""Reviewer opens the preview, drags the inspector wider using the resize handle and watches the main area switch from three columns to two based on its own width, not the window. Under a minute.""",
**{"Edge cases": """* Zoom 150 percent: container widths shrink; rules still apply.
* Nested containers: `panel` queries never inherit `shell` rules."""},
Dependencies="""PAP-14, PAP-16 (hard). Blocks children 2 and 3.""",
Agent="""Built by Forge. Reviewed by Iris.""",
Size="""S""")

add("PAP-21", "Tauri WindowManager: detach, dock, list_displays and topology-hash persistence", "Build", "M", ["Staff", "Developer"],
Goal="""Implement the desktop `WindowManager` so any panel can detach into its own OS window, move across monitors, be remembered per display topology and re-dock, using Tauri `WebviewWindowBuilder` and a `list_displays` command.""",
Scope="""In: `packages/core/src/windows/manager.ts` (`detach`, `dock`, `list`, `focus`, `moveToDisplay`, `subscribe`); Rust `list_displays` returning `{ id, name, bounds, scale, primary }`; store `{ panels, presets }` Zod-validated with versioned migrations in `localStorage` plus `tauri-plugin-window-state`; route `/_window/$panelId` with a chrome-less layout; cap 12 windows.

Out: web fallback and panel header UI (child 3).""",
Spec="""* Topology hash = sorted `${name}:${w}x${h}@${scale}`; mismatch falls back to primary centre.
* Closing a detached window docks it; `dock()` from main closes the child.
* Heartbeat every 5 s detects crashed children and re-docks.
* Events over `BroadcastChannel('paperos-windows')` with `paperos:panel-state` payloads (PAP-145 extends).""",
**{"Interface contract": """Provides: `WindowManager`, `PanelState`, `list_displays` command, `/_window/$panelId` route, channel name and event. Consumes: crate (PAP-19), breakpoints (child 1), routes (PAP-16). Consumed by PAP-23 (display enumeration), PAP-145."""},
**{"Definition of done": """* Linux and macOS recordings: detach, move to display two, quit, relaunch on display two; unplug and relaunch recovers to primary.
* Vitest for hash, migrations and reducer; Rust test for `list_displays`.
* Two-display composite screenshot."""},
**{"Test plan": """* Unit: topology hash ordering; migration v1 to v2 fixture; reducer for detach, dock, crash re-dock; cap at 12.
* Rust: `list_displays` against a mocked monitor list.
* E2E: Tauri WebDriver on Linux for detach and dock.
* Manual recorded: two-display flows on Linux and macOS."""},
Demo="""Reviewer clicks Pop out on the inspector (button from child 3 or a temporary dev command), drags it to a second monitor, quits and relaunches; the inspector returns to that monitor. Under 90 seconds.""",
**{"Edge cases": """* Scale change at runtime: re-query on `scale-changed`.
* Wayland forbids positioning: persist size only.
* More than 8 windows: memory warning."""},
Dependencies="""PAP-19, child 1 (hard), PAP-16. Blocks child 3; feeds PAP-23, PAP-145.""",
Agent="""Built by Forge (Tauri Smith) with Nova on the channel contract. Reviewed by Sentinel.""",
Size="""M""")

add("PAP-21", "Web pop-out fallback, panel header affordances and windows documentation", "Build", "M", ["Staff", "Customer"],
Goal="""Give browsers the same pop-out experience with `window.open` popups mirrored over `BroadcastChannel`, add the Pop out and Dock affordances, keyboard shortcut and detached-window chips to the shell, and write `docs/shell/windows.md`.""",
Scope="""In: web `WindowManager` backend using popups and the shared channel; panel header buttons; `Ctrl/Cmd+Shift+P`; chips per detached panel in the main window; popup-blocked hint; docs.

Out: data coherence beyond panel state (PAP-145).""",
Spec="""* Same `WindowManager` interface, backend chosen by `getTarget()`.
* Popups open `/_window/<panelId>` with `noopener` off so the channel works; closing docks.
* Chips list detached panels with focus and dock actions.
* Shortcut registered through PAP-151 once it exists; plain listener until then.""",
**{"Interface contract": """Provides: web backend, header components `PanelHeader` with `PopOutButton` in `@paperos/ui`, docs. Consumes: manager (child 2), breakpoints (child 1), `AppShell` (PAP-16)."""},
**{"Definition of done": """* Playwright multi-page test: pop out, change a filter in the popup, main window mirrors it.
* Screenshots at seven widths with a detached chip visible; `docs/shell/windows.md` complete; CHANGELOG."""},
**{"Test plan": """* Unit: chip list reducer; popup-blocked detection.
* E2E: Playwright multi-page mirror test; blocked popup shows inline hint.
* Visual: seven widths, light and dark; keyboard shortcut announced to screen readers."""},
Demo="""Reviewer clicks Pop out on the sidebar in Chrome, a popup opens with the sidebar, changes a filter there and sees the main window follow; closing the popup docks it. Under a minute.""",
**{"Edge cases": """* Popup blockers: hint, panel stays docked.
* Popup navigated away by the user: main detects channel silence and docks."""},
Dependencies="""Children 1 and 2 (hard). Soft: PAP-151.""",
Agent="""Built by Forge with Iris on affordances. Reviewed by Sentinel (Visual Inspector).""",
Size="""M""")

# ---------------- PAP-28 modules ----------------
add("PAP-28", "Module manifest contract and registry (packages/core/modules)", "Build", "M", ["Developer"],
Goal="""Define `ModuleManifest`, `defineModule()` and the registry that loads manifests listed in `app.spec.yaml`, resolves dependencies and refuses unknown or incomplete sets, plus the lint rule banning direct imports across optional module boundaries and a `knip` baseline.""",
Scope="""In: Zod schema, registry, dependency resolver, route-collision detection, boundary lint rule, `knip` config; convert `shell`, `identity`, `data`, `design-system`, `spec`, `input`, `i18n` into core manifests and one optional example module.

Out: router and database integration (child 2), CLI and tenant toggles (child 3).""",
Spec="""* Manifest fields per the parent; `dependsOn` resolved topologically; cycles and missing deps fail at boot with module ids.
* `loadModules(appSpec): ResolvedModules` pure and synchronous for use in Vite config and the server.
* Lint rule reports import paths crossing from one optional module package to another unless listed in `dependsOn`.""",
**{"Interface contract": """Provides: `ModuleManifest`, `defineModule`, `loadModules`, `ResolvedModules`, lint rule `@paperos/no-cross-module-import`. Consumes: `app.spec.yaml` shape agreed with PAP-117; event bus `emit` (data-layer events issue) as the sanctioned coupling."""},
**{"Definition of done": """* Core manifests plus one optional example load; unit tests for resolver and collisions; lint rule fixtures; `knip` clean on the template.
* `docs/platform/modules.md` contract section written."""},
**{"Test plan": """* Unit: schema rejects unknown fields; resolver on chains, diamonds, cycles, missing; route collision names both modules.
* Static: lint rule passing and failing fixtures; `knip` in Gate 1.
* Type: `defineModule` infers `settingsSchema` type."""},
Demo="""Reviewer runs `pnpm modules:list` to print the resolved module graph, edits `app.spec.yaml` to disable `identity` and watches `pnpm dev` fail with "core module cannot be disabled". Under a minute.""",
**{"Edge cases": """* Two manifests with the same id from different packages: boot error.
* Optional module with no routes or entities: allowed."""},
Dependencies="""PAP-117 (shape), PAP-13. Blocks children 2 and 3.""",
Agent="""Built by Forge (Platform Engineer). Reviewed by Sentinel.""",
Size="""M""")

add("PAP-28", "Module integration: route tree, spec validator, permissions, jobs and per-module migrations", "Build", "M", ["Developer"],
Goal="""Make enabled modules the source of routes, navigation, permissions, jobs and migration sets: PAP-16 composes the route tree from manifests, the spec validator rejects references to disabled modules, PAP-59 loads `permissions`, PAP-43 registers `jobs`, and `db:migrate` applies `drizzle/<module>/*.sql` for enabled modules only.""",
Scope="""In: `composeRoutes(modules)` implementation; nav from `navItems`; validator rule in PAP-118; permission and job registration hooks; migration runner changes and `_migrations_modules` table; `pnpm db:check` module awareness.

Out: runtime toggles and CLI (child 3).""",
Spec="""* Route tree generated at build time by the Vite plugin from enabled modules; disabled module routes do not exist in the bundle.
* Validator error `MODULE_DISABLED` with module id and component or entity name.
* Migration runner records `(module_id, migration)`; disabled-module migrations already applied are ignorable in `db:check`.""",
**{"Interface contract": """Provides: `composeRoutes`, validator rule, `_migrations_modules` table, `registerModulePermissions`, `registerModuleJobs`. Consumes: registry (child 1), PAP-16, PAP-118, PAP-59, PAP-43, PAP-32."""},
**{"Definition of done": """* Template builds with route tree from manifests; a disabled optional module leaves no route in the bundle (assert by `grep` on `dist`).
* Validator test for `MODULE_DISABLED`; migration runner test on a fresh database; permissions and jobs registered (tests)."""},
**{"Test plan": """* Unit: `composeRoutes` on fixtures; validator fixture with a disabled module reference.
* Integration (CI compose): migrate with module A enabled, then disabled; `_migrations_modules` rows and `db:check` behaviour asserted.
* Build: bundle grep for a disabled module's route path returns nothing."""},
Demo="""Reviewer disables the example module in `app.spec.yaml`, runs `pnpm build` and `pnpm spec:validate` on a page using its component, reads the `MODULE_DISABLED` error, then runs `pnpm db:migrate` and sees the module's migrations skipped. Under 2 minutes.""",
**{"Edge cases": """* Migration of a disabled module previously applied: retained.
* Module adds a permission string already defined by core: boot error."""},
Dependencies="""Child 1 (hard), PAP-16, PAP-32, PAP-118, PAP-59, PAP-43 (soft). Blocks child 3.""",
Agent="""Built by Forge with Quill on validator wording. Reviewed by Sentinel.""",
Size="""M""")

add("PAP-28", "`paperos create --without`, tenant module toggles and the CI removal matrix", "Build", "M", ["Staff", "Developer"],
Goal="""Let apps omit modules at generation time and tenants toggle optional modules at runtime, with retained data, a Needs Justin gate on purge, and a CI matrix that removes each optional module in turn to prove the template stays green.""",
Scope="""In: `--without` in PAP-22 removing module packages and manifest entries; `tenant_module` table and `modules.list|toggle` procedures; settings page `/settings/modules`; runtime 404 and API rejection for disabled modules; `pnpm modules:purge <id>` with production gate; CI matrix workflow; module list written to the Linear project.

Out: entitlement pricing (PAP-178).""",
Spec="""* Toggle checks `dependsOn`; blocked with the dependency list in UI and API.
* Disabled at runtime: route returns not-found, nav item hidden, procedures return `MODULE_DISABLED`; data untouched.
* Purge requires `--tenant` and, in production, a Needs Justin issue link.""",
**{"Interface contract": """Provides: `tenant_module` table, `modules.*` procedures, `useModuleEnabled(id)`, settings page, CLI flag. Consumes: children 1 and 2, PAP-22, PAP-59 for the settings page permission."""},
**{"Definition of done": """* `paperos create demo --without payroll,crm,growth` builds and shows no CRM or payroll navigation (screenshots).
* CI matrix green for every optional module.
* Playwright: admin disables `canvas`, route 404s, API rejects, re-enable restores data; customer cannot open the settings page."""},
**{"Test plan": """* Unit: toggle dependency check; purge guard.
* Integration: `modules.toggle` as admin and as customer via `callAs`.
* E2E: Playwright toggle flow at 375 and 1280.
* CI: matrix job per optional module running `pnpm check`."""},
Demo="""Reviewer opens Settings, Modules, switches Canvas off, sees the nav item vanish and `/canvas` show not-found, switches it back on and the data is intact. Under 90 seconds.""",
**{"Edge cases": """* Tenant disables a module a business template requires: importer refuses or prompts.
* Two admins toggle concurrently: last write wins with an audit event."""},
Dependencies="""Children 1 and 2 (hard), PAP-22. Feeds PAP-29, PAP-207.""",
Agent="""Built by Forge with Iris on the settings page. Reviewed by Sentinel.""",
Size="""M""")

# ---------------- PAP-35 API ----------------
add("PAP-35", "API server, middleware chain and error mapping (apps/api on Hono 4)", "Build", "M", ["Developer"],
Goal="""Stand up `apps/api` hosting oRPC on Hono 4 with the full middleware chain: request id, logging, auth (signed dev token stub until PAP-57), tenant resolution, `withTenant` database context, error mapping, audit and OTel hooks, replacing the `healthz` stub from PAP-26.""",
Scope="""In: server bootstrap, middleware modules, `Principal` import from PAP-55, error code enum, context type, graceful shutdown, `statement_timeout`, 1 MB body limit, env from PAP-17, Dockerfile alignment with PAP-26.

Out: routers and client (child 2), docs and deploy (child 3), rate limiting (separate issue).""",
Spec="""* Middleware order fixed and tested: requestId, logger, auth, tenant, db, audit vars, otel, errorMap.
* Tenant from `x-tenant` header or subdomain; missing on tenant-scoped procedure is `VALIDATION` 400.
* RLS errors (`42501`) map to `NOT_FOUND` for reads, `FORBIDDEN` for writes.
* Dev token stub enabled only when `NODE_ENV !== 'production'` and `AUTH_DEV_TOKEN` set; test asserts production refuses.""",
**{"Interface contract": """Provides: `os` builder with `Context`, `tenantProcedure`, `publicProcedure`, `ApiErrorCode`, headers `x-request-id`. Consumes: `Principal` (PAP-55), `createDb`/`withTenant` (PAP-32), session vars (PAP-34, PAP-38), env (PAP-17)."""},
**{"Definition of done": """* Server runs locally against the PAP-42 stack; `/healthz` and `/__version` respond.
* Vitest for chain order, tenant resolution matrix, error mapping table, production guard.
* Structured logs include request id and tenant."""},
**{"Test plan": """* Unit: each middleware in isolation and the composed chain; error map from `ORPCError` and Postgres codes.
* Integration (CI compose): tenant-scoped call without header is 400; RLS denial mapped correctly; 1 MB body 413; slow query cancelled at 2 s.
* Security: `AUTH_DEV_TOKEN` in production mode refused at boot."""},
Demo="""Reviewer runs `pnpm dev:api`, calls `curl -H "x-tenant: acme" -H "authorization: Bearer $DEV_TOKEN" localhost:3000/api/v1/rpc/health` and then omits the tenant header to read the 400 message. Under a minute.""",
**{"Edge cases": """* Subdomain and header disagree: 400.
* Principal in several tenants: header required."""},
Dependencies="""PAP-33, PAP-32 (hard). Soft: PAP-34, PAP-55, PAP-17. Blocks children 2 and 3.""",
Agent="""Built by Forge. Reviewed by Sentinel (Security Auditor).""",
Size="""M""")

add("PAP-35", "API contract package, core routers and typed client with callAs test utility", "Build", "M", ["Developer"],
Goal="""Publish `packages/api-contract` (Zod from `drizzle-zod` plus DTOs, routers `tenants`, `workspaces`, `users.me`, `memberships`, `roles`, `files` stubs, `health`) and `packages/api-client` (`@orpc/client` fetch link, `@orpc/tanstack-query` utils, auth and tenant header injection, retry policy), plus `callAs(principal)` for tests.""",
Scope="""In: routers with `list|get|create|update|archive` convention and `{ cursor, limit, filter?: FilterTree, sort? }` inputs; `pnpm gen:api` stale check; client package; test utility; `users.me` on the dashboard example route.

Out: server chain (child 1), OpenAPI docs and deploy (child 3).""",
Spec="""* `filter` typed as `FilterTree` from the data-layer filter grammar issue; until it merges, `filter` is `unknown` with a TODO tracked there.
* Client: `createClient(baseUrl, { getToken, getTenant })`; retries only idempotent verbs.
* `callAs(fixture)` builds a context with a fake principal and a per-test tenant.""",
**{"Interface contract": """Provides: `AppRouter`, `createClient`, `orpc.*` query utils, `callAs`, DTO types. Consumes: server builder (child 1), Zod schemas (PAP-33). Consumed by PAP-119, PAP-163, PAP-36 and every business router."""},
**{"Definition of done": """* Every core router happy and forbidden path tested through `callAs`; wrong input fails typecheck (`expectTypeOf`).
* Dashboard renders `users.me`; screenshots at 375, 1024, 1920.
* `pnpm gen:api --check` green in Gate 1."""},
**{"Test plan": """* Unit: router handlers with fake db; pagination cursor round trip; client header injection and retry policy.
* Type: input inference tests.
* Integration (CI compose): `memberships.list` across two tenants never leaks.
* Visual: dashboard at three widths."""},
Demo="""Reviewer opens the dashboard on the preview pointed at a local API and sees their user name from `users.me`; in the terminal `pnpm test --filter api-contract` shows the forbidden-path tests. Under a minute.""",
**{"Edge cases": """* Cursor tampering: signed cursors rejected with `VALIDATION`.
* `limit` above 100 clamped."""},
Dependencies="""Child 1 (hard), PAP-33. Soft: filter grammar issue. Blocks child 3.""",
Agent="""Built by Forge. Reviewed by Sentinel (Code Reviewer).""",
Size="""M""")

add("PAP-35", "OpenAPI docs, health endpoints and staging deploy of apps/api", "Infra", "S", ["Developer"],
Goal="""Serve OpenAPI 3.1 and a Scalar docs page, expose `/api/health` with database check and build SHA, lint the spec in CI and deploy `apps/api` to staging through PAP-26 so the typed client has a live target.""",
Scope="""In: `/api/v1/openapi.json`, `/api/docs` (Scalar), `/api/health`, `redocly lint` in Gate 1, Coolify resource `paperos-staging-api`, `docs/data/api.md`.

Out: production hardening beyond PAP-26 defaults.""",
Spec="""* OpenAPI generated from oRPC metadata; versioned path `/api/v1`; breaking changes need an ADR.
* Health returns `{ ok, db: 'ok'|'fail', version, sha }` and 503 on db failure.
* Docs page disabled in production unless `API_DOCS=1`.""",
**{"Interface contract": """Provides: `/api/docs`, `/api/v1/openapi.json`, `/api/health` for PAP-40 checks and PAP-26 smoke tests; staging base URL for the client. Consumes: children 1 and 2, PAP-26 pipeline, PAP-30 staging database."""},
**{"Definition of done": """* `/api/health` and `/api/docs` reachable over TLS on staging (screenshot of Scalar at 1280).
* `redocly lint` green; `docs/data/api.md` written; Linear comment with the docs URL."""},
**{"Test plan": """* Unit: health handler with db up and down.
* Static: `redocly lint`; OpenAPI snapshot for breaking-change detection.
* Integration: PAP-26 smoke test hits health after deploy.
* Visual: Scalar page at 1280 and 375."""},
Demo="""Reviewer opens `https://staging.PAPEROS_DOMAIN/api/docs`, expands `users.me`, sends it with the dev token and tenant header from the Scalar console and reads the response. Under a minute.""",
**{"Edge cases": """* Database down: health 503, docs still render.
* Docs exposed in production by mistake: env guard test."""},
Dependencies="""Children 1 and 2 (hard), PAP-26, PAP-30.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel.""",
Size="""S""")

# ---------------- PAP-36 sync ----------------
add("PAP-36", "Electric service deployment and tenant-scoped shape proxy (/api/sync/shape)", "Build", "M", ["Developer"],
Goal="""Deploy the ElectricSQL sync service on staging connected directly to Postgres with the `electric` role, and add the `GET /api/sync/shape` proxy in `apps/api` that validates the session and injects `tenant_id = <principal tenant>` into every shape so clients can never request another tenant's rows.""",
Scope="""In: `ops/compose/electric.yml` and Coolify resource; publication `electric_pub`; proxy route with table allowlist from the shape registry; streamed responses; `SHAPE_FORBIDDEN` error; health from `/api/health`.

Out: client (child 2), outbox (child 3).""",
Spec="""* Proxy forwards `table`, `offset`, `handle`, `live`, `columns`; appends the server `where`; strips client-supplied `where`.
* Non-registered table: 403 `SHAPE_FORBIDDEN`.
* Response streamed with Electric headers preserved; `x-sync-schema-hash` added.""",
**{"Interface contract": """Provides: route and error, registry lookup `getShapeDefinition(table)`, env `ELECTRIC_URL`. Consumes: publication and role (PAP-30; PAP-42 locally), API chain (PAP-35 child 1), RLS semantics (PAP-34)."""},
**{"Definition of done": """* Electric on staging; health green.
* Cross-tenant shape request returns 403 (test); allowed shape streams rows for the caller's tenant only.
* `docs/data/sync.md` proxy section written."""},
**{"Test plan": """* Unit: query rewriting (client `where` stripped, tenant appended); allowlist.
* Integration (CI compose with Electric): stream a `workspaces` shape as tenant A and assert no tenant B rows; `live=true` long-poll returns a change within 2 s.
* Security: Sentinel reviews that the proxy never trusts client tenant hints."""},
Demo="""Reviewer runs `curl -N "$API/api/sync/shape?table=workspaces&offset=-1" -H "x-tenant: acme" -H "authorization: Bearer $TOKEN"` and watches rows stream, then requests `table=users_secret` and gets 403. Under a minute.""",
**{"Edge cases": """* Electric restart invalidates handles: client receives 409 and re-fetches (child 2).
* Slot lag: alert via PAP-40 when replication lag exceeds 30 s."""},
Dependencies="""PAP-35 child 1, PAP-30 or PAP-42, PAP-34 (hard). Blocks children 2 and 3.""",
Agent="""Built by Forge (Ops Runner and Platform Engineer). Reviewed by Sentinel (Security Auditor).""",
Size="""M""")

add("PAP-36", "PGlite client, schema generation and read hooks (useShape, useLiveQuery)", "Build", "M", ["Developer", "Customer"],
Goal="""Ship `packages/sync` client pieces: `defineShape`, the shape registry, `SyncClient` lifecycle, PGlite 0.3 with IndexedDB and Tauri file persistence, `pnpm gen:pglite` schema generation from Drizzle with hash-based reset, and `useShape` and `useLiveQuery` hooks.""",
Scope="""In: client package, generated `schema.sql`, hooks, persistence adapters, core shapes `workspaces`, `memberships`, `users`, `files`, demo route reads.

Out: proxy (child 1), writes (child 3).""",
Spec="""* `gen:pglite` emits SQL for registered tables only; hash stored in `_sync_meta`; mismatch resets local data, keeps `_outbox`.
* `useLiveQuery(sql, params)` over PGlite live extension; `useShape(shape)` returns `{ rows, status }`.
* Tauri persistence in app data dir; Android falls back per PAP-31 findings.""",
**{"Interface contract": """Provides: `defineShape`, `registerShape`, `useShape`, `useLiveQuery`, `SyncClient`, generated schema file. Consumes: proxy (child 1), ADR decision (PAP-31), `useOnline` (PAP-18). Consumed by PAP-143, PAP-163."""},
**{"Definition of done": """* Demo route lists workspaces from PGlite; bench of 2k-row initial load under 1.5 s on CI committed.
* Vitest for registry, hash reset, hooks; screenshots of the demo route at seven widths."""},
**{"Test plan": """* Unit: hash reset preserves outbox; hook states loading, ready, error.
* Integration (CI compose with Electric): full shape load into PGlite, live update after a server write appears within 2 s.
* Bench: 2k rows timed.
* Visual: demo route at seven widths."""},
Demo="""Reviewer opens `/_app/sync-demo`, sees workspaces load instantly on second visit, edits one in Drizzle Studio and watches the list update live. Under a minute.""",
**{"Edge cases": """* Safari private mode: in-memory PGlite with banner.
* Storage above 200 MB: warning and `columns` trimming advice."""},
Dependencies="""Child 1 (hard), PAP-31. Blocks child 3.""",
Agent="""Built by Forge with Nova. Reviewed by Sentinel.""",
Size="""M""")

add("PAP-36", "Offline write outbox, replay with backoff, leader election and SyncIndicator", "Build", "M", ["Customer", "Staff"],
Goal="""Add the write path: `mutate()` applies an optimistic update to PGlite and either calls oRPC directly or enqueues in `_outbox`; replay runs with exponential backoff under a `navigator.locks` leader; `<SyncIndicator/>` shows online, offline, syncing and error states; the demo route proves an offline edit survives reload and replays.""",
Scope="""In: `_outbox` table, `mutate()`, replay loop, failure UI (retry or discard), leader election, `useSyncStatus`, `SyncIndicator` in `@paperos/ui`, demo route edit flow.

Out: ordering guarantees across entities and conflict UX (PAP-148, PAP-143 extend).""",
Spec="""* Backoff 1 s to 60 s, 20 attempts, then `failed`.
* `FORBIDDEN` on replay: mark failed, show reason, roll back the optimistic row.
* Tombstones from shapes remove local rows; outbox writes against them fail cleanly.""",
**{"Interface contract": """Provides: `mutate`, `useSyncStatus`, `SyncIndicator`, `_outbox` schema. Consumes: hooks and PGlite (child 2), oRPC client (PAP-35 child 2). Consumed by PAP-148, PAP-143."""},
**{"Definition of done": """* Playwright: rename offline, reload, go online, replay succeeds (recording).
* Two tabs: only the leader replays.
* Vitest for state machine and backoff; `SyncIndicator` screenshots at 375, 768, 1280, 1920."""},
**{"Test plan": """* Unit: outbox transitions; backoff schedule; rollback on `FORBIDDEN`.
* E2E: offline edit and replay; leader election with two pages.
* Visual: four indicator states."""},
Demo="""Reviewer goes offline in DevTools, renames a workspace (indicator shows 1 pending), reloads, goes online and watches the indicator clear as the server row updates. Under 90 seconds.""",
**{"Edge cases": """* Expired handle after long offline: full re-fetch, outbox kept.
* Clock skew: server timestamps only."""},
Dependencies="""Child 2, PAP-35 child 2 (hard). Feeds PAP-143, PAP-148.""",
Agent="""Built by Forge with Nova (CRDT Engineer). Reviewed by Sentinel.""",
Size="""M""")

# ---------------- PAP-45 Forgejo ----------------
add("PAP-45", "Forgejo compose stack behind Caddy with hardened app.ini, accounts and org", "Infra", "M", ["Developer"],
Goal="""Bring Forgejo up on the PAP-25 host as a Coolify Docker Compose resource behind Caddy with TLS, its own Postgres, hardened `app.ini`, admin and service accounts, and the `imagine-os` org with `owners`, `agents`, `reviewers` teams.""",
Scope="""In: `ops/forgejo/docker-compose.yml`, `app.ini.tmpl`, Coolify resource, DNS `git.`, health check, accounts `justin` and `paperos-admin`, org and teams, container registry enabled, SSH 2222.

Out: backups (child 2), OIDC (child 3).""",
Spec="""* Image pinned by digest; `postgres:17-alpine` for Forgejo's database; named volumes.
* `app.ini` keys per parent, including `DEFAULT_ACTIONS_URL` and `[packages] ENABLED=true`.
* `paperos-admin` API token stored in `ops/secrets/forge.enc.yaml`.""",
**{"Interface contract": """Provides: `https://git.PAPEROS_DOMAIN`, API `/api/v1`, SSH 2222, registry path, `FORGEJO_ADMIN_TOKEN`, org and team names. Consumes: PAP-25 host, Caddy, DNS, sops, Resend SMTP."""},
**{"Definition of done": """* Landing page over valid TLS; `/api/healthz` 200; clone over HTTPS token and SSH from another network.
* Registration disabled; only two accounts; Sentinel confirms no plaintext secrets.
* Screenshots at 1280 and 375."""},
**{"Test plan": """* Unit: template render test; `docker compose config` validation.
* Integration: health, clone HTTPS and SSH from CI; sign-up returns 403.
* Security: `gitleaks` on the infra repo.
* Visual: landing page two widths."""},
Demo="""Reviewer opens the forge URL, logs in as `justin`, views the `imagine-os` org and teams, then clones a repo with a token. Under a minute.""",
**{"Edge cases": """* Traefik default proxy: switch to Caddy first.
* ACME rate limit: staging CA during retries."""},
Dependencies="""PAP-25 (hard). Blocks children 2 and 3, PAP-47, PAP-48, PAP-50.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor).""",
Size="""M""")

add("PAP-45", "Forgejo backups with restic and a timed restore drill into a scratch stack", "Infra", "S", ["Developer"],
Goal="""Back up Forgejo data and its database nightly with a `restic` sidecar to `paperos-backups/forgejo`, write a nightly snapshot manifest of repo heads, and prove `restore.sh` restores the latest snapshot into a scratch stack whose UI lists the same repos, with timing recorded.""",
Scope="""In: `forgejo-backup` sidecar (`forgejo dump` plus `pg_dump`, restic init and prune policy 14 daily, 8 weekly), `manifest.json` writer, `restore.sh <snapshot> <target-dir>`, read-only restore credential, failure alert to the orchestrator webhook.

Out: full DR drill on a fresh host (PAP-53).""",
Spec="""* Nightly 03:00 UTC; `restic forget --prune` weekly; `restic check` weekly.
* Manifest `{ snapshotAt, repos: [{ name, heads }] }` produced from the Forgejo API before the dump.
* Backup failure exits non-zero and POSTs to the orchestrator webhook.""",
**{"Interface contract": """Provides: repo path, `restore.sh`, `manifest.json` format, read-only credential name `RESTIC_RO_*`. Consumes: stack (child 1), bucket (PAP-25). Consumed by PAP-53 and the object-storage DR issue."""},
**{"Definition of done": """* First snapshot exists; `restore.sh` into `ops/forgejo/scratch` shows the same repos; timing in the runbook.
* Failure path tested with a bad credential (alert received)."""},
**{"Test plan": """* Unit: `bats` for `restore.sh` argument handling.
* Integration: snapshot, restore, compare repo lists via API; rotated credential produces a webhook POST.
* Timing recorded in `docs/runbooks/forgejo.md`."""},
Demo="""Reviewer runs `restic snapshots` against the forge repo, then `ops/forgejo/restore.sh latest /tmp/forgejo-scratch` and opens the scratch UI on a local port listing the repos. Under 2 minutes for a small forge.""",
**{"Edge cases": """* Bucket credentials rotated: loud failure.
* Restore of a newer Forgejo dump into an older image: version check refuses."""},
Dependencies="""Child 1 (hard), PAP-25. Feeds PAP-53.""",
Agent="""Built by Forge (Ops Runner). Reviewed by Sentinel (Edge Case Hunter).""",
Size="""S""")

add("PAP-45", "OIDC auth source preparation, upgrade procedure and Forgejo runbook", "Docs", "S", ["Developer"],
Goal="""Prepare the Better Auth OIDC login path in Forgejo (auth source `paperos`, auto-registration, group mapping to teams) so PAP-57 can switch it on with one command, and write `docs/runbooks/forgejo.md` covering deploy, upgrade with pre-snapshot, backup, restore, SSO switch and monitoring.""",
Scope="""In: `ops/forgejo/oidc.sh` creating or updating the auth source via `forgejo admin auth add-oauth`, expected issuer and scopes documented, team mapping JSON, runbook, metrics scrape hint for PAP-40.

Out: the identity provider itself (PAP-57).""",
Spec="""* Issuer `https://app.PAPEROS_DOMAIN/api/auth`; scopes `openid email profile groups`; `group_claim_name: groups`; mapping `paperos:staff` to `agents`, `paperos:owner` to `owners`.
* Script idempotent; `--disable` flag for rollback.""",
**{"Interface contract": """Provides: auth source name, expected claims, `oidc.sh`. Consumes: stack (child 1). Consumed by PAP-57 (OIDC provider child)."""},
**{"Definition of done": """* `oidc.sh --dry-run` prints the planned auth source; real run against staging creates a disabled source.
* Runbook merged with all six sections; Sentinel reviews the SSO section."""},
**{"Test plan": """* Unit: `bats` for script flags.
* Integration: source appears in admin UI disabled; `--disable` removes login button.
* Docs: `docs:check` link validation."""},
Demo="""Reviewer reads the runbook's SSO section, runs `oidc.sh --dry-run` and sees the exact `forgejo admin auth` command that PAP-57 will enable. Under a minute.""",
**{"Edge cases": """* Claims missing `groups`: users land in no team; documented.
* Upgrade requiring migration: pre-snapshot step mandatory."""},
Dependencies="""Child 1 (hard). Soft: PAP-57, PAP-40.""",
Agent="""Written by Forge with Quill. Reviewed by Sentinel (Security Auditor).""",
Size="""S""")

# ---------------- PAP-54 in-app git ----------------
add("PAP-54", "Forge client, oRPC forge.* procedures and forge.read permission checks", "Build", "M", ["Developer", "Agent"],
Goal="""Build `packages/forge-client` on the generated Forgejo client from PAP-51 and expose read-only oRPC procedures `forge.repos.list|tree|file|commits|commit` and `forge.pulls.list|get`, each guarded by `can(actor, 'forge.read', { repo })`, with SHA-keyed caching, so the pages in the other children have a permission-safe backend.""",
Scope="""In: client wrapper, DTO mappers, trailer parser for `Linear:` and `Character:`, cache with 30 s staleness for membership filtering, server-side `bot-scout` class token.

Out: pages (children 2 and 3).""",
Spec="""* Token never leaves the server; procedures reject when the actor lacks `forge.read`.
* Cache key includes the ref's current SHA fetched cheaply first.
* `CommitDto.linearKeys` parsed from trailers; `author.character` from the PAP-48 identity convention.""",
**{"Interface contract": """Provides: procedures and DTOs, permission action `forge.read` registered with PAP-59, `packages/forge-client`. Consumes: Forgejo API (PAP-45), generated client (PAP-51), token (PAP-48), API host (PAP-35), `can()` (PAP-59)."""},
**{"Definition of done": """* `callAs(customer)` forbidden on every procedure; developer sees only permitted repos.
* Integration tests against a Forgejo fixture container; trailer parser fixtures."""},
**{"Test plan": """* Unit: DTO mappers; trailer parser; cache key logic.
* Permission: `callAs` matrix for customer, developer, agent.
* Integration (CI compose): fixture Forgejo with two repos and one private."""},
Demo="""Reviewer calls `forge.repos.commits` from the Scalar console as a developer and gets commits with `linearKeys`, then as a customer and gets 403. Under a minute.""",
**{"Edge cases": """* Forgejo unreachable: procedures return `UNAVAILABLE` with last cached payload flag.
* Force-push: cache key changes."""},
Dependencies="""PAP-45, PAP-35, PAP-51 (hard). Soft: PAP-48, PAP-59. Blocks children 2 and 3.""",
Agent="""Built by Forge. Reviewed by Sentinel (Security Auditor).""",
Size="""M""")

add("PAP-54", "Repo list, file tree, file view and commit-list pages with specs", "Build", "M", ["Developer", "Agent"],
Goal="""Add specs and routes `/dev/repos`, `/dev/repos/$repo`, `tree/$ref/$path` and `commits/$ref` using PAP-16 slots (sidebar repo and branch picker, main content, inspector linked issue and spec panel), lazily loading one directory per request and highlighting files with `shiki`.""",
Scope="""In: four page specs with `access: { audiences: [developer, agent] }`, routes, components `RepoPicker`, `FileTree`, `FileView`, `CommitList`, mocked fixture for the Pages demo.

Out: diff and PR pages (child 3).""",
Spec="""* Tree loads one directory per request; breadcrumbs.
* Ref with slashes via splat route with safe encoding.
* `EmptyState` with retry when the backend is unavailable.""",
**{"Interface contract": """Provides: routes, components in `@paperos/ui`, specs passing PAP-118. Consumes: procedures (child 1), slots (PAP-16), `EmptyState` and avatars (PAP-71)."""},
**{"Definition of done": """* Four pages render against live Forgejo and against the mock on Pages; screenshots at seven widths light and dark.
* Specs validate; conformance tests generated; Lighthouse above 85 on the commits page at 1280."""},
**{"Test plan": """* Unit: breadcrumb and ref encoding.
* E2E: Playwright with mocked data at seven widths; ref `release/2026-09-25`; Forgejo-down state.
* Performance: Lighthouse on commits page."""},
Demo="""Reviewer opens `/dev/repos`, picks `paperos-template`, browses to `packages/core/src/index.ts`, then opens the commit list on `main`. Under a minute.""",
**{"Edge cases": """* 50,000 files: lazy directories.
* Binary file view: size and download link only."""},
Dependencies="""Child 1, PAP-16 (hard). Soft: PAP-71, PAP-118. Blocks child 3.""",
Agent="""Built by Forge with Nova's Views team advising. Reviewed by Sentinel (Visual Inspector).""",
Size="""M""")

add("PAP-54", "Commit diff view, pull request pages and Linear trailer links", "Build", "M", ["Developer", "Agent"],
Goal="""Complete the surface with `/dev/repos/$repo/commit/$sha`, `pulls` and `pulls/$n`: a `DiffView` handling binary, rename and mode changes with horizontal scroll inside the diff at 320, `CommitLink` and `PAP-n` links in the inspector, character avatars for agent commits, and the mocked public demo.""",
Scope="""In: three page specs and routes, `DiffView` and `CommitLink` in `@paperos/ui`, inspector panel showing linked Linear issue and spec files touched, docs page `docs/product/in-app-git.md`.

Out: review comments (PAP-131 later), merging.""",
Spec="""* Diff parser fixtures for binary, rename, mode change, huge minified line.
* Linear link uses the workspace URL from PAP-91 config.
* Inspector lists `specs/**` files in the diff with links to the spec editor when PAP-124 exists.""",
**{"Interface contract": """Provides: `DiffView`, `CommitLink` reusable by PAP-131 and PAP-89; routes. Consumes: procedures (child 1), pages scaffolding (child 2)."""},
**{"Definition of done": """* Three pages render live and mocked; `Linear:` trailer link works; agent commit shows the character avatar.
* Diff fixtures pass; screenshots at seven widths; docs page and changelog; Linear comment with the Pages demo link."""},
**{"Test plan": """* Unit: diff parser fixtures; link builder.
* E2E: Playwright at seven widths; wide diff line at 320 shows no page overflow.
* Visual: light and dark for diff view."""},
Demo="""Reviewer opens a commit by "Forge (PaperOS agent)", reads the highlighted diff, clicks the `PAP-n` link in the inspector to reach Linear, then opens the PR list. Under a minute.""",
**{"Edge cases": """* Commit without trailer: inspector says no linked issue.
* PR from a bot with hundreds of files: file list virtualised."""},
Dependencies="""Children 1 and 2 (hard). Soft: PAP-91, PAP-124.""",
Agent="""Built by Forge. Reviewed by Sentinel (Visual Inspector).""",
Size="""M""")
