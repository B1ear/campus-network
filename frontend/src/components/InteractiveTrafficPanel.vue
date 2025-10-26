<template>
  <div class="traffic-sim-panel">
    <h2 class="panel-title">🎮 交互式流量仿真</h2>
    <p class="panel-description">实时模拟网络流量传输 · 动态对比不同策略</p>

    <div v-if="!hasNetwork" class="empty-state">
      <div class="empty-icon">🌐</div>
      <h3>尚未配置网络</h3>
      <p>请先在"网络配置"页面生成并应用网络拓扑</p>
    </div>

    <div v-else class="sim-container">
      <!-- 控制面板 -->
      <div class="control-panel">
        <div class="control-card">
          <h3 class="control-title">⚙️ 仿真控制</h3>
          
          <div class="control-grid">
            <div class="control-group">
              <label>源节点</label>
              <select v-model.number="simConfig.source" :disabled="isRunning">
                <option v-for="node in availableNodes" :key="node" :value="node">
                  节点 {{ node }}
                </option>
              </select>
            </div>

            <div class="control-group">
              <label>目标节点</label>
              <select v-model.number="simConfig.target" :disabled="isRunning">
                <option v-for="node in availableNodes" :key="node" :value="node">
                  节点 {{ node }}
                </option>
              </select>
            </div>

            <div class="control-group">
              <label>流量速率 (单位/秒)</label>
              <input v-model.number="simConfig.flowRate" type="number" min="10" max="1000" step="10" :disabled="isRunning" />
            </div>

            <div class="control-group">
              <label>仿真速度</label>
              <select v-model="simConfig.speed" :disabled="isRunning">
                <option value="slow">慢速 (0.5x)</option>
                <option value="normal">正常 (1x)</option>
                <option value="fast">快速 (2x)</option>
              </select>
            </div>
          </div>

          <!-- 策略选择 -->
          <div class="strategy-selector">
            <h4>负载均衡策略</h4>
            <div class="strategy-options">
              <label class="strategy-option">
                <input type="radio" v-model="simConfig.strategy" value="single" :disabled="isRunning" />
                <span class="strategy-label">
                  <span class="strategy-icon">📍</span>
                  <span class="strategy-text">单路径</span>
                </span>
              </label>
              <label class="strategy-option">
                <input type="radio" v-model="simConfig.strategy" value="balanced" :disabled="isRunning" />
                <span class="strategy-label">
                  <span class="strategy-icon">⚖️</span>
                  <span class="strategy-text">负载均衡</span>
                </span>
              </label>
              <label class="strategy-option">
                <input type="radio" v-model="simConfig.strategy" value="congestion" :disabled="isRunning" />
                <span class="strategy-label">
                  <span class="strategy-icon">🚦</span>
                  <span class="strategy-text">拥塞避免</span>
                </span>
              </label>
            </div>
          </div>

          <!-- 控制按钮 -->
          <div class="control-buttons">
            <button @click="startSimulation" :disabled="isRunning" class="btn btn-primary">
              ▶️ 开始仿真
            </button>
            <button @click="pauseSimulation" :disabled="!isRunning || isPaused" class="btn btn-warning">
              ⏸️ 暂停
            </button>
            <button @click="resumeSimulation" :disabled="!isRunning || !isPaused" class="btn btn-success">
              ▶️ 继续
            </button>
            <button @click="stopSimulation" :disabled="!isRunning" class="btn btn-danger">
              ⏹️ 停止
            </button>
            <button @click="resetSimulation" class="btn btn-secondary">
              🔄 重置
            </button>
          </div>
        </div>

        <!-- 实时统计 -->
        <div class="stats-card">
          <h3 class="control-title">📊 实时统计</h3>
          
          <!-- 流量速率显示 -->
          <div v-if="simConfig._actualFlowRate" class="flow-rate-info">
            <div class="flow-rate-label">实际速率</div>
            <div class="flow-rate-value">
              {{ simConfig._actualFlowRate.toFixed(0) }} 
              <span class="flow-rate-unit">单位/秒</span>
            </div>
            <div v-if="simConfig._originalFlowRate" class="flow-rate-warning">
              ⚠️ 请求: {{ simConfig._originalFlowRate }} 单位/秒
            </div>
          </div>

          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-label">已传输</div>
              <div class="stat-value">{{ stats.totalTransferred.toFixed(0) }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">平均利用率</div>
              <div class="stat-value">{{ (stats.avgUtilization * 100).toFixed(1) }}%</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">活跃路径</div>
              <div class="stat-value">{{ stats.activePaths }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">拥塞链路</div>
              <div class="stat-value" :class="{ 'text-danger': stats.congestedLinks > 0 }">
                {{ stats.congestedLinks }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 可视化区域 -->
      <div class="visualization-area">
        <div class="network-canvas-container">
          <svg ref="svgCanvas" class="network-canvas" :width="canvasSize.width" :height="canvasSize.height">
            <!-- 定义箭头标记 -->
            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#666" />
              </marker>
              <marker id="arrowhead-flow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#4299e1" />
              </marker>
              <marker id="arrowhead-congestion" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#fc8181" />
              </marker>
            </defs>

            <!-- 绘制边 -->
            <g class="edges-layer">
              <g v-for="edge in visualEdges" :key="`edge-${edge.from}-${edge.to}`">
                <!-- 边线 -->
                <line
                  :x1="nodePositions[edge.from]?.x"
                  :y1="nodePositions[edge.from]?.y"
                  :x2="nodePositions[edge.to]?.x"
                  :y2="nodePositions[edge.to]?.y"
                  :stroke="getEdgeColor(edge)"
                  :stroke-width="getEdgeWidth(edge)"
                  :opacity="getEdgeOpacity(edge)"
                  :marker-end="getEdgeMarker(edge)"
                  class="network-edge"
                />
                <!-- 流量动画 -->
                <circle
                  v-if="edge.flowAnimation > 0"
                  :r="4"
                  fill="#4299e1"
                  class="flow-particle"
                >
                  <animateMotion
                    :dur="`${1 / simConfig.speed}s`"
                    repeatCount="indefinite"
                    :path="`M ${nodePositions[edge.from]?.x} ${nodePositions[edge.from]?.y} L ${nodePositions[edge.to]?.x} ${nodePositions[edge.to]?.y}`"
                  />
                </circle>
                <!-- 流量标签（带背景） -->
                <g v-if="edge.currentFlow > 0">
                  <rect
                    :x="(nodePositions[edge.from]?.x + nodePositions[edge.to]?.x) / 2 - 25"
                    :y="(nodePositions[edge.from]?.y + nodePositions[edge.to]?.y) / 2 - 20"
                    width="50"
                    height="16"
                    rx="3"
                    fill="white"
                    opacity="0.95"
                    stroke="#cbd5e0"
                    stroke-width="1"
                  />
                  <text
                    :x="(nodePositions[edge.from]?.x + nodePositions[edge.to]?.x) / 2"
                    :y="(nodePositions[edge.from]?.y + nodePositions[edge.to]?.y) / 2 - 8"
                    class="flow-label"
                    text-anchor="middle"
                  >
                    {{ edge.currentFlow.toFixed(0) }}/{{ edge.capacity }}
                  </text>
                </g>
              </g>
            </g>

            <!-- 绘制节点 -->
            <g class="nodes-layer">
              <g v-for="node in visualNodes" :key="`node-${node.id}`">
                <!-- 节点圆圈 -->
                <circle
                  :cx="nodePositions[node.id]?.x"
                  :cy="nodePositions[node.id]?.y"
                  :r="getNodeRadius(node)"
                  :fill="getNodeColor(node)"
                  :stroke="getNodeStroke(node)"
                  :stroke-width="getNodeStrokeWidth(node)"
                  class="network-node"
                  @click="selectNode(node.id)"
                />
                <!-- 节点标签 -->
                <text
                  :x="nodePositions[node.id]?.x"
                  :y="nodePositions[node.id]?.y + 5"
                  class="node-label"
                  text-anchor="middle"
                >
                  {{ node.id }}
                </text>
                <!-- 节点流量指示器 -->
                <text
                  v-if="node.throughput > 0"
                  :x="nodePositions[node.id]?.x"
                  :y="nodePositions[node.id]?.y - 35"
                  class="node-throughput"
                  text-anchor="middle"
                >
                  ↓{{ node.throughput.toFixed(0) }}
                </text>
              </g>
            </g>
          </svg>

          <!-- 图例 -->
          <div class="legend">
            <h4>图例</h4>
            <div class="legend-item">
              <div class="legend-color" style="background: #48bb78;"></div>
              <span>源节点</span>
            </div>
            <div class="legend-item">
              <div class="legend-color" style="background: #fc8181;"></div>
              <span>目标节点</span>
            </div>
            <div class="legend-item">
              <div class="legend-color" style="background: #4299e1;"></div>
              <span>活跃链路</span>
            </div>
            <div class="legend-item">
              <div class="legend-color" style="background: #f56565;"></div>
              <span>拥塞链路 (>80%)</span>
            </div>
          </div>
        </div>

        <!-- 路径信息 -->
        <div v-if="activePaths.length > 0" class="paths-info">
          <h4>🛣️ 活跃路径</h4>
          <div class="path-list">
            <div v-for="(path, idx) in activePaths" :key="idx" class="path-item">
              <div class="path-header">
                <span class="path-index" :style="{ background: pathColors[idx] }">{{ idx + 1 }}</span>
                <span class="path-route">{{ path.nodes.join(' → ') }}</span>
              </div>
              <div class="path-stats">
                <span>流量: {{ path.flow.toFixed(0) }}</span>
                <span>利用率: {{ (path.utilization * 100).toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Toast通知 -->
  <Toast 
    :message="toast.message" 
    :type="toast.type" 
    :show="toast.show" 
    @close="toast.show = false" 
  />
</template>

<script setup>
import { ref, computed, inject, onMounted, onUnmounted, watch, reactive } from 'vue'
import Toast from './Toast.vue'

const globalNetwork = inject('globalNetwork')
const hasNetwork = computed(() => globalNetwork.value !== null)

// 仿真配置
const simConfig = ref({
  source: 0,
  target: 5,
  flowRate: 100,
  speed: 1,
  strategy: 'balanced'
})

// 仿真状态
const isRunning = ref(false)
const isPaused = ref(false)
const stats = ref({
  totalTransferred: 0,
  avgUtilization: 0,
  activePaths: 0,
  congestedLinks: 0
})

// 可视化数据
const visualNodes = ref([])
const visualEdges = ref([])
const nodePositions = ref({})
const activePaths = ref([])
const canvasSize = ref({ width: 1000, height: 600 })

// 速度映射
const speedMap = {
  slow: 0.5,
  normal: 1,
  fast: 2
}

watch(() => simConfig.value.speed, (newSpeed) => {
  simConfig.value.speed = speedMap[newSpeed] || 1
})

// 可用节点
const availableNodes = computed(() => {
  if (!globalNetwork.value) return []
  return globalNetwork.value.nodes.map(n => n.id)
})

// 路径颜色
const pathColors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']

// Toast通知状态
const toast = reactive({
  show: false,
  message: '',
  type: 'error'
})

function showToast(message, type = 'info') {
  toast.message = message
  toast.type = type
  toast.show = true
}

// 动画循环
let animationId = null
let lastTime = 0

// 初始化可视化
const initVisualization = () => {
  if (!globalNetwork.value) return

  // 初始化节点
  visualNodes.value = globalNetwork.value.nodes.map(node => ({
    id: node.id,
    throughput: 0,
    isSource: false,
    isTarget: false
  }))

  // 初始化边
  visualEdges.value = globalNetwork.value.edges.map(edge => ({
    from: edge.from,
    to: edge.to,
    capacity: edge.capacity || 1000,
    currentFlow: 0,
    utilization: 0,
    flowAnimation: 0,
    isActive: false
  }))

  // 计算节点位置（力导向布局）
  calculateNodePositions()
}

// 计算节点位置（使用力导向布局算法）
const calculateNodePositions = () => {
  const nodes = visualNodes.value
  const edges = visualEdges.value
  const width = canvasSize.value.width
  const height = canvasSize.value.height
  
  if (nodes.length === 0) return
  
  // 初始化随机位置
  const positions = {}
  const velocities = {}
  nodes.forEach(node => {
    positions[node.id] = {
      x: Math.random() * (width - 200) + 100,
      y: Math.random() * (height - 200) + 100
    }
    velocities[node.id] = { x: 0, y: 0 }
  })
  
  // 力导向布局参数
  const iterations = 150
  const repulsionStrength = 3000 // 节点间斥力
  const attractionStrength = 0.02 // 边的引力
  const dampening = 0.85 // 阻尼系数
  const minDistance = 100 // 最小距离
  
  // 迭代计算
  for (let iter = 0; iter < iterations; iter++) {
    const forces = {}
    nodes.forEach(node => {
      forces[node.id] = { x: 0, y: 0 }
    })
    
    // 1. 计算节点间的斥力（库仑力）
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const nodeA = nodes[i]
        const nodeB = nodes[j]
        const dx = positions[nodeB.id].x - positions[nodeA.id].x
        const dy = positions[nodeB.id].y - positions[nodeA.id].y
        const distance = Math.sqrt(dx * dx + dy * dy) || 1
        
        if (distance < minDistance * 3) {
          const force = repulsionStrength / (distance * distance)
          const fx = (dx / distance) * force
          const fy = (dy / distance) * force
          
          forces[nodeA.id].x -= fx
          forces[nodeA.id].y -= fy
          forces[nodeB.id].x += fx
          forces[nodeB.id].y += fy
        }
      }
    }
    
    // 2. 计算边的引力（胡克定律）
    edges.forEach(edge => {
      const dx = positions[edge.to].x - positions[edge.from].x
      const dy = positions[edge.to].y - positions[edge.from].y
      const distance = Math.sqrt(dx * dx + dy * dy) || 1
      
      const force = distance * attractionStrength
      const fx = (dx / distance) * force
      const fy = (dy / distance) * force
      
      forces[edge.from].x += fx
      forces[edge.from].y += fy
      forces[edge.to].x -= fx
      forces[edge.to].y -= fy
    })
    
    // 3. 向中心的拉力（防止节点飞出边界）
    const centerX = width / 2
    const centerY = height / 2
    nodes.forEach(node => {
      const dx = centerX - positions[node.id].x
      const dy = centerY - positions[node.id].y
      forces[node.id].x += dx * 0.01
      forces[node.id].y += dy * 0.01
    })
    
    // 4. 更新速度和位置
    nodes.forEach(node => {
      velocities[node.id].x = (velocities[node.id].x + forces[node.id].x) * dampening
      velocities[node.id].y = (velocities[node.id].y + forces[node.id].y) * dampening
      
      positions[node.id].x += velocities[node.id].x
      positions[node.id].y += velocities[node.id].y
      
      // 边界约束
      const margin = 60
      positions[node.id].x = Math.max(margin, Math.min(width - margin, positions[node.id].x))
      positions[node.id].y = Math.max(margin, Math.min(height - margin, positions[node.id].y))
    })
  }
  
  // 应用计算好的位置
  nodePositions.value = positions
}

// 开始仿真
const startSimulation = async () => {
  if (!globalNetwork.value) return

  isRunning.value = true
  isPaused.value = false
  stats.value = {
    totalTransferred: 0,
    avgUtilization: 0,
    activePaths: 0,
    congestedLinks: 0
  }

  // 标记源和目标节点
  visualNodes.value.forEach(node => {
    node.isSource = node.id === simConfig.value.source
    node.isTarget = node.id === simConfig.value.target
    node.throughput = 0
  })

  // 计算路径
  await calculatePaths()

  // 开始动画循环
  lastTime = performance.now()
  animationLoop()
  
  showToast('仿真已开始', 'success')
}

// 计算路径（简化版本，实际应调用后端）
const calculatePaths = async () => {
  const { source, target, strategy } = simConfig.value

  // 这里简化处理，实际应调用后端API
  // 使用BFS找到k条路径
  const paths = findKPaths(source, target, strategy === 'single' ? 1 : 3)
  
  if (paths.length === 0) {
    showToast(`无法找到从节点 ${source} 到节点 ${target} 的路径！`, 'error')
    stopSimulation()
    return
  }

  // 计算每条路径的瓶颈容量
  const pathCapacities = paths.map(pathNodes => {
    let minCapacity = Infinity
    for (let i = 0; i < pathNodes.length - 1; i++) {
      const edge = visualEdges.value.find(
        e => e.from === pathNodes[i] && e.to === pathNodes[i + 1]
      )
      if (edge && edge.capacity < minCapacity) {
        minCapacity = edge.capacity
      }
    }
    return minCapacity
  })

  // 计算总容量
  const totalCapacity = pathCapacities.reduce((sum, cap) => sum + cap, 0)
  const requestedFlow = simConfig.value.flowRate

  // 检查是否超过容量
  let actualFlowRate = requestedFlow
  let isLimited = false
  
  if (requestedFlow > totalCapacity) {
    isLimited = true
    actualFlowRate = totalCapacity
    
    // 显示警告
    const pathsInfo = strategy === 'single' ? '1条路径' : `${paths.length}条路径`
    showToast(
      `流量速率超出网络容量！请求: ${requestedFlow} 单位/秒，最大: ${totalCapacity.toFixed(0)} 单位/秒 (${pathsInfo})，将使用最大容量进行仿真。`,
      'warning'
    )
  }

  // 按策略分配流量
  activePaths.value = paths.map((pathNodes, idx) => {
    const pathCapacity = pathCapacities[idx]
    let flow

    if (strategy === 'single') {
      // 单路径：使用实际流量，但不超过路径容量
      flow = Math.min(actualFlowRate, pathCapacity)
    } else {
      // 多路径：按容量比例分配
      flow = (pathCapacity / totalCapacity) * actualFlowRate
      // 确保不超过单条路径容量
      flow = Math.min(flow, pathCapacity)
    }

    return {
      nodes: pathNodes,
      flow: flow,
      capacity: pathCapacity,
      utilization: flow / pathCapacity,
      maxCapacity: pathCapacity
    }
  })

  // 更新实际使用的流量速率
  if (isLimited) {
    // 保存原始请求值
    simConfig.value._originalFlowRate = requestedFlow
    // 使用实际可达流量
    simConfig.value._actualFlowRate = actualFlowRate
  } else {
    simConfig.value._actualFlowRate = actualFlowRate
  }

  stats.value.activePaths = activePaths.value.length
}

// 简单的BFS找路径（前端模拟）
const findKPaths = (source, target, k) => {
  const paths = []
  const edges = globalNetwork.value.edges

  // 构建邻接表
  const graph = {}
  edges.forEach(edge => {
    if (!graph[edge.from]) graph[edge.from] = []
    graph[edge.from].push(edge.to)
  })

  // BFS找路径
  const queue = [[source]]
  const visited = new Set()

  while (queue.length > 0 && paths.length < k) {
    const path = queue.shift()
    const node = path[path.length - 1]

    if (node === target) {
      paths.push([...path])
      continue
    }

    if (path.length > 10) continue // 防止路径过长

    const neighbors = graph[node] || []
    for (const next of neighbors) {
      if (!path.includes(next)) {
        queue.push([...path, next])
      }
    }
  }

  return paths.slice(0, k)
}

// 动画循环
const animationLoop = (currentTime = performance.now()) => {
  if (!isRunning.value || isPaused.value) return

  const deltaTime = (currentTime - lastTime) / 1000 // 转换为秒
  lastTime = currentTime

  // 更新流量
  updateTraffic(deltaTime)

  // 更新统计
  updateStats()

  // 继续动画
  animationId = requestAnimationFrame(animationLoop)
}

// 更新流量
const updateTraffic = (deltaTime) => {
  // 使用实际流量速率（如果被限制）
  const effectiveFlowRate = simConfig.value._actualFlowRate || simConfig.value.flowRate
  const flowIncrement = effectiveFlowRate * deltaTime * simConfig.value.speed

  // 重置边的流量
  visualEdges.value.forEach(edge => {
    edge.currentFlow = 0
    edge.isActive = false
  })

  // 根据活跃路径更新流量
  activePaths.value.forEach(path => {
    for (let i = 0; i < path.nodes.length - 1; i++) {
      const from = path.nodes[i]
      const to = path.nodes[i + 1]
      
      const edge = visualEdges.value.find(e => e.from === from && e.to === to)
      if (edge) {
        edge.currentFlow += path.flow
        edge.utilization = edge.currentFlow / edge.capacity
        edge.isActive = true
        edge.flowAnimation = path.flow
      }
    }
  })

  // 更新节点吞吐量
  visualNodes.value.forEach(node => {
    if (node.isSource) {
      const effectiveFlowRate = simConfig.value._actualFlowRate || simConfig.value.flowRate
      node.throughput = effectiveFlowRate
    } else if (node.isTarget) {
      const incomingFlow = visualEdges.value
        .filter(e => e.to === node.id)
        .reduce((sum, e) => sum + e.currentFlow, 0)
      node.throughput = incomingFlow
    } else {
      node.throughput = 0
    }
  })

  stats.value.totalTransferred += flowIncrement
}

// 更新统计
const updateStats = () => {
  const activeEdges = visualEdges.value.filter(e => e.isActive)
  
  if (activeEdges.length > 0) {
    stats.value.avgUtilization = 
      activeEdges.reduce((sum, e) => sum + e.utilization, 0) / activeEdges.length
  }

  stats.value.congestedLinks = visualEdges.value.filter(e => e.utilization > 0.8).length
}

// 暂停仿真
const pauseSimulation = () => {
  isPaused.value = true
  showToast('仿真已暂停', 'info')
}

// 继续仿真
const resumeSimulation = () => {
  isPaused.value = false
  lastTime = performance.now()
  animationLoop()
  showToast('仿真已继续', 'success')
}

// 停止仿真
const stopSimulation = () => {
  isRunning.value = false
  isPaused.value = false
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
  showToast('仿真已停止', 'info')
}

// 重置仿真
const resetSimulation = () => {
  stopSimulation()
  initVisualization()
  showToast('仿真已重置', 'info')
}

// 节点选择
const selectNode = (nodeId) => {
  console.log('Selected node:', nodeId)
}

// 获取节点样式
const getNodeRadius = (node) => {
  return node.isSource || node.isTarget ? 25 : 20
}

const getNodeColor = (node) => {
  if (node.isSource) return '#48bb78'
  if (node.isTarget) return '#fc8181'
  return '#4299e1'
}

const getNodeStroke = (node) => {
  return node.isSource || node.isTarget ? '#2d3748' : '#2c5282'
}

const getNodeStrokeWidth = (node) => {
  return node.isSource || node.isTarget ? 3 : 2
}

// 获取边样式
const getEdgeColor = (edge) => {
  if (edge.utilization > 0.8) return '#f56565'
  if (edge.isActive) return '#4299e1'
  return '#cbd5e0'
}

const getEdgeWidth = (edge) => {
  if (edge.isActive) {
    return 2 + (edge.utilization * 4)
  }
  return 2
}

const getEdgeOpacity = (edge) => {
  return edge.isActive ? 0.9 : 0.3
}

const getEdgeMarker = (edge) => {
  if (edge.utilization > 0.8) return 'url(#arrowhead-congestion)'
  if (edge.isActive) return 'url(#arrowhead-flow)'
  return 'url(#arrowhead)'
}

// 生命周期
onMounted(() => {
  initVisualization()
})

onUnmounted(() => {
  stopSimulation()
})

// 监听网络变化
watch(() => globalNetwork.value, () => {
  initVisualization()
}, { deep: true })
</script>

<style scoped>
.traffic-sim-panel {
  max-width: 100%;
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.panel-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 0.5rem;
  text-align: center;
}

.panel-description {
  text-align: center;
  color: #718096;
  margin: 0 0 2rem;
}

.sim-container {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 1.5rem;
  flex: 1;
  min-height: 0;
}

.control-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
}

.control-card,
.stats-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.control-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 1rem;
}

.control-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.control-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #4a5568;
}

.control-group input,
.control-group select {
  padding: 0.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.9rem;
}

.control-group input:focus,
.control-group select:focus {
  outline: none;
  border-color: #667eea;
}

.strategy-selector {
  margin-bottom: 1.5rem;
}

.strategy-selector h4 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #4a5568;
  margin: 0 0 0.75rem;
}

.strategy-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.strategy-option {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.strategy-option:hover {
  border-color: #667eea;
  background: #f7fafc;
}

.strategy-option input[type="radio"] {
  margin-right: 0.75rem;
}

.strategy-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.strategy-icon {
  font-size: 1.25rem;
}

.strategy-text {
  font-weight: 500;
}

.control-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.btn {
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-warning {
  background: #ed8936;
  color: white;
}

.btn-success {
  background: #48bb78;
  color: white;
}

.btn-danger {
  background: #f56565;
  color: white;
}

.btn-secondary {
  background: #718096;
  color: white;
  grid-column: 1 / -1;
}

.flow-rate-info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-align: center;
}

.flow-rate-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.flow-rate-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.25rem;
}

.flow-rate-unit {
  font-size: 0.9rem;
  font-weight: 400;
  opacity: 0.9;
}

.flow-rate-warning {
  font-size: 0.75rem;
  color: #fbd38d;
  background: rgba(0, 0, 0, 0.2);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
  margin-top: 0.25rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 8px;
}

.stat-label {
  font-size: 0.75rem;
  color: #718096;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
}

.text-danger {
  color: #f56565 !important;
}

.visualization-area {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 0;
}

.network-canvas-container {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.network-canvas {
  width: 100%;
  height: 100%;
}

.network-edge {
  transition: all 0.3s;
}

.network-node {
  cursor: pointer;
  transition: filter 0.2s ease;
  transform-origin: center;
}

.network-node:hover {
  filter: brightness(1.2) drop-shadow(0 0 8px currentColor);
}

.node-label {
  font-size: 14px;
  font-weight: 600;
  fill: white;
  pointer-events: none;
}

.node-throughput {
  font-size: 12px;
  font-weight: 600;
  fill: #2d3748;
  pointer-events: none;
}

.flow-label {
  font-size: 11px;
  font-weight: 600;
  fill: #2d3748;
  pointer-events: none;
}

.flow-particle {
  filter: drop-shadow(0 0 3px #4299e1);
}

.legend {
  position: absolute;
  top: 20px;
  right: 20px;
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.legend h4 {
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.paths-info {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
}

.paths-info h4 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem;
}

.path-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.path-item {
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem;
}

.path-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.path-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
}

.path-route {
  font-weight: 600;
  color: #2d3748;
  font-size: 0.9rem;
}

.path-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #718096;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #2d3748;
  margin: 0 0 0.5rem;
}

.empty-state p {
  color: #718096;
}
</style>
