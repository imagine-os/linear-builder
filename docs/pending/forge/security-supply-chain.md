---
key: "security/supply-chain"
title: "Add supply-chain integrity: lockfile and minimum-release-age policy, pinned actions by digest, SLSA provenance attestations and cosign signatures for container images and Tauri artifacts, verified before deploy and update"
project: "forge"
parent: null
phase: "P1"
type: "Infra"
priority: 2
size: "M"
surfaces: ["Developer"]
milestone: "CI runs on both forges"
intendedState: "Backlog"
blockedBy: ["PAP-80", "PAP-52", "PAP-26"]
blocks: ["PAP-254"]
source: "round2/agent6/pending-issues.json (Security & Threat Model)"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-security-11-27d8ebfcd8d0"
identifier: "PAP-358"
status: "created"
createdAt: "2026-09-17"
---

# Add supply-chain integrity: lockfile and minimum-release-age policy, pinned actions by digest, SLSA provenance attestations and cosign signatures for container images and Tauri artifacts, verified before deploy and update

**Goal**

Most of the code in the product is not ours, and most of our own code is written by agents that run `pnpm add` on request. PAP-80 scans for known vulnerabilities and generates an SBOM; PAP-217 upgrades dependencies; PAP-46 signs commits. The gap is integrity: nothing stops a freshly published malicious package version, an unpinned action, or an image that was not built by our CI from being deployed. This issue closes it with install policy, digest pinning, build provenance and signature verification at every consumer (Coolify deploy, Tauri updater, Forgejo mirror).

**Scope**

* In: pnpm policy (`.npmrc` and `pnpm-workspace.yaml` settings), lockfile integrity checks, action and image digest pinning with a lint, SLSA provenance via `actions/attest-build-provenance` on GitHub and an equivalent `cosign attest` step on Forgejo runners, cosign keyless (GitHub OIDC) or key-based (Forgejo, key in sops) image signing, verification steps in PAP-26 deploy and PAP-257 updater, Renovate config for digest updates (PAP-217), `docs/engineering/supply-chain.md`.
* Out: vulnerability scanning (PAP-80), license policy (PAP-211), app-store signing certificates (app-shell code-signing gap), reproducible builds.

**Spec**

* Install policy: `pnpm` with `frozen-lockfile` everywhere in CI (already in PAP-96 worktrees), `minimum-release-age` set to 3 days for new versions (pnpm setting; Renovate mirrors with `minimumReleaseAge`), `ignore-scripts=true` by default with an explicit allowlist of packages whose postinstall is required (`esbuild`, `sharp`, `@tauri-apps/cli`) in `pnpm.onlyBuiltDependencies`, `verify-store-integrity=true`, registry pinned to `registry.npmjs.org` with optional Forgejo package registry mirror for DR; `pnpm audit signatures` in Gate 1 to verify npm provenance where present.
* Lockfile: Gate 1 fails when `pnpm-lock.yaml` changes without a `package.json` change in the same PR (agents sometimes regenerate) and when a dependency resolves to a git or tarball URL outside `imagine-os`.
* Pinning: all `uses:` in workflows pinned to full commit SHA with a version comment; all `image:` in `ops/compose/**` and Dockerfiles pinned to `@sha256:` digests; lint `scripts/check-pins.ts` in Gate 1; Renovate updates both (PAP-217 `pinDigests: true`).
* Provenance: every image built by PAP-26 gets a SLSA v1 provenance attestation and an SBOM attestation (CycloneDX from PAP-80) attached in the registry (GHCR and the Forgejo registry); Tauri installers (PAP-256) get provenance and detached cosign signatures uploaded with the release (PAP-52).
* Signing: GitHub runs use cosign keyless with the workflow identity; Forgejo runners use a cosign key pair stored in sops (PAP-25) with the public key committed at `ops/security/cosign.pub`; both signatures accepted by verifiers.
* Verification: Coolify pre-deploy command runs `cosign verify` against the image digest with the expected identity or key and `cosign verify-attestation --type slsaprovenance` asserting the source repo is `imagine-os/*` and the branch is `main` or a `v*` tag; failure aborts the rollout; the Tauri updater (PAP-257) already verifies its minisign signature; the release job additionally publishes the cosign signature and the update manifest is itself signed.
* Mirror integrity: PAP-47 mirror sync compares tags and signed commits on both forges nightly; divergence posts to `security/security-telemetry`.

**Interface contract**

* Provides: `.npmrc` policy, `scripts/check-pins.ts`, `scripts/check-lockfile.ts`, reusable workflow `attest-and-sign.yml`, `ops/security/cosign.pub`, verification snippet for Coolify, doc.
* Consumers: PAP-26 (deploy verification), PAP-256 and PAP-257 (artifact signatures), PAP-52 (release assets), PAP-217 (Renovate config), PAP-254 (RC certification requires verified provenance), PAP-219 controls `SEC-SUPPLY-*`.
* Requires: PAP-80 SBOM job, PAP-52 release workflow, PAP-26 image build, PAP-50 runners for the Forgejo path.

**Definition of done**

* `pnpm install` in CI fails on a lockfile edit without manifest change, on a git URL dependency and on a version younger than 3 days (fixtures).
* `check-pins` finds zero unpinned actions or images; a seeded `uses: actions/checkout@v4` fails it.
* Images from `main` carry provenance and SBOM attestations; `cosign verify` and `verify-attestation` pass; a hand-pushed image without attestation is refused by the Coolify pre-deploy step on staging (recording).
* Tauri release assets include signatures; verification documented for users.
* Docs; changelog under "Security"; Linear comment with the verification output.

**Test plan**

* Unit: pin and lockfile linters on fixture repos.
* Integration: build, attest, sign and verify a test image in CI on both forges; negative test with an unsigned image.
* e2e: staging deploy through the verifying pre-deploy step.
* No UI.

**Demo**

Show `cosign verify-attestation` output for the staging API image naming the workflow and commit, then push an unsigned tag to a scratch Coolify app and watch the deploy abort. One minute.

**Edge cases**

* Package with postinstall not on the allowlist: install prints the package name; adding it requires a Sentinel-reviewed PR.
* `minimum-release-age` blocks an urgent security fix: override per package with an expiry comment, flagged in the PAP-80 summary.
* Forgejo runner has no OIDC identity: key-based signing path; key rotation documented in PAP-219 runbook.
* Registry outage during verify: deploy aborts, never bypasses; runbook allows `--skip-verify` only with a Needs Justin approval logged.
* Renovate digest PRs flood: grouped weekly (PAP-217 grouping).

**Dependencies**

Blocked by PAP-80, PAP-52, PAP-26. Blocks PAP-254. Soft: PAP-217, PAP-256, PAP-257, PAP-47, PAP-50.

**Agent**

Built by Forge (Ops Runner sub-agent); reviewed by Sentinel (Security Auditor).

**Size**

M
