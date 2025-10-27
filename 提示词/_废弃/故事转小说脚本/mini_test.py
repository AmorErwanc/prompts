#!/usr/bin/env python3
"""
最小化测试脚本 - 只发送前3个session_id
"""

import json
import time
import requests
from pathlib import Path

def load_session_ids():
    """加载session_id"""
    try:
        script_dir = Path(__file__).parent.absolute()
        full_path = script_dir / "session_id"

        with open(full_path, 'r', encoding='utf-8') as f:
            session_ids = [line.strip() for line in f if line.strip()]

        # 只取前3个进行测试
        return session_ids[:3]
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return []

def send_request(session_id):
    """发送单个请求"""
    try:
        data = {"session_id": session_id}
        url = "https://n8n.games/webhook/novel"

        print(f"📤 发送请求: {session_id}")
        start_time = time.time()

        response = requests.post(
            url,
            json=data,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )

        response_time = time.time() - start_time

        print(f"📊 响应: {session_id} | 状态: {response.status_code} | 耗时: {response_time:.2f}s")

        return {
            "session_id": session_id,
            "status_code": response.status_code,
            "response_time": response_time,
            "success": response.status_code == 200
        }

    except requests.exceptions.Timeout:
        print(f"⏰ 超时: {session_id}")
        return {"session_id": session_id, "status": "timeout", "success": False}
    except Exception as e:
        print(f"❌ 错误: {session_id} | {str(e)}")
        return {"session_id": session_id, "status": "error", "error": str(e), "success": False}

def main():
    """主函数"""
    print("🧪 最小化测试开始...")
    print("只发送前3个session_id进行测试")

    session_ids = load_session_ids()
    if not session_ids:
        print("❌ 没有加载到session_id")
        return

    print(f"📋 准备发送 {len(session_ids)} 个请求")
    print("=" * 50)

    results = []
    for session_id in session_ids:
        result = send_request(session_id)
        results.append(result)
        time.sleep(1)  # 避免请求太快

    print("=" * 50)
    print("📊 测试结果:")

    success_count = sum(1 for r in results if r.get("success"))
    total_count = len(results)

    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"📈 成功率: {success_count/total_count*100:.1f}%")

    # 保存测试结果
    result_file = "mini_test_result.json"
    try:
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "total": total_count,
                    "success": success_count,
                    "success_rate": success_count/total_count*100
                },
                "results": results
            }, f, ensure_ascii=False, indent=2)
        print(f"💾 结果已保存到: {result_file}")
    except Exception as e:
        print(f"❌ 保存结果失败: {e}")

if __name__ == "__main__":
    main()