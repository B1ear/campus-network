# 校园网络算法可视化平台

完整的前后端分离项目，实现最小生成树、最大流和AES加密算法。

## 快速开始

### 1. 启动后端
```bash
cd backend
pip install -r requirements.txt
python app.py
```
后端: `http://localhost:5000`

### 2. 启动前端
```bash
cd frontend
npm install
npm run dev
```
前端: `http://localhost:3000`

## 功能特性

- 🌲 **最小生成树**: Kruskal & Prim算法
- 💧 **最大流**: Edmonds-Karp & Dinic算法  
- 🔐 **AES加密**: 自实现AES-128加密/解密

## 技术栈

**后端**: Flask 3.0 + 自实现算法  
**前端**: Vue 3 + Vite

详见各目录下的README文档。
