import { ref } from 'vue'
import request from '../utils/request'

export function useApiRequest() {
  const loading = ref(false)
  const error = ref(null)

  /**
   * 发送测试请求
   * @param {Object} config - 接口配置
   * @param {Array} params - 输入参数
   * @returns {Promise} - 返回 taskId
   */
  const sendRequest = async (config, params) => {
    try {
      loading.value = true
      error.value = null

      const headers = {
        'Authorization': config.authorization,
        'Content-Type': 'application/json'
      }

      if (config.draft) {
        headers['Draft'] = config.draft
      }

      const body = {
        event: 'input',
        pipeId: config.pipeId,
        in: params
      }

      const response = await request({
        method: 'POST',
        url: 'https://cyapi-t.ideaflow.pro/uat/pipe/chat',
        headers,
        data: body
      })

      // 返回完整响应，让调用方处理不同的 code
      if (response.code === 0) {
        return response.data // 返回 taskId
      } else if (response.code === 405) {
        // 排队中，返回完整响应让调用方处理重试
        return response
      } else {
        throw new Error(response.msg || '请求失败')
      }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 查询任务结果
   * @param {String} taskId - 任务ID
   * @param {String} authorization - 认证令牌
   * @param {String} draft - 草稿标识
   * @returns {Promise} - 返回查询结果
   */
  const queryResult = async (taskId, authorization, draft) => {
    try {
      const headers = {
        'Authorization': authorization
      }

      if (draft) {
        headers['Draft'] = draft
      }

      const response = await request({
        method: 'GET',
        url: `https://cyapi.ideaflow.pro/pipe/album/progress/${taskId}`,
        headers
      })

      return response
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  return {
    loading,
    error,
    sendRequest,
    queryResult
  }
}
