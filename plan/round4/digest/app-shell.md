# Round 4 digest: Universal App Shell & Repo Template (`app-shell`)

Benchmarks: Tauri 2 apps (Linear desktop, Arc, Zed); Electron apps (VS Code, Slack, Notion, Figma desktop); PWAs (Twitter Lite, Starbucks, Excalidraw); Create-T3 / Nx / Turborepo starter templates; Vercel and Coolify preview environments; Expo EAS and fastlane release pipelines.

Feature matrix: 69 rows, 51 covered, 6 partial, 12 gap. New issues: 21 (10 children of existing issues, 11 gap issues, 6 deferred to v0.2). Amendments to existing specs: 8. Cross-project suggestions: 5.

## Feature matrix

| Feature | Covered by | Status | Note |
|---|---|---|---|
| Monorepo scaffold: pnpm, Turborepo, strict TS, Biome, Vitest | PAP-13 | covered |  |
| React 19 + Vite web app with typed alias and CI check | PAP-13 | covered |  |
| File-based typed router with layout slots driven by page specs | PAP-16 | covered | Route-level lazy chunks per module missing (amendment). |
| Typed env and config layer per target | PAP-17 | covered |  |
| Client secret storage: browser session, OS keychain, mobile secure storage | PAP-17 | covered |  |
| Installable PWA, service worker, offline shell, install prompt | PAP-18 | covered | Per-tenant manifest on custom domains missing (amendment). |
| Update flow: SW update toast shared with the desktop updater | PAP-18, PAP-257 | covered |  |
| Desktop target Tauri 2: scaffold, capabilities, menu, tray | PAP-19, PAP-255 | covered |  |
| Desktop installers for three OSes from CI with draft release | PAP-256 | covered |  |
| Desktop auto-updater, single instance, paperos:// deep links | PAP-257 | covered | Update channels (stable/beta) missing (amendment). |
| Desktop OS integration: native notifications, badge, jump list, global shortcut | — | gap | Linear and Slack desktop table stakes; deferred to v0.2 (r4/app-shell/desktop-os-integration). |
| Desktop crash reporting: Rust panic hook, relaunch to last route | PAP-368 | partial | PAP-368 lists it as one bullet; Rust work split out (r4/app-shell/tauri-crash-reporting). |
| Desktop E2E automation (tauri-driver on Linux) | — | gap | Five issues cite "Tauri WebDriver" with no harness; r4/app-shell/tauri-e2e-harness. |
| Mobile targets iOS and Android from the shared crate, CI builds | PAP-20, PAP-258 | covered |  |
| Native capability shim with web fallbacks | PAP-259 | covered |  |
| Mobile plugins, safe areas, back button, keyboard, device proofs | PAP-260 | covered |  |
| Mobile universal links and Android app links | — | gap | Magic links must open the app; deferred (r4/app-shell/mobile-universal-links). |
| Native push registration APNs and FCM | PAP-381 | gap | PAP-381 is the connected-client transport only; deferred (r4/app-shell/native-push-registration). |
| Store distribution: TestFlight and Play internal lanes | PAP-369 | gap | PAP-369 signs; nothing uploads; deferred (r4/app-shell/store-distribution). |
| Code signing and notarisation | PAP-369 | covered |  |
| Linux distribution: apt repo, Flatpak | PAP-256 | gap | Deferred (r4/app-shell/linux-packaging). |
| Device matrix and seven-width breakpoints | PAP-14 | covered |  |
| Container-query breakpoints and layout hooks | PAP-261 | covered |  |
| Multi-monitor window manager: detach, dock, topology persistence | PAP-262 | covered | macOS recordings unverifiable from Linux (PAP-21 amendment). |
| Web pop-out fallback and panel affordances | PAP-263 | covered |  |
| Cross-window and cross-tab state coherence | PAP-145 | covered | realtime |
| Kiosk and multi-display signage mode | PAP-23 | covered | Deferred by schedule. |
| Shell layout persistence, session restore, named presets | PAP-262, PAP-260 | partial | Only detached windows and mobile route are persisted; r4/app-shell/shell-layout-presets. |
| Tabbed or split main area (multi-document workspace) | PAP-70 | gap | SplitPane exists in design-system; tabs deliberately not filed before 10-01; cross-project note. |
| Command bar slot and command palette | PAP-16, PAP-151, PAP-290 | covered | input |
| Keyboard shortcuts, keymaps, focus management | PAP-151, PAP-152, PAP-153 | covered | input |
| Notification centre in the shell | PAP-136, PAP-323 | covered | collab |
| Tenant switcher, customer portal and staff console shells | PAP-58, PAP-62, PAP-63 | covered | identity |
| Theming: light, dark, high contrast, tenant branding | PAP-75 | covered | design-system |
| Internationalisation, RTL, pseudo-locale, Intl helpers | PAP-27 | covered | Translation skill and catalog CI split out (r4/app-shell/i18n-translate-skill). |
| Client error boundaries, error catalogue, reporting | PAP-368 | covered |  |
| Client telemetry: web vitals, route timings, feature usage, consent | PAP-40, PAP-87, PAP-194 | gap | Server traces, lab Lighthouse and marketing attribution exist; no field RUM (r4/app-shell/client-telemetry). |
| Performance budgets and bundle size | PAP-87 | covered | quality; route-level code splitting amendment on PAP-16. |
| Web security headers and CSP | PAP-219, PAP-255 | partial | Baseline defined in PAP-219 and Tauri CSP in PAP-255; web image Caddyfile not wired (PAP-26 amendment). |
| Runtime feature flags per tenant and audience with kill switches | PAP-366 | covered | Settings page split out (r4/app-shell/flags-settings-page). |
| Maintenance mode and read-only degradation banner | PAP-267, PAP-272 | covered | Filed this round by data-layer as r4/data-layer/maintenance-mode (middleware, banner, CLI); app-shell duplicate withdrawn. |
| Deploy pipeline: images, staging on merge, production on tag, rollback | PAP-26 | covered |  |
| Per-PR preview environments with seeded demo tenant | PAP-26 | partial | One bullet in PAP-26 but consumed by five gates; child r4/app-shell/pr-preview-environments. |
| GitHub Pages static demos with PR previews | PAP-15 | covered |  |
| VPS, Coolify, Caddy, DNS, object storage, sops | PAP-25 | covered |  |
| Per-tenant custom domains with on-demand TLS | PAP-431 | covered |  |
| Public route prerendering, SEO and Open Graph | PAP-363, PAP-193 | gap | Head tags, OG image, sitemap and robots filed by spec-builder (r4/spec-builder/seo-public-metadata); static prerendering deferred (r4/app-shell/public-seo-prerender). |
| Module manifests and removable modules at generation and runtime | PAP-28, PAP-264, PAP-265, PAP-266 | covered |  |
| Package boundary map and dependency lint | PAP-305 | covered |  |
| `paperos create` CLI: clone, rename, push, provision | PAP-22 | covered | Linear seeding split out (r4/app-shell/cli-linear-seeding); `.paperos/template.json` not written (amendment). |
| Golden path driver with checkpoints | PAP-364 | covered |  |
| Golden path provisioning DAG and warm pools | PAP-365 | covered | Pool job split out (r4/app-shell/warm-pool-job). |
| Golden path acceptance test nightly | PAP-429 | covered | Depends on cleanup and fixtures that did not exist (r4/forge/repo-cleanup, r4/app-shell/template-fixture-repo). |
| Default surfaces starter kit and deterministic demo tenant | PAP-363 | covered | Seed split out (r4/app-shell/starter-kit-demo-seed). |
| First-run tenant onboarding wizard | PAP-367 | covered | Staff funnel split out (r4/app-shell/onboarding-funnel-admin). |
| `paperos upgrade` template upgrades with three-way merge | PAP-430 | covered | Registry publishing and codemods/fleet split out (two children). |
| Fixture template repository for CLI, upgrade and golden path tests | — | gap | Four issues assume it; r4/app-shell/template-fixture-repo. |
| Developer environment: devcontainer, one-command dev, toolchain doctor | PAP-22, PAP-42 | partial | Doctor checks tokens only; no composed dev command; r4/app-shell/dev-environment-bootstrap. |
| Repo template guide, CLAUDE.md, rules | PAP-24 | covered |  |
| Contract package, conformance suite, kernel wiring | PAP-447, PAP-450, PAP-453 | covered | PAP-453 variant naming inconsistency (amendment). |
| Blank-screen-to-running-app drill | PAP-29 | covered |  |
| Shell accessibility: skip links, focus, reduced motion, axe | PAP-152, PAP-72, PAP-73 | covered | input and design-system |
| Idle lock and shared-device mode | PAP-220 | gap | Kiosks and shared tablets; cross-project suggestion to identity. |
| Print stylesheet and PDF export | PAP-235, PAP-387 | covered | design-system and tables |
| In-app feedback and bug report to Linear with screenshot | PAP-137, PAP-307 | covered | collab and pm-linear |
| Recents and favourites navigation | PAP-151 | gap | Notion and Linear pattern; cross-project suggestion to input. |
| Local-first data persisted on desktop disk (PGlite on Tauri fs) | PAP-271 | partial | PGlite in IndexedDB only; cross-project suggestion to data-layer. |
| Health and version endpoints | PAP-26, PAP-269 | covered |  |
| Environment parity and test mode | PAP-17, PAP-240 | covered |  |

## New issues

| Key | Title | Parent | Type | Size | Model / effort | Priority | Milestone | Deferred |
|---|---|---|---|---|---|---|---|---|
| `r4/app-shell/upgrade-package-registry` | Publish `@paperos/*` packages to the Forgejo npm registry on every template tag with a GitHub Packages mirror and a generated-app `.npmrc` | PAP-430 | Infra P2 | M (3) | Sonnet 5 / medium | 2 | Multi-monitor and PWA polish (2026-09-29) |  |
| `r4/app-shell/upgrade-codemods-fleet` | Template codemod runner (`templates/codemods/<from>-<to>/*.ts`) and `paperos upgrade --fleet` listing every generated app and its template tag | PAP-430 | Build P2 | S (2) | Sonnet 5 / medium | 2 | Multi-monitor and PWA polish (2026-09-29) |  |
| `r4/app-shell/warm-pool-job` | Warm pool job: nightly `warm-pool.yml` and `paperos pool fill|drain|reconcile` keeping preview, database and mirror slots ready with `pool.json` state and a lease mutex | PAP-365 | Infra P1 | M (3) | Sonnet 5 / medium | 2 | Multi-monitor and PWA polish (2026-09-29) |  |
| `r4/app-shell/flags-settings-page` | Flags settings page `/settings/flags`: kill switches, per-tenant and per-audience overrides, rule editor with priority, audit trail and `flags.yaml` declaration status | PAP-366 | Build P1 | S (2) | Sonnet 5 / medium | 2 | Multi-monitor and PWA polish (2026-09-29) |  |
| `r4/app-shell/tauri-crash-reporting` | Tauri crash reporting: Rust panic hook and `tauri-plugin-log` forwarding to `/api/otel`, relaunch to the last route, crash-loop guard and offline report queue | PAP-368 | Build P1 | S (2) | Sonnet 5 / medium | 2 | Desktop and mobile shells build (2026-09-24) |  |
| `r4/app-shell/cli-linear-seeding` | `paperos create` Linear seeding: project with milestones, starter issues from `templates/linear/starter-issues.yaml`, module list in the project description and the `--json` step summary | PAP-22 | Build P1 | S (2) | Sonnet 5 / medium | 2 | Desktop and mobile shells build (2026-09-24) |  |
| `r4/app-shell/i18n-translate-skill` | Translation skill and catalog CI: `.claude/skills/translate` producing locale PRs, fuzzy-entry thresholds, missing-string report and the `en-XA` pseudo-locale column in Gate 3 | PAP-27 | Build P1 | S (2) | Sonnet 5 / medium | 2 | Desktop and mobile shells build (2026-09-24) |  |
| `r4/app-shell/pr-preview-environments` | Per-PR preview environments: `preview.yml`, Coolify preview application lifecycle, seeded demo tenant, sticky PR comment with URLs and teardown within five minutes of close | PAP-26 | Infra P0 | M (3) | Opus 5 / high | 1 | Desktop and mobile shells build (2026-09-24) |  |
| `r4/app-shell/onboarding-funnel-admin` | Onboarding funnel for staff: `/admin/onboarding` tenants by step reached, drop-off counts, resume nudges through the notification centre and the `onboarding.funnel` query | PAP-367 | Build P1 | S (2) | Sonnet 5 / medium | 3 | Multi-monitor and PWA polish (2026-09-29) |  |
| `r4/app-shell/starter-kit-demo-seed` | Deterministic demo tenant seed: `seedDemoTenant(db, appSpec)`, `paperos seed demo --reset`, faker-by-field-type with constraints and the production guard shared by `/__test/seed` | PAP-363 | Build P1 | S (2) | Sonnet 5 / medium | 1 | Multi-monitor and PWA polish (2026-09-29) |  |
| `r4/app-shell/tauri-e2e-harness` | Tauri WebDriver E2E harness: `tauri-driver` on Linux CI, test helpers for windows, deep links, updater and menu actions, and recorded runs attached to PRs | — | Infra P1 | M (3) | Opus 5 / high | 1 | Desktop and mobile shells build (2026-09-24) |  |
| `r4/app-shell/dev-environment-bootstrap` | Developer environment bootstrap: devcontainer, `pnpm setup`, `paperos dev` running compose, api, worker and web together, and `paperos doctor --toolchain` for Rust, Android and Xcode | — | Build P1 | M (3) | Sonnet 5 / medium | 2 | Desktop and mobile shells build (2026-09-24) |  |
| `r4/app-shell/client-telemetry` | Client telemetry: web vitals, route timings, feature-usage events and a consent gate flowing into `/api/otel` with per-tenant dashboards and a `useTrack()` hook | — | Build P1 | M (3) | Sonnet 5 / medium | 2 | Multi-monitor and PWA polish (2026-09-29) |  |
| `r4/app-shell/shell-layout-presets` | Shell layout presets and session restore: persisted panel sizes and collapse state per device, last route on launch, named presets synced per user and a Reset layout command | — | Build P1 | M (3) | Sonnet 5 / medium | 2 | Multi-monitor and PWA polish (2026-09-29) |  |
| `r4/app-shell/template-fixture-repo` | Fixture template repository `paperos-template-fixture` with pinned tags `t1`, `t2`, `t3` for CLI create, bootstrap, upgrade and golden path tests | — | Infra P1 | S (2) | Haiku 4.5 / low | 2 | Multi-monitor and PWA polish (2026-09-29) |  |
| `r4/app-shell/desktop-os-integration` | Desktop OS integration: native notifications with actions, dock and taskbar badge counts, jump-list and dock-menu recents, and a global shortcut that summons the command bar | — | Build P2 | S (2) | Sonnet 5 / medium | 4 | Multi-monitor and PWA polish (2026-09-29) | yes |
| `r4/app-shell/mobile-universal-links` | Mobile universal links and Android app links: `apple-app-site-association`, `assetlinks.json`, route handoff into the app, and a web smart banner for installed apps | — | Build P2 | S (2) | Sonnet 5 / medium | 4 | Multi-monitor and PWA polish (2026-09-29) | yes |
| `r4/app-shell/store-distribution` | Store distribution pipeline: TestFlight and Google Play internal testing lanes with fastlane, store metadata generated from `app.spec.yaml` and screenshots reused from Gate 3 | — | Infra P2 | M (3) | Sonnet 5 / medium | 4 | Multi-monitor and PWA polish (2026-09-29) | yes |
| `r4/app-shell/native-push-registration` | Native push registration (APNs and FCM) behind `NativeCapabilitiesPort.notify`, device token storage per principal and a bridge from the push transport to OS notifications | — | Build P2 | M (3) | Sonnet 5 / medium | 4 | Multi-monitor and PWA polish (2026-09-29) | yes |
| `r4/app-shell/public-seo-prerender` | Public route prerendering: build-time static HTML for `_public` routes with React 19 hydration checks, `noindex` on preview hosts, wired into the Pages build and the web image | — | Build P2 | S (2) | Sonnet 5 / medium | 4 | Multi-monitor and PWA polish (2026-09-29) | yes |
| `r4/app-shell/linux-packaging` | Linux distribution channels: Flatpak manifest on Flathub-compatible tooling, an apt repository served from the VPS and AppImage update feed integration | — | Infra P2 | S (2) | Sonnet 5 / medium | 4 | Multi-monitor and PWA polish (2026-09-29) | yes |

## Amendments to existing specs

* **PAP-16** (Spec): * Route contributions are lazy: each `RouteContribution` from a module manifest (PAP-264) is loaded with `React.lazy` so a module's code is absent from the initial chunk; `Link` prefetches on hover and focus; a `size-limit` entry for `apps/web` initial JS (under 180 KB gzipped) fails Gate 1 when a module leaks into it.
* **PAP-18** (Edge cases): * Custom domains (PAP-431): the manifest is served from `/manifest.webmanifest` per host with the tenant's name, colours and icons from `tenant.branding`, cached 1 h; `start_url`, `scope` and `id` follow the host. The service worker never caches `/api/sync/shape` (Electric, PAP-270) or any response carrying `Set-Cookie` or `X-PaperOS-Env: test`.
* **PAP-22** (Interface contract): * Writes `.paperos/template.json` `{ ref, tag, appliedAt, ownership: "templates/ownership.yaml" }` at creation (PAP-430 reads it and lists it as written here); the schema is co-owned with PAP-430. Step 9 (Linear project and starter issues) is delivered by `r4/app-shell/cli-linear-seeding`; the `--json` summary includes its `linearProject` block.
* **PAP-26** (Spec): * The `apps/web` image Caddyfile applies the PAP-219 header baseline: `Content-Security-Policy` with a per-response nonce for inline scripts, `Strict-Transport-Security`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` and `frame-ancestors 'none'` except on `/embed/*` (PAP-172); a header snapshot test in CI compares against `ops/security/headers.json`. Preview environments are owned by `r4/app-shell/pr-preview-environments`; this issue keeps staging, production and rollback.
* **PAP-257** (Spec): * Update channels: `latest.json` is published per channel at `channels/<stable|beta>/latest.json`; the desktop app reads its channel from `tenant.settings.desktopChannel` (staff can opt a tenant into `beta`) with `stable` as default; `checkForUpdate({ channel })` and a Settings toggle. The manifest signature is additionally verified with cosign once `r4/forge/supply-chain-provenance` lands.
* **PAP-21** (Definition of done): * Evidence rule for a Linux-only session: the Linux recording and the `r4/app-shell/tauri-e2e-harness` detach and dock test are mandatory; the macOS recording is produced by the PAP-371 hosted macOS job (`workflow_dispatch` with the recording script) or, if that runner is not yet available, recorded as a `pending-runner` finding on this issue with the exact command to run, never as a silent omission.
* **PAP-453** (Spec): * Flag variants: `module.app-shell.impl` declares `default`, `next` (the re-exporting stub built here) and `minimal` (the drill shell from PAP-446, bound only when `apps/web-minimal` exists); the Demo section's `minimal` flip therefore runs after PAP-446 binds it, and the merge-time demo uses `next`.
* **PAP-363** (Edge cases): * Idea paragraph yields zero entities (pure service business): the interview (PAP-360) proposes a `request` entity and the starter kit still generates the dashboard with a `ui.emptyState` block instead of failing codegen. * Starter pages pass the PAP-73 axe audit in Storybook before Gate 3 baselines are taken.

## Cross-project suggestions

* **identity**: Idle lock and shared-device mode: re-authenticate after inactivity, lock screen with passkey, per-tenant timeout, kiosk exemption. Shared tablets and kiosks (PAP-23) need it; sessions (PAP-220) own the policy, the shell only renders the lock.
* **input**: Recents and favourites: last opened records and pages per user, pinned favourites in the nav slot, surfaced in the command palette. Notion and Linear pattern; belongs with the command registry (PAP-151) and per-user keymaps sync (PAP-153).
* **data-layer**: PGlite persisted to disk on Tauri targets (file-backed instead of IndexedDB) with encryption at rest via the keychain key. Desktop and kiosk offline durability; PAP-271 targets browsers only.
* **design-system**: Tabbed and split main area components (`Tabs` workspace, `SplitPane` with persisted ratios) for multi-record work. VS Code and Linear multi-document pattern; the shell would persist it through r4/app-shell/shell-layout-presets. Not for 10-01.
* **quality**: Gate 3 captures desktop window screenshots (960x600, 1280x800, 1920x1080) through the Tauri E2E harness beside the seven browser widths. Desktop chrome, menus and detached panels are never screenshotted today; the harness (r4/app-shell/tauri-e2e-harness) makes it possible.

## What was missing and why it matters

* Nobody owned the test and developer infrastructure the shell issues assume: five issues cite a Tauri WebDriver harness, four assume a fixture template repo, three assume a cleanup command, and a cold session has no one-command dev environment; without them the DoDs are unverifiable from a Linux session.
* Per-PR preview environments were one bullet inside PAP-26 although five gates, the golden path and the vision agent all run against `pr-<n>.preview`; as a child with its own session they stop blocking on production tagging work.
* The shell forgets its own state: no layout persistence or session restore, no client telemetry (web vitals, feature usage) and, until this round, no maintenance mode (now filed by data-layer as `r4/data-layer/maintenance-mode`; the app-shell duplicate was withdrawn); Linear, VS Code and Arc treat all three as table stakes.
* Eight specs contradicted each other or a document: PAP-430 reads `.paperos/template.json` that PAP-22 never writes, PAP-453's demo flips a `minimal` variant its scope does not declare, PAP-21 demands macOS recordings a Linux session cannot produce, and PAP-26's web image applies none of the PAP-219 headers.
* Native reach past 10-01 is now explicit rather than missing: universal links, APNs/FCM push, store lanes, Linux packaging and desktop OS integration are filed as deferred v0.2 issues with real specs instead of being absent from the plan.
