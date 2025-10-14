<template>
  <div v-if="visible" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>测试详情 #{{ result.test_index }}</h3>
        <button class="close-btn" @click="handleClose">×</button>
      </div>

      <div class="modal-body">
        <!-- 基本信息 -->
        <section class="detail-section">
          <h4>基本信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">User ID:</span>
              <span class="info-value" @click="copyText(result.user_id)">
                {{ result.user_id }}
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">Session ID:</span>
              <span class="info-value" @click="copyText(result.session_id)">
                {{ result.session_id }}
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">Cartoon ID:</span>
              <span class="info-value" @click="copyText(result.cartoon_id)">
                {{ result.cartoon_id }}
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">状态:</span>
              <span class="status-badge" :class="result.status">
                {{ result.status === 'success' ? '✅ 成功' : '❌ 失败' }}
              </span>
            </div>
            <div v-if="result.duration" class="info-item">
              <span class="info-label">耗时:</span>
              <span class="info-value">{{ formatDuration(result.duration) }}</span>
            </div>
          </div>
        </section>

        <!-- 对话轮次 -->
        <section v-if="result.rounds && result.rounds.length > 0" class="detail-section">
          <h4>对话轮次 (共{{ result.rounds.length }}轮)</h4>
          <div class="rounds-list">
            <div
              v-for="round in result.rounds"
              :key="round.round"
              class="round-item"
            >
              <div class="round-header">
                <span class="round-number">第{{ round.round }}轮</span>
                <span class="round-duration">{{ formatDuration(round.duration) }}</span>
              </div>
              <div class="round-content">
                <div class="message-block">
                  <div class="message-label">请求:</div>
                  <div class="message-text">{{ round.request.user_prompt }}</div>
                </div>
                <div class="message-block">
                  <div class="message-label">回复:</div>
                  <div class="message-text">{{ round.response.response }}</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 错误信息 -->
        <section v-if="result.error" class="detail-section error-section">
          <h4>错误信息</h4>
          <div class="error-content">
            <div><strong>消息:</strong> {{ result.error.message }}</div>
            <div v-if="result.error.code"><strong>代码:</strong> {{ result.error.code }}</div>
            <div v-if="result.error.details">
              <strong>详情:</strong>
              <ul>
                <li v-for="(detail, index) in result.error.details" :key="index">
                  {{ detail }}
                </li>
              </ul>
            </div>
          </div>
        </section>

        <!-- 原始数据 -->
        <section v-if="result.rounds && result.rounds.length > 0" class="detail-section">
          <h4>原始数据 (JSON)</h4>
          <div class="json-viewer">
            <pre>{{ formatJSON(result.rounds[result.rounds.length - 1].response) }}</pre>
          </div>
          <button class="btn-copy-json" @click="copyJSON">
            复制JSON
          </button>
        </section>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="handleClose">关闭</button>
        <button
          v-if="result.status === 'success'"
          class="btn-primary"
          @click="handleEnterChat"
        >
          进入聊天
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  result: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['close', 'enter-chat'])

function handleClose() {
  emit('close')
}

function handleEnterChat() {
  emit('enter-chat', props.result)
}

function formatDuration(ms) {
  if (!ms) return '-'
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(2)}s`
}

function formatJSON(obj) {
  return JSON.stringify(obj, null, 2)
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
    alert(`已复制: ${text}`)
  } catch (error) {
    console.error('复制失败:', error)
  }
}

async function copyJSON() {
  if (props.result.rounds && props.result.rounds.length > 0) {
    const json = formatJSON(props.result.rounds[props.result.rounds.length - 1].response)
    await copyText(json)
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #E5E7EB;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1F2937;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  font-size: 28px;
  color: #9CA3AF;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #F3F4F6;
  color: #1F2937;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #374151;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.info-label {
  color: #6B7280;
  font-weight: 500;
}

.info-value {
  color: #1F2937;
  font-family: 'Monaco', monospace;
  font-size: 13px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.info-value:hover {
  background-color: #F3F4F6;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
}

.status-badge.success {
  background-color: #D1FAE5;
  color: #059669;
}

.status-badge.failed {
  background-color: #FEE2E2;
  color: #DC2626;
}

.rounds-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.round-item {
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  padding: 16px;
  background-color: #F9FAFB;
}

.round-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #E5E7EB;
}

.round-number {
  font-weight: 600;
  color: #1F2937;
}

.round-duration {
  font-size: 13px;
  color: #6B7280;
}

.round-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-block {
  font-size: 14px;
}

.message-label {
  font-weight: 500;
  color: #6B7280;
  margin-bottom: 4px;
}

.message-text {
  color: #1F2937;
  line-height: 1.6;
  white-space: pre-wrap;
}

.error-section {
  background-color: #FEF2F2;
  border: 1px solid #FEC ACA;
  border-radius: 8px;
  padding: 16px;
}

.error-content {
  font-size: 14px;
  color: #991B1B;
}

.error-content ul {
  margin-top: 8px;
  padding-left: 20px;
}

.json-viewer {
  background-color: #1F2937;
  color: #F9FAFB;
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  font-family: 'Monaco', monospace;
  font-size: 12px;
  line-height: 1.5;
  max-height: 300px;
  overflow-y: auto;
}

.json-viewer pre {
  margin: 0;
}

.btn-copy-json {
  margin-top: 8px;
  padding: 6px 12px;
  background-color: #F3F4F6;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-copy-json:hover {
  background-color: #E5E7EB;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #E5E7EB;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #3B82F6;
  color: white;
}

.btn-primary:hover {
  background-color: #2563EB;
}

.btn-secondary {
  background-color: #F3F4F6;
  color: #374151;
}

.btn-secondary:hover {
  background-color: #E5E7EB;
}
</style>
