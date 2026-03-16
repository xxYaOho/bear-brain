---
name: bearbrain/doc-publish
description: 当需要将稳定的 Bear-Brain 笔记发布到 `path/docs/*` 时使用，特别是将活跃的 repo 笔记转换为稳定的 SPEC、GUIDE、CHANGELOG、COMPLETIONS 或 DECISIONS 文档。
---

# Doc Publish

## 概述
使用本 skill 将 Bear 活文档发布为 `path/docs/*` 稳定文档。

## 发布前检查
至少检查以下条件：
- 结构完整
- 已不再是讨论稿
- 已有明确目标类型（SPEC / GUIDE / CHANGELOG / COMPLETIONS / DECISIONS）
- 用户明确要求发布，或阶段已收束

## 规则
- 发布的是稳定快照，不是临时复制
- 不保留 Bear 源笔记回链
- plan 草稿先留 Bear，不直接发布到 `path/docs/*`

## 目标类型
| 类型 | 说明 |
| --- | --- |
| SPEC | 系统规格定义 |
| GUIDE | 使用指南 |
| CHANGELOG | 版本变更记录 |
| COMPLETIONS | 阶段完成总结 |
| DECISIONS | 关键决策记录 |
