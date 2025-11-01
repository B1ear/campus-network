# Campus Network Frontend

校园网络算法可视化平台前端

## 技术栈
- Vue 3 + Vite
- 原生 SVG 可视化

## 功能特性（与后端对齐）
- 最小生成树（Kruskal/Prim 对比与可视化）
- 最大流（Edmonds-Karp / Dinic，可视化）
- AES-128 加解密（hex 格式）
- 网络配置与拓扑生成（默认配置 + 随机生成）
- 原始图预览
- 路径与流量分配（交互仿真：single/balanced、k 条路径）

## 安装与启动
```bash
npm install
npm run dev
```
访问：`http://localhost:3000`

后端需先启动：
```bash
cd ../backend
python app.py
```

## 前端调用的后端 API
见 `src/api/backend.js`，主要封装：
- `mstCompare(nodes, edges)` → POST /api/mst/compare
- `maxflowEdmondsKarp(nodes, edges, source, sink)` → POST /api/maxflow/edmonds-karp
- `maxflowDinic(nodes, edges, source, sink)` → POST /api/maxflow/dinic
- `aesEncrypt(plaintext, key)` / `aesDecrypt(encryptedHex, key)`
- `getDefaultNetworkConfig()` / `generateNetwork(config)`
- `previewGraph(nodes, edges, labelMode)`
- `calculateTrafficPaths(nodes, edges, source, target, totalFlow, strategy, numPaths)`

## 项目结构
```
frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.js
    ├── App.vue
    ├── api/
    │   └── backend.js
    └── components/
        ├── AESPanel.vue
        ├── AnimationPlayer.vue
        ├── EdgeEditor.vue
        ├── ImageViewer.vue
        ├── InteractiveTrafficPanel.vue
        ├── MSTPanel.vue
        ├── MaxFlowPanel.vue
        ├── NetworkConfigPanel.vue
        └── Toast.vue
```

## 使用说明
1. 启动后端与前端
2. 在“网络配置”生成或加载拓扑
3. 使用“MST/最大流/交互式流量”等面板进行实验与可视化

## 注意事项
- AES 接口采用 hex 编码；前端解密需传入 hex 字符串
- 交互仿真仅使用 `/api/traffic/calculate-paths`（不含完整负载均衡模拟）
