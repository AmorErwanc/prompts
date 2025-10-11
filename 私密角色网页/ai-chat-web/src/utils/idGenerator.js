/**
 * 生成24位数字ID
 * 格式：13位毫秒时间戳 + 11位随机数
 * 示例：175985505615742543249277
 */
export function generateId() {
  // 13位时间戳
  const timestamp = Date.now().toString()

  // 11位随机数（0-99999999999）
  const random = Math.floor(Math.random() * 100000000000)
    .toString()
    .padStart(11, '0')

  return timestamp + random
}

/**
 * 生成用户ID
 */
export function generateUserId() {
  return generateId()
}

/**
 * 生成会话ID
 */
export function generateSessionId() {
  return generateId()
}

/**
 * 生成对话ID
 */
export function generateDialogueId() {
  return generateId()
}

/**
 * 生成角色ID
 */
export function generateCartoonId() {
  return generateId()
}
