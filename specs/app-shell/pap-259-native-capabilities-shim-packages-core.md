---
identifier: "PAP-259"
title: "Native capabilities shim (packages/core/native) with web fallbacks"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: "PAP-20"
children: []
blockedBy: ["PAP-17", "PAP-258"]
blocks: ["PAP-260"]
key: "child/PAP-20/4"
url: "https://linear.app/paperos/issue/PAP-259/native-capabilities-shim-packagescorenative-with-web-fallbacks"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T06:22:35.093Z"
---

# PAP-259: Native capabilities shim (packages/core/native) with web fallbacks

**Goal**

Define the `Capabilities` interface and `useCapability()` hook with `NativeCapabilities` and `WebCapabilities` implementations selected by `getTarget()`, so app code calls one API for camera, haptics, biometrics, secure storage, share, geolocation and notifications and degrades gracefully on web.

**Scope**

In: `packages/core/src/native/capabilities.ts`, `web.ts` (Web Share, `navigator.vibrate`, WebAuthn, MediaDevices, Geolocation API, Notification API), `native.ts` stubs wired by child 3, `useCapability(name)`, status model.

Out: plugin wiring (child 3), UI components.

**Spec**

* `Capability = { available: boolean; status: 'granted'|'denied'|'prompt'|'unavailable'; request(): Promise<Status>; openSettings?(): Promise<void> }`.
* `useCapability('camera')` re-renders on status change; never throws on web.
* `secureStore` delegates to PAP-17 `SecretStore`.
* Selection by `getTarget()`; tests inject a fake target.

**Interface contract**

Provides: `Capabilities`, `CapabilityName`, `useCapability`, `getCapabilities()` from `@paperos/core/native`. Consumes: `getTarget()` and `SecretStore` (PAP-17). Consumed by PAP-154 (haptics), PAP-157, PAP-37 (camera uploads), PAP-57 (biometrics).

**Definition of done**

* All seven capabilities implemented for web with correct `available` detection.
* Vitest covering each web fallback and target selection; Storybook story of a capability status panel.
* Types exported and documented in `docs/shell/mobile.md`.

**Test plan**

* Unit: per capability, mocked browser APIs present and absent; `request()` denial path; `useCapability` re-render on permission change.
* Type: `CapabilityName` exhaustive test.
* Visual: status panel story at 375 and 1280.

**Demo**

Reviewer opens the Storybook capability panel in a browser, sees Share and Geolocation available, Biometrics unavailable, clicks Request on Geolocation and watches the status change. Under a minute.

**Edge cases**

* `navigator.share` exists but `canShare` false for files: `available:false` for file shares.
* Permissions API missing (Safari): status `prompt` until requested.

**Dependencies**

PAP-17 (hard). Blocks child 3.

**Agent**

Built by Forge. Reviewed by Sentinel.

**Size**

S
