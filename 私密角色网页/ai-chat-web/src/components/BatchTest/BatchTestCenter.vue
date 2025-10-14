<template>
  <div class="batch-test-center">
    <div class="page-header">
      <h2>批量测试中心</h2>
      <div class="header-actions">
        <button v-if="currentView !== 'list'" class="btn-secondary" @click="backToList">
          ← 返回测试列表
        </button>
        <button class="btn-primary" @click="createNewTest">
          + 新建测试
        </button>
        <button class="btn-secondary" @click="handleClose">
          关闭
        </button>
      </div>
    </div>

    <!-- 测试列表 -->
    <div v-if="currentView === 'list'" class="test-list-section">
      <div v-if="batchHistory.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <div class="empty-text">还没有批量测试记录</div>
        <button class="btn-primary" @click="createNewTest">创建第一个测试</button>
      </div>
      <div v-else class="history-list">
        <div
          v-for="item in batchHistory"
          :key="item.batch_id"
          class="history-item"
          @click="loadTest(item.batch_id)"
        >
          <div class="history-header">
            <h3 class="history-title">{{ item.test_name }}</h3>
            <span class="history-date">{{ formatDate(item.created_at) }}</span>
          </div>
          <div class="history-stats">
            <span class="stat-item success">✅ 成功: {{ item.statistics.success }}</span>
            <span class="stat-item failed">❌ 失败: {{ item.statistics.failed }}</span>
            <span class="stat-item total">📊 总计: {{ item.statistics.total }}</span>
            <span class="stat-item rate">
              成功率: {{ (item.statistics.success_rate * 100).toFixed(1) }}%
            </span>
          </div>
          <div class="history-actions">
            <button class="btn-view" @click.stop="loadTest(item.batch_id)">查看详情</button>
            <button class="btn-delete" @click.stop="confirmDelete(item.batch_id)">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建测试配置 -->
    <div v-if="currentView === 'config'" class="test-config-section">
      <TestConfig
        :is-running="isRunning"
        @start="handleStartTest"
        @stop="handleStopTest"
      />
    </div>

    <!-- 测试结果展示 -->
    <div v-if="currentView === 'results' && currentBatch" class="test-results-section">
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
const currentView = ref('list') // 'list' | 'config' | 'results'
const showDetailModal = ref(false)
const showAppendModal = ref(false)
const selectedResult = ref({})
const appendResults = ref([])
const isSendingAppend = ref(false)

// 计算属性
const currentBatch = computed(() => batchTestStore.currentBatch)
const isRunning = computed(() => batchTestStore.isRunning)
const batchHistory = computed(() => batchTestStore.batchHistory)

const progressPercent = computed(() => {
  if (!currentBatch.value) return 0
  const { success, failed, total } = currentBatch.value.statistics
  return ((success + failed) / total) * 100
})

// 初始化
onMounted(() => {
  batchTestStore.initialize()
  // 根据是否有当前批次决定初始视图
  if (currentBatch.value) {
    currentView.value = 'results'
  } else if (batchHistory.value.length > 0) {
    currentView.value = 'list'
  } else {
    currentView.value = 'config'
  }
})

// 创建新测试
function createNewTest() {
  currentView.value = 'config'
}

// 返回测试列表
function backToList() {
  currentView.value = 'list'
}

// 加载测试
function loadTest(batchId) {
  batchTestStore.loadBatchTest(batchId)
  currentView.value = 'results'
}

// 确认删除
function confirmDelete(batchId) {
  if (confirm('确定要删除这个测试吗？此操作无法撤销。')) {
    batchTestStore.deleteBatchTest(batchId)
  }
}

// 开始测试
async function handleStartTest(config) {
  currentView.value = 'results'
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

/* 按钮样式 */
.btn-primary {
  padding: 10px 20px;
  background-color: #3B82F6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background-color: #2563EB;
}

/* 测试列表样式 */
.test-list-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #9CA3AF;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  margin-bottom: 24px;
  color: #6B7280;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-color: #3B82F6;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1F2937;
}

.history-date {
  font-size: 13px;
  color: #9CA3AF;
}

.history-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
  padding: 12px 0;
  border-top: 1px solid #F3F4F6;
  border-bottom: 1px solid #F3F4F6;
}

.stat-item {
  font-size: 14px;
  font-weight: 500;
}

.stat-item.success {
  color: #059669;
}

.stat-item.failed {
  color: #DC2626;
}

.stat-item.total {
  color: #6B7280;
}

.stat-item.rate {
  color: #3B82F6;
}

.history-actions {
  display: flex;
  gap: 8px;
}

.btn-view,
.btn-delete {
  padding: 6px 16px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-view {
  background-color: #DBEAFE;
  color: #1E40AF;
}

.btn-view:hover {
  background-color: #BFDBFE;
}

.btn-delete {
  background-color: #FEE2E2;
  color: #991B1B;
}

.btn-delete:hover {
  background-color: #FECACA;
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
