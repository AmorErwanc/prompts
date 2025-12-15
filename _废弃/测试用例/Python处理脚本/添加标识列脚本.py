#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json
import os
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font

def load_reference_data():
    """
    加载原始的合并评测集作为参考数据
    """
    reference_csv_path = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/评测集CSV/合并总评测集_全部轮次对话.csv"
    
    try:
        reference_df = pd.read_csv(reference_csv_path, encoding='utf-8')
        print(f"成功加载参考数据: {len(reference_df)} 行")
        return reference_df
    except Exception as e:
        print(f"加载参考数据失败: {str(e)}")
        return None

def match_session_info(target_df, reference_df):
    """
    根据CHARACTER_SETTING和DIALOGUE_HISTORY匹配SESSION_ID和SEGMENT_INFO
    """
    print("开始匹配SESSION_ID和SEGMENT_INFO...")
    
    # 为目标数据添加新列
    target_df['SESSION_ID'] = ''
    target_df['SEGMENT_INFO'] = ''
    
    match_count = 0
    
    for idx, target_row in target_df.iterrows():
        target_character = target_row['CHARACTER_SETTING']
        target_dialogue = target_row['DIALOGUE_HISTORY']
        
        # 在参考数据中查找匹配项
        for _, ref_row in reference_df.iterrows():
            ref_character = ref_row['CHARACTER_SETTING']
            ref_dialogue = ref_row['DIALOGUE_HISTORY']
            
            # 精确匹配CHARACTER_SETTING和DIALOGUE_HISTORY
            if target_character == ref_character and target_dialogue == ref_dialogue:
                target_df.at[idx, 'SESSION_ID'] = ref_row['SESSION_ID']
                target_df.at[idx, 'SEGMENT_INFO'] = ref_row['SEGMENT_INFO']
                match_count += 1
                print(f"匹配成功 {match_count}/{len(target_df)}: {ref_row['SESSION_ID']} - {ref_row['SEGMENT_INFO']}")
                break
        
        if target_df.at[idx, 'SESSION_ID'] == '':
            print(f"未找到匹配项 (行 {idx + 1})")
    
    print(f"匹配完成: {match_count}/{len(target_df)} 行成功匹配")
    return target_df

def reorder_columns(df):
    """
    重新排列列的顺序，将SESSION_ID和SEGMENT_INFO放在前面
    """
    # 获取所有列名
    all_columns = df.columns.tolist()
    
    # 定义新的列顺序
    ordered_columns = ['SESSION_ID', 'SEGMENT_INFO', 'CHARACTER_SETTING', 'DIALOGUE_HISTORY']
    
    # 添加其他列（除了已经指定的）
    for col in all_columns:
        if col not in ordered_columns:
            ordered_columns.append(col)
    
    # 只保留实际存在的列
    final_columns = [col for col in ordered_columns if col in all_columns]
    
    return df[final_columns]

def save_with_formatting(df, output_path):
    """
    保存为Excel文件并设置格式
    """
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='评测数据')
        
        # 获取工作簿和工作表
        workbook = writer.book
        worksheet = writer.sheets['评测数据']
        
        # 设置列宽
        worksheet.column_dimensions['A'].width = 40  # SESSION_ID列
        worksheet.column_dimensions['B'].width = 20  # SEGMENT_INFO列
        worksheet.column_dimensions['C'].width = 80  # CHARACTER_SETTING列
        worksheet.column_dimensions['D'].width = 100  # DIALOGUE_HISTORY列
        
        # 如果有更多列，设置默认宽度
        for col_num in range(5, len(df.columns) + 1):
            column_letter = chr(64 + col_num)  # E, F, G, ...
            worksheet.column_dimensions[column_letter].width = 50
        
        # 设置单元格格式
        for row in worksheet.iter_rows():
            for cell in row:
                # 设置文本对齐方式
                cell.alignment = Alignment(
                    horizontal='left',
                    vertical='top',
                    wrap_text=True
                )
                
                # 设置字体
                if cell.row == 1:  # 标题行
                    cell.font = Font(bold=True, size=12)
                else:
                    cell.font = Font(size=10)
        
        # 设置行高
        for row_num in range(2, len(df) + 2):  # 从第2行开始（跳过标题行）
            worksheet.row_dimensions[row_num].height = 100  # 设置较大的行高以容纳多行文本

def main():
    """主函数"""
    # 输入和输出文件路径
    input_file = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/评测完成/小说章节总结生成_V1_dataset_20250902160819 (1).xlsx"
    output_file = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/评测完成/小说章节总结生成_V1_dataset_带标识列.xlsx"
    
    try:
        print(f"正在读取评测完成的Excel文件...")
        # 读取目标Excel文件
        target_df = pd.read_excel(input_file)
        print(f"成功读取目标文件: {len(target_df)} 行, {len(target_df.columns)} 列")
        print(f"列名: {list(target_df.columns)}")
        
        # 加载参考数据
        reference_df = load_reference_data()
        if reference_df is None:
            print("无法加载参考数据，程序终止")
            return
        
        # 匹配SESSION_ID和SEGMENT_INFO
        updated_df = match_session_info(target_df, reference_df)
        
        # 重新排列列顺序
        final_df = reorder_columns(updated_df)
        
        print(f"\n=== 最终数据结构 ===")
        print(f"总行数: {len(final_df)}")
        print(f"列名: {list(final_df.columns)}")
        
        # 检查匹配结果
        matched_count = len(final_df[final_df['SESSION_ID'] != ''])
        print(f"成功匹配: {matched_count}/{len(final_df)} 行")
        
        # 保存结果
        print(f"\n保存结果到: {output_file}")
        save_with_formatting(final_df, output_file)
        
        print(f"\n=== 处理完成 ===")
        print(f"输入文件: {input_file}")
        print(f"输出文件: {output_file}")
        print(f"添加了SESSION_ID和SEGMENT_INFO列")
        print(f"列宽设置: SESSION_ID(40), SEGMENT_INFO(20), CHARACTER_SETTING(80), DIALOGUE_HISTORY(100)")
        
        # 显示前几行作为预览
        print(f"\n=== 数据预览 ===")
        print(final_df[['SESSION_ID', 'SEGMENT_INFO']].head())
        
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()