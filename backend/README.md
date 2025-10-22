# Campus Network Backend

基于Flask的校园网络算法后端API

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

## API文档

### 健康检查
```
GET /api/health
```

### 最小生成树 - Kruskal算法
```
POST /api/mst/kruskal
Content-Type: application/json

{
  "nodes": [0, 1, 2, 3],
  "edges": [
    {"from": 0, "to": 1, "weight": 10},
    {"from": 1, "to": 2, "weight": 15},
    {"from": 2, "to": 3, "weight": 4},
    {"from": 0, "to": 3, "weight": 5}
  ]
}
```

响应:
```json
{
  "algorithm": "Kruskal",
  "mst_edges": [...],
  "total_weight": 19,
  "plot_url": "/api/plots/kruskal_mst.png"
}
```

### 最小生成树 - Prim算法
```
POST /api/mst/prim
Content-Type: application/json

{
  "nodes": [0, 1, 2, 3],
  "edges": [
    {"from": 0, "to": 1, "weight": 10},
    {"from": 1, "to": 2, "weight": 15},
    {"from": 2, "to": 3, "weight": 4},
    {"from": 0, "to": 3, "weight": 5}
  ],
  "start_node": 0
}
```

### 最大流 - Edmonds-Karp算法
```
POST /api/maxflow/edmonds-karp
Content-Type: application/json

{
  "nodes": [0, 1, 2, 3],
  "edges": [
    {"from": 0, "to": 1, "capacity": 16},
    {"from": 0, "to": 2, "capacity": 13},
    {"from": 1, "to": 3, "capacity": 12},
    {"from": 2, "to": 3, "capacity": 14}
  ],
  "source": 0,
  "sink": 3
}
```

响应:
```json
{
  "algorithm": "Edmonds-Karp",
  "max_flow": 23,
  "flow_edges": [...],
  "source": 0,
  "sink": 3
}
```

### 最大流 - Dinic算法
```
POST /api/maxflow/dinic
```
格式同 Edmonds-Karp

### AES加密
```
POST /api/aes/encrypt
Content-Type: application/json

{
  "plaintext": "Hello World",
  "key": "my_secret_key"
}
```

响应:
```json
{
  "plaintext": "Hello World",
  "encrypted": "base64_encrypted_string",
  "key_length": 13
}
```

### AES解密
```
POST /api/aes/decrypt
Content-Type: application/json

{
  "encrypted": "base64_encrypted_string",
  "key": "my_secret_key"
}
```

响应:
```json
{
  "encrypted": "base64_encrypted_string",
  "decrypted": "Hello World"
}
```

### 获取生成的图像
```
GET /api/plots/<filename>
```

## 项目结构

```
backend/
├── app.py                  # Flask应用主入口
├── requirements.txt        # Python依赖
├── algorithms/
│   ├── mst.py             # 最小生成树算法
│   ├── maxflow.py         # 最大流算法
│   ├── aes_encrypt.py     # AES加密
│   └── utils.py           # 工具函数
└── static/plots/          # 生成的图像文件
```
