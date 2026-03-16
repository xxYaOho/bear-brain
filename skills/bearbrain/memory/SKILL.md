---
name: bearbrain/memory
description: Use when maintaining Bear-Brain long-term memory notes, especially the `#memory` root note or a memory topic note, after reusable knowledge has already been identified.
---

# Memory

## Overview
Use this skill to maintain the long-term experience layer in Bear-Brain.

This skill is for direct maintenance of `#memory` and memory topic notes. It is not for raw logging and it is not the promotion step itself. Use `bearbrain/promote-memory` when the source content still lives in `#memory/daily`.

## When to use
Use this skill when:
- A reusable rule, method, constraint, or judgment has already been identified
- The `#memory` root note needs to stay dense and current
- A memory topic note needs to be created or updated
- The root note is approaching its soft limit and should move detail into topic notes

Do not use this skill to store raw notes, article excerpts, or active project drafts.

## Memory model
### `#memory` root note
Purpose:
- Serve as the high-density inheritance entry point
- Keep only the most important reusable knowledge
- Provide recall keys and links to topic notes

Rules:
- Keep it concise
- Prefer pointers and distilled rules over full explanations
- Treat it as the default entry point for memory-first retrieval

### Memory topic notes
Purpose:
- Hold stable topic-level knowledge that no longer fits in the root note
- Preserve more context, rules, boundaries, and examples for one topic

Create or update a topic note when a pattern becomes specific enough to deserve its own durable home.

## Structure guidance
### Root note
```md
## Position
一句话说明 memory 的作用

## Core Memory
- 当前关键经验

## Recall Keys
- 关键词 -> [[memory/topic]]

## Topics
- [[memory/topic]]
  - 主题说明
```

### Topic note
```md
## Summary
一句话说明这个主题记住了什么

## Rules
- 规则 / 方法 / 判断依据

## Cases
- 典型情况（可选）

## Notes
- 例外情况
- 边界条件
```

## Write decisions
| Situation | Destination |
| --- | --- |
| Highest-priority reusable rule | `#memory` root note |
| Stable topic with growing detail | Topic note |
| Raw daily observation | Do not use this skill; use `promote-memory` later |
| Source material or article summary | Do not use this skill; route to `book/*` |

## Soft-limit rule
The root note has a soft limit.

When it starts getting too large:
- remind the user once
- do not block writing
- suggest a separate cleanup session
- move detail into topic notes, leaving only high-density recall in the root note

## Common mistakes
- Copying daily logs directly into `#memory`
- Copying source material into `#memory` instead of `book/*`
- Treating the root note as a full archive
- Creating topic notes too early, before a stable theme exists

## Final check
Before finishing, confirm:
- The content is truly long-term and reusable
- The destination is correct: root note or topic note
- The root note still reads like a dense entry point, not a storage dump
- A topic note was created only when the theme was stable enough
