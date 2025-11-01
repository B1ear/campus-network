const API_BASE_URL = 'http://localhost:5000/api'

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  }

  try {
    const response = await fetch(url, config)
    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.error || 'Request failed')
    }
    return data
  } catch (error) {
    console.error('API Error:', error)
    throw error
  }
}

export const api = {
  // 最小生成树 - 比较两种算法
  mstCompare(nodes, edges) {
    return request('/mst/compare', {
      method: 'POST',
      body: JSON.stringify({ nodes, edges }),
    })
  },

  // 最大流 - Edmonds-Karp
  maxflowEdmondsKarp(nodes, edges, source, sink) {
    return request('/maxflow/edmonds-karp', {
      method: 'POST',
      body: JSON.stringify({ nodes, edges, source, sink }),
    })
  },

  // 最大流 - Dinic
  maxflowDinic(nodes, edges, source, sink) {
    return request('/maxflow/dinic', {
      method: 'POST',
      body: JSON.stringify({ nodes, edges, source, sink }),
    })
  },

  // AES 加密/解密
  aesEncrypt(plaintext, key) {
    return request('/aes/encrypt', {
      method: 'POST',
      body: JSON.stringify({ plaintext, key }),
    })
  },
  aesDecrypt(encrypted, key) {
    return request('/aes/decrypt', {
      method: 'POST',
      body: JSON.stringify({ encrypted, key }),
    })
  },

  // 网络配置与生成
  getDefaultNetworkConfig() {
    return request('/network/config/default')
  },
  generateNetwork(config = {}) {
    return request('/network/generate', {
      method: 'POST',
      body: JSON.stringify(config),
    })
  },

  // 原始图预览（不包含算法结果）
  previewGraph(nodes, edges, labelMode = 'auto') {
    return request('/graph/preview', {
      method: 'POST',
      body: JSON.stringify({ nodes, edges, label_mode: labelMode }),
    })
  },

  // 交互式仿真 - 计算路径与分配
  calculateTrafficPaths(nodes, edges, source, target, totalFlow, strategy = 'balanced', numPaths = 3) {
    return request('/traffic/calculate-paths', {
      method: 'POST',
      body: JSON.stringify({
        nodes,
        edges,
        source,
        target,
        total_flow: totalFlow,
        strategy,
        num_paths: numPaths,
      }),
    })
  },
}
