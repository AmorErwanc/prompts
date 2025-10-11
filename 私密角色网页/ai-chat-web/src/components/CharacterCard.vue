<template>
  <div class="character-card">
    <div v-if="!character" class="empty-card">
      <div class="skeleton">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line short"></div>
        <div class="skeleton-line"></div>
      </div>
      <p class="hint">选择对话后查看角色信息</p>
    </div>

    <div v-else class="card-content">
      <!-- 角色头像 -->
      <div class="avatar-section">
        <img
          v-if="character.character_image"
          :src="character.character_image"
          alt="角色头像"
          class="character-avatar"
        >
        <div v-else class="placeholder-avatar">?</div>
      </div>

      <!-- 角色基本信息 -->
      <div class="info-section">
        <div class="info-item">
          <label>姓名</label>
          <div class="info-value">{{ profile.name || '暂无' }}</div>
        </div>

        <div class="info-item">
          <label>性别</label>
          <div class="info-value">{{ profile.gender || '暂无' }}</div>
        </div>

        <div class="info-item">
          <label>身份</label>
          <div class="info-value">{{ profile.identity || '暂无' }}</div>
        </div>

        <!-- 性格特征 -->
        <div class="info-item">
          <label>性格特征</label>
          <div v-if="Array.isArray(profile.personality_traits) && profile.personality_traits.length > 0" class="tags">
            <span v-for="(trait, index) in profile.personality_traits" :key="index" class="tag">
              {{ trait }}
            </span>
          </div>
          <div v-else-if="typeof profile.personality_traits === 'string'" class="info-value multiline">
            {{ profile.personality_traits }}
          </div>
          <div v-else class="info-value">暂无</div>
        </div>

        <!-- 说话风格 -->
        <div class="info-item">
          <label>说话风格</label>
          <div class="info-value multiline">{{ profile.speaking_style || '暂无' }}</div>
        </div>

        <!-- 背景故事 -->
        <div class="info-item">
          <label>背景故事</label>
          <div class="info-value multiline">{{ profile.background_story || '暂无' }}</div>
        </div>

        <!-- 与用户关系 -->
        <div class="info-item">
          <label>与你的关系</label>
          <div class="info-value multiline">{{ profile.relationship_with_user || '暂无' }}</div>
        </div>

        <!-- 额外信息 -->
        <div v-if="profile.additional_info" class="info-item">
          <label>额外信息</label>
          <div class="info-value multiline">{{ profile.additional_info }}</div>
        </div>

        <!-- 创建状态 -->
        <div class="status-badge" :class="{ completed: character.draft }">
          {{ character.draft ? '✓ 已完成' : '⏳ 创建中' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useChatStore } from '../stores/chatStore'
import { useCharacterStore } from '../stores/characterStore'

const chatStore = useChatStore()
const characterStore = useCharacterStore()

// 计算属性
const currentSession = computed(() => chatStore.currentSession)

const character = computed(() => {
  if (!currentSession.value) return null
  return characterStore.getCharacter(currentSession.value.cartoon_id)
})

const profile = computed(() => {
  return character.value?.character_profile || {}
})
</script>

<style scoped>
.character-card {
  width: 100%;
  height: 100%;
  background-color: #F8F9FA;
  overflow-y: auto;
}

/* 空状态 */
.empty-card {
  padding: 40px 20px;
  text-align: center;
}

.skeleton {
  max-width: 300px;
  margin: 0 auto 24px;
}

.skeleton-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(90deg, #E5E7EB 25%, #F3F4F6 50%, #E5E7EB 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  margin: 0 auto 20px;
}

.skeleton-line {
  height: 16px;
  background: linear-gradient(90deg, #E5E7EB 25%, #F3F4F6 50%, #E5E7EB 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 12px;
}

.skeleton-line.short {
  width: 60%;
  margin: 0 auto 12px;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.hint {
  color: #6B7280;
  font-size: 14px;
  margin: 0;
}

/* 卡片内容 */
.card-content {
  padding: 24px;
}

.avatar-section {
  text-align: center;
  margin-bottom: 24px;
}

.character-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.placeholder-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background-color: #E5E7EB;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: #9CA3AF;
  margin: 0 auto;
}

/* 信息项 */
.info-section {
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.info-item {
  margin-bottom: 20px;
}

.info-item:last-of-type {
  margin-bottom: 0;
}

.info-item label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.info-value {
  font-size: 14px;
  color: #1F2937;
  line-height: 1.6;
}

.info-value.multiline {
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 标签 */
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  display: inline-block;
  padding: 6px 12px;
  background-color: #EEF2FF;
  color: #4F46E5;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}

/* 状态徽章 */
.status-badge {
  margin-top: 20px;
  padding: 10px;
  border-radius: 8px;
  text-align: center;
  font-size: 13px;
  font-weight: 600;
  background-color: #FEF3C7;
  color: #D97706;
}

.status-badge.completed {
  background-color: #D1FAE5;
  color: #059669;
}

/* 滚动条样式 */
.character-card::-webkit-scrollbar {
  width: 6px;
}

.character-card::-webkit-scrollbar-track {
  background: transparent;
}

.character-card::-webkit-scrollbar-thumb {
  background: #D1D5DB;
  border-radius: 3px;
}

.character-card::-webkit-scrollbar-thumb:hover {
  background: #9CA3AF;
}
</style>
