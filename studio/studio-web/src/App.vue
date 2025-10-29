<template>
  <div id="app" class="app-container">
    <!-- 头部 -->
    <el-header class="app-header">
      <h1>Studio 批量测试工具</h1>
      <el-tag type="info">v1.0.0</el-tag>
    </el-header>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 左侧配置区 -->
      <el-aside width="450px" class="config-sidebar">
        <el-scrollbar>
          <!-- 接口配置 -->
          <ApiConfig
            @api-change="handleApiChange"
            @import-params="handleImportParams"
          />

          <!-- 参数配置 -->
          <ParamConfig
            ref="paramConfigRef"
            @params-change="handleParamsChange"
          />
        </el-scrollbar>
      </el-aside>

      <!-- 右侧主区域 -->
      <el-main class="main-content">
        <el-scrollbar>
          <!-- 批量输入 -->
          <BatchInput
            :param-config="paramConfig"
            :api-config="apiConfig"
            @start-test="handleStartTest"
          />

          <!-- 测试进度 -->
          <el-card v-if="testing" class="testing-progress" shadow="hover">
            <el-alert
              title="正在执行批量测试..."
              type="info"
              :closable="false"
              show-icon
            >
              <template #default>
                <div class="progress-info">
                  <p>已发送: {{ sentCount }} / {{ totalCount }}</p>
                  <p>已完成: {{ completedCount }} / {{ totalCount }}</p>
                  <el-progress
                    :percentage="testProgressPercentage"
                    :status="allTestsCompleted ? 'success' : undefined"
                  />
                </div>
              </template>
            </el-alert>
          </el-card>

          <!-- 结果展示 -->
          <ResultDisplay :results="testResults" />
        </el-scrollbar>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import ApiConfig from './components/ApiConfig.vue'
import ParamConfig from './components/ParamConfig.vue'
import BatchInput from './components/BatchInput.vue'
import ResultDisplay from './components/ResultDisplay.vue'
import { useApiRequest } from './composables/useApiRequest'
import { usePolling } from './composables/usePolling'

// API 和参数配置
const apiConfig = ref({})
const paramConfig = ref([])
const paramConfigRef = ref(null) // ParamConfig 组件的引用

// 测试相关
const testing = ref(false)
const testResults = ref([])
const sentCount = ref(0)
const completedCount = ref(0)
const totalCount = ref(0)
const currentTokenIndex = ref(0) // 当前使用的 token 索引（用于轮询）

// API 请求和轮询
const { sendRequest, queryResult } = useApiRequest()
const { startPolling, stopAllPolling } = usePolling()

// 获取token列表
const getTokenList = () => {
  if (apiConfig.value.authMode === 'multiple' && apiConfig.value.authTokens) {
    return apiConfig.value.authTokens.split('\n').filter(t => t.trim())
  }
  return []
}

// 获取下一个 token（轮询）
// 返回 { token, accountIndex, accountName }
const getNextToken = () => {
  const tokens = getTokenList()
  if (tokens.length === 0) {
    return {
      token: apiConfig.value.authorization,
      accountIndex: 0,
      accountName: '默认账号'
    }
  }

  const accountIndex = currentTokenIndex.value % tokens.length
  const token = tokens[accountIndex]
  currentTokenIndex.value++
  return {
    token,
    accountIndex,
    accountName: `账号${accountIndex + 1}`
  }
}

// 测试进度
const testProgressPercentage = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((completedCount.value / totalCount.value) * 100)
})

const allTestsCompleted = computed(() => {
  return completedCount.value === totalCount.value && totalCount.value > 0
})

// 处理接口配置变化
const handleApiChange = (config) => {
  apiConfig.value = config
}

// 处理参数配置变化
const handleParamsChange = (params) => {
  paramConfig.value = params
}

// 处理导入参数
const handleImportParams = (params) => {
  // 通过 ref 调用 ParamConfig 组件的方法来导入参数
  if (paramConfigRef.value) {
    paramConfigRef.value.importParams(params)
  }
}

// 开始批量测试
const handleStartTest = async (testData) => {
  if (!apiConfig.value || !apiConfig.value.pipeId) {
    ElMessage.error('请先配置接口')
    return
  }

  if (testData.length === 0) {
    ElMessage.warning('没有测试数据')
    return
  }

  // 重置状态
  testing.value = true
  testResults.value = []
  sentCount.value = 0
  completedCount.value = 0
  totalCount.value = testData.length
  currentTokenIndex.value = 0 // 重置token索引

  ElNotification({
    title: '开始测试',
    message: `准备发送 ${testData.length} 个测试请求`,
    type: 'info'
  })

  // 批量发送请求（限制并发数）
  const concurrencyLimit = 5 // 同时最多5个请求
  const batches = []

  for (let i = 0; i < testData.length; i += concurrencyLimit) {
    const batch = testData.slice(i, i + concurrencyLimit)
    batches.push(batch)
  }

  // 逐批次发送
  for (const batch of batches) {
    await Promise.all(
      batch.map((testItem, batchIndex) => {
        const globalIndex = testResults.value.length
        return sendTestRequest(testItem, globalIndex)
      })
    )
  }

  ElNotification({
    title: '请求发送完成',
    message: `已发送 ${totalCount.value} 个请求，正在查询结果...`,
    type: 'success'
  })
}

// 发送单个测试请求（支持重试）
const sendTestRequest = async (testItem, index, retryCount = 0) => {
  const startTime = Date.now()
  const maxRetries = 3 // 最大重试次数

  // 兼容旧格式和新格式
  const params = testItem.params || testItem
  const groupIndex = testItem.groupIndex !== undefined ? testItem.groupIndex : null
  const testIndex = testItem.testIndex !== undefined ? testItem.testIndex : null
  const groupTestCount = testItem.groupTestCount || null

  // 创建结果对象（仅在第一次时）
  let result
  if (retryCount === 0) {
    result = {
      id: Date.now() + '_' + index,
      index,
      params,
      groupIndex, // 所属组索引
      testIndex, // 组内测试索引
      groupTestCount, // 该组总测试次数
      status: 'pending',
      data: null,
      error: null,
      duration: null,
      taskId: null,
      usedToken: null // 记录使用的token（用于调试）
    }
    testResults.value.push(result)
  } else {
    result = testResults.value[index]
  }

  try {
    // 获取要使用的 token（轮询）
    let token, accountIndex, accountName
    if (apiConfig.value.authMode === 'multiple') {
      const tokenInfo = getNextToken()
      token = tokenInfo.token
      accountIndex = tokenInfo.accountIndex
      accountName = tokenInfo.accountName
    } else {
      token = apiConfig.value.authorization
      accountIndex = 0
      accountName = '默认账号'
    }

    result.usedToken = token.substring(0, 20) + '...' // 只保存前20个字符用于调试
    result.accountIndex = accountIndex // 保存账号索引
    result.accountName = accountName // 保存账号名称

    // 创建临时配置对象，使用轮询的 token
    const requestConfig = {
      ...apiConfig.value,
      authorization: token
    }

    // 发送请求
    console.log(`[发送请求] 测试 #${index + 1} 发送参数:`, params)
    const response = await sendRequest(requestConfig, params)
    console.log(`[发送请求] 测试 #${index + 1} 响应:`, response)

    // 检查是否是排队错误 (code: 405)
    // response 可能是对象（包含 code）或字符串（taskId）
    if (typeof response === 'object' && response.code === 405) {
      // 排队中，需要重试
      if (retryCount < maxRetries) {
        result.status = 'pending'
        result.error = `排队中，2秒后重试... (第${retryCount + 1}次)`

        // 等待2秒后重试
        await new Promise(resolve => setTimeout(resolve, 2000))
        return sendTestRequest(testItem, index, retryCount + 1)
      } else {
        throw new Error('超过最大重试次数，服务器排队中，请稍后再试')
      }
    }

    // 成功获取 taskId（response 是字符串）
    const taskId = response
    result.taskId = taskId
    result.error = null // 清空之前的错误信息
    sentCount.value++

    console.log(`[发送请求] ✅ 测试 #${index + 1} 获取 taskId: ${taskId}，开始轮询...`)

    // 开始轮询查询结果（使用相同的 token）
    startPolling(
      taskId,
      () => queryResult(taskId, token, apiConfig.value.draft),
      (pollingResult) => handleTestComplete(result, pollingResult, startTime)
    )
  } catch (error) {
    // 检查是否是405错误
    if (error.response && error.response.status === 405) {
      if (retryCount < maxRetries) {
        result.status = 'pending'
        result.error = `排队中，${2}秒后重试... (第${retryCount + 1}次)`

        await new Promise(resolve => setTimeout(resolve, 2000))
        return sendTestRequest(testItem, index, retryCount + 1)
      }
    }

    result.status = 'error'
    result.error = error.message || '请求失败'
    result.duration = Date.now() - startTime
    completedCount.value++
    checkAllCompleted()
  }
}

// 处理测试完成
const handleTestComplete = (result, pollingResult, startTime) => {
  console.log('[测试完成] 收到回调:', pollingResult)
  console.log('[测试完成] 当前result对象:', result)

  result.duration = Date.now() - startTime

  if (pollingResult.success) {
    result.status = 'success'
    result.data = pollingResult.data
    console.log('[测试完成] ✅ 设置结果数据:', result.data)
  } else {
    result.status = 'error'
    result.error = pollingResult.error || '查询失败'
    result.data = null
    console.log('[测试完成] ❌ 设置错误:', result.error)
  }

  console.log('[测试完成] 更新后的result:', JSON.stringify(result))

  // 强制触发响应式更新
  testResults.value = [...testResults.value]

  completedCount.value++
  checkAllCompleted()

  console.log('[测试完成] 当前所有结果:', testResults.value.map(r => ({
    index: r.index,
    status: r.status,
    hasData: !!r.data,
    hasError: !!r.error
  })))
}

// 检查是否全部完成
const checkAllCompleted = () => {
  if (completedCount.value === totalCount.value) {
    testing.value = false

    const successCount = testResults.value.filter(r => r.status === 'success').length
    const errorCount = testResults.value.filter(r => r.status === 'error').length

    ElNotification({
      title: '测试完成',
      message: `成功: ${successCount}, 失败: ${errorCount}`,
      type: successCount === totalCount.value ? 'success' : 'warning',
      duration: 5000
    })
  }
}

// 保存测试结果到本地
const saveTestResults = () => {
  try {
    const data = {
      results: testResults.value,
      timestamp: Date.now(),
      apiConfig: {
        pipeId: apiConfig.value.pipeId,
        authorization: apiConfig.value.authorization,
        authMode: apiConfig.value.authMode,
        authTokens: apiConfig.value.authTokens, // 保存多账号token列表
        draft: apiConfig.value.draft
      }
    }
    localStorage.setItem('studio_test_results', JSON.stringify(data))
  } catch (error) {
    console.error('保存测试结果失败:', error)
  }
}

// 加载测试结果
const loadTestResults = () => {
  try {
    const saved = localStorage.getItem('studio_test_results')
    if (saved) {
      const data = JSON.parse(saved)
      // 只加载24小时内的结果
      const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000
      if (data.timestamp > oneDayAgo) {
        testResults.value = data.results || []

        // 恢复 API 配置（如果当前没有配置）
        if (data.apiConfig && (!apiConfig.value || !apiConfig.value.pipeId)) {
          apiConfig.value = data.apiConfig
          console.log('[恢复轮询] 恢复 API 配置:', apiConfig.value)
        }

        if (testResults.value.length > 0) {
          // 更新完成数量
          completedCount.value = testResults.value.filter(
            r => r.status === 'success' || r.status === 'error'
          ).length
          totalCount.value = testResults.value.length

          // 检查是否有进行中的任务需要恢复轮询
          // 只恢复1小时内的任务，超过1小时的任务可能已经失效
          const oneHourAgo = Date.now() - 60 * 60 * 1000
          const pendingTests = []

          testResults.value.forEach(r => {
            if (r.status === 'pending' && r.taskId) {
              // 如果有记录创建时间，检查是否超过1小时
              const taskTime = parseInt(r.id.split('_')[0]) || Date.now()
              if (taskTime > oneHourAgo) {
                pendingTests.push(r)
              } else {
                // 超过1小时的任务标记为超时失败
                r.status = 'error'
                r.error = '任务已超时（超过1小时未完成）'
                completedCount.value++
                console.log(`[恢复轮询] 任务 ${r.taskId} 已超时，标记为失败`)
              }
            }
          })

          if (pendingTests.length > 0 && apiConfig.value && apiConfig.value.pipeId) {
            console.log(`[恢复轮询] 发现 ${pendingTests.length} 个进行中的任务`)
            testing.value = true
            sentCount.value = testResults.value.filter(r => r.taskId).length

            // 恢复每个进行中任务的轮询
            pendingTests.forEach(result => {
              console.log(`[恢复轮询] 恢复任务: ${result.taskId}`)

              // 使用保存的 API 配置中的 token
              let token
              if (apiConfig.value.authMode === 'multiple') {
                const tokenInfo = getNextToken()
                token = tokenInfo.token
              } else {
                token = apiConfig.value.authorization
              }

              const startTime = Date.now() - (result.duration || 0)

              // 重新开始轮询
              startPolling(
                result.taskId,
                () => queryResult(result.taskId, token, apiConfig.value.draft),
                (pollingResult) => handleTestComplete(result, pollingResult, startTime)
              )
            })

            ElNotification({
              title: '已恢复历史测试',
              message: `加载了 ${testResults.value.length} 条记录，其中 ${pendingTests.length} 个任务正在继续执行`,
              type: 'info',
              duration: 5000
            })
          } else {
            ElNotification({
              title: '已恢复历史测试结果',
              message: `加载了 ${testResults.value.length} 条历史测试记录`,
              type: 'success',
              duration: 3000
            })
          }
        }
      }
    }
  } catch (error) {
    console.error('加载测试结果失败:', error)
  }
}

// 监听测试结果变化，自动保存
watch(testResults, () => {
  if (testResults.value.length > 0) {
    saveTestResults()
  }
}, { deep: true })

// 组件挂载时加载测试结果
onMounted(() => {
  loadTestResults()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
}

.app-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.main-container {
  flex: 1;
  overflow: hidden;
}

.config-sidebar {
  background-color: #f5f7fa;
  border-right: 1px solid #dcdfe6;
  padding: 20px;
}

.main-content {
  padding: 20px;
  background-color: #ffffff;
}

.testing-progress {
  margin-bottom: 20px;
}

.progress-info {
  margin-top: 10px;
}

.progress-info p {
  margin: 5px 0;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
