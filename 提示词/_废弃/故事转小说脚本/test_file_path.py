#!/usr/bin/env python3
"""
测试文件路径是否正确
"""

from pathlib import Path
import os

def test_file_path():
    """测试文件路径"""
    print("🔍 测试文件路径...")

    # 获取脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    print(f"📂 脚本目录: {script_dir}")

    # 当前工作目录
    current_dir = Path.cwd()
    print(f"📂 当前工作目录: {current_dir}")

    # session_id文件路径
    session_id_path = script_dir / "session_id"
    print(f"📄 session_id文件路径: {session_id_path}")
    print(f"📂 文件是否存在: {session_id_path.exists()}")

    if session_id_path.exists():
        print("✅ 文件路径正确！")

        # 读取文件内容
        try:
            with open(session_id_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            print(f"📋 文件包含 {len(lines)} 行")
            print(f"📄 前3行内容: {lines[:3]}")
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
    else:
        print("❌ 文件路径有问题！")

        # 列出目录中的所有文件
        print(f"📁 目录中的文件:")
        for file in script_dir.iterdir():
            print(f"  - {file.name}")

if __name__ == "__main__":
    test_file_path()