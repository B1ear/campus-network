# Campus Network Backend

基于 Flask 的校园网络算法后端 API

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
python app.py
```

默认地址：`http://localhost:5000`

## API 概览（已对齐前端实际使用）
- POST /api/network/generate — 生成随机校园网络拓扑
- GET  /api/network/config/default — 获取默认网络配置
- POST /api/graph/preview — 绘制原始图
- POST /api/mst/compare — 比较 Kruskal 与 Prim
- POST /api/maxflow/edmonds-karp — Edmonds-Karp 最大流
- POST /api/maxflow/dinic — Dinic 最大流
- POST /api/aes/encrypt — AES-128 加密（输出 hex）
- POST /api/aes/decrypt — AES-128 解密（输入 hex）
- POST /api/traffic/calculate-paths — 路径与流量分配（交互仿真）
- GET  /api/plots/<filename> — 获取生成图片（如需）

## 详细说明与示例

### 1) 生成网络拓扑
```
POST /api/network/generate
Content-Type: application/json

{
  "num_nodes": 12,
  "cost_range": [1, 20],
  "capacity_range": [50, 300],
  "seed": 42
}
```
响应包含：`config`、`nodes`、`edges`、`topology_image`(base64) 与统计信息。

### 2) 默认网络配置
```
GET /api/network/config/default
```

### 3) 原始图预览
```
POST /api/graph/preview
{
  "nodes": [{"id":0,"label":"0"}, ...],
  "edges": [{"from":0,"to":1,"weight":10,"capacity":100}, ...],
  "label_mode": "auto"  // 可选
}
```
返回 `visualization`(base64)。

### 4) 最小生成树对比
```
POST /api/mst/compare
{
  "nodes": [...],
  "edges": [{"from":0,"to":1,"weight":10}, ...]
}
```
返回 `kruskal` 与 `prim` 两套结果（含 steps 与 visualization）。

### 5) 最大流（Edmonds-Karp / Dinic）
```
POST /api/maxflow/edmonds-karp
POST /api/maxflow/dinic
{
  "nodes": [...],
  "edges": [{"from":0,"to":1,"capacity":16}, ...],
  "source": 0,
  "sink": 5
}
```
返回 `max_flow`、`flow_edges`、`steps` 与 `visualization`。

### 6) AES 加密/解密（十六进制）
```
POST /api/aes/encrypt
{
  "plaintext": "Hello World",
  "key": "my_secret_key"
}
```
响应：`encrypted` 为 hex 字符串；同时返回 `format: "hex"`。
```
POST /api/aes/decrypt
{
  "encrypted": "<hex_string>",
  "key": "my_secret_key"
}
```

### 7) 路径与流量分配（交互仿真）
```
POST /api/traffic/calculate-paths
{
  "nodes": [...],
  "edges": [...],
  "source": 0,
  "target": 5,
  "total_flow": 1000,
  "strategy": "balanced",   // "single" | "balanced"
  "num_paths": 3
}
```
返回：
- `paths`: 路径数组
- `path_allocations`: 每条路径的 {flow, capacity, utilization}
- `total_capacity`, `requested_flow`, `actual_flow`, `is_limited`, `num_paths`

## 项目结构
```
backend/
├── app.py                    # Flask 应用入口与路由
├── requirements.txt          # 依赖
├── algorithms/
│   ├── mst.py               # MST 算法
│   ├── maxflow.py           # 最大流算法
│   ├── aes_encrypt.py       # AES-128 实现
│   ├── traffic.py           # 路径与分配（calculate-paths）
│   ├── generate_graph.py    # 随机网络生成
│   └── utils.py             # 绘图与通用工具
├── config/
│   └── network_config.py    # 配置模型与默认配置
└── static/plots/            # 生成的图像文件
```

> 说明：鲁棒性与负载均衡模拟的历史接口已移除，后端与前端保持最小必要对齐。
