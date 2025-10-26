<template>
  <div class="simulation-panel">
    <h2 class="panel-title">🔬 网络静态分析</h2>
    <p class="panel-description">实时流量监控 · 鲁棒性分析 · 负载均衡</p>

    <!-- 功能选择 -->
    <div class="function-selector">
      <button 
        v-for="func in functions" 
        :key="func.id"
        :class="['func-button', { active: activeFunction === func.id }]"
        @click="activeFunction = func.id"
      >
        <span class="func-icon">{{ func.icon }}</span>
        <span class="func-name">{{ func.name }}</span>
      </button>
    </div>

    <!-- 鲁棒性分析 -->
    <div v-if="activeFunction === 'robustness'" class="function-content">
      <div class="card">
        <h3 class="card-title">📊 网络鲁棒性分析</h3>
        
        <button @click="analyzeRobustness" :disabled="loading || !hasNetwork" class="action-button primary">
          <span v-if="!loading">🔍 分析网络鲁棒性</span>
          <span v-else>⏳ 分析中...</span>
        </button>

        <div v-if="robustnessResult" class="results">
          <!-- 鲁棒性指标 -->
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-value">{{ robustnessResult.metrics.num_bridges }}</div>
              <div class="metric-label">关键边(桥)</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ robustnessResult.metrics.num_articulation_points }}</div>
              <div class="metric-label">关键节点(割点)</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ (robustnessResult.metrics.robustness_score * 100).toFixed(1) }}%</div>
              <div class="metric-label">鲁棒性得分</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ robustnessResult.metrics.average_degree.toFixed(2) }}</div>
              <div class="metric-label">平均度数</div>
            </div>
          </div>

          <!-- 可视化图 -->
          <div v-if="robustnessResult.visualization" class="visualization">
            <img :src="`data:image/png;base64,${robustnessResult.visualization}`" alt="鲁棒性分析图" />
          </div>

          <!-- 关键边列表 -->
          <div v-if="robustnessResult.bridges.length > 0" class="detail-section">
            <h4>⚠️ 关键边（删除后网络断开）</h4>
            <div class="item-list">
              <div v-for="(bridge, idx) in robustnessResult.bridges" :key="idx" class="list-item critical">
                边 {{ bridge.from }} → {{ bridge.to }}
              </div>
            </div>
          </div>

          <!-- 关键节点列表 -->
          <div v-if="robustnessResult.articulation_points.length > 0" class="detail-section">
            <h4>⚠️ 关键节点（删除后网络断开）</h4>
            <div class="item-list">
              <div v-for="node in robustnessResult.articulation_points" :key="node" class="list-item critical">
                节点 {{ node }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 流量监控与负载均衡 -->
    <div v-if="activeFunction === 'loadbalancing'" class="function-content">
      <div class="card">
        <h3 class="card-title">⚖️ 负载均衡仿真</h3>
        
        <div class="form-grid">
          <div class="form-group">
            <label>源节点</label>
            <input v-model.number="trafficParams.source" type="number" min="0" />
          </div>
          <div class="form-group">
            <label>目标节点</label>
            <input v-model.number="trafficParams.target" type="number" min="0" />
          </div>
          <div class="form-group">
            <label>总流量</label>
            <input v-model.number="trafficParams.totalFlow" type="number" min="100" step="100" />
          </div>
          <div class="form-group">
            <label>路径数量</label>
            <input v-model.number="trafficParams.numPaths" type="number" min="1" max="5" />
          </div>
        </div>

        <!-- 功能开关 -->
        <div class="toggle-group">
          <label class="toggle-item">
            <input type="checkbox" v-model="trafficParams.enableLoadBalancing" />
            <span>启用负载均衡</span>
          </label>
          <label class="toggle-item">
            <input type="checkbox" v-model="trafficParams.enableCongestionAvoidance" />
            <span>启用拥塞避免</span>
          </label>
        </div>

        <button @click="simulateLoadBalancing" :disabled="loading || !hasNetwork" class="action-button primary">
          <span v-if="!loading">🚀 开始仿真</span>
          <span v-else>⏳ 仿真中...</span>
        </button>

        <div v-if="trafficResult" class="results">
          <!-- 策略信息 -->
          <div class="info-banner">
            <strong>策略：</strong> {{ getStrategyName(trafficResult.strategy) }}
          </div>

          <!-- 流量统计 -->
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-value">{{ trafficResult.num_paths }}</div>
              <div class="metric-label">使用路径数</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ (trafficResult.statistics.average_utilization * 100).toFixed(1) }}%</div>
              <div class="metric-label">平均利用率</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ (trafficResult.statistics.max_utilization * 100).toFixed(1) }}%</div>
              <div class="metric-label">最大利用率</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ trafficResult.congestion.num_congested }}</div>
              <div class="metric-label">拥塞链路数</div>
            </div>
          </div>

          <!-- 可视化图 -->
          <div v-if="trafficResult.visualization" class="visualization">
            <img :src="`data:image/png;base64,${trafficResult.visualization}`" alt="负载均衡图" />
          </div>

          <!-- 路径列表 -->
          <div v-if="trafficResult.paths" class="detail-section">
            <h4>📍 使用的路径</h4>
            <div class="item-list">
              <div v-for="(path, idx) in trafficResult.paths" :key="idx" class="list-item">
                <strong>路径 {{ idx + 1 }}:</strong> {{ path.join(' → ') }}
                <span v-if="trafficResult.path_flows" class="flow-info">
                  (流量: {{ trafficResult.path_flows[idx].toFixed(0) }})
                </span>
              </div>
            </div>
          </div>

          <!-- 拥塞警告 -->
          <div v-if="trafficResult.congestion.is_congested" class="detail-section warning">
            <h4>⚠️ 拥塞警告</h4>
            <div class="item-list">
              <div v-for="(link, idx) in trafficResult.congestion.congested_links" :key="idx" class="list-item critical">
                链路 {{ link.from }} → {{ link.to }} (利用率: {{ (link.utilization * 100).toFixed(1) }}%)
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 最大流计算 -->
    <div v-if="activeFunction === 'maxflow'" class="function-content">
      <div class="card">
        <h3 class="card-title">💧 最大流计算</h3>
        
        <div class="form-grid">
          <div class="form-group">
            <label>源节点</label>
            <input v-model.number="maxflowParams.source" type="number" min="0" />
          </div>
          <div class="form-group">
            <label>汇节点</label>
            <input v-model.number="maxflowParams.sink" type="number" min="0" />
          </div>
        </div>

        <button @click="calculateMaxFlow" :disabled="loading || !hasNetwork" class="action-button primary">
          <span v-if="!loading">💧 计算最大流</span>
          <span v-else>⏳ 计算中...</span>
        </button>

        <div v-if="maxflowResult" class="results">
          <div class="info-banner success">
            <strong>最大流值：</strong> {{ maxflowResult.max_flow }}
          </div>

          <!-- 可视化图 -->
          <div v-if="maxflowResult.visualization" class="visualization">
            <img :src="`data:image/png;base64,${maxflowResult.visualization}`" alt="最大流图" />
          </div>
        </div>
      </div>
    </div>

    <!-- 网络未配置提示 -->
    <div v-if="!hasNetwork" class="empty-state">
      <div class="empty-icon">🌐</div>
      <h3>尚未配置网络</h3>
      <p>请先在"网络配置"页面生成并应用网络拓扑</p>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, computed } from 'vue'
import { analyzeRobustness as apiAnalyzeRobustness, simulateTrafficLoadBalancing, calculateMaxFlowAPI } from '../api/backend'

const globalNetwork = inject('globalNetwork')
const hasNetwork = computed(() => globalNetwork.value !== null)

const loading = ref(false)
const activeFunction = ref('robustness')

const functions = [
  { id: 'robustness', name: '鲁棒性分析', icon: '🛡️' },
  { id: 'loadbalancing', name: '负载均衡', icon: '⚖️' },
  { id: 'maxflow', name: '最大流', icon: '💧' }
]

// 鲁棒性分析结果
const robustnessResult = ref(null)

// 负载均衡参数和结果
const trafficParams = ref({
  source: 0,
  target: 5,
  totalFlow: 1000,
  numPaths: 3,
  enableLoadBalancing: true,
  enableCongestionAvoidance: true
})
const trafficResult = ref(null)

// 最大流参数和结果
const maxflowParams = ref({
  source: 0,
  sink: 5
})
const maxflowResult = ref(null)

// 鲁棒性分析
const analyzeRobustness = async () => {
  if (!globalNetwork.value) return
  
  loading.value = true
  robustnessResult.value = null
  
  try {
    const result = await apiAnalyzeRobustness(
      globalNetwork.value.nodes,
      globalNetwork.value.edges
    )
    robustnessResult.value = result
  } catch (error) {
    alert('分析失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 负载均衡仿真
const simulateLoadBalancing = async () => {
  if (!globalNetwork.value) return
  
  loading.value = true
  trafficResult.value = null
  
  try {
    const result = await simulateTrafficLoadBalancing(
      globalNetwork.value.nodes,
      globalNetwork.value.edges,
      trafficParams.value.source,
      trafficParams.value.target,
      trafficParams.value.totalFlow,
      trafficParams.value.enableLoadBalancing,
      trafficParams.value.enableCongestionAvoidance,
      trafficParams.value.numPaths
    )
    trafficResult.value = result
  } catch (error) {
    alert('仿真失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 最大流计算
const calculateMaxFlow = async () => {
  if (!globalNetwork.value) return
  
  loading.value = true
  maxflowResult.value = null
  
  try {
    const result = await calculateMaxFlowAPI(
      globalNetwork.value.nodes,
      globalNetwork.value.edges,
      maxflowParams.value.source,
      maxflowParams.value.sink
    )
    maxflowResult.value = result
  } catch (error) {
    alert('计算失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 策略名称映射
const getStrategyName = (strategy) => {
  const names = {
    'single_path': '单路径传输',
    'weighted_load_balancing': '加权负载均衡',
    'load_balancing_with_congestion_avoidance': '拥塞避免负载均衡'
  }
  return names[strategy] || strategy
}
</script>

<style scoped>
.simulation-panel {
  max-width: 1400px;
  margin: 0 auto;
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
  font-size: 0.95rem;
}

.function-selector {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}

.func-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: white;
  color: #4a5568;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.func-button:hover {
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.func-button.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.func-icon {
  font-size: 1.25rem;
}

.function-content {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #4a5568;
  font-size: 0.9rem;
}

.form-group input {
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.toggle-group {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.toggle-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  color: #4a5568;
}

.toggle-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.action-button {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 1.5rem;
}

.action-button.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.action-button.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.results {
  margin-top: 1.5rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-card {
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  padding: 1.25rem;
  border-radius: 12px;
  text-align: center;
  border: 2px solid #e2e8f0;
}

.metric-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.25rem;
}

.metric-label {
  font-size: 0.85rem;
  color: #718096;
  font-weight: 500;
}

.visualization {
  margin: 1.5rem 0;
  text-align: center;
  background: #f7fafc;
  padding: 1rem;
  border-radius: 12px;
}

.visualization img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}

.detail-section {
  margin-top: 1.5rem;
  padding: 1.25rem;
  background: #f7fafc;
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.detail-section.warning {
  background: #fff5f5;
  border-left-color: #fc8181;
}

.detail-section h4 {
  margin: 0 0 1rem;
  font-size: 1.1rem;
  color: #2d3748;
}

.item-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.list-item {
  padding: 0.75rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  font-size: 0.9rem;
  color: #4a5568;
}

.list-item.critical {
  border-color: #fc8181;
  background: #fff5f5;
  color: #c53030;
  font-weight: 600;
}

.flow-info {
  color: #667eea;
  font-weight: 600;
  margin-left: 0.5rem;
}

.info-banner {
  padding: 1rem;
  background: #ebf8ff;
  border-radius: 8px;
  border-left: 4px solid #4299e1;
  margin-bottom: 1rem;
  color: #2c5282;
}

.info-banner.success {
  background: #f0fff4;
  border-left-color: #48bb78;
  color: #22543d;
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
  font-size: 0.95rem;
}
</style>
