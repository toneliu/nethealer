<template>
  <div class="detection-view">
    <div class="view-header">
      <div class="header-left">
        <h2>故障检测与根因分析</h2>
        <p class="subtitle">多Agent协作推理，自动定位网络故障根因</p>
      </div>
      <div class="header-actions">
        <el-button @click="agentStore.clearAlerts" :disabled="!agentStore.detectionResults.detected">
          <el-icon><Delete /></el-icon>
          清除结果
        </el-button>
      </div>
    </div>

    <div class="detection-container">
      <div class="reasoning-panel">
        <div class="panel-header">
          <h3><el-icon><Connection /></el-icon> 推理过程</h3>
          <el-progress 
            v-if="agentStore.isDetecting" 
            :percentage="Math.round(agentStore.detectionProgress)" 
            :color="progressColor"
            :width="60"
            type="circle"
          />
        </div>

        <div class="agent-pipeline">
          <div 
            v-for="(step, index) in agentStore.reasoningChain" 
            :key="index"
            class="pipeline-step"
            :class="step.status"
          >
            <div class="step-indicator">
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-line" v-if="index < agentStore.reasoningChain.length - 1"></div>
            </div>
            <div class="step-content">
              <div class="step-header">
                <span class="step-agent">{{ step.agent }}</span>
                <el-tag 
                  :type="step.status === 'completed' ? 'success' : 'warning'" 
                  size="small"
                >
                  {{ step.status === 'completed' ? '完成' : '执行中' }}
                </el-tag>
              </div>
              <div class="step-action">{{ step.action }}</div>
              <div v-if="step.details && step.details.length" class="step-details">
                <div v-for="(detail, dIndex) in step.details" :key="dIndex" class="detail-item">
                  <el-icon><ArrowRight /></el-icon>
                  <span>{{ detail }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!agentStore.reasoningChain.length && !agentStore.isDetecting" class="empty-state">
          <el-icon :size="60" color="#374151"><VideoPlay /></el-icon>
          <p>点击"开始检测"启动故障分析</p>
        </div>
      </div>

      <div class="result-panel">
        <div v-if="agentStore.detectionResults.detected" class="fault-analysis">
          <div class="fault-header" :class="agentStore.detectionResults.severity">
            <div class="fault-icon">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="fault-info">
              <h4>检测到故障</h4>
              <span class="fault-type">{{ agentStore.detectionResults.faultType }}</span>
            </div>
            <div class="confidence">
              <span class="confidence-label">置信度</span>
              <span class="confidence-value">{{ (agentStore.detectionResults.confidence * 100).toFixed(0) }}%</span>
            </div>
          </div>

          <div class="root-cause-card">
            <div class="card-header">
              <h3><el-icon><Aim /></el-icon> 根因定位</h3>
            </div>
            <div class="root-cause-content">
              <div class="cause-item">
                <span class="cause-label">设备</span>
                <span class="cause-value device">{{ agentStore.detectionResults.rootCause?.deviceName }}</span>
                <el-tag size="small" type="danger">{{ agentStore.detectionResults.rootCause?.device }}</el-tag>
              </div>
              <div class="cause-item">
                <span class="cause-label">端口</span>
                <span class="cause-value mono">{{ agentStore.detectionResults.rootCause?.port }}</span>
              </div>
              <div class="cause-item">
                <span class="cause-label">问题</span>
                <span class="cause-value">{{ agentStore.detectionResults.rootCause?.issue }}</span>
              </div>
            </div>
          </div>

          <div class="evidence-card">
            <div class="card-header">
              <h3><el-icon><Document /></el-icon> 证据链</h3>
            </div>
            <div class="evidence-list">
              <div v-for="(evidence, index) in agentStore.detectionResults.evidence" :key="index" class="evidence-item">
                <div class="evidence-header">
                  <el-tag size="small" :type="getEvidenceTypeColor(evidence.type)">
                    {{ evidence.type.toUpperCase() }}
                  </el-tag>
                  <span class="evidence-time">{{ formatTime(evidence.timestamp) }}</span>
                </div>
                <div class="evidence-content mono">{{ evidence.content }}</div>
              </div>
            </div>
          </div>

          <div class="actions-card">
            <div class="card-header">
              <h3><el-icon><Tools /></el-icon> 修复建议</h3>
            </div>
            <div class="actions-list">
              <div v-for="action in agentStore.repairActions" :key="action.id" class="action-item">
                <div class="action-info">
                  <span class="action-name">{{ action.action }}</span>
                  <span class="action-desc">{{ action.description }}</span>
                </div>
                <div class="action-status">
                  <el-tag v-if="action.autoExecute" size="small" type="info">自动执行</el-tag>
                  <el-button 
                    size="small" 
                    type="primary"
                    :loading="action.status === 'running'"
                    :disabled="action.status === 'completed'"
                    @click="agentStore.executeRepair(action.id)"
                  >
                    {{ action.status === 'completed' ? '已执行' : '执行' }}
                  </el-button>
                </div>
              </div>
            </div>
            <div class="action-footer">
              <el-button type="primary" size="large" @click="agentStore.executeAll">
                <el-icon><VideoPlay /></el-icon>
                一键自动修复
              </el-button>
            </div>
          </div>
        </div>

        <div v-else class="no-fault">
          <div class="no-fault-icon">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>网络运行正常</h3>
          <p>未检测到故障，当前网络状态健康</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAgentStore } from '@/stores/agent'
import { Delete, Connection, ArrowRight, VideoPlay, Aim, Document, Tools } from '@element-plus/icons-vue'

const agentStore = useAgentStore()

const progressColor = computed(() => {
  const progress = agentStore.detectionProgress
  if (progress < 30) return '#4facfe'
  if (progress < 70) return '#f59e0b'
  return '#10b981'
})

const getEvidenceTypeColor = (type) => {
  const colors = {
    syslog: 'primary',
    snmp: 'success',
    metric: 'warning'
  }
  return colors[type] || 'info'
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}
</script>

<style lang="scss" scoped>
.detection-view {
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

.detection-container {
  flex: 1;
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 20px;
  min-height: 0;
}

.reasoning-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-color);

    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
  }
}

.agent-pipeline {
  flex: 1;
  overflow-y: auto;
}

.pipeline-step {
  display: flex;
  gap: 16px;
  opacity: 0;
  animation: slideIn 0.4s ease forwards;

  &.running {
    .step-number {
      background: var(--warning-color);
      box-shadow: 0 0 12px rgba(245, 158, 11, 0.5);
      animation: pulse 1.5s infinite;
    }
  }

  &.completed {
    .step-number {
      background: var(--success-color);
    }

    .step-line {
      background: var(--success-color);
    }
  }
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--text-muted);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.step-line {
  width: 2px;
  flex: 1;
  min-height: 40px;
  background: var(--border-color);
  margin: 8px 0;
}

.step-content {
  flex: 1;
  padding-bottom: 20px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.step-agent {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.step-action {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.step-details {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 10px 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;

  &:last-child {
    margin-bottom: 0;
  }

  .el-icon {
    color: var(--primary-color);
    font-size: 10px;
  }
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  text-align: center;

  p {
    margin-top: 16px;
    font-size: 14px;
  }
}

.result-panel {
  overflow-y: auto;
}

.fault-analysis {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.fault-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;

  &.high {
    border-color: rgba(239, 68, 68, 0.5);
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);

    .fault-icon {
      color: var(--danger-color);
    }
  }

  &.medium {
    border-color: rgba(245, 158, 11, 0.5);
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);

    .fault-icon {
      color: var(--warning-color);
    }
  }
}

.fault-icon {
  width: 48px;
  height: 48px;
  flex-shrink: 0;

  svg {
    width: 100%;
    height: 100%;
  }
}

.fault-info {
  flex: 1;

  h4 {
    font-size: 12px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
  }

  .fault-type {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.confidence {
  text-align: center;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;

  .confidence-label {
    display: block;
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 4px;
  }

  .confidence-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--success-color);
  }
}

.root-cause-card, .evidence-card, .actions-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
}

.root-cause-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cause-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;

  .cause-label {
    font-size: 12px;
    color: var(--text-muted);
    width: 50px;
  }

  .cause-value {
    flex: 1;
    font-size: 14px;
    color: var(--text-primary);

    &.device {
      font-weight: 600;
      color: var(--danger-color);
    }

    &.mono {
      font-family: 'JetBrains Mono', monospace;
      color: var(--secondary-color);
    }
  }
}

.evidence-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.evidence-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.evidence-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.evidence-time {
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-muted);
}

.evidence-content {
  font-size: 12px;
  color: var(--text-secondary);
  word-break: break-all;
  line-height: 1.5;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.action-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.action-info {
  .action-name {
    display: block;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 2px;
  }

  .action-desc {
    font-size: 12px;
    color: var(--text-muted);
  }
}

.action-footer {
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.no-fault {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
  text-align: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;

  .no-fault-icon {
    width: 80px;
    height: 80px;
    color: var(--success-color);
    margin-bottom: 20px;

    svg {
      width: 100%;
      height: 100%;
    }
  }

  h3 {
    font-size: 20px;
    color: var(--text-primary);
    margin-bottom: 8px;
  }

  p {
    font-size: 14px;
    color: var(--text-muted);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
