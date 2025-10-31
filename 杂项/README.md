# 对话数据批量转换工具

本项目用于批量处理"对话数据导出/"目录下的CSV文件，将其按session（会话ID）整理，并导出为两种JSON格式的Markdown文档。

## 功能说明

### 输入数据
- 数据源：`对话数据导出/` 目录
- 目录结构：每个pipeid一个文件夹，包含两个CSV文件
  - `{pipeid}_低质量用户输入.csv` （短用户输入）
  - `{pipeid}_高质量用户输入.csv` （长用户输入）

### CSV字段
- 创建时间
- 会话ID
- 用户ID
- 用户输入
- AI回复
- 完整消息

### 输出格式

脚本会为每个CSV生成两种格式的Markdown文件：

#### 版本A：原messages格式（sessions格式）
按session_id分组，每个消息包含role和content字段：
```json
[
  {
    "role": "user",
    "content": "用户输入内容"
  },
  {
    "role": "assistant",
    "content": "AI输出内容"
  }
]
```

#### 版本B：优化后messages格式（pairs格式）
按session_id分组，每对消息包含user和assistant字段：
```json
[
  {
    "user": "用户输入内容",
    "assistant": "AI输出内容"
  }
]
```

## 使用方法

### 快速开始

直接运行批量转换脚本：

```bash
python3 batch_convert_pipeid_csvs.py
```

### 输出目录结构

```
markdown_outputs/
  000003863243117306593299/
    000003863243117306593299_低质量用户输入-原messages.md
    000003863243117306593299_低质量用户输入-优化后messages.md
    000003863243117306593299_高质量用户输入-原messages.md
    000003863243117306593299_高质量用户输入-优化后messages.md
  000003924847270611763219/
    ...
```

### 输出示例

#### 原messages格式 (版本A)
```markdown
## session_id: 000004683536058406158336 （user_id: 000004683085351970455552）
\`\`\`json
[
  {
    "role": "user",
    "content": "你现在是什么职业？"
  },
  {
    "role": "assistant",
    "content": "（轻笑一声）猜猜看？"
  }
]
\`\`\`
```

#### 优化后messages格式 (版本B)
```markdown
## session_id: 000004683536058406158336 （user_id: 000004683085351970455552）
\`\`\`json
[
  {
    "user": "你现在是什么职业？",
    "assistant": "（轻笑一声）猜猜看？"
  }
]
\`\`\`
```

## 关键实现细节

- **分组**：按 `会话ID` 分组；若缺失则用占位 `"<EMPTY_SESSION_ID>"`
- **排序**：同一会话内按 `创建时间` 升序，兼容常见日期格式
- **编码**：读取时使用 `utf-8-sig` 以兼容带BOM的CSV；写出为 `utf-8`
- **缺失字段处理**：
  - 原messages格式：仅当存在用户输入或AI回复时分别追加对应消息
  - 优化后messages格式：始终生成成对结构；若缺失则对应值为空字符串

## 文件说明

### 主要文件
- `batch_convert_pipeid_csvs.py` - 批量转换脚本（新）
- `对话数据导出/` - 原始CSV数据目录
- `markdown_outputs/` - 输出目录（自动生成）
- `旧数据归档/` - 之前版本的脚本和数据归档

### 归档文件（旧数据归档/）
- `preprocess_sessions_md.py` - 旧版脚本（仅sessions格式）
- `preprocess_dual_outputs.py` - 旧版脚本（双格式输出）
- `csv/` - 旧版示例CSV文件
- `sessions_md/` - 旧版sessions格式输出
- `pairs_md/` - 旧版pairs格式输出

## 常见问题

### 时间格式不统一
脚本已尝试多种常见格式解析；若仍无法解析，请规范化 `创建时间` 字段或在脚本中补充格式。

### 大文件处理
Markdown汇总较长，建议使用编辑器的折叠或搜索功能快速定位会话。

### 空会话ID
会被归为 `"<EMPTY_SESSION_ID>"` 分组；如需独立处理可在导出前清洗数据。

### 安全与隐私
输出文件包含原始对话内容，请按需脱敏或限制访问。

## 可扩展方向

- 将每个 `session_id` 导出为独立 `.json` 文件，便于程序直接消费
- 按类别（如"单聊/剧情/长/短"）自动分类到多级子目录
- 增加过滤器（按 `user_id`、时间段、质量等）生成子集
- 输出其他格式（如NDJSON、CSV回写、HTML预览）

## 维护建议

- 新增CSV后重复执行脚本即可生成最新输出
- 所有输出统一归档到 `markdown_outputs/` 目录
- 若调整字段名或新增列，请同步更新脚本中的取值逻辑
