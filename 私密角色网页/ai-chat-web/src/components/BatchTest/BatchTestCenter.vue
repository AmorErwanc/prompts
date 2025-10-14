<template>
  <div class="batch-test-center">
    <div class="page-header">
      <h2>批量测试中心</h2>
      <div class="header-actions">
        <button class="btn-secondary" @click="showNewTest = !currentBatch">
          {{ currentBatch ? '查看结果' : '新建测试' }}
        </button>
        <button v-if="!showNewTest" class="btn-secondary" @click="handleClose">
          关闭
        </button>
      </div>
    </div>

    <!-- 新建测试配置 -->
    <div v-if="showNewTest" class="test-config-section">
      <TestConfig
        :is-running="isRunning"
        @start="handleStartTest"
        @stop="handleStopTest"
      />
    </div>

    <!-- 测试结果展示 -->
    <div v-else-if="currentBatch" class="test-results-section">
      <!-- 测试信息 -->
      <div class="test-info">
        <div class="info-row">
          <span class="info-label">测试名称:</span>
          <span class="info-value">
            {{ currentBatch.config.test_name || `测试-${formatDate(currentBatch.created_at)}` }}
          </span>
        </div>
        <div class="info-row">
          <span class="info-label">输入内容:</span>
          <span class="info-value">{{ truncateText(currentBatch.config.user_prompt, 100) }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">ID策略:</span>
          <span class="info-value">
            {{ currentBatch.config.id_strategy === 'same_user' ? '同user不同session' : '不同user不同session' }}
          </span>
        </div>
      </div>

      <!-- 统计数据 -->
      <TestStatistics :statistics="currentBatch.statistics" />

      <!-- 测试进度 -->
      <div v-if="isRunning" class="progress-section">
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: progressPercent + '%' }"
          ></div>
        </div>
        <div class="progress-text">
          测试进度: {{ currentBatch.statistics.success + currentBatch.statistics.failed }} / {{ currentBatch.statistics.total }}
          {{ isRunning ? '进行中...' : '已完成' }}
        </div>
      </div>

      <!-- 测试结果列表 -->
      <TestResults
        :results="currentBatch.results"
        @view-detail="handleViewDetail"
        @enter-chat="handleEnterChat"
        @append-round="handleAppendRound"
        @batch-append="handleBatchAppend"
      />
    </div>

    <!-- 详情弹窗 -->
    <TestDetailModal
      :visible="showDetailModal"
      :result="selectedResult"
      @close="showDetailModal = false"
      @enter-chat="handleEnterChat"
    />

    <!-- 批量追加弹窗 -->
    <BatchAppendModal
      :visible="showAppendModal"
      :results="appendResults"
      :is-sending="isSendingAppend"
      @close="showAppendModal = false"
      @send="handleSendAppend"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useBatchTestStore } from '../../stores/batchTestStore'
import TestConfig from './TestConfig.vue'
import TestStatistics from './TestStatistics.vue'
import TestResults from './TestResults.vue'
import TestDetailModal from './TestDetailModal.vue'
import BatchAppendModal from './BatchAppendModal.vue'

const emit = defineEmits(['close', 'enter-chat'])

const batchTestStore = useBatchTestStore()

// 状态
const showNewTest = ref(true)
const showDetailModal = ref(false)
const showAppendModal = ref(false)
const selectedResult = ref({})
const appendResults = ref([])
const isSendingAppend = ref(false)

// 计算属性
const currentBatch = computed(() => batchTestStore.currentBatch)
const isRunning = computed(() => batchTestStore.isRunning)

const progressPercent = computed(() => {
  if (!currentBatch.value) return 0
  const { success, failed, total } = currentBatch.value.statistics
  return ((success + failed) / total) * 100
})

// 初始化
onMounted(() => {
  batchTestStore.initialize()
  // 如果有当前批次，显示结果
  if (currentBatch.value) {
    showNewTest.value = false
  }
})

// 开始测试
async function handleStartTest(config) {
  showNewTest.value = false
  await batchTestStore.createAndRunBatchTest(config)
}

// 停止测试（暂时不实现，因为是并行的）
function handleStopTest() {
  // 并行测试无法中途停止
}

// 查看详情
function handleViewDetail(result) {
  selectedResult.value = result
  showDetailModal.value = true
}

// 进入聊天
function handleEnterChat(result) {
  emit('enter-chat', result)
}

// 单个追加
function handleAppendRound(result) {
  appendResults.value = [result]
  showAppendModal.value = true
}

// 批量追加
function handleBatchAppend(results) {
  appendResults.value = results
  showAppendModal.value = true
}

// 发送追加消息
async function handleSendAppend(message) {
  isSendingAppend.value = true
  await batchTestStore.batchAppendRound(appendResults.value, message)
  isSendingAppend.value = false
  showAppendModal.value = false
  appendResults.value = []
}

// 关闭页面
function handleClose() {
  emit('close')
}

// 工具函数
function formatDate(timestamp) {
  return new Date(timestamp).toLocaleString('zh-CN')
}

function truncateText(text, maxLength) {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
</script>

<style scoped>
.batch-test-center {
  width: 95vw;
  max-width: 1400px;
  height: 90vh;
  overflow-y: auto;
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  color: #1F2937;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  padding: 10px 20px;
  background-color: white;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background-color: #F3F4F6;
  border-color: #9CA3AF;
}

.test-config-section,
.test-results-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.test-info {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.info-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 14px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-weight: 500;
  color: #6B7280;
  min-width: 80px;
}

.info-value {
  color: #1F2937;
  flex: 1;
}

.progress-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #E5E7EB;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background-color: #3B82F6;
  transition: width 0.3s;
}

.progress-text {
  text-align: center;
  font-size: 14px;
  color: #6B7280;
}

/* 滚动条样式 */
.batch-test-center::-webkit-scrollbar {
  width: 8px;
}

.batch-test-center::-webkit-scrollbar-track {
  background: #F3F4F6;
}

.batch-test-center::-webkit-scrollbar-thumb {
  background: #D1D5DB;
  border-radius: 4px;
}

.batch-test-center::-webkit-scrollbar-thumb:hover {
  background: #9CA3AF;
}
</style>
