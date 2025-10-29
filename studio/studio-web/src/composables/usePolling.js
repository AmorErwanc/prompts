import { ref } from 'vue'

export function usePolling() {
  const pollingTasks = ref(new Map()) // 存储轮询任务

  /**
   * 开始轮询任务
   * @param {String} taskId - 任务ID
   * @param {Function} queryFn - 查询函数
   * @param {Function} callback - 完成回调
   * @param {Number} interval - 轮询间隔（毫秒）
   * @param {Number} maxRetries - 最大重试次数
   */
  const startPolling = (taskId, queryFn, callback, interval = 1000, maxRetries = 300) => {
    let retries = 0

    const poll = async () => {
      try {
        console.log(`[轮询] 第 ${retries + 1} 次查询 taskId: ${taskId}`)
        const result = await queryFn()

        console.log(`[轮询] taskId: ${taskId} 返回结果:`, result)

        // 根据返回结果判断任务状态
        if (result.code === 0 && result.data) {
          const progress = result.data.progress

          if (progress === 'completed') {
            // 任务完成
            console.log(`[轮询] ✅ taskId: ${taskId} 完成`, result.data)
            stopPolling(taskId)

            // 检查是否有错误信息（有些完成的任务可能带有错误）
            if (result.data.errMsg && result.data.errCode && result.data.errCode !== '00000') {
              console.log(`[轮询] ❌ taskId: ${taskId} 完成但有错误:`, result.data.errMsg)
              callback({
                success: false,
                error: result.data.errMsg,
                taskId
              })
              return
            }

            // 解析 content 字段（可能是 JSON 字符串）
            let content = result.data.content
            console.log('[轮询] 原始 content:', content)

            if (typeof content === 'string' && content) {
              try {
                const parsed = JSON.parse(content)
                console.log('[轮询] 解析后的 content:', parsed)

                // 尝试提取图片 URL
                if (parsed && parsed[0] && parsed[0].content && parsed[0].content[0]) {
                  const firstItem = parsed[0].content[0]
                  console.log('[轮询] 第一个内容项:', firstItem)

                  if (firstItem.type === 'img' && firstItem.val) {
                    content = firstItem.val
                    console.log('[轮询] 提取的图片URL:', content)
                  }
                }
              } catch (e) {
                console.warn('[轮询] 解析 content 失败，使用原始数据', e)
              }
            }

            console.log('[轮询] 最终返回的 content:', content)
            callback({ success: true, data: content, taskId })
          } else if (progress === 'handing') {
            // 还在处理中
            if (retries >= maxRetries) {
              console.log(`[轮询] ❌ taskId: ${taskId} 超时`)
              stopPolling(taskId)
              callback({ success: false, error: '查询超时', taskId })
            } else {
              retries++
              console.log(`[轮询] ⏳ taskId: ${taskId} 处理中... (${retries}/${maxRetries})`)
              const timer = setTimeout(poll, interval)
              pollingTasks.value.set(taskId, { timer, retries })
            }
          } else if (progress === 'fail') {
            // 任务失败（API 文档规定的状态是 'fail'，不是 'failed' 或 'error'）
            console.log(`[轮询] ❌ taskId: ${taskId} 失败:`, result.data.errMsg)
            stopPolling(taskId)
            callback({
              success: false,
              error: result.data.errMsg || result.data.content || '任务执行失败',
              taskId
            })
          } else {
            // 其他未知状态
            console.log(`[轮询] ⚠️ taskId: ${taskId} 未知状态: ${progress}`, result.data)
            stopPolling(taskId)
            callback({
              success: false,
              error: result.data.errMsg || result.data.content || ('任务状态异常: ' + progress),
              taskId
            })
          }
        } else {
          // 返回格式错误
          console.log(`[轮询] ⚠️ taskId: ${taskId} 返回格式错误`)
          if (retries >= maxRetries) {
            stopPolling(taskId)
            callback({ success: false, error: result.msg || '查询失败', taskId })
          } else {
            retries++
            const timer = setTimeout(poll, interval)
            pollingTasks.value.set(taskId, { timer, retries })
          }
        }
      } catch (error) {
        console.error(`[轮询] ⚠️  taskId: ${taskId} 查询出错:`, error)
        if (retries >= maxRetries) {
          stopPolling(taskId)
          callback({ success: false, error: error.message, taskId })
        } else {
          retries++
          const timer = setTimeout(poll, interval)
          pollingTasks.value.set(taskId, { timer, retries })
        }
      }
    }

    // 开始第一次轮询
    poll()
  }

  /**
   * 停止轮询任务
   * @param {String} taskId - 任务ID
   */
  const stopPolling = (taskId) => {
    const task = pollingTasks.value.get(taskId)
    if (task) {
      clearTimeout(task.timer)
      pollingTasks.value.delete(taskId)
    }
  }

  /**
   * 停止所有轮询任务
   */
  const stopAllPolling = () => {
    pollingTasks.value.forEach((task) => {
      clearTimeout(task.timer)
    })
    pollingTasks.value.clear()
  }

  return {
    pollingTasks,
    startPolling,
    stopPolling,
    stopAllPolling
  }
}
