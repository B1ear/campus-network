import math
import random
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import font_manager
import io
import base64

def generate_random_planar_network(n=25, cost_range=(10, 100), cap_range=(100, 1000), seed=None):
    """
    生成随机连通平面图网络
    
    Args:
        n: 节点数量
        cost_range: 造价范围 (min, max)
        cap_range: 容量范围 (min, max)
        seed: 随机种子
    
    Returns:
        G: NetworkX图对象
        pos: 节点位置字典
        adjacency: 邻接表
    """
    if seed is not None:
        random.seed(seed)

    # 方法：生成随机树作为基础（保证连通），然后添加额外的边
    G = nx.Graph()
    G.add_nodes_from(range(n))
    
    # 使用随机生成树算法（保证连通）
    # 首先创建一个随机生成树
    nodes = list(range(n))
    random.shuffle(nodes)
    
    # 从第一个节点开始构建树
    tree_nodes = [nodes[0]]
    remaining_nodes = nodes[1:]
    
    while remaining_nodes:
        # 随机选择一个已在树中的节点
        u = random.choice(tree_nodes)
        # 随机选择一个不在树中的节点
        v = remaining_nodes.pop(0)
        # 添加边
        G.add_edge(u, v)
        tree_nodes.append(v)
    
    # 添加额外的边以增加连接性（但保持平面性）
    # 随机添加 n//3 到 n//2 条边
    extra_edges = random.randint(n // 3, n // 2)
    attempts = 0
    max_attempts = n * n
    
    while extra_edges > 0 and attempts < max_attempts:
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        
        if u != v and not G.has_edge(u, v):
            # 尝试添加边
            G.add_edge(u, v)
            # 检查是否仍然是平面图
            is_planar, _ = nx.check_planarity(G)
            if is_planar:
                extra_edges -= 1
            else:
                # 如果不是平面图，移除这条边
                G.remove_edge(u, v)
        
        attempts += 1
    
    # 验证图是连通的
    assert nx.is_connected(G), "生成的图不连通"
    
    # 生成节点位置（使用平面图布局）
    try:
        # 使用 planar_layout 获得平面布局
        pos = nx.planar_layout(G)
    except:
        # 如果失败，使用 spring_layout
        pos = nx.spring_layout(G, seed=seed, k=2, iterations=50)
    
    # 分配 cost / capacity
    for u, v in G.edges():
        G.edges[u, v]['cost'] = random.randint(*cost_range)
        G.edges[u, v]['capacity'] = random.randint(*cap_range)
    
    # 为每个节点设置位置属性
    for node, (x, y) in pos.items():
        G.nodes[node]['pos'] = (x, y)

    # 生成邻接表
    adjacency = {i: [] for i in range(n)}
    for u, v in G.edges():
        adjacency[u].append((v, G.edges[u, v]['cost'], G.edges[u, v]['capacity']))
        adjacency[v].append((u, G.edges[u, v]['cost'], G.edges[u, v]['capacity']))

    return G, pos, adjacency


def draw_campus_network(G, pos, save_path=None, return_base64=False):
    """
    绘制校园网拓扑图
    节点为路由器，边标签显示 cost / capacity
    优化标签位置以减少遮挡
    
    Args:
        G: NetworkX图对象
        pos: 节点位置字典
        save_path: 保存路径（可选）
        return_base64: 是否返回base64编码的图像
    
    Returns:
        如果return_base64=True，返回base64编码的图像字符串
    """
    try:
        zh_font = next(f for f in font_manager.fontManager.ttflist 
                    if "SimHei" in f.name or "Heiti" in f.name or "Source Han" in f.name)
        matplotlib.rcParams['font.sans-serif'] = [zh_font.name]
    except StopIteration:
        matplotlib.rcParams['font.sans-serif'] = ['Arial'] 
    matplotlib.rcParams['axes.unicode_minus'] = False 
    
    # 创建更大的画布以减少遮挡
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # 绘制边（背景）
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', width=2, alpha=0.6)
    
    # 绘制节点
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color='lightblue', 
                          node_size=700, alpha=0.9, edgecolors='navy', linewidths=2)
    
    # 绘制节点标签（使用白色背景框减少遮挡）
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=11, font_weight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                    edgecolor='none', alpha=0.8))
    
    # 绘制边标签（优化位置和样式）
    edge_labels = {(u, v): f"{G.edges[u, v]['cost']}/{G.edges[u, v]['capacity']}"
                   for u, v in G.edges()}
    
    # 使用白色背景框和更小的字体
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax,
                                font_size=8, 
                                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                         edgecolor='lightgray', alpha=0.85),
                                rotate=False)
    
    plt.title("校园网路由设计图（边标签：造价/容量）", fontsize=16, pad=20)
    ax.axis('off')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=150, facecolor='white')
    
    if return_base64:
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150, facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        return image_base64
    
    plt.close()


# 主程序部分
if __name__ == "__main__":
    n = 25  # 路由器数量（>=20）
    G, pos, adjacency = generate_planar_campus_network(n=n, seed=42)

    print("=== 校园网路由邻接表 ===")
    for i in range(0, n):  # 打印前10个节点的连接信息
        print(f"路由器 {i}: {adjacency[i]}")

    # 绘制网络图
    draw_campus_network(G, pos)