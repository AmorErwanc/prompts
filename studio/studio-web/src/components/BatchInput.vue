<template>
  <div class="batch-input">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>批量测试数据</span>
          <div class="header-buttons">
            <!-- 快速添加 -->
            <el-popover placement="bottom" :width="400" trigger="click">
              <template #reference>
                <el-button type="primary" size="small">
                  <el-icon><Lightning /></el-icon>
                  快速添加N组
                </el-button>
              </template>
              <div class="quick-add-popover">
                <div style="margin-bottom: 15px; color: #606266;">
                  💡 使用参数默认值，快速添加多组相同的测试数据
                </div>
                <div class="quick-batch-controls">
                  <div class="input-group">
                    <span class="label">添加数量：</span>
                    <el-input-number
                      v-model="quickBatchCount"
                      :min="1"
                      :max="100"
                      :step="1"
                      size="default"
                      style="width: 120px"
                    />
                  </div>
                  <el-button-group style="margin-top: 10px;">
                    <el-button @click="quickBatchCount = 5" size="small">5组</el-button>
                    <el-button @click="quickBatchCount = 10" size="small">10组</el-button>
                    <el-button @click="quickBatchCount = 15" size="small">15组</el-button>
                    <el-button @click="quickBatchCount = 20" size="small">20组</el-button>
                  </el-button-group>
                  <el-button
                    type="primary"
                    size="default"
                    @click="addQuickBatch"
                    :disabled="!canQuickBatch"
                    style="width: 100%; margin-top: 10px;"
                  >
                    添加到列表
                  </el-button>
                </div>
              </div>
            </el-popover>

            <!-- 手动添加 -->
            <el-button type="success" size="small" @click="addTestGroup">
              <el-icon><Plus /></el-icon>
              手动添加1组
            </el-button>

            <!-- 导入 Excel -->
            <el-upload
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleFileChange"
              accept=".xlsx,.xls,.csv"
            >
              <el-button type="warning" size="small">
                <el-icon><Upload /></el-icon>
                导入 Excel
              </el-button>
            </el-upload>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <div v-if="testGroups.length > 0" style="margin-top: 15px">
        <el-table :data="testGroups" border style="width: 100%">
          <el-table-column type="index" label="序号" width="60" />

          <!-- 动态列：根据参数配置生成 -->
          <el-table-column
            v-for="param in paramConfig"
            :key="param.name"
            :label="`${param.name} (${param.type})`"
            min-width="150"
          >
            <template #default="{ row, $index }">
              <el-input
                v-model="row[param.name]"
                :placeholder="`请输入 ${param.name}`"
                size="small"
                @change="handleDataChange"
              />
            </template>
          </el-table-column>

          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ $index }">
              <el-button
                type="danger"
                size="small"
                link
                @click="removeTestGroup($index)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="action-bar">
          <div class="action-info">
            <el-tag type="success" size="large">共 {{ testGroups.length }} 组测试数据</el-tag>
          </div>
          <el-space>
            <el-button type="warning" @click="clearAll">
              <el-icon><Delete /></el-icon>
              清空全部
            </el-button>
            <el-button type="primary" size="large" :disabled="!canExecute" @click="executeTests">
              <el-icon><Promotion /></el-icon>
              开始批量测试
            </el-button>
          </el-space>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <el-empty description="暂无测试数据">
          <el-button type="primary" @click="addTestGroup">添加第一组测试数据</el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Promotion, Lightning, Plus, Delete } from '@element-plus/icons-vue'
import { readExcel } from '../utils/excel'

// Props
const props = defineProps({
  paramConfig: {
    type: Array,
    default: () => []
  },
  apiConfig: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['start-test'])

// 测试数据组
const testGroups = ref([])

// 快速批量测试次数
const quickBatchCount = ref(10)

// 是否可以执行测试
const canExecute = computed(() => {
  if (testGroups.value.length === 0) return false
  if (!props.apiConfig || !props.apiConfig.pipeId) return false
  if (props.paramConfig.length === 0) return false
  return true
})

// 是否可以快速批量测试
const canQuickBatch = computed(() => {
  if (!props.apiConfig || !props.apiConfig.pipeId) return false
  if (props.paramConfig.length === 0) return false
  if (quickBatchCount.value < 1) return false
  return true
})

// 添加测试组
const addTestGroup = () => {
  if (props.paramConfig.length === 0) {
    ElMessage.warning('请先配置输入参数')
    return
  }

  const newGroup = {}
  props.paramConfig.forEach(param => {
    newGroup[param.name] = param.val || ''
  })
  testGroups.value.push(newGroup)
}

// 删除测试组
const removeTestGroup = (index) => {
  testGroups.value.splice(index, 1)
  handleDataChange()
}

// 清空所有测试组
const clearAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有测试数据吗？',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    testGroups.value = []
    handleDataChange()
    ElMessage.success('已清空所有测试数据')
  } catch {
    // 用户取消
  }
}

// 处理文件上传
const handleFileChange = async (file) => {
  try {
    const { headers, rows } = await readExcel(file.raw)

    if (rows.length === 0) {
      ElMessage.warning('Excel 文件中没有数据')
      return
    }

    // 验证 Excel 列头是否匹配参数配置
    const paramNames = props.paramConfig.map(p => p.name)
    const missingParams = paramNames.filter(name => !headers.includes(name))

    if (missingParams.length > 0) {
      ElMessage.warning(`Excel 缺少以下参数列: ${missingParams.join(', ')}`)
      return
    }

    // 导入数据（追加到现有数据）
    const newGroups = rows.map(row => {
      const group = {}
      props.paramConfig.forEach(param => {
        group[param.name] = row[param.name] || ''
      })
      return group
    })

    testGroups.value.push(...newGroups)

    handleDataChange()
    ElMessage.success(`成功导入 ${rows.length} 组测试数据，当前共 ${testGroups.value.length} 组`)
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败: ' + error.message)
  }
}

// 数据变化时保存
const handleDataChange = () => {
  // 可以选择保存到 localStorage
  // localStorage.setItem('studio_test_groups', JSON.stringify(testGroups.value))
}

// 快速添加多组测试数据
const addQuickBatch = () => {
  if (!canQuickBatch.value) {
    ElMessage.warning('请先配置接口和参数')
    return
  }

  // 生成指定次数的测试数据（追加，不清空现有数据）
  for (let i = 0; i < quickBatchCount.value; i++) {
    const group = {}
    props.paramConfig.forEach(param => {
      group[param.name] = param.val || ''
    })
    testGroups.value.push(group)
  }

  ElMessage.success(`已添加 ${quickBatchCount.value} 组测试数据到列表`)
  handleDataChange()
}

// 执行测试
const executeTests = () => {
  if (!canExecute.value) {
    ElMessage.warning('请检查配置和测试数据')
    return
  }

  // 转换测试数据为 API 需要的格式
  const testData = testGroups.value.map(group => {
    const params = []
    props.paramConfig.forEach(param => {
      params.push({
        type: param.type,
        name: param.name,
        val: group[param.name] || ''
      })
    })
    return params
  })

  emit('start-test', testData)
}

// 监听参数配置变化
watch(() => props.paramConfig, (newConfig, oldConfig) => {
  // 如果参数配置发生变化，更新现有测试组
  if (testGroups.value.length > 0 && newConfig.length > 0) {
    testGroups.value = testGroups.value.map(group => {
      const newGroup = {}
      newConfig.forEach(param => {
        newGroup[param.name] = group[param.name] || param.val || ''
      })
      return newGroup
    })
  }
}, { deep: true })

// 暴露方法给父组件
defineExpose({
  getTestGroups: () => testGroups.value,
  clearTestGroups: () => { testGroups.value = [] }
})
</script>

<style scoped>
.batch-input {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.action-bar {
  margin-top: 20px;
  padding: 20px;
  background: linear-gradient(to right, #f5f7fa, #e8f4f8);
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #d9ecff;
}

.action-info {
  flex: 1;
}

.empty-state {
  padding: 40px 0;
}

.quick-add-popover {
  padding: 10px;
}

.quick-batch-controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.input-group .label {
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}
</style>
