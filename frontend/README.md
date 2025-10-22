# Campus Network Frontend

校园网络算法可视化平台前端

## 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Vite** - 下一代前端构建工具
- **原生SVG** - 图形可视化

## 功能特性

### 1. 最小生成树 (MST)
- ✅ Kruskal 算法
- ✅ Prim 算法
- ✅ 可视化图形展示
- ✅ 实时计算结果

### 2. 最大流 (Max Flow)
- ✅ Edmonds-Karp 算法
- ✅ Dinic 算法
- ✅ 流量分配可视化
- ✅ 性能对比

### 3. AES加密
- ✅ AES-128 加密
- ✅ AES-128 解密
- ✅ Base64 编码
- ✅ 一键复制功能

## 安装依赖

```bash
npm install
```

## 开发模式

```bash
npm run dev
```

访问 `http://localhost:3000`

## 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录

## 预览生产版本

```bash
npm run preview
```

## 项目结构

```
frontend/
├── index.html              # HTML入口
├── package.json            # 依赖配置
├── vite.config.js          # Vite配置
└── src/
    ├── main.js             # 应用入口
    ├── App.vue             # 根组件
    ├── style.css           # 全局样式
    ├── api/
    │   └── backend.js      # 后端API封装
    └── components/
        ├── MSTPanel.vue        # 最小生成树面板
        ├── MaxFlowPanel.vue    # 最大流面板
        ├── AESPanel.vue        # AES加密面板
        └── NetworkGraph.vue    # 图形可视化组件
```

## 使用说明

1. **启动后端服务**
   ```bash
   cd ../backend
   python app.py
   ```

2. **启动前端服务**
   ```bash
   npm run dev
   ```

3. **访问应用**
   - 打开浏览器访问 `http://localhost:3000`
   - 选择相应的功能标签页
   - 输入数据或加载示例
   - 点击计算按钮查看结果

## 注意事项

- 确保后端服务已启动（默认端口5000）
- 浏览器需要支持ES6+和SVG
- 建议使用Chrome、Firefox或Edge浏览器
