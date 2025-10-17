#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from collections import defaultdict, Counter
from typing import Dict, List, Tuple

def analyze_json_badcase(file_path: str) -> Dict:
    """
    分析包含JSON对象的badcase文件中的错误类型
    """
    error_categories = defaultdict(int)
    error_examples = defaultdict(list)
    json_objects = []
    total_objects = 0
    valid_objects = 0

    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 尝试分割JSON对象 - 寻找完整的JSON对象
    # 这个文件似乎包含连续的JSON对象
    json_parts = []
    brace_count = 0
    current_json = ""
    in_string = False
    escape_next = False

    for char in content:
        current_json += char

        if escape_next:
            escape_next = False
            continue

        if char == '\\' and in_string:
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1

                if brace_count == 0:
                    # 找到完整的JSON对象
                    json_parts.append(current_json.strip())
                    current_json = ""

    print(f"发现 {len(json_parts)} 个JSON对象片段")

    # 分析每个JSON对象
    for i, json_str in enumerate(json_parts):
        total_objects += 1

        # 识别和修复常见问题
        error_types = analyze_single_json(json_str, i + 1)

        for error_type in error_types:
            error_categories[error_type] += 1

            # 保存错误示例
            if len(error_examples[error_type]) < 3:
                error_examples[error_type].append({
                    'object_number': i + 1,
                    'content': json_str[:200] + '...' if len(json_str) > 200 else json_str,
                    'error_details': error_type
                })

        # 尝试修复并验证JSON
        fixed_json = try_fix_json(json_str)
        try:
            json.loads(fixed_json)
            valid_objects += 1
        except:
            pass

    return {
        'total_objects': total_objects,
        'valid_objects': valid_objects,
        'error_count': total_objects - valid_objects,
        'error_categories': dict(error_categories),
        'error_examples': dict(error_examples),
        'error_rate': (total_objects - valid_objects) / total_objects * 100 if total_objects > 0 else 0
    }

def analyze_single_json(json_str: str, obj_num: int) -> List[str]:
    """
    分析单个JSON字符串中的错误类型
    """
    errors = []

    # 1. 检查双引号转义问题
    if '""' in json_str and not r'\"' in json_str:
        errors.append('双引号转义错误')

    # 2. 检查尾随逗号
    if re.search(r',\s*[}\]]', json_str):
        errors.append('尾随逗号')

    # 3. 检查缺少逗号
    if re.search(r'"\s*\n\s*"[^,}:\]]', json_str):
        errors.append('缺少逗号分隔')

    # 4. 检查未闭合字符串
    string_pattern = r'"[^"]*$'
    if re.search(string_pattern, json_str, re.MULTILINE):
        errors.append('未闭合字符串')

    # 5. 检查键名格式
    if re.search(r'[{\s,][^"]*[^"\s]:\s*', json_str):
        errors.append('键名缺少引号')

    # 6. 检查控制字符
    if re.search(r'[\x00-\x1f]', json_str):
        errors.append('包含控制字符')

    # 7. 检查中文引号
    if re.search(r'[""''『』【】]', json_str):
        errors.append('使用中文标点符号')

    # 8. 尝试解析检查语法错误
    try:
        json.loads(json_str)
    except json.JSONDecodeError as e:
        error_msg = str(e).lower()
        if 'expecting' in error_msg and 'delimiter' in error_msg:
            errors.append('分隔符错误')
        elif 'expecting property name' in error_msg:
            errors.append('属性名格式错误')
        elif 'expecting value' in error_msg:
            errors.append('缺少属性值')
        elif 'unterminated string' in error_msg:
            errors.append('未终止字符串')
        elif 'extra data' in error_msg:
            errors.append('多余数据')
        elif 'control character' in error_msg:
            errors.append('控制字符错误')
        else:
            errors.append('其他JSON语法错误')

    return errors if errors else ['格式正确']

def try_fix_json(json_str: str) -> str:
    """
    尝试修复常见的JSON格式错误
    """
    fixed = json_str

    # 1. 修复双引号转义
    fixed = fixed.replace('""', '"')

    # 2. 移除尾随逗号
    fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)

    # 3. 修复中文引号
    fixed = fixed.replace('"', '"').replace('"', '"')
    fixed = fixed.replace(''', "'").replace(''', "'")

    return fixed

def print_detailed_report(report: Dict):
    """
    打印详细分析报告
    """
    print("\n" + "="*80)
    print("📊 故事线BadCase JSON格式错误详细分析报告")
    print("="*80)

    print(f"\n📈 总体统计:")
    print(f"  • 发现JSON对象总数: {report['total_objects']:,}")
    print(f"  • 格式正确的对象: {report['valid_objects']:,}")
    print(f"  • 存在错误的对象: {report['error_count']:,}")
    print(f"  • 错误率: {report['error_rate']:.1f}%")

    print(f"\n🔍 错误类型统计 (按频率排序):")
    sorted_errors = sorted(report['error_categories'].items(),
                          key=lambda x: x[1], reverse=True)

    for error_type, count in sorted_errors:
        if error_type == '格式正确':
            continue
        percentage = count / sum(report['error_categories'].values()) * 100
        print(f"  • {error_type}: {count:,} 次 ({percentage:.1f}%)")

    print(f"\n📝 主要错误类型示例:")
    for error_type, examples in report['error_examples'].items():
        if error_type == '格式正确' or not examples:
            continue

        print(f"\n  🔸 {error_type}:")
        for example in examples[:2]:  # 只显示前2个示例
            print(f"    - 对象 #{example['object_number']}:")
            print(f"      内容: {example['content'][:150]}...")
            print(f"      问题: {example['error_details']}")

    # 提供修复建议
    print(f"\n💡 修复建议:")
    if '双引号转义错误' in report['error_categories']:
        print(f"  • 修复双引号转义: 将 \"\" 替换为 \"")
    if '尾随逗号' in report['error_categories']:
        print(f"  • 移除尾随逗号: 删除对象或数组末尾的多余逗号")
    if '使用中文标点符号' in report['error_categories']:
        print(f"  • 替换中文标点: 将中文引号替换为英文引号")
    if '控制字符错误' in report['error_categories']:
        print(f"  • 清理控制字符: 移除不可见的控制字符")

if __name__ == "__main__":
    file_path = "/Users/edy/Desktop/project/idea flow/提示词/故事线商业化提示词/badcase/故事线badcase.csv"

    print("🔍 开始分析故事线BadCase文件中的JSON格式错误...")

    try:
        report = analyze_json_badcase(file_path)
        print_detailed_report(report)

    except Exception as e:
        print(f"❌ 分析过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()