#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json
import os
from collections import defaultdict
import re

def extract_dialog_from_messages(messages_str):
    """
    从messages字符串中提取完整的对话历史
    
    Args:
        messages_str: messages字段的JSON字符串
        
    Returns:
        list: 包含role和content的对话列表
    """
    try:
        messages = json.loads(messages_str)
        dialog = []
        
        for msg in messages:
            if msg.get('role') in ['user', 'assistant'] and msg.get('content'):
                # 清理内容，去除多余空白字符
                content = msg['content'].strip()
                if content:
                    dialog.append({
                        "role": msg['role'],
                        "content": content
                    })
        
        return dialog
    except (json.JSONDecodeError, TypeError, KeyError):
        return []

def process_enhanced_dialog_csv(csv_file_path):
    """
    处理对话CSV文件，优先从messages字段提取完整对话历史
    
    Args:
        csv_file_path: CSV文件路径
    
    Returns:
        dict: 按session_id组织的对话数据
    """
    print(f"正在读取CSV文件: {csv_file_path}")
    
    # 读取CSV文件
    df = pd.read_csv(csv_file_path)
    print(f"总共读取了 {len(df)} 条记录")
    
    # 按session_id分组，保存完整的对话历史
    sessions_full = defaultdict(list)
    sessions_simple = defaultdict(list)
    
    for idx, row in df.iterrows():
        session_id = row['session_id']
        
        # 方式1：从messages字段提取完整对话
        if pd.notna(row.get('messages')):
            messages_dialog = extract_dialog_from_messages(row['messages'])
            if messages_dialog:
                # 只保留最新的完整对话历史（去重）
                sessions_full[session_id] = messages_dialog
        
        # 方式2：从request_content和response_content构建简单对话
        request_content = str(row['request_content']) if pd.notna(row['request_content']) else ""
        response_content = str(row['response_content']) if pd.notna(row['response_content']) else ""
        
        dialog_pair = []
        if request_content.strip():
            dialog_pair.append({"role": "user", "content": request_content.strip()})
        if response_content.strip():
            dialog_pair.append({"role": "assistant", "content": response_content.strip()})
        
        if dialog_pair:
            sessions_simple[session_id].extend(dialog_pair)
    
    # 合并结果，优先使用messages字段的完整对话
    final_sessions = {}
    
    for session_id in set(list(sessions_full.keys()) + list(sessions_simple.keys())):
        if session_id in sessions_full and sessions_full[session_id]:
            # 使用messages字段的完整对话历史
            final_sessions[session_id] = sessions_full[session_id]
            print(f"Session {session_id}: 使用messages字段，{len(sessions_full[session_id])} 条消息")
        elif session_id in sessions_simple and sessions_simple[session_id]:
            # 使用简单构建的对话
            final_sessions[session_id] = sessions_simple[session_id]
            print(f"Session {session_id}: 使用简单构建，{len(sessions_simple[session_id])} 条消息")
    
    print(f"找到 {len(final_sessions)} 个不同的session")
    return final_sessions

def clean_dialog_content(content):
    """
    清理对话内容，去除特殊标记和格式化
    """
    if not content:
        return content
        
    # 去除角色标记，如 |<角色名&性别>|
    content = re.sub(r'\|<[^>]+>\|', '', content)
    
    # 清理多余的空白字符
    content = re.sub(r'\s+', ' ', content).strip()
    
    return content

def save_enhanced_conversations(sessions, output_dir):
    """
    保存转换后的对话到文件
    
    Args:
        sessions: 转换后的对话数据
        output_dir: 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存每个session的对话
    for session_id, conversation in sessions.items():
        if not conversation:  # 跳过空对话
            continue
        
        # 清理对话内容
        cleaned_conversation = []
        for msg in conversation:
            cleaned_content = clean_dialog_content(msg['content'])
            if cleaned_content:
                cleaned_conversation.append({
                    "role": msg['role'],
                    "content": cleaned_content
                })
        
        if not cleaned_conversation:
            continue
            
        filename = f"session_{session_id}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cleaned_conversation, f, ensure_ascii=False, indent=2)
        
        print(f"保存对话: {filepath} ({len(cleaned_conversation)} 条消息)")
    
    # 保存所有对话到一个文件
    all_conversations_file = os.path.join(output_dir, "all_conversations_enhanced.json")
    
    # 为所有对话创建清理后的版本
    all_cleaned = {}
    for session_id, conversation in sessions.items():
        cleaned_conversation = []
        for msg in conversation:
            cleaned_content = clean_dialog_content(msg['content'])
            if cleaned_content:
                cleaned_conversation.append({
                    "role": msg['role'],
                    "content": cleaned_content
                })
        if cleaned_conversation:
            all_cleaned[session_id] = cleaned_conversation
    
    with open(all_conversations_file, 'w', encoding='utf-8') as f:
        json.dump(all_cleaned, f, ensure_ascii=False, indent=2)
    
    print(f"保存所有对话: {all_conversations_file}")

def main():
    """主函数"""
    # CSV文件路径
    csv_file = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/固定内容session150轮至250轮对话日志.csv"
    
    # 输出目录
    output_dir = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/改进版切分后的对话"
    
    try:
        # 处理CSV文件
        sessions = process_enhanced_dialog_csv(csv_file)
        
        # 保存结果
        save_enhanced_conversations(sessions, output_dir)
        
        print("\n=== 改进版处理完成 ===")
        print(f"共处理了 {len(sessions)} 个会话")
        print(f"结果保存在: {output_dir}")
        
        # 打印统计信息
        total_messages = sum(len(conv) for conv in sessions.values())
        print(f"总消息数: {total_messages}")
        
        # 显示每个session的消息数量统计
        print("\n会话统计:")
        for session_id, conversation in sessions.items():
            print(f"  Session {session_id}: {len(conversation)} 条消息")
    
    except FileNotFoundError:
        print(f"错误: 找不到CSV文件 {csv_file}")
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()