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

  // 最小生成树 - 比较两种算法
  mstCompare(nodes, edges) {
    return request('/mst/compare', {
      method: 'POST',
      body: JSON.stringify({ nodes, edges }),
    })
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

  // 获取默认网络配置
  getDefaultNetworkConfig() {
    return request('/network/config/default')
  },

  // 生成网络拓扑
  generateNetwork(config = {}) {
    return request('/network/generate', {
      method: 'POST',
      body: JSON.stringify(config),
    })
  },

  // 预览原始图（不包含算法结果）
  previewGraph(nodes, edges, labelMode = 'auto') {
    return request('/graph/preview', {
      method: 'POST',
      body: JSON.stringify({ nodes, edges, label_mode: labelMode }),
    })
  },

  // 鲁棒性分析
  analyzeRobustness(nodes, edges) {
    return request('/robustness/analyze', {
      method: 'POST',
      body: JSON.stringify({ nodes, edges }),
    })
  },

  // 模拟边移除
  simulateEdgeRemoval(nodes, edges, edgeFrom, edgeTo) {
    return request('/robustness/simulate-edge-removal', {
      method: 'POST',
      body: JSON.stringify({ nodes, edges, edge_from: edgeFrom, edge_to: edgeTo }),
    })
  },

  // 模拟节点移除
  simulateNodeRemoval(nodes, edges, nodeId) {
    return request('/robustness/simulate-node-removal', {
      method: 'POST',
      body: JSON.stringify({ nodes, edges, node_id: nodeId }),
    })
  },

  // 获取冗余路径
  getRedundantPaths(nodes, edges, source, target) {
    return request('/robustness/redundant-paths', {
      method: 'POST',
      body: JSON.stringify({ nodes, edges, source, target }),
    })
  },

  // 模拟流量负载均衡
  simulateLoadBalancing(nodes, edges, source, target, totalFlow, enableLoadBalancing, enableCongestionAvoidance, numPaths) {
    return request('/traffic/simulate-load-balancing', {
      method: 'POST',
      body: JSON.stringify({
        nodes,
        edges,
        source,
        target,
        total_flow: totalFlow,
        enable_load_balancing: enableLoadBalancing,
        enable_congestion_avoidance: enableCongestionAvoidance,
        num_paths: numPaths,
      }),
    })
  },

  // 计算路径和流量分配（用于交互式仿真）
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

// 导出单独的函数（保持向后兼容）
export const analyzeRobustness = api.analyzeRobustness
export const simulateTrafficLoadBalancing = api.simulateLoadBalancing
export const calculateMaxFlowAPI = api.maxflowDinic
