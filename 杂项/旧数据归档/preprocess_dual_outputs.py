#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
import os
from datetime import datetime


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def parse_created_at(value: str):
    if value is None:
        return (datetime.min, value)
    v = value.strip()
    if not v:
        return (datetime.min, value)
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
        return (datetime.fromisoformat(v), value)
    except Exception:
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


def build_pairs(rows):
    pairs = []
    for row in rows:
        req = (row.get("request_content") or "").strip()
        resp = (row.get("response_content") or "").strip()
        pairs.append({"user": req, "assistant": resp})
    return pairs


def process_csv(csv_path: str, out_dir_sessions_md: str, out_dir_pairs_md: str):
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        sessions = {}
        for row in reader:
            session_id = (row.get("session_id") or "").strip()
            key = session_id if session_id else "<EMPTY_SESSION_ID>"
            sessions.setdefault(key, []).append(row)

    for key in sessions:
        sessions[key].sort(key=lambda r: parse_created_at(r.get("created_at"))[0])

    base_name = os.path.splitext(os.path.basename(csv_path))[0]

    # Version A: per-session messages array in Markdown with JSON code blocks
    ensure_dir(out_dir_sessions_md)
    md_a_path = os.path.join(out_dir_sessions_md, f"{base_name}-sessions.md")
    lines_a = []
    lines_a.append(f"# 会话导出（来源：{os.path.basename(csv_path)}）")
    lines_a.append("")
    for sess_id, rows in sessions.items():
        user_id = (rows[0].get("user_id") or "").strip()
        title_suffix = f"（user_id: {user_id}）" if user_id else ""
        lines_a.append(f"## session_id: {sess_id} {title_suffix}")
        messages = build_messages(rows)
        lines_a.append("```json")
        lines_a.append(json.dumps(messages, ensure_ascii=False, indent=2))
        lines_a.append("```")
        lines_a.append("")
    with open(md_a_path, "w", encoding="utf-8") as out:
        out.write("\n".join(lines_a))

    # Version B: per-session user/assistant pairs array in Markdown with JSON code blocks
    ensure_dir(out_dir_pairs_md)
    md_b_path = os.path.join(out_dir_pairs_md, f"{base_name}-pairs.md")
    lines_b = []
    lines_b.append(f"# 成对消息导出（来源：{os.path.basename(csv_path)}）")
    lines_b.append("")
    for sess_id, rows in sessions.items():
        user_id = (rows[0].get("user_id") or "").strip()
        title_suffix = f"（user_id: {user_id}）" if user_id else ""
        lines_b.append(f"## session_id: {sess_id} {title_suffix}")
        pairs = build_pairs(rows)
        lines_b.append("```json")
        lines_b.append(json.dumps(pairs, ensure_ascii=False, indent=2))
        lines_b.append("```")
        lines_b.append("")
    with open(md_b_path, "w", encoding="utf-8") as out:
        out.write("\n".join(lines_b))

    return md_a_path, md_b_path


def main():
    parser = argparse.ArgumentParser(description="从聊天 CSV 生成两种 Markdown 版本：A(按会话的消息数组) 与 B(按行成对的 user/assistant)")
    parser.add_argument("csv", help="输入 CSV 文件路径")
    parser.add_argument("--out-a", default="sessions_md", help="版本A输出目录（默认：sessions_md）")
    parser.add_argument("--out-b", default="pairs_md", help="版本B输出目录（默认：pairs_md）")
    args = parser.parse_args()

    csv_path = args.csv
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"找不到 CSV 文件：{csv_path}")

    md_a_path, md_b_path = process_csv(csv_path, args.out_a, args.out_b)
    print("已生成：")
    print(f"  A: {md_a_path}")
    print(f"  B: {md_b_path}")


if __name__ == "__main__":
    main()