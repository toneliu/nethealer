<template>
  <div class="report-view">
    <div class="view-header">
      <div class="header-left">
        <h2>报告中心</h2>
        <p class="subtitle">故障分析报告和运维知识库</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="generateReport">
          <el-icon><Document /></el-icon>
          生成报告
        </el-button>
      </div>
    </div>

    <div class="report-container">
      <div class="report-list">
        <div class="card">
          <div class="card-header">
            <h3><el-icon><Folder /></el-icon> 历史报告</h3>
          </div>
          <div class="report-filters">
            <el-select v-model="reportType" placeholder="报告类型" size="small">
              <el-option label="全部" value="all" />
              <el-option label="故障分析" value="fault" />
              <el-option label="健康检查" value="health" />
              <el-option label="变更记录" value="change" />
            </el-select>
          </div>
          <div class="reports">
            <div 
              v-for="report in filteredReports" 
              :key="report.id" 
              class="report-item"
              :class="{ active: selectedReport?.id === report.id }"
              @click="selectReport(report)"
            >
              <div class="report-icon">
                <el-icon size="20"><Document /></el-icon>
              </div>
              <div class="report-info">
                <span class="report-title">{{ report.title }}</span>
                <span class="report-meta">{{ report.date }} · {{ report.size }}</span>
              </div>
              <el-tag size="small" :type="getReportTypeColor(report.type)">
                {{ getReportTypeName(report.type) }}
              </el-tag>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3><el-icon><Collection /></el-icon> 知识库</h3>
          </div>
          <div class="knowledge-list">
            <div v-for="item in knowledgeBase" :key="item.id" class="knowledge-item">
              <div class="knowledge-header">
                <span class="knowledge-title">{{ item.title }}</span>
                <el-tag size="small" type="info">{{ item.category }}</el-tag>
              </div>
              <p class="knowledge-desc">{{ item.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="report-detail">
        <div v-if="selectedReport" class="card report-content">
          <div class="report-header">
            <div class="report-header-info">
              <h3>{{ selectedReport.title }}</h3>
              <div class="report-meta-row">
                <span><el-icon><Clock /></el-icon> {{ selectedReport.date }}</span>
                <span><el-icon><User /></el-icon> {{ selectedReport.author }}</span>
              </div>
            </div>
            <div class="report-actions">
              <el-button size="small">
                <el-icon><Download /></el-icon>
                下载
              </el-button>
              <el-button size="small">
                <el-icon><Share /></el-icon>
                分享
              </el-button>
            </div>
          </div>

          <div class="report-body">
            <div class="report-section">
              <h4>执行摘要</h4>
              <p>本次检测于 {{ selectedReport.date }} 执行，通过多Agent协作系统完成网络故障的自动检测与根因分析。系统成功定位到接入交换机-2的端口故障，并自动生成了修复方案。</p>
            </div>

            <div class="report-section">
              <h4>故障信息</h4>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">故障类型</span>
                  <span class="value">端口CRC错误</span>
                </div>
                <div class="info-item">
                  <span class="label">严重程度</span>
                  <el-tag type="danger" size="small">高</el-tag>
                </div>
                <div class="info-item">
                  <span class="label">影响范围</span>
                  <span class="value">接入交换机-2 (acc-02)</span>
                </div>
                <div class="info-item">
                  <span class="label">持续时间</span>
                  <span class="value">约 45 分钟</span>
                </div>
              </div>
            </div>

            <div class="report-section">
              <h4>根因分析</h4>
              <div class="cause-diagram">
                <div class="cause-node root">
                  <span class="node-label">根因</span>
                  <span class="node-value">端口物理损坏</span>
                </div>
                <div class="cause-arrow">↓</div>
                <div class="cause-node symptom">
                  <span class="node-label">表象</span>
                  <span class="node-value">CRC错误率上升</span>
                </div>
                <div class="cause-arrow">↓</div>
                <div class="cause-node effect">
                  <span class="node-label">影响</span>
                  <span class="node-value">丢包率增加</span>
                </div>
              </div>
            </div>

            <div class="report-section">
              <h4>证据收集</h4>
              <el-table :data="evidenceData" size="small">
                <el-table-column prop="type" label="类型" width="100">
                  <template #default="{ row }">
                    <el-tag size="small">{{ row.type }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="source" label="来源" width="120" />
                <el-table-column prop="timestamp" label="时间" width="150" />
                <el-table-column prop="description" label="描述" />
              </el-table>
            </div>

            <div class="report-section">
              <h4>修复措施</h4>
              <div class="fix-steps">
                <div class="fix-step completed">
                  <div class="step-number">1</div>
                  <div class="step-content">
                    <span class="step-title">端口重启</span>
                    <span class="step-status">已完成</span>
                  </div>
                </div>
                <div class="fix-step completed">
                  <div class="step-number">2</div>
                  <div class="step-content">
                    <span class="step-title">配置验证</span>
                    <span class="step-status">已完成</span>
                  </div>
                </div>
                <div class="fix-step pending">
                  <div class="step-number">3</div>
                  <div class="step-content">
                    <span class="step-title">硬件更换</span>
                    <span class="step-status">待执行</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="report-section">
              <h4>建议与预防</h4>
              <ul class="recommendations">
                <li>建议更换故障端口对应的网线，使用Cat6A屏蔽线缆</li>
                <li>增加端口CRC错误的监控告警阈值，提前预警</li>
                <li>定期执行端口健康检查，建立基线数据</li>
                <li>考虑将该端口配置为冗余端口，自动切换</li>
              </ul>
            </div>
          </div>
        </div>

        <div v-else class="card empty-detail">
          <el-icon :size="60" color="#374151"><Document /></el-icon>
          <p>选择一个报告查看详情</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Document, Folder, Collection, Clock, User, Download, Share } from '@element-plus/icons-vue'

const reportType = ref('all')
const selectedReport = ref(null)

const reports = ref([
  { id: 1, title: '接入交换机端口故障分析报告', date: '2024-01-15 10:30', size: '1.2MB', type: 'fault', author: '系统自动生成' },
  { id: 2, title: '核心网络健康检查周报', date: '2024-01-14 08:00', size: '2.5MB', type: 'health', author: '运维团队' },
  { id: 3, title: '防火墙策略变更记录', date: '2024-01-13 15:20', size: '856KB', type: 'change', author: 'admin' },
  { id: 4, title: '汇聚交换机带宽异常分析', date: '2024-01-12 09:15', size: '1.8MB', type: 'fault', author: '系统自动生成' },
  { id: 5, title: '网络设备固件升级报告', date: '2024-01-10 14:00', size: '3.2MB', type: 'change', author: '运维团队' }
])

const knowledgeBase = ref([
  { id: 1, title: 'CRC错误故障排查指南', category: '故障处理', description: '详细说明CRC错误的常见原因和排查步骤' },
  { id: 2, title: '交换机端口基础知识', category: '技术文档', description: '交换机端口类型、速率和工作模式说明' },
  { id: 3, title: '网络冗余设计最佳实践', category: '架构设计', description: 'STP、RSTP、MSTP配置和优化建议' }
])

const evidenceData = ref([
  { type: 'Syslog', source: 'acc-02', timestamp: '10:23:45', description: 'Interface GigabitEthernet0/1: CRC errors increased' },
  { type: 'SNMP', source: 'acc-02', timestamp: '10:24:00', description: 'ifInErrors: 23456 (normal: <100)' },
  { type: 'Metric', source: 'System', timestamp: '10:24:30', description: 'Packet loss: 5.2% (threshold: 1%)' }
])

const filteredReports = computed(() => {
  if (reportType.value === 'all') return reports.value
  return reports.value.filter(r => r.type === reportType.value)
})

const selectReport = (report) => {
  selectedReport.value = report
}

const getReportTypeColor = (type) => {
  const colors = { fault: 'danger', health: 'success', change: 'warning' }
  return colors[type] || 'info'
}

const getReportTypeName = (type) => {
  const names = { fault: '故障', health: '健康', change: '变更' }
  return names[type] || '其他'
}

const generateReport = () => {
  console.log('Generating new report...')
}
</script>

<style lang="scss" scoped>
.report-view {
  height: 100%;
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

.report-container {
  flex: 1;
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 20px;
  min-height: 0;
}

.report-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-filters {
  margin-bottom: 16px;
}

.reports {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.report-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(0, 0, 0, 0.3);
  }

  &.active {
    background: rgba(0, 242, 254, 0.1);
    border: 1px solid rgba(0, 242, 254, 0.3);
  }
}

.report-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(79, 172, 254, 0.1);
  color: var(--secondary-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.report-info {
  flex: 1;

  .report-title {
    display: block;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 2px;
  }

  .report-meta {
    font-size: 11px;
    color: var(--text-muted);
  }
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 250px;
  overflow-y: auto;
}

.knowledge-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.knowledge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.knowledge-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.knowledge-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.4;
}

.report-detail {
  overflow-y: auto;
}

.report-content {
  min-height: 100%;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;

  h3 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
  }
}

.report-meta-row {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-muted);

  span {
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

.report-actions {
  display: flex;
  gap: 8px;
}

.report-body {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.report-section {
  h4 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-color);
  }

  p {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;

  .label {
    display: block;
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 4px;
  }

  .value {
    font-size: 13px;
    color: var(--text-primary);
    font-weight: 500;
  }
}

.cause-diagram {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
}

.cause-node {
  padding: 12px 24px;
  border-radius: 8px;
  text-align: center;

  .node-label {
    display: block;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
  }

  .node-value {
    font-size: 13px;
    font-weight: 500;
  }

  &.root {
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid rgba(239, 68, 68, 0.3);
    .node-label { color: var(--danger-color); }
    .node-value { color: var(--danger-color); }
  }

  &.symptom {
    background: rgba(245, 158, 11, 0.2);
    border: 1px solid rgba(245, 158, 11, 0.3);
    .node-label { color: var(--warning-color); }
    .node-value { color: var(--warning-color); }
  }

  &.effect {
    background: rgba(79, 172, 254, 0.2);
    border: 1px solid rgba(79, 172, 254, 0.3);
    .node-label { color: var(--secondary-color); }
    .node-value { color: var(--secondary-color); }
  }
}

.cause-arrow {
  color: var(--text-muted);
  font-size: 18px;
}

.fix-steps {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.fix-step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;

  .step-number {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--text-muted);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
  }

  .step-content {
    flex: 1;

    .step-title {
      display: block;
      font-size: 13px;
      color: var(--text-primary);
      margin-bottom: 2px;
    }

    .step-status {
      font-size: 11px;
      color: var(--text-muted);
    }
  }

  &.completed .step-number {
    background: var(--success-color);
  }

  &.pending .step-number {
    background: var(--warning-color);
  }
}

.recommendations {
  list-style: none;
  padding: 0;

  li {
    position: relative;
    padding-left: 20px;
    margin-bottom: 10px;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;

    &::before {
      content: '•';
      position: absolute;
      left: 0;
      color: var(--primary-color);
    }
  }
}

.empty-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;

  p {
    margin-top: 16px;
    font-size: 14px;
    color: var(--text-muted);
  }
}
</style>
