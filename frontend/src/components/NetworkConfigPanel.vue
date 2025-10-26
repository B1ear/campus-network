<template>
  <div class="panel">
    <h2>🌐 网络配置与拓扑生成</h2>
    
    <!-- 模式切换 -->
    <div class="mode-selector">
      <button 
        :class="['mode-btn', { active: mode === 'auto' }]"
        @click="mode = 'auto'"
      >
        🤖 随机生成
      </button>
      <button 
        :class="['mode-btn', { active: mode === 'manual' }]"
        @click="mode = 'manual'"
      >
        ✏️ 手动编辑
      </button>
    </div>

    <div class="layout">
      <!-- 配置区域 -->
      <div class="section">
        <!-- 随机生成模式 -->
        <div v-if="mode === 'auto'">
        <h3>网络参数配置</h3>
        
        <div class="form-group">
          <label>节点数量 (路由器数量):</label>
          <input type="number" v-model.number="config.num_nodes" min="2" max="100" />
          <span class="hint">推荐: 20-30，网络将自动保证所有节点可达</span>
        </div>

        <div class="form-group">
          <label>造价范围:</label>
          <div class="range-input">
            <input type="number" v-model.number="config.cost_range[0]" min="1" />
            <span>~</span>
            <input type="number" v-model.number="config.cost_range[1]" min="1" />
          </div>
          <span class="hint">最小 ~ 最大造价</span>
        </div>

        <div class="form-group">
          <label>吞吐量/容量范围:</label>
          <div class="range-input">
            <input type="number" v-model.number="config.capacity_range[0]" min="1" />
            <span>~</span>
            <input type="number" v-model.number="config.capacity_range[1]" min="1" />
          </div>
          <span class="hint">最小 ~ 最大吞吐量</span>
        </div>

        <div class="form-group">
          <label>随机种子:</label>
          <input type="number" v-model.number="config.seed" />
          <span class="hint">相同种子生成相同网络</span>
        </div>

        <div class="button-group">
          <button @click="generateNetwork" :disabled="loading" class="primary">
            {{ loading ? '生成中...' : '🚀 生成网络' }}
          </button>
          <button @click="loadDefaultConfig" class="secondary">
            📋 使用默认配置
          </button>
          <button @click="useGeneratedNetwork" :disabled="!networkData" class="success">
            ✅ 应用到算法
          </button>
        </div>
        </div>

        <!-- 手动编辑模式 -->
        <div v-else>
          <h3>手动编辑网络</h3>
          
          <div class="form-group">
            <label>节点数量:</label>
            <input type="number" v-model.number="manualNodes" min="2" max="100" @change="initManualEdges" />
            <span class="hint">设置节点数量后，可以配置边</span>
          </div>

          <div v-if="manualNodes >= 2" class="edges-editor">
            <div class="edges-header">
              <h4>边配置</h4>
              <button @click="addManualEdge" class="add-edge-btn">➕ 添加边</button>
            </div>
            
            <!-- 列标题 -->
            <div class="edges-header-labels">
              <span class="label-from">起点</span>
              <span class="label-arrow"></span>
              <span class="label-to">终点</span>
              <span class="label-cost">造价</span>
              <span class="label-capacity">容量</span>
              <span class="label-action">操作</span>
            </div>
            
            <div class="edges-list">
              <div v-for="(edge, idx) in manualEdges" :key="idx" class="edge-item">
                <select v-model.number="edge.from" class="select-from" title="起点节点">
                  <option v-for="n in manualNodes" :key="n" :value="n-1">{{ n-1 }}</option>
                </select>
                <span class="arrow">→</span>
                <select v-model.number="edge.to" class="select-to" title="终点节点">
                  <option v-for="n in manualNodes" :key="n" :value="n-1">{{ n-1 }}</option>
                </select>
                <input 
                  type="number" 
                  v-model.number="edge.cost" 
                  placeholder="造价" 
                  min="1" 
                  class="input-cost"
                  title="边的造价（用于MST算法）"
                />
                <input 
                  type="number" 
                  v-model.number="edge.capacity" 
                  placeholder="容量" 
                  min="1" 
                  class="input-capacity"
                  title="边的容量（用于最大流算法）"
                />
                <button @click="removeManualEdge(idx)" class="remove-btn" title="删除此边">❌</button>
              </div>
            </div>
          </div>

          <div class="button-group" style="margin-top: 1.5rem;">
            <button @click="applyManualNetwork" :disabled="loading || manualEdges.length === 0" class="primary">
              {{ loading ? '处理中...' : '💾 生成网络' }}
            </button>
            <button @click="loadExampleManual" class="secondary">
              📝 加载示例
            </button>
            <button @click="useGeneratedNetwork" :disabled="!networkData" class="success">
              ✅ 应用到算法
            </button>
          </div>
        </div>
      </div>

      <!-- 结果展示区域 -->
      <div class="section">
        <h3>网络拓扑可视化</h3>
        
        <div v-if="error" class="error-box">
          ❌ {{ error }}
        </div>

        <div v-if="networkData" class="result-container">
          <!-- 统计信息 -->
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-label">节点数</div>
              <div class="stat-value">{{ networkData.stats.num_nodes }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">边数</div>
              <div class="stat-value">{{ networkData.stats.num_edges }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">平均造价</div>
              <div class="stat-value">{{ networkData.stats.avg_cost.toFixed(1) }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">平均容量</div>
              <div class="stat-value">{{ networkData.stats.avg_capacity.toFixed(1) }}</div>
            </div>
          </div>

          <!-- 拓扑图 -->
          <div class="topology-image">
            <img 
              v-if="networkData.topology_image" 
              :src="'data:image/png;base64,' + networkData.topology_image" 
              alt="网络拓扑图"
              class="topology-img clickable"
              @click="openImageViewer('data:image/png;base64,' + networkData.topology_image, '网络拓扑图可视化')"
              title="点击放大"
            />
          </div>

          <!-- 应用状态 -->
          <div v-if="isApplied" class="success-box" style="animation: fadeIn 0.3s ease-in;">
            ✅ 网络配置已应用！
            <div style="margin-top: 0.5rem; font-size: 0.9rem;">
              👉 请切换到“最小生成树”或“最大流”标签页，点击“加载配置网络”按钮使用
            </div>
          </div>
        </div>

        <div v-if="!networkData && !loading" class="placeholder">
          <p>👆 配置参数并生成网络拓扑</p>
        </div>
      </div>
    </div>
    
    <!-- 图片查看器 -->
    <ImageViewer 
      :src="viewerImageSrc" 
      :alt="viewerImageAlt" 
      :show="showImageViewer" 
      @close="closeImageViewer" 
    />
    
    <!-- Toast通知 -->
    <Toast 
      :message="toast.message" 
      :type="toast.type" 
      :show="toast.show" 
      @close="toast.show = false" 
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, inject } from 'vue'
import { api } from '../api/backend.js'
import ImageViewer from './ImageViewer.vue'
import Toast from './Toast.vue'

const config = reactive({
  num_nodes: 25,
  cost_range: [10, 100],
  capacity_range: [100, 1000],
  seed: 42
})

const loading = ref(false)
const error = ref(null)
const networkData = ref(null)
const isApplied = ref(false)
const mode = ref('auto') // 'auto' or 'manual'

// 图片查看器状态
const showImageViewer = ref(false)
const viewerImageSrc = ref('')
const viewerImageAlt = ref('')

// Toast通知状态
const toast = reactive({
  show: false,
  message: '',
  type: 'success'
})

function showToast(message, type = 'success') {
  toast.message = message
  toast.type = type
  toast.show = true
}

// 手动编辑模式的数据
const manualNodes = ref(5)
const manualEdges = ref([])

// 获取全局状态管理（如果存在）
const setGlobalNetwork = inject('setGlobalNetwork', null)

onMounted(async () => {
  // 加载默认配置
  try {
    const defaultConfig = await api.getDefaultNetworkConfig()
    Object.assign(config, defaultConfig)
  } catch (err) {
    console.error('加载默认配置失败:', err)
  }
})

async function generateNetwork() {
  loading.value = true
  error.value = null
  isApplied.value = false
  
  try {
    const result = await api.generateNetwork(config)
    networkData.value = result
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function loadDefaultConfig() {
  try {
    const defaultConfig = await api.getDefaultNetworkConfig()
    Object.assign(config, defaultConfig)
    error.value = null
  } catch (err) {
    error.value = '加载默认配置失败: ' + err.message
  }
}

function useGeneratedNetwork() {
  if (!networkData.value) return
  
  const dataToSave = {
    nodes: networkData.value.nodes,
    edges: networkData.value.edges,
    config: networkData.value.config
  }
  
  console.log('保存网络数据到 localStorage:', dataToSave)
  
  // 保存到 localStorage
  localStorage.setItem('campus-network-data', JSON.stringify(dataToSave))
  
  // 验证保存成功
  const saved = localStorage.getItem('campus-network-data')
  console.log('验证保存:', saved ? 'OK' : 'FAILED')
  
  // 如果有全局状态管理，也更新到全局
  if (setGlobalNetwork) {
    setGlobalNetwork(networkData.value)
  }
  
  isApplied.value = true
  
  // 显示成功通知
  showToast('网络配置已成功应用！可以在算法页面使用了', 'success')
}

function initManualEdges() {
  manualEdges.value = []
}

function addManualEdge() {
  if (manualNodes.value < 2) return
  manualEdges.value.push({
    from: 0,
    to: 1,
    cost: 10,
    capacity: 100
  })
}

function removeManualEdge(index) {
  manualEdges.value.splice(index, 1)
}

function loadExampleManual() {
  manualNodes.value = 6
  manualEdges.value = [
    { from: 0, to: 1, cost: 6, capacity: 100 },
    { from: 0, to: 3, cost: 12, capacity: 150 },
    { from: 0, to: 2, cost: 8, capacity: 120 },
    { from: 1, to: 4, cost: 7, capacity: 200 },
    { from: 1, to: 2, cost: 3, capacity: 80 },
    { from: 2, to: 3, cost: 5, capacity: 90 },
    { from: 2, to: 5, cost: 9, capacity: 110 },
    { from: 3, to: 5, cost: 4, capacity: 130 },
    { from: 4, to: 5, cost: 11, capacity: 160 }
  ]
}

async function applyManualNetwork() {
  loading.value = true
  error.value = null
  isApplied.value = false
  
  try {
    // 验证边
    for (const edge of manualEdges.value) {
      if (edge.from === edge.to) {
        throw new Error(`边 ${edge.from}-${edge.to} 不能连接到自身`)
      }
      if (edge.from < 0 || edge.from >= manualNodes.value || 
          edge.to < 0 || edge.to >= manualNodes.value) {
        throw new Error(`边 ${edge.from}-${edge.to} 的节点超出范围`)
      }
      if (!edge.cost || edge.cost <= 0 || !edge.capacity || edge.capacity <= 0) {
        throw new Error(`边 ${edge.from}-${edge.to} 的造价和容量必须大于0`)
      }
    }
    
    // 构造网络数据
    const nodes = []
    for (let i = 0; i < manualNodes.value; i++) {
      nodes.push({ id: i, label: String(i) })
    }
    
    const edges = manualEdges.value.map(e => ({
      from: e.from,
      to: e.to,
      cost: e.cost,
      capacity: e.capacity,
      weight: e.cost
    }))
    
    // 计算统计信息
    const stats = {
      num_nodes: nodes.length,
      num_edges: edges.length,
      avg_cost: edges.reduce((sum, e) => sum + e.cost, 0) / edges.length,
      avg_capacity: edges.reduce((sum, e) => sum + e.capacity, 0) / edges.length
    }
    
    // 生成拓扑图（使用API）
    const previewResult = await api.previewGraph(nodes, edges)
    
    networkData.value = {
      nodes,
      edges,
      stats,
      topology_image: previewResult.visualization,
      config: { mode: 'manual' }
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function openImageViewer(imageSrc, imageAlt) {
  viewerImageSrc.value = imageSrc
  viewerImageAlt.value = imageAlt
  showImageViewer.value = true
}

function closeImageViewer() {
  showImageViewer.value = false
}
</script>

<style scoped>
.panel {
  padding: 0;
  background: transparent;
}

.layout {
  display: grid;
  grid-template-columns: minmax(450px, 550px) 1fr;
  gap: 1.5rem;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

h2 {
  color: #667eea;
  margin: 0 0 1.5rem;
  font-size: 1.8rem;
}

h3 {
  color: #1f2937;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.75rem;
  margin: 0 0 1rem;
  font-size: 1.15rem;
  font-weight: 600;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

label {
  font-weight: 600;
  color: #555;
  font-size: 0.95rem;
}

input[type="number"] {
  padding: 0.6rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  font-family: inherit;
  transition: all 0.2s;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.range-input {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.range-input input {
  flex: 1;
  min-width: 0;
  width: 0;
}

.range-input span {
  color: #666;
  font-weight: bold;
  flex-shrink: 0;
}

.hint {
  font-size: 0.85rem;
  color: #888;
  font-style: italic;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

button {
  padding: 0.75rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

button.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

button.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

button.secondary {
  background: #f0f0f0;
  color: #666;
}

button.secondary:hover {
  background: #e0e0e0;
}

button.success {
  background: #10b981;
  color: white;
}

button.success:hover:not(:disabled) {
  background: #059669;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.error-box {
  padding: 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  color: #dc2626;
  font-weight: 500;
}

.success-box {
  padding: 1rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 10px;
  color: #16a34a;
  font-weight: 500;
}

.result-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
  margin-bottom: 0.3rem;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
}

.topology-image {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.topology-image img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.topology-image img.clickable {
  cursor: zoom-in;
}

.topology-image img.clickable:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  background: white;
  border: 2px dashed #e5e7eb;
  border-radius: 12px;
  color: #9ca3af;
  font-size: 1.1rem;
}

@media (max-width: 1024px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 模式切换按钮 */
.mode-selector {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  justify-content: center;
  background: white;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.mode-btn {
  flex: 1;
  max-width: 200px;
  padding: 1rem 1.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  background: transparent;
  color: #6b7280;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mode-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

.mode-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

/* 手动编辑区域 */
.edges-editor {
  margin-top: 1.5rem;
  padding: 1rem;
  background: white;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.edges-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.edges-header h4 {
  margin: 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
}

.edges-header-labels {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 0.75rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #6b7280;
  overflow-x: auto;
}

.label-from {
  width: 60px;
  flex-shrink: 0;
}

.select-from {
  width: 60px;
  min-width: 60px;
  flex-shrink: 0;
}

.label-to {
  width: 60px;
  flex-shrink: 0;
}

.select-to {
  width: 60px;
  min-width: 60px;
  flex-shrink: 0;
}

.label-arrow {
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.arrow {
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.label-cost {
  width: 70px;
  flex-shrink: 0;
}

.input-cost {
  width: 70px;
  min-width: 70px;
  flex-shrink: 0;
  box-sizing: border-box;
}

.label-capacity {
  width: 70px;
  flex-shrink: 0;
}

.input-capacity {
  width: 70px;
  min-width: 70px;
  flex-shrink: 0;
  box-sizing: border-box;
}

.label-action {
  width: 40px;
  text-align: center;
  flex-shrink: 0;
}

.add-edge-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.add-edge-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.edges-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 350px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 0.5rem;
}

.edge-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #fafbfc;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
  overflow-x: auto;
  min-height: 60px;
}

.edge-item:hover {
  background: white;
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.edge-item select {
  padding: 0.4rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.85rem;
  background: white;
  transition: all 0.2s;
  box-sizing: border-box;
}

.edge-item input[type="number"] {
  padding: 0.4rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.85rem;
  background: white;
  transition: all 0.2s;
  box-sizing: border-box;
}

.edge-item select:focus,
.edge-item input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.edge-item .arrow {
  font-weight: bold;
  color: #667eea;
  font-size: 1.2rem;
}

.remove-btn {
  padding: 0.3rem 0.5rem;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #ef4444;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
  width: 40px;
  min-width: 40px;
  flex-shrink: 0;
}

.remove-btn:hover {
  background: #fef2f2;
  transform: scale(1.1);
}

@media (max-width: 768px) {
  .edge-item {
    flex-wrap: wrap;
  }
  
  .edge-item input,
  .edge-item select {
    flex: 1;
    min-width: 70px;
  }
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
