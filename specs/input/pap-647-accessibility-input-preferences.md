---
identifier: "PAP-647"
title: "Accessibility input preferences: /settings/accessibility with single-key shortcut disable (WCAG 2.1.4), sticky-key chords, key repeat, hover and dwell delays, always-visible focus, timing extensions"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Voice and accessibility certification"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-72", "PAP-152", "PAP-153"]
blocks: ["PAP-160", "PAP-650"]
key: "r4/input/accessibility-input-preferences"
url: "https://linear.app/paperos/issue/PAP-647/accessibility-input-preferences-settingsaccessibility-with-single-key"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:21.062Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-647: Accessibility input preferences: /settings/accessibility with single-key shortcut disable (WCAG 2.1.4), sticky-key chords, key repeat, hover and dwell delays, always-visible focus, timing extensions

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

WCAG 2.1.4 requires that single-character shortcuts can be turned off or remapped, 2.2.1 that timing is adjustable, and motor-impaired users need chords without simultaneous presses. PAP-153 remaps keys and PAP-72 handles motion, but no page collects these preferences or feeds them to the registry, focus ring and toasts. PAP-160 must point at it.

**Scope**

In: `/settings/accessibility` page spec and `AccessibilitySettingsPage`; `user_preferences.accessibility jsonb` (PAP-33 extension) `{ singleKeyShortcuts: 'on'|'off'|'modifierOnly', stickyChords, keyRepeatDelayMs, hoverDelayMs, dwellClickMs?, focusRing: 'auto'|'always', timing: 'default'|'extended'|'none', motion (link to PAP-72), fontScale }`; registry and focus integrations; `useA11yPrefs()`.

Out: screen-reader testing (PAP-156), switch scanning (PAP-650), OS-level settings, spatial navigation (PAP-158).

**Spec**

* `singleKeyShortcuts: 'off'` makes the PAP-289 matcher ignore chords without a modifier (sequences like `g i` included) except inside `role=grid|listbox|tree` composites where arrow-style keys are native; `'modifierOnly'` rebinds them to `alt+<key>` through the PAP-153 resolver layer `a11y` (highest precedence below user overrides).
* `stickyChords`: modifiers pressed and released within 2 s latch for the next key (`Ctrl`, then `K` opens the palette); a status-bar glyph shows latched modifiers; implemented in the chord matcher, not the OS.
* `keyRepeatDelayMs` throttles `repeat` key events in roving lists and grids; `hoverDelayMs` feeds Tooltip (PAP-237) and hover cards; `dwellClickMs` (optional, off by default) activates the hovered focusable after the delay with a visible progress ring for head-pointer users.
* `focusRing: 'always'` shows the ring on `:focus` not only `:focus-visible` (PAP-152 `FocusRing`); `timing: 'extended'` multiplies toast durations by 3 and disables auto-dismiss under `'none'` (PAP-237 `useToast` reads it); session timeout warnings (PAP-57) get 10 minutes instead of 2.
* `fontScale` 1 to 1.5 sets `--pos-font-scale` consumed by PAP-66 type tokens; every preference persists through PAP-143 and applies within one frame; the page itself is operable with every setting on.
* Preferences mirror as `data-a11y-*` on `<html>` for CSS; an `a11y.prefs.changed` window message (PAP-145) keeps windows aligned.

**Interface contract**

Provides: `AccessibilitySettingsPage` (spec id `app.settingsAccessibility`), `useA11yPrefs()`, `A11yPrefs` Zod schema (in `contract-input`), matcher hooks `shortcutPolicy`, `stickyChords`, CSS variables `--pos-font-scale`, `data-a11y-*` attributes, procedures `preferences.accessibility.get|set`. Consumes: keymap resolver layers (PAP-153), chord matcher (PAP-289), focus ring and announcer (PAP-152), motion setting (PAP-72), toast durations (PAP-237), tooltip delay (PAP-237), type tokens (PAP-66), preferences storage and sync (PAP-33, PAP-143), settings route (PAP-63). Consumed by PAP-160 (statement links and criteria 2.1.4, 2.2.1), PAP-156 (protocol runs with `singleKeyShortcuts: off`).

**Definition of done**

* Every preference demonstrably changes behaviour in the template app; Playwright proves 2.1.4 (single-key shortcut ignored when off, remapped under modifierOnly) and 2.2.1 (toast persists under `none`); screenshots at 375, 768, 1280 in three themes; axe clean.
* `docs/platform/a11y/input-preferences.md` mapped to WCAG criteria; changelog; Linear comment on PAP-160 with the criteria mapping.

**Test plan**

* Unit: matcher policy matrix (shortcut kind × setting × focused role); sticky latch timing with fake timers; dwell activation and cancel on move; toast duration multiplier; font scale clamp.
* Integration: `preferences.accessibility.set` persists and reaches a second context within 2 s; RLS scopes to the user.
* E2E: turn single-key shortcuts off and confirm `g i` does nothing while `mod+k` works; enable sticky chords and open the palette with sequential `Ctrl` then `K`; set timing to none and see a toast stay; enable dwell and activate a button by hovering.

**Demo**

Reviewer opens `/settings/accessibility`, switches shortcuts to modifier-only, sees the help sheet update to `alt+g alt+i`, enables sticky chords and opens the palette pressing keys one at a time. Under two minutes.

**Edge cases**

* Preference conflicts with a user keymap override: override wins, page shows the conflict.
* Font scale 1.5 at 320 px: layouts reflow per PAP-70 container queries.

**Dependencies**

PAP-153 (hard, resolver layer), PAP-152 (hard), PAP-72 (hard, motion link). Soft: PAP-237, PAP-66, PAP-143, PAP-63, PAP-145. Blocks PAP-160; PAP-156 adopts the variant softly.

**Agent**

Builder: Iris (Motion and Input Stylist) with Nova on the matcher. Reviewer: Sentinel (Edge Case Hunter, Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/input/switch-access-scanning` = PAP-650.
