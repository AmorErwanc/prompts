# 常量与配置管理

统一的常量组织和配置管理策略。

## 常量包结构

```
com.agent.constant/
├── ToolConstant.java       # 工具类型和名称
├── StepConstant.java       # 步骤和SSE事件
├── AgentConstant.java      # Agent类型和意图
├── StatusConstant.java     # 状态码
├── DictionaryConstant.java # 字典常量
├── RedisKeyConstant.java   # Redis键模式
├── ModelApiConfig.java     # 模型配置
└── Constant.java           # 通用常量
```

## 核心常量参考

### ToolConstant
| 类别 | 常量 | 值 | 用途 |
|------|------|-----|------|
| **工具类型** | PURE_TOOL | "pure_tool" | 纯工具策略 |
| | PROMPT_TOOL | "prompt_tool" | 提示词工具 |
| | HYBRID_TOOL | "hybrid_tool" | 异构工具 |
| **播客工具** | TOOL_RADIO_INTENTION | "radio_intention" | 意图识别 |
| | TOOL_RADIO_SCRIPT | "radio_script" | 脚本生成 |
| | TOOL_RADIO_COVER | "radio_cover" | 封面生成 |

### StepConstant
| 类别 | 常量 | 值 | 用途 |
|------|------|-----|------|
| **播客步骤** | PLAN_INTRO | "plan_intro" | 播客简介 |
| | PLAN_OUTLINE | "plan_outline" | 播客大纲 |
| | PLAN_SCRIPT | "plan_script" | 播客脚本 |
| | PLAN_SUMMARY | "plan_summary" | 播客总结 |
| | PLAN_GENERATE_MP3 | "plan_generate_mp3" | 生成音频 |
| **通用步骤** | PLAN_PLOT | "plan_plot" | 剧情/情节（玩法使用） |
| | PLAN_COVER | "plan_cover" | 封面生成（播客/玩法共用） |
| | PLAN_BGM | "plan_bgm" | 背景音乐（播客/玩法共用） |
| **SSE前缀** | SSE_PLAN_DOC_STEP_PREFIX | "response.plan_doc_step." | 步骤事件 |
| **SSE状态** | SSE_BEGIN | "begin" | 开始 |
| | SSE_DELTA | "delta" | 流式数据 |
| | SSE_DONE | "done" | 完成 |

### AgentConstant
| 类别 | 常量 | 值 | 用途 |
|------|------|-----|------|
| **Agent类型** | AGENT_TYPE_PODCAST | "podcast" | 播客Agent |
| | AGENT_TYPE_INTERACT | "interact" | 玩法Agent |
| **意图类型** | INTENT_NEW_PLAN | "new_plan" | 新计划 |
| | INTENT_MODIFY_STEP | "modify_step" | 修改步骤 |
| | INTENT_CHAT_ONLY | "chat_only" | 仅聊天 |

## 模型配置策略

### ModelApiConfig
```java
@Configuration
public class ModelApiConfig {
    // 默认模型
    private String model = "ep-20250713090634-7bmxw";
    
    // 特殊提示词的模型映射
    private static final Map<String, String> SPECIAL_MODELS = Map.of(
        "radio_intention", "ep-20250122142510-jrcvh"  // 高性能模型
    );
    
    public static String getModel(String promptCode, String defaultModel) {
        if (promptCode == null) return defaultModel;
        return SPECIAL_MODELS.getOrDefault(promptCode, defaultModel);
    }
}
```

### 模型选择原则
- **默认优先**：大部分使用快速模型
- **按需升级**：特定任务使用高级模型
- **统一管理**：通过promptCode确定模型
- **易于扩展**：配置化的映射关系

## Redis键管理

### RedisKeyConstant
```java
public class RedisKeyConstant {
    // 会话相关
    public static final String SESSION_KEY = "agent:session:{sessionId}";
    public static final String SESSION_LOCK = "agent:lock:session:{sessionId}";
    
    // 任务相关
    public static final String ASYNC_TASK = "agent:task:{taskId}";
    public static final String TASK_RESULT = "agent:result:{taskId}";
    
    // 缓存相关
    public static final String PROMPT_CACHE = "agent:prompt:{promptCode}";
    public static final String TOOL_CACHE = "agent:tool:{toolCode}";
}
```

## 配置管理最佳实践

### 环境配置
```yaml
# application.yml
agent:
  llm:
    default-model: ${LLM_MODEL:ep-20250713090634-7bmxw}
    timeout: ${LLM_TIMEOUT:120000}
  
  async:
    pool-size: ${ASYNC_POOL_SIZE:10}
    queue-capacity: ${ASYNC_QUEUE_CAPACITY:100}
  
  sse:
    timeout: ${SSE_TIMEOUT:300000}
    buffer-size: ${SSE_BUFFER_SIZE:100}
```

### 常量使用示例
```java
// 工具类型判断
if (ToolConstant.PROMPT_TOOL.equals(tool.getToolType())) {
    // 提示词工具处理
}

// 步骤事件发送
String eventType = StepConstant.SSE_PLAN_DOC_STEP_PREFIX + StepConstant.SSE_BEGIN;
eventSender.sendEvent(eventType, data);

// 意图路由
switch (intent.getType()) {
    case AgentConstant.INTENT_NEW_PLAN:
        handleNewPlan();
        break;
    case AgentConstant.INTENT_MODIFY_STEP:
        handleModifyStep();
        break;
}
```

## 常量管理原则

1. **统一包管理**：所有常量在`com.agent.constant`包
2. **语义化命名**：清晰表达用途
3. **私有构造函数**：防止实例化
4. **分类组织**：按功能领域分类
5. **注释完整**：每个常量都有说明