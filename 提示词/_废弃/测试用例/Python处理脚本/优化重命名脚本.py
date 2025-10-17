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

def rename_with_rounds_first(input_dir):
    """
    重命名对话文件，将轮次信息放在文件名开头
    
    Args:
        input_dir: 包含对话文件的目录
    """
    print(f"正在处理目录: {input_dir}")
    
    if not os.path.exists(input_dir):
        print(f"错误: 目录不存在 {input_dir}")
        return
    
    # 获取所有需要重命名的JSON文件（包括已经重命名过的）
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json') and ('session_' in f or '轮次' in f)]
    
    print(f"找到 {len(json_files)} 个对话文件")
    
    rename_log = []
    
    for filename in json_files:
        if filename == 'all_conversations.json' or filename == '重命名日志.json':
            continue  # 跳过汇总文件和日志文件
            
        filepath = os.path.join(input_dir, filename)
        
        try:
            # 读取对话文件
            with open(filepath, 'r', encoding='utf-8') as f:
                conversation = json.load(f)
            
            # 计算轮次
            rounds = count_dialog_rounds(conversation)
            total_messages = len(conversation)
            
            # 提取session_id
            if filename.startswith('session_'):
                # 从原始文件名或已重命名文件中提取session_id
                session_id = filename.split('_')[1]
                if '_' in session_id:
                    session_id = session_id.split('_')[0]
            else:
                # 如果文件名格式不标准，使用文件名的一部分
                session_id = filename.replace('.json', '').split('_')[-1][:10]
            
            # 生成新文件名：轮次优先
            new_filename = f"{rounds:03d}轮对话_共{total_messages}条消息_session{session_id}.json"
            new_filepath = os.path.join(input_dir, new_filename)
            
            # 如果新文件名与旧文件名相同，跳过
            if filename == new_filename:
                print(f"跳过: {filename} (已是最新格式)")
                continue
            
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
            
            print(f"重命名: {filename}")
            print(f"    -> {new_filename}")
        
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {str(e)}")
    
    if rename_log:
        # 保存重命名日志
        log_filepath = os.path.join(input_dir, "重命名日志_优化版.json")
        with open(log_filepath, 'w', encoding='utf-8') as f:
            json.dump(rename_log, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== 优化重命名完成 ===")
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
        print(f"\n=== 各会话轮次统计（按轮次排序）===")
        sorted_log = sorted(rename_log, key=lambda x: x['rounds'], reverse=True)
        for entry in sorted_log:
            print(f"{entry['rounds']:3d}轮对话 (Session {entry['session_id']})")
    else:
        print("没有需要重命名的文件，所有文件可能已经是最新格式。")

def main():
    """主函数"""
    input_dir = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/切分后的对话"
    
    try:
        rename_with_rounds_first(input_dir)
        
        print(f"\n=== 查看最终结果 ===")
        # 显示重命名后的文件列表（按轮次排序）
        files = [f for f in os.listdir(input_dir) if f.endswith('.json') and f.startswith('0')]
        files.sort()  # 按文件名排序，轮次数字在前面会自然排序
        
        if files:
            print("重命名后的文件列表（按轮次排序）:")
            for i, filename in enumerate(files, 1):
                print(f"{i:2d}. {filename}")
    
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()