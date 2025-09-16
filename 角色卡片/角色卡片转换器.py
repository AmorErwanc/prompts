#!/usr/bin/env python3
"""
角色卡片数据转换器
功能：将CSV格式的聊天室数据转换为易读的Markdown格式
输入：CSV文件（包含JSON格式的角色数据）
输出：Markdown格式的角色卡片文档
"""

import csv
import json
import re
import sys
import os
from pathlib import Path

class CharacterCardConverter:
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        
    def has_chinese(self, text):
        """检查文本是否包含中文字符"""
        if not isinstance(text, str):
            return False
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    def extract_role_info(self, role_val):
        """从角色信息中提取关键内容"""
        if isinstance(role_val, dict):
            return role_val
        elif isinstance(role_val, str) and role_val.startswith('{'):
            try:
                return json.loads(role_val)
            except:
                return {}
        return {}
    
    def clean_text(self, text):
        """清理文本格式"""
        if not text:
            return ""
        # 移除多余的换行符和空格
        text = re.sub(r'\r\n|\r|\n', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_character_data(self, content_data, param_data):
        """提取角色的所有相关数据"""
        character = {
            'name': '未知角色',
            'background': '',
            'description': '',
            'gender': '',
            'profession': '',
            'language_style': '',
            'relationships': '',
            'history': '',
            'dialogue': '',
            'summary': ''
        }
        
        # 从content_data中提取信息
        for item in content_data:
            if item.get("type") == "system" and "content" in item:
                for content_item in item["content"]:
                    val = content_item.get("val", "")
                    if val == "背景介绍":
                        continue
                    elif len(val) > 20 and self.has_chinese(val):
                        character['background'] = val
            
            elif item.get("type") == "normal" and "role" in item:
                # 提取角色基本信息
                role_info = self.extract_role_info(item["role"].get("val", ""))
                if role_info:
                    character['name'] = role_info.get("nickname", "未知角色")
                    character['description'] = role_info.get("features", "")
                    character['summary'] = role_info.get("summary", "")
                
                # 提取对话内容
                if "content" in item:
                    for content_item in item["content"]:
                        dialogue_text = content_item.get("val", "")
                        if dialogue_text and len(dialogue_text) > 10:
                            character['dialogue'] = dialogue_text
        
        # 从param_data中提取详细设定
        try:
            for param_item in param_data:
                if isinstance(param_item, dict) and "set" in param_item:
                    for setting in param_item["set"]:
                        if setting.get("inName") == "systemPlay":
                            detailed_setting = setting.get("val", "")
                            if detailed_setting:
                                self._parse_detailed_setting(character, detailed_setting)
                            break
        except:
            pass
        
        return character
    
    def _parse_detailed_setting(self, character, detailed_setting):
        """解析详细设定信息"""
        lines = detailed_setting.split('\n')
        
        for line in lines:
            line = line.strip()
            if '性别:' in line or '性别：' in line:
                character['gender'] = line
            elif '职业:' in line or '职业：' in line:
                character['profession'] = line
            elif '语言特点:' in line or '语言特点：' in line:
                character['language_style'] = line
            elif '人物关系:' in line or '人物关系：' in line:
                character['relationships'] = line
        
        # 提取过往经历
        if '过往经历:' in detailed_setting or '过往经历：' in detailed_setting:
            history_start = detailed_setting.find('过往经历:')
            if history_start == -1:
                history_start = detailed_setting.find('过往经历：')
            if history_start != -1:
                history_text = detailed_setting[history_start:]
                history_text = history_text.replace('过往经历:', '').replace('过往经历：', '')
                character['history'] = self.clean_text(history_text)
    
    def format_character_to_markdown(self, character, index, pipe_id):
        """将角色数据格式化为Markdown"""
        md_content = []
        
        # 角色标题
        md_content.append(f"## 角色 #{index}：{character['name']}\n")
        
        # 故事背景
        if character['background']:
            md_content.append(f"### 🌟 故事背景\n{character['background']}\n")
        
        # 角色描述
        if character['description']:
            md_content.append(f"### 👤 角色描述\n{character['description']}\n")
        
        # 角色摘要
        if character['summary'] and character['summary'] != character['description']:
            md_content.append(f"### 📝 角色摘要\n{character['summary']}\n")
        
        # 基本信息
        basic_info = []
        if character['gender']:
            basic_info.append(f"- ⚥ {character['gender']}")
        if character['profession']:
            basic_info.append(f"- 💼 {character['profession']}")
        if character['language_style']:
            basic_info.append(f"- 💬 {character['language_style']}")
        if character['relationships']:
            basic_info.append(f"- 👥 {character['relationships']}")
        
        if basic_info:
            md_content.append("### 📋 基本信息")
            md_content.extend(basic_info)
            md_content.append("")
        
        # 过往经历
        if character['history']:
            md_content.append(f"### 📖 过往经历\n{character['history']}\n")
        
        # 开场对话
        if character['dialogue']:
            md_content.append(f"### 💭 开场对话\n{character['dialogue']}\n")
        
        # 数据信息
        md_content.append(f"### 🆔 数据信息\n- ID: `{pipe_id}`\n")
        md_content.append("---\n")
        
        return "\n".join(md_content)
    
    def convert_csv_to_markdown(self, input_file, output_file):
        """主转换函数：CSV -> Markdown"""
        print(f"开始处理文件: {input_file}")
        print(f"输出文件: {output_file}")
        print("-" * 50)
        
        try:
            with open(input_file, 'r', encoding='utf-8') as infile, \
                 open(output_file, 'w', encoding='utf-8') as outfile:
                
                reader = csv.reader(infile)
                headers = next(reader)  # 跳过表头
                
                # 写入Markdown文件头
                outfile.write("# 角色卡片数据整理\n\n")
                outfile.write(f"> 本文档由角色卡片转换器自动生成  \n")
                outfile.write(f"> 数据来源: {os.path.basename(input_file)}  \n")
                outfile.write(f"> 生成时间: {self._get_current_time()}\n\n")
                
                # 处理每一行数据
                for row_num, row in enumerate(reader, start=1):
                    try:
                        if len(row) >= 3:
                            pipe_id = row[0]
                            content_json = row[1]
                            param_json = row[2]
                            
                            # 解析JSON数据
                            content_data = json.loads(content_json)
                            param_data = json.loads(param_json)
                            
                            # 提取角色数据
                            character = self.extract_character_data(content_data, param_data)
                            
                            # 格式化为Markdown并写入文件
                            md_content = self.format_character_to_markdown(character, row_num, pipe_id)
                            outfile.write(md_content)
                            
                            self.processed_count += 1
                            print(f"✅ 已处理角色 #{row_num}: {character['name']}")
                            
                    except Exception as e:
                        self.error_count += 1
                        print(f"❌ 处理第 {row_num} 行时出错: {str(e)}")
                        continue
                
                # 写入文档尾部统计信息
                outfile.write(f"\n## 📊 处理统计\n\n")
                outfile.write(f"- 成功处理角色数量: {self.processed_count}\n")
                outfile.write(f"- 处理错误数量: {self.error_count}\n")
                outfile.write(f"- 总计数据行数: {self.processed_count + self.error_count}\n")
                
        except FileNotFoundError:
            print(f"❌ 错误: 找不到输入文件 {input_file}")
            return False
        except Exception as e:
            print(f"❌ 处理过程中发生错误: {str(e)}")
            return False
        
        print("-" * 50)
        print(f"🎉 转换完成！")
        print(f"📁 输出文件: {output_file}")
        print(f"📊 处理统计: 成功 {self.processed_count} 个角色，错误 {self.error_count} 个")
        return True
    
    def _get_current_time(self):
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """主函数"""
    # 配置文件路径
    input_file = '/Users/edy/Desktop/project/角色卡片/优秀聊天室数据(2).csv'
    output_file = '/Users/edy/Desktop/project/角色卡片/角色卡片易读版.md'
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        print("请检查文件路径是否正确")
        sys.exit(1)
    
    # 创建输出目录（如果不存在）
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建转换器实例并执行转换
    converter = CharacterCardConverter()
    success = converter.convert_csv_to_markdown(input_file, output_file)
    
    if success:
        print("\n✨ 转换成功完成！您可以使用以下方式查看结果：")
        print(f"📖 直接打开: {output_file}")
        print("🌐 或使用支持Markdown的编辑器（如VS Code、Typora等）")
        sys.exit(0)
    else:
        print("\n❌ 转换过程中遇到错误")
        sys.exit(1)

if __name__ == "__main__":
    main()