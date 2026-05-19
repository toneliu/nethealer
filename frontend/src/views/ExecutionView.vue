<template>
  <div class="execution-view">
    <div class="view-header">
      <div class="header-left">
        <h2>执行控制台</h2>
        <p class="subtitle">执行网络设备自愈命令和配置变更</p>
      </div>
    </div>

    <div class="execution-container">
      <div class="command-panel">
        <div class="card">
          <div class="card-header">
            <h3><el-icon><Terminal /></el-icon> 命令执行</h3>
          </div>
          <div class="command-input">
            <el-select v-model="selectedDevice" placeholder="选择设备" size="large">
              <el-option 
                v-for="node in agentStore.networkTopology.nodes" 
                :key="node.id" 
                :label="node.name" 
                :value="node.id" 
              />
            </el-select>
            <el-input
              v-model="command"
              placeholder="输入命令..."
              size="large"
              type="textarea"
              :rows="3"
              class="command-textarea"
            />
            <div class="command-actions">
              <el-button type="primary" size="large" @click="executeCommand" :loading="executing">
                <el-icon><VideoPlay /></el-icon>
                执行
              </el-button>
              <el-button size="large" @click="clearCommand">
                <el-icon><RefreshLeft /></el-icon>
                清空
              </el-button>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h3><el-icon><Document /></el-icon> 预设命令模板</h3>
          </div>
          <div class="command-templates">
            <div v-for="template in commandTemplates" :key="template.name" class="template-item">
              <div class="template-info">
                <span class="template-name">{{ template.name }}</span>
                <span class="template-desc">{{ template.description }}</span>
              </div>
              <el-button size="small" @click="applyTemplate(template)">
                <el-icon><TopRight /></el-icon>
                应用
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="output-panel">
        <div class="card terminal-card">
          <div class="card-header">
            <h3><el-icon><Screen /></el-icon> 执行输出</h3>
            <el-button size="small" @click="clearOutput">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
          </div>
          <div class="terminal-output" ref="terminalRef">
            <div v-for="(line, index) in outputLines" :key="index" class="output-line" :class="line.type">
              <span class="line-prefix">{{ getLinePrefix(line.type) }}</span>
              <span class="line-content">{{ line.content }}</span>
            </div>
            <div v-if="executing" class="output-line running">
              <span class="line-prefix">$</span>
              <span class="typing-cursor"></span>
            </div>
          </div>
        </div>

        <div class="card history-card">
          <div class="card-header">
            <h3><el-icon><Clock /></el-icon> 执行历史</h3>
          </div>
          <div class="history-list">
            <div v-for="(record, index) in executionHistory" :key="index" class="history-item">
              <div class="history-time">{{ record.time }}</div>
              <div class="history-content">
                <el-tag size="small" :type="record.success ? 'success' : 'danger'">
                  {{ record.success ? '成功' : '失败' }}
                </el-tag>
                <span class="history-command">{{ record.command }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useAgentStore } from '@/stores/agent'
import { Terminal, VideoPlay, RefreshLeft, Document, Screen, Delete, Clock, TopRight } from '@element-plus/icons-vue'

const agentStore = useAgentStore()

const selectedDevice = ref('')
const command = ref('')
const executing = ref(false)
const terminalRef = ref(null)
const outputLines = ref([])
const executionHistory = ref([
  { time: '10:24:32', command: 'show interfaces GigabitEthernet0/1', success: true },
  { time: '10:23:15', command: 'show spanning-tree', success: true },
  { time: '10:21:08', command: 'show mac address-table', success: true }
])

const commandTemplates = [
  { 
    name: '端口重启', 
    description: '关闭然后开启指定端口',
    command: 'interface GigabitEthernet0/1\nshutdown\nno shutdown'
  },
  { 
    name: '端口统计', 
    description: '查看端口流量和错误统计',
    command: 'show interfaces GigabitEthernet0/1\nshow interfaces GigabitEthernet0/1 statistics'
  },
  { 
    name: '配置备份', 
    description: '备份当前配置到TFTP服务器',
    command: 'copy running-config tftp://192.168.1.100/backup.cfg'
  },
  { 
    name: '端口隔离', 
    description: '禁用问题端口防止影响网络',
    command: 'interface GigabitEthernet0/1\nswitchport port-security maximum 0\nshutdown'
  }
]

const applyTemplate = (template) => {
  command.value = template.command
  if (template.name.includes('端口重启') || template.name.includes('端口隔离')) {
    selectedDevice.value = 'acc-02'
  }
}

const executeCommand = async () => {
  if (!command.value.trim()) return
  
  executing.value = true
  
  outputLines.value.push({
    type: 'command',
    content: `> ${command.value}`
  })
  
  await new Promise(resolve => setTimeout(resolve, 800))
  
  const outputs = [
    { type: 'info', content: 'Connecting to device...' },
    { type: 'success', content: 'Connection established.' },
    { type: 'output', content: 'Interface GigabitEthernet0/1 is up, line protocol is up' },
    { type: 'output', content: 'Hardware is Intel, address is 00a1.b2c3.d4e5' },
    { type: 'output', content: 'MTU 1500 bytes, BW 1000000 Kbit, DLY 10 usec' },
    { type: 'warning', content: 'CRC errors: 23456 (threshold exceeded)' },
    { type: 'info', content: 'Executing command...' },
    { type: 'success', content: 'Command executed successfully.' }
  ]
  
  for (const output of outputs) {
    await new Promise(resolve => setTimeout(resolve, 200))
    outputLines.value.push(output)
  }
  
  executionHistory.value.unshift({
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    command: command.value.split('\n')[0],
    success: true
  })
  
  executing.value = false
  
  await nextTick()
  if (terminalRef.value) {
    terminalRef.value.scrollTop = terminalRef.value.scrollHeight
  }
}

const clearCommand = () => {
  command.value = ''
  selectedDevice.value = ''
}

const clearOutput = () => {
  outputLines.value = []
}

const getLinePrefix = (type) => {
  const prefixes = {
    command: '$',
    info: 'i',
    success: '✓',
    warning: '!',
    error: '✗',
    output: '>',
    running: '>'
  }
  return prefixes[type] || '>'
}
</script>

<style lang="scss" scoped>
.execution-view {
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

.execution-container {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  min-height: 0;
}

.command-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.command-input {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.command-textarea {
  :deep(.el-textarea__inner) {
    font-family: 'JetBrains Mono', monospace;
    background: rgba(0, 0, 0, 0.3);
    border-color: var(--border-color);
    color: var(--text-primary);
    resize: none;

    &:focus {
      border-color: var(--primary-color);
    }
  }
}

.command-actions {
  display: flex;
  gap: 12px;
}

.command-templates {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.template-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  transition: background 0.2s;

  &:hover {
    background: rgba(0, 0, 0, 0.3);
  }
}

.template-info {
  .template-name {
    display: block;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 2px;
  }

  .template-desc {
    font-size: 11px;
    color: var(--text-muted);
  }
}

.output-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.terminal-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.terminal-output {
  flex: 1;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 8px;
  padding: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  overflow-y: auto;
  max-height: 300px;
}

.output-line {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 6px;
  line-height: 1.5;

  .line-prefix {
    width: 16px;
    flex-shrink: 0;
    color: var(--text-muted);
  }

  .line-content {
    color: var(--text-secondary);
  }

  &.command {
    color: var(--primary-color);
    
    .line-prefix {
      color: var(--primary-color);
    }
    
    .line-content {
      color: var(--primary-color);
    }
  }

  &.info {
    color: var(--secondary-color);
  }

  &.success {
    color: var(--success-color);
    
    .line-prefix {
      color: var(--success-color);
    }
  }

  &.warning {
    color: var(--warning-color);
    
    .line-prefix {
      color: var(--warning-color);
    }
  }

  &.error {
    color: var(--danger-color);
    
    .line-prefix {
      color: var(--danger-color);
    }
  }

  &.running {
    .typing-cursor {
      display: inline-block;
      width: 8px;
      height: 14px;
      background: var(--primary-color);
      animation: blink 1s infinite;
    }
  }
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.history-card {
  max-height: 250px;
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-color);

  &:last-child {
    border-bottom: none;
  }
}

.history-time {
  font-size: 11px;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.history-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.history-command {
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-secondary);
}
</style>
