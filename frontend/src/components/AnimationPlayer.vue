<template>
  <div class="animation-player" v-if="steps && steps.length > 0">
    <div class="player-header">
      <h3>{{ title }}</h3>
      <span class="step-counter">步骤 {{ currentStep + 1 }} / {{ steps.length }}</span>
    </div>
    
    <div class="step-description">
      {{ steps[currentStep]?.description || '' }}
    </div>
    
    <div class="step-visualization" v-if="steps[currentStep]?.visualization">
      <img 
        :src="'data:image/png;base64,' + steps[currentStep].visualization" 
        alt="算法步骤可视化"
        class="viz-image clickable"
        @click="handleImageClick"
        title="点击放大"
      />
    </div>
    
    <div class="controls">
      <button @click="goToStart" :disabled="currentStep === 0" class="control-btn">
        ⏮️ 开始
      </button>
      <button @click="previousStep" :disabled="currentStep === 0" class="control-btn">
        ⏪ 上一步
      </button>
      <button @click="togglePlay" class="control-btn play-btn">
        {{ isPlaying ? '⏸️ 暂停' : '▶️ 播放' }}
      </button>
      <button @click="nextStep" :disabled="currentStep === steps.length - 1" class="control-btn">
        ⏩ 下一步
      </button>
      <button @click="goToEnd" :disabled="currentStep === steps.length - 1" class="control-btn">
        ⏭️ 结束
      </button>
    </div>
    
    <div class="speed-control">
      <label>播放速度:</label>
      <input 
        type="range" 
        v-model.number="speed" 
        min="0.5" 
        max="3" 
        step="0.5"
        class="speed-slider"
      />
      <span>{{ speed }}x</span>
    </div>
    
    <div class="progress-bar">
      <div 
        class="progress-fill" 
        :style="{ width: `${(currentStep / (steps.length - 1)) * 100}%` }"
      ></div>
    </div>
    
    <!-- 图片查看器 -->
    <ImageViewer 
      :src="viewerImageSrc" 
      :alt="viewerImageAlt" 
      :show="showImageViewer" 
      :showPlayControl="true"
      :isPlaying="isPlaying"
      @toggle-play="togglePlay"
      @close="closeImageViewer" 
    />
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import ImageViewer from './ImageViewer.vue'

const props = defineProps({
  steps: {
    type: Array,
    required: true
  },
  title: {
    type: String,
    default: '算法演示'
  }
})

const emit = defineEmits(['step-change'])

const currentStep = ref(0)
const isPlaying = ref(false)
const speed = ref(1)
let playInterval = null

function startInterval() {
  if (playInterval) return
  playInterval = setInterval(() => {
    nextStep()
    if (!isPlaying.value) {
      clearInterval(playInterval)
      playInterval = null
    }
  }, 1000 / speed.value)
}

function stopInterval() {
  if (playInterval) {
    clearInterval(playInterval)
    playInterval = null
  }
}

// 图片查看器状态（支持放大后继续播放，实时跟随当前帧）
const showImageViewer = ref(false)
const viewerImageSrc = ref('')
const viewerImageAlt = ref('')
const viewerLiveFollow = ref(true)

watch(currentStep, (newStep) => {
  emit('step-change', newStep, props.steps[newStep])
  // 放大状态下保持实时刷新
  if (showImageViewer.value && viewerLiveFollow.value) {
    const step = props.steps[newStep]
    if (step?.visualization) {
      viewerImageSrc.value = 'data:image/png;base64,' + step.visualization
      viewerImageAlt.value = step.description || '算法步骤可视化'
    }
  }
})

watch(() => props.steps, () => {
  currentStep.value = 0
  isPlaying.value = false
  stopInterval()
  // 步骤切换时，如果处于放大 & 跟随，则立即刷新首帧
  if (showImageViewer.value && viewerLiveFollow.value && props.steps?.[0]?.visualization) {
    viewerImageSrc.value = 'data:image/png;base64,' + props.steps[0].visualization
    viewerImageAlt.value = props.steps[0].description || '算法步骤可视化'
  }
})

function goToStart() {
  currentStep.value = 0
}

function goToEnd() {
  currentStep.value = props.steps.length - 1
}

function previousStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function nextStep() {
  if (currentStep.value < props.steps.length - 1) {
    currentStep.value++
  } else {
    // 到达末尾，停止播放
    isPlaying.value = false
    if (playInterval) {
      clearInterval(playInterval)
      playInterval = null
    }
  }
}

function togglePlay() {
  isPlaying.value = !isPlaying.value
  
  if (isPlaying.value) {
    // 如果已经在最后一步，从头开始
    if (currentStep.value === props.steps.length - 1) {
      currentStep.value = 0
    }
    
    startInterval()
  } else {
    stopInterval()
  }
}

// 当速度改变时，重新启动定时器
watch(speed, () => {
  if (isPlaying.value) {
    stopInterval()
    startInterval()
  }
})

function handleImageClick() {
  const step = props.steps[currentStep.value]
  if (step?.visualization) {
    viewerImageSrc.value = 'data:image/png;base64,' + step.visualization
    viewerImageAlt.value = step.description || '算法步骤可视化'
    viewerLiveFollow.value = true
    showImageViewer.value = true
    // 放大后保持播放：若当前在播放，则确保定时器存在
    if (isPlaying.value) {
      startInterval()
    }
  }
}

function closeImageViewer() {
  showImageViewer.value = false
}

onUnmounted(() => {
  stopInterval()
})
</script>

<style scoped>
.animation-player {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e5e7eb;
}

.player-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.1rem;
  font-weight: 600;
}

.step-counter {
  font-size: 0.9rem;
  color: #6b7280;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  background: #f3f4f6;
  border-radius: 12px;
}

.step-description {
  padding: 1rem;
  background: #f0f9ff;
  border-left: 4px solid #667eea;
  border-radius: 6px;
  color: #1e40af;
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
  min-height: 3rem;
  display: flex;
  align-items: center;
}

.step-visualization {
  margin-bottom: 1.5rem;
  background: #fafbfc;
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

.step-visualization .viz-image {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.step-visualization .viz-image.clickable {
  cursor: zoom-in;
}

.step-visualization .viz-image.clickable:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.controls {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.control-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  background: #f3f4f6;
  color: #374151;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 90px;
}

.control-btn:hover:not(:disabled) {
  background: #e5e7eb;
  transform: translateY(-1px);
}

.control-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.control-btn.play-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  min-width: 110px;
}

.control-btn.play-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.speed-control {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
}

.speed-control label {
  font-size: 0.9rem;
  color: #4b5563;
  font-weight: 600;
}

.speed-slider {
  width: 150px;
  height: 6px;
  border-radius: 3px;
  background: #e5e7eb;
  outline: none;
  -webkit-appearance: none;
}

.speed-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #667eea;
  cursor: pointer;
}

.speed-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #667eea;
  cursor: pointer;
  border: none;
}

.speed-control span {
  font-size: 0.9rem;
  color: #374151;
  font-weight: 600;
  min-width: 40px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .controls {
    gap: 0.3rem;
  }
  
  .control-btn {
    padding: 0.4rem 0.6rem;
    font-size: 0.8rem;
    min-width: 70px;
  }
  
  .control-btn.play-btn {
    min-width: 90px;
  }
}
</style>
