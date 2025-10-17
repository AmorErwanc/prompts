#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import shutil

def count_dialog_rounds(conversation):
    """
    计算对话轮次数
    一轮 = 一个user消息 + 一个assistant消息的配对
    
    Args:
        conversation: 包含role和content的对话列表
    
    Returns:
        int: 对话轮次数
    """
    if not conversation:
        return 0
    
    rounds = 0
    user_count = 0
    assistant_count = 0
    
    for msg in conversation:
        if msg.get('role') == 'user':
            user_count += 1
        elif msg.get('role') == 'assistant':
            assistant_count += 1
    
    # 一轮对话需要一个user和一个assistant消息
    # 取较小值作为完整轮次数
    rounds = min(user_count, assistant_count)
    
    return rounds

def rename_conversation_files(input_dir):
    """
    重命名对话文件，添加轮次信息
    
    Args:
        input_dir: 包含对话文件的目录
    """
    print(f"正在处理目录: {input_dir}")
    
    if not os.path.exists(input_dir):
        print(f"错误: 目录不存在 {input_dir}")
        return
    
    # 获取所有JSON文件
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json') and f.startswith('session_')]
    
    print(f"找到 {len(json_files)} 个session文件")
    
    rename_log = []
    
    for filename in json_files:
        filepath = os.path.join(input_dir, filename)
        
        try:
            # 读取对话文件
            with open(filepath, 'r', encoding='utf-8') as f:
                conversation = json.load(f)
            
            # 计算轮次
            rounds = count_dialog_rounds(conversation)
            total_messages = len(conversation)
            
            # 提取session_id
            session_id = filename.replace('session_', '').replace('.json', '')
            
            # 生成新文件名
            new_filename = f"session_{session_id}_{rounds}轮次_{total_messages}条消息.json"
            new_filepath = os.path.join(input_dir, new_filename)
            
            # 重命名文件
            shutil.move(filepath, new_filepath)
            
            log_entry = {
                'session_id': session_id,
                'old_filename': filename,
                'new_filename': new_filename,
                'rounds': rounds,
                'total_messages': total_messages
            }
            rename_log.append(log_entry)
            
            print(f"重命名: {filename} -> {new_filename}")
            print(f"  轮次: {rounds}，总消息数: {total_messages}")
        
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {str(e)}")
    
    # 保存重命名日志
    log_filepath = os.path.join(input_dir, "重命名日志.json")
    with open(log_filepath, 'w', encoding='utf-8') as f:
        json.dump(rename_log, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 重命名完成 ===")
    print(f"处理了 {len(rename_log)} 个文件")
    print(f"重命名日志保存在: {log_filepath}")
    
    # 统计信息
    total_rounds = sum(entry['rounds'] for entry in rename_log)
    total_messages = sum(entry['total_messages'] for entry in rename_log)
    
    print(f"\n=== 统计信息 ===")
    print(f"总轮次数: {total_rounds}")
    print(f"总消息数: {total_messages}")
    print(f"平均每个会话轮次: {total_rounds / len(rename_log):.1f}")
    
    # 按轮次排序显示
    print(f"\n=== 各会话轮次统计 ===")
    sorted_log = sorted(rename_log, key=lambda x: x['rounds'], reverse=True)
    for entry in sorted_log:
        print(f"Session {entry['session_id']}: {entry['rounds']}轮次 ({entry['total_messages']}条消息)")

def main():
    """主函数"""
    input_dir = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/切分后的对话"
    
    try:
        rename_conversation_files(input_dir)
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()