<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="isVisible" class="image-viewer-overlay" @click="close">
        <div class="viewer-container" @click.stop>
          <button class="close-btn" @click="close">✕</button>
          <img :src="imageSrc" :alt="imageAlt" class="viewer-image" />
          <div v-if="imageAlt" class="image-caption">{{ imageAlt }}</div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  src: String,
  alt: String,
  show: Boolean
})

const emit = defineEmits(['close'])

const isVisible = ref(false)
const imageSrc = ref('')
const imageAlt = ref('')

watch(() => props.show, (newVal) => {
  isVisible.value = newVal
  if (newVal) {
    imageSrc.value = props.src
    imageAlt.value = props.alt
    // 禁用背景滚动
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

// 在可见状态下，跟随外部 src/alt 实时更新，支持放大后继续播放时的帧刷新
watch(() => props.src, (val) => {
  if (isVisible.value && typeof val === 'string') {
    imageSrc.value = val
  }
})
watch(() => props.alt, (val) => {
  if (isVisible.value && typeof val === 'string') {
    imageAlt.value = val
  }
})

function close() {
  emit('close')
}

// 键盘ESC关闭
const handleKeyDown = (e) => {
  if (e.key === 'Escape' && isVisible.value) {
    close()
  }
}

// 监听键盘事件
if (typeof window !== 'undefined') {
  window.addEventListener('keydown', handleKeyDown)
}
</script>

<style scoped>
.image-viewer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(8px);
  cursor: zoom-out;
}

.viewer-container {
  position: relative;
  max-width: 95vw;
  max-height: 95vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: default;
}

.close-btn {
  position: absolute;
  top: -50px;
  right: 0;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.viewer-image {
  max-width: 100%;
  max-height: 85vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 10px 50px rgba(0, 0, 0, 0.5);
  animation: zoomIn 0.3s ease-out;
}

.image-caption {
  margin-top: 1rem;
  color: white;
  font-size: 1rem;
  text-align: center;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  backdrop-filter: blur(10px);
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes zoomIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .close-btn {
    top: 10px;
    right: 10px;
    width: 36px;
    height: 36px;
    font-size: 1.2rem;
  }
  
  .viewer-image {
    max-height: 80vh;
  }
}
</style>
