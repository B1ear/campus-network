# 新功能说明

## 🎉 网络配置与拓扑可视化功能

### 功能亮点

✅ **可配置网络参数**
- 节点数量（路由器数量）：2-100
- 连接半径：0.1-1.0
- 造价范围：自定义最小-最大值
- 吞吐量/容量范围：自定义最小-最大值
- 随机种子：可重现的网络生成

✅ **自动拓扑可视化**
- 自动生成网络拓扑图
- 节点和边的清晰标注
- 边标签显示：造价 / 容量
- 高分辨率 PNG 图片

✅ **默认配置支持**
- 开箱即用的默认参数
- 一键加载默认配置
- 适合快速开始使用

✅ **算法集成**
- 无缝集成到 MST 算法
- 无缝集成到最大流算法
- 一键加载配置的网络
- 自动格式转换

### 文件结构

```
backend/
├── config/
│   ├── __init__.py              # 配置模块初始化
│   └── network_config.py        # 网络配置类和默认配置
├── algorithms/
│   └── generate_graph.py        # 网络生成和可视化（已更新）
└── app.py                       # Flask 应用（已添加 API 端点）

frontend/
├── src/
│   ├── components/
│   │   ├── NetworkConfigPanel.vue    # 网络配置组件（新增）
│   │   ├── MSTPanel.vue              # MST 面板（已更新）
│   │   └── MaxFlowPanel.vue          # 最大流面板（已更新）
│   ├── api/
│   │   └── backend.js                # API 接口（已添加方法）
│   └── App.vue                       # 主应用（已集成网络配置）
```

### API 端点

#### 1. 获取默认配置
```http
GET /api/network/config/default
```

#### 2. 生成网络
```http
POST /api/network/generate
Content-Type: application/json

{
  "num_nodes": 25,
  "radius": 0.4,
  "cost_range": [10, 100],
  "capacity_range": [100, 1000],
  "seed": 42
}
```

### 使用方式

#### 前端使用

1. **网络配置标签页**
   - 调整网络参数
   - 生成网络拓扑
   - 查看拓扑图和统计信息
   - 应用到算法

2. **算法标签页**
   - 点击"加载配置网络"按钮
   - 自动填充网络数据
   - 运行算法计算

#### 后端使用

```python
from config.network_config import NetworkConfig, DEFAULT_CONFIG
from algorithms.generate_graph import generate_random_planar_network, draw_campus_network

# 使用默认配置
config = NetworkConfig.default()

# 自定义配置
config = NetworkConfig(
    num_nodes=30,
    radius=0.5,
    cost_range=[5, 50],
    capacity_range=[50, 500],
    seed=789
)

# 生成网络
G, pos, adjacency = generate_random_planar_network(
    n=config.num_nodes,
    radius=config.radius,
    cost_range=tuple(config.cost_range),
    cap_range=tuple(config.capacity_range),
    seed=config.seed
)

# 生成拓扑图（base64 编码）
topology_image = draw_campus_network(G, pos, return_base64=True)

# 或保存到文件
draw_campus_network(G, pos, save_path='topology.png')
```

### 技术实现

#### 后端技术栈
- **Flask**: Web 框架
- **NetworkX**: 图生成和处理
- **Matplotlib**: 图形可视化
- **NumPy**: 数值计算

#### 前端技术栈
- **Vue 3**: 响应式 UI 框架
- **Composition API**: 组件逻辑
- **localStorage**: 本地数据持久化

#### 核心算法
- 随机几何图生成
- 连通性检查和修复
- 平面性验证
- 自动布局算法

### 数据流

```
用户输入配置
    ↓
前端验证
    ↓
发送到后端 API
    ↓
NetworkConfig 验证
    ↓
生成随机几何图
    ↓
确保连通性
    ↓
确保平面性
    ↓
分配边属性
    ↓
生成拓扑图
    ↓
返回数据 + 图片
    ↓
前端展示
    ↓
保存到 localStorage
    ↓
其他算法页面使用
```

### 配置参数说明

| 参数 | 类型 | 范围 | 默认值 | 说明 |
|------|------|------|--------|------|
| num_nodes | int | 2-100 | 25 | 网络节点（路由器）数量 |
| radius | float | 0.1-1.0 | 0.4 | 连接半径，决定连接密度 |
| cost_range | [int, int] | [min, max] | [10, 100] | 边的造价范围 |
| capacity_range | [int, int] | [min, max] | [100, 1000] | 边的容量范围 |
| seed | int | 任意 | 42 | 随机种子，相同种子生成相同网络 |

### 优势特性

1. **灵活性**: 完全可配置的网络参数
2. **可视化**: 直观的图形展示
3. **可重现性**: 通过种子值确保可重现
4. **集成性**: 与现有算法无缝集成
5. **易用性**: 默认配置开箱即用
6. **实用性**: 适合教学、研究、测试

### 应用场景

- 📚 **教学演示**: 展示不同网络规模下的算法表现
- 🔬 **算法研究**: 测试算法在各种网络拓扑下的性能
- 🎯 **性能测试**: 对比不同网络配置的计算效率
- 🏫 **校园规划**: 模拟真实校园网络布局

### 后续扩展

可能的扩展方向：
- [ ] 支持导入/导出网络配置
- [ ] 支持多种网络生成算法
- [ ] 添加网络分析指标
- [ ] 支持动态修改网络
- [ ] 添加网络对比功能

---

**版本**: 1.0.0  
**更新日期**: 2025-10-22  
**状态**: ✅ 已完成并测试
