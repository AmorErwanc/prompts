# Studio 批量测试工具 - 项目文档

## 📋 项目概述

这是一个用于批量测试 Studio API 接口的 Web 应用工具，支持多接口配置、批量数据导入、智能多账号轮询、自动结果查询等功能。

**主要目的：**
- 批量测试 Studio API 的 workflow
- 支持多种输入类型（图片、文本、数字）
- 自动轮询多个账号避免排队问题
- 实时查看测试结果和进度

## 📝 更新日志

### 2025-10-29 - 批量测试核心功能增强

#### 🎯 分组测试功能
**问题**：用户需要对同一组数据进行多次测试，之前只能手动添加多个重复的测试组，导致数据列表过长且难以管理。

**解决方案**：
- 在批量测试数据表格中添加"测试次数"列（`BatchInput.vue`）
- 支持为每个测试组设置 1-50 次重复测试
- 使用 `el-input-number` 组件提供友好的数量调节
- 测试数据转换时自动根据 testCount 重复发送请求
- 添加"总计 X 次测试"统计显示

**实现细节**：
```javascript
// BatchInput.vue - executeTests()
testGroups.value.forEach((group, groupIndex) => {
  const testCount = group.testCount || 1

  for (let i = 0; i < testCount; i++) {
    testData.push({
      params,
      groupIndex,      // 所属组的索引
      testIndex: i,    // 在组内的测试索引
      groupTestCount: testCount  // 该组的总测试次数
    })
  }
})
```

#### 👤 账号标识功能
**问题**：使用多账号轮询时，无法知道每个测试使用的是哪个token账号。

**解决方案**：
- 修改 `getNextToken()` 返回账号信息对象（token, accountIndex, accountName）
- 在测试结果中保存账号索引和名称
- 在结果展示界面使用 `el-tag` 显示账号名称（如"账号1"、"账号2"）
- 默认账号显示为"默认账号"

**实现细节**：
```javascript
// App.vue - getNextToken()
const getNextToken = () => {
  const tokens = getTokenList()
  const accountIndex = currentTokenIndex.value % tokens.length
  const token = tokens[accountIndex]
  currentTokenIndex.value++

  return {
    token,
    accountIndex,
    accountName: `账号${accountIndex + 1}`
  }
}

// ResultDisplay.vue - 显示
<el-tag v-if="result.accountName" type="info" size="small">
  {{ result.accountName }}
</el-tag>
```

#### 🔍 多输出解析功能
**问题**：API 返回的 content 字段可能包含多个输出项（提示词、图片、视频等），之前的解析逻辑只提取第一项，导致错过实际的图片或视频内容。

**API 返回格式示例**：
```json
{
  "code": 0,
  "data": {
    "progress": "completed",
    "content": "[
      {\"content\":[{\"type\":\"str\",\"val\":\"首帧提示词...\"}]},
      {\"content\":[{\"type\":\"str\",\"val\":\"分镜提示词...\"}]},
      {\"content\":[{\"type\":\"img\",\"val\":\"https://...\"}]},
      {\"content\":[{\"type\":\"video\",\"val\":\"https://...\"}]}
    ]"
  }
}
```

**解决方案**：
- 实现基于优先级的内容提取算法：**video > img > str**
- 遍历所有输出项的所有 content 数组
- 三遍查找：先找视频，没找到再找图片，最后才找文本
- 提取到第一个匹配的内容后立即停止

**实现细节**（`usePolling.js`）：
```javascript
// 第一遍：查找视频
for (const item of parsed) {
  if (item.content && Array.isArray(item.content)) {
    for (const contentItem of item.content) {
      if (contentItem.type === 'video' && contentItem.val) {
        foundContent = contentItem.val
        break
      }
    }
    if (foundContent) break
  }
}

// 第二遍：如果没找到视频，查找图片
if (!foundContent) {
  for (const item of parsed) {
    if (item.content && Array.isArray(item.content)) {
      for (const contentItem of item.content) {
        if (contentItem.type === 'img' && contentItem.val) {
          foundContent = contentItem.val
          break
        }
      }
      if (foundContent) break
    }
  }
}

// 第三遍：如果都没找到，查找文本
if (!foundContent) {
  for (const item of parsed) {
    if (item.content && Array.isArray(item.content)) {
      for (const contentItem of item.content) {
        if (contentItem.type === 'str' && contentItem.val) {
          foundContent = contentItem.val
          break
        }
      }
      if (foundContent) break
    }
  }
}
```

**优点**：
- 自动提取最有价值的内容类型
- 支持视频、图片、文本混合输出
- 兼容单输出和多输出格式
- 提取失败时使用原始数据作为后备

#### 📋 分组结果展示
**改进**：
- 测试结果按组分类显示（`ResultDisplay.vue`）
- 每个组显示"第 X 组"标题和"共 N 次测试"标签
- 组内测试显示"第 X 次测试"序号
- 使用卡片式布局，清晰的视觉层次
- 分组和未分组结果分别展示

**样式优化**：
```css
.result-group {
  background-color: #f9fafb;
  border-radius: 8px;
  padding: 15px;
  border: 2px solid #e4e7ed;
}

.result-header-tags {
  display: flex;
  gap: 8px;
  align-items: center;
}
```

#### 💾 多账号恢复功能修复
**问题**：页面刷新后，多账号轮询模式的 `authTokens` 列表没有被保存和恢复。

**解决**：
- 在 `saveTestResults()` 中添加 `authTokens` 字段保存
- 页面加载时自动恢复 token 列表
- 确保刷新后继续使用多账号轮询

---

### 2025-10-29 - API 规范修正

#### 🔧 关键修复
根据 default.md 中的官方 API 文档，修正了轮询状态判断问题：

**轮询状态判断修正** (`usePolling.js`)
- **问题**：判断失败状态使用的是 `'failed'` 或 `'error'`
- **API 文档规定**：失败状态是 `'fail'`（不是 `'failed'`）
- **修复**：将状态判断修改为 `progress === 'fail'`
- **位置**：`studio-web/src/composables/usePolling.js:82`
- **影响**：现在可以正确识别和处理任务失败状态

#### 📖 API 文档对照

**对话生成接口** (`/pipe/chat`)：
- 请求方式：POST
- 必须字段：`pipeId`, `in`（包含 `type`, `name`, `val`）
- 可选字段：`event`, `contentContinue`, `chainId`, `voiceName`, `hideNames`, `roomId`, `inId`

**进度查询接口** (`/pipe/album/progress/{albumId}`)：
- 请求方式：GET
- 路径参数：`albumId`（任务ID）
- 返回状态：`completed`（完成）、`handing`（处理中）、`fail`（失败）
- 返回字段：`progress`, `errMsg`, `content`, `errCode`

### 2025-10-28 - UX 体验优化

#### 🎨 界面优化
1. **测试结果简化**
   - 移除输入参数显示，只展示输出结果
   - 将输入参数预览移至"输入参数配置"模块
   - 结果图片尺寸增大到 300x300

2. **参数配置增强**
   - 添加参数预览功能
   - 图片类型：显示 200x200 预览图，支持点击放大
   - 文本/数字类型：使用标签展示
   - URL 自动验证
   - 加载失败友好提示

### 2025-10-28 - 重大功能更新

#### 1. 批量测试 UI 优化
- **统一测试数据管理**
  - 移除了"方式一"和"方式二"的区分
  - 统一使用一个测试数据表格
  - 提供三种添加数据方式：
    - ⚡ 快速添加N组（使用参数默认值）
    - ➕ 手动添加1组
    - 📊 导入 Excel/CSV

- **快速批量测试**
  - 支持一键添加 5/10/15/20 组或自定义数量
  - 使用参数配置的默认值
  - 自动轮询不同 token 避免排队

#### 2. 测试结果展示优化
- **图片显示改进**
  - 输入参数图片：150x150 缩略图
  - 输出结果图片：200x200 缩略图
  - 点击图片可放大查看原图
  - 点击灰色区域关闭预览
  - 图片加载失败显示友好提示

- **滚动条优化**
  - 每个测试结果卡片独立滚动（最大高度 600px）
  - 自定义滚动条样式
  - 避免内容被压缩

- **界面美化**
  - 参数和结果使用卡片式布局
  - 鼠标悬停高亮效果
  - 图片容器带边框和阴影

#### 3. 页面刷新恢复功能
- **自动恢复进行中的任务**
  - 页面刷新后自动恢复所有测试结果
  - 自动恢复 API 配置
  - 检测"进行中"的任务并继续轮询
  - 只恢复1小时内的任务，超时任务自动标记为失败

- **数据持久化**
  - 保存测试结果到 localStorage（24小时）
  - 保存 API 配置（pipeId, authorization, draft）
  - 保存每个测试的 taskId 和使用的 token

#### 4. 轮询逻辑增强
- **智能状态判断**
  - 支持 `progress: "completed"` - 任务完成
  - 支持 `progress: "handing"` - 处理中
  - 支持 `progress: "failed"` / `"error"` - 任务失败
  - 检测 completed 状态下的错误（errCode !== '00000'）

- **错误处理改进**
  - 正确识别和显示 API 返回的错误信息
  - 支持多种错误状态和错误格式
  - 错误任务自动标记为失败状态

- **数据解析优化**
  - 自动解析 content 字段（JSON 字符串）
  - 自动提取图片 URL（从嵌套的 JSON 结构中）
  - 支持多种数据格式（图片、文本、视频）

#### 5. 调试和日志
- **详细的控制台日志**
  - `[发送请求]` - 请求发送和响应
  - `[轮询]` - 轮询状态和进度
  - `[测试完成]` - 结果处理
  - `[ResultDisplay]` - UI 渲染
  - `[恢复轮询]` - 页面刷新后的恢复过程

- **响应式更新优化**
  - 强制触发 Vue 响应式更新
  - 确保状态变化实时反映在 UI 上

#### 6. API 接口适配
- **测试环境支持**
  - 发送请求：`https://cyapi-t.ideaflow.pro/uat/pipe/chat`
  - 查询进度：`https://cyapi.ideaflow.pro/pipe/album/progress`（生产环境）
  - 支持 Draft 模式（可选）

- **返回数据格式**
  ```javascript
  // 等待中
  {
    "code": 0,
    "data": {
      "progress": "handing",
      "errMsg": "",
      "content": null
    }
  }

  // 完成
  {
    "code": 0,
    "data": {
      "progress": "completed",
      "errMsg": "",
      "content": "[{...}]",  // JSON 字符串
      "errCode": "00000"
    }
  }

  // 错误
  {
    "code": 0,
    "data": {
      "progress": "completed",
      "errMsg": "(70010:3)错误信息",
      "errCode": "70010:3"
    }
  }
  ```

## 🛠 技术栈

### 前端框架
- **Vue 3** - 使用 Composition API
- **Vite** - 快速的开发构建工具
- **Element Plus** - UI 组件库

### 核心依赖
- **Axios** - HTTP 请求库
- **XLSX** - Excel 文件处理

### 开发环境
- Node.js 14+
- npm 或 yarn

## 📁 项目结构

```
studio-web/
├── index.html                    # 入口 HTML
├── package.json                  # 项目配置和依赖
├── vite.config.js               # Vite 构建配置
├── README.md                     # 用户使用文档
├── CLAUDE.md                     # 开发者架构文档（本文件）
│
├── src/
│   ├── main.js                  # 应用入口文件
│   ├── App.vue                  # 主应用组件
│   │
│   ├── components/              # Vue 组件目录
│   │   ├── ApiConfig.vue        # 接口配置组件
│   │   ├── ParamConfig.vue      # 参数配置组件
│   │   ├── BatchInput.vue       # 批量输入组件
│   │   └── ResultDisplay.vue    # 结果展示组件
│   │
│   ├── composables/             # 组合式函数（业务逻辑）
│   │   ├── useApiRequest.js     # API 请求封装
│   │   └── usePolling.js        # 轮询查询逻辑
│   │
│   └── utils/                   # 工具函数
│       ├── request.js           # Axios 实例配置
│       └── excel.js             # Excel 处理工具
│
└── node_modules/                # 依赖包
```

## 🎯 核心功能模块

### 1. 接口配置模块 (ApiConfig.vue)

**功能：**
- 管理多个接口配置
- 支持单账号和多账号轮询两种模式
- Token 列表管理（增删改）
- 一键导入请求体配置

**关键字段：**
- `pipeId`: Workflow ID
- `authorization`: 认证令牌
- `authTokens`: 多账号 token 列表（每行一个）
- `draft`: 草稿标识（可选）
- `authMode`: 认证模式（single/multiple）

**数据存储：**
- 使用 `localStorage` 持久化配置
- Key: `studio_api_configs`

### 2. 参数配置模块 (ParamConfig.vue)

**功能：**
- 配置请求参数（type, name, val）
- 支持三种类型：img（图片）、str（文本）、num（数字）
- 动态增删参数
- 从请求体导入参数

**参数结构：**
```javascript
{
  type: 'img' | 'str' | 'num',
  name: 'k_1',           // 参数名称
  val: ''                // 默认值
}
```

**数据存储：**
- Key: `studio_params_config`

### 3. 批量输入模块 (BatchInput.vue)

**功能：**
- 手动添加测试数据
- Excel/CSV 文件导入
- 快速批量测试（一键生成 N 次测试）
- 测试数据编辑和删除

**快速批量测试：**
- 支持快捷按钮：5次、10次、15次、20次
- 自定义输入任意次数（1-100）
- 使用当前参数配置的默认值
- 自动开始测试

### 4. 结果展示模块 (ResultDisplay.vue)

**功能：**
- 实时显示测试进度
- 结果筛选（全部/成功/失败/进行中）
- 支持图片、文本、视频三种内容展示
- 导出测试结果到 Excel

**结果数据结构：**
```javascript
{
  id: 'unique_id',
  index: 0,
  params: [],           // 请求参数
  status: 'pending' | 'success' | 'error',
  data: null,           // 返回结果
  error: null,          // 错误信息
  duration: 0,          // 耗时（毫秒）
  taskId: '',           // 任务ID
  usedToken: ''         // 使用的token（前20字符）
}
```

**数据缓存：**
- 测试结果自动保存到 `localStorage`
- Key: `studio_test_results`
- 保留时间：24小时
- 刷新页面自动恢复

## 🔄 数据流和状态管理

### 应用状态 (App.vue)

```javascript
// 配置状态
const apiConfig = ref({})        // 当前接口配置
const paramConfig = ref([])      // 参数配置列表

// 测试状态
const testing = ref(false)       // 是否正在测试
const testResults = ref([])      // 测试结果列表
const sentCount = ref(0)         // 已发送数量
const completedCount = ref(0)    // 已完成数量
const totalCount = ref(0)        // 总数量
const currentTokenIndex = ref(0) // 当前token索引
```

### 事件流

```
用户操作
  ↓
ApiConfig/ParamConfig/BatchInput (配置和输入)
  ↓
App.vue (协调器)
  ↓
useApiRequest (发送请求)
  ↓
usePolling (轮询查询)
  ↓
ResultDisplay (展示结果)
```

## 🚀 关键功能实现

### 1. 多账号轮询机制

**位置：** `App.vue`

**原理：**
```javascript
// 获取下一个 token（轮询）
const getNextToken = () => {
  const tokens = getTokenList()
  const token = tokens[currentTokenIndex.value % tokens.length]
  currentTokenIndex.value++
  return token
}
```

**特点：**
- 每次请求使用不同的 token
- 循环使用所有可用 token
- 有效避免单账号排队

### 2. 405 排队错误处理

**位置：** `App.vue` - `sendTestRequest`

**机制：**
```javascript
// 检测 405 错误
if (response.code === 405) {
  // 等待 2 秒后重试
  await new Promise(resolve => setTimeout(resolve, 2000))
  return sendTestRequest(params, index, retryCount + 1)
}
```

**特点：**
- 自动检测排队错误
- 等待 2 秒后重试
- 最多重试 3 次
- 界面显示重试状态

### 3. 智能轮询查询

**位置：** `composables/usePolling.js`

**配置：**
- 轮询间隔：1 秒
- 最大重试次数：300 次（5分钟）

**逻辑：**
```javascript
const startPolling = (taskId, queryFn, callback, interval = 1000) => {
  const poll = async () => {
    const result = await queryFn()

    if (result.code === 0) {
      // 任务完成
      callback({ success: true, data: result.data })
    } else {
      // 继续轮询
      setTimeout(poll, interval)
    }
  }

  poll()
}
```

### 4. 一键导入请求体

**位置：** `ApiConfig.vue` - `handleImport`

**解析流程：**
```javascript
const data = JSON.parse(importJson.value)

// 1. 提取 pipeId
currentApi.value.pipeId = data.pipeId

// 2. 提取参数列表
// 通知 ParamConfig 组件导入
emit('import-params', data.in)
```

### 5. 本地缓存机制

**缓存内容：**
1. 接口配置 (`studio_api_configs`)
2. 参数配置 (`studio_params_config`)
3. 测试结果 (`studio_test_results`)

**自动保存：**
- 配置变更时自动保存
- 测试结果实时保存
- 刷新页面自动恢复

## 🔧 API 接口说明

### 请求接口

**URL:** `https://cyapi-t.ideaflow.pro/uat/pipe/chat`

**方法:** POST

**请求头：**
```javascript
{
  'Authorization': 'token字符串',
  'Draft': '1',  // 可选
  'Content-Type': 'application/json'
}
```

**请求体：**
```javascript
{
  "event": "input",
  "pipeId": "workflow_id",
  "in": [
    {
      "type": "img",
      "name": "k_1",
      "val": "图片URL"
    }
  ]
}
```

**响应：**
```javascript
{
  "code": 0,           // 0=成功, 405=排队中
  "msg": "success",
  "data": "taskId"     // 任务ID，用于查询结果
}
```

### 查询接口

**URL:** `https://cyapi.ideaflow.pro/pipe/album/progress/{taskId}`

**方法:** GET

**请求头：**
```javascript
{
  'Authorization': 'token字符串',
  'Draft': '1'  // 可选
}
```

**响应：**
```javascript
{
  "code": 0,
  "data": {
    // 结果数据（图片URL、文本等）
  }
}
```

## 📝 开发指南

### 本地开发

```bash
# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev

# 3. 访问
http://localhost:5173
```

### 构建生产版本

```bash
npm run build

# 产物在 dist/ 目录
```

### 添加新功能

#### 1. 添加新组件

```vue
<!-- src/components/NewComponent.vue -->
<template>
  <div class="new-component">
    <!-- 模板 -->
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Props
const props = defineProps({
  // ...
})

// Emits
const emit = defineEmits(['event-name'])

// 逻辑
</script>

<style scoped>
/* 样式 */
</style>
```

#### 2. 添加新的 Composable

```javascript
// src/composables/useNewFeature.js
import { ref } from 'vue'

export function useNewFeature() {
  const state = ref(null)

  const doSomething = () => {
    // 逻辑
  }

  return {
    state,
    doSomething
  }
}
```

### 代码规范

1. **组件命名：** 使用 PascalCase（如 `ApiConfig.vue`）
2. **文件命名：** 使用 camelCase（如 `useApiRequest.js`）
3. **变量命名：** 使用 camelCase
4. **常量命名：** 使用 UPPER_SNAKE_CASE
5. **注释：** 使用中文，函数需要注释说明

## 🐛 常见问题

### 1. 轮询一直不停止

**原因：** API 返回格式不符合预期

**解决：** 检查 `usePolling.js` 中的成功判断逻辑

### 2. Token 轮询不生效

**检查：**
- 是否选择了"多账号轮询"模式
- Token 列表是否为空
- 每行是否只有一个 token

### 3. 导入 Excel 失败

**原因：**
- Excel 列名与参数配置不匹配
- 文件格式不支持

**解决：**
- 确保第一行列名与参数 name 一致
- 使用 .xlsx 或 .csv 格式

### 4. 测试结果丢失

**原因：** 清除了浏览器缓存

**解决：**
- 测试完及时导出结果
- 缓存只保留 24 小时

### 5. 405 错误一直重试

**原因：** 服务器持续排队

**解决：**
- 减少并发数量
- 使用更多 token
- 等待服务器负载降低

## 🔄 后续优化建议

### 功能增强
1. [ ] 支持测试计划保存和加载
2. [ ] 添加测试报告生成
3. [ ] 支持定时批量测试
4. [ ] 添加性能监控图表
5. [ ] 支持 WebSocket 实时推送结果

### 性能优化
1. [ ] 虚拟滚动优化大量结果展示
2. [ ] 使用 IndexedDB 替代 localStorage
3. [ ] 添加请求队列优化
4. [ ] 结果分页加载

### 用户体验
1. [ ] 添加深色模式
2. [ ] 快捷键支持
3. [ ] 拖拽排序
4. [ ] 更多主题配置

## 📚 相关资源

- [Vue 3 官方文档](https://cn.vuejs.org/)
- [Element Plus 文档](https://element-plus.org/zh-CN/)
- [Vite 文档](https://cn.vitejs.dev/)
- [Axios 文档](https://axios-http.com/zh/)

## 👥 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

MIT License

---

**最后更新：** 2025-10-29
**维护者：** Studio Team
