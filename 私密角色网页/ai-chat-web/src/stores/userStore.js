import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { generateUserId } from '../utils/idGenerator'
import { getStorage, setStorage, KEYS } from '../utils/storage'

export const useUserStore = defineStore('user', () => {
  // 状态
  const users = ref([])
  const currentUserId = ref(null)

  // 计算属性
  const currentUser = computed(() => {
    return users.value.find(u => u.user_id === currentUserId.value) || null
  })

  // 初始化：从localStorage加载数据
  function initialize() {
    const savedUsers = getStorage(KEYS.USERS)
    const savedCurrent = getStorage(KEYS.CURRENT)

    if (savedUsers && savedUsers.length > 0) {
      // 数据迁移：为旧用户数据补充缺失的字段
      users.value = savedUsers.map(user => ({
        ...user,
        sessions: user.sessions || [], // 确保 sessions 字段存在
        avatar: user.avatar || null,    // 确保 avatar 字段存在
        created_at: user.created_at || Date.now() // 确保 created_at 字段存在
      }))

      if (savedCurrent && savedCurrent.user_id) {
        currentUserId.value = savedCurrent.user_id
      } else {
        currentUserId.value = savedUsers[0].user_id
      }

      // 保存迁移后的数据
      saveToStorage()
    } else {
      // 如果没有数据，创建一个默认用户
      createUser('默认用户')
    }
  }

  // 创建新用户
  function createUser(username = '新用户') {
    const newUser = {
      user_id: generateUserId(),
      username,
      avatar: null,
      created_at: Date.now(),
      sessions: []
    }

    users.value.push(newUser)
    currentUserId.value = newUser.user_id
    saveToStorage()

    return newUser
  }

  // 切换当前用户
  function switchUser(userId) {
    const user = users.value.find(u => u.user_id === userId)
    if (user) {
      currentUserId.value = userId
      saveCurrentToStorage()
      return true
    }
    return false
  }

  // 更新用户信息
  function updateUser(userId, updates) {
    const user = users.value.find(u => u.user_id === userId)
    if (user) {
      Object.assign(user, updates)
      saveToStorage()
      return true
    }
    return false
  }

  // 删除用户
  function deleteUser(userId) {
    const index = users.value.findIndex(u => u.user_id === userId)
    if (index !== -1) {
      users.value.splice(index, 1)

      // 如果删除的是当前用户，切换到第一个用户
      if (currentUserId.value === userId) {
        currentUserId.value = users.value[0]?.user_id || null
        if (users.value.length === 0) {
          createUser('默认用户')
        }
      }

      saveToStorage()
      return true
    }
    return false
  }

  // 添加会话到用户
  function addSessionToUser(userId, sessionId) {
    const user = users.value.find(u => u.user_id === userId)
    if (user) {
      // 确保 sessions 数组存在
      if (!user.sessions) {
        user.sessions = []
      }
      if (!user.sessions.includes(sessionId)) {
        user.sessions.push(sessionId)
        saveToStorage()
      }
      return true
    }
    return false
  }

  // 从用户移除会话
  function removeSessionFromUser(userId, sessionId) {
    const user = users.value.find(u => u.user_id === userId)
    if (user) {
      const index = user.sessions.indexOf(sessionId)
      if (index !== -1) {
        user.sessions.splice(index, 1)
        saveToStorage()
        return true
      }
    }
    return false
  }

  // 保存到localStorage
  function saveToStorage() {
    setStorage(KEYS.USERS, users.value)
    saveCurrentToStorage()
  }

  // 保存当前状态
  function saveCurrentToStorage() {
    setStorage(KEYS.CURRENT, {
      user_id: currentUserId.value
    })
  }

  return {
    // 状态
    users,
    currentUserId,
    currentUser,

    // 方法
    initialize,
    createUser,
    switchUser,
    updateUser,
    deleteUser,
    addSessionToUser,
    removeSessionFromUser,
    saveToStorage
  }
})
