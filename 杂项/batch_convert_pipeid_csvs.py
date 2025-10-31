#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量转换"对话数据导出/"目录下所有pipeid文件夹中的CSV文件
生成两种JSON格式的Markdown文件：
- sessions格式：[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
- pairs格式：[{"user": "...", "assistant": "..."}]
"""

import os
import csv
import json
from datetime import datetime
from pathlib import Path


def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def parse_created_at(value: str):
    """解析时间字符串，返回datetime对象用于排序"""
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


def build_sessions_format(rows):
    """构建sessions格式：[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]"""
    messages = []
    for row in rows:
        user_input = (row.get("用户输入") or "").strip()
        ai_reply = (row.get("AI回复") or "").strip()
        if user_input:
            messages.append({"role": "user", "content": user_input})
        if ai_reply:
            messages.append({"role": "assistant", "content": ai_reply})
    return messages


def build_pairs_format(rows):
    """构建pairs格式：[{"user": "...", "assistant": "..."}]"""
    pairs = []
    for row in rows:
        user_input = (row.get("用户输入") or "").strip()
        ai_reply = (row.get("AI回复") or "").strip()
        pairs.append({"user": user_input, "assistant": ai_reply})
    return pairs


def process_csv_file(csv_path: str, output_dir: str):
    """处理单个CSV文件，生成sessions和pairs两种格式的Markdown"""
    print(f"  处理文件: {os.path.basename(csv_path)}")

    # 读取CSV并按session_id分组
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        sessions = {}
        for row in reader:
            session_id = (row.get("会话ID") or "").strip()
            key = session_id if session_id else "<EMPTY_SESSION_ID>"
            sessions.setdefault(key, []).append(row)

    # 对每个session内的记录按时间排序
    for key in sessions:
        sessions[key].sort(key=lambda r: parse_created_at(r.get("创建时间"))[0])

    base_name = os.path.splitext(os.path.basename(csv_path))[0]

    # 生成sessions格式的Markdown（原messages.md）
    ensure_dir(output_dir)
    md_sessions_path = os.path.join(output_dir, f"{base_name}-原messages.md")
    lines_sessions = []
    lines_sessions.append(f"# 会话导出（来源：{os.path.basename(csv_path)}）")
    lines_sessions.append("")

    for sess_id, rows in sessions.items():
        user_id = (rows[0].get("用户ID") or "").strip()
        title_suffix = f"（user_id: {user_id}）" if user_id else ""
        lines_sessions.append(f"## session_id: {sess_id} {title_suffix}")
        messages = build_sessions_format(rows)
        lines_sessions.append("```json")
        lines_sessions.append(json.dumps(messages, ensure_ascii=False, indent=2))
        lines_sessions.append("```")
        lines_sessions.append("")

    with open(md_sessions_path, "w", encoding="utf-8") as out:
        out.write("\n".join(lines_sessions))

    # 生成pairs格式的Markdown（优化后messages.md）
    md_pairs_path = os.path.join(output_dir, f"{base_name}-优化后messages.md")
    lines_pairs = []
    lines_pairs.append(f"# 成对消息导出（来源：{os.path.basename(csv_path)}）")
    lines_pairs.append("")

    for sess_id, rows in sessions.items():
        user_id = (rows[0].get("用户ID") or "").strip()
        title_suffix = f"（user_id: {user_id}）" if user_id else ""
        lines_pairs.append(f"## session_id: {sess_id} {title_suffix}")
        pairs = build_pairs_format(rows)
        lines_pairs.append("```json")
        lines_pairs.append(json.dumps(pairs, ensure_ascii=False, indent=2))
        lines_pairs.append("```")
        lines_pairs.append("")

    with open(md_pairs_path, "w", encoding="utf-8") as out:
        out.write("\n".join(lines_pairs))

    return md_sessions_path, md_pairs_path


def process_pipeid_folder(pipeid_folder: str, output_base_dir: str):
    """处理单个pipeid文件夹"""
    pipeid = os.path.basename(pipeid_folder)
    print(f"\n处理pipeid文件夹: {pipeid}")

    # 创建输出目录
    output_dir = os.path.join(output_base_dir, pipeid)
    ensure_dir(output_dir)

    # 查找该文件夹下的所有CSV文件
    csv_files = [f for f in os.listdir(pipeid_folder) if f.endswith('.csv')]

    if not csv_files:
        print(f"  警告: 未找到CSV文件")
        return

    # 处理每个CSV文件
    for csv_file in csv_files:
        csv_path = os.path.join(pipeid_folder, csv_file)
        try:
            sessions_path, pairs_path = process_csv_file(csv_path, output_dir)
            print(f"    ✓ 已生成: {os.path.basename(sessions_path)}")
            print(f"    ✓ 已生成: {os.path.basename(pairs_path)}")
        except Exception as e:
            print(f"    ✗ 处理失败: {str(e)}")


def main():
    """主函数：批量处理所有pipeid文件夹"""
    # 输入和输出目录
    input_base_dir = "对话数据导出"
    output_base_dir = "markdown_outputs"

    if not os.path.exists(input_base_dir):
        print(f"错误: 找不到目录 '{input_base_dir}'")
        return

    # 获取所有pipeid文件夹
    pipeid_folders = [
        os.path.join(input_base_dir, d)
        for d in os.listdir(input_base_dir)
        if os.path.isdir(os.path.join(input_base_dir, d)) and not d.startswith('.')
    ]

    if not pipeid_folders:
        print(f"错误: 在 '{input_base_dir}' 中未找到pipeid文件夹")
        return

    print(f"找到 {len(pipeid_folders)} 个pipeid文件夹")
    print(f"输出目录: {output_base_dir}")
    print("=" * 60)

    # 处理每个pipeid文件夹
    success_count = 0
    for pipeid_folder in sorted(pipeid_folders):
        try:
            process_pipeid_folder(pipeid_folder, output_base_dir)
            success_count += 1
        except Exception as e:
            print(f"\n错误: 处理文件夹 {os.path.basename(pipeid_folder)} 时失败: {str(e)}")

    print("\n" + "=" * 60)
    print(f"处理完成！成功处理 {success_count}/{len(pipeid_folders)} 个文件夹")
    print(f"所有输出文件保存在: {output_base_dir}/")


if __name__ == "__main__":
    main()
