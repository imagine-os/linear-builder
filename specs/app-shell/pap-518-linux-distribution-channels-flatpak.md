---
identifier: "PAP-518"
title: "Linux distribution channels: Flatpak manifest on Flathub-compatible tooling, an apt repository served from the VPS and AppImage update feed integration"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P2"
type: "Infra"
priority: 4
surfaces: ["Customer"]
milestone: "Multi-monitor and PWA polish"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-25", "PAP-256"]
blocks: []
key: "r4/app-shell/linux-packaging"
url: "https://linear.app/paperos/issue/PAP-518/linux-distribution-channels-flatpak-manifest-on-flathub-compatible"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:53.703Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-518: Linux distribution channels: Flatpak manifest on Flathub-compatible tooling, an apt repository served from the VPS and AppImage update feed integration

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

Deferred to v0.2 (past 2026-10-01). PAP-256 produces `.deb`, `.rpm` and AppImage on a draft release and PAP-369 explicitly defers Linux signing. Kiosks (PAP-23) and staff Linux desktops need an install path that updates itself: an apt repository and a Flatpak are the two channels Linux users expect.

**Scope**

In:

* `ops/apt/`: `reprepro` repository served by Caddy at `https://apt.PAPEROS_DOMAIN`, GPG signing key in sops (PAP-25), publish step in the PAP-256 workflow, install snippet for the docs.
* `ops/flatpak/os.imagine.paperos.yml` manifest (`org.freedesktop.Platform` runtime, WebKitGTK), `flatpak-builder` job producing a bundle attached to the release; metainfo generated from `app.spec.yaml`.
* AppImage: `latest.json` (PAP-257) entries for `linux-x86_64` verified against the cosign signature (PAP-358); `.desktop` file and `MimeType=x-scheme-handler/paperos` shipped by every channel so deep links work from all three.
* Docs `docs/shell/linux-install.md`: apt, Flatpak and AppImage instructions, sandbox permissions table and the key rotation runbook.

Out: Snap, AUR, distro inclusion, Flathub submission (documented as a follow-up).

**Spec**

* apt repo signed; `apt-get update` verifies; key rotation runbook.
* Flatpak sandbox permissions minimal (`--share=network`, `--socket=wayland`, `--socket=fallback-x11`, `--talk-name=org.freedesktop.secrets`), listed in the docs.
* Kiosk recipe (PAP-23) uses the apt package.

**Interface contract**

Provides: apt repository, Flatpak manifest and bundle, install docs; consumed by PAP-23 (kiosk install), PAP-88 (release assets), PAP-29.

Consumes: installers workflow (PAP-256), host and Caddy (PAP-25), tags (PAP-52), signatures (PAP-358, soft), updater feed (PAP-257).

**Definition of done**

* Ubuntu 24.04 VM installs from the apt repo and receives an update on the next tag (recording); Flatpak bundle installs and launches.
* `docs/shell/desktop.md` Linux install section; CHANGELOG; Linear comment.

**Test plan**

* Unit: metainfo generation; repository publish script idempotency.
* E2E: CI: publish a test tag, `apt-get install` in a container, assert version.

**Demo**

Reviewer runs the two-line apt install on a fresh Ubuntu VM and launches PaperOS from the app grid. Under 2 minutes.

**Edge cases**

* Secret service missing inside Flatpak: PAP-17 encrypted-file fallback applies.
* Repo disk full on the VPS: publish fails loudly; disk alert from PAP-25.

**Dependencies**

Hard: PAP-256, PAP-25. Soft: PAP-52, PAP-358, PAP-257, PAP-23.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.
