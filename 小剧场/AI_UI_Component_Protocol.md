# AI UI 样式化协议 (收敛统一版 v2)

本协议适用于“写作与样式分离”的双流架构：写作 AI 只产出纯文本剧情，样式 AI 只分析剧情并输出 UI 组件化指令。两者通过段落 id 对齐。

本版重点收敛：
- 组件统一壳：所有组件都用 component.type + component.props
- props 统一为对象（不再出现某个组件 props 是数组）
- 数值变化统一用 number（前端负责展示成 +5 之类）

## 1. 核心交互流程
1. 写作：写作 AI 生成纯文本剧情
2. 预处理：后端按段落切分为数组 Array<{id:number, text:string}>
3. 样式化：将段落数组发送给样式 AI
4. 渲染：前端根据样式 AI 返回的指令，在指定 id 位置替换/追加组件或修饰文本

## 2. 样式 AI 交互协议

### 2.1 输入 (Request)
样式 AI 接收一组带唯一 id 的段落数组：

```json
[
  { "id": 0, "text": "第 203 号档案室，2026年1月26日，雷雨。" },
  { "id": 1, "text": "沈念安坐在阴影里，手里把玩着手术刀。" },
  { "id": 2, "text": "“你终于来了。”他笑着说。" },
  { "id": 3, "text": "我收到了一条银行转账短信，到账五百万。" }，
  { "id": 3, "jiacu": "我收到了一条银行转/" },
  { "id": 3, "image": "我收到了一条银行转/" },
]
```

### 2.2 输出 (Response)
样式 AI 输出一个 JSON 数组 instructions，包含对特定段落的操作指令。

```json
[
  {
    "target_ids": [2, 3],
    "action": "convert",
    "component": {
      "type": "interaction_chat",
      "props": {
        "messages": [
          { "role": "npc", "name": "沈念安", "content": "你终于来了。" },
          { "role": "user", "name": "我", "content": "我收到了一条银行转账短信，到账五百万。" }
        ]
      }
    }
  },
  {
    "target_ids": [3],
    "action": "append",
    "component": {
      "type": "container",
      "props": {
        "title": "账户入账通知",
        "body": "- 金额：5,000,000\n- 币种：RMB\n- 备注：封口费"
      }
    }
  }
]
```

当需要输出 Markdown（例如标题、强调、高亮）时，使用 action="format"，并在 data.new_string 中给出替换后的文本：

```json
[
  {
    "target_ids": [7],
    "action": "format",
    "data": {
      "new_string": "## 侧写模式分析中..."
    }
  },
  {
    "target_ids": [8],
    "action": "format",
    "data": {
      "new_string": "他盯着我，语气突然变得==很轻==：`别出声`。"
    }
  },
  {
    "target_ids": [9],
    "action": "format",
    "data": {
      "new_string": "> 备忘：不要相信任何人\\n\\n- 线索：`A-9527`\\n- 状态：==危险==\\n\\n<span class=\"text\">提示：去查门禁记录。</span>"
    }
  }
]
```

## 3. 操作指令定义 (Actions)

### 3.1 convert (替换)
- 前端行为：不渲染原 text，在 target_ids[0] 的位置渲染 component
- 合并：允许 target_ids 多个 id，用于把多段内容合并成一个组件
- 合并约束：只合并连续段落 id（例如 [2,3,4]）
- 合并隐藏：前端应自动隐藏 target_ids[1..] 的纯文本内容，防止重复渲染

### 3.2 append (追加)
- 前端行为：保留并渲染原 text，然后在该段落下方插入 component
- 约束：target_ids 必须只包含 1 个 id（追加锚点）

### 3.3 format (修饰)
- 前端行为：用 data.new_string 覆盖原 text，然后作为标准文本渲染
- 输出结构：

```json
{
  "target_ids": [5],
  "action": "format",
  "data": {
    "new_string": "需要渲染的新文本"
  }
}
```

## 4. 组件数据结构 (Component Schemas)
所有组件一律使用：
- component.type: 组件类型
- component.props: 组件属性对象

仅允许以下 4 个组件类型（标题不再使用组件，统一用 format + Markdown 标题语法实现）。

容器内 Markdown 支持规则：
- container.props.title 与 container.props.body 允许使用第 5 节定义的 Markdown/高亮语法
- 除此之外，协议未明确声明支持 Markdown 的字段，默认按纯文本处理

### 4.1 interaction_chat
- type: "interaction_chat"
- props:
  - messages: Array<{role:"npc"|"user", name:string, content:string}>

示例：
```json
{
  "type": "interaction_chat",
  "props": {
    "messages": [
      { "role": "npc", "name": "沈念安", "content": "你真的觉得这家医院没有问题吗？" },
      { "role": "user", "name": "我", "content": "别担心，我会查清楚的。" }
    ]
  }
}
```

### 4.2 status_settlement
- type: "status_settlement"
- props:
  - attribute: string
  - icon: string (可选)
  - current_value: number
  - delta: number
  - comment: string (可选)

示例：
```json
{
  "type": "status_settlement",
  "props": {
    "attribute": "占有欲",
    "icon": "🔒",
    "current_value": 85,
    "delta": 5,
    "comment": "他对你的警惕心似乎下降了..."
  }
}
```

### 4.3 container
- type: "container"
- props:
  - title: string（支持 Markdown，见第 5 节）
  - body: string（支持 Markdown，见第 5 节）

示例：
```json
{
  "type": "container",
  "props": {
    "title": "连环失踪案最新进展（==疑点==浮现）",
    "body": "据本市警方通报...\n\n关键证物：`A-9527`。\n\n<span class=\"text\">目击者称：当晚有人从后门离开。</span>"
  }
}
```

### 4.4 image_full
- type: "image_full"
- props:
  - trigger_generation: true
  - context_summary: string

说明：
- 该组件仅作为生图触发信号
- 系统检测到该组件后，应调用专门的 Painting Agent 生成 Prompt 并产出图片

示例：
```json
{
  "type": "image_full",
  "props": {
    "trigger_generation": true,
    "context_summary": "雨夜中闪烁的红蓝霓虹灯牌，赛博朋克风格"
  }
}
```

## 5. 文本修饰语法 (Text Decoration Syntax)
为满足“造梦次元”视觉需求，format 的 new_string 允许使用 Markdown 子集 + 扩展高亮语法 + 极小的 HTML 子集。

Markdown 支持范围说明：
- 本协议只保证以下列出的 Markdown 语法可用
- 未列出的 Markdown/HTML 用法不要输出（避免不同端渲染不一致）

### 5.0 标题规范（替代 header_section 组件）
- 当某个段落是“分节标题/章节标题/模式提示”等标题性质文本时，使用 action="format"
- 将该段落的 new_string 改为 Markdown 标题：
  - 语法：## 标题内容（推荐）
  - 可选：# / ###（仅在确实需要层级时使用）
  - 说明：标题内容应来自原段落 text，禁止凭空新增标题含义

### 5.1 标题 (Markdown)
- 一级标题：# 标题
- 二级标题：## 标题
- 三级标题：### 标题

### 5.2 强调 (Markdown)
- 加粗：**文字**
- 斜体：*文字*
- 删除线：~~文字~~

### 5.3 列表 (Markdown)
- 无序列表：
  - 语法：- 条目
- 有序列表：
  - 语法：1. 条目

### 5.4 引用 (Markdown)
- 语法：> 引用内容

### 5.5 浅高亮 (Extended Syntax)
- 语法：`文字`
- 说明：
  - 反引号仅表示浅高亮，不表示代码
  - 用于专有名词、物品名、编号、金额等短文本

### 5.6 深高亮 (Extended Syntax)
- 强高亮：==文字==
- 说明：用于强调线索/情绪/关键短语，不要包裹整段大段文字

### 5.7 极小 HTML 子集 (HTML Subset)
- 语法：<span class="text">文字</span>
- 说明：
  - 只允许使用 class="text"
  - 具体颜色与表现由前端统一决定，样式 AI 不需要也不应指定颜色

## 6. 迁移说明 (v1 -> v2)
### 6.1 指令字段迁移
- v1：{ target_ids, action, type, data }
- v2：{ target_ids, action, component: { type, props } }
- 例外：format 保持 { action:"format", data:{new_string} } 不变

### 6.2 组件迁移映射
- interaction_chat：v1 的 data(数组) -> v2 的 props.messages(数组)
- container：
  - v1 的 container_media -> v2 的 container（headline -> title，body 保持 body）
  - v1 的 card_notification -> v2 的 container（title 保持 title，body 保持 body）
- status_settlement：v1 的 change_value(如 "+5") -> v2 的 delta(数字，如 5)
- header_section：v1 的 header_section 组件不再使用；改为 action="format"，data.new_string="## 原标题"
