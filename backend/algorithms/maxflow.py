"""
比较 Edmonds-Karp 与 Dinic 的最大流实现，并绘制两种算法的流分布图
输入格式示例（有向）： "(1,2,5)(1,3,7)..."
默认 source = 1, sink = max node
"""

import re
from collections import deque, defaultdict
import time
import copy

import networkx as nx
import matplotlib.pyplot as plt

# ===========================
# 输入（可修改）
# ===========================
INPUT_DATA = "(1,2,5)(1,3,7)(1,4,4)(2,5,8)(3,7,4)(4,3,2)(4,5,5)(4,7,6)(5,6,12)(5,8,6)(6,8,7)(7,6,4)(7,8,5)"
SRC = 1
# 若未指定sink，将选取 edges 中最大的节点为 sink
# ===========================


# ---------------------------
# 解析输入
# ---------------------------
def parse_directed_input(s):
    edges = re.findall(r"\((\d+),(\d+),(\d+)\)", s)
    return [(int(u), int(v), int(w)) for u, v, w in edges]


# ---------------------------
# 通用构建函数（为算法准备）
# capacity: dict (u,v)->cap
# adj: adjacency list for residual traversal
# orig_caps: original capacities for reporting flows
# ---------------------------
def build_capacity_graph(edges):
    capacity = defaultdict(int)
    adj = defaultdict(list)
    orig_caps = defaultdict(int)
    nodes = set()
    for u, v, w in edges:
        nodes.add(u); nodes.add(v)
        capacity[(u, v)] += w
        orig_caps[(u, v)] += w
        # adjacency for residual graph: ensure both directions present as nodes may need back-edge
        if v not in adj[u]:
            adj[u].append(v)
        if u not in adj[v]:
            adj[v].append(u)
    return capacity, adj, orig_caps, nodes


# ============================
# Edmonds-Karp (BFS Ford-Fulkerson)
# ============================
def edmonds_karp(source, sink, capacity, adj):
    # capacity is a dict (u,v)->remaining cap, modifies in-place
    flow = 0
    while True:
        parent = {source: None}
        q = deque([source])
        bottleneck = {source: float('inf')}
        found = False
        while q and not found:
            u = q.popleft()
            for v in adj[u]:
                if v not in parent and capacity[(u, v)] > 0:
                    parent[v] = u
                    bottleneck[v] = min(bottleneck[u], capacity[(u, v)])
                    if v == sink:
                        found = True
                        break
                    q.append(v)
        if sink not in parent:
            break
        inc = bottleneck[sink]
        flow += inc
        v = sink
        while v != source:
            u = parent[v]
            capacity[(u, v)] -= inc
            capacity[(v, u)] += inc
            if u not in adj[v]:
                adj[v].append(u)
            v = u
    return flow


# ============================
# Dinic's Algorithm
# ============================
class Dinic:
    def __init__(self, n_nodes_estimate=0):
        # We'll keep adjacency list of edges (for fast iteration), and capacities in arrays
        self.adj = defaultdict(list)  # node -> list of edge indices
        self.edges = []  # list of (u, v, cap)
        # edges stored as: forward edge index i, backward edge index i^1
        # When we add edge, we append forward then backward; so idx and idx^1 are pair.

    def add_edge(self, u, v, cap):
        # forward edge
        self.edges.append([u, v, cap])
        self.adj[u].append(len(self.edges) - 1)
        # backward edge
        self.edges.append([v, u, 0])
        self.adj[v].append(len(self.edges) - 1)

    def bfs_level(self, s, t):
        level = {}
        q = deque([s])
        level[s] = 0
        while q:
            u = q.popleft()
            for ei in self.adj[u]:
                _, v, cap = self.edges[ei]
                if cap > 0 and v not in level:
                    level[v] = level[u] + 1
                    q.append(v)
        return level

    def dfs_flow(self, u, t, f, level, it):
        if u == t:
            return f
        for i in range(it[u], len(self.adj[u])):
            ei = self.adj[u][i]
            _, v, cap = self.edges[ei]
            if cap > 0 and level.get(v, -1) == level.get(u, -1) + 1:
                pushed = self.dfs_flow(v, t, min(f, cap), level, it)
                if pushed > 0:
                    # subtract forward cap, add backward cap
                    self.edges[ei][2] -= pushed
                    self.edges[ei ^ 1][2] += pushed
                    return pushed
            it[u] += 1
        return 0

    def max_flow(self, s, t):
        flow = 0
        while True:
            level = self.bfs_level(s, t)
            if t not in level:
                break
            it = defaultdict(int)
            while True:
                pushed = self.dfs_flow(s, t, float('inf'), level, it)
                if pushed == 0:
                    break
                flow += pushed
        return flow

    def flows_on_original_edges(self, orig_caps):
        """
        orig_caps: dict (u,v)->orig_cap
        return flows dict (u,v)->flow_sent_on_that_edge
        Note: edges were added via add_edge; forward edges are at even indices 0,2,4...
        The flow on a forward edge = original cap - remaining cap (edges[ei][2])
        However, if original edges were split / duplicated, we sum up accordingly.
        """
        sent = defaultdict(int)
        # iterate all forward edges (even indices)
        for ei in range(0, len(self.edges), 2):
            u, v, rem_cap = self.edges[ei]
            # original cap = rem_cap + flow_sent
            # but we don't store original cap here; so we derive from orig_caps if available
            orig = orig_caps.get((u, v), None)
            if orig is not None:
                sent[(u, v)] += orig - rem_cap
            else:
                # fallback: if orig unknown, we can use backward edge cap as flow sent
                sent[(u, v)] += self.edges[ei ^ 1][2]
        return sent


# ============================
# Helpers：将残量表示转换为原始边上的已发送流量（用于 Edmonds-Karp）
# ============================
def compute_sent_from_capacity(orig_caps, final_capacity):
    sent = {}
    for (u, v), orig in orig_caps.items():
        rem = final_capacity.get((u, v), 0)
        sent[(u, v)] = orig - rem
    return sent


# ============================
# 绘图函数（并排显示两张图：EK 与 Dinic）
# ============================
def plot_flows(edges, orig_caps, flows_ek, flows_dinic, title_ek="Edmonds-Karp", title_dinic="Dinic"):
    """
    edges: original edges list [(u,v,cap)...]
    orig_caps: dict (u,v)->cap
    flows_ek/dinic: dict (u,v)->flow
    """
    # Create a directed graph for layout (use undirected for layout stability)
    G = nx.DiGraph()
    for u, v, w in edges:
        G.add_edge(u, v, capacity=w)

    # Use a consistent layout for both plots
    pos = nx.spring_layout(G, seed=42)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    for ax, flows, title in zip(axes, [flows_ek, flows_dinic], [title_ek, title_dinic]):
        ax.set_title(f"{title} — 最大流可视化\n(标签: flow/capacity)", fontsize=14)
        # draw nodes
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=700)
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=10)
        # draw all edges faintly first
        nx.draw_networkx_edges(G, pos, ax=ax, connectionstyle='arc3, rad=0.05', alpha=0.3)
        # prepare labels and colored/thick edges for edges with flow > 0
        edge_labels = {}
        ek_edges_with_flow = []
        for u, v, w in edges:
            f = flows.get((u, v), 0)
            edge_labels[(u, v)] = f"{f}/{w}"
            if f > 0:
                ek_edges_with_flow.append((u, v))
        # draw labels
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, ax=ax)
        # highlight edges carrying positive flow
        if ek_edges_with_flow:
            nx.draw_networkx_edges(G, pos, edgelist=ek_edges_with_flow, ax=ax,
                                   width=3.0, edge_color='r', connectionstyle='arc3, rad=0.05')
        ax.axis('off')

    plt.tight_layout()
    plt.show()


# ============================
# 主流程：构造图、运行两种算法、计时、输出、绘图
# ============================
def main(input_data, source=SRC, sink=None, do_plot=True):
    edges = parse_directed_input(input_data)
    _, _, orig_caps, nodes = build_capacity_graph(edges)
    if sink is None:
        sink = max(nodes)
    # --- Edmonds-Karp ---
    cap_ek, adj_ek, orig_caps_ek, _ = build_capacity_graph(edges)
    # copy because algorithm modifies capacity in-place; make independent copy for Dinic
    cap_ek_copy = copy.deepcopy(cap_ek)
    adj_ek_copy = copy.deepcopy(adj_ek)

    t0 = time.perf_counter()
    maxflow_ek = edmonds_karp(source, sink, cap_ek_copy, adj_ek_copy)
    t1 = time.perf_counter()
    time_ek = t1 - t0
    flows_ek = compute_sent_from_capacity(orig_caps, cap_ek_copy)

    # --- Dinic ---
    # Build Dinic graph from original edges
    dinic = Dinic()
    # we must preserve original capacities for reporting
    for u, v, w in edges:
        dinic.add_edge(u, v, w)
    t0 = time.perf_counter()
    maxflow_dinic = dinic.max_flow(source, sink)
    t1 = time.perf_counter()
    time_dinic = t1 - t0
    flows_dinic = dinic.flows_on_original_edges(orig_caps)

    # --- 输出比较结果 ---
    print("=== 最大流计算结果 ===")
    print(f"Edmonds-Karp: max flow = {maxflow_ek}, time = {time_ek:.10f} s")
    print(f"Dinic       : max flow = {maxflow_dinic}, time = {time_dinic:.10f} s\n")

    print("Edmonds-Karp 边上实际流量 (u,v,flow):")
    for (u, v), f in sorted(flows_ek.items()):
        print(f"  ({u},{v},{f})")
    print("\nDinic 边上实际流量 (u,v,flow):")
    for (u, v), f in sorted(flows_dinic.items()):
        print(f"  ({u},{v},{f})")

    # 若需要绘图
    if do_plot:
        plot_flows(edges, orig_caps, flows_ek, flows_dinic,
                   title_ek=f"Edmonds-Karp (flow={maxflow_ek}, t={time_ek:.4f}s)",
                   title_dinic=f"Dinic (flow={maxflow_dinic}, t={time_dinic:.4f}s)")

    return {
        "edges": edges,
        "orig_caps": orig_caps,
        "ek": {"maxflow": maxflow_ek, "time": time_ek, "flows": flows_ek},
        "dinic": {"maxflow": maxflow_dinic, "time": time_dinic, "flows": flows_dinic},
    }


if __name__ == "__main__":
    results = main(INPUT_DATA, source=SRC, sink=None, do_plot=True)
