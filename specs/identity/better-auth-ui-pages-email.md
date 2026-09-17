---
identifier: "PAP-224"
title: "Auth UI pages and magic-link email delivery"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Customer", "Staff"]
milestone: "Auth works across web and desktop"
state: "Backlog"
parent: "PAP-57"
children: []
blockedBy: ["PAP-223"]
blocks: ["PAP-140", "PAP-220", "PAP-240", "PAP-58", "PAP-86"]
key: "identity/better-auth/ui-pages-email"
url: "https://linear.app/paperos/issue/PAP-224/auth-ui-pages-and-magic-link-email-delivery"
source: "Linear snapshot 2026-09-17T06:03Z (round-2 issue)"
---

# PAP-224: Auth UI pages and magic-link email delivery

**Goal**

Ship the sign-in, verify, passkey management and callback pages with page specs, plus the Resend-backed magic-link email, so a human can get into any PaperOS app on the web with a passkey, a link or Google/GitHub.

**Scope**

* In: `/auth/sign-in`, `/auth/verify`, `/auth/passkeys`, `/auth/callback` in `apps/web` with specs under `specs/pages/auth/`, `packages/auth/src/client.ts` with `authClient` and hooks, React Email template `magic-link.tsx`, Resend transport with sandbox allowlist, copy file for i18n, screenshots.
* Out: server config (sibling), Tauri deep links (sibling), org pages (PAP-58).

**Spec**

* Client: `createAuthClient({ baseURL, plugins: [passkeyClient(), magicLinkClient(), bearerClient()] })`; hooks `useSession`, `useSignIn`, `useSignOut`; `SignInForm` component with passkey button (conditional UI via `PublicKeyCredential.isConditionalMediationAvailable`), email field for magic link, Google and GitHub buttons.
* Pages use design-system primitives (Button, Input, Field, Toast) and the portal layout when present; copy in `packages/auth/src/copy.ts`.
* Email: `sendMagicLink` implementation using Resend with `RESEND_API_KEY`; in `PAPEROS_ENV != production` only `*@e2e.local` and an allowlist receive mail, everything else goes to Mailpit (PAP-42).
* Errors: expired link, used link, unknown provider account, rate limited, each with a specific message and retry action.

**Interface contract**

* Provides: `authClient`, `useSession()`, `<SignInForm>`, `<PasskeyList>` (reused by session management and PAP-62), `sendMagicLink` implementation registered into the server child.
* Requires: server child; PAP-67 primitives; PAP-16 routes; Mailpit from PAP-42.

**Definition of done**

* Passkey sign-up and sign-in work in Chromium and WebKit (Playwright with virtual authenticator); magic link works via Mailpit in CI and Resend sandbox once manually.
* Google and GitHub OAuth pass with `msw`-mocked providers in CI; live GitHub run logged once.
* Four page specs validate; screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark; axe zero serious.
* Email renders in React Email preview (screenshot) and in Mailpit.

**Test plan**

* Unit: form validation, error mapping table.
* E2E: three sign-in methods, expired link path, passkey cancel path.
* Visual: sign-in story at seven widths; email preview snapshot.

**Demo**

Open `/auth/sign-in` on the Pages preview, sign in with a passkey (or request a link and open Mailpit), land on `/`, open `/auth/passkeys` and add a second passkey. Under two minutes.

**Edge cases**

* Conditional UI unsupported: show the passkey button explicitly.
* Link opened on another device: landing page names the signed-in account.
* Resend outage: honest error and log, never fake success.

**Dependencies**

Sibling "Better Auth server, Drizzle schema merge and session helpers" (hard), PAP-67 (soft: proceed with unstyled primitives if late).

**Agent**

Built by Iris (Component Crafter) with Forge on the transport. Reviewed by Sentinel (Visual Inspector, Code Reviewer).

**Size**

M.
