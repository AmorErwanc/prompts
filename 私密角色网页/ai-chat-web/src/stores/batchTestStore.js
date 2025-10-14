import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { generateId, generateUserId, generateSessionId, generateCartoonId, generateDialogueId } from '../utils/idGenerator'
import { getStorage, setStorage } from '../utils/storage'
import { callCharacterCreationWebhook } from '../utils/api'
import { validateResponse } from '../utils/validator'
import { useCharacterStore } from './characterStore'

const BATCH_TESTS_KEY = 'ai_chat_batch_tests'

export const useBatchTestStore = defineStore('batchTest', () => {
  // 状态
  const currentBatch = ref(null)
  const isRunning = ref(false)
  const batchHistory = ref([])

  // 计算属性
  const successResults = computed(() => {
    if (!currentBatch.value) return []
    return currentBatch.value.results.filter(r => r.status === 'success')
  })

  const failedResults = computed(() => {
    if (!currentBatch.value) return []
    return currentBatch.value.results.filter(r => r.status === 'failed')
  })

  // 初始化：加载历史记录
  function initialize() {
    const saved = getStorage(BATCH_TESTS_KEY)
    if (saved && Array.isArray(saved)) {
      batchHistory.value = saved
    }
  }

  // 创建并执行批量测试
  async function createAndRunBatchTest(config) {
    const batchId = generateId()
    const batch = {
      batch_id: batchId,
      config: {
        ...config,
        created_at: Date.now()
      },
      statistics: {
        total: config.test_count,
        success: 0,
        failed: 0,
        pending: config.test_count,
        success_rate: 0,
        avg_duration: 0,
        min_duration: null,
        max_duration: null,
        start_time: Date.now(),
        end_time: null,
        total_duration: 0
      },
      results: [],
      created_at: Date.now()
    }

    currentBatch.value = batch
    isRunning.value = true

    // 生成所有测试任务
    const tasks = generateTasks(config, batchId)

    // 并行执行所有任务
    const promises = tasks.map((task, index) =>
      executeTest(task, index, batch)
    )

    await Promise.allSettled(promises)

    // 计算统计信息
    updateStatistics(batch)

    // 保存到 localStorage
    saveBatchTest(batch)

    isRunning.value = false
    return batch
  }

  // 生成测试任务
  function generateTasks(config, batchId) {
    const tasks = []
    const baseUserId = config.id_strategy === 'same_user' ? generateUserId() : null

    for (let i = 0; i < config.test_count; i++) {
      const userId = baseUserId || generateUserId()
      const sessionId = generateSessionId()
      const cartoonId = generateCartoonId()
      const dialogueId = generateDialogueId()

      tasks.push({
        test_id: `${batchId}_${i}`,
        user_id: userId,
        session_id: sessionId,
        cartoon_id: cartoonId,
        dialogue_id: dialogueId,
        user_prompt: config.user_prompt,
        character_image: config.character_image,
        status: 'processing',
        tool_code: 'character_creation',
        force_generate: null
      })
    }

    return tasks
  }

  // 执行单个测试
  async function executeTest(task, index, batch) {
    const startTime = Date.now()

    const result = {
      test_index: index + 1,
      status: 'pending',
      user_id: task.user_id,
      session_id: task.session_id,
      cartoon_id: task.cartoon_id,
      current_round: 0,
      rounds: [],
      error: null,
      validation: null
    }

    batch.results.push(result)

    try {
      // 调用 webhook
      const response = await callCharacterCreationWebhook(task)

      const duration = Date.now() - startTime

      if (!response.success) {
        result.status = 'failed'
        result.error = {
          message: response.error || '请求失败',
          code: 'REQUEST_FAILED'
        }
        result.duration = duration
        return
      }

      // 验证返回数据
      const validation = validateResponse(response.data)
      result.validation = validation

      if (!validation.valid) {
        result.status = 'failed'
        result.error = {
          message: '数据验证失败',
          code: 'VALIDATION_FAILED',
          details: validation.errors
        }
        result.duration = duration
        return
      }

      // 保存成功数据
      result.status = 'success'
      result.current_round = 1
      result.rounds.push({
        round: 1,
        dialogue_id: task.dialogue_id,
        request: {
          user_prompt: task.user_prompt,
          character_image: task.character_image,
          timestamp: startTime
        },
        response: response.data,
        duration,
        timestamp: Date.now()
      })
      result.duration = duration

      // 创建角色记录
      const characterStore = useCharacterStore()
      characterStore.createCharacter(task.cartoon_id, task.character_image)
      characterStore.updateCharacter(task.cartoon_id, {
        character_profile: response.data.character_profile,
        draft: response.data.draft
      })

    } catch (error) {
      result.status = 'failed'
      result.error = {
        message: error.message || '未知错误',
        code: 'EXCEPTION'
      }
      result.duration = Date.now() - startTime
    }
  }

  // 更新统计信息
  function updateStatistics(batch) {
    const results = batch.results
    const successCount = results.filter(r => r.status === 'success').length
    const failedCount = results.filter(r => r.status === 'failed').length
    const durations = results.filter(r => r.duration).map(r => r.duration)

    batch.statistics.success = successCount
    batch.statistics.failed = failedCount
    batch.statistics.pending = 0
    batch.statistics.success_rate = successCount / results.length
    batch.statistics.end_time = Date.now()
    batch.statistics.total_duration = batch.statistics.end_time - batch.statistics.start_time

    if (durations.length > 0) {
      batch.statistics.avg_duration = Math.round(
        durations.reduce((a, b) => a + b, 0) / durations.length
      )
      batch.statistics.min_duration = Math.min(...durations)
      batch.statistics.max_duration = Math.max(...durations)
    }
  }

  // 保存批量测试
  function saveBatchTest(batch) {
    // 保存到历史记录
    const historyItem = {
      batch_id: batch.batch_id,
      test_name: batch.config.test_name || `测试-${new Date(batch.created_at).toLocaleString()}`,
      created_at: batch.created_at,
      statistics: batch.statistics
    }

    const index = batchHistory.value.findIndex(h => h.batch_id === batch.batch_id)
    if (index !== -1) {
      batchHistory.value[index] = historyItem
    } else {
      batchHistory.value.unshift(historyItem)
    }

    // 保存历史列表
    setStorage(BATCH_TESTS_KEY, batchHistory.value)

    // 保存完整数据
    setStorage(`${BATCH_TESTS_KEY}_${batch.batch_id}`, batch)
  }

  // 加载批量测试
  function loadBatchTest(batchId) {
    const batch = getStorage(`${BATCH_TESTS_KEY}_${batchId}`)
    if (batch) {
      currentBatch.value = batch
      return batch
    }
    return null
  }

  // 批量追加轮次
  async function batchAppendRound(selectedResults, message) {
    if (!currentBatch.value) return

    isRunning.value = true

    const promises = selectedResults.map(result =>
      appendRound(result, message)
    )

    await Promise.allSettled(promises)

    // 更新统计信息（重新计算平均耗时等）
    updateStatistics(currentBatch.value)

    // 保存
    saveBatchTest(currentBatch.value)

    isRunning.value = false
  }

  // 追加单个轮次
  async function appendRound(result, message) {
    const nextRound = result.current_round + 1
    const startTime = Date.now()

    try {
      const response = await callCharacterCreationWebhook({
        user_id: result.user_id,
        session_id: result.session_id,
        dialogue_id: generateDialogueId(),
        cartoon_id: result.cartoon_id,
        user_prompt: message,
        character_image: result.rounds[0].request.character_image,
        status: 'processing',
        tool_code: 'character_creation',
        force_generate: null
      })

      const duration = Date.now() - startTime

      if (response.success) {
        const validation = validateResponse(response.data)

        if (validation.valid) {
          result.rounds.push({
            round: nextRound,
            dialogue_id: generateDialogueId(),
            request: {
              user_prompt: message,
              timestamp: startTime
            },
            response: response.data,
            duration,
            timestamp: Date.now()
          })

          result.current_round = nextRound

          // 更新角色信息
          const characterStore = useCharacterStore()
          characterStore.updateCharacter(result.cartoon_id, {
            character_profile: response.data.character_profile,
            draft: response.data.draft
          })
        } else {
          // 验证失败，记录但不更新轮次
          console.error('追加轮次验证失败:', validation.errors)
        }
      } else {
        console.error('追加轮次请求失败:', response.error)
      }
    } catch (error) {
      console.error('追加轮次异常:', error)
    }
  }

  // 删除批量测试
  function deleteBatchTest(batchId) {
    // 从历史记录中删除
    const index = batchHistory.value.findIndex(h => h.batch_id === batchId)
    if (index !== -1) {
      batchHistory.value.splice(index, 1)
      setStorage(BATCH_TESTS_KEY, batchHistory.value)
    }

    // 删除完整数据
    localStorage.removeItem(`${BATCH_TESTS_KEY}_${batchId}`)

    // 如果是当前批次，清空
    if (currentBatch.value?.batch_id === batchId) {
      currentBatch.value = null
    }
  }

  return {
    // 状态
    currentBatch,
    isRunning,
    batchHistory,
    successResults,
    failedResults,

    // 方法
    initialize,
    createAndRunBatchTest,
    batchAppendRound,
    loadBatchTest,
    saveBatchTest,
    deleteBatchTest
  }
})
