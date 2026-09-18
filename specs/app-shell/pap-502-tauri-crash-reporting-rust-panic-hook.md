---
identifier: "PAP-502"
title: "Tauri crash reporting: Rust panic hook and `tauri-plugin-log` forwarding to `/api/otel`, relaunch to the last route, crash-loop guard and offline report queue"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-16", "PAP-17", "PAP-255", "PAP-368"]
blocks: ["PAP-548"]
key: "r4/app-shell/tauri-crash-reporting"
url: "https://linear.app/paperos/issue/PAP-502/tauri-crash-reporting-rust-panic-hook-and-tauri-plugin-log-forwarding"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:49:45.881Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-24"
cycle: null
---

# PAP-502: Tauri crash reporting: Rust panic hook and `tauri-plugin-log` forwarding to `/api/otel`, relaunch to the last route, crash-loop guard and offline report queue

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-368 defines `reportError` and the boundary for the web layer; native crashes need Rust work that a TypeScript session should not block on. This child wires the Tauri side so a desktop or mobile crash produces the same report shape as a browser error and the app comes back where the user was.

**Scope**

In:

* `apps/desktop/src-tauri/src/crash.rs`: `std::panic::set_hook` capturing message, location and a backtrace (release builds with `debug = 1`), writing `crash-<ts>.json` to the app data dir before exit; `tauri-plugin-log` targets stdout and a rolling file (5 MB, 3 files).
* TS bridge `packages/core/src/native/crash.ts`: on launch, read pending crash files through the `crash_drain` command, convert to the PAP-368 `AppError` envelope (`code: NATIVE_PANIC`, `fingerprint`), send through `reportError`, delete on success.
* Relaunch: `tauri-plugin-process` relaunch after a panic with `--restore-route=<last route>` read from the PAP-262 store; the shell navigates there and shows a toast "PaperOS restarted after a crash" with copy diagnostics.
* Crash-loop guard: three panics within 60 s disables relaunch, opens on `/` with the sidebar collapsed and offers "reset local state".
* Rust unit tests with a mocked transport; capability `crash_drain` limited to the main window.

Out: browser error capture and the catalogue (PAP-368), server error mapping (PAP-267), alert rules (PAP-40).

**Spec**

* Reports carry `target` (`desktop|ios|android`), app version, OS and the topology hash (PAP-262) but never the window contents or secrets.
* PII scrub with the PAP-40 denylist before send; file paths are reduced to the crate-relative form.
* Offline: crash files stay on disk until sent; capped at 20 files, oldest dropped.
* Mobile: the same hook compiled under the mobile features; on iOS the backtrace is symbolicated in CI with the dSYM from PAP-258 builds when available, otherwise raw.

**Interface contract**

Provides: command `crash_drain`, `--restore-route` argv, `NATIVE_PANIC` code in `errors.yaml`, rolling log location documented for support; consumed by PAP-368 (envelope), PAP-40 (dashboards), PAP-29 (drill friction evidence).

Consumes: crate and capabilities (PAP-255), `reportError` and `AppError` (PAP-368), window store (PAP-262, soft), collector (PAP-40, soft).

**Definition of done**

* Recording on Linux: trigger a test panic from a dev command, app relaunches on the same route with the toast, report visible in the collector with `NATIVE_PANIC`.
* Three forced panics in a minute open the safe mode; `cargo test` and Vitest green; `docs/shell/errors.md` native section; CHANGELOG; Linear comment.

**Test plan**

* Unit: Rust: hook writes a file with message and location; drain returns and deletes; loop guard counts within the window.
* Unit: TS: crash file to `AppError` mapping, scrub of a path containing a username.
* E2E: Tauri WebDriver (PAP-508) on Linux: invoke `__test_panic`, assert relaunch and toast.

**Demo**

Reviewer runs the desktop build, triggers `paperos://open/__test/panic` (dev builds only), watches the app close and reopen on the same page with the restart toast, then finds the report in Grafana Explore by fingerprint. Under 90 seconds.

**Edge cases**

* Panic inside the panic hook (allocation failure): hook is re-entrancy guarded and falls back to stderr.
* App data dir unwritable: report kept in memory for the relaunch only.
* Relaunch loop on a corrupt store: the guard resets the PAP-262 store after the third restart with a visible note.

**Dependencies**

Hard: PAP-255. Soft: PAP-368 (envelope; a local shape until it merges), PAP-262, PAP-40, PAP-508 for the automated proof.

**Agent**

Builder: Forge (Tauri Smith). Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/app-shell/tauri-e2e-harness` = PAP-508.

*Round 4 critique fix (2026-09-18):* de-parented from PAP-368 (FIX-R4-1: this issue is an add-on to its former parent's core scope, which is a claimable leaf again). PAP-368 blocks this issue (`blocks` relation).
