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
    <div style="margin-top: 2rem; padding: 1rem; background: #f0f4ff; border-radius: 8px; border: 2px dashed #667eea;">
      <h3 style="color: #667eea; margin-top: 0;">ℹ️ 说明</h3>
      <ul style="margin: 0; padding-left: 1.5rem; color: #555;">
        <li>使用自实现的 AES-128 加密算法</li>
        <li>密钥会自动调整为16字节</li>
        <li>解密时必须使用相同的密钥</li>
        <li>密文以十六进制字符串格式输出</li>
      </ul>
      <button @click="loadExample" style="background: #ff9800; margin-top: 1rem;">💡 加载示例</button>
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
.panel { padding: 1rem; } .layout { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem; }
.section { display: flex; flex-direction: column; gap: 0.75rem; padding: 1rem; background: #f9f9f9; border-radius: 8px; }
h2 { color: #667eea; margin: 0 0 1rem; } h3 { color: #333; border-bottom: 2px solid #667eea; padding-bottom: 0.5rem; margin: 0; }
label { font-weight: 600; color: #555; font-size: 0.9rem; }
input, textarea { padding: 0.6rem; border: 2px solid #ddd; border-radius: 6px; font-size: 1rem; font-family: inherit; }
input:focus, textarea:focus { outline: none; border-color: #667eea; }
button { padding: 0.75rem; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; background: #667eea; color: white; font-size: 1rem; }
button:hover:not(:disabled) { opacity: 0.9; } button:disabled { opacity: 0.6; cursor: not-allowed; }
@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
</style>
