#!/usr/bin/env python3
"""
Bear 多标签交集计算工具

用法:
    printf 'tag:inbox\n%s\n---\ntag:read-later\n%s\n' '<result1>' '<result2>' | python3 intersect.py

路径:
    skills/bearbrain/search/script/intersect.py

每段格式:
    第一行: tag:<tag_name>   （agent 手动加，用于标识）
    其余行: bear-search-notes 的原始输出
    段与段之间用单独一行 --- 分隔

输出: JSON {count, results: [{id, title}], per_tag: [{tag, count}]}
"""

import json
import re
import sys

UUID_RE = re.compile(
    r"([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})"
)
TITLE_RE = re.compile(r"^\d+\.\s+\*\*(.+?)\*\*")
TAG_LINE_RE = re.compile(r"^tag:\s*(.+)$")


def parse_segment(text: str) -> tuple[str, dict[str, str]]:
    """
    解析一段 bear-search-notes 输出（含首行 tag: 标识）。
    返回 (tag_name, {id: title})
    """
    lines = text.splitlines()
    tag = "unknown"
    notes: dict[str, str] = {}
    current_title: str | None = None

    for line in lines:
        stripped = line.strip()

        # 首行 tag 标识
        tag_match = TAG_LINE_RE.match(stripped)
        if tag_match:
            tag = tag_match.group(1).strip()
            continue

        # 笔记标题行: "1. **Title**"
        title_match = TITLE_RE.match(stripped)
        if title_match:
            current_title = title_match.group(1)
            continue

        # ID 行
        id_match = UUID_RE.search(stripped)
        if id_match and current_title is not None:
            notes[id_match.group(1).upper()] = current_title
            current_title = None

    return tag, notes


def main() -> None:
    raw = sys.stdin.read()
    segments = [s.strip() for s in re.split(r"^---$", raw, flags=re.MULTILINE) if s.strip()]

    if not segments:
        print(json.dumps({"error": "no input"}))
        sys.exit(1)

    parsed = [parse_segment(s) for s in segments]

    # 计算交集
    id_sets = [set(notes) for _, notes in parsed]
    intersection = id_sets[0].copy()
    for s in id_sets[1:]:
        intersection &= s

    # 合并所有 title
    merged_titles: dict[str, str] = {}
    for _, notes in parsed:
        merged_titles.update(notes)

    results = [{"id": i, "title": merged_titles[i]} for i in sorted(intersection)]

    output = {
        "count": len(results),
        "results": results,
        "per_tag": [{"tag": tag, "count": len(notes)} for tag, notes in parsed],
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
