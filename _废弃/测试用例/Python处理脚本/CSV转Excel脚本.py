#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils.dataframe import dataframe_to_rows

def convert_csv_to_excel(csv_file_path, excel_file_path):
    """
    将CSV文件转换为Excel文件，并设置格式
    
    Args:
        csv_file_path: CSV文件路径
        excel_file_path: Excel文件输出路径
    """
    # 读取CSV文件
    df = pd.read_csv(csv_file_path, encoding='utf-8')
    
    # 保存为Excel文件
    with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='评测数据')
        
        # 获取工作簿和工作表
        workbook = writer.book
        worksheet = writer.sheets['评测数据']
        
        # 设置列宽
        if 'CHARACTER_SETTING' in df.columns:
            worksheet.column_dimensions['A'].width = 80  # CHARACTER_SETTING列
            if 'DIALOGUE_HISTORY' in df.columns:
                worksheet.column_dimensions['B'].width = 100  # DIALOGUE_HISTORY列
        elif 'SESSION_ID' in df.columns:
            # 合并CSV的格式
            worksheet.column_dimensions['A'].width = 40  # SESSION_ID列
            worksheet.column_dimensions['B'].width = 20  # SEGMENT_INFO列
            worksheet.column_dimensions['C'].width = 80  # CHARACTER_SETTING列
            worksheet.column_dimensions['D'].width = 100  # DIALOGUE_HISTORY列
        
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

def convert_all_csv_to_excel(csv_dir, excel_dir):
    """
    将目录中的所有CSV文件转换为Excel文件
    
    Args:
        csv_dir: CSV文件目录
        excel_dir: Excel文件输出目录
    """
    print(f"正在处理CSV目录: {csv_dir}")
    print(f"Excel输出目录: {excel_dir}")
    
    # 创建输出目录
    os.makedirs(excel_dir, exist_ok=True)
    
    # 获取所有CSV文件
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    conversion_log = []
    
    for csv_filename in csv_files:
        csv_file_path = os.path.join(csv_dir, csv_filename)
        
        # 生成Excel文件名
        excel_filename = csv_filename.replace('.csv', '.xlsx')
        excel_file_path = os.path.join(excel_dir, excel_filename)
        
        try:
            print(f"转换: {csv_filename} -> {excel_filename}")
            convert_csv_to_excel(csv_file_path, excel_file_path)
            
            # 获取文件大小信息
            csv_size = os.path.getsize(csv_file_path)
            excel_size = os.path.getsize(excel_file_path)
            
            conversion_log.append({
                'csv_filename': csv_filename,
                'excel_filename': excel_filename,
                'csv_size_kb': round(csv_size / 1024, 2),
                'excel_size_kb': round(excel_size / 1024, 2),
                'status': 'success'
            })
            
        except Exception as e:
            print(f"转换文件 {csv_filename} 时出错: {str(e)}")
            conversion_log.append({
                'csv_filename': csv_filename,
                'excel_filename': excel_filename,
                'csv_size_kb': 0,
                'excel_size_kb': 0,
                'status': f'error: {str(e)}'
            })
    
    # 保存转换日志
    log_df = pd.DataFrame(conversion_log)
    log_file_path = os.path.join(excel_dir, "CSV转Excel日志.xlsx")
    
    with pd.ExcelWriter(log_file_path, engine='openpyxl') as writer:
        log_df.to_excel(writer, index=False, sheet_name='转换日志')
        
        # 设置日志表格格式
        workbook = writer.book
        worksheet = writer.sheets['转换日志']
        
        # 设置列宽
        for col_num, column in enumerate(log_df.columns, 1):
            column_letter = chr(64 + col_num)  # A, B, C, D, E
            if column == 'csv_filename' or column == 'excel_filename':
                worksheet.column_dimensions[column_letter].width = 50
            else:
                worksheet.column_dimensions[column_letter].width = 15
        
        # 设置标题行格式
        for cell in worksheet[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
    
    print(f"\n=== CSV转Excel完成 ===")
    print(f"成功转换: {len([log for log in conversion_log if log['status'] == 'success'])} 个文件")
    print(f"转换失败: {len([log for log in conversion_log if log['status'] != 'success'])} 个文件")
    print(f"转换日志保存在: {log_file_path}")
    
    return conversion_log

def main():
    """主函数"""
    csv_dir = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/评测集CSV"
    excel_dir = "/Users/edy/Desktop/project/挑战玩法/提示词/故事线商业化提示词/用户数据 150-250轮/评测集Excel"
    
    try:
        conversion_log = convert_all_csv_to_excel(csv_dir, excel_dir)
        
        print(f"\n=== 转换统计 ===")
        
        # 统计成功转换的文件
        successful_conversions = [log for log in conversion_log if log['status'] == 'success']
        
        if successful_conversions:
            total_csv_size = sum(log['csv_size_kb'] for log in successful_conversions)
            total_excel_size = sum(log['excel_size_kb'] for log in successful_conversions)
            
            print(f"CSV文件总大小: {total_csv_size:.2f} KB")
            print(f"Excel文件总大小: {total_excel_size:.2f} KB")
            print(f"大小变化: {((total_excel_size - total_csv_size) / total_csv_size * 100):+.1f}%")
        
        print(f"\nExcel文件保存在: {excel_dir}")
        print("所有文件已成功转换为Excel格式！")
        
        # 显示生成的文件列表
        excel_files = [f for f in os.listdir(excel_dir) if f.endswith('.xlsx')]
        print(f"\n=== 生成的Excel文件 ({len(excel_files)}个) ===")
        for i, filename in enumerate(sorted(excel_files)[:10], 1):
            print(f"{i:2d}. {filename}")
        
        if len(excel_files) > 10:
            print(f"... 还有 {len(excel_files) - 10} 个文件")
        
    except Exception as e:
        print(f"转换过程中出现错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()