---
identifier: "PAP-219"
title: "Write the security threat model and hardening baseline: STRIDE per trust boundary, CSP and security headers, CSRF, secret rotation runbook, incident response playbook"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Spec"
priority: 1
surfaces: ["Developer", "Agent"]
milestone: "Auth works across web and desktop"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-60", "PAP-80"]
key: "identity/threat-model"
url: "https://linear.app/paperos/issue/PAP-219/write-the-security-threat-model-and-hardening-baseline-stride-per"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:59.411Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-219: Write the security threat model and hardening baseline: STRIDE per trust boundary, CSP and security headers, CSRF, secret rotation runbook, incident response playbook

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Spec P0

**Goal**

Write the one document every security check points at: a STRIDE threat model per trust boundary (browser, Tauri webview, API, Postgres, orchestrator, agent sessions, forges, VPS), the hardening baseline every app inherits (headers, CSP, CSRF, cookies, rate limits), a secret rotation runbook and an incident response playbook. Gate 2's security reviewer, the Semgrep local rules and Sentinel's audits check against it instead of against opinion.

**Read first.** Read before coding: [Blueprint](<https://linear.app/paperos/document/paperos-core-platform-blueprint-0c2115fe48f1>) → [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) → your project's `Contract` section (Linear project content) → your character sheet ([Roster](<https://linear.app/paperos/document/paperos-agent-roster-org-chart-and-character-index-fc7ea7f41ff3>)) → [Execution Schedule](<https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795>) for your start day and the branch-start rule. The [Security & Threat Model](<https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c>) is v1 of the document this issue owns: §3 STRIDE by boundary, §4 deny list, §5 secrets handling, §6 prompt-injection tiers, §7 backup and DR, §8 compliance posture, §9 gap register. Treat it as the draft baseline, give every control an `SEC-*` id in `controls.yaml`, and file any disagreement as an ADR rather than silently diverging.

**Scope**

* In: `docs/security/threat-model.md`, `docs/security/hardening-baseline.md`, `docs/security/secret-rotation.md`, `docs/security/incident-response.md`; the machine-readable control list `ops/security/controls.yaml`; a `securityHeaders()` Hono middleware in `packages/core/src/security/` that implements the baseline; a header check in Gate 1.
* Out: penetration testing, the scanners themselves (PAP-80), WAF, SOC 2 evidence collection.

**Spec**

* Trust boundaries and assets table: for each boundary list entry points, data crossing it, authentication used, STRIDE threats, existing controls, gaps with an owning issue key. The orchestrator (holds Linear, forge and Claude keys) is boundary T1 and gets its own section: key storage in sops, least-privilege bot accounts (PAP-48), per-session agent keys (PAP-60), network egress allowlist.
* Baseline: `Content-Security-Policy` with nonces (`script-src 'self' 'nonce-…'`, `connect-src` limited to API, Electric and Hocuspocus origins, `frame-ancestors 'none'`), `Strict-Transport-Security` 2 years preload, `X-Content-Type-Options`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` minimal, `Cross-Origin-Opener-Policy: same-origin`. CSRF: origin check on all mutating routes plus `SameSite=Lax` cookies; bearer tokens on Tauri exempt. Rate limits per route class. Cookie names and flags. Upload rules (type sniffing, SVG sanitising). Logging rules (never tokens, never full emails in prompt logs).
* `controls.yaml`: `{ id: SEC-<area>-<nn>, statement, boundary, verify: lint|test|scan|manual, owner, issues: [PAP-…] }`; at least 40 controls.
* Rotation runbook: every secret class (DB, Resend, Stripe, forge tokens, Better Auth secret, agent keys, sops age keys) with rotation steps, blast radius and the command that proves the old value is dead.
* Incident playbook: severity levels, who is paged (Justin via Needs Justin and email), containment steps per boundary, evidence to preserve, 72-hour disclosure checklist, post-mortem template.

**Interface contract**

* Provides: `securityHeaders(options)` middleware exported from `packages/core/src/security/headers.ts`; `CSP_NONCE` request-context key; `controls.yaml` consumed by PAP-80 (Semgrep rule ids reference `SEC-*`), PAP-81 (security reviewer prompt lists controls), PAP-79 (`security.md` rubric cites control ids).
* Requires: nothing at runtime; references PAP-17 secret storage and PAP-25 sops layout by path.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (RLS session variables and `app.bypass` are the controls the harness in PAP-34 proves) and §4 (auth headers and error codes the hardening baseline covers). Threat Model source: [PaperOS Security & Threat Model](https://linear.app/paperos/document/paperos-security-and-threat-model-51fd5fd8929c) §3 STRIDE by boundary, §4 deny list, §5 secrets handling, §6 prompt-injection tiers, §7 backup and DR, §8 compliance posture; `controls.yaml` must give every control named there an `SEC-*` id, and §9's gap register names the pending security issues that extend this baseline.

**Definition of done**

* Four documents merged; every trust boundary has a STRIDE table with no empty cell (gaps name an issue).
* `controls.yaml` validates against its Zod schema and has 40 or more controls, 25 with `verify: lint|test|scan`.
* `securityHeaders()` applied in `apps/api` and the header check passes in Gate 1 on the example app.
* Sentinel Security Auditor and Atlas approve; Justin reads the incident playbook and confirms the paging channel in one comment.
* Changelog entry under "Security"; Linear comment linking the model.

**Test plan**

* Unit: `securityHeaders()` sets every header from the baseline (snapshot); nonce differs per request; CSP report-only toggle works.
* Integration: Playwright loads `/` and `/auth/sign-in` at 375 and 1280 with CSP enforced, zero console CSP violations; an inline script without nonce is blocked (seeded).
* Schema: `controls.yaml` Vitest validation; every `issues` key exists in the Linear snapshot export.
* Manual: rotation runbook dry-run for the Resend key on staging, timed.

**Demo**

Open `docs/security/threat-model.md`, jump to the orchestrator boundary table, then run `curl -I https://staging.<domain>/` and read the headers; run `pnpm security:controls --verify lint` to list controls with their check status. Under two minutes.

**Edge cases**

* CSP breaks Storybook or the Pages demo: those hosts use a documented relaxed policy, never the app.
* Tauri `tauri://localhost` origin: CSP and CSRF rules list it explicitly; the model notes IPC as a boundary.
* Embedded OSS products (PAP-215) with inline scripts: allowed only behind their own route prefix with a per-route CSP.
* A control has no possible automated check: `verify: manual` with a review cadence field, never omitted.
* Model contradicts an existing spec: the spec changes; open an issue and link it from the gap cell.

**Dependencies**

None blocking. Consumers: PAP-80, PAP-81, PAP-60, PAP-106, PAP-57 children (headers and cookie flags).

**Agent**

Written by Sentinel (Security Auditor sub-agent); Forge implements the middleware. Reviewed by Atlas; Justin confirms paging.

**Size**

M: a writing task with one small middleware; the value is in completeness.
