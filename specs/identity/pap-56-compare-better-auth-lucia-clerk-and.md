---
identifier: "PAP-56"
title: "Compare Better Auth, Lucia, Clerk and Auth.js for self-hosting, organizations and passkeys; write ADR"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Research"
priority: 2
surfaces: ["Developer"]
milestone: "Auth works across web and desktop"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-57", "PAP-223"]
key: "identity/auth-research"
url: "https://linear.app/paperos/issue/PAP-56/compare-better-auth-lucia-clerk-and-authjs-for-self-hosting"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:06.549Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-56: Compare Better Auth, Lucia, Clerk and Auth.js for self-hosting, organizations and passkeys; write ADR

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — security-sensitive title keyword: Auth

**Goal**

Confirm the authentication choice before it is wired into every surface: compare Better Auth, Lucia, Clerk and Auth.js against PaperOS's hard requirements with a hands-on spike in the browser and in a Tauri 2 webview, and record the result as an ADR that PAP-57 executes with exact package versions.

**Scope**

* In: rubric comparison, a spike per finalist (at minimum Better Auth and one alternative) proving passkeys and organization membership on web and in Tauri on Linux and macOS, the ADR, the plugin and version list.
* Out: production wiring (PAP-57), SSO and SCIM depth (PAP-65; the ADR notes each candidate's path).

**Spec**

* `docs/decisions/ADR-000X-authentication.md` in the MADR format from PAP-44, scored on PAP-209 criteria plus requirement columns: self-hostable on Postgres (hard), organizations and teams, passkeys, magic link, Google and GitHub OAuth, Tauri-compatible session strategy (bearer or webview cookie), API keys for agents, OIDC provider capability (PAP-45 needs it), enterprise SSO client, SCIM story, TypeScript quality, licence, weekly downloads and last release (with retrieval date), Drizzle adapter.
* Spike `spikes/auth/<candidate>/` excluded from the production workspace: a Vite React page with passkey sign-up, magic-link sign-in (console-logged), create organization, invite, switch; run in the browser and in `tauri dev`. Record WebAuthn availability in WebKitGTK (expected missing; document the system-browser plus `paperos://auth/callback` fallback) and in WKWebView.
* Hosted providers: state data-residency implications and monthly cost at 10 000 MAU.
* Output the exact package list and versions (`better-auth`, passkey, organization, magic-link, API-key, OIDC provider plugins, Drizzle adapter) and known bugs with issue links.
* Time box 6 agent-hours; unfinished verification is recorded as risk.

**Interface contract**

* Provides: the ADR (status Accepted or Proposed), `spikes/auth/README.md`, a `versions.json` under `spikes/auth/` that PAP-57 children copy into `package.json`, and a findings section "Tauri" that PAP-225 implements.
* Consumers: PAP-57 and its children (PAP-223 to PAP-226), PAP-214 (shares findings), PAP-65 (SSO notes).
* Requires: nothing.

**Definition of done**

* ADR merged; if the recommendation differs from Better Auth, the ADR is Proposed and a Needs Justin item is opened with a five-line summary.
* Comparison table complete for all four candidates; every cell filled or marked "not verified" with reason.
* Spike code committed with run instructions; screenshots at 1280 (web) and of the Tauri window on Linux and macOS.
* Tauri passkey behaviour documented with the fallback decision; `versions.json` present.
* Sentinel Security Auditor reviews session and token notes; Scout reviews scoring; changelog entry under "Docs".

**Test plan**

* Spike smoke: each candidate's page completes sign-up, sign-in, organization create and switch in Chromium (recorded once, not CI).
* Tauri: the same flow in `tauri dev` on Linux (expect passkey unavailable) and macOS.
* Review: Atlas checks every hard requirement has evidence, not a vendor claim.

**Demo**

Open the ADR's comparison table, then `cd spikes/auth/better-auth && pnpm dev`, register a passkey and create an organization in the browser; open the Linux Tauri screenshot showing the fallback message. Under two minutes.

**Edge cases**

* Candidate lacks a Drizzle adapter: score it, note the custom adapter cost.
* Passkeys fail in the webview but pass in the browser: expected on Linux; still recommend passkey-first with fallback.
* Breaking release mid-spike: pin the tested version and cite the migration guide.
* Google OAuth test-app limits: spike with GitHub, mark Google unverified.
* Evidence contradicts the plan: escalate to Needs Justin rather than agree silently.

**Dependencies**

None blocking. Soft: PAP-209 (criteria), PAP-214 (shared findings).

**Agent**

Scout (Library Evaluator) drives; Forge (Tauri Smith) runs the Tauri spike. Reviewed by Sentinel (Security Auditor); Atlas approves the ADR.

**Size**

S: time-boxed research producing a decision.
