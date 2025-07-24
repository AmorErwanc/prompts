# n8n JSON解析器测试用例

## 测试用例集合

### 1. 正常格式
```json
{
  "assistant_reply": "让我帮你策划一个判断类的挑战玩法",
  "intent_type": "new_plan",
  "target_step": null,
  "template_type": "judgment",
  "character_info": {
    "name": "顾飞祁",
    "gender": "男",
    "features": "京圈大佬"
  },
  "planning_brief": "10轮对话判断好坏人"
}
```

### 2. 数组格式（您提到的问题）
```json
[{"output": "{\"assistant_reply\":\"好的\",\"intent_type\":\"chat_only\",\"target_step\":null,\"template_type\":null}"}]
```

### 3. 中文引号
```json
{
  "assistant_reply": "让我帮你策划",
  "intent_type": "new_plan",
  "target_step": null,
  "template_type": "judgment"
}
```

### 4. 缺少逗号
```json
{
  "assistant_reply": "让我帮你策划"
  "intent_type": "new_plan"
  "target_step": null
  "template_type": "judgment"
}
```

### 5. 末尾多余逗号
```json
{
  "assistant_reply": "让我帮你策划",
  "intent_type": "new_plan",
  "target_step": null,
  "template_type": "judgment",
}
```

### 6. 未加引号的键
```json
{
  assistant_reply: "让我帮你策划",
  intent_type: "new_plan",
  target_step: null,
  template_type: "judgment"
}
```

### 7. Python格式（None/True/False）
```json
{
  "assistant_reply": "让我帮你策划",
  "intent_type": "new_plan",
  "target_step": None,
  "template_type": "judgment",
  "is_valid": True
}
```

### 8. 带Markdown代码块
```json
```json
{
  "assistant_reply": "让我帮你策划",
  "intent_type": "new_plan",
  "target_step": null,
  "template_type": "judgment"
}
```
```

### 9. 带额外文字说明
```
根据您的需求，我生成了以下JSON响应：
{
  "assistant_reply": "让我帮你策划",
  "intent_type": "new_plan",
  "target_step": null,
  "template_type": "judgment"
}
希望对您有帮助！
```

### 10. Unicode转义
```json
{
  "assistant_reply": "\u8ba9\u6211\u5e2e\u4f60\u7b56\u5212",
  "intent_type": "new_plan",
  "target_step": null,
  "template_type": "judgment"
}
```

### 11. 过度转义
```json
{
  \"assistant_reply\": \"让我帮你策划\",
  \"intent_type\": \"new_plan\",
  \"target_step\": null,
  \"template_type\": \"judgment\"
}
```

### 12. 单引号JSON
```json
{
  'assistant_reply': '让我帮你策划',
  'intent_type': 'new_plan',
  'target_step': null,
  'template_type': 'judgment'
}
```

### 13. 嵌套的output属性
```json
{
  "output": {
    "assistant_reply": "让我帮你策划",
    "intent_type": "new_plan",
    "target_step": null,
    "template_type": "judgment"
  }
}
```

### 14. 带BOM字符
```json
﻿{
  "assistant_reply": "让我帮你策划",
  "intent_type": "new_plan",
  "target_step": null,
  "template_type": "judgment"
}
```

### 15. 混合问题（最复杂的情况）
```
模型输出如下：
```json
{
  "assistant_reply": "让我帮你策划一个"判断类"的挑战玩法",
  'intent_type': 'new_plan',
  target_step: None,
  "template_type": "judgment"，
}
```
```

## 预期结果

所有测试用例都应该成功解析，并返回标准化的输出格式：
- `success: true`
- 包含所有必需字段
- 正确处理null值
- 保留原始输出以便调试

## 错误情况测试

### 1. 完全无效的JSON
```
这不是JSON格式的内容
```

### 2. 缺少必需字段
```json
{
  "intent_type": "new_plan"
}
```

### 3. 无效的intent_type
```json
{
  "assistant_reply": "测试",
  "intent_type": "invalid_type",
  "target_step": null,
  "template_type": null
}
```

这些错误情况应该返回：
- `success: false`
- 明确的错误类型和消息
- 调试信息