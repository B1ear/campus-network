"""
简化后的流量路径与分配模块（仅保留前端实际使用的功能）
"""

import networkx as nx


class LoadBalancer:
    """多路径负载均衡器（用于路径计算）"""

    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.G = self._build_graph()

    def _build_graph(self):
        """构建带权重与容量的有向图（无向边双向添加）"""
        G = nx.DiGraph()
        for node in self.nodes:
            G.add_node(node['id'])
        for edge in self.edges:
            # 正向与反向边（便于无向拓扑）
            for u, v in [(edge['from'], edge['to']), (edge['to'], edge['from'])]:
                G.add_edge(
                    u,
                    v,
                    weight=edge.get('weight', 1),
                    capacity=edge.get('capacity', 1000),
                    cost=edge.get('cost', edge.get('weight', 1)),
                )
        return G

    def find_k_shortest_paths(self, source, target, k=3):
        """基于加惩罚的多条最短路径搜索"""
        try:
            paths = []
            # 第一条最短路径
            try:
                shortest = nx.shortest_path(self.G, source, target, weight='weight')
                paths.append(shortest)
            except nx.NetworkXNoPath:
                return []

            # 策略1：避免已用边（边不相交）
            used_edges = set()
            for path in paths:
                for i in range(len(path) - 1):
                    used_edges.add((path[i], path[i + 1]))

            for _ in range(1, k):
                G_temp = self.G.copy()
                for u, v in used_edges:
                    if G_temp.has_edge(u, v):
                        G_temp.remove_edge(u, v)
                try:
                    path = nx.shortest_path(G_temp, source, target, weight='weight')
                    if path not in paths:
                        paths.append(path)
                        for i in range(len(path) - 1):
                            used_edges.add((path[i], path[i + 1]))
                        if len(paths) >= k:
                            break
                except nx.NetworkXNoPath:
                    break

            # 策略2：对已使用边增加权重惩罚
            if len(paths) < k:
                edge_penalty = {}
                for path in paths:
                    for i in range(len(path) - 1):
                        e = (path[i], path[i + 1])
                        edge_penalty[e] = edge_penalty.get(e, 0) + 1

                for _ in range(len(paths), k):
                    G_temp = self.G.copy()
                    for (u, v), penalty in edge_penalty.items():
                        if G_temp.has_edge(u, v):
                            original = G_temp[u][v]['weight']
                            G_temp[u][v]['weight'] = original * (1 + penalty * 10)
                    try:
                        path = nx.shortest_path(G_temp, source, target, weight='weight')
                        if path not in paths:
                            paths.append(path)
                            for i in range(len(path) - 1):
                                e = (path[i], path[i + 1])
                                edge_penalty[e] = edge_penalty.get(e, 0) + 1
                    except nx.NetworkXNoPath:
                        break

            return paths
        except Exception:
            import traceback
            traceback.print_exc()
            return []


def calculate_paths_with_allocation(
    nodes,
    edges,
    source,
    target,
    total_flow,
    strategy='balanced',
    num_paths=3,
):
    """
    计算路径和流量分配（供 /api/traffic/calculate-paths 使用）
    """
    balancer = LoadBalancer(nodes, edges)

    # 根据策略确定路径数量
    k = 1 if strategy == 'single' else num_paths

    # 查找 k 条路径
    paths = balancer.find_k_shortest_paths(source, target, k)
    if not paths:
        return {'error': 'No path found', 'paths': [], 'path_allocations': []}

    # 计算每条路径的瓶颈容量
    path_capacities = []
    for path in paths:
        min_capacity = float('inf')
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            capacity = balancer.G[u][v].get('capacity', 1000)
            min_capacity = min(min_capacity, capacity)
        path_capacities.append(min_capacity)

    total_capacity = sum(path_capacities)
    actual_flow = min(total_flow, total_capacity)
    is_limited = actual_flow < total_flow

    # 分配流量
    path_allocations = []
    if strategy == 'single':
        flow = min(actual_flow, path_capacities[0])
        path_allocations.append({
            'flow': flow,
            'capacity': path_capacities[0],
            'utilization': flow / path_capacities[0] if path_capacities[0] > 0 else 0,
        })
    else:
        for capacity in path_capacities:
            flow = (capacity / total_capacity) * actual_flow if total_capacity > 0 else 0
            flow = min(flow, capacity)
            path_allocations.append({
                'flow': flow,
                'capacity': capacity,
                'utilization': flow / capacity if capacity > 0 else 0,
            })

    return {
        'paths': paths,
        'path_allocations': path_allocations,
        'total_capacity': total_capacity,
        'requested_flow': total_flow,
        'actual_flow': actual_flow,
        'is_limited': is_limited,
        'num_paths': len(paths),
    }
