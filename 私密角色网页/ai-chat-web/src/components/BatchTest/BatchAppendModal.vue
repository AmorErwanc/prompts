<template>
  <div v-if="visible" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>批量发送下一轮</h3>
        <button class="close-btn" @click="handleClose">×</button>
      </div>

      <div class="modal-body">
        <div class="selected-info">
          已选择: <strong>{{ results.length }}</strong> 个测试
        </div>

        <div class="selected-list">
          <div
            v-for="result in results"
            :key="result.test_index"
            class="selected-item"
          >
            <span class="item-index">#{{ result.test_index }}</span>
            <span class="item-session">Session: {{ formatId(result.session_id) }}</span>
            <span class="item-round">轮次: {{ result.current_round }} → {{ result.current_round + 1 }}</span>
          </div>
        </div>

        <div class="message-input-section">
          <label>输入消息内容</label>
          <textarea
            v-model="message"
            placeholder="输入要发送的消息..."
            rows="4"
          ></textarea>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="handleClose">取消</button>
        <button
          class="btn-primary"
          :disabled="!message.trim() || isSending"
          @click="handleSend"
        >
          {{ isSending ? '发送中...' : `发送 (${results.length}个测试)` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  results: {
    type: Array,
    default: () => []
  },
  isSending: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'send'])

const message = ref('')

function handleClose() {
  message.value = ''
  emit('close')
}

function handleSend() {
  if (message.value.trim()) {
    emit('send', message.value.trim())
    message.value = ''
  }
}

function formatId(id) {
  if (!id || id.length <= 16) return id
  return `${id.slice(0, 8)}...${id.slice(-8)}`
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
  max-width: 600px;
  max-height: 80vh;
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

.selected-info {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #EFF6FF;
  border: 1px solid #BFDBFE;
  border-radius: 8px;
  font-size: 14px;
  color: #1E40AF;
}

.selected-list {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 20px;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
}

.selected-item {
  padding: 12px;
  border-bottom: 1px solid #E5E7EB;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
}

.selected-item:last-child {
  border-bottom: none;
}

.item-index {
  font-weight: 600;
  color: #1F2937;
}

.item-session {
  flex: 1;
  font-family: 'Monaco', monospace;
  color: #6B7280;
}

.item-round {
  color: #3B82F6;
  font-weight: 500;
}

.message-input-section {
  margin-bottom: 0;
}

.message-input-section label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.message-input-section textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
}

.message-input-section textarea:focus {
  border-color: #3B82F6;
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

.btn-primary:hover:not(:disabled) {
  background-color: #2563EB;
}

.btn-primary:disabled {
  background-color: #9CA3AF;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #F3F4F6;
  color: #374151;
}

.btn-secondary:hover {
  background-color: #E5E7EB;
}
</style>
