# 故事转小说Webhook请求脚本

## 功能说明
这个脚本用于并行发送session_id到指定的webhook地址，支持高并发请求和错误处理。

## 文件说明

### 1. webhook_request.py (推荐)
- **异步版本**，使用aiohttp库
- 支持更高的并发性能
- 内置重试机制和详细日志
- 适合大量请求的高效处理

### 2. simple_webhook_request.py (简化版)
- **同步版本**，使用requests库
- 依赖更少，只需要requests
- 代码更简单，易于理解
- 适合小规模请求或简单场景

### 3. requirements.txt
- 异步版本所需的依赖包

## 安装依赖

### 使用异步版本 (推荐)
```bash
pip install -r requirements.txt
```

### 使用简化版
```bash
pip install requests
```

## 使用方法

### 1. 准备文件
确保 `session_id` 文件存在于同一目录下，每行一个session_id。

### 2. 运行脚本

#### 异步版本 (高性能)
```bash
python webhook_request.py
```

#### 简化版本
```bash
python simple_webhook_request.py
```

## 配置参数

可以在脚本中修改以下参数：

- `webhook_url`: 目标webhook地址 (默认: https://n8n.games/webhook/novel)
- `max_concurrent`: 最大并发数 (默认: 10)
- `timeout`: 请求超时时间 (默认: 30秒)

## 输出文件

### 日志文件
- `webhook_requests.log`: 详细的请求日志

### 结果文件
- `webhook_results_[时间戳].json`: 异步版本的详细结果
- `simple_results_[时间戳].json`: 简化版本的结果

## 结果格式

```json
{
  "summary": {
    "total": 20,
    "success": 18,
    "failed": 2,
    "success_rate": 90.0,
    "total_time": 15.23,
    "requests_per_second": 1.31
  },
  "results": [
    {
      "session_id": "000004597515065020170241",
      "status": "success",
      "status_code": 200,
      "response_time": 0.85
    }
  ]
}
```

## 性能对比

| 版本 | 并发性能 | 内存使用 | 依赖复杂度 | 适用场景 |
|------|----------|----------|------------|----------|
| 异步版本 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 大量请求 |
| 简化版本 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | 小规模请求 |

## 注意事项

1. **并发数设置**: 根据服务器承载能力调整，建议从10开始测试
2. **网络环境**: 确保网络连接稳定
3. **文件编码**: session_id文件使用UTF-8编码
4. **错误处理**: 脚本内置重试机制，失败的请求会自动重试

## 故障排除

### 常见问题

1. **ImportError**: 检查是否正确安装依赖
2. **连接超时**: 增加timeout参数或检查网络
3. **服务器拒绝**: 减少并发数或联系服务器管理员

### 调试建议

1. 先用简化版测试基本功能
2. 使用小并发数测试 (比如2-3)
3. 检查日志文件获取详细错误信息

## 示例输出

```
🚀 开始执行Webhook批量请求
🌐 目标URL: https://n8n.games/webhook/novel
📁 Session文件: session_id
⚡ 最大并发数: 10
📂 加载了 20 个session_id
📤 开始发送 20 个请求...
✅ 成功: 000004597515065020170241 | 耗时: 0.85s
✅ 成功: 000004599635844289544196 | 耗时: 0.92s
...
==================================================
📊 请求完成统计:
✅ 成功: 18
❌ 失败: 2
📈 成功率: 90.0%
⏱️  总耗时: 15.23s
🚀 平均速度: 1.31 请求/秒
💾 详细结果已保存到: webhook_results_1703123456.json
```