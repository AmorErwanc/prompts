/**
 * Webhook API调用
 */

const WEBHOOK_URL = 'https://n8n.games/webhook/ideaflow/character'

/**
 * 调用角色创建webhook
 * @param {Object} params - 请求参数
 * @param {string} params.session_id - 会话ID
 * @param {string} params.user_id - 用户ID
 * @param {string} params.dialogue_id - 对话ID
 * @param {string} params.cartoon_id - 角色ID
 * @param {string} params.user_prompt - 用户输入
 * @param {string} params.character_image - 角色图片URL
 * @param {string} params.status - 处理状态（processing/success/failed）
 * @param {string} params.tool_code - 工具代码（默认character_creation）
 * @param {string|null} params.force_generate - 是否强制生成（null/manual/auto）
 * @returns {Promise<Object>} 返回响应数据
 */
export async function callCharacterCreationWebhook(params) {
  try {
    const requestBody = {
      session_id: params.session_id,
      user_id: params.user_id,
      dialogue_id: params.dialogue_id,
      cartoon_id: params.cartoon_id,
      user_prompt: params.user_prompt,
      character_image: params.character_image,
      status: params.status || 'processing',
      tool_code: params.tool_code || 'character_creation',
      force_generate: params.force_generate || null
    }

    const response = await fetch(WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    })

    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status}`)
    }

    const data = await response.json()
    return {
      success: true,
      data
    }
  } catch (error) {
    console.error('Webhook调用失败:', error)
    return {
      success: false,
      error: error.message
    }
  }
}

/**
 * 默认角色头像列表
 */
export const DEFAULT_AVATARS = [
  'https://img.ideaflow.pro/image/05b5a28fd9cdbee86a9cefec726d814c.png',
  'https://img.ideaflow.pro/image/055f6da72bae8cfb58757f7c3df4cd07.png',
  'https://img.ideaflow.pro/image/09f34c0ecfbebc88db6fe6e912bdf256.png'
]
