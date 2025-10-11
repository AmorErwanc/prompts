<template>
  <div class="left-sidebar">
    <!-- 用户管理部分 -->
    <div class="user-section">
      <div class="section-header">
        <h3>用户</h3>
        <button class="add-btn" @click="handleCreateUser" title="新建用户">+</button>
      </div>
      <div class="user-list">
        <div
          v-for="user in users"
          :key="user.user_id"
          class="user-item"
          :class="{ active: user.user_id === currentUserId }"
          @click="handleSwitchUser(user.user_id)"
        >
          <span class="user-name">{{ user.username }}</span>
          <span class="user-sessions-count">({{ user.sessions.length }})</span>
        </div>
      </div>
    </div>

    <!-- 分割线 -->
    <div class="divider"></div>

    <!-- 会话管理部分 -->
    <div class="session-section">
      <div class="section-header">
        <h3>对话</h3>
        <button class="add-btn" @click="showImageSelector = true" title="新建对话">+</button>
      </div>
      <div class="session-list">
        <div
          v-for="session in currentUserSessions"
          :key="session.session_id"
          class="session-item"
          :class="{ active: session.session_id === currentSessionId }"
          @click="handleSwitchSession(session.session_id)"
        >
          <span class="session-name">{{ session.session_name }}</span>
          <button class="delete-btn" @click.stop="handleDeleteSession(session.session_id)">×</button>
        </div>
        <div v-if="currentUserSessions.length === 0" class="empty-hint">
          点击 + 创建新对话
        </div>
      </div>
    </div>

    <!-- 图片选择器弹窗 -->
    <div v-if="showImageSelector" class="modal-overlay" @click="showImageSelector = false">
      <div class="modal-content" @click.stop>
        <h3>选择角色形象</h3>
        <div class="avatar-grid">
          <div
            v-for="(avatar, index) in defaultAvatars"
            :key="index"
            class="avatar-option"
            :class="{ selected: selectedAvatar === avatar }"
            @click="selectedAvatar = avatar"
          >
            <img :src="avatar" :alt="`头像${index + 1}`">
          </div>
        </div>
        <div class="custom-url">
          <input
            v-model="customAvatarUrl"
            type="text"
            placeholder="或输入自定义图片URL"
            @input="selectedAvatar = customAvatarUrl"
          >
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showImageSelector = false">取消</button>
          <button class="confirm-btn" @click="handleCreateSession">确认</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../stores/userStore'
import { useChatStore } from '../stores/chatStore'
import { useCharacterStore } from '../stores/characterStore'
import { generateCartoonId } from '../utils/idGenerator'
import { DEFAULT_AVATARS } from '../utils/api'

const userStore = useUserStore()
const chatStore = useChatStore()
const characterStore = useCharacterStore()

// 状态
const showImageSelector = ref(false)
const selectedAvatar = ref(DEFAULT_AVATARS[0])
const customAvatarUrl = ref('')
const defaultAvatars = DEFAULT_AVATARS

// 计算属性
const users = computed(() => userStore.users)
const currentUserId = computed(() => userStore.currentUserId)
const currentUserSessions = computed(() => {
  return chatStore.getUserSessions(currentUserId.value)
})
const currentSessionId = computed(() => chatStore.currentSessionId)

// 方法
function handleCreateUser() {
  const username = prompt('请输入用户名:', '新用户')
  if (username) {
    userStore.createUser(username)
  }
}

function handleSwitchUser(userId) {
  userStore.switchUser(userId)
  // 切换到该用户的第一个会话，如果有的话
  const userSessions = chatStore.getUserSessions(userId)
  if (userSessions.length > 0) {
    chatStore.switchSession(userSessions[0].session_id)
  } else {
    chatStore.currentSessionId = null
  }
}

function handleCreateSession() {
  if (!currentUserId.value) {
    alert('请先选择用户')
    return
  }

  const cartoonId = generateCartoonId()
  const avatarUrl = customAvatarUrl.value || selectedAvatar.value

  // 创建角色
  characterStore.createCharacter(cartoonId, avatarUrl)

  // 创建会话
  chatStore.createSession(currentUserId.value, cartoonId, '新对话')

  // 关闭弹窗并重置
  showImageSelector.value = false
  selectedAvatar.value = DEFAULT_AVATARS[0]
  customAvatarUrl.value = ''
}

function handleSwitchSession(sessionId) {
  chatStore.switchSession(sessionId)
}

function handleDeleteSession(sessionId) {
  if (confirm('确定要删除这个对话吗？')) {
    chatStore.deleteSession(sessionId)
  }
}
</script>

<style scoped>
.left-sidebar {
  width: 100%;
  height: 100%;
  background-color: #F8F9FA;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.user-section {
  flex: 0.35;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.session-section {
  flex: 0.65;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.section-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #E5E7EB;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1F2937;
}

.add-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background-color: #3B82F6;
  color: white;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.add-btn:hover {
  background-color: #2563EB;
}

.user-list,
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.user-item,
.session-item {
  padding: 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-item:hover,
.session-item:hover {
  background-color: #E5E7EB;
}

.user-item.active,
.session-item.active {
  background-color: #3B82F6;
  color: white;
}

.user-name,
.session-name {
  font-size: 14px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-sessions-count {
  font-size: 12px;
  color: #6B7280;
  margin-left: 8px;
}

.user-item.active .user-sessions-count {
  color: rgba(255, 255, 255, 0.8);
}

.delete-btn {
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 4px;
  background-color: transparent;
  color: #6B7280;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  margin-left: 8px;
}

.delete-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.session-item.active .delete-btn {
  color: white;
}

.session-item.active .delete-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.divider {
  height: 1px;
  background-color: #E5E7EB;
  margin: 0 16px;
}

.empty-hint {
  padding: 32px 16px;
  text-align: center;
  color: #6B7280;
  font-size: 14px;
}

/* 弹窗样式 */
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
  padding: 24px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-content h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #1F2937;
}

.avatar-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.avatar-option {
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 3px solid transparent;
  transition: all 0.2s;
}

.avatar-option:hover {
  border-color: #3B82F6;
  transform: scale(1.05);
}

.avatar-option.selected {
  border-color: #3B82F6;
}

.avatar-option img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.custom-url input {
  width: 100%;
  padding: 10px;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.custom-url input:focus {
  border-color: #3B82F6;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.cancel-btn,
.confirm-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background-color: #F3F4F6;
  color: #1F2937;
}

.cancel-btn:hover {
  background-color: #E5E7EB;
}

.confirm-btn {
  background-color: #3B82F6;
  color: white;
}

.confirm-btn:hover {
  background-color: #2563EB;
}
</style>
