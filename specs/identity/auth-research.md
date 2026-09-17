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
blocks: ["PAP-223", "PAP-57"]
key: "identity/auth-research"
url: "https://linear.app/paperos/issue/PAP-56/compare-better-auth-lucia-clerk-and-authjs-for-self-hosting"
source: "plan/specs/bucket-1.json (round-1 canonical spec JSON)"
---

# PAP-56: Compare Better Auth, Lucia, Clerk and Auth.js for self-hosting, organizations and passkeys; write ADR

**Goal**

Confirm the auth choice before it is wired into every surface: compare Better Auth, Lucia, Clerk and Auth.js against PaperOS's hard requirements (self-hosting, organizations, passkeys, Tauri support, agent API keys, OIDC provider for Forgejo SSO) with a hands-on spike, and record the result as an ADR that identity/better-auth executes.

**Scope**

- In: rubric-based comparison, a minimal spike per finalist proving passkeys and organization membership in a web app and in a Tauri 2 webview on Linux and macOS, the ADR, and a list of plugins and versions to adopt.
- Out: production wiring (identity/better-auth), SSO/SCIM depth (identity/sso-scim, though the ADR must note each candidate's path).

**Spec**

Deliverables in `imagine-os/paperos-template`:

- `docs/decisions/ADR-000X-authentication.md` (next free number) in the MADR format used by forge/vcs-decision-adr, with a comparison table scored on the libraries/eval-rubric criteria plus these requirement columns: self-hostable with Postgres (hard), organizations/teams plugin, passkeys (WebAuthn) registration and login, magic link, Google and GitHub OAuth, session strategy suitable for Tauri (bearer token or cookie in webview), API keys for agents, OIDC/OAuth2 provider capability (needed by forge/forgejo-deploy), SAML/OIDC SSO client for enterprise, SCIM story, TypeScript quality, licence, weekly npm downloads and last release date (with retrieval date), Drizzle adapter availability.
- Spike directory `spikes/auth/` (excluded from the production build via `pnpm` workspace ignore) with one sub-folder per finalist that reaches the spike stage (at minimum Better Auth and one alternative): a Vite React page with sign-up via passkey, sign-in via magic link (console-logged), create organization, invite member, switch active organization; run in the browser and inside a Tauri 2 dev window. Record findings, notably WebAuthn availability in WebKitGTK on Linux (expected missing; document the fallback to magic link or a system browser flow with deep link `paperos://auth/callback`) and on macOS WKWebView.
- Vendor lock-in note: Clerk and other hosted providers are evaluated but the ADR must state the data-residency implication and monthly cost at 10 000 MAU.
- Output the exact package list with versions for identity/better-auth (for example `better-auth`, `@better-auth/passkey` or the built-in passkey plugin as applicable at spike time, organization plugin, magic-link plugin, API-key plugin, OIDC provider plugin, Drizzle adapter) and any known bugs with links to issues.
- Time box: 6 agent-hours; if the spike cannot finish, the ADR records what was verified and what remains as risk.

**Definition of done**

- ADR merged with status Accepted (or Proposed and moved to Needs Justin if the recommendation differs from the plan's Better Auth decision).
- Comparison table complete for all four candidates, every cell filled or marked "not verified" with reason.
- Spike code committed under `spikes/auth/` with a README describing how to run each in browser and Tauri; screenshots at 1280 (web) and the Tauri window on Linux and macOS attached.
- Passkey behaviour in Tauri on Linux and macOS documented with the fallback decision.
- Package and plugin list with versions and Drizzle adapter compatibility recorded.
- Sentinel Security Auditor reviews the session and token handling notes; Scout (Library Evaluator) reviews rubric scoring.
- Linear comment summarising the recommendation in five lines; changelog entry under "Docs".

**Edge cases**

- A candidate has no Drizzle adapter: score it but note the maintenance burden of a custom adapter.
- Passkeys work in browser but not in the Tauri webview: this is expected on Linux; the ADR must still recommend a passkey-first design with graceful fallback, not abandon passkeys.
- Better Auth releases a breaking version during the spike: pin the version tested and note the migration guide.
- Rate limits on Google OAuth test app: use GitHub OAuth for the spike and document Google as configured but unverified.
- Justin already has strong preference from the plan: the ADR still needs evidence; if evidence contradicts the plan, escalate to Needs Justin rather than silently agree.

**Dependencies**

- None blocking. Soft: libraries/eval-rubric (criteria), libraries/backend-landscape (shares findings; link both ways). Consumer: identity/better-auth.

**Agent**

- Builds: Scout (Library Evaluator sub-agent) drives the comparison; Forge (Tauri Smith) runs the Tauri spike.
- Reviews: Sentinel (Security Auditor); Atlas approves the ADR.

**Size**

S: time-boxed research with a small spike; the deliverable is a decision, not a system.
