---
identifier: "PAP-532"
title: "Forgejo runner `heavy` profile with a Playwright browsers image so Gates 3 and 4 and the golden path run on Forgejo without GitHub"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Disaster recovery proven"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-50", "PAP-82", "PAP-248", "PAP-519"]
blocks: []
key: "r4/forge/playwright-runner-image"
url: "https://linear.app/paperos/issue/PAP-532/forgejo-runner-heavy-profile-with-a-playwright-browsers-image-so-gates"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:41.818Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-532: Forgejo runner `heavy` profile with a Playwright browsers image so Gates 3 and 4 and the golden path run on Forgejo without GitHub

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Infra S

**Goal**

PAP-50 proves Gate 1 on Forgejo and leaves browser images "for when PAP-82 needs them"; PAP-53 then proves only a Gate 1 PR on the restored forge. Forge independence that cannot run the visual gate is partial. This issue adds the heavy runner profile and image so the full gate suite runs on our own runners.

**Scope**

In:

* Image `git.PAPEROS_DOMAIN/imagine-os/runner-playwright:<pw-version>` built weekly from `mcr.microsoft.com/playwright` pinned by digest (PAP-358) plus Node 22, pnpm and `ffmpeg`; label `ubuntu-playwright` in the runner `config.yml`.
* `heavy` compose profile (PAP-50): one runner on a second Hetzner host (`cpx41`) with `capacity: 2`, KVM enabled for the Android emulator (PAP-258), pnpm store and Playwright cache volumes.
* Workflow changes: Gate 3 (PAP-82, PAP-246) and Gate 4 (PAP-85) jobs use `runs-on: [ubuntu-playwright]` with the same label defined on GitHub through a `runs-on` matrix mapping; portability checker (PAP-519) knows the label.
* Proof: the PAP-246 screenshot matrix and one PAP-85 scenario run green on Forgejo from a commit that also ran on GitHub, artefacts compared.

Out: the gate suites themselves (quality), macOS and Windows runners (PAP-371), autoscaling (PAP-536).

**Spec**

* Image rebuild pinned to the Playwright version in `package.json`; a mismatch fails the job with the fix.
* Video artefacts under 200 MB per run; retention 14 days on Forgejo (PAP-529 policy).
* Host cost documented; runner stopped nightly 01:00 to 05:00 UTC when idle unless a drill is scheduled.

**Interface contract**

Provides: runner image and label `ubuntu-playwright`, `heavy` profile, GitHub label mapping; consumed by PAP-82, PAP-246, PAP-85, PAP-429 (golden path on Forgejo), PAP-53 (full-gate DR proof), PAP-258 (emulator).

Consumes: runner deployment (PAP-50), Gate 3 suite (PAP-82), Hetzner project (PAP-25), pin policy (PAP-358, soft).

**Definition of done**

* Gate 3 contact sheet produced on Forgejo for the template with zero diff against the GitHub run of the same commit (both URLs).
* Runner online in org settings; image rebuild workflow green; `docs/engineering/ci-runners.md` heavy section; CHANGELOG; Linear comment.

**Test plan**

* Unit: label mapping in the workflow templater; Playwright version check script.
* E2E: Gate 3 and one Gate 4 scenario on the Forgejo runner; artefact comparison.

**Demo**

Reviewer opens the Forgejo Actions run for Gate 3, sees the seven-width contact sheet artefact, then the GitHub run of the same SHA with the identical sheet. Under a minute.

**Edge cases**

* Fonts differ between images: the image installs the same font set as the GitHub job (`fonts-noto`), asserted by a font-list step.
* Emulator needs `/dev/kvm`: documented host flag; job skips with a note when absent.
* Second host down: jobs queue on GitHub only; PAP-53 records the gap.

**Dependencies**

Hard: PAP-50, PAP-82. Soft: PAP-25, PAP-358, PAP-246, PAP-85. Feeds PAP-53, PAP-429.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 3 round-4 file keys in this description to Linear identifiers: `r4/forge/lfs-and-artifacts` = PAP-529, `r4/forge/portability-checker` = PAP-519, `r4/forge/runner-autoscaling` = PAP-536.
