<template>
  <div class="test-statistics">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">总数</div>
        <div class="stat-value">{{ statistics.total }}</div>
      </div>

      <div class="stat-card success">
        <div class="stat-label">成功</div>
        <div class="stat-value">{{ statistics.success }}</div>
      </div>

      <div class="stat-card failed">
        <div class="stat-label">失败</div>
        <div class="stat-value">{{ statistics.failed }}</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">成功率</div>
        <div class="stat-value">{{ successRateText }}</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">平均耗时</div>
        <div class="stat-value">{{ avgDurationText }}</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">总耗时</div>
        <div class="stat-value">{{ totalDurationText }}</div>
      </div>
    </div>

    <div v-if="statistics.min_duration !== null" class="stat-details">
      <span>最快: {{ formatDuration(statistics.min_duration) }}</span>
      <span>最慢: {{ formatDuration(statistics.max_duration) }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  statistics: {
    type: Object,
    required: true
  }
})

const successRateText = computed(() => {
  const rate = props.statistics.success_rate * 100
  return `${rate.toFixed(1)}%`
})

const avgDurationText = computed(() => {
  return formatDuration(props.statistics.avg_duration)
})

const totalDurationText = computed(() => {
  return formatDuration(props.statistics.total_duration)
})

function formatDuration(ms) {
  if (ms === null || ms === undefined) return '-'
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(2)}s`
}
</script>

<style scoped>
.test-statistics {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.stat-card {
  text-align: center;
  padding: 16px;
  border-radius: 8px;
  background-color: #F9FAFB;
  border: 1px solid #E5E7EB;
}

.stat-card.success {
  background-color: #ECFDF5;
  border-color: #A7F3D0;
}

.stat-card.failed {
  background-color: #FEF2F2;
  border-color: #FECACA;
}

.stat-label {
  font-size: 12px;
  color: #6B7280;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1F2937;
}

.stat-card.success .stat-value {
  color: #059669;
}

.stat-card.failed .stat-value {
  color: #DC2626;
}

.stat-details {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #E5E7EB;
  display: flex;
  justify-content: space-around;
  font-size: 13px;
  color: #6B7280;
}

.stat-details span {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
