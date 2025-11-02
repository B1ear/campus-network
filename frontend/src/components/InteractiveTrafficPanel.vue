<template>
  <div class="traffic-sim-panel">
    <h2>🎮 交互式流量仿真</h2>

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
            </div>
          </div>

          <!-- 控制按钮 -->
          <div class="control-buttons">
            <button @click="startSimulation" :disabled="isRunning" class="btn btn-primary">
              ▶️ 开始
            </button>
            <button @click="togglePause" :disabled="!isRunning" :class="isPaused ? 'btn btn-success' : 'btn btn-warning'">
              {{ isPaused ? '▶️ 继续' : '⏸️ 暂停' }}
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
          <svg 
            ref="svgCanvas" 
            class="network-canvas" 
            :viewBox="`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`"
            @mousedown="handleMouseDown"
            @mousemove="handleMouseMove"
            @mouseup="handleMouseUp"
            @mouseleave="handleMouseUp"
            @wheel="handleWheel"
          >
            <!-- 定义箭头标记 -->
            <defs>
              <marker id="arrowhead" markerWidth="8" markerHeight="8" refX="7" refY="2.5" orient="auto">
                <polygon points="0 0, 8 2.5, 0 5" fill="#666" />
              </marker>
              <marker id="arrowhead-flow" markerWidth="8" markerHeight="8" refX="7" refY="2.5" orient="auto">
                <polygon points="0 0, 8 2.5, 0 5" fill="#4299e1" />
              </marker>
              <marker id="arrowhead-congestion" markerWidth="8" markerHeight="8" refX="7" refY="2.5" orient="auto">
                <polygon points="0 0, 8 2.5, 0 5" fill="#fc8181" />
              </marker>
            </defs>

            <!-- 绘制边 -->
            <g class="edges-layer">
              <g v-for="edge in visualEdges" :key="`edge-${edge.from}-${edge.to}`">
                <!-- 边线 -->
                <line
                  :x1="getEdgeStartX(edge)"
                  :y1="getEdgeStartY(edge)"
                  :x2="getEdgeEndX(edge)"
                  :y2="getEdgeEndY(edge)"
                  :stroke="getEdgeColor(edge)"
                  :stroke-width="getEdgeWidth(edge)"
                  :opacity="getEdgeOpacity(edge)"
                  :marker-end="getEdgeMarker(edge)"
                  class="network-edge"
                />
                <!-- 流量动画 -->
                <circle
                  v-if="edge.flowAnimation > 0 && isRunning && !isPaused"
                  :r="4"
                  fill="#4299e1"
                  class="flow-particle"
                >
                  <animateMotion
                    dur="1s"
                    repeatCount="indefinite"
                    :path="`M ${getEdgeStartX(edge)} ${getEdgeStartY(edge)} L ${getEdgeEndX(edge)} ${getEdgeEndY(edge)}`"
                  />
                </circle>
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

            <!-- 绘制边标签（在节点之上） -->
            <g class="edge-labels-layer">
              <g v-for="edge in visualEdges" :key="`edge-label-${edge.from}-${edge.to}`">
                <g v-if="edge.currentFlow > 0">
                  <rect
                    :x="(getEdgeStartX(edge) + getEdgeEndX(edge)) / 2 - 25"
                    :y="(getEdgeStartY(edge) + getEdgeEndY(edge)) / 2 - 20"
                    width="50"
                    height="16"
                    rx="3"
                    fill="white"
                    opacity="0.75"
                    stroke="#cbd5e0"
                    stroke-width="1"
                  />
                  <text
                    :x="(getEdgeStartX(edge) + getEdgeEndX(edge)) / 2"
                    :y="(getEdgeStartY(edge) + getEdgeEndY(edge)) / 2 - 8"
                    class="flow-label"
                    text-anchor="middle"
                    opacity="0.85"
                  >
                    {{ edge.currentFlow.toFixed(0) }}/{{ edge.capacity }}
                  </text>
                </g>
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
import { api } from '../api/backend.js'

const globalNetwork = inject('globalNetwork')
const hasNetwork = computed(() => globalNetwork.value !== null)

// 仿真配置
const simConfig = ref({
  source: 0,
  target: 5,
  flowRate: 100,
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
const canvasSize = ref({ width: 1200, height: 700 })
const edgeUsageMap = ref({}) // 跟踪边的当前使用情况 {"from-to": flow}

// 平移和缩放状态
const viewBox = ref({ x: 0, y: 0, width: 1200, height: 700 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const svgCanvas = ref(null)


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
const initVisualization = (forceRecalculate = false) => {
  if (!globalNetwork.value) return

  // 初始化节点
  visualNodes.value = globalNetwork.value.nodes.map(node => ({
    id: node.id,
    throughput: 0,
    isSource: false,
    isTarget: false,
    isUsed: false // 记录节点是否在仿真中使用
  }))

  // 初始化边
  visualEdges.value = globalNetwork.value.edges.map(edge => ({
    from: edge.from,
    to: edge.to,
    capacity: edge.capacity || 1000,
    currentFlow: 0,
    utilization: 0,
    flowAnimation: 0,
    isActive: false,
    flowDirection: null // 记录实际流量方向: 'forward', 'reverse', 或 null
  }))

  // 计算节点位置（力导向布局）
  // 只在网络变化或强制重算时才重新计算位置
  if (forceRecalculate || Object.keys(nodePositions.value).length === 0) {
    calculateNodePositions()
  }
}

// 计算节点位置（使用力导向布局算法）
const calculateNodePositions = () => {
  const nodes = visualNodes.value
  const edges = visualEdges.value
  const width = canvasSize.value.width
  const height = canvasSize.value.height
  
  if (nodes.length === 0) return
  
  // 初始化随机位置（使用固定种子以保证一致性）
  const positions = {}
  const velocities = {}
  
  // 使用节点ID作为种子来生成伺随机位置
  const seededRandom = (seed) => {
    const x = Math.sin(seed) * 10000
    return x - Math.floor(x)
  }
  
  nodes.forEach(node => {
    const seedX = node.id * 12345 + 67890
    const seedY = node.id * 54321 + 9876
    positions[node.id] = {
      x: seededRandom(seedX) * (width - 200) + 100,
      y: seededRandom(seedY) * (height - 200) + 100
    }
    velocities[node.id] = { x: 0, y: 0 }
  })
  
  // 力导向布局参数
  const iterations = 150
  const repulsionStrength = 12000 // 节点间斥力（大幅增加）
  const attractionStrength = 0.01 // 边的引力（继续减小）
  const dampening = 0.85 // 阻尼系数
  const minDistance = 250 // 最小距离（大幅增加）
  
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
      
      // 边界约束（增大边界）
      const margin = 80
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
  
  // 重置边使用情况
  edgeUsageMap.value = {}

  // 重置所有节点状态
  visualNodes.value.forEach(node => {
    node.isSource = false
    node.isTarget = false
    node.isUsed = false
    node.throughput = 0
  })

  // 标记源和目标节点
  const sourceNode = visualNodes.value.find(n => n.id === simConfig.value.source)
  const targetNode = visualNodes.value.find(n => n.id === simConfig.value.target)
  if (sourceNode) {
    sourceNode.isSource = true
    sourceNode.isUsed = true
  }
  if (targetNode) {
    targetNode.isTarget = true
    targetNode.isUsed = true
  }

  // 计算路径
  await calculatePaths()

  // 只有在路径计算成功后才启动动画
  if (activePaths.value.length > 0) {
    lastTime = performance.now()
    animationLoop()
    
    const strategyName = {
      single: '单路径',
      balanced: '负载均衡'
    }[simConfig.value.strategy] || simConfig.value.strategy
    showToast(`🚀 仿真启动成功 | 策略: ${strategyName} | 路径数: ${activePaths.value.length}`, 'success')
  }
}

// 计算路径（调用后端负载均衡算法）
const calculatePaths = async () => {
  const { source, target, strategy, flowRate } = simConfig.value

  try {
    // 准备边使用情况数据（传递给后端）
    const edgeUsageList = []
    for (const key in edgeUsageMap.value) {
      const [from, to] = key.split('-').map(Number)
      edgeUsageList.push({
        from,
        to,
        flow: edgeUsageMap.value[key]
      })
    }
    
    console.log('🔍 调用后端API计算路径:', {
      source,
      target,
      strategy,
      flowRate,
      nodeCount: globalNetwork.value.nodes.length,
      edgeCount: globalNetwork.value.edges.length,
      currentEdgeUsage: edgeUsageList.length
    })
    
    // 调用后端API计算路径和流量分配（传入边使用情况）
    const result = await api.calculateTrafficPaths(
      globalNetwork.value.nodes,
      globalNetwork.value.edges,
      source,
      target,
      flowRate,
      strategy, // 'single' or 'balanced'
      3, // 最多查找3条路径
      edgeUsageList // 传递当前边使用情况
    )
    
    console.log('✅ 后端返回结果:', result)

    if (result.error) {
      showToast(`❌ 路径计算失败 | ${result.error}`, 'error')
      stopSimulation()
      return
    }

    const { paths, path_allocations, total_capacity, actual_flow, is_limited, requested_flow } = result

    if (!paths || paths.length === 0) {
      showToast(`❌ 路径查找失败 | 无法从节点 ${source} 到达节点 ${target}`, 'error')
      stopSimulation()
      return
    }

    // 检查是否超过容量
    if (is_limited) {
      const pathsInfo = strategy === 'single' ? '1条路径' : `${paths.length}条路径`
      showToast(
        `⚠️ 容量限制 | 请求: ${requested_flow} 单位/秒 > 最大: ${total_capacity.toFixed(0)} 单位/秒 (${pathsInfo}) | 已自动调整`,
        'warning'
      )
    }

    // 使用后端计算的结果
    activePaths.value = paths.map((pathNodes, idx) => {
      const allocation = path_allocations[idx]
      return {
        nodes: pathNodes,
        flow: allocation.flow,
        capacity: allocation.capacity,
        utilization: allocation.utilization,
        maxCapacity: allocation.capacity
      }
    })

    // 更新实际使用的流量速率
    if (is_limited) {
      simConfig.value._originalFlowRate = requested_flow
      simConfig.value._actualFlowRate = actual_flow
    } else {
      simConfig.value._actualFlowRate = actual_flow
    }

    stats.value.activePaths = activePaths.value.length

    // 标记路径上的节点为已使用
    activePaths.value.forEach(path => {
      path.nodes.forEach(nodeId => {
        const node = visualNodes.value.find(n => n.id === nodeId)
        if (node) {
          node.isUsed = true
        }
      })
    })
  } catch (error) {
    console.error('路径计算失败:', error)
    showToast(`❌ 路径计算失败 | ${error.message}`, 'error')
    stopSimulation()
  }
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
  const flowIncrement = effectiveFlowRate * deltaTime

  // 重置边的流量
  visualEdges.value.forEach(edge => {
    edge.currentFlow = 0
    edge.isActive = false
    edge.flowDirection = null
  })
  
  // 重置边使用情况映射
  edgeUsageMap.value = {}

  // 根据活跃路径更新流量
  activePaths.value.forEach(path => {
    for (let i = 0; i < path.nodes.length - 1; i++) {
      const from = path.nodes[i]
      const to = path.nodes[i + 1]
      
      // 查找边（无向图：正向或反向）
      let edge = visualEdges.value.find(e => e.from === from && e.to === to)
      let isReverse = false
      let edgeKey = null
      
      if (!edge) {
        edge = visualEdges.value.find(e => e.from === to && e.to === from)
        isReverse = true
      }
      
      if (edge) {
        edge.currentFlow += path.flow
        edge.utilization = edge.currentFlow / edge.capacity
        edge.isActive = true
        edge.flowAnimation = path.flow
        // 记录流量方向
        edge.flowDirection = isReverse ? 'reverse' : 'forward'
        
        // 更新边使用情况映射（使用边的原始定义方向）
        edgeKey = `${edge.from}-${edge.to}`
        edgeUsageMap.value[edgeKey] = (edgeUsageMap.value[edgeKey] || 0) + path.flow
      }
    }
  })

  // 更新节点吞吐量
  visualNodes.value.forEach(node => {
    if (node.isSource) {
      const effectiveFlowRate = simConfig.value._actualFlowRate || simConfig.value.flowRate
      node.throughput = effectiveFlowRate
    } else if (node.isTarget) {
      // 计算流入目标节点的总流量（考虑流量方向）
      let incomingFlow = 0
      visualEdges.value.forEach(edge => {
        if (edge.flowDirection === 'forward' && edge.to === node.id) {
          // 正向流量流入
          incomingFlow += edge.currentFlow
        } else if (edge.flowDirection === 'reverse' && edge.from === node.id) {
          // 反向流量流入
          incomingFlow += edge.currentFlow
        }
      })
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
  const utilization = (stats.value.avgUtilization * 100).toFixed(1)
  showToast(`⏸️ 仿真已暂停 | 平均利用率: ${utilization}% | 已传输: ${stats.value.totalTransferred.toFixed(0)}`, 'info')
}

// 继续仿真
const resumeSimulation = () => {
  isPaused.value = false
  lastTime = performance.now()
  animationLoop()
  showToast('▶️ 仿真继续运行', 'success')
}

// 切换暂停/继续
const togglePause = () => {
  if (isPaused.value) {
    resumeSimulation()
  } else {
    pauseSimulation()
  }
}

// 停止仿真
const stopSimulation = () => {
  isRunning.value = false
  isPaused.value = false
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
  // 只在统计数据非零时显示停止消息
  if (stats.value.totalTransferred > 0) {
    const transferred = stats.value.totalTransferred.toFixed(0)
    const utilization = (stats.value.avgUtilization * 100).toFixed(1)
    showToast(`⏹️ 仿真已停止 | 总传输: ${transferred} | 平均利用率: ${utilization}%`, 'info')
  }
}

// 重置仿真
const resetSimulation = () => {
  stopSimulation()
  
  // 重置统计数据
  stats.value = {
    totalTransferred: 0,
    avgUtilization: 0,
    activePaths: 0,
    congestedLinks: 0
  }
  
  // 清除流量限制警告标识
  delete simConfig.value._originalFlowRate
  delete simConfig.value._actualFlowRate
  
  // 清除活跃路径
  activePaths.value = []
  
  // 清空边使用情况
  edgeUsageMap.value = {}
  
  // 重新初始化可视化
  initVisualization()
  
  showToast('🔄 仿真环境已重置，可以开始新的仿真', 'info')
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
  if (node.isSource) return '#48bb78' // 源节点：绿色
  if (node.isTarget) return '#fc8181' // 目标节点：红色
  if (isRunning.value && !node.isUsed) return '#ffffff' // 仿真中未使用：白色
  return '#4299e1' // 默认/使用中：蓝色
}

const getNodeStroke = (node) => {
  if (node.isSource || node.isTarget) return '#2d3748'
  if (isRunning.value && !node.isUsed) return '#cbd5e0' // 未使用节点：浅灰边框
  return '#2c5282'
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
    // 确保利用率不超过100%，以防止箭头过大
    const clampedUtilization = Math.min(edge.utilization, 1.0)
    return 2 + (clampedUtilization * 4)
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

// 获取边的起点和终点（根据流量方向）
const getEdgeStartX = (edge) => {
  if (edge.flowDirection === 'reverse') {
    return nodePositions.value[edge.to]?.x
  }
  return nodePositions.value[edge.from]?.x
}

const getEdgeStartY = (edge) => {
  if (edge.flowDirection === 'reverse') {
    return nodePositions.value[edge.to]?.y
  }
  return nodePositions.value[edge.from]?.y
}

const getEdgeEndX = (edge) => {
  if (edge.flowDirection === 'reverse') {
    return nodePositions.value[edge.from]?.x
  }
  return nodePositions.value[edge.to]?.x
}

const getEdgeEndY = (edge) => {
  if (edge.flowDirection === 'reverse') {
    return nodePositions.value[edge.from]?.y
  }
  return nodePositions.value[edge.to]?.y
}

// 处理鼠标拖拽事件
const handleMouseDown = (event) => {
  // 只在点击背景时开始拖拽，不在节点上
  if (event.target.tagName !== 'svg' && !event.target.closest('.edges-layer')) return
  
  isDragging.value = true
  dragStart.value = {
    x: event.clientX,
    y: event.clientY,
    viewX: viewBox.value.x,
    viewY: viewBox.value.y
  }
  event.preventDefault()
}

const handleMouseMove = (event) => {
  if (!isDragging.value) return
  
  const dx = (event.clientX - dragStart.value.x) * (viewBox.value.width / canvasSize.value.width)
  const dy = (event.clientY - dragStart.value.y) * (viewBox.value.height / canvasSize.value.height)
  
  viewBox.value.x = dragStart.value.viewX - dx
  viewBox.value.y = dragStart.value.viewY - dy
}

const handleMouseUp = () => {
  isDragging.value = false
}

// 处理滚轮缩放
const handleWheel = (event) => {
  event.preventDefault()
  
  // 获取鼠标在SVG中的位置
  const svg = svgCanvas.value
  if (!svg) return
  
  const rect = svg.getBoundingClientRect()
  const mouseX = event.clientX - rect.left
  const mouseY = event.clientY - rect.top
  
  // 转换为视图坐标
  const viewMouseX = viewBox.value.x + (mouseX / rect.width) * viewBox.value.width
  const viewMouseY = viewBox.value.y + (mouseY / rect.height) * viewBox.value.height
  
  // 缩放因子
  const scaleFactor = event.deltaY > 0 ? 1.1 : 0.9
  
  // 限制缩放范围（0.5x 到 3x）
  const newWidth = viewBox.value.width * scaleFactor
  const newHeight = viewBox.value.height * scaleFactor
  
  if (newWidth > canvasSize.value.width * 3 || newWidth < canvasSize.value.width * 0.5) {
    return
  }
  
  // 以鼠标为中心缩放
  viewBox.value.width = newWidth
  viewBox.value.height = newHeight
  viewBox.value.x = viewMouseX - (mouseX / rect.width) * newWidth
  viewBox.value.y = viewMouseY - (mouseY / rect.height) * newHeight
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
  // 网络变化时强制重新计算位置
  initVisualization(true)
}, { deep: true })
</script>

<style scoped>
.traffic-sim-panel {
  max-width: 100%;
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.traffic-sim-panel > h2 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 1.5rem;
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
  grid-template-columns: 1fr 1fr 1fr;
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
  cursor: grab;
}

.network-canvas-container:active {
  cursor: grabbing;
}

.network-canvas {
  width: 100%;
  height: 100%;
  display: block;
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
