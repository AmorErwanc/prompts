<template>
  <div class="chat-area">
    <!-- ID信息栏 -->
    <div v-if="currentSession" class="id-info-bar">
      <div class="id-item">
        <span class="id-label">User ID:</span>
        <span class="id-value" @click="copyToClipboard(currentSession.user_id)" :title="currentSession.user_id">
          {{ formatId(currentSession.user_id) }}
        </span>
      </div>
      <div class="id-item">
        <span class="id-label">Session ID:</span>
        <span class="id-value" @click="copyToClipboard(currentSession.session_id)" :title="currentSession.session_id">
          {{ formatId(currentSession.session_id) }}
        </span>
      </div>
    </div>

    <!-- 消息列表 -->
    <div
      class="message-list"
      :style="{ backgroundImage: showBackground ? `url(${characterImage})` : 'none' }"
      ref="messageListRef"
    >
      <div v-if="!currentSession" class="empty-state">
        <p>请选择或创建一个对话</p>
      </div>

      <div v-else class="messages">
        <div
          v-for="message in currentMessages"
          :key="message.dialogue_id"
        >
          <!-- 普通消息气泡 -->
          <div class="message-wrapper" :class="message.role">
            <!-- AI消息 -->
            <div v-if="message.role === 'assistant'" class="message-content">
              <div class="bubble assistant-bubble">
                {{ message.content }}
              </div>
            </div>

            <!-- 用户消息 -->
            <div v-else class="message-content">
              <div class="bubble user-bubble">
                {{ message.content }}
              </div>
            </div>
          </div>

          <!-- draft=true时显示"开始聊天"按钮（独立的容器） -->
          <div v-if="message.draft && message.role === 'assistant'" class="message-wrapper assistant">
            <div class="chat-start-card">
              <div class="card-icon">✓</div>
              <div class="card-title">角色创建完成！</div>
              <button class="start-chat-btn" @click="handleStartChat">
                开始聊天
              </button>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="isLoading" class="message-wrapper assistant">
          <div class="message-content">
            <div class="bubble assistant-bubble loading">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div v-if="currentSession" class="input-area">
      <textarea
        v-model="inputText"
        placeholder="输入消息..."
        @keydown.enter.exact.prevent="handleSend"
        @keydown.enter.shift.exact="inputText += '\n'"
        rows="1"
        ref="textareaRef"
      ></textarea>
      <button
        class="send-btn"
        :disabled="!inputText.trim() || isLoading"
        @click="handleSend"
      >
        发送
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useChatStore } from '../stores/chatStore'
import { useCharacterStore } from '../stores/characterStore'

const chatStore = useChatStore()
const characterStore = useCharacterStore()

// 状态
const inputText = ref('')
const isLoading = ref(false)
const messageListRef = ref(null)
const textareaRef = ref(null)

// 计算属性
const currentSession = computed(() => chatStore.currentSession)
const currentMessages = computed(() => chatStore.currentMessages)

const character = computed(() => {
  if (!currentSession.value) return null
  return characterStore.getCharacter(currentSession.value.cartoon_id)
})

const characterImage = computed(() => {
  return character.value?.character_image || null
})

// 判断是否显示背景图（当有draft=true的消息时）
const showBackground = computed(() => {
  return currentMessages.value.some(msg => msg.draft && msg.role === 'assistant')
})

// 方法
async function handleSend() {
  if (!inputText.value.trim() || isLoading.value) return

  const message = inputText.value.trim()
  inputText.value = ''

  // 重置textarea高度
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }

  isLoading.value = true

  try {
    await chatStore.sendMessage(message)
  } finally {
    isLoading.value = false
    // 滚动到底部
    await nextTick()
    scrollToBottom()
  }
}

function handleStartChat() {
  alert('开始聊天功能暂未实现')
}

function scrollToBottom() {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

// 格式化ID显示（显示前8位...后8位）
function formatId(id) {
  if (!id) return ''
  if (id.length <= 16) return id
  return `${id.slice(0, 8)}...${id.slice(-8)}`
}

// 复制到剪贴板
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text)
    alert(`已复制: ${text}`)
  } catch (error) {
    console.error('复制失败:', error)
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    try {
      document.execCommand('copy')
      alert(`已复制: ${text}`)
    } catch (err) {
      alert('复制失败，请手动复制')
    }
    document.body.removeChild(textarea)
  }
}

// 监听消息变化，自动滚动到底部
watch(currentMessages, async () => {
  await nextTick()
  scrollToBottom()
}, { deep: true })

// 监听textarea输入，自动调整高度
watch(inputText, () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = textareaRef.value.scrollHeight + 'px'
  }
})
</script>

<style scoped>
.chat-area {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: white;
}

/* ID信息栏 */
.id-info-bar {
  padding: 12px 20px;
  background-color: #F8F9FA;
  border-bottom: 1px solid #E5E7EB;
  display: flex;
  gap: 24px;
  font-size: 12px;
  flex-shrink: 0;
}

.id-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.id-label {
  color: #6B7280;
  font-weight: 500;
}

.id-value {
  color: #1F2937;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  background-color: white;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #E5E7EB;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.id-value:hover {
  background-color: #3B82F6;
  color: white;
  border-color: #3B82F6;
  transform: translateY(-1px);
}

.id-value:active {
  transform: translateY(0);
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  position: relative;
}

/* 有背景图时添加半透明遮罩 */
.message-list[style*="background-image"] {
  background-blend-mode: overlay;
  background-color: rgba(255, 255, 255, 0.95);
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6B7280;
  font-size: 16px;
}

.messages {
  max-width: 800px;
  margin: 0 auto;
}

.message-wrapper {
  margin-bottom: 20px;
}

.message-wrapper.assistant {
  text-align: left;
}

.message-wrapper.user {
  text-align: right;
}

.message-content {
  display: inline-block;
  max-width: 70%;
}


.bubble {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.5;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.assistant-bubble {
  background-color: white;
  border: 1px solid #E5E7EB;
  color: #1F2937;
}

.user-bubble {
  background-color: #3B82F6;
  color: white;
}

/* 加载动画 */
.bubble.loading {
  display: flex;
  gap: 6px;
  padding: 16px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #9CA3AF;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 开始聊天卡片 */
.chat-start-card {
  background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
  border: 1px solid #BFDBFE;
  padding: 32px 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  max-width: 400px;
  margin: 0 auto;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #3B82F6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E40AF;
  margin: 0;
}

.start-chat-btn {
  padding: 10px 28px;
  border: none;
  border-radius: 8px;
  background-color: #3B82F6;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.start-chat-btn:hover {
  background-color: #2563EB;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.start-chat-btn:active {
  transform: translateY(0);
}

/* 输入框区域 */
.input-area {
  padding: 16px 20px;
  border-top: 1px solid #E5E7EB;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

textarea {
  flex: 1;
  min-height: 40px;
  max-height: 120px;
  padding: 10px 12px;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
}

textarea:focus {
  border-color: #3B82F6;
}

.send-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  background-color: #3B82F6;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  background-color: #2563EB;
}

.send-btn:disabled {
  background-color: #9CA3AF;
  cursor: not-allowed;
}

/* 滚动条样式 */
.message-list::-webkit-scrollbar {
  width: 6px;
}

.message-list::-webkit-scrollbar-track {
  background: transparent;
}

.message-list::-webkit-scrollbar-thumb {
  background: #D1D5DB;
  border-radius: 3px;
}

.message-list::-webkit-scrollbar-thumb:hover {
  background: #9CA3AF;
}
</style>
