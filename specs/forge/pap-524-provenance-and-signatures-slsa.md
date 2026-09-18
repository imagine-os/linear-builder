---
identifier: "PAP-524"
title: "Provenance and signatures: SLSA attestations and cosign signing for container images and Tauri artifacts on both forges, verified in the Coolify pre-deploy step and the desktop updater"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P1"
type: "Infra"
priority: 2
surfaces: ["Developer"]
milestone: "Disaster recovery proven"
state: "Backlog"
parent: "PAP-358"
children: []
blockedBy: ["PAP-26", "PAP-50", "PAP-52", "PAP-80", "PAP-256", "PAP-505", "PAP-519"]
blocks: ["PAP-254"]
key: "r4/forge/supply-chain-provenance"
url: "https://linear.app/paperos/issue/PAP-524/provenance-and-signatures-slsa-attestations-and-cosign-signing-for"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:01.422Z"
model: "claude-opus-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-524: Provenance and signatures: SLSA attestations and cosign signing for container images and Tauri artifacts on both forges, verified in the Coolify pre-deploy step and the desktop updater

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Infra M

**Goal**

The second half of PAP-358: prove every deployed image and every shipped installer was built by our CI from our repository, and refuse anything else at the two consumers that matter (Coolify rollout, desktop update). This is the piece the release certification (PAP-254) needs before a candidate reaches Justin.

**Scope**

In:

* Reusable workflow `attest-and-sign.yml` in `paperos-infra`: on GitHub, `actions/attest-build-provenance` plus `cosign sign` keyless with the workflow identity; on Forgejo runners, `cosign attest --predicate slsa.json` and `cosign sign --key` with a key pair from sops (PAP-25), public key committed at `ops/security/cosign.pub`.
* Attach SBOM (CycloneDX from PAP-80) as an attestation to every image in GHCR and the Forgejo registry; Tauri installers (PAP-256) get detached `.sig` files and the update manifest `latest.json` is itself signed.
* Verification: Coolify pre-deploy command `ops/security/verify-image.sh <digest>` running `cosign verify` (identity or key) and `cosign verify-attestation --type slsaprovenance` asserting repo `imagine-os/*` and ref `main` or `v*`; the updater (PAP-257) verifies the cosign signature of `latest.json` in addition to minisign.
* Runbook `docs/engineering/supply-chain.md` sections: keys, rotation, `--skip-verify` with Needs Justin approval logged.

Out: install and pin policy (PAP-523), vulnerability scanning (PAP-80), OS code signing (PAP-369), reproducible builds.

**Spec**

* Verification never bypasses on registry outage: deploy aborts (PAP-358 rule).
* Both signature types (keyless, key-based) accepted by one verifier policy file `ops/security/policy.yaml`.
* Attestation subjects use digests, never tags; the deploy job resolves the digest before verify.
* Key rotation: new key added to the policy before old removed; documented 30-day overlap.

**Interface contract**

Provides: `attest-and-sign.yml`, `cosign.pub`, `policy.yaml`, `verify-image.sh`, signed `latest.json`; consumed by PAP-26 (pre-deploy), PAP-257 (updater), PAP-52 (release assets), PAP-254 (RC certification), PAP-53 (restored forge must verify).

Consumes: image build (PAP-26), installers (PAP-256), Forgejo runners (PAP-50), SBOM (PAP-80), release workflow (PAP-52), sops (PAP-25).

**Definition of done**

* Images from `main` carry provenance and SBOM attestations; `cosign verify` and `verify-attestation` pass; a hand-pushed unsigned image is refused by staging pre-deploy (recording).
* Tauri test release includes `.sig` files and a signed `latest.json` the updater accepts; a tampered manifest is rejected (test); CHANGELOG under Security; Linear comment.

**Test plan**

* Unit: policy evaluation over fixture signatures (keyless ok, key ok, wrong repo, wrong ref); manifest signature verification in the updater bridge.
* E2E: build, attest, sign, verify a test image on both forges; negative unsigned deploy.

**Demo**

Reviewer runs `cosign verify-attestation --type slsaprovenance <staging api digest>` and reads the workflow and commit, then pushes an unsigned tag to a scratch Coolify app and watches the deploy abort. Under 2 minutes.

**Edge cases**

* Forgejo runner lacks OIDC: key path used; both accepted.
* Rekor transparency log unavailable: keyless verify uses the bundle offline mode; documented.
* Renovate digest PR changes a base image: provenance still ours (we build), base image digest recorded in the SBOM.

**Dependencies**

Hard: PAP-26, PAP-256, PAP-50. Soft: PAP-80, PAP-52, PAP-25. Blocks PAP-254. Sibling PAP-523.

**Agent**

Builder: Forge (Ops Runner). Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/forge/supply-chain-install-policy` = PAP-523.
