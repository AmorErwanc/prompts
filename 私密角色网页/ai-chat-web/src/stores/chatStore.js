import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { generateSessionId, generateDialogueId } from '../utils/idGenerator'
import { getStorage, setStorage, KEYS } from '../utils/storage'
import { callCharacterCreationWebhook } from '../utils/api'
import { useUserStore } from './userStore'
import { useCharacterStore } from './characterStore'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const sessions = ref({}) // { session_id: sessionData }
  const currentSessionId = ref(null)

  // 计算属性
  const currentSession = computed(() => {
    return sessions.value[currentSessionId.value] || null
  })

  const currentMessages = computed(() => {
    return currentSession.value?.messages || []
  })

  // 初始化：从localStorage加载数据
  function initialize() {
    const savedSessions = getStorage(KEYS.SESSIONS)
    const savedCurrent = getStorage(KEYS.CURRENT)

    if (savedSessions) {
      sessions.value = savedSessions
    }

    if (savedCurrent && savedCurrent.session_id) {
      currentSessionId.value = savedCurrent.session_id
    }
  }

  // 创建新会话
  function createSession(userId, cartoonId, sessionName = '新对话') {
    const sessionId = generateSessionId()
    const newSession = {
      session_id: sessionId,
      user_id: userId,
      cartoon_id: cartoonId,
      session_name: sessionName,
      created_at: Date.now(),
      messages: []
    }

    sessions.value[sessionId] = newSession
    currentSessionId.value = sessionId

    // 将会话添加到用户
    const userStore = useUserStore()
    userStore.addSessionToUser(userId, sessionId)

    saveToStorage()
    return newSession
  }

  // 切换当前会话
  function switchSession(sessionId) {
    if (sessions.value[sessionId]) {
      currentSessionId.value = sessionId
      saveCurrentToStorage()
      return true
    }
    return false
  }

  // 删除会话
  function deleteSession(sessionId) {
    const session = sessions.value[sessionId]
    if (session) {
      // 从用户的会话列表中移除
      const userStore = useUserStore()
      userStore.removeSessionFromUser(session.user_id, sessionId)

      // 删除会话
      delete sessions.value[sessionId]

      // 如果删除的是当前会话，清空当前会话ID
      if (currentSessionId.value === sessionId) {
        currentSessionId.value = null
      }

      saveToStorage()
      return true
    }
    return false
  }

  // 发送消息并调用webhook
  async function sendMessage(content) {
    if (!currentSession.value) {
      return { success: false, error: '没有选中的会话' }
    }

    const userStore = useUserStore()
    const characterStore = useCharacterStore()

    const session = currentSession.value
    const character = characterStore.getCharacter(session.cartoon_id)

    // 生成对话ID
    const dialogueId = generateDialogueId()

    // 添加用户消息
    const userMessage = {
      dialogue_id: dialogueId,
      role: 'user',
      content,
      timestamp: Date.now()
    }
    session.messages.push(userMessage)
    saveToStorage()

    // 调用webhook
    try {
      const result = await callCharacterCreationWebhook({
        session_id: session.session_id,
        user_id: session.user_id,
        dialogue_id: generateDialogueId(), // AI回复的对话ID
        cartoon_id: session.cartoon_id,
        user_prompt: content,
        character_image: character?.character_image || '',
        status: 'processing',
        tool_code: 'character_creation',
        force_generate: null
      })

      if (result.success && result.data) {
        // 添加AI回复消息
        const assistantMessage = {
          dialogue_id: generateDialogueId(),
          role: 'assistant',
          content: result.data.response,
          character_profile: result.data.character_profile || null,
          draft: result.data.draft,
          timestamp: Date.now()
        }
        session.messages.push(assistantMessage)

        // 只有在 draft 为 true 且有 character_profile 时才更新角色信息
        if (result.data.draft === true && result.data.character_profile) {
          characterStore.updateCharacter(session.cartoon_id, {
            character_profile: result.data.character_profile,
            draft: result.data.draft,
            updated_at: Date.now()
          })
        } else {
          // draft 为 false 时，只更新 draft 状态
          characterStore.updateCharacter(session.cartoon_id, {
            draft: result.data.draft,
            updated_at: Date.now()
          })
        }

        saveToStorage()
        return { success: true, data: result.data }
      } else {
        // 添加错误消息
        const errorMessage = {
          dialogue_id: generateDialogueId(),
          role: 'assistant',
          content: '抱歉，消息发送失败，请重试。',
          error: true,
          timestamp: Date.now()
        }
        session.messages.push(errorMessage)
        saveToStorage()
        return { success: false, error: result.error }
      }
    } catch (error) {
      console.error('发送消息失败:', error)
      return { success: false, error: error.message }
    }
  }

  // 更新会话信息
  function updateSession(sessionId, updates) {
    if (sessions.value[sessionId]) {
      Object.assign(sessions.value[sessionId], updates)
      saveToStorage()
      return true
    }
    return false
  }

  // 获取用户的所有会话
  function getUserSessions(userId) {
    return Object.values(sessions.value).filter(s => s.user_id === userId)
  }

  // 保存到localStorage
  function saveToStorage() {
    setStorage(KEYS.SESSIONS, sessions.value)
    saveCurrentToStorage()
  }

  // 保存当前状态
  function saveCurrentToStorage() {
    const current = getStorage(KEYS.CURRENT) || {}
    current.session_id = currentSessionId.value
    setStorage(KEYS.CURRENT, current)
  }

  return {
    // 状态
    sessions,
    currentSessionId,
    currentSession,
    currentMessages,

    // 方法
    initialize,
    createSession,
    switchSession,
    deleteSession,
    sendMessage,
    updateSession,
    getUserSessions,
    saveToStorage
  }
})
