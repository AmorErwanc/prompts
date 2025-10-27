#!/usr/bin/env python3
"""
故事转小说Webhook请求脚本
并行发送session_id到指定的webhook地址
"""

import asyncio
import aiohttp
import json
import logging
import time
from pathlib import Path
from typing import List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook_requests.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebhookRequester:
    """Webhook请求处理器"""

    def __init__(self, webhook_url: str, max_concurrent: int = 10, timeout: int = 30):
        """
        初始化请求器

        Args:
            webhook_url: webhook地址
            max_concurrent: 最大并发数
            timeout: 请求超时时间（秒）
        """
        self.webhook_url = webhook_url
        self.max_concurrent = max_concurrent
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = None
        self.semaphore = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        # 创建连接器，限制连接池大小
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent + 2,  # 总连接数限制
            limit_per_host=self.max_concurrent,  # 每个主机连接数限制
            force_close=False,
            enable_cleanup_closed=True
        )

        # 创建session
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers={'Content-Type': 'application/json'}
        )

        # 创建信号量控制并发数
        self.semaphore = asyncio.Semaphore(self.max_concurrent)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()

    async def send_single_request(self, session_id: str, retry_count: int = 3) -> dict:
        """
        发送单个请求

        Args:
            session_id: 会话ID
            retry_count: 重试次数

        Returns:
            请求结果字典
        """
        async with self.semaphore:  # 控制并发数
            request_data = {
                "session_id": session_id.strip()
            }

            for attempt in range(retry_count + 1):
                try:
                    start_time = time.time()

                    # 发送POST请求
                    async with self.session.post(
                        self.webhook_url,
                        json=request_data
                    ) as response:
                        response_time = time.time() - start_time

                        # 检查响应状态
                        if response.status == 200:
                            result_data = await response.json() if response.content_type == 'application/json' else await response.text()
                            logger.info(f"✅ 成功: {session_id} | 状态: {response.status} | 耗时: {response_time:.2f}s")
                            return {
                                "session_id": session_id,
                                "status": "success",
                                "status_code": response.status,
                                "response_time": response_time,
                                "response_data": result_data,
                                "attempt": attempt + 1
                            }
                        else:
                            error_text = await response.text()
                            logger.warning(f"❌ 失败: {session_id} | 状态: {response.status} | 尝试: {attempt + 1}/{retry_count + 1}")
                            if attempt == retry_count:
                                return {
                                    "session_id": session_id,
                                    "status": "failed",
                                    "status_code": response.status,
                                    "error": error_text,
                                    "attempt": attempt + 1
                                }

                except asyncio.TimeoutError:
                    logger.warning(f"⏰ 超时: {session_id} | 尝试: {attempt + 1}/{retry_count + 1}")
                    if attempt == retry_count:
                        return {
                            "session_id": session_id,
                            "status": "timeout",
                            "error": "请求超时",
                            "attempt": attempt + 1
                        }

                except aiohttp.ClientError as e:
                    logger.warning(f"🔌 连接错误: {session_id} | 错误: {str(e)} | 尝试: {attempt + 1}/{retry_count + 1}")
                    if attempt == retry_count:
                        return {
                            "session_id": session_id,
                            "status": "connection_error",
                            "error": str(e),
                            "attempt": attempt + 1
                        }

                except Exception as e:
                    logger.error(f"💥 未知错误: {session_id} | 错误: {str(e)} | 尝试: {attempt + 1}/{retry_count + 1}")
                    if attempt == retry_count:
                        return {
                            "session_id": session_id,
                            "status": "unknown_error",
                            "error": str(e),
                            "attempt": attempt + 1
                        }

                # 如果不是最后一次尝试，等待一段时间再重试
                if attempt < retry_count:
                    wait_time = min(2 ** attempt, 10)  # 指数退避，最大等待10秒
                    logger.info(f"⏳ 等待 {wait_time}s 后重试: {session_id}")
                    await asyncio.sleep(wait_time)

def load_session_ids(file_path: str) -> List[str]:
    """
    从文件加载session_id列表

    Args:
        file_path: session_id文件路径

    Returns:
        session_id列表
    """
    try:
        # 获取脚本的绝对路径
        script_dir = Path(__file__).parent.absolute()
        full_path = script_dir / file_path

        logger.info(f"🔍 查找文件: {full_path}")
        logger.info(f"📂 文件是否存在: {full_path.exists()}")

        with open(full_path, 'r', encoding='utf-8') as f:
            session_ids = [line.strip() for line in f if line.strip()]

        logger.info(f"📂 加载了 {len(session_ids)} 个session_id")
        return session_ids
    except FileNotFoundError:
        logger.error(f"❌ 文件未找到: {file_path}")
        logger.error(f"📂 脚本目录: {script_dir}")
        logger.error(f"💡 请确保 session_id 文件与脚本在同一目录下")
        return []
    except Exception as e:
        logger.error(f"💥 读取文件失败: {str(e)}")
        return []

async def main():
    """主函数"""
    # 配置参数
    webhook_url = "https://n8n.games/webhook/novel-v2"
    session_id_file = "session_id"
    max_concurrent = 10  # 最大并发数

    logger.info("🚀 开始执行Webhook批量请求")
    logger.info(f"🌐 目标URL: {webhook_url}")
    logger.info(f"📁 Session文件: {session_id_file}")
    logger.info(f"⚡ 最大并发数: {max_concurrent}")

    # 加载session_id
    session_ids = load_session_ids(session_id_file)
    if not session_ids:
        logger.error("❌ 没有找到有效的session_id，脚本终止")
        return

    # 使用WebhookRequester发送请求
    async with WebhookRequester(webhook_url, max_concurrent) as requester:
        start_time = time.time()

        # 创建所有请求任务
        tasks = [
            requester.send_single_request(session_id)
            for session_id in session_ids
        ]

        logger.info(f"📤 开始发送 {len(tasks)} 个请求...")

        # 执行所有并发请求
        results = await asyncio.gather(*tasks, return_exceptions=True)

        total_time = time.time() - start_time

        # 统计结果
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
        failed_count = len(results) - success_count

        logger.info("=" * 50)
        logger.info("📊 请求完成统计:")
        logger.info(f"✅ 成功: {success_count}")
        logger.info(f"❌ 失败: {failed_count}")
        logger.info(f"📈 成功率: {success_count/len(results)*100:.1f}%")
        logger.info(f"⏱️  总耗时: {total_time:.2f}s")
        logger.info(f"🚀 平均速度: {len(results)/total_time:.2f} 请求/秒")

        # 保存详细结果
        result_file = f"webhook_results_{int(time.time())}.json"
        try:
            # 过滤掉异常对象，只保留有效的字典结果
            valid_results = [r for r in results if isinstance(r, dict)]
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "summary": {
                        "total": len(valid_results),
                        "success": success_count,
                        "failed": failed_count,
                        "success_rate": success_count/len(valid_results)*100,
                        "total_time": total_time,
                        "requests_per_second": len(valid_results)/total_time
                    },
                    "results": valid_results
                }, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 详细结果已保存到: {result_file}")
        except Exception as e:
            logger.error(f"💥 保存结果文件失败: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  用户中断执行")
    except Exception as e:
        logger.error(f"💥 脚本执行失败: {str(e)}")