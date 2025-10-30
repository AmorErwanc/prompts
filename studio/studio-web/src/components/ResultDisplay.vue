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
        <!-- 分组结果 -->
        <div v-for="group in groupedResults.groups" :key="`group-${group.groupIndex}`" class="result-group">
          <div class="group-header">
            <span class="group-title">第 {{ group.groupIndex + 1 }} 组</span>
            <el-tag type="info" size="small">共 {{ group.testCount }} 次测试</el-tag>
          </div>
          <div class="group-results">
            <el-card
              v-for="result in group.results"
              :key="result.id"
              class="result-item"
              :class="getResultClass(result.status)"
            >
              <div class="result-item-content">
                <div class="result-header">
                  <span class="result-title">第 {{ result.testIndex + 1 }} 次测试</span>
                  <div class="result-header-tags">
                    <el-tag v-if="result.accountName" type="info" size="small">
                      {{ result.accountName }}
                    </el-tag>
                    <el-tag :type="getStatusType(result.status)" size="small">
                      {{ getStatusText(result.status) }}
                    </el-tag>
                  </div>
                </div>

                <!-- 返回结果：非多输出时走单内容逻辑 -->
                <template v-if="result.status === 'success' && result.data && !isMultiOutput(result.data)">
                  <div class="result-content">
                    <!-- 根据返回数据类型展示 -->
                    <div v-if="isImageUrl(result.data)" class="result-image-container">
                      <el-image
                        :src="normalizeVal(result.data)"
                        style="width: 150px; height: auto; cursor: pointer;"
                        fit="contain"
                        :preview-src-list="[normalizeVal(result.data)]"
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
                      <video :src="normalizeVal(result.data)" controls style="max-width: 100%; max-height: 200px; cursor: pointer;" @click="onVideoClick"></video>
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

                <!-- 返回结果：多输出内容展示（分组结果） -->
                <template v-else-if="result.status === 'success' && isMultiOutput(result.data)">
                  <div class="result-content">
                    <div class="multi-content">
                      <div
                        v-for="(item, idx) in result.data"
                        :key="idx"
                        class="content-item"
                      >
                        <!-- 图片类型 -->
                        <div v-if="isImageType(item.type)" class="result-image-container">
                          <div class="content-type-label">
                            <el-tag type="success" size="small">图片 #{{ idx + 1 }}</el-tag>
                          </div>
                          <el-image
                            :src="normalizeVal(item.val)"
                            style="width: 150px; height: auto; cursor: pointer;"
                            fit="contain"
                            :preview-src-list="[normalizeVal(item.val)]"
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

                        <!-- 视频类型 -->
                        <div v-else-if="isVideoType(item.type)" class="result-video-container">
                          <div class="content-type-label">
                            <el-tag type="warning" size="small">视频 #{{ idx + 1 }}</el-tag>
                          </div>
                          <video
                            :src="normalizeVal(item.val)"
                            controls
                            preload="metadata"
                            crossorigin="anonymous"
                            style="max-width: 100%; max-height: 200px; border-radius: 8px; cursor: pointer;"
                            @click="onVideoClick"
                          >
                            您的浏览器不支持视频播放
                          </video>
                          <div class="video-url">
                            <el-link :href="normalizeVal(item.val)" target="_blank" type="primary">
                              打开原始视频链接
                            </el-link>
                          </div>
                        </div>

                        <!-- 文本类型 -->
                        <div v-else-if="isTextType(item.type)" class="result-text-container">
                          <div class="content-type-label">
                            <el-tag type="info" size="small">文本 #{{ idx + 1 }}</el-tag>
                          </div>
                          <el-input
                            :model-value="item.val"
                            type="textarea"
                            :rows="4"
                            readonly
                          />
                        </div>

                        <!-- 其他类型 -->
                        <div v-else class="result-text-container">
                          <div class="content-type-label">
                            <el-tag type="info" size="small">{{ item.type }} #{{ idx + 1 }}</el-tag>
                          </div>
                          <template v-if="isUrl(normalizeVal(item.val))">
                            <el-link :href="normalizeVal(item.val)" target="_blank" type="primary">{{ normalizeVal(item.val) }}</el-link>
                          </template>
                          <template v-else>
                            <el-input
                              :model-value="JSON.stringify(item.val, null, 2)"
                              type="textarea"
                              :rows="4"
                              readonly
                            />
                          </template>
                        </div>
                      </div>
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
        </div>

        <!-- 未分组结果（兼容旧数据） -->
        <el-card
          v-for="result in groupedResults.ungrouped"
          :key="result.id"
          class="result-item"
          :class="getResultClass(result.status)"
        >
          <div class="result-item-content">
            <div class="result-header">
              <span class="result-title">测试 #{{ result.index + 1 }}</span>
              <div class="result-header-tags">
                <el-tag v-if="result.accountName" type="info" size="small">
                  {{ result.accountName }}
                </el-tag>
                <el-tag :type="getStatusType(result.status)" size="small">
                  {{ getStatusText(result.status) }}
                </el-tag>
              </div>
            </div>

            <!-- 返回结果 -->
            <template v-if="result.status === 'success' && result.data">
              <div class="result-content">
                <!-- 多输出内容展示 -->
                <div v-if="isMultiOutput(result.data)" class="multi-content">
                  <div
                    v-for="(item, idx) in result.data"
                    :key="idx"
                    class="content-item"
                  >
                    <!-- 图片类型 -->
                    <div v-if="isImageType(item.type)" class="result-image-container">
                      <div class="content-type-label">
                        <el-tag type="success" size="small">图片 #{{ idx + 1 }}</el-tag>
                      </div>
                      <el-image
                        :src="normalizeVal(item.val)"
                        style="width: 150px; height: auto; cursor: pointer;"
                        fit="contain"
                        :preview-src-list="[normalizeVal(item.val)]"
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

                    <!-- 视频类型 -->
                    <div v-else-if="isVideoType(item.type)" class="result-video-container">
                      <div class="content-type-label">
                        <el-tag type="warning" size="small">视频 #{{ idx + 1 }}</el-tag>
                      </div>
                      <video
                        :src="normalizeVal(item.val)"
                        controls
                        preload="metadata"
                        crossorigin="anonymous"
                        style="width: 100%; height: auto; max-height: 200px; border-radius: 8px; cursor: pointer;"
                        @click="openVideoPreview(normalizeVal(item.val))"
                      >
                        您的浏览器不支持视频播放
                      </video>
                      <div class="video-url">
                        <el-link :href="normalizeVal(item.val)" target="_blank" type="primary">
                          打开原始视频链接
                        </el-link>
                      </div>
                      <div class="video-actions" style="text-align: center; margin-top: 6px;">
                        <el-button size="small" type="primary" @click="openVideoPreview(normalizeVal(item.val))">放大预览</el-button>
                      </div>
                    </div>

                    <!-- 文本类型 -->
                    <div v-else-if="isTextType(item.type)" class="result-text-container">
                      <div class="content-type-label">
                        <el-tag type="info" size="small">文本 #{{ idx + 1 }}</el-tag>
                      </div>
                      <el-input
                        :model-value="item.val"
                        type="textarea"
                        :rows="4"
                        readonly
                      />
                    </div>

                    <!-- 其他类型 -->
                    <div v-else class="result-text-container">
                      <div class="content-type-label">
                        <el-tag type="info" size="small">{{ item.type }} #{{ idx + 1 }}</el-tag>
                      </div>
                      <template v-if="isUrl(normalizeVal(item.val))">
                        <el-link :href="normalizeVal(item.val)" target="_blank" type="primary">{{ normalizeVal(item.val) }}</el-link>
                      </template>
                      <template v-else>
                        <el-input
                          :model-value="JSON.stringify(item.val, null, 2)"
                          type="textarea"
                          :rows="4"
                          readonly
                        />
                      </template>
                    </div>
                  </div>
                </div>

                <!-- 单个内容展示（兼容旧数据） -->
                <div v-else>
                  <div v-if="isImageUrl(result.data)" class="result-image-container">
                    <el-image
                      :src="result.data"
                      style="width: 150px; height: auto; cursor: pointer;"
                      fit="contain"
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
                    <video :src="normalizeVal(result.data)" controls style="width: 100%; height: auto; max-height: 200px; cursor: pointer;" @click="openVideoPreview(normalizeVal(result.data))"></video>
                    <div class="video-actions" style="text-align: center; margin-top: 6px;">
                      <el-button size="small" type="primary" @click="openVideoPreview(normalizeVal(result.data))">放大预览</el-button>
                    </div>
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
    <!-- 视频预览遮罩层 -->
    <el-dialog
      v-model="videoPreviewVisible"
      title="视频预览"
      width="80%"
      append-to-body
      :destroy-on-close="true"
    >
      <div class="video-preview-content">
        <video
          :src="videoPreviewUrl"
          controls
          :style="previewVideoStyle"
          @loadedmetadata="onPreviewVideoMetadata"
          crossorigin="anonymous"
          playsinline
        >
          您的浏览器不支持视频播放
        </video>
      </div>
    </el-dialog>
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

    // 详细调试 data 结构
    if (result.status === 'success' && result.data) {
      console.log(`[ResultDisplay] 结果 #${index + 1} - data 类型检查:`, {
        'typeof data': typeof result.data,
        'isArray': Array.isArray(result.data),
        'data.length': result.data.length,
        'data[0]': result.data[0],
        'data[0].type': result.data[0]?.type,
        'data[0].val': result.data[0]?.val
      })
    }
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

// 按组分类的结果
const groupedResults = computed(() => {
  const groups = []
  const ungrouped = []

  filteredResults.value.forEach(result => {
    if (result.groupIndex !== null && result.groupIndex !== undefined) {
      // 有分组信息
      if (!groups[result.groupIndex]) {
        groups[result.groupIndex] = {
          groupIndex: result.groupIndex,
          testCount: result.groupTestCount || 1,
          results: []
        }
      }
      groups[result.groupIndex].results.push(result)
    } else {
      // 没有分组信息（旧数据）
      ungrouped.push(result)
    }
  })

  // 过滤掉空组，并按 groupIndex 排序
  const sortedGroups = groups.filter(g => g && g.results.length > 0)

  return {
    groups: sortedGroups,
    ungrouped
  }
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

// 判断是否为多输出格式
const isMultiOutput = (data) => {
  const result = Array.isArray(data) &&
                 data.length > 0 &&
                 data[0] &&
                 typeof data[0] === 'object' &&
                 ('type' in data[0])
  console.log('[ResultDisplay] 判断是否为多输出格式:', {
    data,
    isArray: Array.isArray(data),
    length: data?.length,
    hasFirstElement: !!data?.[0],
    firstElementType: typeof data?.[0],
    hasTypeProperty: data?.[0] && 'type' in data[0],
    result
  })
  return result
}

// 判断是否为图片 URL（扩展支持无后缀与查询参数标识）
const isImageUrl = (url) => {
  console.log('[ResultDisplay] 判断是否为图片URL:', url, typeof url)
  if (typeof url !== 'string') {
    console.log('[ResultDisplay] 不是字符串类型')
    return false
  }
  // 1) 常规后缀判断
  if (/\.(jpg|jpeg|png|gif|webp|bmp)(\?.*)?$/i.test(url)) return true
  // 2) 查询参数或路径提示
  try {
    const u = new URL(url)
    const typeParam = u.searchParams.get('type') || u.searchParams.get('contentType') || u.searchParams.get('mime')
    if (typeParam && /image/i.test(typeParam)) return true
    if (/\/image\//i.test(u.pathname) || /\/images?\//i.test(u.pathname)) return true
  } catch (e) {
    // 非绝对URL或解析失败则忽略
  }
  return false
}

// 判断是否为视频 URL（扩展支持 m3u8 与查询参数标识）
const isVideoUrl = (url) => {
  if (typeof url !== 'string') return false
  // 1) 常规后缀判断（含 m3u8）
  if (/\.(mp4|webm|ogg|mov|m3u8)(\?.*)?$/i.test(url)) return true
  // 2) 查询参数或路径提示
  try {
    const u = new URL(url)
    const typeParam = u.searchParams.get('type') || u.searchParams.get('contentType') || u.searchParams.get('mime')
    if (typeParam && /video/i.test(typeParam)) return true
    if (/\/video\//i.test(u.pathname) || /\/videos?\//i.test(u.pathname)) return true
  } catch (e) {}
  return false
}

// 判断类型（多输出）
const isImageType = (t) => typeof t === 'string' && /^(img|image)$/i.test(t)
const isVideoType = (t) => typeof t === 'string' && /^(video|mp4|webm|ogg|mov|m3u8)$/i.test(t)
const isTextType  = (t) => typeof t === 'string' && /^(str|string|text)$/i.test(t)

// 判断是否为URL
const isUrl = (val) => typeof val === 'string' && /^(https?:\/\/|data:)/i.test(val)

// 归一化内容值（移除首尾空格与反引号/引号）
const normalizeVal = (val) => {
  if (typeof val !== 'string') return val
  let s = val.trim()
  s = s.replace(/^`+|`+$/g, '')
  s = s.replace(/^"+|"+$/g, '')
  s = s.replace(/^'+|'+$/g, '')
  return s
}

// 视频遮罩层预览
const videoPreviewVisible = ref(false)
const videoPreviewUrl = ref('')
// 预览视频样式，默认按容器最大尺寸约束
const previewVideoStyle = ref({
  maxWidth: '80vw',
  maxHeight: '70vh',
  width: 'auto',
  height: 'auto',
  borderRadius: '8px'
})

const openVideoPreview = (url) => {
  videoPreviewUrl.value = normalizeVal(url)
  // 打开前重置为容器自适应，待 metadata 加载后再根据视频实际尺寸调整
  previewVideoStyle.value = {
    maxWidth: '80vw',
    maxHeight: '70vh',
    width: 'auto',
    height: 'auto',
    borderRadius: '8px'
  }
  videoPreviewVisible.value = true
}

// 根据视频元数据自适应尺寸（按 80vw x 70vh 约束，保持比例）
const onPreviewVideoMetadata = (e) => {
  const el = e?.target
  if (!el) return
  const vw = el.videoWidth || 0
  const vh = el.videoHeight || 0
  if (vw <= 0 || vh <= 0) return
  const viewportW = Math.floor(window.innerWidth * 0.8)
  const viewportH = Math.floor(window.innerHeight * 0.7)
  const scale = Math.min(viewportW / vw, viewportH / vh, 1)
  previewVideoStyle.value = {
    width: Math.round(vw * scale) + 'px',
    height: Math.round(vh * scale) + 'px',
    borderRadius: '8px'
  }
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
  /* 批量测试结果展示 */
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
  gap: 25px;
}

/* 分组样式 */
.result-group {
  background-color: #f9fafb;
  border-radius: 8px;
  padding: 15px;
  border: 2px solid #e4e7ed;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e4e7ed;
}

.group-title {
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}

.group-results {
  display: flex;
  flex-direction: column;
  gap: 12px;
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

.result-header-tags {
  display: flex;
  gap: 8px;
  align-items: center;
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

/* 多内容显示样式 */
.multi-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 10px;
}

.content-item {
  padding: 15px;
  background-color: #fafafa;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}

.content-type-label {
  margin-bottom: 10px;
}

.result-video-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.video-url {
  text-align: center;
  padding-top: 8px;
}

.result-text-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.empty-state {
  padding: 40px 0;
}

/* 视频遮罩预览弹窗内容居中 */
.video-preview-content {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
