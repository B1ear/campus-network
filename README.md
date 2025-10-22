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

- 🌐 **网络配置**: 可配置网络参数（节点数、连接半径、造价范围、吞吐量等）
- 🖼️ **拓扑可视化**: 自动生成并显示网络拓扑图
- 🌲 **最小生成树**: Kruskal & Prim算法
- 💧 **最大流**: Edmonds-Karp & Dinic算法  
- 🔐 **AES加密**: 自实现AES-128加密/解密

## 使用说明

1. **网络配置**: 先在“网络配置”标签页配置并生成网络拓扑
2. **应用网络**: 点击“应用到算法”按钮，将网络保存为默认配置
3. **运行算法**: 在其他标签页使用配置的网络运行算法

## 技术栈

**后端**: Flask 3.0 + 自实现算法  
**前端**: Vue 3 + Vite

详见各目录下的README文档。
