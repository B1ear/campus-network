# -*- coding: utf-8 -*-
"""
题目七：校园网路由设计（最小造价网络）
实现算法：Prim、Kruskal
此模块提供对前端或主程序可调用的接口 run_mst_comparison()
"""

import re
import time
import networkx as nx
import matplotlib.pyplot as plt


# =========================================================
# 1. 解析输入字符串，生成边表
# =========================================================
def parse_input(data_str):
    """
    输入格式示例：(1,2,6)(1,4,12)(1,3,8)
    输出：[(1,2,6), (1,4,12), (1,3,8)]
    """
    edges = re.findall(r"\((\d+),(\d+),(\d+)\)", data_str)
    edges = [(int(u), int(v), int(w)) for u, v, w in edges]
    return edges


# =========================================================
# 2. Prim 算法
# =========================================================
def prim_mst(n, edges):
    """
    Prim算法实现，支持0索引节点
    
    Args:
        n: 节点数量（从0到n-1或从1到n）
        edges: 边列表 [(u, v, weight), ...]
    
    Returns:
        (mst_edges, total_cost)
    """
    if not edges:
        return [], 0
    
    # 自动检测节点的最小值（判断是0索引还是1索引）
    all_nodes = set()
    for u, v, w in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    
    min_node = min(all_nodes)
    max_node = max(all_nodes)
    node_count = max_node - min_node + 1
    
    # 构建邻接表
    adj = {i: [] for i in range(min_node, max_node + 1)}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    
    # Prim算法
    selected = {i: False for i in range(min_node, max_node + 1)}
    start_node = min_node  # 从最小的节点开始
    selected[start_node] = True
    mst_edges = []
    total_cost = 0
    
    for _ in range(node_count - 1):
        min_w = float("inf")
        a = b = -1
        
        for u in range(min_node, max_node + 1):
            if selected[u]:
                for v, w in adj[u]:
                    if not selected[v] and w < min_w:
                        min_w = w
                        a, b = u, v
        
        if a != -1:
            selected[b] = True
            mst_edges.append((a, b, min_w))
            total_cost += min_w
    
    return mst_edges, total_cost


# =========================================================
# 3. Kruskal 算法
# =========================================================
def kruskal_mst(n, edges):
    parent = [i for i in range(n + 1)]

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        root_x, root_y = find(x), find(y)
        if root_x != root_y:
            parent[root_y] = root_x
            return True
        return False

    mst_edges = []
    total_cost = 0
    edges = sorted(edges, key=lambda x: x[2])  # 按造价排序

    for u, v, w in edges:
        if union(u, v):
            mst_edges.append((u, v, w))
            total_cost += w
        if len(mst_edges) == n - 1:
            break
    return mst_edges, total_cost


# =========================================================
# 4. 绘制拓扑图
# =========================================================
def draw_network(n, edges, mst_edges, title):
    G = nx.Graph()
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    pos = nx.spring_layout(G, seed=42)  # 自然布局
    edge_labels = {(u, v): f"{w}" for u, v, w in edges}

    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=600, font_size=12)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    nx.draw_networkx_edges(G, pos, edgelist=mst_edges, width=2.5, edge_color='r')
    plt.title(title + "（红色为最小造价连接）", fontsize=14)
    plt.axis("off")
    plt.show()


# =========================================================
# 5. 算法性能对比封装函数
# =========================================================
def compare_mst_algorithms(n, edges, repeats=30):
    """
    对 Prim 与 Kruskal 两种最小生成树算法进行运行时间测量与结果对比。
    返回字典：{ 'prim': (tree, cost, avg_time), 'kruskal': (tree, cost, avg_time) }
    """
    # 测量 Prim（多次取平均）
    t0 = time.perf_counter()
    for _ in range(repeats):
        prim_tree, prim_cost = prim_mst(n, edges)
    t1 = time.perf_counter()
    prim_time = (t1 - t0) / repeats

    # 测量 Kruskal（多次取平均）
    t0 = time.perf_counter()
    for _ in range(repeats):
        kruskal_tree, kruskal_cost = kruskal_mst(n, edges)
    t1 = time.perf_counter()
    kruskal_time = (t1 - t0) / repeats

    return {
        'prim': (prim_tree, prim_cost, prim_time),
        'kruskal': (kruskal_tree, kruskal_cost, kruskal_time)
    }


# =========================================================
# 6. 前端/主程序统一调用接口
# =========================================================
def run_mst_comparison(edge_string, repeats=30, draw=False):
    """
    封装主流程：解析输入、运行两种算法、可选绘图。
    参数:
        edge_string: "(1,2,6)(1,4,12)..."
        repeats: 重复次数，用于平均时间
        draw: 是否绘制结果图
    返回:
        结果字典，包括两种算法的边、总代价与平均时间
    """
    edges = parse_input(edge_string)
    n = max(max(u, v) for u, v, _ in edges)
    results = compare_mst_algorithms(n, edges, repeats=repeats)

    if draw:
        prim_tree = results['prim'][0]
        kruskal_tree = results['kruskal'][0]
        draw_network(n, edges, prim_tree, "校园网最小造价拓扑图（Prim算法）")
        draw_network(n, edges, kruskal_tree, "校园网最小造价拓扑图（Kruskal算法）")

    return results
