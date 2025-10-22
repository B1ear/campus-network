<template>
  <div class="panel">
    <h2>🌲 最小生成树算法</h2>
    <div class="layout">
      <div class="section">
        <h3>输入数据</h3>
        <label>节点 (逗号分隔):</label>
        <input v-model="nodes" placeholder="1,2,3,4,5" />
        <label>边 (格式: from-to-weight):</label>
        <textarea v-model="edges" rows="6" placeholder="1-2-10&#10;1-3-15"></textarea>
        <div style="display: flex; gap: 1rem; margin: 1rem 0;">
          <label><input type="radio" v-model="algo" value="kruskal" /> Kruskal</label>
          <label><input type="radio" v-model="algo" value="prim" /> Prim</label>
        </div>
        <button @click="calc" :disabled="loading">{{ loading ? '计算中...' : '计算MST' }}</button>
        <button @click="example" style="background: #eee; color: #666;">示例数据</button>
      </div>
      <div class="section">
        <h3>结果</h3>
        <div v-if="error" style="padding: 1rem; background: #fee; border-radius: 6px; color: #c33;">{{ error }}</div>
        <div v-if="result">
          <div style="padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 6px; margin-bottom: 1rem;">
            <div>算法: {{ result.algorithm }}</div>
            <div style="font-size: 1.5rem; font-weight: bold;">总权重: {{ result.total_weight }}</div>
          </div>
          <h4>MST 边:</h4>
          <div v-for="(e, i) in result.mst_edges" :key="i" style="padding: 0.5rem; background: #f5f5f5; margin: 0.5rem 0; border-left: 4px solid #667eea; border-radius: 4px;">
            {{ e.from }} → {{ e.to }} <span style="color: #764ba2; font-weight: bold;">({{ e.weight }})</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { api } from '../api/backend.js'
const nodes = ref('1,2,3,4,5')
const edges = ref('1-2-10\n1-3-15\n2-3-4\n2-4-5\n3-4-8')
const algo = ref('kruskal')
const loading = ref(false)
const result = ref(null)
const error = ref(null)
const parseNodes = computed(() => nodes.value.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n)))
const parseEdges = computed(() => edges.value.split('\n').map(line => {
  const p = line.trim().split('-')
  if (p.length === 3) return { from: parseInt(p[0]), to: parseInt(p[1]), weight: parseInt(p[2]) }
  return null
}).filter(e => e))
async function calc() {
  error.value = null; result.value = null; loading.value = true
  try {
    const n = parseNodes.value; const e = parseEdges.value
    if (!n.length || !e.length) throw new Error('请输入有效数据')
    result.value = algo.value === 'kruskal' ? await api.mstKruskal(n, e) : await api.mstPrim(n, e)
  } catch (err) { error.value = err.message } finally { loading.value = false }
}
function example() { nodes.value = '1,2,3,4,5,6'; edges.value = '1-2-6\n1-4-12\n1-3-8\n2-5-7\n2-3-3\n3-4-5\n3-6-9\n4-6-4\n5-6-11' }
</script>

<style scoped>
.panel { padding: 1rem; } .layout { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
.section { display: flex; flex-direction: column; gap: 0.75rem; }
h2 { color: #667eea; margin: 0 0 1rem; } h3 { color: #333; border-bottom: 2px solid #667eea; padding-bottom: 0.5rem; margin: 0; }
label { font-weight: 600; color: #555; font-size: 0.9rem; }
input, textarea { padding: 0.6rem; border: 2px solid #ddd; border-radius: 6px; font-size: 1rem; font-family: inherit; }
input:focus, textarea:focus { outline: none; border-color: #667eea; }
button { padding: 0.75rem; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; background: #667eea; color: white; font-size: 1rem; }
button:hover:not(:disabled) { background: #5568d3; } button:disabled { opacity: 0.6; cursor: not-allowed; }
@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
</style>
