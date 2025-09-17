#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量并行请求webhook脚本 - 2000轮数据
用途：批量向指定webhook发送session_id参数
"""

import asyncio
import aiohttp
import json
import time
from typing import List, Dict, Any

class WebhookBatchRequester:
    def __init__(self, webhook_url: str):
        """
        初始化批量请求器

        Args:
            webhook_url: webhook地址
        """
        self.webhook_url = webhook_url
        self.session_ids = [
            "000003933323854593409024",
            "000004034045491842940929",
            "000004057950874425704448",
            "000004299280578177974272",
            "000004392034981577768962",
            "000004422158042704412675",
            "000004429584871312637953",
            "000004448711811390816259",
            "000004473182313186377732",
            "000004496651411597590529",
            "000004557297952729088004",
            "000004559899983973220361",
            "000004560164954615349250",
            "000004600551101468000258",
            "000004603366239577325570",
            "000004608289222779518980",
            "000004613257115149549575",
            "000004616966515295043586",
            "000004623859383435575296",
            "000004626625727209979909"
        ]

    async def send_single_request(self, session: aiohttp.ClientSession, session_id: str) -> Dict[str, Any]:
        """
        发送单个webhook请求

        Args:
            session: aiohttp会话
            session_id: 会话ID

        Returns:
            包含请求结果的字典
        """
        request_data = {
            "session_id": session_id
        }

        start_time = time.time()
        try:
            async with session.post(
                self.webhook_url,
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=aiohttp.ClientTimeout(total=180)  # 3分钟超时
            ) as response:
                response_text = await response.text()
                elapsed_time = time.time() - start_time

                result = {
                    "session_id": session_id,
                    "status_code": response.status,
                    "success": response.status == 200,
                    "response": response_text,
                    "elapsed_time": round(elapsed_time, 3),
                    "error": None
                }

                print(f"✅ {session_id}: {response.status} ({elapsed_time:.3f}s)")
                return result

        except asyncio.TimeoutError:
            elapsed_time = time.time() - start_time
            result = {
                "session_id": session_id,
                "status_code": 408,
                "success": False,
                "response": None,
                "elapsed_time": round(elapsed_time, 3),
                "error": "请求超时"
            }
            print(f"⏰ {session_id}: 请求超时 ({elapsed_time:.3f}s)")
            return result

        except Exception as e:
            elapsed_time = time.time() - start_time
            result = {
                "session_id": session_id,
                "status_code": 500,
                "success": False,
                "response": None,
                "elapsed_time": round(elapsed_time, 3),
                "error": str(e)
            }
            print(f"❌ {session_id}: 请求失败 - {str(e)} ({elapsed_time:.3f}s)")
            return result

    async def batch_request(self, max_concurrent: int = 20) -> List[Dict[str, Any]]:
        """
        批量并行发送请求

        Args:
            max_concurrent: 最大并发数

        Returns:
            所有请求结果的列表
        """
        print(f"开始批量请求webhook: {self.webhook_url}")
        print(f"session_id数量: {len(self.session_ids)}")
        print(f"最大并发数: {max_concurrent}")
        print("-" * 60)

        # 创建TCP连接器，设置连接池
        connector = aiohttp.TCPConnector(
            limit=max_concurrent,
            limit_per_host=max_concurrent,
            ttl_dns_cache=300,
            use_dns_cache=True
        )

        async with aiohttp.ClientSession(connector=connector) as session:
            # 创建信号量限制并发数
            semaphore = asyncio.Semaphore(max_concurrent)

            async def limited_request(session_id: str):
                async with semaphore:
                    return await self.send_single_request(session, session_id)

            # 创建所有任务
            tasks = [limited_request(session_id) for session_id in self.session_ids]

            # 等待所有任务完成
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time

            # 统计结果
            success_count = sum(1 for r in results if r["success"])
            failed_count = len(results) - success_count
            avg_time = sum(r["elapsed_time"] for r in results) / len(results)

            print("-" * 60)
            print(f"批量请求完成:")
            print(f"总耗时: {total_time:.3f}s")
            print(f"成功: {success_count}/{len(results)}")
            print(f"失败: {failed_count}/{len(results)}")
            print(f"平均响应时间: {avg_time:.3f}s")

            return results

    def save_results(self, results: List[Dict[str, Any]], filename: str = "webhook_results.json"):
        """
        保存结果到JSON文件

        Args:
            results: 请求结果列表
            filename: 保存的文件名
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "webhook_url": self.webhook_url,
                    "total_requests": len(results),
                    "success_count": sum(1 for r in results if r["success"]),
                    "failed_count": sum(1 for r in results if not r["success"]),
                    "results": results
                }, f, ensure_ascii=False, indent=2)

            print(f"📄 结果已保存到: {filename}")

        except Exception as e:
            print(f"❌ 保存结果失败: {str(e)}")


async def main():
    """主函数"""
    webhook_url = "https://n8n.games/webhook/782a041e-b5d5-4b47-b756-6b85a42f55e4"

    # 创建请求器
    requester = WebhookBatchRequester(webhook_url)

    # 执行批量请求（最大并发数可调整）
    results = await requester.batch_request(max_concurrent=20)

    # 保存结果
    requester.save_results(results, "webhook_批量请求结果_2000.json")

    # 显示详细结果
    print("\n" + "="*60)
    print("详细结果:")
    print("="*60)

    for result in results:
        status_icon = "✅" if result["success"] else "❌"
        print(f"{status_icon} {result['session_id']}: "
              f"状态码={result['status_code']}, "
              f"耗时={result['elapsed_time']}s")

        if result["error"]:
            print(f"   错误: {result['error']}")

        if result["response"] and len(result["response"]) > 100:
            print(f"   响应: {result['response'][:100]}...")
        elif result["response"]:
            print(f"   响应: {result['response']}")

    print("\n🎉 批量请求任务完成!")


if __name__ == "__main__":
    try:
        # 运行异步主函数
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ 用户中断了程序")
    except Exception as e:
        print(f"❌ 程序执行出错: {str(e)}")