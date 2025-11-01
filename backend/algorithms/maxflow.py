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
import matplotlib
matplotlib.use('Agg')
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
def edmonds_karp(source, sink, capacity, adj, return_steps=False, nodes=None, edges_list=None):
    # capacity is a dict (u,v)->remaining cap, modifies in-place
    flow = 0
    steps = []
    iteration = 0
    fixed_layout = None  # 用于保存固定布局
    
    if return_steps:
        from algorithms.utils import draw_maxflow_step_visualization, compute_fixed_layout, draw_maxflow_result
        # 为可视化准备节点与边（即使调用方未提供，也做兼容）
        if nodes and edges_list:
            vis_nodes = nodes
            vis_edges = edges_list
        else:
            # 从残量图推断节点与边（初始状态下等同原始容量）
            node_set = set([source, sink])
            for u in adj:
                node_set.add(u)
                for v in adj[u]:
                    node_set.add(v)
            vis_nodes = [{'id': n} for n in sorted(node_set)]
            vis_edges = []
            for u in adj:
                for v in adj[u]:
                    cap_uv = capacity.get((u, v), 0)
                    if cap_uv > 0:
                        vis_edges.append({'from': u, 'to': v, 'capacity': cap_uv})
        # 预先计算固定布局并绘制初始化帧
        fixed_layout = compute_fixed_layout(vis_nodes, vis_edges)
        history_paths = []
        viz = draw_maxflow_step_visualization(vis_nodes, vis_edges, source, sink, None, 0, "Edmonds-Karp", fixed_layout, history_paths)
        steps.append({
            'step': 0,
            'description': f'初始化：源点 {source}, 汇点 {sink}',
            'flow': 0,
            'path': None,
            'bottleneck': None,
            'visualization': viz
        })
    
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
        
        # 构建路径
        path = []
        v = sink
        while v != source:
            u = parent[v]
            path.append((u, v))
            v = u
        path.reverse()
        
        inc = bottleneck[sink]
        flow += inc
        iteration += 1
        
        if return_steps:
            viz = None
            if nodes and edges_list:
                viz = draw_maxflow_step_visualization(nodes, edges_list, source, sink, path, flow, "Edmonds-Karp", fixed_layout, history_paths)
            steps.append({
                'step': iteration,
                'description': f'找到增广路径，瓶颈值 {inc}',
                'flow': flow,
                'path': path,
                'bottleneck': inc,
                'visualization': viz
            })
            # 累积历史路径（用于后续帧叠加展示）
            history_paths.append(list(path))
        
        v = sink
        while v != source:
            u = parent[v]
            capacity[(u, v)] -= inc
            capacity[(v, u)] += inc
            if u not in adj[v]:
                adj[v].append(u)
            v = u
    
    if return_steps:
        # 结束帧：显示最终的流量分配（所有路径综合后的结果）
        if nodes and edges_list:
            # 根据初始容量与当前残量计算每条边的最终流量
            final_flow_edges = []
            for e in edges_list:
                u, v = e['from'], e['to']
                cap0 = e.get('capacity', e.get('weight', 0))
                rem = capacity.get((u, v), 0)
                f = max(cap0 - rem, 0)
                if f > 0:
                    final_flow_edges.append({'from': u, 'to': v, 'flow': f})
            from algorithms.utils import draw_maxflow_result
            viz = draw_maxflow_result(nodes, edges_list, final_flow_edges, source, sink, flow, "Edmonds-Karp")
        else:
            # 回退到步骤可视化（无高亮路径）
            viz = draw_maxflow_step_visualization(vis_nodes, vis_edges, source, sink, None, flow, "Edmonds-Karp", fixed_layout, history_paths)
        steps.append({
            'step': iteration + 1,
            'description': f'没有更多增广路径，算法结束（显示最终流量分配）',
            'flow': flow,
            'path': None,
            'bottleneck': None,
            'visualization': viz
        })
        return flow, steps
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

    def dfs_flow(self, u, t, f, level, it, path=None, collect_path=False):
        if collect_path and path is None:
            path = []
        if u == t:
            return (f, list(path)) if collect_path else f
        for i in range(it[u], len(self.adj[u])):
            ei = self.adj[u][i]
            _, v, cap = self.edges[ei]
            if cap > 0 and level.get(v, -1) == level.get(u, -1) + 1:
                if collect_path:
                    path.append((u, v))
                pushed_res = self.dfs_flow(v, t, min(f, cap), level, it, path, collect_path)
                if collect_path:
                    pushed, used_path = pushed_res
                else:
                    pushed = pushed_res
                if pushed > 0:
                    # subtract forward cap, add backward cap
                    self.edges[ei][2] -= pushed
                    self.edges[ei ^ 1][2] += pushed
                    return (pushed, used_path) if collect_path else pushed
                if collect_path and path:
                    path.pop()
            it[u] += 1
        return (0, []) if collect_path else 0

    def max_flow(self, s, t, return_steps=False, nodes=None, edges_list=None):
        flow = 0
        steps = []
        iteration = 0
        fixed_layout = None  # 用于保存固定布局
        
        if return_steps:
            from algorithms.utils import draw_dinic_step_visualization, compute_fixed_layout
            # 预先计算固定布局
            if nodes and edges_list:
                fixed_layout = compute_fixed_layout(nodes, edges_list)
                viz = draw_dinic_step_visualization(nodes, edges_list, s, t, None, 0, 0, "Dinic", fixed_layout)
            else:
                viz = None
            steps.append({
                'step': 0,
                'description': f'初始化Dinic算法：源点 {s}, 汇点 {t}',
                'flow': 0,
                'level': None,
                'pushed': None,
                'visualization': viz
            })
        
        while True:
            level = self.bfs_level(s, t)
            if t not in level:
                if return_steps:
                    viz = None
                    if nodes and edges_list:
                        # 最终结果帧：计算每条边的最终流并绘制
                        final_flows = self.flows_on_original_edges({(e['from'], e['to']): e.get('capacity', e.get('weight', 0)) for e in edges_list})
                        flow_edges_list = [{'from': u, 'to': v, 'flow': f} for (u, v), f in final_flows.items() if f > 0]
                        from algorithms.utils import draw_maxflow_result
                        viz = draw_maxflow_result(nodes, edges_list, flow_edges_list, s, t, flow, "Dinic")
                    steps.append({
                        'step': iteration + 999,
                        'description': '没有更多层次图，算法结束（显示最终流量分配）',
                        'flow': flow,
                        'level': level,
                        'pushed': None,
                        'visualization': viz
                    })
                break
            
            it = defaultdict(int)
            phase_flow = 0
            phase_paths = []
            # 在阶段开始时生成一帧，展示层次图
            if return_steps and nodes and edges_list:
                viz = draw_dinic_step_visualization(
                    nodes, edges_list, s, t, level, flow, 0, "Dinic", fixed_layout,
                    current_path=None, path_history=phase_paths
                )
                steps.append({
                    'step': iteration + 0.1,
                    'description': '构建层次图（BFS）',
                    'flow': flow,
                    'level': level,
                    'pushed': 0,
                    'visualization': viz
                })
            while True:
                if return_steps:
                    pushed, aug_path = self.dfs_flow(s, t, float('inf'), level, it, path=[], collect_path=True)
                else:
                    pushed = self.dfs_flow(s, t, float('inf'), level, it)
                if pushed == 0:
                    break
                # 统计当前路径上饱和边（推完之后剩余cap为0的前向边）
                saturated = []
                if return_steps:
                    for (uu, vv) in aug_path:
                        # 找到前向边的剩余cap
                        fcap = None
                        for ei in self.adj[uu]:
                            if ei % 2 == 0 and self.edges[ei][1] == vv:
                                fcap = self.edges[ei][2]
                                break
                        if fcap == 0:
                            saturated.append((uu, vv))
                flow += pushed
                phase_flow += pushed
                if return_steps and nodes and edges_list:
                    # 每次增广后输出一帧：当前路径红色，高亮历史路径淡蓝，标注瓶颈与饱和边
                    phase_paths.append(list(aug_path) if return_steps else [])
                    viz = draw_dinic_step_visualization(
                        nodes, edges_list, s, t, level, flow, phase_flow, "Dinic", fixed_layout,
                        current_path=aug_path, path_history=phase_paths, bottleneck=pushed, saturated_edges=saturated
                    )
                    steps.append({
                        'step': iteration + 0.2 + len(phase_paths) * 0.01,
                        'description': f'沿阻塞网络增广一条路径，瓶颈值 {pushed}',
                        'flow': flow,
                        'level': level,
                        'pushed': pushed,
                        'visualization': viz
                    })
            
            iteration += 1
            if return_steps:
                viz = None
                if nodes and edges_list:
                    viz = draw_dinic_step_visualization(nodes, edges_list, s, t, level, flow, phase_flow, "Dinic", fixed_layout,
                                                        current_path=None, path_history=phase_paths, bottleneck=None, saturated_edges=None)
                steps.append({
                    'step': iteration + 1,
                    'description': f'完成一个阶段，本阶段增加流量 {phase_flow}',
                    'flow': flow,
                    'level': level,
                    'pushed': phase_flow,
                    'visualization': viz
                })
        
        if return_steps:
            return flow, steps
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
def main(input_data, source=SRC, sink=None, do_plot=True, return_steps=False):
    edges = parse_directed_input(input_data)
    _, _, orig_caps, nodes = build_capacity_graph(edges)
    if sink is None:
        sink = max(nodes)
    # --- Edmonds-Karp ---
    cap_ek, adj_ek, orig_caps_ek, _ = build_capacity_graph(edges)
    # copy because algorithm modifies capacity in-place; make independent copy for Dinic
    cap_ek_copy = copy.deepcopy(cap_ek)
    adj_ek_copy = copy.deepcopy(adj_ek)

    # 准备可视化需要的数据
    nodes_for_viz = list(nodes)
    edges_for_viz = [{'from': u, 'to': v, 'capacity': w} for u, v, w in edges]
    
    t0 = time.perf_counter()
    if return_steps:
        maxflow_ek, steps_ek = edmonds_karp(source, sink, cap_ek_copy, adj_ek_copy, 
                                            return_steps=True, nodes=nodes_for_viz, edges_list=edges_for_viz)
    else:
        maxflow_ek = edmonds_karp(source, sink, cap_ek_copy, adj_ek_copy)
        steps_ek = None
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
    if return_steps:
        maxflow_dinic, steps_dinic = dinic.max_flow(source, sink, return_steps=True, 
                                                    nodes=nodes_for_viz, edges_list=edges_for_viz)
    else:
        maxflow_dinic = dinic.max_flow(source, sink)
        steps_dinic = None
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

    result = {
        "edges": edges,
        "ek": {"maxflow": maxflow_ek, "time": time_ek, "flows": flows_ek},
        "dinic": {"maxflow": maxflow_dinic, "time": time_dinic, "flows": flows_dinic},
    }
    
    if return_steps:
        result["ek"]["steps"] = steps_ek
        result["dinic"]["steps"] = steps_dinic
    
    return result


if __name__ == "__main__":
    results = main(INPUT_DATA, source=SRC, sink=None, do_plot=True)
