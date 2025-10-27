#!/usr/bin/env python3
"""
简化版Webhook请求脚本
使用标准库实现，无需安装额外依赖
"""

import json
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

def send_request(session_id: str, webhook_url: str) -> dict:
    """
    发送单个请求
    """
    try:
        data = {"session_id": session_id.strip()}
        start_time = time.time()

        response = requests.post(
            webhook_url,
            json=data,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )

        response_time = time.time() - start_time

        if response.status_code == 200:
            print(f"✅ 成功: {session_id} | 耗时: {response_time:.2f}s")
            return {
                "session_id": session_id,
                "status": "success",
                "status_code": response.status_code,
                "response_time": response_time
            }
        else:
            print(f"❌ 失败: {session_id} | 状态码: {response.status_code}")
            return {
                "session_id": session_id,
                "status": "failed",
                "status_code": response.status_code
            }

    except requests.exceptions.Timeout:
        print(f"⏰ 超时: {session_id}")
        return {"session_id": session_id, "status": "timeout"}
    except Exception as e:
        print(f"💥 错误: {session_id} | {str(e)}")
        return {"session_id": session_id, "status": "error", "error": str(e)}

def load_session_ids(file_path: str) -> List[str]:
    """加载session_id列表"""
    try:
        # 获取脚本的绝对路径
        script_dir = Path(__file__).parent.absolute()
        full_path = script_dir / file_path

        print(f"🔍 查找文件: {full_path}")
        print(f"📂 文件是否存在: {full_path.exists()}")

        with open(full_path, 'r', encoding='utf-8') as f:
            session_ids = [line.strip() for line in f if line.strip()]

        print(f"📋 成功读取 {len(session_ids)} 个session_id")
        return session_ids

    except FileNotFoundError:
        print(f"❌ 文件未找到: {file_path}")
        print(f"📂 脚本目录: {Path(__file__).parent.absolute()}")
        print(f"💡 请确保 session_id 文件与脚本在同一目录下")
        return []
    except Exception as e:
        print(f"💥 读取文件失败: {str(e)}")
        return []

def main():
    """主函数"""
    webhook_url = "https://n8n.games/webhook/novel"
    session_id_file = "session_id"
    max_workers = 10  # 最大并发线程数

    print("🚀 开始执行Webhook批量请求")
    print(f"🌐 目标URL: {webhook_url}")
    print(f"📁 Session文件: {session_id_file}")
    print(f"⚡ 最大并发数: {max_workers}")

    # 加载session_id
    session_ids = load_session_ids(session_id_file)
    if not session_ids:
        print("❌ 没有找到有效的session_id")
        return

    print(f"📤 开始发送 {len(session_ids)} 个请求...")
    start_time = time.time()

    # 使用线程池执行并发请求
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_session = {
            executor.submit(send_request, session_id, webhook_url): session_id
            for session_id in session_ids
        }

        results = []
        # 收集结果
        for future in as_completed(future_to_session):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                session_id = future_to_session[future]
                print(f"💥 任务执行错误: {session_id} | {str(e)}")

    total_time = time.time() - start_time

    # 统计结果
    success_count = sum(1 for r in results if r.get("status") == "success")
    failed_count = len(results) - success_count

    print("=" * 50)
    print("📊 请求完成统计:")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {failed_count}")
    print(f"📈 成功率: {success_count/len(results)*100:.1f}%")
    print(f"⏱️  总耗时: {total_time:.2f}s")
    print(f"🚀 平均速度: {len(results)/total_time:.2f} 请求/秒")

    # 保存结果
    result_file = f"simple_results_{int(time.time())}.json"
    try:
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total": len(results),
                    "success": success_count,
                    "failed": failed_count,
                    "success_rate": success_count/len(results)*100,
                    "total_time": total_time
                },
                "results": results
            }, f, ensure_ascii=False, indent=2)
        print(f"💾 结果已保存到: {result_file}")
    except Exception as e:
        print(f"💥 保存结果失败: {str(e)}")

if __name__ == "__main__":
    main()