<template>
  <div class="api-config">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>接口配置</span>
          <div class="header-buttons">
            <el-button type="success" size="small" @click="showImportDialog">
              一键导入请求体
            </el-button>
            <el-button type="primary" size="small" @click="addNewApi">新增接口</el-button>
          </div>
        </div>
      </template>

      <!-- 接口选择器 -->
      <el-select
        v-model="currentApiId"
        placeholder="选择接口"
        size="large"
        style="width: 100%; margin-bottom: 20px"
        @change="handleApiChange"
      >
        <el-option
          v-for="api in apiList"
          :key="api.id"
          :label="api.name"
          :value="api.id"
        />
      </el-select>

      <!-- 当前接口配置表单 -->
      <el-form v-if="currentApi" label-width="120px">
        <el-form-item label="接口名称">
          <el-input v-model="currentApi.name" placeholder="请输入接口名称" />
        </el-form-item>

        <el-form-item label="PipeId" required>
          <el-input
            v-model="currentApi.pipeId"
            placeholder="调用不同 workflow 的参数"
          />
        </el-form-item>

        <el-form-item label="Authorization" required>
          <el-radio-group v-model="authMode" style="margin-bottom: 10px">
            <el-radio label="single">单个账号</el-radio>
            <el-radio label="multiple">多账号轮询（避免排队）</el-radio>
          </el-radio-group>

          <!-- 单个账号模式 -->
          <el-input
            v-if="authMode === 'single'"
            v-model="currentApi.authorization"
            type="textarea"
            :rows="2"
            placeholder="必填，用于身份认证"
          />

          <!-- 多账号模式 -->
          <div v-else>
            <el-alert
              title="多账号轮询模式"
              type="info"
              :closable="false"
              style="margin-bottom: 10px"
            >
              批量测试时会自动轮流使用不同账号的 token，避免单个账号排队
            </el-alert>

            <!-- Token 列表 -->
            <div class="token-list">
              <div
                v-for="(token, index) in tokenList"
                :key="index"
                class="token-item"
              >
                <el-tag
                  closable
                  @close="removeToken(index)"
                  type="success"
                  style="width: 100%; justify-content: space-between"
                >
                  <span class="token-text">
                    账号 {{ index + 1 }}: {{ token.substring(0, 30) }}...
                  </span>
                </el-tag>
              </div>
            </div>

            <!-- 添加新token -->
            <el-input
              v-model="newToken"
              placeholder="粘贴新的 token 后按回车添加"
              @keyup.enter="addToken"
              style="margin-top: 10px"
            >
              <template #append>
                <el-button @click="addToken" type="primary">添加</el-button>
              </template>
            </el-input>

            <div style="margin-top: 10px; color: #909399; font-size: 12px">
              当前共 {{ tokenCount }} 个账号 | 点击标签上的 × 可删除
            </div>
          </div>
        </el-form-item>

        <el-form-item label="Draft">
          <el-input
            v-model="currentApi.draft"
            placeholder="可选，默认为 1"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="success" @click="saveApiConfig">保存配置</el-button>
          <el-button type="danger" @click="deleteApi" v-if="apiList.length > 1">删除接口</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 导入请求体对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="一键导入请求体"
      width="600px"
    >
      <el-alert
        title="导入说明"
        type="info"
        :closable="false"
        style="margin-bottom: 15px"
      >
        粘贴完整的请求体 JSON，系统会自动解析并填充配置
      </el-alert>

      <el-input
        v-model="importJson"
        type="textarea"
        :rows="15"
        placeholder='粘贴请求体 JSON，例如：
{
  "event": "input",
  "pipeId": "000004712327027238682646",
  "in": [
    {
      "type": "img",
      "name": "k_5",
      "val": "https://img.ideaflow.pro/image/xxx.jpg"
    },
    {
      "type": "str",
      "name": "k_3",
      "val": "2"
    }
  ]
}'
      />

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImport">导入配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// Props 和 Emits
const emit = defineEmits(['api-change', 'import-params'])

// 数据
const apiList = ref([])
const currentApiId = ref('')
const currentApi = ref(null)
const authMode = ref('multiple') // 默认使用多账号模式

// 预置的10个 token
const DEFAULT_TOKENS = `metatube-eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDM3OTQ1MDc1NjE3NTY1NDA5MjgiLCJuaWNrbmFtZSI6InRlc3RlcjAwMDAzIiwiZXhwIjoxNzkxNTQzODcyLCJ1c2VySWQiOiIwMDAwMDM3OTQ1MDc1NjE3NTY1NDA5MjgiLCJqdGkiOiIwMDAwMDM3OTQ1MDc1NjE3NTY1NDA5MjgifQ.3tpGZ3KpaqnvohFW7h3kxjUqiBAXSaHoPwtljU0IKK40Nb2Lh0smcOEorWmFp4CegvjclXbNrhR29U4URtoUQg
metatube-eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDM3OTQ1MDc1NjQ4NDM1NDg2NzIiLCJuaWNrbmFtZSI6InRlc3RlcjAwMDA2IiwiZXhwIjoxNzkxNTQzODcyLCJ1c2VySWQiOiIwMDAwMDM3OTQ1MDc1NjQ4NDM1NDg2NzIiLCJqdGkiOiIwMDAwMDM3OTQ1MDc1NjQ4NDM1NDg2NzIifQ.hVkpPI39KhOTEhCxITh6r47R_VkHmR7xRcdnM-7wese4g-X2kIIMjQdAvkMxb4Kp9slWrNDcj0GWK8TLN64h1w
metatube-eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDM3OTQ1MDc1NjcxOTYzMDc0NTYiLCJuaWNrbmFtZSI6InRlc3RlcjAwMDA5IiwiZXhwIjoxNzkxNTQzODcyLCJ1c2VySWQiOiIwMDAwMDM3OTQ1MDc1NjcxOTYzMDc0NTYiLCJqdGkiOiIwMDAwMDM3OTQ1MDc1NjcxOTYzMDc0NTYifQ.wE1wmWiJNVKC2D7rqNb6sJjAkCrb-g_DXCt9MLUVM-WdB55_vce360MROfgv5N7cFvK5z9erYm6SoF3NqnYmzg
metatube-eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDM3OTQ1MDc1NTgxNzAxNjUyNDgiLCJuaWNrbmFtZSI6InRlc3RlcjAwMDAwIiwiZXhwIjoxNzkxNTQzODcxLCJ1c2VySWQiOiIwMDAwMDM3OTQ1MDc1NTgxNzAxNjUyNDgiLCJqdGkiOiIwMDAwMDM3OTQ1MDc1NTgxNzAxNjUyNDgifQ.VcCphjC9yEb8RVumetQQQTipBpQoN4nTs7uPKdd1bsMdLxHebRT03pOpxI_o4knes_LpsbZJuZlfdJCjUGNtnw
metatube-eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDM3OTQ1MDc1NjY0MzczODQxOTIiLCJuaWNrbmFtZSI6InRlc3RlcjAwMDA4IiwiZXhwIjoxNzkxNTQzODcyLCJ1c2VySWQiOiIwMDAwMDM3OTQ1MDc1NjY0MzczODQxOTIiLCJqdGkiOiIwMDAwMDM3OTQ1MDc1NjY0MzczODQxOTIifQ.ufrTuuJCeUpwP6gJWWRERNVp4eUNVIvSllNaD4vx2gfuIUkiG6mNj4N-sedjW9OjP-pkne5gaRBPwOPoXdAQoA
metatube-eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDM3OTQ1MDc1NjA5NTUxODMxMDQiLCJuaWNrbmFtZSI6InRlc3RlcjAwMDAyIiwiZXhwIjoxNzkxNTQzODcyLCJ1c2VySWQiOiIwMDAwMDM3OTQ1MDc1NjA5NTUxODMxMDQiLCJqdGkiOiIwMDAwMDM3OTQ1MDc1NjA5NTUxODMxMDQifQ.rcMrIgN32gTWa0_iRhrDaAtg4iwV1i52YV8s8ESrXB1L0QgaghMKmZDICSgzIkwoYjLPZR2L-hSGt9zDvJbMsA
metatube-eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDM3OTQ0OTExNjkwMjQwMDAwMDAiLCJuaWNrbmFtZSI6InRlc3RlcjAwMDAxIiwiZXhwIjoxNzkxNTQzODcyLCJ1c2VySWQiOiIwMDAwMDM3OTQ0OTExNjkwMjQwMDAwMDAiLCJqdGkiOiIwMDAwMDM3OTQ0OTExNjkwMjQwMDAwMDAifQ.U9utLfepuOf7kUPZkz3newxyr91PfH9nsM9_0RDxGsfQJWumiAz7RSIT581NXfzWPEjadmz0V_kV-o966btDPA
metatube-eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDM3OTQ1MDc1NjMwMTQ4MzIxMjgiLCJuaWNrbmFtZSI6InRlc3RlcjAwMDA0IiwiZXhwIjoxNzkxNTQzODcyLCJ1c2VySWQiOiIwMDAwMDM3OTQ1MDc1NjMwMTQ4MzIxMjgiLCJqdGkiOiIwMDAwMDM3OTQ1MDc1NjMwMTQ4MzIxMjgifQ.YGo9TG4decBz5KU77Uwmav7fxQHUJ9-yP10wBPmT5DUrAPWztaTt7sHHiMsUdAUXLnyIBu3VWcCoMYqMUYsCXA
metatube-eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDM3OTQ1MDc1NjU2MDI0NzE5MzYiLCJuaWNrbmFtZSI6InRlc3RlcjAwMDA3IiwiZXhwIjoxNzkxNTQzODcyLCJ1c2VySWQiOiIwMDAwMDM3OTQ1MDc1NjU2MDI0NzE5MzYiLCJqdGkiOiIwMDAwMDM3OTQ1MDc1NjU2MDI0NzE5MzYifQ.1RawgQIBbR4A1n3WFTV1JgLmaTqdorkjvNPZ4C7NfU4EWces6XCbxXehQ7NBF4HCk6bnTW4Fw9fQn694rkgBig
metatube-eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDM3OTQ1MDc1NjQwOTI1MjI0OTYiLCJuaWNrbmFtZSI6InRlc3RlcjAwMDA1IiwiZXhwIjoxNzkxNTQzODcyLCJ1c2VySWQiOiIwMDAwMDM3OTQ1MDc1NjQwOTI1MjI0OTYiLCJqdGkiOiIwMDAwMDM3OTQ1MDc1NjQwOTI1MjI0OTYifQ.UhJ9hYLtqcXJUwNYYWuTKDrsv3fawgUkjLRWxhb59lczT0TG7xjfzYXN_7c557GDENR1cE89s4FI8yLfzG6W0Q`

// 计算 token 数量
const tokenCount = computed(() => {
  if (!currentApi.value || !currentApi.value.authTokens) return 0
  return currentApi.value.authTokens.split('\n').filter(t => t.trim()).length
})

// Token 列表
const tokenList = computed(() => {
  if (!currentApi.value || !currentApi.value.authTokens) return []
  return currentApi.value.authTokens.split('\n').filter(t => t.trim())
})

// 新 token 输入
const newToken = ref('')

// 导入对话框
const importDialogVisible = ref(false)
const importJson = ref('')

// 添加 token
const addToken = () => {
  if (!newToken.value.trim()) {
    ElMessage.warning('请输入 token')
    return
  }

  const tokens = tokenList.value
  tokens.push(newToken.value.trim())
  currentApi.value.authTokens = tokens.join('\n')
  newToken.value = ''
  ElMessage.success('Token 已添加')
}

// 删除 token
const removeToken = (index) => {
  const tokens = tokenList.value
  tokens.splice(index, 1)
  currentApi.value.authTokens = tokens.join('\n')
  ElMessage.success('Token 已删除')
}

// 显示导入对话框
const showImportDialog = () => {
  importJson.value = ''
  importDialogVisible.value = true
}

// 处理导入
const handleImport = () => {
  try {
    // 解析 JSON
    const data = JSON.parse(importJson.value)

    // 验证数据格式
    if (!data.pipeId) {
      ElMessage.warning('请求体中缺少 pipeId 字段')
      return
    }

    if (!data.in || !Array.isArray(data.in)) {
      ElMessage.warning('请求体中缺少 in 字段或格式不正确')
      return
    }

    // 更新 pipeId
    currentApi.value.pipeId = data.pipeId

    // 通知父组件导入参数
    emit('import-params', data.in)

    // 关闭对话框
    importDialogVisible.value = false

    ElMessage.success('导入成功！请记得保存配置')
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('JSON 格式错误，请检查后重试')
  }
}

// 生成唯一ID
const generateId = () => {
  return 'api_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

// 初始化默认接口
const initDefaultApi = () => {
  const defaultApi = {
    id: generateId(),
    name: '默认接口',
    pipeId: '',
    authorization: '',
    authTokens: DEFAULT_TOKENS, // 预置10个token
    draft: '1'
  }
  apiList.value = [defaultApi]
  currentApiId.value = defaultApi.id
  currentApi.value = { ...defaultApi }
  authMode.value = 'multiple' // 默认使用多账号模式
}

// 加载保存的配置
const loadConfig = () => {
  const saved = localStorage.getItem('studio_api_configs')
  if (saved) {
    try {
      const configs = JSON.parse(saved)
      apiList.value = configs
      if (configs.length > 0) {
        currentApiId.value = configs[0].id
        currentApi.value = { ...configs[0] }
      }
    } catch (error) {
      console.error('加载配置失败:', error)
      initDefaultApi()
    }
  } else {
    initDefaultApi()
  }
}

// 保存配置到 localStorage
const saveToStorage = () => {
  localStorage.setItem('studio_api_configs', JSON.stringify(apiList.value))
}

// 新增接口
const addNewApi = () => {
  const newApi = {
    id: generateId(),
    name: '新接口',
    pipeId: '',
    authorization: '',
    authTokens: DEFAULT_TOKENS, // 预置10个token
    draft: '1'
  }
  apiList.value.push(newApi)
  currentApiId.value = newApi.id
  currentApi.value = { ...newApi }
  saveToStorage()
  ElMessage.success('新接口已添加')
}

// 切换接口
const handleApiChange = () => {
  const api = apiList.value.find(a => a.id === currentApiId.value)
  if (api) {
    currentApi.value = { ...api }
    authMode.value = api.authMode || 'multiple'
    emit('api-change', { ...currentApi.value, authMode: authMode.value })
  }
}

// 保存接口配置
const saveApiConfig = () => {
  if (!currentApi.value.name) {
    ElMessage.warning('请输入接口名称')
    return
  }
  if (!currentApi.value.pipeId) {
    ElMessage.warning('请输入 PipeId')
    return
  }

  // 验证 Authorization
  if (authMode.value === 'single') {
    if (!currentApi.value.authorization) {
      ElMessage.warning('请输入 Authorization')
      return
    }
  } else {
    if (!currentApi.value.authTokens || currentApi.value.authTokens.trim() === '') {
      ElMessage.warning('请输入至少一个 token')
      return
    }
  }

  const index = apiList.value.findIndex(a => a.id === currentApiId.value)
  if (index !== -1) {
    apiList.value[index] = { ...currentApi.value, authMode: authMode.value }
    saveToStorage()
    emit('api-change', { ...currentApi.value, authMode: authMode.value })
    ElMessage.success('配置保存成功')
  }
}

// 删除接口
const deleteApi = () => {
  if (apiList.value.length <= 1) {
    ElMessage.warning('至少保留一个接口')
    return
  }

  apiList.value = apiList.value.filter(a => a.id !== currentApiId.value)

  if (apiList.value.length > 0) {
    currentApiId.value = apiList.value[0].id
    currentApi.value = { ...apiList.value[0] }
  }

  saveToStorage()
  ElMessage.success('接口已删除')
}

// 监听当前接口变化
watch(currentApi, () => {
  if (currentApi.value) {
    emit('api-change', currentApi.value)
  }
}, { deep: true })

// 组件挂载时加载配置
onMounted(() => {
  loadConfig()
  if (currentApi.value) {
    emit('api-change', currentApi.value)
  }
})
</script>

<style scoped>
.api-config {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.token-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  background-color: #f5f7fa;
}

.token-item {
  margin-bottom: 8px;
}

.token-item:last-child {
  margin-bottom: 0;
}

.token-text {
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 12px;
  word-break: break-all;
}
</style>
