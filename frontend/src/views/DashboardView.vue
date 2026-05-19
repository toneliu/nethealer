<template>
  <div class="dashboard-view">
    <div class="view-header">
      <div class="header-left">
        <h2>监控仪表盘</h2>
        <p class="subtitle">实时网络健康状态和性能指标</p>
      </div>
      <div class="time-selector">
        <el-radio-group v-model="timeRange" size="default">
          <el-radio-button label="1h">1小时</el-radio-button>
          <el-radio-button label="6h">6小时</el-radio-button>
          <el-radio-button label="24h">24小时</el-radio-button>
          <el-radio-button label="7d">7天</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <div class="metrics-grid">
      <div class="metric-card" v-for="(metric, index) in metrics" :key="index" :class="`delay-${index + 1}`">
        <div class="metric-header">
          <span class="metric-icon" :style="{ background: metric.iconBg }">{{ metric.icon }}</span>
          <span class="metric-title">{{ metric.title }}</span>
        </div>
        <div class="metric-value">
          <span class="value">{{ metric.value }}</span>
          <span class="unit">{{ metric.unit }}</span>
        </div>
        <div class="metric-change" :class="metric.trend">
          <el-icon v-if="metric.trend === 'up'"><Top /></el-icon>
          <el-icon v-else-if="metric.trend === 'down'"><Bottom /></el-icon>
          <span>{{ metric.change }}</span>
        </div>
      </div>
    </div>

    <div class="charts-row">
      <div class="card chart-card">
        <div class="card-header">
          <h3><el-icon><DataLine /></el-icon> 流量趋势</h3>
          <el-select v-model="selectedInterface" size="small">
            <el-option label="核心-汇聚" value="core-dist" />
            <el-option label="汇聚-接入" value="dist-acc" />
            <el-option label="互联网出口" value="internet" />
          </el-select>
        </div>
        <div class="chart-container" ref="trafficChartRef"></div>
      </div>

      <div class="card chart-card">
        <div class="card-header">
          <h3><el-icon><Warning /></el-icon> 告警统计</h3>
        </div>
        <div class="chart-container" ref="alertChartRef"></div>
      </div>
    </div>

    <div class="data-row">
      <div class="card">
        <div class="card-header">
          <h3><el-icon><Document /></el-icon> 实时 Syslog</h3>
          <el-tag type="success" size="small">在线</el-tag>
        </div>
        <div class="log-list">
          <div v-for="(log, index) in recentLogs" :key="index" class="log-item" :class="log.level">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-source">{{ log.source }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3><el-icon><Cpu /></el-icon> 设备健康状态</h3>
        </div>
        <div class="device-health">
          <div v-for="device in deviceHealth" :key="device.id" class="device-item">
            <div class="device-info">
              <span class="device-name">{{ device.name }}</span>
              <span class="device-status" :class="device.status">{{ device.statusText }}</span>
            </div>
            <div class="health-bars">
              <div class="health-bar">
                <span class="bar-label">CPU</span>
                <el-progress :percentage="device.cpu" :color="getHealthColor(device.cpu)" :show-text="false" />
              </div>
              <div class="health-bar">
                <span class="bar-label">内存</span>
                <el-progress :percentage="device.memory" :color="getHealthColor(device.memory)" :show-text="false" />
              </div>
              <div class="health-bar">
                <span class="bar-label">温度</span>
                <el-progress :percentage="device.temp" :color="getHealthColor(device.temp)" :show-text="false" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import * as echarts from 'echarts'
import { DataLine, Warning, Document, Cpu, Top, Bottom } from '@element-plus/icons-vue'

const timeRange = ref('1h')
const selectedInterface = ref('core-dist')
const trafficChartRef = ref(null)
const alertChartRef = ref(null)

const metrics = ref([
  { title: '网络可用性', value: '99.97', unit: '%', change: '+0.02%', trend: 'up', icon: '📊', iconBg: 'rgba(16, 185, 129, 0.2)' },
  { title: '平均延迟', value: '12.3', unit: 'ms', change: '-2.1ms', trend: 'down', icon: '⚡', iconBg: 'rgba(79, 172, 254, 0.2)' },
  { title: '丢包率', value: '0.08', unit: '%', change: '+0.03%', trend: 'up', icon: '📉', iconBg: 'rgba(245, 158, 11, 0.2)' },
  { title: '活跃会话', value: '2,847', unit: '', change: '+156', trend: 'up', icon: '🔗', iconBg: 'rgba(139, 92, 246, 0.2)' }
])

const recentLogs = ref([
  { time: '10:24:32', source: 'acc-02', level: 'error', message: 'Interface GigabitEthernet0/1: CRC errors increased' },
  { time: '10:24:18', source: 'core-01', level: 'warning', message: 'Port GigabitEthernet1/0/1: High bandwidth utilization (87%)' },
  { time: '10:23:55', source: 'fw-01', level: 'info', message: 'Firewall rule hit count updated' },
  { time: '10:23:41', source: 'dist-01', level: 'info', message: 'Spanning tree topology change detected' },
  { time: '10:23:28', source: 'router-01', level: 'warning', message: 'BGP neighbor 192.168.1.1 state changed' }
])

const deviceHealth = ref([
  { id: 'core-01', name: '核心交换机', status: 'healthy', statusText: '健康', cpu: 34, memory: 56, temp: 42 },
  { id: 'dist-01', name: '汇聚交换机-A', status: 'healthy', statusText: '健康', cpu: 28, memory: 48, temp: 38 },
  { id: 'dist-02', name: '汇聚交换机-B', status: 'warning', statusText: '注意', cpu: 67, memory: 72, temp: 55 },
  { id: 'acc-02', name: '接入交换机-2', status: 'critical', statusText: '异常', cpu: 89, memory: 78, temp: 72 }
])

const getHealthColor = (value) => {
  if (value < 60) return '#10b981'
  if (value < 80) return '#f59e0b'
  return '#ef4444'
}

const initTrafficChart = () => {
  if (!trafficChartRef.value) return

  const chart = echarts.init(trafficChartRef.value)
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1f2937',
      borderColor: '#374151',
      textStyle: { color: '#e5e7eb' }
    },
    legend: {
      data: ['入站流量', '出站流量'],
      textStyle: { color: '#9ca3af' },
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '40px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#6b7280' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#6b7280' },
      splitLine: { lineStyle: { color: '#1f2937' } }
    },
    series: [
      {
        name: '入站流量',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#00f2fe', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 242, 254, 0.3)' },
            { offset: 1, color: 'rgba(0, 242, 254, 0)' }
          ])
        },
        data: [320, 280, 450, 680, 720, 580, 420]
      },
      {
        name: '出站流量',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#4facfe', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(79, 172, 254, 0.3)' },
            { offset: 1, color: 'rgba(79, 172, 254, 0)' }
          ])
        },
        data: [280, 250, 380, 620, 680, 520, 380]
      }
    ]
  }

  chart.setOption(option)
}

const initAlertChart = () => {
  if (!alertChartRef.value) return

  const chart = echarts.init(alertChartRef.value)
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1f2937',
      borderColor: '#374151',
      textStyle: { color: '#e5e7eb' }
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#111827',
          borderWidth: 2
        },
        label: {
          show: true,
          color: '#9ca3af',
          formatter: '{b}: {c} ({d}%)'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            color: '#fff'
          }
        },
        data: [
          { value: 45, name: '信息', itemStyle: { color: '#4facfe' } },
          { value: 28, name: '警告', itemStyle: { color: '#f59e0b' } },
          { value: 15, name: '错误', itemStyle: { color: '#ef4444' } },
          { value: 12, name: '严重', itemStyle: { color: '#dc2626' } }
        ]
      }
    ]
  }

  chart.setOption(option)
}

onMounted(() => {
  initTrafficChart()
  initAlertChart()
})
</script>

<style lang="scss" scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;

  h2 {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .subtitle {
    font-size: 13px;
    color: var(--text-muted);
  }
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
  opacity: 0;
  animation: fadeIn 0.5s ease forwards;

  &:hover {
    border-color: rgba(0, 242, 254, 0.3);
    transform: translateY(-2px);
  }
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.metric-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.metric-title {
  font-size: 13px;
  color: var(--text-muted);
}

.metric-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 8px;

  .value {
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary);
  }

  .unit {
    font-size: 14px;
    color: var(--text-muted);
  }
}

.metric-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;

  &.up {
    color: #10b981;
  }

  &.down {
    color: #ef4444;
  }
}

.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

.chart-card {
  .card-header {
    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
}

.chart-container {
  height: 280px;
}

.data-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.log-list {
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  background: rgba(255, 255, 255, 0.02);
  font-size: 12px;
  transition: background 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.05);
  }

  .log-time {
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-muted);
    font-size: 11px;
  }

  .log-source {
    font-family: 'JetBrains Mono', monospace;
    color: var(--secondary-color);
    background: rgba(79, 172, 254, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
  }

  .log-message {
    flex: 1;
    color: var(--text-secondary);
  }

  &.error {
    border-left: 3px solid var(--danger-color);
  }

  &.warning {
    border-left: 3px solid var(--warning-color);
  }

  &.info {
    border-left: 3px solid var(--secondary-color);
  }
}

.device-health {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.device-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 10px;
}

.device-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;

  .device-name {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .device-status {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;

    &.healthy {
      background: rgba(16, 185, 129, 0.1);
      color: #10b981;
    }

    &.warning {
      background: rgba(245, 158, 11, 0.1);
      color: #f59e0b;
    }

    &.critical {
      background: rgba(239, 68, 68, 0.1);
      color: #ef4444;
    }
  }
}

.health-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.health-bar {
  display: flex;
  align-items: center;
  gap: 10px;

  .bar-label {
    font-size: 10px;
    color: var(--text-muted);
    width: 30px;
  }

  :deep(.el-progress) {
    flex: 1;

    .el-progress-bar__outer {
      background: rgba(255, 255, 255, 0.05);
    }
  }
}
</style>
