---
identifier: "PAP-340"
title: "Relational and computed types (relation, lookup, rollup, formula storage) and convertFieldType with lossiness report"
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
blockedBy: ["PAP-339"]
blocks: ["PAP-165", "PAP-171", "PAP-199"]
key: "tables/fields/relational-computed"
url: "https://linear.app/paperos/issue/PAP-340/relational-and-computed-types-relation-lookup-rollup-formula-storage"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:05:34.130Z"
---

# PAP-340: Relational and computed types (relation, lookup, rollup, formula storage) and convertFieldType with lossiness report

**Goal**

Add relation, lookup, rollup and the formula storage type with their lateral-join contracts, and the type conversion routine every schema change relies on.

**Scope**

In: `fields/{relation,lookup,rollup,formula}.ts`, `convertFieldType`, `docs/views/field-types.md` conversion matrix. Out: formula evaluation (PAP-171), the schema editor UI (gap issue).

**Spec**

* `relation` options `{ datasetRef, limitOne, symmetricFieldId }`; symmetric writes kept consistent in one transaction; unreadable targets render "Restricted".
* `lookup { relationFieldId, targetFieldId }` and `rollup { relationFieldId, targetFieldId, fn }` are `computed: true`, compile via lateral joins in PAP-163.
* `formula` stores AST and result type only; renders `#PENDING` until PAP-171.
* `convertFieldType(field, newType) => { lossy, sampleLosses[] }` for every pair in the matrix; conversions run in a PAP-43 job in batches of 1,000 with progress.

**Interface contract**

Provides: four types, `convertFieldType`, `conversionMatrix`, `runConversion(job)`. Consumes: framework child, compiler joins (PAP-163), jobs (PAP-43). Consumed by PAP-332.

**Definition of done**

* Tests per type and for every conversion pair; matrix documented; stories screenshotted at 375, 1024, 1920.

**Test plan**

* Unit: symmetric relation consistency; lossiness for number to text, text to date, multi to single select.
* Integration: lookup and rollup values match a brute-force query on the seed.

**Demo**

Storybook `fields/relational`: link two records, watch the lookup fill, convert a text column to a select and read the report.

**Edge cases**

* Cycle of lookups rejected; conversion with 100k rows shows progress and is cancellable.

**Dependencies**

Framework child (hard), PAP-163 core child (hard), PAP-43.

**Agent**

Builder: Nova. Reviewer: Sentinel (Code Reviewer), Forge on joins.

**Size**

M: conversion matrix is the bulk.
