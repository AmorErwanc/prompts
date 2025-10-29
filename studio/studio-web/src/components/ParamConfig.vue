<template>
  <div class="param-config">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>输入参数配置</span>
          <el-button type="primary" size="small" @click="addParam">添加参数</el-button>
        </div>
      </template>

      <div v-if="params.length === 0" class="empty-tip">
        <el-empty description="暂无参数，请点击【添加参数】开始配置" />
      </div>

      <div v-else class="param-list">
        <el-card
          v-for="(param, index) in params"
          :key="index"
          class="param-item"
          shadow="hover"
        >
          <el-form label-width="100px">
            <el-form-item label="参数类型">
              <el-select v-model="param.type" placeholder="选择类型">
                <el-option label="图片(img)" value="img" />
                <el-option label="文本(str)" value="str" />
                <el-option label="数字(num)" value="num" />
              </el-select>
            </el-form-item>

            <el-form-item label="参数名称">
              <el-input
                v-model="param.name"
                placeholder="例如: k_1, k_2, k_3"
              />
            </el-form-item>

            <el-form-item label="默认值">
              <el-input
                v-model="param.val"
                :type="param.type === 'img' ? 'text' : 'textarea'"
                :rows="2"
                :placeholder="getPlaceholder(param.type)"
              />
              <span class="tip-text">注意：此处设置的默认值会被缓存</span>

              <!-- 参数预览 -->
              <div v-if="param.val" class="param-preview">
                <div class="preview-label">预览：</div>
                <div class="preview-content">
                  <!-- 图片预览 -->
                  <div v-if="param.type === 'img' && isValidUrl(param.val)" class="image-preview">
                    <el-image
                      :src="param.val"
                      style="width: 200px; height: 200px; cursor: pointer;"
                      fit="cover"
                      :preview-src-list="[param.val]"
                    >
                      <template #error>
                        <div class="image-error">
                          <el-icon><Picture /></el-icon>
                          <span>图片加载失败</span>
                        </div>
                      </template>
                    </el-image>
                    <div class="preview-hint">点击图片可放大查看</div>
                  </div>

                  <!-- 文本/数字预览 -->
                  <div v-else-if="param.type === 'str' || param.type === 'num'" class="text-preview">
                    <el-tag type="info">{{ param.val }}</el-tag>
                  </div>
                </div>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button type="danger" size="small" @click="removeParam(index)">
                删除此参数
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <div class="action-buttons" v-if="params.length > 0">
        <el-button type="success" @click="saveParams">保存参数配置</el-button>
        <el-button @click="clearParams">清空所有参数</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'

// Props 和 Emits
const emit = defineEmits(['params-change'])

// 参数列表
const params = ref([])

// 获取占位符文本
const getPlaceholder = (type) => {
  switch (type) {
    case 'img':
      return '请输入图片URL地址'
    case 'str':
      return '请输入文本内容'
    case 'num':
      return '请输入数字'
    default:
      return '请输入参数值'
  }
}

// 验证URL是否有效
const isValidUrl = (url) => {
  if (!url || typeof url !== 'string') return false
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

// 添加参数
const addParam = () => {
  params.value.push({
    type: 'str',
    name: `k_${params.value.length + 1}`,
    val: ''
  })
}

// 删除参数
const removeParam = (index) => {
  params.value.splice(index, 1)
  saveParams()
}

// 清空所有参数
const clearParams = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有参数吗？',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    params.value = []
    saveParams()
    ElMessage.success('已清空所有参数')
  } catch {
    // 用户取消
  }
}

// 保存参数配置
const saveParams = () => {
  // 验证参数
  for (let i = 0; i < params.value.length; i++) {
    const param = params.value[i]
    if (!param.name) {
      ElMessage.warning(`第 ${i + 1} 个参数的名称不能为空`)
      return
    }
  }

  // 保存到 localStorage
  localStorage.setItem('studio_params_config', JSON.stringify(params.value))

  // 通知父组件
  emit('params-change', params.value)

  ElMessage.success('参数配置已保存')
}

// 加载保存的参数配置
const loadParams = () => {
  const saved = localStorage.getItem('studio_params_config')
  if (saved) {
    try {
      params.value = JSON.parse(saved)
      emit('params-change', params.value)
    } catch (error) {
      console.error('加载参数配置失败:', error)
    }
  }
}

// 监听参数变化
watch(params, () => {
  emit('params-change', params.value)
}, { deep: true })

// 组件挂载时加载配置
onMounted(() => {
  loadParams()
})

// 导入参数（从请求体）
const importParams = (importedParams) => {
  params.value = importedParams.map(param => ({
    type: param.type,
    name: param.name,
    val: param.val || ''
  }))

  // 自动保存
  saveParams()

  ElMessage.success(`成功导入 ${params.value.length} 个参数`)
}

// 暴露方法给父组件
defineExpose({
  getParams: () => params.value,
  importParams
})
</script>

<style scoped>
.param-config {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.param-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.param-item {
  border-left: 3px solid #409eff;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}

.tip-text {
  color: #909399;
  font-size: 12px;
  margin-left: 10px;
}

.empty-tip {
  padding: 20px;
}

.param-preview {
  margin-top: 15px;
  padding: 15px;
  background-color: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #b3d8ff;
}

.preview-label {
  font-weight: 600;
  color: #409eff;
  margin-bottom: 10px;
  font-size: 14px;
}

.preview-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.preview-hint {
  font-size: 12px;
  color: #909399;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #f56c6c;
  padding: 20px;
}

.image-error .el-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.text-preview {
  width: 100%;
}

.text-preview .el-tag {
  max-width: 100%;
  white-space: normal;
  word-break: break-all;
  height: auto;
  padding: 8px 12px;
}
</style>
