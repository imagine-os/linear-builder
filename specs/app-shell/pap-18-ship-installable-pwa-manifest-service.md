---
identifier: "PAP-18"
title: "Ship installable PWA manifest, service worker and offline app shell"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Template scaffolds and runs on web"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13", "PAP-15"]
blocks: ["PAP-600"]
key: "app-shell/pwa"
url: "https://linear.app/paperos/issue/PAP-18/ship-installable-pwa-manifest-service-worker-and-offline-app-shell"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:21:45.656Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-20"
cycle: null
---

# PAP-18: Ship installable PWA manifest, service worker and offline app shell

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Make the web build installable in any browser and load its shell instantly offline, so customers on flaky connections and staff on shared tablets get an app-like experience without a store download. Offline data sync is PAP-36 and PAP-148; this is the shell only.

**Scope**

In:

* `vite-plugin-pwa` 1.x with Workbox 7 `generateSW` in `apps/web`.
* Manifest: name, short name, theme colours from tokens, 192/512 and maskable icons, screenshots, `display: standalone`, `display_override`, shortcuts for three routes, `id`.
* Precache of HTML, JS, CSS, fonts, icons; runtime caching for API (`NetworkFirst`, 10 s), images (`CacheFirst`, 30 days, 200 entries), fonts (`StaleWhileRevalidate`).
* `registerType: 'prompt'` with `<UpdateToast/>` in `packages/ui`; `<OfflineBanner/>` in `packages/ui` (moved from `core/pwa` so codegen's `ui.offlineBanner` from PAP-120 resolves).
* `useInstallPrompt()` with an iOS instructions sheet.

Out: push transport, offline writes, native updater (PAP-19 reuses the toast).

**Spec**

* `VitePWA({ registerType:'prompt', manifest, workbox:{ navigateFallback:'index.html', navigateFallbackDenylist:[/^\/api/], globPatterns, maximumFileSizeToCacheInBytes: 3_000_000, cleanupOutdatedCaches: true, runtimeCaching }, devOptions:{ enabled:false } })`.
* `BASE_PATH` propagates to `start_url`, `scope` and `id` so `/pr/12/` never hijacks `/pr/13/`.
* `pnpm gen:icons` from `packages/ui/assets/logo.svg` via `@vite-pwa/assets-generator`.
* `packages/core/src/pwa/`: `useServiceWorker()` (`needRefresh`, `offlineReady`, `update()`), `useOnline()` (navigator plus heartbeat), `useInstallPrompt()`.
* `skipWaiting` only after the user accepts; `clients.claim()` on activate.
* `<meta name="theme-color">` bound to light and dark tokens; Apple meta tags.
* `ops/ci/lighthouserc.json` asserting installability (feeds PAP-87).

**Interface contract**

Provides:

* Hooks `useServiceWorker`, `useOnline`, `useInstallPrompt` from `@paperos/core/pwa`; components `UpdateToast`, `OfflineBanner` from `@paperos/ui` (the `ui.offlineBanner` target for PAP-120 codegen).
* Cache names `paperos-api-v1`, `paperos-img-v1`, `paperos-font-v1`; `/api/auth/*` and any response with `Set-Cookie` are never cached (PAP-57 relies on this).
* Event `paperos:sw-updated` on `window` for PAP-19's updater to share the toast.

Consumes: `BASE_PATH` (PAP-13), Pages preview URLs (PAP-15) for scope testing, colour tokens (PAP-66; placeholders until merged).

**Definition of done**

* DevTools Application panel shows the manifest without warnings; Lighthouse installability passes on the preview.
* Playwright: load, `setOffline(true)`, reload, shell renders with `<OfflineBanner/>`; online hides it.
* Update toast appears between two builds with a bumped constant.
* Install recorded on Chrome desktop, Android Chrome and iOS Safari.
* Screenshots at all seven widths of standalone mode and the banner; `docs/shell/pwa.md`; CHANGELOG; Linear comment.

**Test plan**

* Unit: `useOnline` with mocked `navigator.onLine` and heartbeat failures; install-prompt 14-day dismissal logic.
* Integration: Vitest with `vite-plugin-pwa` config snapshot asserting `scope` and `id` follow `BASE_PATH`.
* E2E: Playwright offline reload test; second-build update-toast test; assert `/api/auth/session` is `no-store` via the SW.
* Visual: banner and toast at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark.
* Lighthouse CI on the preview URL.

**Demo**

Reviewer opens the Pages preview in Chrome, clicks Install, launches the standalone window, toggles DevTools offline, reloads and sees the shell with the offline banner; toggles online and the banner disappears. Under 90 seconds.

**Edge cases**

* iOS 50 MB quota: `purgeOnQuotaError: true` on image cache.
* Dismissed install prompt: no re-ask for 14 days.
* SW on localhost breaks HMR: `devOptions.enabled=false`.
* Stale precache after a failed deploy: `cleanupOutdatedCaches`.
* Browsers without SW: hooks return safe defaults.

*Round 4 amendment (2026-09-18):*

* Custom domains (PAP-431): the manifest is served from `/manifest.webmanifest` per host with the tenant's name, colours and icons from `tenant.branding`, cached 1 h; `start_url`, `scope` and `id` follow the host. The service worker never caches `/api/sync/shape` (Electric, PAP-270) or any response carrying `Set-Cookie` or `X-PaperOS-Env: test`.

**Dependencies**

PAP-13 (hard), PAP-15 (scope testing, now encoded as blocks). Soft: PAP-66 tokens.

**Agent**

Built by Forge. Reviewed by Sentinel (Visual Inspector for install UI).

**Size**

S: mostly configuration plus three hooks and two components.
