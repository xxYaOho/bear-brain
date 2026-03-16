---
name: bearbrain/workstream
description: 创建或维护 `Workstream: ...` 笔记时使用，包含 Meta、Related Notes、Notes、Task 等 section。
---

# Workstream

## 概述
使用本 skill 来创建或维护工作容器主笔记。

`workstream` 只管理"一轮工作"的主笔记，不承载活文档正文。

## 职责
- 维护 `Meta / Related Notes / Notes / Task`
- 把相关笔记挂进 `Related Notes`
- 记录当前阶段状态与下一步

## 不负责
- 不写 PRD、QA、FT、FB 正文
- 不直接承担 memory 提炼
- 不发布到 `path/docs/*`

## 使用前提
写入前先经过 `bearbrain/admission`，写入时遵守 `bearbrain/bear-editing`。
