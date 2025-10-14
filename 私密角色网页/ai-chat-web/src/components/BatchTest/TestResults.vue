<template>
  <div class="test-results">
    <div class="results-header">
      <div class="header-left">
        <label class="checkbox-label">
          <input
            v-model="selectAll"
            type="checkbox"
            @change="handleSelectAll"
          >
          <span>全选成功项</span>
        </label>
        <button
          v-if="selectedResults.length > 0"
          class="btn-batch-append"
          @click="$emit('batch-append', selectedResults)"
        >
          批量发送下一轮 ({{ selectedResults.length }})
        </button>
      </div>
      <div class="header-right">
        <span>排序:</span>
        <label class="radio-label">
          <input v-model="sortBy" type="radio" value="status">
          <span>按状态</span>
        </label>
        <label class="radio-label">
          <input v-model="sortBy" type="radio" value="index">
          <span>按序号</span>
        </label>
      </div>
    </div>

    <!-- 成功结果 -->
    <div v-if="sortedSuccessResults.length > 0" class="result-section">
      <h4 class="section-title success">✅ 成功 ({{ sortedSuccessResults.length }})</h4>
      <div class="result-list">
        <div
          v-for="result in sortedSuccessResults"
          :key="result.test_index"
          class="result-item success"
        >
          <div class="result-checkbox">
            <input
              v-model="selectedIndexes"
              type="checkbox"
              :value="result.test_index"
            >
          </div>
          <div class="result-content">
            <div class="result-header-line">
              <span class="result-index">#{{ result.test_index }}</span>
              <span class="result-status">成功</span>
              <span class="result-duration">{{ formatDuration(result.duration) }}</span>
              <span class="result-round">轮次: {{ result.current_round }}</span>
            </div>
            <div class="result-ids">
              <span>User: {{ formatId(result.user_id) }}</span>
              <span>Session: {{ formatId(result.session_id) }}</span>
            </div>
            <div class="result-response">
              最新回复: {{ getLatestResponse(result) }}
            </div>
            <div class="result-actions">
              <button class="btn-detail" @click="$emit('view-detail', result)">
                📊 查看详情
              </button>
              <button class="btn-chat" @click="$emit('enter-chat', result)">
                💬 进入聊天
              </button>
              <button class="btn-append" @click="$emit('append-round', result)">
                ➕ 追加消息
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 失败结果 -->
    <div v-if="sortedFailedResults.length > 0" class="result-section">
      <h4 class="section-title failed">❌ 失败 ({{ sortedFailedResults.length }})</h4>
      <div class="result-list">
        <div
          v-for="result in sortedFailedResults"
          :key="result.test_index"
          class="result-item failed"
        >
          <div class="result-content">
            <div class="result-header-line">
              <span class="result-index">#{{ result.test_index }}</span>
              <span class="result-status">失败</span>
              <span class="result-duration">{{ formatDuration(result.duration) }}</span>
            </div>
            <div class="result-error">
              错误: {{ result.error?.message || '未知错误' }}
              <span v-if="result.error?.code">({{ result.error.code }})</span>
            </div>
            <div v-if="result.error?.details" class="result-error-details">
              {{ result.error.details.join('; ') }}
            </div>
            <div class="result-actions">
              <button class="btn-detail" @click="$emit('view-detail', result)">
                📋 查看详情
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="results.length === 0" class="empty-state">
      暂无测试结果
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  results: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['view-detail', 'enter-chat', 'append-round', 'batch-append'])

const sortBy = ref('status')
const selectAll = ref(false)
const selectedIndexes = ref([])

// 成功和失败的结果
const successResults = computed(() => {
  return props.results.filter(r => r.status === 'success')
})

const failedResults = computed(() => {
  return props.results.filter(r => r.status === 'failed')
})

// 排序后的结果
const sortedSuccessResults = computed(() => {
  if (sortBy.value === 'index') {
    return [...successResults.value].sort((a, b) => a.test_index - b.test_index)
  }
  return successResults.value
})

const sortedFailedResults = computed(() => {
  if (sortBy.value === 'index') {
    return [...failedResults.value].sort((a, b) => a.test_index - b.test_index)
  }
  return failedResults.value
})

// 选中的结果
const selectedResults = computed(() => {
  return props.results.filter(r => selectedIndexes.value.includes(r.test_index))
})

// 全选/取消全选
function handleSelectAll() {
  if (selectAll.value) {
    selectedIndexes.value = successResults.value.map(r => r.test_index)
  } else {
    selectedIndexes.value = []
  }
}

// 格式化ID
function formatId(id) {
  if (!id || id.length <= 16) return id
  return `${id.slice(0, 8)}...${id.slice(-8)}`
}

// 格式化时长
function formatDuration(ms) {
  if (ms === null || ms === undefined) return '-'
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(2)}s`
}

// 获取最新回复
function getLatestResponse(result) {
  if (!result.rounds || result.rounds.length === 0) return ''
  const latestRound = result.rounds[result.rounds.length - 1]
  const response = latestRound.response?.response || ''
  return response.length > 50 ? response.substring(0, 50) + '...' : response
}
</script>

<style scoped>
.test-results {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #E5E7EB;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #6B7280;
}

.checkbox-label,
.radio-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-batch-append {
  padding: 8px 16px;
  background-color: #3B82F6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-batch-append:hover {
  background-color: #2563EB;
}

.result-section {
  margin-bottom: 24px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
}

.section-title.success {
  color: #059669;
}

.section-title.failed {
  color: #DC2626;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #E5E7EB;
  transition: all 0.2s;
}

.result-item:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.result-item.success {
  background-color: #F0FDF4;
  border-color: #BBF7D0;
}

.result-item.failed {
  background-color: #FEF2F2;
  border-color: #FECACA;
}

.result-checkbox {
  padding-top: 2px;
}

.result-content {
  flex: 1;
}

.result-header-line {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 14px;
}

.result-index {
  font-weight: 600;
  color: #1F2937;
}

.result-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.result-item.success .result-status {
  background-color: #D1FAE5;
  color: #059669;
}

.result-item.failed .result-status {
  background-color: #FEE2E2;
  color: #DC2626;
}

.result-duration,
.result-round {
  font-size: 13px;
  color: #6B7280;
}

.result-ids {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
  font-size: 12px;
  font-family: 'Monaco', monospace;
  color: #6B7280;
}

.result-response {
  margin-bottom: 12px;
  font-size: 13px;
  color: #374151;
  line-height: 1.5;
}

.result-error {
  margin-bottom: 8px;
  font-size: 13px;
  color: #DC2626;
}

.result-error-details {
  margin-bottom: 12px;
  padding: 8px;
  background-color: #FEE2E2;
  border-radius: 4px;
  font-size: 12px;
  color: #991B1B;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.result-actions button {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-detail {
  background-color: #F3F4F6;
  color: #374151;
}

.btn-detail:hover {
  background-color: #E5E7EB;
}

.btn-chat {
  background-color: #DBEAFE;
  color: #1E40AF;
}

.btn-chat:hover {
  background-color: #BFDBFE;
}

.btn-append {
  background-color: #D1FAE5;
  color: #065F46;
}

.btn-append:hover {
  background-color: #A7F3D0;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #9CA3AF;
  font-size: 14px;
}
</style>
