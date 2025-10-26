<template>
  <div class="panel">
    <h2>🔐 AES-128 加密/解密</h2>
    <div class="layout">
      <div class="section">
        <h3>🔒 加密</h3>
        <label>明文:</label>
        <textarea v-model="plaintext" rows="5" placeholder="输入要加密的文本..."></textarea>
        <label>密钥:</label>
        <input v-model="encKey" placeholder="输入加密密钥" />
        <button @click="encrypt" :disabled="encLoading">{{ encLoading ? '加密中...' : '🔒 加密' }}</button>
        <div v-if="encError" style="padding: 1rem; background: #fee; border-radius: 6px; color: #c33;">{{ encError }}</div>
        <div v-if="encResult">
          <label>密文 (十六进制):</label>
          <textarea :value="encResult.encrypted" readonly rows="4" style="background: #f5f5f5; font-family: monospace;"></textarea>
          <button @click="copy(encResult.encrypted)" style="background: #4caf50;">📋 复制密文</button>
        </div>
      </div>
      <div class="section">
        <h3>🔓 解密</h3>
        <label>密文 (十六进制):</label>
        <textarea v-model="ciphertext" rows="5" placeholder="输入要解密的密文..."></textarea>
        <label>密钥:</label>
        <input v-model="decKey" placeholder="输入解密密钥" />
        <button @click="decrypt" :disabled="decLoading">{{ decLoading ? '解密中...' : '🔓 解密' }}</button>
        <button @click="useEnc" :disabled="!encResult" style="background: #eee; color: #666;">⬅️ 使用加密结果</button>
        <div v-if="decError" style="padding: 1rem; background: #fee; border-radius: 6px; color: #c33;">{{ decError }}</div>
        <div v-if="decResult">
          <label>明文:</label>
          <textarea :value="decResult.decrypted" readonly rows="4" style="background: #e8f5e9;"></textarea>
          <button @click="copy(decResult.decrypted)" style="background: #4caf50;">📋 复制明文</button>
        </div>
      </div>
    </div>
    <div style="padding: 1.5rem; background: white; border-radius: 12px; border: 2px solid #e0e7ff; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);">
      <h3 style="color: #667eea; margin-top: 0; font-size: 1.1rem; font-weight: 600;">ℹ️ 说明</h3>
      <ul style="margin: 0.5rem 0 0; padding-left: 1.5rem; color: #6b7280; line-height: 1.8;">
        <li>使用自实现的 AES-128 加密算法</li>
        <li>密钥会自动调整为16字节</li>
        <li>解密时必须使用相同的密钥</li>
        <li>密文以十六进制字符串格式输出</li>
      </ul>
      <button @click="loadExample" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); margin-top: 1rem;">💡 加载示例</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '../api/backend.js'
const plaintext = ref(''); const encKey = ref(''); const encLoading = ref(false); const encResult = ref(null); const encError = ref(null)
const ciphertext = ref(''); const decKey = ref(''); const decLoading = ref(false); const decResult = ref(null); const decError = ref(null)
async function encrypt() {
  encError.value = null; encResult.value = null; encLoading.value = true
  try {
    if (!plaintext.value || !encKey.value) throw new Error('请输入明文和密钥')
    encResult.value = await api.aesEncrypt(plaintext.value, encKey.value)
  } catch (err) { encError.value = err.message } finally { encLoading.value = false }
}
async function decrypt() {
  decError.value = null; decResult.value = null; decLoading.value = true
  try {
    if (!ciphertext.value || !decKey.value) throw new Error('请输入密文和密钥')
    decResult.value = await api.aesDecrypt(ciphertext.value, decKey.value)
  } catch (err) { decError.value = err.message } finally { decLoading.value = false }
}
function useEnc() { if (encResult.value) { ciphertext.value = encResult.value.encrypted; decKey.value = encKey.value } }
function copy(text) { navigator.clipboard.writeText(text).then(() => alert('已复制到剪贴板！')) }
function loadExample() { plaintext.value = 'Hello, Campus Network! 这是一个测试消息。'; encKey.value = 'my_secret_key123' }
</script>

<style scoped>
.panel { padding: 0; background: transparent; }
.layout { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }
.section { 
  display: flex; 
  flex-direction: column; 
  gap: 0.75rem; 
  padding: 1.5rem; 
  background: white; 
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}
h2 { color: #1f2937; margin: 0 0 1.5rem; font-size: 1.5rem; font-weight: 600; }
h3 { color: #1f2937; border-bottom: 2px solid #667eea; padding-bottom: 0.75rem; margin: 0 0 1rem; font-size: 1.15rem; font-weight: 600; }
label { font-weight: 600; color: #4b5563; font-size: 0.9rem; }
input, textarea { 
  padding: 0.75rem; 
  border: 1px solid #e5e7eb; 
  border-radius: 8px; 
  font-size: 0.95rem; 
  font-family: inherit;
  transition: all 0.2s;
}
input:focus, textarea:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
button { 
  padding: 0.75rem 1rem; 
  border: none; 
  border-radius: 8px; 
  font-weight: 600; 
  cursor: pointer; 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
  color: white; 
  font-size: 0.95rem;
  transition: all 0.3s;
}
button:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3); } 
button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
</style>
