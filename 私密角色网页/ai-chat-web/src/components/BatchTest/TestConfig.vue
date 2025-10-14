<template>
  <div class="test-config">
    <h3>测试配置</h3>

    <div class="form-group">
      <label>测试名称（可选）</label>
      <input
        v-model="config.test_name"
        type="text"
        placeholder="例如：角色创建测试-林玉"
      >
    </div>

    <div class="form-group">
      <label>输入内容 <span class="required">*</span></label>
      <textarea
        v-model="config.user_prompt"
        placeholder="输入要测试的角色创建内容..."
        rows="4"
      ></textarea>
    </div>

    <div class="form-group">
      <label>角色图片 <span class="required">*</span></label>
      <div class="avatar-selector">
        <div
          v-for="(avatar, index) in defaultAvatars"
          :key="index"
          class="avatar-option"
          :class="{ selected: config.character_image === avatar }"
          @click="config.character_image = avatar"
        >
          <img :src="avatar" :alt="`头像${index + 1}`">
        </div>
        <div class="custom-url-input">
          <input
            v-model="customImageUrl"
            type="text"
            placeholder="或输入自定义图片URL"
            @input="config.character_image = customImageUrl"
          >
        </div>
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label>请求次数 <span class="required">*</span></label>
        <input
          v-model.number="config.test_count"
          type="number"
          min="1"
          max="20"
          placeholder="10"
        >
      </div>

      <div class="form-group">
        <label>ID策略 <span class="required">*</span></label>
        <div class="radio-group">
          <label class="radio-label">
            <input
              v-model="config.id_strategy"
              type="radio"
              value="same_user"
            >
            <span>同user不同session</span>
          </label>
          <label class="radio-label">
            <input
              v-model="config.id_strategy"
              type="radio"
              value="different_user"
            >
            <span>不同user不同session</span>
          </label>
        </div>
      </div>
    </div>

    <div class="form-actions">
      <button
        class="btn-primary"
        :disabled="!isValid || isRunning"
        @click="handleStart"
      >
        {{ isRunning ? '测试中...' : '开始测试' }}
      </button>
      <button
        v-if="isRunning"
        class="btn-secondary"
        @click="$emit('stop')"
      >
        停止测试
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { DEFAULT_AVATARS } from '../../utils/api'

const props = defineProps({
  isRunning: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['start', 'stop'])

// 配置数据
const config = ref({
  test_name: '',
  user_prompt: '',
  character_image: DEFAULT_AVATARS[0],
  test_count: 10,
  id_strategy: 'same_user'
})

const customImageUrl = ref('')
const defaultAvatars = DEFAULT_AVATARS

// 验证配置是否完整
const isValid = computed(() => {
  return config.value.user_prompt.trim() !== '' &&
         config.value.character_image !== '' &&
         config.value.test_count > 0 &&
         config.value.test_count <= 20
})

// 开始测试
function handleStart() {
  if (isValid.value) {
    emit('start', { ...config.value })
  }
}
</script>

<style scoped>
.test-config {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.test-config h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #1F2937;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.required {
  color: #EF4444;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #3B82F6;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.avatar-selector {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.avatar-option {
  width: 60px;
  height: 60px;
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
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.avatar-option img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.custom-url-input {
  flex: 1;
  min-width: 200px;
}

.custom-url-input input {
  width: 100%;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
}

.radio-label input[type="radio"] {
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
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
