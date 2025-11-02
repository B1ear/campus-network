<template>
  <div class="app">
    <header class="header">
      <h1>🌐 校园网络算法可视化平台</h1>
      <p class="subtitle">最小生成树 · 最大流 · AES加密</p>
    </header>

    <div class="container">
      <div class="main-layout">
        <div class="sidebar">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            :class="['tab-button', { active: activeTab === tab.id }]"
            @click="activeTab = tab.id"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-name">{{ tab.name }}</span>
          </button>
        </div>

        <div class="content">
          <NetworkConfigPanel v-if="activeTab === 'network'" />
          <InteractiveTrafficPanel v-if="activeTab === 'interactive'" />
          <MSTPanel v-if="activeTab === 'mst'" />
          <MaxFlowPanel v-if="activeTab === 'maxflow'" />
          <AESPanel v-if="activeTab === 'aes'" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import MSTPanel from './components/MSTPanel.vue'
import MaxFlowPanel from './components/MaxFlowPanel.vue'
import AESPanel from './components/AESPanel.vue'
import NetworkConfigPanel from './components/NetworkConfigPanel.vue'
import InteractiveTrafficPanel from './components/InteractiveTrafficPanel.vue'

const activeTab = ref('network')
const globalNetwork = ref(null)

// 提供全局网络状态
const setGlobalNetwork = (networkData) => {
  globalNetwork.value = networkData
}

provide('globalNetwork', globalNetwork)
provide('setGlobalNetwork', setGlobalNetwork)

const tabs = [
  { id: 'network', name: '网络配置', icon: '🌐' },
  { id: 'mst', name: '最小生成树', icon: '🌲' },
  { id: 'maxflow', name: '最大流', icon: '💧' },
  { id: 'aes', name: 'AES加密', icon: '🔐' },
  { id: 'interactive', name: '交互式仿真', icon: '🎮' },
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
  padding: 0.8rem 1rem 0.6rem;
  color: white;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(25px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.25);
  position: relative;
  overflow: hidden;
}

.header::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  animation: pulse 8s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.5; }
  50% { transform: translate(10%, 10%) scale(1.1); opacity: 0.8; }
}

.header h1 {
  margin: 0;
  font-size: 2.2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 50%, #ffffff 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: none;
  letter-spacing: 0.5px;
  animation: shimmer 3s linear infinite;
  position: relative;
  z-index: 1;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.3));
  line-height: 1.2;
}

@keyframes shimmer {
  to { background-position: 200% center; }
}

.subtitle {
  margin: 0.5rem 0 0;
  font-size: 0.95rem;
  opacity: 0.95;
  font-weight: 500;
  letter-spacing: 2px;
  position: relative;
  z-index: 1;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.container {
  flex: 1;
  width: 100%;
  display: flex;
  overflow: hidden;
}

.main-layout {
  display: flex;
  width: 100%;
  height: calc(100vh - 90px);
  gap: 0;
}

.sidebar {
  width: 70px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  padding: 1.5rem 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  border-right: 1px solid rgba(0, 0, 0, 0.06);
  overflow: visible;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 100;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.05);
}

.sidebar:hover {
  width: 220px;
}

.tab-button {
  width: 100%;
  padding: 0.85rem;
  font-size: 0.9rem;
  font-weight: 500;
  border: none;
  border-radius: 12px;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  overflow: hidden;
  white-space: nowrap;
}

.tab-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.tab-name {
  flex: 1;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar:hover .tab-name {
  opacity: 1;
  transform: translateX(0);
}

.tab-button:hover {
  background: rgba(102, 126, 234, 0.08);
  color: #667eea;
}

.tab-button:hover .tab-icon {
  transform: scale(1.1);
}

.tab-button.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.25);
}

.tab-button.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: white;
  border-radius: 0 3px 3px 0;
}

.tab-button.active .tab-icon {
  transform: scale(1.1);
}

.content {
  flex: 1;
  background: #fafbfc;
  padding: 2rem;
  overflow-y: auto;
  overflow-x: hidden;
}


@media (max-width: 968px) {
  .header h1 {
    font-size: 1.5rem;
  }

  .main-layout {
    flex-direction: column;
    height: auto;
  }

  .sidebar {
    width: 100% !important;
    flex-direction: row;
    padding: 1rem;
    border-right: none;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    overflow-x: auto;
    overflow-y: hidden;
    gap: 0.5rem;
  }

  .sidebar:hover {
    width: 100% !important;
  }

  .tab-button {
    min-width: 120px;
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
    padding: 0.75rem 0.5rem;
    flex-shrink: 0;
  }

  .tab-button.active::before {
    display: none;
  }

  .tab-button:hover {
    transform: translateY(-2px);
  }

  .tab-name {
    opacity: 1 !important;
    transform: translateX(0) !important;
    font-size: 0.75rem;
  }

  .tab-icon {
    font-size: 1.5rem;
  }

  .content {
    padding: 1rem;
    height: auto;
  }
}
</style>