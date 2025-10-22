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
  // 健康检查
  healthCheck() {
    return request('/health')
  },

  // 最小生成树 - Kruskal
  mstKruskal(nodes, edges) {
    return request('/mst/kruskal', {
      method: 'POST',
      body: JSON.stringify({ nodes, edges }),
    })
  },

  // 最小生成树 - Prim
  mstPrim(nodes, edges, startNode) {
    return request('/mst/prim', {
      method: 'POST',
      body: JSON.stringify({ nodes, edges, start_node: startNode }),
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

  // AES 加密
  aesEncrypt(plaintext, key) {
    return request('/aes/encrypt', {
      method: 'POST',
      body: JSON.stringify({ plaintext, key }),
    })
  },

  // AES 解密
  aesDecrypt(encrypted, key) {
    return request('/aes/decrypt', {
      method: 'POST',
      body: JSON.stringify({ encrypted, key }),
    })
  },
}
