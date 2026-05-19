import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAgentStore = defineStore('agent', () => {
  const agents = ref([
    { name: '数据采集Agent', status: 'idle', lastUpdate: null, description: '收集网络日志和指标数据' },
    { name: '日志解析Agent', status: 'idle', lastUpdate: null, description: '解析syslog和SNMP信息' },
    { name: '拓扑感知Agent', status: 'idle', lastUpdate: null, description: '构建和维护网络拓扑' },
    { name: '推理Agent', status: 'idle', lastUpdate: null, description: '执行根因分析和推理' },
    { name: '执行Agent', status: 'idle', lastUpdate: null, description: '执行自愈操作' }
  ])

  const isDetecting = ref(false)
  const detectionProgress = ref(0)
  const currentTask = ref(null)

  const networkTopology = ref({
    nodes: [
      { id: 'core-01', name: '核心交换机', type: 'core', x: 400, y: 200 },
      { id: 'dist-01', name: '汇聚交换机-A', type: 'distribution', x: 250, y: 320 },
      { id: 'dist-02', name: '汇聚交换机-B', type: 'distribution', x: 550, y: 320 },
      { id: 'acc-01', name: '接入交换机-1', type: 'access', x: 120, y: 440 },
      { id: 'acc-02', name: '接入交换机-2', type: 'access', x: 250, y: 440 },
      { id: 'acc-03', name: '接入交换机-3', type: 'access', x: 380, y: 440 },
      { id: 'acc-04', name: '接入交换机-4', type: 'access', x: 510, y: 440 },
      { id: 'acc-05', name: '接入交换机-5', type: 'access', x: 640, y: 440 },
      { id: 'fw-01', name: '防火墙', type: 'firewall', x: 400, y: 80 },
      { id: 'router-01', name: '边界路由器', type: 'router', x: 400, y: 20 }
    ],
    links: [
      { source: 'router-01', target: 'fw-01', bandwidth: '10G' },
      { source: 'fw-01', target: 'core-01', bandwidth: '10G' },
      { source: 'core-01', target: 'dist-01', bandwidth: '10G' },
      { source: 'core-01', target: 'dist-02', bandwidth: '10G' },
      { source: 'dist-01', target: 'acc-01', bandwidth: '1G' },
      { source: 'dist-01', target: 'acc-02', bandwidth: '1G' },
      { source: 'dist-01', target: 'acc-03', bandwidth: '1G' },
      { source: 'dist-02', target: 'acc-03', bandwidth: '1G' },
      { source: 'dist-02', target: 'acc-04', bandwidth: '1G' },
      { source: 'dist-02', target: 'acc-05', bandwidth: '1G' }
    ],
    alerts: []
  })

  const detectionResults = ref({
    detected: false,
    faultType: null,
    severity: null,
    evidence: [],
    rootCause: null,
    confidence: 0,
    timestamp: null
  })

  const reasoningChain = ref([])
  const repairActions = ref([])

  const fetchStatus = async () => {
    try {
      const response = await axios.get('/api/status')
      if (response.data) {
        updateFromResponse(response.data)
      }
    } catch (error) {
      console.log('Using simulated data')
    }
  }

  const updateFromResponse = (data) => {
    if (data.agents) {
      agents.value = data.agents
    }
    if (data.topology) {
      networkTopology.value = data.topology
    }
  }

  const startDetection = async () => {
    isDetecting.value = true
    detectionProgress.value = 0
    reasoningChain.value = []

    const steps = [
      { agent: '数据采集Agent', action: '正在采集网络日志和指标...', duration: 1500 },
      { agent: '日志解析Agent', action: '正在解析syslog和SNMP数据...', duration: 1200 },
      { agent: '拓扑感知Agent', action: '正在分析网络拓扑关联...', duration: 1000 },
      { agent: '推理Agent', action: '正在执行根因推理...', duration: 2000 },
      { agent: '执行Agent', action: '正在生成自愈方案...', duration: 800 }
    ]

    for (let i = 0; i < steps.length; i++) {
      const step = steps[i]
      const agentIndex = agents.value.findIndex(a => a.name === step.agent)
      
      if (agentIndex !== -1) {
        agents.value[agentIndex].status = 'running'
      }
      
      reasoningChain.value.push({
        step: i + 1,
        agent: step.agent,
        action: step.action,
        status: 'running',
        timestamp: new Date().toISOString(),
        details: []
      })

      await new Promise(resolve => setTimeout(resolve, step.duration))
      
      if (agentIndex !== -1) {
        agents.value[agentIndex].status = 'active'
        agents.value[agentIndex].lastUpdate = new Date().toISOString()
      }
      
      reasoningChain.value[i].status = 'completed'
      detectionProgress.value = ((i + 1) / steps.length) * 100
    }

    await simulateDetectionResult()
    
    isDetecting.value = false
  }

  const simulateDetectionResult = async () => {
    const faultTypes = [
      {
        type: '端口CRC错误',
        severity: 'high',
        rootCause: {
          device: 'acc-02',
          deviceName: '接入交换机-2',
          port: 'GigabitEthernet0/1',
          issue: 'CRC错误率异常上升',
          evidence: [
            { type: 'syslog', content: '%Interface GigabitEthernet0/1: CRC errors increased from 0.01% to 2.3%', timestamp: '2024-01-15T10:23:45Z' },
            { type: 'snmp', content: 'ifInErrors: 23456 (normal: <100)', timestamp: '2024-01-15T10:24:00Z' },
            { type: 'metric', content: 'Packet loss: 5.2% (threshold: 1%)', timestamp: '2024-01-15T10:24:30Z' }
          ]
        },
        repairAction: {
          command: 'interface GigabitEthernet0/1\nshutdown\nno shutdown',
          description: '重启故障端口'
        }
      }
    ]

    const fault = faultTypes[0]
    
    detectionResults.value = {
      detected: true,
      faultType: fault.type,
      severity: fault.severity,
      evidence: fault.rootCause.evidence,
      rootCause: fault.rootCause,
      confidence: 0.92,
      timestamp: new Date().toISOString()
    }

    networkTopology.value.alerts = [
      {
        nodeId: fault.rootCause.device,
        type: 'error',
        message: fault.type
      }
    ]

    reasoningChain.value.push({
      step: 6,
      agent: '推理Agent',
      action: '故障定位完成',
      status: 'completed',
      timestamp: new Date().toISOString(),
      details: [
        `故障类型: ${fault.type}`,
        `严重程度: ${fault.severity}`,
        `置信度: ${(fault.confidence * 100).toFixed(0)}%`,
        `根因设备: ${fault.rootCause.deviceName}`,
        `根因端口: ${fault.rootCause.port}`
      ]
    })

    repairActions.value = [
      {
        id: 1,
        action: '重启端口',
        command: fault.repairAction.command,
        status: 'pending',
        description: fault.repairAction.description,
        autoExecute: true
      },
      {
        id: 2,
        action: '隔离终端',
        command: 'interface GigabitEthernet0/1\nswitchport port-security maximum 0',
        status: 'pending',
        description: '禁用问题端口防止影响网络',
        autoExecute: false
      }
    ]
  }

  const executeRepair = async (actionId) => {
    const action = repairActions.value.find(a => a.id === actionId)
    if (action) {
      action.status = 'running'
      
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      action.status = 'completed'
      action.executedAt = new Date().toISOString()
    }
  }

  const executeAll = async () => {
    for (const action of repairActions.value.filter(a => a.autoExecute)) {
      await executeRepair(action.id)
    }
  }

  const clearAlerts = () => {
    networkTopology.value.alerts = []
    detectionResults.value = {
      detected: false,
      faultType: null,
      severity: null,
      evidence: [],
      rootCause: null,
      confidence: 0,
      timestamp: null
    }
    reasoningChain.value = []
    repairActions.value = []
    agents.value.forEach(a => a.status = 'idle')
  }

  return {
    agents,
    isDetecting,
    detectionProgress,
    currentTask,
    networkTopology,
    detectionResults,
    reasoningChain,
    repairActions,
    fetchStatus,
    startDetection,
    executeRepair,
    executeAll,
    clearAlerts
  }
})
