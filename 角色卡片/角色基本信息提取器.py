#!/usr/bin/env python3
"""
角色基本信息提取器
功能：从CSV聊天室数据中提取角色的基本信息（姓名、性别、特征描述）
输入：CSV文件（包含JSON格式的角色数据）
输出：CSV文件（包含name, gender, features三个字段）
"""

import csv
import json
import sys
import os

class CharacterInfoExtractor:
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        self.characters = []
    
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
    
    def extract_character_basic_info(self, content_data, param_data):
        """提取角色基本信息：姓名、性别、特征"""
        character = {
            'name': '',
            'gender': '',
            'features': ''
        }
        
        # 从content_data中提取信息
        for item in content_data:
            if item.get("type") == "normal" and "role" in item:
                # 提取角色基本信息
                role_info = self.extract_role_info(item["role"].get("val", ""))
                if role_info:
                    # 获取角色名字
                    character['name'] = role_info.get("nickname", "").strip()
                    
                    # 获取性别
                    character['gender'] = role_info.get("gender", "").strip()
                    
                    # 获取特征描述
                    features = role_info.get("features", "").strip()
                    # 清理features中的换行符，保持单行格式
                    if features:
                        features = features.replace('\n', ' ').replace('\r', ' ')
                        # 移除多余空格
                        features = ' '.join(features.split())
                    character['features'] = features
                
                break  # 找到第一个角色信息后跳出
        
        # 如果从content_data中没有找到完整信息，尝试从param_data中提取
        if not character['name'] or not character['gender']:
            try:
                for param_item in param_data:
                    if isinstance(param_item, dict) and "set" in param_item:
                        for setting in param_item["set"]:
                            # 查找性别信息
                            if setting.get("inName") == "sys_gender" and not character['gender']:
                                gender = setting.get("val", "").strip()
                                if gender and gender != "无":
                                    character['gender'] = gender
                            
                            # 查找角色名或详细设定
                            elif setting.get("inName") == "primary_bot_name" and not character['name']:
                                # 这里通常是ID，我们跳过
                                pass
                            
                            elif setting.get("inName") == "systemPlay" and not character['features']:
                                detailed_setting = setting.get("val", "")
                                if detailed_setting:
                                    # 从详细设定中提取特征
                                    features = self._extract_features_from_setting(detailed_setting)
                                    if features:
                                        character['features'] = features
            except:
                pass
        
        return character
    
    def _extract_features_from_setting(self, setting_text):
        """从详细设定中提取特征描述"""
        if not setting_text:
            return ""
        
        # 寻找角色描述的关键部分
        lines = setting_text.split('\n')
        features_parts = []
        
        for line in lines:
            line = line.strip()
            if any(keyword in line for keyword in ['职业：', '职业:', '语言特点:', '语言特点：', '人物关系:', '人物关系：']):
                features_parts.append(line)
            elif line.startswith('你是') and len(line) > 20:
                # 通常是角色的基本介绍
                features_parts.append(line)
                break
        
        if features_parts:
            result = ' '.join(features_parts)
            # 清理格式
            result = result.replace('\r', ' ').replace('\n', ' ')
            result = ' '.join(result.split())  # 移除多余空格
            return result
        
        # 如果没有找到特定格式，返回前200个字符作为特征描述
        clean_text = setting_text.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
        clean_text = ' '.join(clean_text.split())
        return clean_text[:200] + "..." if len(clean_text) > 200 else clean_text
    
    def process_csv_data(self, input_file):
        """处理CSV数据，提取角色基本信息"""
        print(f"开始处理文件: {input_file}")
        print("-" * 50)
        
        try:
            with open(input_file, 'r', encoding='utf-8') as infile:
                reader = csv.reader(infile)
                headers = next(reader)  # 跳过表头
                
                for row_num, row in enumerate(reader, start=1):
                    try:
                        if len(row) >= 3:
                            pipe_id = row[0]
                            content_json = row[1]
                            param_json = row[2]
                            
                            # 解析JSON数据
                            content_data = json.loads(content_json)
                            param_data = json.loads(param_json)
                            
                            # 提取角色基本信息
                            character = self.extract_character_basic_info(content_data, param_data)
                            
                            # 只保存有名字的角色
                            if character['name']:
                                self.characters.append(character)
                                self.processed_count += 1
                                print(f"✅ 提取角色 #{row_num}: {character['name']} ({character['gender']})")
                            else:
                                print(f"⚠️  跳过第 {row_num} 行: 未找到角色名字")
                            
                    except Exception as e:
                        self.error_count += 1
                        print(f"❌ 处理第 {row_num} 行时出错: {str(e)}")
                        continue
        
        except FileNotFoundError:
            print(f"❌ 错误: 找不到输入文件 {input_file}")
            return False
        except Exception as e:
            print(f"❌ 处理过程中发生错误: {str(e)}")
            return False
        
        return True
    
    def save_to_csv(self, output_file):
        """将提取的角色信息保存到CSV文件"""
        try:
            with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.writer(outfile)
                
                # 写入表头
                writer.writerow(['name', 'gender', 'features'])
                
                # 写入角色数据
                for character in self.characters:
                    writer.writerow([
                        character['name'],
                        character['gender'],
                        character['features']
                    ])
            
            return True
        
        except Exception as e:
            print(f"❌ 保存文件时出错: {str(e)}")
            return False
    
    def remove_duplicates(self):
        """去除重复的角色（基于角色名字）"""
        seen_names = set()
        unique_characters = []
        duplicates_count = 0
        
        for character in self.characters:
            name = character['name']
            if name not in seen_names:
                seen_names.add(name)
                unique_characters.append(character)
            else:
                duplicates_count += 1
        
        self.characters = unique_characters
        print(f"🔄 去重完成: 移除了 {duplicates_count} 个重复角色")
        return duplicates_count
    
    def print_statistics(self):
        """打印处理统计信息"""
        print("-" * 50)
        print(f"📊 处理统计:")
        print(f"   - 成功提取角色: {self.processed_count}")
        print(f"   - 最终保存角色: {len(self.characters)}")
        print(f"   - 处理错误: {self.error_count}")
        
        # 显示角色名字列表
        if self.characters:
            print(f"\n📝 提取的角色列表:")
            for i, char in enumerate(self.characters, 1):
                gender_display = f"({char['gender']})" if char['gender'] else ""
                print(f"   {i:2d}. {char['name']} {gender_display}")

def main():
    """主函数"""
    # 配置文件路径
    input_file = '/Users/edy/Desktop/project/角色卡片/优秀聊天室数据(2).csv'
    output_file = '/Users/edy/Desktop/project/角色卡片/角色基本信息.csv'
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        print("请检查文件路径是否正确")
        sys.exit(1)
    
    # 创建提取器实例
    extractor = CharacterInfoExtractor()
    
    # 处理数据
    if extractor.process_csv_data(input_file):
        # 去除重复角色
        extractor.remove_duplicates()
        
        # 保存结果
        if extractor.save_to_csv(output_file):
            extractor.print_statistics()
            print(f"\n✨ 提取完成！")
            print(f"📁 输出文件: {output_file}")
            print(f"🎯 共提取 {len(extractor.characters)} 个独特角色的基本信息")
        else:
            print("\n❌ 保存文件失败")
            sys.exit(1)
    else:
        print("\n❌ 数据处理失败")
        sys.exit(1)

if __name__ == "__main__":
    main()