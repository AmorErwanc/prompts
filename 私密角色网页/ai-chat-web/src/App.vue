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
  console.log('进入聊天 - result:', result)
  console.log('当前用户列表:', userStore.users)
  console.log('当前会话列表:', chatStore.sessions)

  // 检查用户是否存在，不存在则创建
  if (!userStore.users.find(u => u.user_id === result.user_id)) {
    const userName = `测试用户-${result.user_id.slice(0, 8)}`
    userStore.users.push({
      user_id: result.user_id,
      username: userName,  // 注意是 username 不是 user_name
      avatar: null,
      sessions: [result.session_id],  // 注意是 sessions 不是 session_ids
      created_at: Date.now()
    })
    userStore.saveToStorage()
  } else {
    // 用户存在，添加会话ID
    userStore.addSessionToUser(result.user_id, result.session_id)
  }

  // 检查会话是否存在，不存在则创建
  if (!chatStore.sessions[result.session_id]) {
    const sessionName = `测试会话-${result.session_id.slice(0, 8)}`

    // 从测试结果中恢复所有消息
    const messages = []
    result.rounds.forEach(round => {
      // 用户消息
      messages.push({
        dialogue_id: round.dialogue_id,
        role: 'user',
        content: round.request.user_prompt,
        timestamp: round.request.timestamp
      })

      // AI回复消息
      messages.push({
        dialogue_id: round.dialogue_id,
        role: 'assistant',
        content: round.response.response,
        character_profile: round.response.character_profile,
        draft: round.response.draft,
        timestamp: round.timestamp
      })
    })

    chatStore.sessions[result.session_id] = {
      session_id: result.session_id,
      user_id: result.user_id,
      cartoon_id: result.cartoon_id,
      session_name: sessionName,
      created_at: result.rounds[0]?.request.timestamp || Date.now(),
      messages: messages
    }
    chatStore.saveToStorage()
  }

  // 检查角色是否存在，不存在则创建
  if (!characterStore.getCharacter(result.cartoon_id)) {
    const latestRound = result.rounds[result.rounds.length - 1]
    characterStore.createCharacter(result.cartoon_id, latestRound.request.character_image)
    if (latestRound.response.character_profile) {
      characterStore.updateCharacter(result.cartoon_id, {
        character_profile: latestRound.response.character_profile,
        draft: latestRound.response.draft
      })
    }
  }

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
