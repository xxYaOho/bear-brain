---
name: bearbrain/bear-editing
description: Use when creating or editing Bear-Brain Bear notes and you must preserve note structure, section anchors, Related Notes formatting, snapshot-before-overwrite workflow, or append-versus-overwrite safety rules.
---

# Bear editing

## Overview
Use this skill to decide **how** to edit a Bear-Brain note safely.

This skill does not decide **where** content belongs. Run `bearbrain/admission` first when routing is still unclear.

## When to use
Use this skill when any of these are true:
- A Bear note already has stable sections and must be updated without breaking structure
- A long-lived note needs snapshot + overwrite instead of endless append
- `Related Notes` needs to be added or cleaned up
- A note needs section-level updates such as `Meta`, `Task`, `Notes`, or `Promote Status`

Do not use this skill to decide content routing or to rewrite large note bodies without first deciding the note type.

## Core rules
- Use the Bear title field for the note title; do not repeat H1 in the body
- Use Bear native tags; do not place tags in the body
- Keep long-lived planning and governance notes on snapshot + overwrite
- Keep `#memory/daily` and running logs on append
- Keep `Related Notes` as nested bullet lists, never tables
- Mark invalid entry points with strikethrough instead of deleting them

## Edit decision table
| Situation | Action |
| --- | --- |
| Long-lived main note with structural refresh | Snapshot + overwrite |
| `#memory/daily` log growth | Append |
| `Notes` incremental status entry | Append |
| `Meta`, `Task`, `Promote Status` update | Section replace |
| No stable anchor exists | Prefer snapshot + overwrite |

## Related Notes format
```md
- [[note title]]
  - `NOTE-ID`
  - 描述

- ~~[[old note title]]~~
  - `NOTE-ID`
  - 已被新入口覆盖 / 历史参考
```

## Anchor order
Before editing, locate anchors in this order:
1. Section title, such as `## Related Notes`
2. Stable field lines, such as `- Status:`
3. List structure or table header
4. Delimiter blocks

If none of these are stable, stop using section-level edits and switch to snapshot + overwrite.

## Note-type specifics
### Workstream
Prefer maintaining these sections only:
- `## Meta`
- `## Related Notes`
- `## Notes`
- `## Task`

### Daily memory
Always preserve:
- `## Promote Status`
- `## Summary`
- `## Log`

### Plans and governance notes
During trial-stage iteration, Bear is the primary draft surface.
Repo files hold stable snapshots later.

## Common mistakes
- Writing tags into the body
- Reintroducing `Related Notes` tables
- Appending to a long-lived main note when overwrite is the right action
- Overwriting before taking a snapshot
- Forcing section replacement without a stable anchor

## Final check
Before finishing, confirm:
- Title still exists in Bear
- Tags are still correct
- Required sections still exist
- `Related Notes` still uses nested bullets
- A snapshot exists if this was a long-lived main note overwrite
