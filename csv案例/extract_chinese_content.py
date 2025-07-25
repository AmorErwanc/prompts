#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
好人坏人挑战游戏CSV数据解析程序
提取所有案例的中文文字信息
"""

import csv
import json
import re
from typing import Dict, List, Any
from collections import OrderedDict

def extract_chinese_text(obj: Any, path: str = "") -> Dict[str, str]:
    """递归提取JSON对象中的所有中文文本"""
    chinese_texts = OrderedDict()
    
    # 定义中文正则表达式
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]+')
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            chinese_texts.update(extract_chinese_text(value, new_path))
            
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_path = f"{path}[{i}]"
            chinese_texts.update(extract_chinese_text(item, new_path))
            
    elif isinstance(obj, str):
        # 检查是否包含中文
        if chinese_pattern.search(obj):
            # 清理文本，去除多余的空格和换行
            clean_text = obj.strip()
            if clean_text:
                chinese_texts[path] = clean_text
                
    return chinese_texts

def parse_case_content(content_json: str) -> Dict[str, Any]:
    """解析单个案例的内容"""
    try:
        content = json.loads(content_json)
        case_info = {
            '背景介绍': '',
            '角色名称': '',
            '角色性别': '',
            '角色设定': '',
            '内在人设': '',
            '开场白': '',
            '好人结局': '',
            '坏人结局': '',
            'AI模型': '',
            '其他中文内容': []
        }
        
        # 提取content部分的文本
        if isinstance(content, list) and len(content) > 0:
            for item in content:
                if 'content' in item and isinstance(item['content'], list):
                    for content_item in item['content']:
                        if 'val' in content_item:
                            val = content_item['val']
                            # 检查是否是背景介绍的内容
                            if 'outName' in content_item and content_item.get('inName') == 'none':
                                # 这通常是背景介绍的实际内容
                                if len(val) > 10 and '背景' not in val:
                                    case_info['背景介绍'] = val
        
        # 提取所有中文文本
        chinese_texts = extract_chinese_text(content)
        
        # 补充其他信息
        for path, text in chinese_texts.items():
            if 'nickname' in path:
                case_info['角色名称'] = text
            elif 'gender' in path:
                case_info['角色性别'] = text
            elif 'features' in path:
                case_info['角色设定'] = text
            elif '内在人设' in text:
                case_info['内在人设'] = text
            elif 'initChat' in path or '开场' in text:
                case_info['开场白'] = text
            elif '好人' in text and '结局' in text:
                case_info['好人结局'] = text
            elif '坏人' in text and '结局' in text:
                case_info['坏人结局'] = text
            elif 'model' in path and 'ep-' in text:
                case_info['AI模型'] = text
                    
        return case_info
        
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return {}

def parse_in_param(in_param_json: str) -> Dict[str, str]:
    """解析输入参数中的中文内容"""
    try:
        in_param = json.loads(in_param_json)
        chinese_texts = extract_chinese_text(in_param)
        return chinese_texts
    except json.JSONDecodeError:
        return {}

def main():
    """主程序"""
    csv_file = '/Users/edy/Desktop/project/挑战玩法/csv案例/好人坏人挑战数据.csv'
    
    all_cases = []
    
    # 读取CSV文件
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row_num, row in enumerate(csv_reader, 1):
            pipe_id = row['pipe_id']
            content = row['content']
            in_param = row['in_param']
            
            print(f"\n{'='*80}")
            print(f"案例 {row_num}: {pipe_id}")
            print(f"{'='*80}")
            
            # 解析content中的内容
            case_info = parse_case_content(content)
            
            # 解析in_param中的内容
            param_info = parse_in_param(in_param)
            
            # 合并信息
            full_case = {
                '案例ID': pipe_id,
                '案例编号': row_num,
                **case_info
            }
            
            # 打印案例信息
            for key, value in full_case.items():
                if key == '其他中文内容' and value:
                    print(f"\n{key}:")
                    for i, text in enumerate(value, 1):
                        print(f"  {i}. {text}")
                elif value and key != '案例ID' and key != '案例编号':
                    print(f"\n{key}: {value}")
            
            # 从in_param中提取额外信息
            if param_info:
                print("\n从参数中提取的额外信息:")
                unique_params = {}
                for path, text in param_info.items():
                    # 过滤掉已经在case_info中的内容
                    if text not in str(case_info.values()):
                        unique_params[text] = path
                
                for text in unique_params:
                    print(f"  - {text}")
            
            all_cases.append(full_case)
    
    # 统计总结
    print(f"\n\n{'='*80}")
    print("数据统计总结")
    print(f"{'='*80}")
    print(f"总案例数: {len(all_cases)}")
    
    # 统计角色名称
    role_names = [case['角色名称'] for case in all_cases if case['角色名称']]
    print(f"\n所有角色: {', '.join(role_names)}")
    
    # 统计有完整信息的案例
    complete_cases = []
    for case in all_cases:
        if all([case['背景介绍'], case['角色名称'], case['角色设定'], case['开场白']]):
            complete_cases.append(case)
    
    print(f"\n信息完整的案例数: {len(complete_cases)}")
    
    # 保存结果到文件
    output_file = '/Users/edy/Desktop/project/挑战玩法/csv案例/extracted_chinese_content.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_cases, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_file}")

if __name__ == "__main__":
    main()