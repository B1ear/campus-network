<template>
  <div class="app">
    <header class="header">
      <h1>🌐 校园网络算法可视化平台</h1>
      <p class="subtitle">最小生成树 · 最大流 · AES加密</p>
    </header>

    <div class="container">
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="['tab-button', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          {{ tab.icon }} {{ tab.name }}
        </button>
      </div>

      <div class="content">
        <MSTPanel v-if="activeTab === 'mst'" />
        <MaxFlowPanel v-if="activeTab === 'maxflow'" />
        <AESPanel v-if="activeTab === 'aes'" />
      </div>
    </div>

    <footer class="footer">
      <p>Campus Network Visualization Platform © 2025</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MSTPanel from './components/MSTPanel.vue'
import MaxFlowPanel from './components/MaxFlowPanel.vue'
import AESPanel from './components/AESPanel.vue'

const activeTab = ref('mst')

const tabs = [
  { id: 'mst', name: '最小生成树', icon: '🌲' },
  { id: 'maxflow', name: '最大流', icon: '💧' },
  { id: 'aes', name: 'AES加密', icon: '🔐' },
]
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  text-align: center;
  padding: 2rem 1rem;
  color: white;
  background: rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.header h1 {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.subtitle {
  margin: 0.5rem 0 0;
  font-size: 1.1rem;
  opacity: 0.95;
}

.container {
  flex: 1;
  max-width: 1400px;
  width: 100%;
  margin: 2rem auto;
  padding: 0 1rem;
}

.tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.tab-button {
  flex: 1;
  min-width: 150px;
  padding: 1rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.tab-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  background: white;
}

.tab-button.active {
  background: white;
  color: #764ba2;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.content {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  min-height: 500px;
}

.footer {
  text-align: center;
  padding: 1.5rem;
  color: white;
  background: rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  margin-top: 2rem;
}

.footer p {
  margin: 0;
  opacity: 0.9;
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 1.8rem;
  }

  .tabs {
    flex-direction: column;
  }

  .tab-button {
    min-width: 100%;
  }

  .content {
    padding: 1rem;
  }
}
</style>