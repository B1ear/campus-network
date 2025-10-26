<template>
  <div class="panel">
    <h2>💧 最大流算法</h2>
    
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
        <div class="input-grid">
          <div class="input-group-compact">
            <label>节点:</label>
            <input v-model="nodes" placeholder="1,2,3,4" />
          </div>
          <div class="input-group-compact">
            <label>边 (from-to-capacity):</label>
            <textarea v-model="edges" rows="4" placeholder="1-2-16&#10;1-3-13"></textarea>
          </div>
          <div class="source-sink-grid">
            <div><label>源点:</label><input v-model.number="source" type="number" /></div>
            <div><label>汇点:</label><input v-model.number="sink" type="number" /></div>
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
              <div class="source-sink-inline">
                <div><label>源点:</label><input v-model.number="source" type="number" /></div>
                <div><label>汇点:</label><input v-model.number="sink" type="number" /></div>
              </div>
            </div>
            <div class="edge-stats">
              <span class="stat-item">📍 节点数: <strong>{{ parseNodes.length }}</strong></span>
              <span class="stat-item">🔗 边数: <strong>{{ visualEdges.length }}</strong></span>
            </div>
            <EdgeEditor 
              :edges="visualEdges"
              :nodes="parseNodes"
              title="边配置"
              :show-cost="false"
              :show-capacity="true"
              capacity-label="容量"
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

      <div class="algo-selector">
        <label><input type="radio" v-model="algo" value="edmonds-karp" /> Edmonds-Karp</label>
        <label><input type="radio" v-model="algo" value="dinic" /> Dinic</label>
      </div>

      <div class="button-group">
        <button @click="calc" :disabled="loading" class="primary-btn">
          {{ loading ? '🔄 计算中...' : '🚀 计算最大流' }}
        </button>
        <button @click="loadConfiguredNetwork" class="secondary-btn">
          💾 加载配置网络
        </button>
        <button @click="example" class="tertiary-btn">
          📝 示例数据
        </button>
      </div>
    </div>

    <div v-if="error" class="error-box">
      ❌ {{ error }}
    </div>

    <div class="result-section" v-if="result">
      <div class="section">
        <h3>结果</h3>
        <div v-if="result">
          <div style="padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 6px; margin-bottom: 1rem;">
            <div>算法: {{ result.algorithm }}</div>
            <div style="font-size: 1.5rem; font-weight: bold;">最大流: {{ result.max_flow }}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">源点: {{ result.source }} | 汇点: {{ result.sink }}</div>
          </div>
          
          <!-- 可视化图片 -->
          <div v-if="result.visualization" style="margin-bottom: 1.5rem; background: #f9f9f9; border: 2px solid #e0e0e0; border-radius: 8px; padding: 1rem;">
            <h4 style="margin-top: 0;">算法可视化:</h4>
            <img 
              :src="'data:image/png;base64,' + result.visualization" 
              alt="最大流可视化" 
              class="viz-image" 
              @click="openImageViewer('data:image/png;base64,' + result.visualization, result.algorithm + ' 最大流算法可视化')" 
              title="点击放大"
              style="max-width: 100%; height: auto; border-radius: 4px; cursor: zoom-in; transition: all 0.3s ease;" 
              @mouseover="$event.target.style.transform = 'scale(1.02)'; $event.target.style.boxShadow = '0 4px 16px rgba(102, 126, 234, 0.3)'"
              @mouseout="$event.target.style.transform = 'scale(1)'; $event.target.style.boxShadow = 'none'"
            />
          </div>
          
          <h4>流量分配:</h4>
          <div v-for="(e, i) in result.flow_edges" :key="i" style="padding: 0.5rem; background: #f5f5f5; margin: 0.5rem 0; border-left: 4px solid #667eea; border-radius: 4px;">
            {{ e.from }} → {{ e.to }} <span style="color: #764ba2; font-weight: bold;">流量: {{ e.flow }}</span>
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
// 生成20节点全联通图
function generateConnectedGraph() {
  const nodeCount = 20
  const nodeList = Array.from({ length: nodeCount }, (_, i) => i + 1)
  const edgeList = []
  
  // 首先生成一个生成树确保联通
  for (let i = 1; i < nodeCount; i++) {
    const from = Math.floor(Math.random() * i) + 1
    const to = i + 1
    const capacity = Math.floor(Math.random() * 80) + 20
    edgeList.push(`${from}-${to}-${capacity}`)
  }
  
  // 添加额外的边
  const additionalEdges = 20
  for (let i = 0; i < additionalEdges; i++) {
    const from = Math.floor(Math.random() * nodeCount) + 1
    const to = Math.floor(Math.random() * nodeCount) + 1
    if (from !== to) {
      const capacity = Math.floor(Math.random() * 80) + 20
      const exists = edgeList.some(e => {
        const [f, t] = e.split('-').map(Number)
        return (f === Math.min(from, to) && t === Math.max(from, to))
      })
      if (!exists) {
        edgeList.push(`${from}-${to}-${capacity}`)
      }
    }
  }
  
  return {
    nodes: nodeList.join(','),
    edges: edgeList.join('\\n')
  }
}

const defaultGraph = generateConnectedGraph()
const nodes = ref(defaultGraph.nodes)
const edges = ref(defaultGraph.edges)
const source = ref(1)
const sink = ref(20)
const algo = ref('edmonds-karp')
const loading = ref(false)
const result = ref(null)
const error = ref(null)
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
  const parsed = edges.value.split('\\n').map(line => {
    const p = line.trim().split('-')
    if (p.length === 3) {
      return { 
        from: parseInt(p[0]), 
        to: parseInt(p[1]), 
        capacity: parseInt(p[2]) 
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
    return visualEdges.value.map(e => ({ from: e.from, to: e.to, capacity: e.capacity }))
  }
  return edges.value.split('\\n').map(line => {
    const p = line.trim().split('-')
    if (p.length === 3) return { from: parseInt(p[0]), to: parseInt(p[1]), capacity: parseInt(p[2]) }
    return null
  }).filter(e => e)
})
async function calc() {
  error.value = null; result.value = null; loading.value = true
  try {
    const n = parseNodes.value; const e = parseEdges.value
    if (!n.length || !e.length) throw new Error('请输入有效数据')
    if (!n.includes(source.value) || !n.includes(sink.value)) throw new Error('源点和汇点必须在节点列表中')
    result.value = algo.value === 'edmonds-karp' ? await api.maxflowEdmondsKarp(n, e, source.value, sink.value) : await api.maxflowDinic(n, e, source.value, sink.value)
  } catch (err) { error.value = err.message } finally { loading.value = false }
}
function example() { 
  const graph = generateConnectedGraph()
  nodes.value = graph.nodes
  edges.value = graph.edges
  source.value = 1
  sink.value = 20
  if (inputMode.value === 'visual') {
    const parsed = edges.value.split('\\n').map(line => {
      const p = line.trim().split('-')
      if (p.length === 3) {
        return { 
          from: parseInt(p[0]), 
          to: parseInt(p[1]), 
          capacity: parseInt(p[2]) 
        }
      }
      return null
    }).filter(e => e)
    visualEdges.value = parsed
  }
}

function loadNetworkFromStorage() {
  try {
    const data = localStorage.getItem('campus-network-data')
    if (data) {
      const network = JSON.parse(data)
      console.log('加载的网络数据:', network)
      // 转换为面板格式
      nodes.value = network.nodes.map(n => n.id).join(',')
      edges.value = network.edges.map(e => `${e.from}-${e.to}-${e.capacity}`).join('\n')
      // 设置默认源点和汇点
      if (network.nodes.length > 0) {
        source.value = network.nodes[0].id
        sink.value = network.nodes[network.nodes.length - 1].id
      }
      return true
    }
    return false
  } catch (err) {
    console.error('加载网络数据失败:', err)
    return false
  }
}

function loadConfiguredNetwork() {
  const loaded = loadNetworkFromStorage()
  if (loaded) {
    error.value = null
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
  if (inputMode.value === 'visual') {
    setTimeout(() => refreshPreview(), 100)
  }
}

function removeVisualEdge(index) {
  visualEdges.value.splice(index, 1)
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
      capacity: e.capacity 
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
  if (newMode === 'visual' && visualEdges.value.length === 0) {
    const parsed = edges.value.split('\\n').map(line => {
      const p = line.trim().split('-')
      if (p.length === 3) {
        return { 
          from: parseInt(p[0]), 
          to: parseInt(p[1]), 
          capacity: parseInt(p[2]) 
        }
      }
      return null
    }).filter(e => e)
    visualEdges.value = parsed
    await refreshPreview()
  } else if (newMode === 'text') {
    edges.value = visualEdges.value.map(e => `${e.from}-${e.to}-${e.capacity}`).join('\\n')
  }
})

// 监听边数据变化，延迟刷新预览
let refreshTimeout = null
watch(visualEdges, () => {
  if (inputMode.value === 'visual' && visualEdges.value.length > 0) {
    if (refreshTimeout) clearTimeout(refreshTimeout)
    refreshTimeout = setTimeout(() => {
      refreshPreview()
    }, 1000)
  }
}, { deep: true })
</script>

<style scoped>
.panel { padding: 0; background: transparent; max-width: 1600px; margin: 0 auto; }

h2 { color: #667eea; margin: 0 0 1rem; font-size: 1.5rem; font-weight: 600; }

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

.mode-toggle-btn:hover { background: rgba(102, 126, 234, 0.1); color: #667eea; }
.mode-toggle-btn.active { background: white; color: #667eea; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }

.text-input-mode,
.visual-input-mode { margin-bottom: 1rem; }

.input-grid {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.input-group-compact {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-group-compact label { font-weight: 600; color: #4b5563; font-size: 0.85rem; }

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

.source-sink-grid,
.source-sink-inline {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.visual-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
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
  margin-bottom: 1rem;
}

.stat-item { font-size: 0.85rem; color: #0369a1; }
.stat-item strong { font-size: 1rem; color: #0c4a6e; }

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

.preview-header h4 { margin: 0; color: #1f2937; font-size: 0.95rem; font-weight: 600; }

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

.refresh-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3); }
.refresh-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

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

.preview-image:hover { transform: scale(1.02); box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2); }

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
.preview-placeholder p { margin: 0.5rem 0 0; font-size: 0.9rem; }

.preview-error p { color: #dc2626; }

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.algo-selector {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
}

.algo-selector label { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; }

.button-group {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.button-group button { flex: 1; min-width: 150px; }

.primary-btn,
.secondary-btn,
.tertiary-btn {
  padding: 0.7rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.3s;
}

.primary-btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.primary-btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3); }

.secondary-btn { background: #10b981; color: white; }
.secondary-btn:hover:not(:disabled) { background: #059669; }

.tertiary-btn { background: #f0f0f0; color: #666; }
.tertiary-btn:hover { background: #e0e0e0; }

button:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }

.error-box {
  padding: 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  color: #dc2626;
  font-weight: 500;
  margin-bottom: 1.5rem;
}

.layout { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.result-section { margin-top: 1.5rem; }
.section {
  display: flex; 
  flex-direction: column; 
  gap: 0.75rem;
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

h3 { color: #1f2937; border-bottom: 2px solid #667eea; padding-bottom: 0.75rem; margin: 0 0 1rem; font-size: 1.15rem; font-weight: 600; }
h4 { color: #1f2937; margin: 1rem 0 0.5rem; font-size: 1rem; font-weight: 600; }

@media (max-width: 1200px) {
  .visual-layout { grid-template-columns: 1fr; }
  .preview-container { min-height: 300px; }
}

@media (max-width: 900px) { 
  .layout { grid-template-columns: 1fr; }
  .input-grid { grid-template-columns: 1fr; }
}
</style>
