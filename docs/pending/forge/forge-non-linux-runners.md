---
key: "gap/forge/non-linux-runners"
title: "Provision non-Linux CI capacity: hosted macOS runners (Xcode, VoiceOver) and a Windows VM runner (NVDA, MSI signing) with cost caps and secrets"
project: "forge"
parent: null
phase: "P1"
type: "Infra"
priority: 2
size: null
surfaces: []
milestone: null
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/gaps-pending-0.json (agent0/gaps.py)"
linearDocument: null
status: "pending"
---

# Provision non-Linux CI capacity: hosted macOS runners (Xcode, VoiceOver) and a Windows VM runner (NVDA, MSI signing) with cost caps and secrets

**Goal**

Provide the runners PAP-19, PAP-20, PAP-156 and PAP-73 silently require: GitHub-hosted macOS runners for Xcode builds, notarisation and VoiceOver checks, and a self-hosted Windows VM registered to both forges for NVDA screen-reader tests and MSI signing, with spend caps and the secrets each needs. PAP-50 sizes Linux docker runners only; iOS builds and screen-reader CI cannot run anywhere today.

**Scope**

In:

* GitHub: `macos-14` usage policy (tags and `workflow_dispatch` only, plus a nightly a11y job), spending limit set in org billing, reusable workflow `imagine-os/paperos-infra/.github/workflows/macos-job.yml` with Xcode selection and simulator boot; cost report job posting monthly minutes to Linear.
* Windows: Hetzner Windows Server VM (or a Windows 11 VM on a dedicated host) with the GitHub runner and Forgejo runner both installed as services, labels `windows-self-hosted`, NVDA installed with the `nvda-remote` speech viewer for PAP-156, `signtool`, PowerShell scripts for reset between jobs.
* Secrets: signing (code-signing issue) and Apple keys wired; `ops/forge/secrets-manifest.yml` updated.
* Portability notes added to PAP-50's guide; `if` guards pattern for jobs that need these runners.

Out: buying Apple accounts (code-signing issue files the ask), Android emulator capacity (Linux with KVM in PAP-50).

**Spec**

* macOS budget: 300 minutes per week; jobs fail fast if the monthly cap is within 10 percent.
* Windows VM snapshot restored nightly; runner ephemeral mode for GitHub; Forgejo runner `capacity: 1`.
* NVDA speech log captured to an artifact for PAP-156 assertions.
* All non-Linux jobs skip cleanly on Forgejo when the label is absent.

**Interface contract**

Provides: labels `macos-14` (hosted) and `windows-self-hosted`, reusable macOS workflow, NVDA speech-log artifact name `nvda-speech.log`, secrets names in the manifest, monthly cost report. Consumes: Forgejo runner registration (PAP-50), secrets (PAP-51), Hetzner project (PAP-25), signing keys (code-signing issue, soft). Consumed by PAP-19 child 2, PAP-20 child 1, PAP-73, PAP-156, code-signing issue.

**Definition of done**

* iOS simulator build (PAP-20) and macOS installer (PAP-19) jobs run green on hosted macOS with the cost cap in place (run URLs).
* Windows VM shows online in both forges; a job runs `signtool /?` and launches NVDA producing a speech log artifact.
* Cost report posted once; `docs/engineering/ci-runners.md`; Linear comment; changelog under Infra.

**Test plan**

* Workflow: dispatch the macOS reusable workflow with `xcodebuild -version`; assert minutes recorded.
* Windows: job runs a PowerShell smoke (`signtool`, NVDA start and stop, speech log non-empty).
* Portability: PAP-50 checker recognises the labels and guards.
* Cost: simulated cap breach makes the job fail fast with a clear message.

**Demo**

Reviewer opens the Actions tab, dispatches `ci-runners-smoke`, and watches a macOS job print the Xcode version while the Windows job uploads `nvda-speech.log`; then opens the cost report comment on this issue. Under 5 minutes of wall clock, 1 minute of attention.

**Edge cases**

* Hosted macOS queue delays: jobs have a 60-minute timeout and are not on the PR critical path.
* Windows VM update reboots mid-job: job retried once by the workflow.
* NVDA licence and telemetry prompts: pre-configured in the snapshot.
* Forgejo has no macOS runner: jobs guarded; documented gap in the DR drill.

**Dependencies**

PAP-50, PAP-25 (hard). Soft: PAP-51, code-signing issue. Unblocks PAP-20 (iOS CI), PAP-73, PAP-156; feeds PAP-19.

**Agent**

Built by Forge (Ops Runner). Reviewed by Sentinel (Security Auditor for runner isolation).

**Size**

M
