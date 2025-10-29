# Studio 批量测试工具

一个用于批量测试 Studio API 接口的网页工具，支持多接口配置、批量数据导入、自动轮询查询结果等功能。

## 功能特性

### 🔧 接口配置
- ✅ 支持配置多个接口
- ✅ 可动态切换不同接口
- ✅ 配置自动保存到本地
- ✅ 支持配置 Authorization、Draft、PipeId 等参数

### 📝 参数配置
- ✅ 支持三种输入类型：图片(img)、文本(str)、数字(num)
- ✅ 动态添加和删除参数
- ✅ 自定义参数名称
- ✅ 参数默认值缓存

### 📊 批量测试
- ✅ 手动添加多组测试数据
- ✅ 从 Excel/CSV 文件导入测试数据
- ✅ 自动批量发送请求
- ✅ 智能并发控制（默认5个并发）

### 🔍 结果查询
- ✅ 自动轮询查询结果
- ✅ 实时显示测试进度
- ✅ 支持图片、文本、视频结果展示
- ✅ 状态筛选（全部/成功/失败/进行中）
- ✅ 导出测试结果到 Excel

## 快速开始

### 1. 安装依赖

```bash
cd studio-web
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

启动后会自动打开浏览器，访问 `http://localhost:3000`

### 3. 构建生产版本

```bash
npm run build
```

构建完成后，产物在 `dist` 目录中。

## 使用指南

### 第一步：配置接口

1. 在左侧「接口配置」区域，填写以下信息：
   - **接口名称**：给接口起个名字，方便识别
   - **PipeId**：你的 workflow ID（必填）
   - **Authorization**：身份认证令牌（必填）
   - **Draft**：草稿标识（可选，默认为 1）

2. 点击「保存配置」按钮

3. 如需配置多个接口，点击「新增接口」按钮

### 第二步：配置输入参数

1. 在左侧「输入参数配置」区域，点击「添加参数」
2. 为每个参数配置：
   - **参数类型**：选择 img（图片）、str（文本）或 num（数字）
   - **参数名称**：如 k_1, k_2, k_3 等
   - **默认值**：设置默认值（可选，会被缓存）
3. 点击「保存参数配置」

### 第三步：准备测试数据

#### 方式一：手动添加
1. 在右侧「批量测试数据」区域，点击「手动添加」
2. 在表格中填写每组测试数据
3. 可点击「删除」按钮删除某一组数据

#### 方式二：导入 Excel
1. 准备 Excel 文件，格式如下：
   ```
   | k_1 | k_2 | k_3 |
   |-----|-----|-----|
   | 值1 | 值2 | 值3 |
   | 值4 | 值5 | 值6 |
   ```
   - 第一行是参数名称（需与参数配置中的名称一致）
   - 后续每行是一组测试数据

2. 点击「导入 Excel」按钮，选择文件

### 第四步：开始测试

1. 点击「开始批量测试」按钮
2. 系统会自动：
   - 批量发送请求到 API
   - 自动轮询查询每个任务的结果
   - 实时更新测试进度和结果

### 第五步：查看结果

1. 在「测试结果」区域查看所有测试结果
2. 可以：
   - 筛选不同状态的结果（全部/成功/失败/进行中）
   - 查看每个测试的请求参数和返回结果
   - 预览图片和播放视频
   - 点击「导出结果」按钮导出到 Excel

## Excel 导入格式示例

```csv
k_1,k_2,k_3,k_4
https://example.com/image1.jpg,https://example.com/image2.jpg,2,女
https://example.com/image3.jpg,https://example.com/image4.jpg,1,男
```

## API 接口说明

### 请求接口
- **URL**: `https://cyapi-t.ideaflow.pro/uat/pipe/chat`
- **方法**: POST
- **请求头**:
  - `Authorization`: 认证令牌（必填）
  - `Draft`: 草稿标识（可选）
  - `Content-Type`: application/json

- **请求体**:
```json
{
  "event": "input",
  "pipeId": "你的 workflow ID",
  "in": [
    {
      "type": "img",
      "name": "k_1",
      "val": "图片URL"
    },
    {
      "type": "str",
      "name": "k_2",
      "val": "文本内容"
    }
  ]
}
```

### 查询接口
- **URL**: `https://cyapi.ideaflow.pro/pipe/album/progress/{taskId}`
- **方法**: GET
- **请求头**:
  - `Authorization`: 认证令牌
  - `Draft`: 草稿标识（可选）

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **HTTP 客户端**: Axios
- **Excel 处理**: XLSX

## 项目结构

```
studio-web/
├── index.html                  # 入口 HTML
├── package.json                # 项目配置
├── vite.config.js             # Vite 配置
├── src/
│   ├── main.js                # 应用入口
│   ├── App.vue                # 主应用组件
│   ├── components/            # 组件目录
│   │   ├── ApiConfig.vue      # 接口配置组件
│   │   ├── ParamConfig.vue    # 参数配置组件
│   │   ├── BatchInput.vue     # 批量输入组件
│   │   └── ResultDisplay.vue  # 结果展示组件
│   ├── composables/           # 组合式函数
│   │   ├── useApiRequest.js   # API 请求逻辑
│   │   └── usePolling.js      # 轮询逻辑
│   └── utils/                 # 工具函数
│       ├── request.js         # Axios 封装
│       └── excel.js           # Excel 处理
```

## 常见问题

### 1. 导入 Excel 提示缺少参数列？
确保 Excel 文件的第一行列名与参数配置中的参数名称完全一致。

### 2. 测试一直显示"进行中"？
检查网络连接和 API 地址是否正确，查询接口可能返回了错误。

### 3. 如何批量测试不同接口？
先配置好所有接口，然后在顶部切换接口，每个接口可以单独进行批量测试。

### 4. 配置数据会丢失吗？
不会，所有配置（接口配置、参数配置）都会自动保存到浏览器本地存储。

## 开发说明

### 修改 API 地址
如需修改 API 地址，请编辑以下文件：
- `src/composables/useApiRequest.js`

### 修改轮询间隔
轮询间隔默认为 2 秒，可在 `src/App.vue` 中修改。

### 调整并发数
并发数默认为 5，可在 `src/App.vue` 的 `handleStartTest` 方法中修改 `concurrencyLimit`。

## 许可证

MIT License
