#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import csv
import pandas as pd

# 角色设定常量
CHARACTER_SETTING = """你是瑟兰，正在和我进行对话
性别：男
人物关系：我是你的少爷
性格：冷漠古板，一本正经，寡言少语，礼貌冷静，优雅从容，腹黑，只对我忠犬，对我外冷内热，被我捉弄时会迅速报复回来，有仇必报，但对我会手下留情，被调戏会结巴会脸红会眼神躲闪，但被逼得没有办法会调戏回去
说话风格：你喜欢用恭敬礼貌的语气说话，讲话文雅，措辞简短优美，你喜欢冷静从容的说话方式，喜欢用礼貌的语气说强硬狠话，毒舌，对我嘴硬心软，比如：少爷，若是您继续不听话，我只能约束您的一切出行事项，请您乖乖听话，请收敛您的言行，上天把智慧洒满了人间，却给你打了把伞
过往经历：你从小接受严格的训练和礼仪指导，小时候的你怕黑，却被同伴戏弄，在树林里爬到树上摘果子时，梯子被搬走，在树上度过了两天两夜才被救回，所以你讨厌欺骗和背叛，你喜欢小动物，尤其是忠诚热情的小狗，你孤独坚强，长大后第一项任务就是保护我这个贵族少爷，你觉得我顽劣又有趣，像个调皮脆弱的小动物，需要保护和教导
人物关系：我是你需要保护的贵族少爷，我曾经流落在外20年，养成了粗鲁，顽劣，痞里痞气的性格，你受我父亲的嘱托，不仅要保护我，还有权利约束教导我的言行举止，你要把我从小混混改造成优雅的贵族少爷，而我不喜欢你古板严肃的性格，总与你对着干
你是贵族雇佣的优秀保镖，年轻，战斗力很强，礼貌恭谨，一言一行都十分端正，认真履行自己保镖的工作，你平时的表情冷漠严谨，但你情绪稳定很少生气，只有在我故意调戏你时，你会害羞和不知所措，在察觉到我讨厌并试图摆脱你时，你会真的生气发怒，生气方式是说话毒舌，态度冷硬强势
人物目的：保护我的生命安全，把我教成优雅的贵族少爷，用生命守护我
你可以将动作、神情语气、心理活动、故事背景放在（）中来表示，为对话提供补充信息。
<关键事件>
瑟兰西装内袋藏着一个褪色的金属项圈，项圈上挂着刻有"小煤球"字样的小牌子，字迹歪歪扭扭似孩子手笔。最近三天深夜，瑟兰都会独自前往庭院西北角的老树下，在那里发呆半小时。树下泥土里埋着个破瓷碗，碗里剩着半块没吃完的牛奶饼干，旁边还有几根狗毛。书房书桌最底层抽屉里放着一罐未拆封的小狗饼干，包装上有本地"尾巴尖"宠物店的标志。书房书架顶层摆着一本封面泛黄的钢琴乐谱，书页边缘卷角，扉页用铅笔写着"12岁生日·瑟兰"。庭院西北角的灌木丛后面藏着一个废弃狗屋，屋顶铺着旧茅草，门是木板钉的，门上挂着个褪色的铜铃铛。这些迹象表明瑟兰可能曾经养过一只叫"小煤球"的狗，深夜去树下或许是在怀念它，而小狗饼干和狗屋都与这只狗有着关联，那本旧乐谱则是他12岁生日时的物品。
</关键事件>"""

def load_segment_data(session_folder_path):
    """
    加载session文件夹中的所有分段数据
    
    Args:
        session_folder_path: session文件夹路径
    
    Returns:
        tuple: (session_info, segments_data)
    """
    # 读取session信息
    session_info_path = os.path.join(session_folder_path, "session_info.json")
    with open(session_info_path, 'r', encoding='utf-8') as f:
        session_info = json.load(f)
    
    # 读取所有分段数据
    segments_data = []
    for segment in session_info['segments']:
        segment_path = os.path.join(session_folder_path, segment['filename'])
        with open(segment_path, 'r', encoding='utf-8') as f:
            dialogue_data = json.load(f)
        
        # 将对话数据转换为JSON字符串
        dialogue_json = json.dumps(dialogue_data, ensure_ascii=False, separators=(',', ':'))
        
        segments_data.append({
            'filename': segment['filename'],
            'start_round': segment['start_round'],
            'end_round': segment['end_round'],
            'messages_count': segment['messages_count'],
            'dialogue_history': dialogue_json,
            'segment_info': f"第{segment['start_round']}-{segment['end_round']}轮"
        })
    
    return session_info, segments_data

def create_individual_csv(session_folder_path, output_dir):
    """
    为单个session创建CSV文件
    
    Args:
        session_folder_path: session文件夹路径
        output_dir: 输出目录
    
    Returns:
        dict: session处理信息
    """
    folder_name = os.path.basename(session_folder_path)
    session_info, segments_data = load_segment_data(session_folder_path)
    
    # 创建CSV数据
    csv_data = []
    for segment in segments_data:
        csv_data.append({
            'CHARACTER_SETTING': CHARACTER_SETTING,
            'DIALOGUE_HISTORY': segment['dialogue_history']
        })
    
    # 保存CSV文件
    csv_filename = f"{folder_name}_评测集.csv"
    csv_filepath = os.path.join(output_dir, csv_filename)
    
    df = pd.DataFrame(csv_data)
    df.to_csv(csv_filepath, index=False, encoding='utf-8')
    
    print(f"生成CSV: {csv_filename} ({len(csv_data)}行)")
    
    return {
        'session_id': session_info['session_id'],
        'folder_name': folder_name,
        'csv_filename': csv_filename,
        'total_rounds': session_info['total_rounds'],
        'segments_count': len(segments_data),
        'segments_data': segments_data  # 保存分段数据供合并使用
    }

def create_merged_csv(all_sessions_data, output_dir):
    """
    创建合并的总CSV文件
    
    Args:
        all_sessions_data: 所有session的数据
        output_dir: 输出目录
    """
    print(f"\n创建合并总CSV文件...")
    
    # 准备合并数据
    merged_data = []
    
    for session_data in all_sessions_data:
        session_id = f"{session_data['total_rounds']}轮对话_session{session_data['session_id']}"
        
        for segment in session_data['segments_data']:
            merged_data.append({
                'SESSION_ID': session_id,
                'SEGMENT_INFO': segment['segment_info'],
                'CHARACTER_SETTING': CHARACTER_SETTING,
                'DIALOGUE_HISTORY': segment['dialogue_history']
            })
    
    # 保存合并CSV文件
    merged_csv_filename = "合并总评测集_全部轮次对话.csv"
    merged_csv_filepath = os.path.join(output_dir, merged_csv_filename)
    
    df = pd.DataFrame(merged_data)
    df.to_csv(merged_csv_filepath, index=False, encoding='utf-8')
    
    print(f"生成合并CSV: {merged_csv_filename} ({len(merged_data)}行)")
    
    # 统计信息
    total_sessions = len(all_sessions_data)
    total_segments = len(merged_data)
    
    print(f"\n=== 合并CSV统计 ===")
    print(f"包含Session数: {total_sessions}")
    print(f"包含分段数: {total_segments}")
    print(f"平均每Session分段数: {total_segments / total_sessions:.1f}")
    
    return merged_csv_filepath

def process_all_sessions(input_dir, output_dir):
    """
    处理所有session文件夹，生成评测集CSV文件
    
    Args:
        input_dir: 输入目录（包含所有session文件夹）
        output_dir: 输出目录
    """
    print(f"正在处理目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有session文件夹
    session_folders = [f for f in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, f)) and f.endswith('轮对话_session')]
    # 修正文件夹匹配模式
    session_folders = [f for f in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, f)) and '轮对话_session' in f]
    
    print(f"找到 {len(session_folders)} 个session文件夹")
    
    all_sessions_data = []
    
    # 处理每个session
    for folder_name in sorted(session_folders):
        session_folder_path = os.path.join(input_dir, folder_name)
        
        try:
            session_data = create_individual_csv(session_folder_path, output_dir)
            all_sessions_data.append(session_data)
        except Exception as e:
            print(f"处理session {folder_name} 时出错: {str(e)}")
    
    print(f"\n=== 单独CSV生成完成 ===")
    print(f"成功生成 {len(all_sessions_data)} 个session CSV文件")
    
    # 创建合并CSV
    merged_csv_path = create_merged_csv(all_sessions_data, output_dir)
    
    # 生成处理日志
    log_data = {
        'total_sessions': len(all_sessions_data),
        'output_directory': output_dir,
        'merged_csv_file': os.path.basename(merged_csv_path),
        'sessions_summary': [
            {
                'session_id': s['session_id'],
                'total_rounds': s['total_rounds'],
                'csv_filename': s['csv_filename']
            } for s in all_sessions_data
        ]
    }
    
    log_filepath = os.path.join(output_dir, "评测集生成日志.json")
    with open(log_filepath, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 评测集生成完成 ===")
    print(f"单独CSV文件: {len(all_sessions_data)} 个")
    print(f"合并CSV文件: 1 个")
    print(f"处理日志: {log_filepath}")
    
    return all_sessions_data, merged_csv_path

def main():
    """主函数"""
    input_dir = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/分段后的对话"
    output_dir = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/评测集CSV"
    
    try:
        all_sessions_data, merged_csv_path = process_all_sessions(input_dir, output_dir)
        
        print(f"\n=== 最终结果 ===")
        print(f"评测集CSV文件保存在: {output_dir}")
        print(f"- 单独CSV: 20个文件")
        print(f"- 合并CSV: 1个文件")
        print(f"- 总数据行: {sum(s['segments_count'] for s in all_sessions_data) * 2} 行")  # *2因为有单独+合并
        
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()