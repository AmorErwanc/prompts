#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
import os
from datetime import datetime


def parse_created_at(value: str):
    if value is None:
        return (datetime.min, value)
    v = value.strip()
    if not v:
        return (datetime.min, value)
    # Try common datetime formats; fallback to lexicographic ordering
    fmts = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d",
    ]
    for fmt in fmts:
        try:
            return (datetime.strptime(v, fmt), value)
        except Exception:
            pass
    try:
        # Python 3.11+ handles many ISO forms
        return (datetime.fromisoformat(v), value)
    except Exception:
        # Fallback: use lexicographic string for ordering if not parseable
        return (v, value)


def build_messages(rows):
    messages = []
    for row in rows:
        req = (row.get("request_content") or "").strip()
        resp = (row.get("response_content") or "").strip()
        if req:
            messages.append({"role": "user", "content": req})
        if resp:
            messages.append({"role": "assistant", "content": resp})
    return messages


def process_csv(csv_path: str, output_md: str):
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        sessions = {}
        for row in reader:
            session_id = (row.get("session_id") or "").strip()
            # Group even if session_id is empty, but mark it
            key = session_id if session_id else "<EMPTY_SESSION_ID>"
            sessions.setdefault(key, []).append(row)

    # Sort rows within each session by created_at
    for key in sessions:
        sessions[key].sort(key=lambda r: parse_created_at(r.get("created_at"))[0])

    # Build Markdown content
    lines = []
    lines.append(f"# 会话导出（来源：{os.path.basename(csv_path)}）")
    lines.append("")
    for sess_id, rows in sessions.items():
        # Try to pick a representative user_id for the session (first row)
        user_id = (rows[0].get("user_id") or "").strip()
        title_suffix = f"（user_id: {user_id}）" if user_id else ""
        lines.append(f"## session_id: {sess_id} {title_suffix}")
        messages = build_messages(rows)
        lines.append("```json")
        lines.append(json.dumps(messages, ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")

    with open(output_md, "w", encoding="utf-8") as out:
        out.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="预处理聊天 CSV，按 session 分组排序并输出为 Markdown（JSON 代码块）")
    parser.add_argument("csv", help="输入 CSV 文件路径")
    parser.add_argument("--output", "-o", help="输出 Markdown 文件路径（默认：同名 -sessions.md）")
    args = parser.parse_args()

    csv_path = args.csv
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"找不到 CSV 文件：{csv_path}")

    base, _ = os.path.splitext(csv_path)
    output_md = args.output or f"{base}-sessions.md"
    process_csv(csv_path, output_md)
    print(f"已生成：{output_md}")


if __name__ == "__main__":
    main()