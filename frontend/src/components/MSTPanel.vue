<template>
  <div class="panel">
    <h2>🌲 最小生成树算法比较</h2>
    
    <!-- 输入区域 -->
    <div class="input-section">
      <div class="input-mode-selector">
        <button 
          :class="['mode-toggle-btn', { active: inputMode === 'text' }]" 
          @click="inputMode = 'text'"
        >
          📝 文本输入
        </button>
        <button 
          :class="['mode-toggle-btn', { active: inputMode === 'visual' }]" 
          @click="inputMode = 'visual'"
        >
          🎨 可视化配置
        </button>
      </div>

      <!-- 文本输入模式 -->
      <div v-if="inputMode === 'text'" class="text-input-mode">
        <div class="input-row">
          <div class="input-group-compact">
            <label>节点:</label>
            <input v-model="nodes" placeholder="1,2,3,4,5" />
          </div>
          <div class="input-group-compact">
            <label>边 (from-to-weight):</label>
            <textarea v-model="edges" rows="3" placeholder="1-2-10&#10;1-3-15&#10;2-3-4"></textarea>
          </div>
        </div>
      </div>

      <!-- 可视化配置模式 -->
      <div v-if="inputMode === 'visual'" class="visual-input-mode">
        <div class="visual-layout">
          <div class="visual-config-section">
            <div class="visual-input-grid">
              <div class="input-group-compact">
                <label>节点 (逗号分隔):</label>
                <input v-model="nodes" placeholder="1,2,3,4,5" @input="updateVisualNodes" />
              </div>
              <div class="edge-stats">
                <span class="stat-item">📍 节点数: <strong>{{ parseNodes.length }}</strong></span>
                <span class="stat-item">🔗 边数: <strong>{{ visualEdges.length }}</strong></span>
              </div>
            </div>
            <EdgeEditor 
              :edges="visualEdges"
              :nodes="parseNodes"
              title="边配置"
              :show-cost="true"
              :show-capacity="false"
              cost-label="权重"
              @add-edge="addVisualEdge"
              @remove-edge="removeVisualEdge"
            />
          </div>
          
          <!-- 实时图预览 -->
          <div class="graph-preview-section">
            <div class="preview-header">
              <h4>🖼️ 原路由图预览</h4>
              <button @click="refreshPreview" class="refresh-btn" :disabled="previewLoading">
                {{ previewLoading ? '🔄' : '🔄 刷新' }}
              </button>
            </div>
            <div class="preview-container">
              <div v-if="previewLoading" class="preview-loading">
                <div class="spinner"></div>
                <p>生成中...</p>
              </div>
              <div v-else-if="previewError" class="preview-error">
                <p>⚠️ {{ previewError }}</p>
              </div>
              <img 
                v-else-if="previewImage" 
                :src="previewImage" 
                alt="路由图预览"
                class="preview-image"
                @click="openImageViewer(previewImage, '原路由图预览')"
                title="点击放大"
              />
              <div v-else class="preview-placeholder">
                <p>📝 配置边后点击刷新查看预览</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="button-group">
        <button @click="calc" :disabled="loading" class="primary-btn">
          {{ loading ? '🔄 计算中...' : '🚀 比较 Kruskal 与 Prim' }}
        </button>
        <button @click="loadConfiguredNetwork" class="secondary-btn">
          💾 加载配置网络
        </button>
        <button @click="example" class="tertiary-btn">
          📝 示例数据
        </button>
      </div>
    </div>

    <!-- 加载进度提示 -->
    <div v-if="loading && loadingMessage" class="loading-box">
      <div class="loading-spinner"></div>
      <div class="loading-text">{{ loadingMessage }}</div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-box">
      ❌ {{ error }}
    </div>

    <!-- 结果对比区域 -->
    <div v-if="result" class="results-container">
      <!-- 性能对比卡片 -->
      <div class="comparison-card">
        <h3>⚡ 性能对比</h3>
        <div class="comparison-grid">
          <div class="metric-card kruskal">
            <div class="metric-label">Kruskal 算法</div>
            <div class="metric-value">{{ result.kruskal.time_ms.toFixed(4) }} ms</div>
            <div class="metric-extra">总权重: {{ result.kruskal.total_weight }}</div>
          </div>
          <div class="vs-divider">
            <div class="vs-icon">VS</div>
            <div class="winner" v-if="result.comparison.faster_algorithm">
              🏆 {{ result.comparison.faster_algorithm }} 更快
              <br>
              <small>快 {{ result.comparison.time_difference_ms.toFixed(4) }} ms</small>
            </div>
          </div>
          <div class="metric-card prim">
            <div class="metric-label">Prim 算法</div>
            <div class="metric-value">{{ result.prim.time_ms.toFixed(4) }} ms</div>
            <div class="metric-extra">总权重: {{ result.prim.total_weight }}</div>
          </div>
        </div>
        <div class="validation" :class="{ valid: result.comparison.weights_match }">
          {{ result.comparison.weights_match ? '✅ 两种算法结果一致' : '⚠️ 结果不一致，请检查数据' }}
        </div>
      </div>

      <!-- 动画演示区域 -->
      <div class="animation-section" v-if="result && (result.kruskal.steps || result.prim.steps)">
        <h3 class="section-title">🎬 算法动态演示</h3>
        <div class="animation-grid">
          <div class="animation-wrapper" v-if="result.kruskal.steps">
            <AnimationPlayer 
              :steps="result.kruskal.steps" 
              title="Kruskal 算法步骤"
              @step-change="onKruskalStepChange"
            />
          </div>
          <div class="animation-wrapper" v-if="result.prim.steps">
            <AnimationPlayer 
              :steps="result.prim.steps" 
              title="Prim 算法步骤"
              @step-change="onPrimStepChange"
            />
          </div>
        </div>
      </div>
      
      <!-- 可视化对比 -->
      <div class="visualization-comparison">
        <div class="viz-card">
          <h3>🔴 Kruskal 算法结果</h3>
          <img :src="'data:image/png;base64,' + result.kruskal.visualization" 
               alt="Kruskal可视化" 
               class="viz-image clickable" 
               @click="openImageViewer('data:image/png;base64,' + result.kruskal.visualization, 'Kruskal 最小生成树算法可视化')" 
               title="点击放大" />
          <div class="edge-list">
            <h4>MST 边 ({{ result.kruskal.mst_edges.length }} 条):</h4>
            <div class="edges-grid">
              <div v-for="(e, i) in result.kruskal.mst_edges" :key="i" class="edge-item">
                {{ e.from }} → {{ e.to }} <span class="weight">({{ e.weight }})</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="viz-card">
          <h3>🔵 Prim 算法结果</h3>
          <img :src="'data:image/png;base64,' + result.prim.visualization" 
               alt="Prim可视化" 
               class="viz-image clickable" 
               @click="openImageViewer('data:image/png;base64,' + result.prim.visualization, 'Prim 最小生成树算法可视化')" 
               title="点击放大" />
          <div class="edge-list">
            <h4>MST 边 ({{ result.prim.mst_edges.length }} 条):</h4>
            <div class="edges-grid">
              <div v-for="(e, i) in result.prim.mst_edges" :key="i" class="edge-item">
                {{ e.from }} → {{ e.to }} <span class="weight">({{ e.weight }})</span>
              </div>
            </div>
          </div>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject, watch } from 'vue'
import { api } from '../api/backend.js'
import ImageViewer from './ImageViewer.vue'
import EdgeEditor from './EdgeEditor.vue'
import AnimationPlayer from './AnimationPlayer.vue'
// 生成20节点全联通图
function generateConnectedGraph() {
  const nodeCount = 20
  const nodeList = Array.from({ length: nodeCount }, (_, i) => i + 1)
  const edgeList = []
  
  // 首先生成一个生成树确保联通
  for (let i = 1; i < nodeCount; i++) {
    const from = Math.floor(Math.random() * i) + 1
    const to = i + 1
    const weight = Math.floor(Math.random() * 50) + 10
    edgeList.push(`${from}-${to}-${weight}`)
  }
  
  // 添加额外的边使图更丰富（约20条额外边）
  const additionalEdges = 20
  for (let i = 0; i < additionalEdges; i++) {
    const from = Math.floor(Math.random() * nodeCount) + 1
    const to = Math.floor(Math.random() * nodeCount) + 1
    if (from !== to) {
      const weight = Math.floor(Math.random() * 50) + 10
      // 检查边是否已存在
      const edgeStr = `${Math.min(from, to)}-${Math.max(from, to)}-${weight}`
      const exists = edgeList.some(e => {
        const [f, t] = e.split('-').map(Number)
        return (f === Math.min(from, to) && t === Math.max(from, to))
      })
      if (!exists) {
        edgeList.push(`${from}-${to}-${weight}`)
      }
    }
  }
  
  return {
    nodes: nodeList.join(','),
    edges: edgeList.join('\\n')
  }
}

// 使用指定的默认图数据
const defaultExampleData = {
  nodes: '1,2,3,4,5,6,7,8',
  edges: '1-2-6\n1-4-12\n1-3-8\n2-4-7\n2-5-8\n2-6-13\n3-6-12\n3-7-11\n4-5-5\n4-7-6\n5-6-12\n5-8-15\n6-7-4\n6-8-7\n7-8-5'
}
const nodes = ref(defaultExampleData.nodes)
const edges = ref(defaultExampleData.edges)
const algo = ref('kruskal')
const loading = ref(false)
const result = ref(null)
const error = ref(null)
const loadingMessage = ref('')
const inputMode = ref('visual') // 'text' or 'visual'
const visualEdges = ref([])
const previewImage = ref(null)
const previewLoading = ref(false)
const previewError = ref(null)

// 图片查看器状态
const showImageViewer = ref(false)
const viewerImageSrc = ref('')
const viewerImageAlt = ref('')

// 获取全局网络配置
const globalNetwork = inject('globalNetwork', null)

onMounted(async () => {
  // 初始化可视化边数据
  const parsed = edges.value.split('\n').map(line => {
    const p = line.trim().split('-')
    if (p.length === 3) {
      return { 
        from: parseInt(p[0]), 
        to: parseInt(p[1]), 
        cost: parseInt(p[2]) 
      }
    }
    return null
  }).filter(e => e)
  visualEdges.value = parsed
  
  // 自动生成预览
  await refreshPreview()
})
const parseNodes = computed(() => nodes.value.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n)))
const parseEdges = computed(() => {
  if (inputMode.value === 'visual') {
    return visualEdges.value.map(e => ({ from: e.from, to: e.to, weight: e.cost }))
  }
  return edges.value.split('\n').map(line => {
    const p = line.trim().split('-')
    if (p.length === 3) return { from: parseInt(p[0]), to: parseInt(p[1]), weight: parseInt(p[2]) }
    return null
  }).filter(e => e)
})

async function calc() {
  error.value = null
  result.value = null
  loading.value = true
  
  try {
    const n = parseNodes.value
    const e = parseEdges.value
    
    if (!n.length || !e.length) {
      throw new Error('请输入有效数据')
    }
    
    // 显示计算进度
    loadingMessage.value = '正在比较Kruskal和Prim算法...'
    
    // 调用比较接口，同时运行两种算法
    result.value = await api.mstCompare(n, e)
    
    loadingMessage.value = '完成！'
    await new Promise(resolve => setTimeout(resolve, 500))
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
    loadingMessage.value = ''
  }
}
function example() { 
  // 使用指定的示例数据
  nodes.value = defaultExampleData.nodes
  edges.value = defaultExampleData.edges
  
  // 无论在什么模式下都同步更新visualEdges
  const parsed = edges.value.split('\n').map(line => {
    const p = line.trim().split('-')
    if (p.length === 3) {
      return { 
        from: parseInt(p[0]), 
        to: parseInt(p[1]), 
        cost: parseInt(p[2]) 
      }
    }
    return null
  }).filter(e => e)
  visualEdges.value = parsed
  
  // 如果在可视化模式,刷新预览
  if (inputMode.value === 'visual') {
    setTimeout(() => refreshPreview(), 100)
  }
}

function loadNetworkFromStorage() {
  try {
    const data = localStorage.getItem('campus-network-data')
    if (data) {
      const network = JSON.parse(data)
      console.log('加载的网络数据:', network)
      console.log('边数据:', network.edges)
      
      // 转换为面板格式，最小生成树使用cost（造价）
      nodes.value = network.nodes.map(n => n.id).join(',')
      edges.value = network.edges.map(e => `${e.from}-${e.to}-${e.cost}`).join('\n')
      
      console.log('转换后的edges:', edges.value)
      
      // 直接从网络数据构建 visualEdges
      visualEdges.value = network.edges.map(e => ({
        from: e.from,
        to: e.to,
        cost: e.cost
      }))
      
      console.log('更新后的visualEdges:', visualEdges.value)
      
      // 如枟在可视化模式，刷新预览
      if (inputMode.value === 'visual') {
        setTimeout(() => refreshPreview(), 200)
      }
      
      return true
    }
    return false
  } catch (err) {
    console.error('加载网络数据失败:', err)
    console.error(err)
    return false
  }
}

function loadConfiguredNetwork() {
  const loaded = loadNetworkFromStorage()
  if (loaded) {
    error.value = null
    // 显示成功消息（可选）
    console.log('网络配置已加载')
  } else {
    error.value = '未找到配置的网络，请先在"网络配置"标签页生成并应用网络'
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

function addVisualEdge(edge) {
  visualEdges.value.push(edge)
  // 自动刷新预览
  if (inputMode.value === 'visual') {
    setTimeout(() => refreshPreview(), 100)
  }
}

function removeVisualEdge(index) {
  visualEdges.value.splice(index, 1)
  // 自动刷新预览
  if (inputMode.value === 'visual') {
    setTimeout(() => refreshPreview(), 100)
  }
}

function updateVisualNodes() {
  // 当节点改变时，更新可视化边配置器
}

async function refreshPreview() {
  if (parseNodes.value.length === 0 || visualEdges.value.length === 0) {
    previewError.value = '请先配置节点和边'
    return
  }
  
  previewLoading.value = true
  previewError.value = null
  
  try {
    const edges = visualEdges.value.map(e => ({ 
      from: e.from, 
      to: e.to, 
      weight: e.cost 
    }))
    
    // 调用原始图预览API
    const response = await api.previewGraph(parseNodes.value, edges)
    if (response && response.visualization) {
      previewImage.value = 'data:image/png;base64,' + response.visualization
    }
  } catch (err) {
    previewError.value = '生成预览失败: ' + err.message
  } finally {
    previewLoading.value = false
  }
}

// 监听输入模式切换
watch(inputMode, async (newMode) => {
  if (newMode === 'visual') {
    // 从文本模式切换到可视化模式时，总是解析现有边数据
    const parsed = edges.value.split('\n').map(line => {
      const p = line.trim().split('-')
      if (p.length === 3) {
        return { 
          from: parseInt(p[0]), 
          to: parseInt(p[1]), 
          cost: parseInt(p[2]) 
        }
      }
      return null
    }).filter(e => e)
    visualEdges.value = parsed
    // 刷新预览
    if (parsed.length > 0) {
      await refreshPreview()
    }
  } else if (newMode === 'text') {
    // 从可视化模式切换回文本模式时，同步数据
    edges.value = visualEdges.value.map(e => `${e.from}-${e.to}-${e.cost}`).join('\n')
  }
})

// 监听边数据变化，延迟刷新预览
let refreshTimeout = null
watch(visualEdges, () => {
  if (inputMode.value === 'visual' && visualEdges.value.length > 0) {
    // 防抖，避免频繁刷新
    if (refreshTimeout) clearTimeout(refreshTimeout)
    refreshTimeout = setTimeout(() => {
      refreshPreview()
    }, 1000)
  }
}, { deep: true })

// 动画步骤变化处理
function onKruskalStepChange(stepIndex, stepData) {
  // 可以在这里添加额外的视觉反馈
  console.log('Kruskal step:', stepIndex, stepData)
}

function onPrimStepChange(stepIndex, stepData) {
  // 可以在这里添加额外的视觉反馈
  console.log('Prim step:', stepIndex, stepData)
}
</script>

<style scoped>
.panel {
  padding: 0;
  max-width: 1600px;
  margin: 0 auto;
  background: transparent;
}

h2 {
  color: #667eea;
  margin: 0 0 1rem;
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 输入区域 */
.input-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.input-mode-selector {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding: 0.4rem;
  background: #f3f4f6;
  border-radius: 8px;
}

.mode-toggle-btn {
  flex: 1;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #6b7280;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.mode-toggle-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.mode-toggle-btn.active {
  background: white;
  color: #667eea;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.text-input-mode,
.visual-input-mode {
  margin-bottom: 1rem;
}

.visual-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.input-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1rem;
}

.visual-input-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: end;
}

.edge-stats {
  display: flex;
  gap: 1rem;
  padding: 0.6rem 1rem;
  background: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #bae6fd;
}

.stat-item {
  font-size: 0.85rem;
  color: #0369a1;
}

.stat-item strong {
  font-size: 1rem;
  color: #0c4a6e;
}

/* 图预览区域 */
.graph-preview-section {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 10px;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e5e7eb;
}

.preview-header h4 {
  margin: 0;
  color: #1f2937;
  font-size: 0.95rem;
  font-weight: 600;
}

.refresh-btn {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
}

.refresh-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.preview-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: #fafbfc;
  border-radius: 8px;
  position: relative;
}

.preview-image {
  max-width: 100%;
  max-height: 500px;
  border-radius: 6px;
  cursor: zoom-in;
  transition: all 0.3s ease;
}

.preview-image:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
}

.preview-loading,
.preview-error,
.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #6b7280;
}

.preview-loading p,
.preview-error p,
.preview-placeholder p {
  margin: 0.5rem 0 0;
  font-size: 0.9rem;
}

.preview-error p {
  color: #dc2626;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .visual-layout {
    grid-template-columns: 1fr;
  }
  
  .preview-container {
    min-height: 300px;
  }
}

.input-group-compact {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-group-compact label {
  font-weight: 600;
  color: #4b5563;
  font-size: 0.85rem;
}

.input-group-compact input,
.input-group-compact textarea {
  padding: 0.6rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  transition: all 0.2s;
}

.input-group-compact input:focus,
.input-group-compact textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-group label {
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
}

.input-group input,
.input-group textarea {
  padding: 0.6rem;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.3s;
}

.input-group input:focus,
.input-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.button-group {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.button-group button {
  flex: 1;
  min-width: 150px;
}

.primary-btn {
  padding: 0.7rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 0.95rem;
  transition: all 0.3s;
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.secondary-btn {
  padding: 0.65rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  background: #10b981;
  color: white;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.secondary-btn:hover {
  background: #059669;
}

.tertiary-btn {
  padding: 0.65rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  background: #f0f0f0;
  color: #666;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.tertiary-btn:hover {
  background: #e0e0e0;
}

/* 加载进度提示 */
.loading-box {
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  font-weight: 600;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  animation: slideIn 0.3s ease-out;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-text {
  font-size: 1rem;
  flex: 1;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 错误提示 */
.error-box {
  padding: 1rem;
  background: #fee;
  border: 2px solid #fcc;
  border-radius: 8px;
  color: #c33;
  font-weight: 500;
  margin-bottom: 1.5rem;
}

/* 结果区域 */
.results-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 性能对比卡片 */
.comparison-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.comparison-card h3 {
  color: #333;
  margin: 0 0 1.2rem;
  font-size: 1.15rem;
  font-weight: 600;
  text-align: center;
}

.comparison-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 2rem;
  align-items: center;
  margin-bottom: 1rem;
}

.metric-card {
  padding: 1.2rem;
  border-radius: 8px;
  text-align: center;
}

.metric-card.kruskal {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.metric-card.prim {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.metric-label {
  font-size: 0.9rem;
  opacity: 0.9;
  margin-bottom: 0.4rem;
}

.metric-value {
  font-size: 1.6rem;
  font-weight: bold;
  margin-bottom: 0.4rem;
}

.metric-extra {
  font-size: 0.85rem;
  opacity: 0.85;
}

.vs-divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.vs-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.winner {
  padding: 0.6rem 1.2rem;
  background: #fff7ed;
  border: 2px solid #fbbf24;
  border-radius: 6px;
  color: #92400e;
  font-weight: 600;
  text-align: center;
  font-size: 0.9rem;
}

.winner small {
  font-size: 0.85rem;
  opacity: 0.8;
}

.validation {
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}

.validation.valid {
  background: #d1fae5;
  border: 2px solid #6ee7b7;
  color: #065f46;
}

/* 可视化对比 */
.visualization-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.viz-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.viz-card h3 {
  color: #333;
  margin: 0 0 0.8rem;
  font-size: 1.05rem;
  font-weight: 600;
  border-bottom: 3px solid;
  padding-bottom: 0.4rem;
}

.viz-card:first-child h3 {
  border-color: #f5576c;
}

.viz-card:last-child h3 {
  border-color: #4facfe;
}

.viz-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
  border: 2px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.viz-image.clickable {
  cursor: zoom-in;
}

.viz-image.clickable:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  border-color: #667eea;
}

.edge-list {
  margin-top: 1rem;
}

.edge-list h4 {
  color: #555;
  font-size: 1rem;
  margin: 0 0 0.75rem;
}

.edges-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
}

.edge-item {
  padding: 0.5rem;
  background: #f5f5f5;
  border-radius: 6px;
  font-size: 0.9rem;
  text-align: center;
  border-left: 3px solid #667eea;
}

.edge-item .weight {
  color: #764ba2;
  font-weight: bold;
}

/* 动画区域 */
.animation-section {
  margin-bottom: 2rem;
}

.section-title {
  color: #1f2937;
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0 0 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 3px solid #667eea;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.animation-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.animation-wrapper {
  min-width: 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .input-section {
    grid-template-columns: 1fr;
  }
  
  .visualization-comparison {
    grid-template-columns: 1fr;
  }
  
  .comparison-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .animation-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .panel {
    padding: 1rem;
  }
  
  h2 {
    font-size: 1.5rem;
  }
  
  .metric-value {
    font-size: 1.5rem;
  }
  
  .edges-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
}
</style>
