<template>
  <div class="app">
    <div class="app-container">
      <!-- 左侧栏 20% -->
      <div class="sidebar-left">
        <LeftSidebar @open-batch-test="showBatchTest = true" />
      </div>

      <!-- 中间对话区 40% -->
      <div class="chat-area">
        <ChatArea />
      </div>

      <!-- 右侧角色卡片区 40% -->
      <div class="sidebar-right">
        <CharacterCard />
      </div>
    </div>

    <!-- 批量测试弹窗 -->
    <div v-if="showBatchTest" class="batch-test-overlay">
      <BatchTestCenter @close="showBatchTest = false" @enter-chat="handleEnterChatFromTest" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import LeftSidebar from './components/LeftSidebar.vue'
import ChatArea from './components/ChatArea.vue'
import CharacterCard from './components/CharacterCard.vue'
import BatchTestCenter from './components/BatchTest/BatchTestCenter.vue'
import { useUserStore } from './stores/userStore'
import { useChatStore } from './stores/chatStore'
import { useCharacterStore } from './stores/characterStore'
import { useBatchTestStore } from './stores/batchTestStore'

const userStore = useUserStore()
const chatStore = useChatStore()
const characterStore = useCharacterStore()
const batchTestStore = useBatchTestStore()

// 状态
const showBatchTest = ref(false)

// 页面加载时初始化所有数据
onMounted(() => {
  userStore.initialize()
  chatStore.initialize()
  characterStore.initialize()
  batchTestStore.initialize()
})

// 从批量测试进入聊天
function handleEnterChatFromTest(result) {
  // 切换到对应的用户和会话
  userStore.switchUser(result.user_id)
  chatStore.switchSession(result.session_id)

  // 关闭批量测试弹窗
  showBatchTest.value = false
}
</script>

<style>
/* 全局重置样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.app {
  width: 100%;
  height: 100%;
}

.app-container {
  width: 100%;
  height: 100%;
  display: flex;
}

.sidebar-left {
  width: 20%;
  height: 100%;
  border-right: 1px solid #E5E7EB;
  overflow: hidden;
}

.chat-area {
  width: 40%;
  height: 100%;
  border-right: 1px solid #E5E7EB;
  overflow: hidden;
}

.sidebar-right {
  width: 40%;
  height: 100%;
  overflow: hidden;
}

/* 滚动条全局样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #F3F4F6;
}

::-webkit-scrollbar-thumb {
  background: #D1D5DB;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #9CA3AF;
}

/* 批量测试弹窗 */
.batch-test-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.3);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
