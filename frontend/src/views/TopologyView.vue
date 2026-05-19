<template>
  <div class="topology-view">
    <div class="view-header">
      <div class="header-left">
        <h2>网络拓扑视图</h2>
        <p class="subtitle">实时展示网络设备连接状态和故障告警</p>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <span class="stat-value">{{ agentStore.networkTopology.nodes.length }}</span>
          <span class="stat-label">网络设备</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ agentStore.networkTopology.links.length }}</span>
          <span class="stat-label">链路连接</span>
        </div>
        <div class="stat-item alert">
          <span class="stat-value">{{ agentStore.networkTopology.alerts.length }}</span>
          <span class="stat-label">活跃告警</span>
        </div>
      </div>
    </div>

    <div class="topology-container">
      <div class="topology-canvas" ref="canvasRef">
        <svg class="topology-svg" :viewBox="`0 0 ${canvasWidth} ${canvasHeight}`">
          <defs>
            <linearGradient id="linkGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#4facfe"/>
              <stop offset="100%" style="stop-color:#00f2fe"/>
            </linearGradient>
            <linearGradient id="linkGradientAlert" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#ef4444"/>
              <stop offset="100%" style="stop-color:#f59e0b"/>
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          <g class="links">
            <g v-for="(link, index) in agentStore.networkTopology.links" :key="`link-${index}`">
              <line
                :x1="getNodePosition(link.source).x"
                :y1="getNodePosition(link.source).y"
                :x2="getNodePosition(link.target).x"
                :y2="getNodePosition(link.target).y"
                :stroke="isLinkAffected(link) ? 'url(#linkGradientAlert)' : 'url(#linkGradient)'"
                stroke-width="2"
                :stroke-dasharray="isLinkAffected(link) ? '5,5' : 'none'"
                :class="{ 'alert-link': isLinkAffected(link) }"
              />
              <text
                :x="(getNodePosition(link.source).x + getNodePosition(link.target).x) / 2"
                :y="(getNodePosition(link.source).y + getNodePosition(link.target).y) / 2 - 8"
                class="link-label"
                fill="#6b7280"
                font-size="10"
              >
                {{ link.bandwidth }}
              </text>
            </g>
          </g>

          <g class="nodes">
            <g
              v-for="node in agentStore.networkTopology.nodes"
              :key="node.id"
              :transform="`translate(${node.x}, ${node.y})`"
              class="node-group"
              @click="selectNode(node)"
              :class="{ selected: selectedNode?.id === node.id, alert: hasAlert(node.id) }"
            >
              <circle
                r="32"
                :fill="getNodeFill(node)"
                :stroke="getNodeStroke(node)"
                stroke-width="2"
                :filter="hasAlert(node.id) ? 'url(#glow)' : 'none'"
              />
              <circle r="26" fill="rgba(17, 24, 39, 0.8)"/>
              <text y="5" text-anchor="middle" :fill="getNodeTextColor(node)" font-size="18">
                {{ getNodeIcon(node.type) }}
              </text>
              <text y="52" text-anchor="middle" fill="#9ca3af" font-size="11" font-weight="500">
                {{ node.name }}
              </text>
              <text y="65" text-anchor="middle" fill="#6b7280" font-size="9">
                {{ node.id }}
              </text>
            </g>
          </g>
        </svg>
      </div>

      <div class="topology-sidebar">
        <div class="card">
          <div class="card-header">
            <h3><el-icon><InfoFilled /></el-icon> 设备详情</h3>
          </div>
          <div v-if="selectedNode" class="node-details">
            <div class="detail-row">
              <span class="label">设备名称</span>
              <span class="value">{{ selectedNode.name }}</span>
            </div>
            <div class="detail-row">
              <span class="label">设备ID</span>
              <span class="value mono">{{ selectedNode.id }}</span>
            </div>
            <div class="detail-row">
              <span class="label">设备类型</span>
              <el-tag :type="getTypeColor(selectedNode.type)" size="small">
                {{ getTypeName(selectedNode.type) }}
              </el-tag>
            </div>
            <div class="detail-row">
              <span class="label">连接状态</span>
              <el-tag :type="hasAlert(selectedNode.id) ? 'danger' : 'success'" size="small">
                {{ hasAlert(selectedNode.id) ? '异常' : '正常' }}
              </el-tag>
            </div>
            <div class="detail-row">
              <span class="label">CPU使用率</span>
              <el-progress :percentage="Math.random() * 40 + 20" :color="getProgressColor" :show-text="true" :width="80"/>
            </div>
            <div class="detail-row">
              <span class="label">内存使用率</span>
              <el-progress :percentage="Math.random() * 30 + 40" :color="getProgressColor" :show-text="true" :width="80"/>
            </div>
          </div>
          <div v-else class="no-selection">
            <el-icon :size="40" color="#6b7280"><<Monitor /></el-icon>
            <p>点击设备查看详情</p>
          </div>
        </div>

        <div class="card legend-card">
          <div class="card-header">
            <h3><el-icon><Collection /></el-icon> 图例</h3>
          </div>
          <div class="legend-items">
            <div class="legend-item">
              <span class="legend-icon core">C</span>
              <span>核心层</span>
            </div>
            <div class="legend-item">
              <span class="legend-icon dist">D</span>
              <span>汇聚层</span>
            </div>
            <div class="legend-item">
              <span class="legend-icon acc">A</span>
              <span>接入层</span>
            </div>
            <div class="legend-item">
              <span class="legend-icon fw">F</span>
              <span>防火墙</span>
            </div>
            <div class="legend-item">
              <span class="legend-icon router">R</span>
              <span>路由器</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAgentStore } from '@/stores/agent'
import { InfoFilled, Collection, Monitor } from '@element-plus/icons-vue'

const agentStore = useAgentStore()

const canvasRef = ref(null)
const canvasWidth = 800
const canvasHeight = 500
const selectedNode = ref(null)

const getNodePosition = (nodeId) => {
  const node = agentStore.networkTopology.nodes.find(n => n.id === nodeId)
  return node ? { x: node.x, y: node.y } : { x: 0, y: 0 }
}

const getNodeIcon = (type) => {
  const icons = {
    core: '🔷',
    distribution: '🔶',
    access: '🔹',
    firewall: '🛡️',
    router: '🌐'
  }
  return icons[type] || '📦'
}

const getNodeFill = (node) => {
  if (hasAlert(node.id)) {
    return 'rgba(239, 68, 68, 0.2)'
  }
  return 'rgba(79, 172, 254, 0.1)'
}

const getNodeStroke = (node) => {
  if (hasAlert(node.id)) {
    return '#ef4444'
  }
  if (selectedNode.value?.id === node.id) {
    return '#00f2fe'
  }
  return '#4facfe'
}

const getNodeTextColor = (node) => {
  if (hasAlert(node.id)) {
    return '#ef4444'
  }
  return '#4facfe'
}

const hasAlert = (nodeId) => {
  return agentStore.networkTopology.alerts.some(a => a.nodeId === nodeId)
}

const isLinkAffected = (link) => {
  return hasAlert(link.source) || hasAlert(link.target)
}

const getTypeName = (type) => {
  const names = {
    core: '核心交换机',
    distribution: '汇聚交换机',
    access: '接入交换机',
    firewall: '防火墙',
    router: '路由器'
  }
  return names[type] || '未知'
}

const getTypeColor = (type) => {
  const colors = {
    core: 'primary',
    distribution: 'success',
    access: 'info',
    firewall: 'warning',
    router: ''
  }
  return colors[type] || 'info'
}

const getProgressColor = (percentage) => {
  if (percentage < 50) return '#10b981'
  if (percentage < 80) return '#f59e0b'
  return '#ef4444'
}

const selectNode = (node) => {
  selectedNode.value = node
}
</script>

<style lang="scss" scoped>
.topology-view {
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

.header-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;

  .stat-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--primary-color);
  }

  .stat-label {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  &.alert .stat-value {
    color: var(--danger-color);
  }
}

.topology-container {
  flex: 1;
  display: flex;
  gap: 20px;
  min-height: 0;
}

.topology-canvas {
  flex: 1;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      radial-gradient(circle at 20% 30%, rgba(0, 242, 254, 0.03) 0%, transparent 50%),
      radial-gradient(circle at 80% 70%, rgba(79, 172, 254, 0.03) 0%, transparent 50%);
    pointer-events: none;
  }
}

.topology-svg {
  width: 100%;
  height: 100%;

  .node-group {
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      transform: scale(1.05);
      
      circle:first-child {
        stroke-width: 3;
      }
    }

    &.selected {
      transform: scale(1.08);
    }

    &.alert {
      animation: alertPulse 2s infinite;
    }
  }

  .alert-link {
    animation: dashMove 0.5s linear infinite;
  }

  .link-label {
    pointer-events: none;
    font-family: 'JetBrains Mono', monospace;
  }
}

@keyframes alertPulse {
  0%, 100% {
    filter: drop-shadow(0 0 8px rgba(239, 68, 68, 0.6));
  }
  50% {
    filter: drop-shadow(0 0 16px rgba(239, 68, 68, 0.8));
  }
}

@keyframes dashMove {
  to {
    stroke-dashoffset: -10;
  }
}

.topology-sidebar {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.node-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .label {
    font-size: 12px;
    color: var(--text-muted);
  }

  .value {
    font-size: 13px;
    color: var(--text-primary);
    font-weight: 500;
  }
}

.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-muted);
  text-align: center;

  p {
    margin-top: 12px;
    font-size: 13px;
  }
}

.legend-card {
  flex: 1;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.legend-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;

  &.core {
    background: rgba(79, 172, 254, 0.2);
    color: #4facfe;
    border: 1px solid rgba(79, 172, 254, 0.3);
  }

  &.dist {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
  }

  &.acc {
    background: rgba(139, 92, 246, 0.2);
    color: #8b5cf6;
    border: 1px solid rgba(139, 92, 246, 0.3);
  }

  &.fw {
    background: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.3);
  }

  &.router {
    background: rgba(236, 72, 153, 0.2);
    color: #ec4899;
    border: 1px solid rgba(236, 72, 153, 0.3);
  }
}
</style>
