/**
 * 数据验证器
 * 验证 Webhook 返回的数据是否符合要求
 */

/**
 * 验证响应数据
 * @param {Object} data - Webhook 返回的数据
 * @returns {Object} { valid: boolean, errors: string[] }
 */
export function validateResponse(data) {
  const errors = []

  // 验证数据对象存在
  if (!data || typeof data !== 'object') {
    return {
      valid: false,
      errors: ['返回数据不是有效的对象']
    }
  }

  // 验证 response 字段（必须有值）
  if (!data.response || typeof data.response !== 'string') {
    errors.push('response 字段缺失或类型错误（必须是非空字符串）')
  }

  // 验证 summary 字段（必须有值）
  if (!data.summary || typeof data.summary !== 'string') {
    errors.push('summary 字段缺失或类型错误（必须是非空字符串）')
  }

  // 验证 draft 字段（必须有值）
  if (typeof data.draft !== 'boolean') {
    errors.push('draft 字段缺失或类型错误（必须是 boolean）')
  }

  // 只有 draft 为 true 时才验证 character_profile
  if (data.draft === true) {
    if (!data.character_profile || typeof data.character_profile !== 'object') {
      errors.push('draft 为 true 时，character_profile 字段缺失或类型错误（必须是对象）')
    } else {
      // 必须存在的字段列表（值可以为 null）
      const requiredFields = [
        'name',
        'gender',
        'identity',
        'personality_traits',
        'speaking_style',
        'background_story',
        'relationship',
        'additional_info'
      ]

      for (const field of requiredFields) {
        if (!(field in data.character_profile)) {
          errors.push(`character_profile.${field} 字段不存在`)
        }
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * 格式化验证错误信息
 * @param {string[]} errors - 错误列表
 * @returns {string} 格式化后的错误信息
 */
export function formatValidationErrors(errors) {
  if (!errors || errors.length === 0) {
    return ''
  }
  return errors.join('; ')
}
