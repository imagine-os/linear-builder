---
identifier: "PAP-256"
title: "Desktop CI installers for Linux, macOS and Windows via tauri-action with draft release"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P0"
type: "Infra"
priority: 1
surfaces: ["Developer"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: "PAP-19"
children: []
blockedBy: ["PAP-255"]
blocks: ["PAP-257"]
key: "child/PAP-19/1"
url: "https://linear.app/paperos/issue/PAP-256/desktop-ci-installers-for-linux-macos-and-windows-via-tauri-action"
source: "Linear snapshot 2026-09-17T06:03Z (round-2 issue)"
---

# PAP-256: Desktop CI installers for Linux, macOS and Windows via tauri-action with draft release

**Goal**

Produce `.deb`, `.rpm`, `.AppImage`, `.dmg`, `.msi` and `.nsis` installers from CI on tags and manual dispatch, attached to a draft GitHub release together with the updater's `latest.json`, so desktop releases are reproducible without a developer laptop.

**Scope**

In: `ops/ci/desktop.yml` using `tauri-apps/tauri-action` on ubuntu-22.04, macos-14 and windows-2022; Rust cache; artifact upload; draft release creation; `latest.json` generation with the updater signing key from sops (this is the Tauri updater key, not OS code signing); Forgejo portability notes.

Out: OS code signing and notarisation (app-shell signing issue), updater client logic (child 3).

**Spec**

* Trigger: `push` tags `desktop-v*` (PAP-52 format) and `workflow_dispatch`; macOS jobs only on these triggers to control minutes.
* Matrix builds `apps/web` once and shares `dist` as an artifact to the three OS jobs.
* Secrets `TAURI_SIGNING_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` from repository secrets set by PAP-51.
* `latest.json` includes platform entries for `linux-x86_64`, `darwin-aarch64`, `darwin-x86_64`, `windows-x86_64` with signatures.
* Job summary lists artifact names, sizes and sha256.
* Forgejo: workflow runs on Linux only there; macOS and Windows depend on the forge non-Linux runner issue and are `if`-guarded.

**Interface contract**

Provides: release asset names `<app>_<version>_<arch>.<ext>`, `latest.json` URL `https://github.com/imagine-os/<repo>/releases/latest/download/latest.json` consumed by child 3 and PAP-88; workflow `desktop.yml` copied by PAP-22. Consumes: crate (child 1), tag format (PAP-52), secrets (PAP-51, PAP-25), portability checker (PAP-50).

**Definition of done**

* Tag `desktop-v0.0.1-test` yields all six installers on a draft release with valid `latest.json`; the tag is then deleted.
* Each installer launches on its OS (Linux and macOS recorded; Windows via CI smoke `--version`).
* No-change rebuild under 12 minutes on Linux; job summary with checksums.

**Test plan**

* Workflow: dispatch run on a branch; assert six assets and `latest.json` schema via a small script.
* Smoke: install `.deb` on ubuntu runner and run `paperos-desktop --version`; open `.dmg` on macOS runner; `msiexec /quiet` on Windows then run `--version`.
* Static: `check-workflow-portability.ts` passes with the OS jobs guarded.
* Size: installers under 30 MB compressed each.

**Demo**

Reviewer opens the draft release, downloads the AppImage, `chmod +x` and runs it, then opens `latest.json` in the browser and matches the version. Under 2 minutes.

**Edge cases**

* Unsigned macOS build: Gatekeeper workaround documented until the signing issue lands.
* Rust cache miss on macOS: build under 25 minutes still passes.
* Draft release already exists for the tag: assets replaced, not duplicated.

**Dependencies**

Child 1 (hard), PAP-52 tag format (soft), PAP-51 secrets (soft). Blocks child 3.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel.

**Size**

M
