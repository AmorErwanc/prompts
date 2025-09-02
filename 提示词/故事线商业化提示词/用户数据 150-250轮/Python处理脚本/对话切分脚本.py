#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json
import os
from collections import defaultdict

def process_dialog_csv(csv_file_path):
    """
    处理对话CSV文件，按session_id切分并转换为指定格式
    
    Args:
        csv_file_path: CSV文件路径
    
    Returns:
        dict: 按session_id组织的对话数据
    """
    print(f"正在读取CSV文件: {csv_file_path}")
    
    # 读取CSV文件
    df = pd.read_csv(csv_file_path)
    print(f"总共读取了 {len(df)} 条记录")
    
    # 按session_id分组
    sessions = defaultdict(list)
    
    for idx, row in df.iterrows():
        session_id = row['session_id']
        request_content = row['request_content']
        response_content = row['response_content']
        created_at = row['created_at']
        
        # 提取对话内容
        dialog_pair = {
            "timestamp": created_at,
            "user_input": str(request_content) if pd.notna(request_content) else "",
            "assistant_response": str(response_content) if pd.notna(response_content) else ""
        }
        
        sessions[session_id].append(dialog_pair)
    
    print(f"找到 {len(sessions)} 个不同的session")
    
    return sessions

def convert_to_target_format(sessions):
    """
    将对话数据转换为目标格式
    
    Args:
        sessions: 按session_id组织的对话数据
    
    Returns:
        dict: 转换后的对话数据
    """
    converted_sessions = {}
    
    for session_id, dialog_list in sessions.items():
        conversation = []
        
        for dialog in dialog_list:
            # 添加用户消息
            if dialog['user_input'].strip():
                conversation.append({
                    "role": "user",
                    "content": dialog['user_input'].strip()
                })
            
            # 添加助手消息
            if dialog['assistant_response'].strip():
                conversation.append({
                    "role": "assistant",
                    "content": dialog['assistant_response'].strip()
                })
        
        converted_sessions[session_id] = conversation
        print(f"Session {session_id}: {len(conversation)} 条消息")
    
    return converted_sessions

def save_conversations(converted_sessions, output_dir):
    """
    保存转换后的对话到文件
    
    Args:
        converted_sessions: 转换后的对话数据
        output_dir: 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存每个session的对话
    for session_id, conversation in converted_sessions.items():
        if not conversation:  # 跳过空对话
            continue
            
        filename = f"session_{session_id}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)
        
        print(f"保存对话: {filepath} ({len(conversation)} 条消息)")
    
    # 保存所有对话到一个文件
    all_conversations_file = os.path.join(output_dir, "all_conversations.json")
    with open(all_conversations_file, 'w', encoding='utf-8') as f:
        json.dump(converted_sessions, f, ensure_ascii=False, indent=2)
    
    print(f"保存所有对话: {all_conversations_file}")

def main():
    """主函数"""
    # CSV文件路径
    csv_file = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/固定内容session150轮至250轮对话日志.csv"
    
    # 输出目录
    output_dir = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/切分后的对话"
    
    try:
        # 处理CSV文件
        sessions = process_dialog_csv(csv_file)
        
        # 转换为目标格式
        converted_sessions = convert_to_target_format(sessions)
        
        # 保存结果
        save_conversations(converted_sessions, output_dir)
        
        print("\n=== 处理完成 ===")
        print(f"共处理了 {len(converted_sessions)} 个会话")
        print(f"结果保存在: {output_dir}")
        
        # 打印统计信息
        total_messages = sum(len(conv) for conv in converted_sessions.values())
        print(f"总消息数: {total_messages}")
        
        # 显示每个session的消息数量统计
        print("\n会话统计:")
        for session_id, conversation in converted_sessions.items():
            print(f"  Session {session_id}: {len(conversation)} 条消息")
    
    except FileNotFoundError:
        print(f"错误: 找不到CSV文件 {csv_file}")
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()