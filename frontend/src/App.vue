<template>
  <div class="app-container">
    <aside class="sidebar">
      <div class="logo">
        <div class="logo-icon">
          <svg viewBox="0 0 40 40" fill="none">
            <circle cx="20" cy="20" r="18" stroke="url(#grad1)" stroke-width="2"/>
            <path d="M12 20h16M20 12v16" stroke="url(#grad1)" stroke-width="2" stroke-linecap="round"/>
            <circle cx="20" cy="20" r="6" fill="url(#grad1)" opacity="0.3"/>
            <defs>
              <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#00f2fe"/>
                <stop offset="100%" style="stop-color:#4facfe"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div class="logo-text">
          <span class="title">NetAgent</span>
          <span class="subtitle">智能运维系统</span>
        </div>
      </div>
      
      <nav class="nav-menu">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path" 
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
        >
          <component :is="item.icon" class="nav-icon" />
          <span>{{ item.name }}</span>
        </router-link>
      </nav>

      <div class="agent-status">
        <div class="status-title">Agent 状态</div>
        <div class="status-list">
          <div v-for="agent in agentStore.agents" :key="agent.name" class="status-item">
            <span class="status-dot" :class="agent.status"></span>
            <span class="agent-name">{{ agent.name }}</span>
          </div>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <header class="top-bar">
        <div class="page-title">{{ currentTitle }}</div>
        <div class="top-actions">
          <el-button type="primary" @click="startDetection" :loading="agentStore.isDetecting">
            <el-icon><Monitor /></el-icon>
            开始检测
          </el-button>
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </header>

      <div class="content-area">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAgentStore } from '@/stores/agent'
import { Monitor, Refresh, Connection, DataAnalysis, Operation, Document } from '@element-plus/icons-vue'

const route = useRoute()
const agentStore = useAgentStore()

const menuItems = [
  { path: '/', name: '网络拓扑', icon: Connection },
  { path: '/dashboard', name: '监控仪表盘', icon: DataAnalysis },
  { path: '/detection', name: '故障检测', icon: Monitor },
  { path: '/execution', name: '执行控制', icon: Operation },
  { path: '/report', name: '报告中心', icon: Document }
]

const currentTitle = computed(() => {
  const item = menuItems.find(m => m.path === route.path)
  return item ? item.name : ''
})

const startDetection = () => {
  agentStore.startDetection()
}

const refreshData = () => {
  agentStore.fetchStatus()
}
</script>

<style lang="scss" scoped>
.app-container {
  display: flex;
  height: 100vh;
  background: #0a0e1a;
  color: #e4e7ed;
}

.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #111827 0%, #0d1117 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  padding: 20px 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.logo-icon {
  width: 40px;
  height: 40px;
  
  svg {
    width: 100%;
    height: 100%;
  }
}

.logo-text {
  display: flex;
  flex-direction: column;
  
  .title {
    font-size: 18px;
    font-weight: 700;
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .subtitle {
    font-size: 11px;
    color: #6b7280;
    letter-spacing: 1px;
  }
}

.nav-menu {
  flex: 1;
  padding: 20px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 10px;
  color: #9ca3af;
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;

  .nav-icon {
    width: 20px;
    height: 20px;
  }

  &:hover {
    background: rgba(79, 172, 254, 0.1);
    color: #4facfe;
  }

  &.active {
    background: linear-gradient(135deg, rgba(0, 242, 254, 0.15) 0%, rgba(79, 172, 254, 0.1) 100%);
    color: #00f2fe;
    border: 1px solid rgba(0, 242, 254, 0.3);
    
    .nav-icon {
      color: #00f2fe;
    }
  }
}

.agent-status {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  margin-top: auto;
}

.status-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #6b7280;
  margin-bottom: 12px;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  
  &.active {
    background: #10b981;
    box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
  }
  
  &.idle {
    background: #6b7280;
  }
  
  &.error {
    background: #ef4444;
    box-shadow: 0 0 8px rgba(239, 68, 68, 0.6);
  }
  
  &.running {
    background: #f59e0b;
    box-shadow: 0 0 8px rgba(245, 158, 11, 0.6);
    animation: pulse 1.5s infinite;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-bar {
  height: 64px;
  background: rgba(17, 24, 39, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #f3f4f6;
}

.top-actions {
  display: flex;
  gap: 12px;
}

.content-area {
  flex: 1;
  padding: 24px;
  overflow: auto;
}
</style>
