---
identifier: "PAP-585"
title: "Portal profile, security, billing stub and notification preference pages with specs, optimistic save through the write queue and the unsaved-changes prompt"
project: "identity"
projectName: "Identity, Roles & Audiences"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Agent principals and enterprise"
state: "Backlog"
parent: "PAP-62"
children: []
blockedBy: ["PAP-584"]
blocks: ["PAP-623", "PAP-841", "PAP-865", "PAP-887"]
key: "r4/identity/portal-account-pages"
url: "https://linear.app/paperos/issue/PAP-585/portal-profile-security-billing-stub-and-notification-preference-pages"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:12.016Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-585: Portal profile, security, billing stub and notification preference pages with specs, optimistic save through the write queue and the unsaved-changes prompt

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Second half of PAP-62: the pages a customer actually uses. Profile with avatar and verified email change, security embedding the `SecurityPage` and access history, an honest billing stub until PAP-177 fills it, and notification preferences stored on the user until PAP-136 owns them.

**Scope**

In: Pages and specs `specs/pages/portal/{profile,security,billing,notifications}.spec.yaml`: profile (name, avatar via PAP-37, email change with verification, locale and timezone, contact method; optimistic save via `mutate` with a saved indicator); security (embeds `SecurityPage` from PAP-581 and `AccessHistoryList` from PAP-61, delete account with 30-day grace); billing (plan, payment method, invoices when PAP-177 exists, else `EmptyState` 'Billing is not configured' with `data-stub`); notifications (channel toggles in `user.attributes.notificationPrefs` until PAP-136); shared `SettingRow` and `DangerZone`; Zod validation shared with the API; unsaved-changes prompt.

Out: Frame and login (sibling), session and 2FA logic (PAP-220 children provide the components), billing logic (PAP-177), notification delivery (PAP-136), legal pages (PAP-221).

**Spec**

* Profile save goes through `mutate(orpc.users.updateMe, { optimistic })` (PAP-272) with a saved indicator and revert on rejection; email change sends a verification link and only then swaps the address; 'cannot use this email' is the only message for a taken address.
* Security page composes the two embeds and adds `DangerZone` with delete account, which calls the PAP-221 request when present, else `users.requestDeletion` with the 30-day grace explained; deletion with an active subscription is blocked with guidance (hook for PAP-177).
* Billing stub renders `EmptyState` with `data-stub` and no dead buttons; PAP-177 replaces the page body through `registerPortalSection('billing')`.
* Notification preferences: kinds list from PAP-136 when present, else the three defaults (mentions, digests, product news); persisted with optimistic save.
* Every page declares states; forms validate with the shared Zod schemas; unsaved-changes prompt on navigation.

**Interface contract**

Provides: Four routes and specs, `registerPortalSection(id, component)`, `ProfileForm`, `NotificationPrefs` component, `data-stub` convention shared with the console.

Consumes: Frame (sibling), `SecurityPage` (PAP-581, soft: placeholder if late), `AccessHistoryList` (PAP-61, soft), files (PAP-37, soft), write queue (PAP-272), states (PAP-234), primitives (PAP-67, PAP-71), deletion flow (PAP-221 or PAP-432, soft), billing (PAP-177, soft), notifications (PAP-136, soft).

**Definition of done**

* Four specs validate; profile save round-trips through the write queue including offline then reconnect; email-change verification path tested.
* Screenshots of every page at seven widths in three themes; RTL and 80-character-name stories; axe zero serious or critical.
* Deletion blocked with an active subscription fixture; docs page catalogue; changelog under Customer.

**Test plan**

* Unit: form schemas, stub detection, preference defaults, unsaved-changes guard.
* E2E: edit display name offline, reload, reconnect, saved indicator clears; change email and verify via Mailpit; open security and see passkeys and access history.

**Demo**

As the seeded customer edit the display name and watch the saved indicator, open Security and see passkeys and access history, open Billing and see the honest stub. Under two minutes.

**Edge cases**

* Avatar upload fails: previous avatar kept, toast with retry.
* Locale change: UI re-renders in the new locale without reload (PAP-27).
* Deletion requested then cancelled within grace: `cancelDeletion` restores (PAP-432).

**Dependencies**

Blocked by PAP-584 (hard). Soft: PAP-581, PAP-61, PAP-37, PAP-272, PAP-234, PAP-67, PAP-71, PAP-221, PAP-432, PAP-177, PAP-136, PAP-27.

**Agent**

Builder: Iris (Component Crafter) with Quill on specs. Reviewer: Sentinel (Visual Inspector; Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/identity/portal-frame` = PAP-584, `r4/identity/sessions-stepup` = PAP-581.
