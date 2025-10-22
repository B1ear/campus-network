import math
import random
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import font_manager

def generate_random_planar_network(n=25, radius=0.4, cost_range=(10, 100), cap_range=(100, 1000), seed=None):
    if seed:
        random.seed(seed)

    # 生成随机几何图：节点坐标随机分布在单位正方形内
    G = nx.random_geometric_graph(n, radius)

    # 确保连通（若不连通则补全最短边）
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        for i in range(len(components) - 1):
            u = random.choice(list(components[i]))
            v = random.choice(list(components[i + 1]))
            G.add_edge(u, v)
        assert nx.is_connected(G)

    # 检查是否平面，若不平面则删边
    is_planar, _ = nx.check_planarity(G)
    while not is_planar:
        # 随机删除一条边直到平面
        edge = random.choice(list(G.edges()))
        G.remove_edge(*edge)
        is_planar, _ = nx.check_planarity(G)

    # 分配 cost / capacity
    for u, v in G.edges():
        G.edges[u, v]['cost'] = random.randint(*cost_range)
        G.edges[u, v]['capacity'] = random.randint(*cap_range)

    # 生成邻接表
    adjacency = {i: [] for i in range(n)}
    for u, v in G.edges():
        adjacency[u].append((v, G.edges[u, v]['cost'], G.edges[u, v]['capacity']))
        adjacency[v].append((u, G.edges[u, v]['cost'], G.edges[u, v]['capacity']))

    return G, nx.get_node_attributes(G, 'pos'), adjacency


def draw_campus_network(G, pos):
    """
    绘制校园网拓扑图
    节点为路由器，边标签显示 cost / capacity
    """
    try:
        zh_font = next(f for f in font_manager.fontManager.ttflist 
                    if "SimHei" in f.name or "Heiti" in f.name or "Source Han" in f.name)
        matplotlib.rcParams['font.sans-serif'] = [zh_font.name]
    except StopIteration:
        matplotlib.rcParams['font.sans-serif'] = ['Arial'] 
    matplotlib.rcParams['axes.unicode_minus'] = False 
    
    plt.figure(figsize=(12, 10))
    nx.draw(G, pos, with_labels=True, node_size=600, font_size=12)
    edge_labels = {(u, v): f"{G.edges[u, v]['cost']} / {G.edges[u, v]['capacity']}"
                   for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)
    plt.title("校园网路由设计图（边标签：cost / capacity）", fontsize=14)
    plt.axis("off")
    plt.show()


# 主程序部分
if __name__ == "__main__":
    n = 25  # 路由器数量（>=20）
    G, pos, adjacency = generate_planar_campus_network(n=n, seed=42)

    print("=== 校园网路由邻接表 ===")
    for i in range(0, n):  # 打印前10个节点的连接信息
        print(f"路由器 {i}: {adjacency[i]}")

    # 绘制网络图
    draw_campus_network(G, pos)