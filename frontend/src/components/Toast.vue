<template>
  <Transition name="toast">
    <div v-if="visible" :class="['toast', type]">
      <span class="toast-icon">{{ icon }}</span>
      <span class="toast-message">{{ message }}</span>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'

const props = defineProps({
  message: String,
  type: {
    type: String,
    default: 'info' // 'success', 'error', 'warning', 'info'
  },
  duration: {
    type: Number,
    default: 3000
  },
  show: Boolean
})

const emit = defineEmits(['close'])

const visible = ref(false)
let timer = null

const icons = {
  success: '✅',
  error: '❌',
  warning: '⚠️',
  info: 'ℹ️'
}

// 使用 computed 使图标响应式更新
const icon = computed(() => props.type in icons ? icons[props.type] : icons.info)

watch(() => props.show, (newVal) => {
  if (newVal) {
    visible.value = true
    
    // 清除之前的定时器
    if (timer) clearTimeout(timer)
    
    // 设置自动关闭
    timer = setTimeout(() => {
      visible.value = false
      setTimeout(() => {
        emit('close')
      }, 300) // 等待动画完成
    }, props.duration)
  } else {
    visible.value = false
  }
})

onMounted(() => {
  if (props.show) {
    visible.value = true
    timer = setTimeout(() => {
      visible.value = false
      setTimeout(() => {
        emit('close')
      }, 300)
    }, props.duration)
  }
})
</script>

<style scoped>
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  font-size: 0.95rem;
  font-weight: 500;
  z-index: 9999;
  min-width: 280px;
  max-width: 500px;
  backdrop-filter: blur(10px);
}

.toast-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.toast-message {
  flex: 1;
  line-height: 1.5;
}

/* 类型样式 */
.toast.success {
  background: linear-gradient(135deg, #d4f4dd 0%, #a8e6cf 100%);
  border-left: 4px solid #48bb78;
  color: #22543d;
}

.toast.error {
  background: linear-gradient(135deg, #fed7d7 0%, #fc8181 100%);
  border-left: 4px solid #f56565;
  color: #742a2a;
}

.toast.warning {
  background: linear-gradient(135deg, #fef5e7 0%, #fbd38d 100%);
  border-left: 4px solid #ed8936;
  color: #7c2d12;
}

.toast.info {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  border-left: 4px solid #4299e1;
  color: #2c5282;
}

/* 过渡动画 */
.toast-enter-active {
  animation: slideInRight 0.3s ease-out;
}

.toast-leave-active {
  animation: slideOutRight 0.3s ease-in;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOutRight {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}
</style>
