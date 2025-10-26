<template>
  <div class="edge-editor">
    <div class="editor-header">
      <h4>{{ title }}</h4>
      <button @click="addEdge" class="add-edge-btn">➕ 添加边</button>
    </div>
    
    <!-- 列标题 -->
    <div v-if="edges.length > 0" class="edge-header-labels">
      <span class="label-from">起点</span>
      <span class="label-arrow"></span>
      <span class="label-to">终点</span>
      <span v-if="showCost" class="label-cost">{{ costLabel }}</span>
      <span v-if="showCapacity" class="label-capacity">{{ capacityLabel }}</span>
      <span class="label-action">操作</span>
    </div>
    
    <div class="edges-list">
      <div v-for="(edge, idx) in edges" :key="idx" class="edge-item">
        <select v-model.number="edge.from" class="select-from" :title="`起点节点`">
          <option v-for="n in availableNodes" :key="n" :value="n">{{ n }}</option>
        </select>
        <span class="arrow">→</span>
        <select v-model.number="edge.to" class="select-to" :title="`终点节点`">
          <option v-for="n in availableNodes" :key="n" :value="n">{{ n }}</option>
        </select>
        <input 
          v-if="showCost"
          type="number" 
          v-model.number="edge.cost" 
          :placeholder="costLabel" 
          min="1" 
          class="input-cost"
          :title="`边的${costLabel}`"
        />
        <input 
          v-if="showCapacity"
          type="number" 
          v-model.number="edge.capacity" 
          :placeholder="capacityLabel" 
          min="1" 
          class="input-capacity"
          :title="`边的${capacityLabel}`"
        />
        <button @click="removeEdge(idx)" class="remove-btn" title="删除此边">❌</button>
      </div>
    </div>
    
    <div v-if="edges.length === 0" class="empty-state">
      点击"➕ 添加边"按钮开始配置
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  edges: {
    type: Array,
    required: true
  },
  nodes: {
    type: Array,
    required: true
  },
  title: {
    type: String,
    default: '边配置'
  },
  showCost: {
    type: Boolean,
    default: true
  },
  showCapacity: {
    type: Boolean,
    default: true
  },
  costLabel: {
    type: String,
    default: '造价'
  },
  capacityLabel: {
    type: String,
    default: '容量'
  }
})

const emit = defineEmits(['update:edges', 'add-edge', 'remove-edge'])

const availableNodes = computed(() => {
  return props.nodes
})

function addEdge() {
  const newEdge = {
    from: props.nodes[0] || 0,
    to: props.nodes[1] || 1
  }
  
  if (props.showCost) {
    newEdge.cost = 10
  }
  if (props.showCapacity) {
    newEdge.capacity = 100
  }
  
  emit('add-edge', newEdge)
}

function removeEdge(index) {
  emit('remove-edge', index)
}
</script>

<style scoped>
.edge-editor {
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.editor-header h4 {
  margin: 0;
  color: #1f2937;
  font-size: 0.9rem;
  font-weight: 600;
}

.add-edge-btn {
  padding: 0.35rem 0.7rem;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(16, 185, 129, 0.2);
}

.add-edge-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.edge-header-labels {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.5rem;
  background: white;
  border-radius: 6px;
  margin-bottom: 0.5rem;
  font-size: 0.7rem;
  font-weight: 600;
  color: #6b7280;
}

.label-from,
.select-from {
  width: 55px;
  flex-shrink: 0;
}

.label-to,
.select-to {
  width: 55px;
  flex-shrink: 0;
}

.label-arrow,
.arrow {
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.label-cost,
.input-cost {
  width: 65px;
  flex-shrink: 0;
}

.label-capacity,
.input-capacity {
  width: 65px;
  flex-shrink: 0;
}

.label-action {
  width: 36px;
  text-align: center;
  flex-shrink: 0;
}

.edges-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 350px;
  overflow-y: auto;
  overflow-x: hidden;
}

.edge-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.edge-item:hover {
  border-color: #667eea;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.1);
}

.edge-item select {
  padding: 0.3rem;
  border: 1px solid #e5e7eb;
  border-radius: 5px;
  font-size: 0.75rem;
  background: #fafbfc;
  transition: all 0.2s;
  box-sizing: border-box;
}

.edge-item input[type="number"] {
  padding: 0.3rem;
  border: 1px solid #e5e7eb;
  border-radius: 5px;
  font-size: 0.75rem;
  background: #fafbfc;
  transition: all 0.2s;
  box-sizing: border-box;
}

.edge-item select:focus,
.edge-item input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.edge-item .arrow {
  font-weight: bold;
  color: #667eea;
  font-size: 1.1rem;
}

.remove-btn {
  padding: 0.25rem 0.4rem;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #ef4444;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  width: 36px;
  min-width: 36px;
  flex-shrink: 0;
}

.remove-btn:hover {
  background: #fef2f2;
  transform: scale(1.1);
}

.empty-state {
  text-align: center;
  padding: 1.5rem 1rem;
  color: #9ca3af;
  font-size: 0.85rem;
}
</style>
