#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
import re
from collections import defaultdict
from typing import Dict, List, Tuple

def analyze_json_errors(csv_file_path: str) -> Dict:
    """
    分析CSV文件中JSON格式错误的类型和统计信息
    """
    error_categories = defaultdict(int)
    error_examples = defaultdict(list)
    total_rows = 0
    valid_json_count = 0

    # 常见JSON错误模式
    error_patterns = {
        '缺失引号': r'[{\s,]([a-zA-Z_][a-zA-Z0-9_]*)\s*:',  # 键没有引号
        '多余逗号': r',\s*[}\]]',  # 末尾多余逗号
        '缺失逗号': r'"\s*\n\s*"[^,}]',  # 缺少逗号分隔
        '单引号错误': r"'[^']*'",  # 使用单引号而非双引号
        '转义字符错误': r'\\[^"\\\/bfnrt]',  # 无效的转义字符
        '未闭合字符串': r'"[^"]*$',  # 字符串未正确闭合
        '中文引号': r'[""]',  # 使用中文引号
        '注释': r'//.*$|/\*.*?\*/',  # JSON中不允许注释
        '尾随逗号': r',(\s*[}\]])',  # 对象或数组末尾的逗号
        '键值格式错误': r'[{\s,][^"]*[^"\s]:\s*',  # 键不是字符串格式
    }

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            # 读取整个文件内容
            content = file.read()

            # 尝试解析为JSON
            try:
                json_data = json.loads(content)
                print("✅ 整个文件是有效的JSON格式")
                return {"status": "valid", "message": "文件是有效的JSON格式"}
            except json.JSONDecodeError as e:
                print(f"❌ 文件不是有效的JSON格式，开始逐行分析...")
                print(f"主要错误: {str(e)}")

            # 重新读取文件进行逐行分析
            file.seek(0)

            # 如果是CSV格式，按行处理
            lines = content.split('\n')
            for i, line in enumerate(lines):
                total_rows += 1
                line = line.strip()

                if not line:
                    continue

                # 尝试解析每行为JSON
                try:
                    json.loads(line)
                    valid_json_count += 1
                except json.JSONDecodeError as e:
                    error_type = classify_json_error(line, str(e), error_patterns)
                    error_categories[error_type] += 1

                    # 保存错误示例（限制数量）
                    if len(error_examples[error_type]) < 3:
                        error_examples[error_type].append({
                            'line_number': i + 1,
                            'content': line[:200] + '...' if len(line) > 200 else line,
                            'error_message': str(e)
                        })

    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        return {"status": "error", "message": str(e)}

    # 生成分析报告
    report = {
        'total_rows': total_rows,
        'valid_json_count': valid_json_count,
        'error_count': total_rows - valid_json_count,
        'error_categories': dict(error_categories),
        'error_examples': dict(error_examples),
        'error_rate': (total_rows - valid_json_count) / total_rows * 100 if total_rows > 0 else 0
    }

    return report

def classify_json_error(content: str, error_message: str, patterns: Dict) -> str:
    """
    根据内容和错误信息分类JSON错误类型
    """
    error_msg_lower = error_message.lower()

    # 基于错误消息的分类
    if 'expecting property name' in error_msg_lower:
        return '属性名错误'
    elif 'expecting' in error_msg_lower and 'delimiter' in error_msg_lower:
        return '分隔符错误'
    elif 'unterminated string' in error_msg_lower:
        return '未终止字符串'
    elif 'expecting value' in error_msg_lower:
        return '缺少值'
    elif 'trailing comma' in error_msg_lower:
        return '尾随逗号'
    elif 'duplicate key' in error_msg_lower:
        return '重复键'
    elif 'control character' in error_msg_lower:
        return '控制字符错误'
    elif 'escape' in error_msg_lower:
        return '转义字符错误'

    # 基于内容模式的分类
    for pattern_name, pattern in patterns.items():
        if re.search(pattern, content):
            return pattern_name

    # 其他未分类错误
    return '其他格式错误'

def print_analysis_report(report: Dict):
    """
    打印分析报告
    """
    print("\n" + "="*60)
    print("📊 JSON格式错误分析报告")
    print("="*60)

    print(f"\n📈 基本统计:")
    print(f"  • 总行数: {report['total_rows']:,}")
    print(f"  • 有效JSON行数: {report['valid_json_count']:,}")
    print(f"  • 错误行数: {report['error_count']:,}")
    print(f"  • 错误率: {report['error_rate']:.2f}%")

    print(f"\n🔍 错误类型分布:")
    sorted_errors = sorted(report['error_categories'].items(), key=lambda x: x[1], reverse=True)
    for error_type, count in sorted_errors:
        percentage = count / report['error_count'] * 100 if report['error_count'] > 0 else 0
        print(f"  • {error_type}: {count:,} 次 ({percentage:.1f}%)")

    print(f"\n📝 错误示例:")
    for error_type, examples in report['error_examples'].items():
        print(f"\n  🔸 {error_type}:")
        for example in examples[:2]:  # 只显示前2个示例
            print(f"    - 第{example['line_number']}行: {example['content'][:100]}...")
            print(f"      错误信息: {example['error_message']}")

if __name__ == "__main__":
    csv_file_path = "/Users/edy/Desktop/project/idea flow/提示词/故事线商业化提示词/badcase/故事线badcase.csv"

    print("🔍 开始分析JSON格式错误...")
    report = analyze_json_errors(csv_file_path)

    if report.get("status") == "error":
        print(f"❌ 分析失败: {report['message']}")
    elif report.get("status") == "valid":
        print(f"✅ {report['message']}")
    else:
        print_analysis_report(report)