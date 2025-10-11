/**
 * localStorage封装工具
 */

const STORAGE_PREFIX = 'ai_chat_'

const KEYS = {
  USERS: `${STORAGE_PREFIX}users`,
  SESSIONS: `${STORAGE_PREFIX}sessions`,
  CHARACTERS: `${STORAGE_PREFIX}characters`,
  CURRENT: `${STORAGE_PREFIX}current`
}

/**
 * 获取数据
 */
export function getStorage(key) {
  try {
    const data = localStorage.getItem(key)
    return data ? JSON.parse(data) : null
  } catch (error) {
    console.error('读取localStorage失败:', error)
    return null
  }
}

/**
 * 保存数据
 */
export function setStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
    return true
  } catch (error) {
    console.error('保存localStorage失败:', error)
    return false
  }
}

/**
 * 删除数据
 */
export function removeStorage(key) {
  try {
    localStorage.removeItem(key)
    return true
  } catch (error) {
    console.error('删除localStorage失败:', error)
    return false
  }
}

/**
 * 清空所有数据
 */
export function clearAllStorage() {
  try {
    Object.values(KEYS).forEach(key => {
      localStorage.removeItem(key)
    })
    return true
  } catch (error) {
    console.error('清空localStorage失败:', error)
    return false
  }
}

// 导出key常量
export { KEYS }
