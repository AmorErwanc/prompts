<template>
  <div class="result-display">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>测试结果</span>
          <div class="header-actions">
            <el-radio-group v-model="filterStatus" size="small">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="success">成功</el-radio-button>
              <el-radio-button label="error">失败</el-radio-button>
              <el-radio-button label="pending">进行中</el-radio-button>
            </el-radio-group>
            <el-button
              v-if="results.length > 0"
              type="success"
              size="small"
              @click="exportResults"
            >
              导出结果
            </el-button>
          </div>
        </div>
      </template>

      <!-- 进度统计 -->
      <div v-if="results.length > 0" class="stats-bar">
        <el-space>
          <el-tag>总数: {{ results.length }}</el-tag>
          <el-tag type="success">成功: {{ successCount }}</el-tag>
          <el-tag type="danger">失败: {{ errorCount }}</el-tag>
          <el-tag type="warning">进行中: {{ pendingCount }}</el-tag>
        </el-space>
        <el-progress
          :percentage="progressPercentage"
          :status="allCompleted ? 'success' : undefined"
        />
      </div>

      <!-- 结果列表 -->
      <div v-if="filteredResults.length > 0" class="result-list">
        <el-card
          v-for="(result, index) in filteredResults"
          :key="result.id"
          class="result-item"
          :class="getResultClass(result.status)"
        >
          <div class="result-item-content">
            <div class="result-header">
              <span class="result-title">测试 #{{ result.index + 1 }}</span>
              <el-tag :type="getStatusType(result.status)" size="small">
                {{ getStatusText(result.status) }}
              </el-tag>
            </div>

            <!-- 返回结果 -->
            <template v-if="result.status === 'success' && result.data">
              <div class="result-content">
                <!-- 根据返回数据类型展示 -->
                <div v-if="isImageUrl(result.data)" class="result-image-container">
                  <el-image
                    :src="result.data"
                    style="width: 300px; height: 300px; cursor: pointer;"
                    fit="cover"
                    :preview-src-list="[result.data]"
                    :initial-index="0"
                  >
                    <template #error>
                      <div class="image-error">
                        <el-icon><Picture /></el-icon>
                        <span>加载失败</span>
                      </div>
                    </template>
                  </el-image>
                  <div class="image-hint">点击放大查看原图</div>
                </div>
                <div v-else-if="isVideoUrl(result.data)">
                  <video :src="result.data" controls style="max-width: 100%"></video>
                </div>
                <div v-else class="text-result">
                  <el-input
                    :model-value="JSON.stringify(result.data, null, 2)"
                    type="textarea"
                    :rows="6"
                    readonly
                  />
                </div>
              </div>
            </template>

            <!-- 错误信息 -->
            <template v-if="result.status === 'error' && result.error">
              <el-divider content-position="left">错误信息</el-divider>
              <el-alert :title="result.error" type="error" :closable="false" />
            </template>

            <!-- 耗时信息 -->
            <div v-if="result.duration" class="duration-info">
              <el-tag size="small">耗时: {{ result.duration }}ms</el-tag>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <el-empty description="暂无测试结果" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import { exportExcel } from '../utils/excel'

// Props
const props = defineProps({
  results: {
    type: Array,
    default: () => []
  }
})

// 监听结果变化
watch(() => props.results, (newResults) => {
  console.log('[ResultDisplay] 收到新的结果数据:', newResults)
  newResults.forEach((result, index) => {
    console.log(`[ResultDisplay] 结果 #${index + 1}:`, {
      status: result.status,
      data: result.data,
      error: result.error,
      taskId: result.taskId
    })
  })
}, { deep: true })

// 筛选状态
const filterStatus = ref('all')

// 统计数据
const successCount = computed(() =>
  props.results.filter(r => r.status === 'success').length
)

const errorCount = computed(() =>
  props.results.filter(r => r.status === 'error').length
)

const pendingCount = computed(() =>
  props.results.filter(r => r.status === 'pending').length
)

const progressPercentage = computed(() => {
  if (props.results.length === 0) return 0
  const completed = successCount.value + errorCount.value
  return Math.round((completed / props.results.length) * 100)
})

const allCompleted = computed(() => pendingCount.value === 0)

// 筛选后的结果
const filteredResults = computed(() => {
  if (filterStatus.value === 'all') {
    return props.results
  }
  return props.results.filter(r => r.status === filterStatus.value)
})

// 获取状态样式
const getResultClass = (status) => {
  return `status-${status}`
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    success: 'success',
    error: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: '进行中',
    success: '成功',
    error: '失败'
  }
  return textMap[status] || '未知'
}

// 判断是否为图片 URL
const isImageUrl = (url) => {
  console.log('[ResultDisplay] 判断是否为图片URL:', url, typeof url)
  if (typeof url !== 'string') {
    console.log('[ResultDisplay] 不是字符串类型')
    return false
  }
  const isImage = /\.(jpg|jpeg|png|gif|webp|bmp)(\?.*)?$/i.test(url)
  console.log('[ResultDisplay] 是否为图片:', isImage)
  return isImage
}

// 判断是否为视频 URL
const isVideoUrl = (url) => {
  if (typeof url !== 'string') return false
  return /\.(mp4|webm|ogg|mov)(\?.*)?$/i.test(url)
}

// 导出结果
const exportResults = () => {
  try {
    const data = props.results.map((result, index) => {
      const row = {
        '序号': index + 1,
        '状态': getStatusText(result.status),
        '耗时(ms)': result.duration || '-'
      }

      // 添加请求参数
      result.params.forEach(param => {
        row[`参数_${param.name}`] = param.val
      })

      // 添加结果
      if (result.status === 'success') {
        row['结果'] = typeof result.data === 'string'
          ? result.data
          : JSON.stringify(result.data)
      } else if (result.status === 'error') {
        row['错误'] = result.error
      }

      return row
    })

    exportExcel(data, `测试结果_${Date.now()}.xlsx`)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败: ' + error.message)
  }
}
</script>

<style scoped>
.result-display {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.stats-bar {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.result-item {
  border-left: 4px solid #dcdfe6;
  transition: all 0.3s;
}

.result-item-content {
  max-height: 600px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 10px;
}

/* 自定义滚动条样式 */
.result-item-content::-webkit-scrollbar {
  width: 8px;
}

.result-item-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.result-item-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.result-item-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.result-item.status-success {
  border-left-color: #67c23a;
}

.result-item.status-error {
  border-left-color: #f56c6c;
}

.result-item.status-pending {
  border-left-color: #e6a23c;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.result-title {
  font-weight: bold;
  font-size: 16px;
}

.params-display {
  margin: 10px 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}

.param-label {
  font-weight: 600;
  color: #606266;
  font-size: 14px;
}

.param-value {
  color: #303133;
}

.param-image {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background-color: #fff;
  border-radius: 8px;
  border: 2px solid #dcdfe6;
  transition: all 0.3s;
}

.param-image:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

.param-image .el-image {
  display: block;
  border-radius: 4px;
  overflow: hidden;
}

.image-hint {
  font-size: 12px;
  color: #909399;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #c0c4cc;
}

.image-error .el-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.result-image-container {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 2px solid #e8e8e8;
  transition: all 0.3s;
}

.result-image-container:hover {
  border-color: #67c23a;
  box-shadow: 0 2px 12px rgba(103, 194, 58, 0.2);
}

.result-image-container .el-image {
  border-radius: 4px;
  overflow: hidden;
}

.param-text {
  padding: 8px;
  background-color: #fff;
  border-radius: 4px;
  word-break: break-all;
}

.result-content {
  margin: 10px 0;
}

.text-result {
  margin-top: 10px;
}

.duration-info {
  margin-top: 10px;
  text-align: right;
}

.empty-state {
  padding: 40px 0;
}
</style>
