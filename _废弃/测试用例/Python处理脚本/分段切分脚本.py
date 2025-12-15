#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import math

def create_dialog_segments(conversation, segment_size=50):
    """
    将对话按轮次分段
    
    Args:
        conversation: 完整对话列表
        segment_size: 每段的轮次数（默认50轮）
    
    Returns:
        list: 分段后的对话列表
    """
    segments = []
    current_segment = []
    user_count = 0
    assistant_count = 0
    current_rounds = 0
    
    for msg in conversation:
        current_segment.append(msg)
        
        if msg.get('role') == 'user':
            user_count += 1
        elif msg.get('role') == 'assistant':
            assistant_count += 1
            # 当user和assistant都有消息时，算作一轮完成
            if user_count > 0 and assistant_count > 0:
                current_rounds = min(user_count, assistant_count)
                
                # 如果达到分段大小，开始新分段
                if current_rounds >= segment_size:
                    segments.append({
                        'messages': current_segment.copy(),
                        'rounds': current_rounds,
                        'start_round': len(segments) * segment_size + 1,
                        'end_round': len(segments) * segment_size + current_rounds
                    })
                    
                    current_segment = []
                    user_count = 0
                    assistant_count = 0
                    current_rounds = 0
    
    # 添加最后一段（如果有剩余）
    if current_segment:
        final_rounds = min(user_count, assistant_count)
        if final_rounds > 0:
            segments.append({
                'messages': current_segment,
                'rounds': final_rounds,
                'start_round': len(segments) * segment_size + 1,
                'end_round': len(segments) * segment_size + final_rounds
            })
    
    return segments

def process_conversation_segments(input_dir, output_dir, segment_size=50):
    """
    处理所有对话文件，为每个session创建分段
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        segment_size: 每段轮次数
    """
    print(f"正在处理目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"分段大小: {segment_size}轮/段")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有对话文件
    dialog_files = [f for f in os.listdir(input_dir) if f.endswith('.json') and f.startswith('2')]
    
    print(f"找到 {len(dialog_files)} 个对话文件")
    
    processing_log = []
    
    for filename in dialog_files:
        filepath = os.path.join(input_dir, filename)
        
        try:
            # 从文件名提取轮次信息
            parts = filename.split('_')
            total_rounds = int(parts[0].replace('轮对话', ''))
            total_messages = int(parts[1].replace('共', '').replace('条消息', ''))
            session_id = parts[2].replace('session', '').replace('.json', '')
            
            print(f"\n处理: {filename}")
            print(f"总轮次: {total_rounds}, 总消息: {total_messages}")
            
            # 读取对话文件
            with open(filepath, 'r', encoding='utf-8') as f:
                conversation = json.load(f)
            
            # 创建session文件夹
            session_folder_name = f"{total_rounds}轮对话_session{session_id}"
            session_folder_path = os.path.join(output_dir, session_folder_name)
            os.makedirs(session_folder_path, exist_ok=True)
            
            # 按50轮分段
            segments = create_dialog_segments_v2(conversation, segment_size)
            
            segment_files = []
            
            for i, segment in enumerate(segments, 1):
                start_round = (i - 1) * segment_size + 1
                end_round = min(i * segment_size, total_rounds)
                actual_rounds = len([msg for msg in segment if msg.get('role') == 'user'])
                
                # 生成分段文件名
                segment_filename = f"第{start_round}-{end_round}轮_共{len(segment)}条消息.json"
                segment_filepath = os.path.join(session_folder_path, segment_filename)
                
                # 保存分段文件
                with open(segment_filepath, 'w', encoding='utf-8') as f:
                    json.dump(segment, f, ensure_ascii=False, indent=2)
                
                segment_files.append({
                    'filename': segment_filename,
                    'start_round': start_round,
                    'end_round': end_round,
                    'messages_count': len(segment)
                })
                
                print(f"  分段 {i}: {segment_filename} ({len(segment)}条消息)")
            
            # 创建session信息文件
            session_info = {
                'session_id': session_id,
                'total_rounds': total_rounds,
                'total_messages': total_messages,
                'segment_size': segment_size,
                'total_segments': len(segments),
                'segments': segment_files,
                'original_file': filename
            }
            
            info_filepath = os.path.join(session_folder_path, "session_info.json")
            with open(info_filepath, 'w', encoding='utf-8') as f:
                json.dump(session_info, f, ensure_ascii=False, indent=2)
            
            processing_log.append({
                'session_id': session_id,
                'total_rounds': total_rounds,
                'total_segments': len(segments),
                'folder_name': session_folder_name
            })
            
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {str(e)}")
    
    # 保存处理日志
    log_filepath = os.path.join(output_dir, "分段处理日志.json")
    with open(log_filepath, 'w', encoding='utf-8') as f:
        json.dump(processing_log, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 分段处理完成 ===")
    print(f"处理了 {len(processing_log)} 个session")
    print(f"处理日志保存在: {log_filepath}")
    
    # 统计信息
    total_segments = sum(log['total_segments'] for log in processing_log)
    print(f"总共生成了 {total_segments} 个分段文件")
    
    return processing_log

def create_dialog_segments_v2(conversation, segment_size=50):
    """
    改进的对话分段方法，更准确地按轮次分段
    
    Args:
        conversation: 完整对话列表
        segment_size: 每段的轮次数
    
    Returns:
        list: 分段后的对话列表
    """
    segments = []
    current_segment = []
    current_round = 0
    
    i = 0
    while i < len(conversation):
        msg = conversation[i]
        current_segment.append(msg)
        
        # 如果当前是user消息，检查下一个是否是assistant消息
        if msg.get('role') == 'user' and i + 1 < len(conversation):
            next_msg = conversation[i + 1]
            if next_msg.get('role') == 'assistant':
                current_segment.append(next_msg)
                current_round += 1
                i += 2  # 跳过下一个消息，因为已经处理了
                
                # 检查是否需要开始新分段
                if current_round >= segment_size:
                    segments.append(current_segment.copy())
                    current_segment = []
                    current_round = 0
            else:
                i += 1
        else:
            i += 1
    
    # 添加最后一段（如果有剩余）
    if current_segment:
        segments.append(current_segment)
    
    return segments

def main():
    """主函数"""
    input_dir = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/切分后的对话"
    output_dir = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/分段后的对话"
    segment_size = 50  # 每段50轮
    
    try:
        processing_log = process_conversation_segments(input_dir, output_dir, segment_size)
        
        print(f"\n=== 文件夹结构预览 ===")
        # 显示生成的文件夹结构
        for log in processing_log[:3]:  # 只显示前3个作为示例
            folder_name = log['folder_name']
            print(f"{folder_name}/ ({log['total_segments']}个分段)")
        
        if len(processing_log) > 3:
            print(f"... 还有 {len(processing_log) - 3} 个session文件夹")
    
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()