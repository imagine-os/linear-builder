---
identifier: "PAP-339"
title: "Choice, people and attachment types (select, multiSelect, user, attachment) with FieldSettingsPanel"
project: "tables"
projectName: "Table & Views Engine"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Grid with sort, filter, group"
state: "Backlog"
parent: "PAP-164"
children: []
blockedBy: ["PAP-238", "PAP-338"]
blocks: ["PAP-340"]
key: "tables/fields/choice-people-attachment"
url: "https://linear.app/paperos/issue/PAP-339/choice-people-and-attachment-types-select-multiselect-user-attachment"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:42:31.560Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-339: Choice, people and attachment types (select, multiSelect, user, attachment) with FieldSettingsPanel

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Add the four types that need external data (options, users, files) plus the settings panel used by column menus and the schema editor.

**Scope**

In: `fields/{select,multiSelect,user,attachment}.ts`, `FieldSettingsPanel`, option colour tokens. Out: relational types (sibling).

**Spec**

* `select` stores option id; options `{ id, name, color }` with a token palette; deleted options render grey "Unknown option".
* `multiSelect` as id arrays with `hasAll|hasAny` ops and `expandMulti` grouping.
* `user` as `user.id[]` with a searchable Combobox (PAP-238) over tenant members; avatar chips.
* `attachment` as `file.id[]` from PAP-37 with thumbnail cells, upload editor and broken-file retry.
* `FieldSettingsPanel` renders each type's `OptionsEditor` with validation.

**Interface contract**

Provides: four types, `FieldSettingsPanel`, `OptionColorPicker`. Consumes: framework child, Combobox (PAP-238), `uploadFile` and variants (PAP-37), members (PAP-58).

**Definition of done**

* Tests per type; panel story; screenshots at 375, 1024, 1920; axe on the panel and editors.

**Test plan**

* Unit: option delete keeps values; `hasAll` and `hasAny` compile; attachment `failed` state.
* Integration: upload through the editor stores a file row and renders the `sm` variant.
* Visual: matrix above.

**Demo**

Storybook `fields/choice`: add an option with a colour, pick two users, upload an image.

**Edge cases**

* Member removed from tenant renders as "Former member"; 200 options virtualised in the picker.

**Dependencies**

Framework child (hard), PAP-238, PAP-37 (hard).

**Agent**

Builder: Nova with Iris. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.
