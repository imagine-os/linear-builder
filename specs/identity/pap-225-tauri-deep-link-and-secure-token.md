---
identifier: "PAP-225"
title: "Tauri deep-link and secure-token session flow"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: "PAP-57"
children: []
blockedBy: ["PAP-223"]
blocks: []
key: "identity/better-auth/tauri-session"
url: "https://linear.app/paperos/issue/PAP-225/tauri-deep-link-and-secure-token-session-flow"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:04:36.750Z"
---

# PAP-225: Tauri deep-link and secure-token session flow

**Goal**

Make the same sign-in work inside Tauri 2 on Linux and macOS: OAuth and magic links complete in the system browser, return through `paperos://auth/callback`, exchange a one-time token for a bearer session stored in the OS keychain, and survive restarts.

**Scope**

* In: deep-link registration and handling (`tauri-plugin-deep-link`), one-time token exchange endpoint `/api/auth/token`, bearer storage through the `SecretStore` interface (`tauri-plugin-stronghold` desktop, secure-storage shim mobile), client transport switch, passkey capability detection with magic-link fallback, restart persistence, startup URL handling.
* Out: web cookies (sibling), mobile store submission (PAP-20 owns).

**Spec**

* Server: `POST /api/auth/token/exchange { code }` accepts a 60-second single-use code minted at the end of OAuth or magic-link completion when the request carried `client=tauri`; returns a bearer token bound to the device name.
* Client: `authClient` gains `transport: 'bearer'` when `window.__TAURI__` exists; token read from `SecretStore.get('auth.token')` on boot, written on exchange, cleared on sign-out; `Authorization: Bearer` on every API call.
* Deep link: register scheme `paperos` in `tauri.conf.json`; handler routes `auth/callback?code=…` both at runtime and from the launch arguments (cold start).
* Passkeys: `PublicKeyCredential` undefined on WebKitGTK; the sign-in form hides the passkey button and opens the system browser for magic link or OAuth.

**Interface contract**

* Provides: `/api/auth/token/exchange`, `SecretStore` usage contract (`auth.token`), `openExternalAuth(url)` helper.
* Requires: PAP-19 desktop scaffold and deep-link plugin, PAP-17 `SecretStore` interface, sibling server child.

**Definition of done**

* Linux and macOS dev builds sign in via GitHub OAuth in the system browser and land back signed in; app restart keeps the session (video).
* Cold-start deep link (app closed) signs in correctly (test via `xdg-open paperos://…`).
* Token never appears in logs or the URL bar after exchange (grep test).
* Sign-out clears the keychain entry (assert `SecretStore.get` is null).

**Test plan**

* Unit: transport selection, code expiry and single use.
* Integration: exchange endpoint replay returns 400 `CODE_USED`.
* Manual on both OSes with recording; Windows noted as untested until a runner exists.

**Demo**

`pnpm tauri dev`, click "Continue with GitHub", finish in the browser, watch the desktop window flip to signed in; quit and relaunch, still signed in. Under two minutes.

**Edge cases**

* Deep link arrives with no pending sign-in: ignored with a toast.
* Keychain locked or unavailable: fall back to in-memory session with a warning banner.
* Two windows: token shared through the store; sign-out broadcasts via BroadcastChannel.

**Dependencies**

Sibling server child (hard), PAP-19 (hard for the desktop shell). Soft: PAP-20.

**Agent**

Built by Forge (Tauri Smith sub-agent). Reviewed by Sentinel (Security Auditor).

**Size**

M.
