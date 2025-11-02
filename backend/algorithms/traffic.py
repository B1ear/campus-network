"""
简化后的流量路径与分配模块（仅保留前端实际使用的功能）
"""

import networkx as nx


class LoadBalancer:
    """多路径负载均衡器（用于路径计算）"""

    def __init__(self, nodes, edges, edge_usage=None):
        self.nodes = nodes
        self.edges = edges
        self.edge_usage = edge_usage or {}  # 边使用情况字典 {(u,v): used_flow}
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

    def find_k_shortest_paths(self, source, target, k=3, utilization_threshold=0.8):
        """基于加惩罚的多条最短路径搜索，考虑链路利用率阈值
        
        Args:
            source: 源节点
            target: 目标节点
            k: 最多返回k条路径
            utilization_threshold: 链路利用率阈值（默认0.8，即80%）
        """
        try:
            paths = []
            
            # 创建考虑链路占用率的临时图
            G_weighted = self.G.copy()
            for u, v in G_weighted.edges():
                capacity = G_weighted[u][v].get('capacity', 1000)
                used_flow = self.edge_usage.get((u, v), 0)
                utilization = used_flow / capacity if capacity > 0 else 0
                
                # 如果链路占用率超过阈值，大幅增加权重惩罚
                original_weight = G_weighted[u][v]['weight']
                if utilization >= 0.95:  # 接近饱和（95%+）
                    # 极高惩罚，几乎不可能被选中
                    penalty_factor = 1 + (utilization - 0.95) * 200
                    G_weighted[u][v]['weight'] = original_weight * max(penalty_factor, 100)
                elif utilization >= utilization_threshold:  # 80%-95%
                    # 根据超出阈值的程度增加惩罚（指数增长）
                    penalty_factor = 1 + (utilization - utilization_threshold) * 100
                    G_weighted[u][v]['weight'] = original_weight * penalty_factor
                elif utilization > 0.5:  # 50%-80%之间也给予较小的惩罚
                    penalty_factor = 1 + (utilization - 0.5) * 3
                    G_weighted[u][v]['weight'] = original_weight * penalty_factor
            
            # 第一条最短路径（考虑链路占用）
            try:
                shortest = nx.shortest_path(G_weighted, source, target, weight='weight')
                paths.append(shortest)
            except nx.NetworkXNoPath:
                return []

            # 策略1：避免已用边（边不相交），同时考虑链路占用率
            used_edges = set()
            for path in paths:
                for i in range(len(path) - 1):
                    used_edges.add((path[i], path[i + 1]))

            for _ in range(1, k):
                G_temp = G_weighted.copy()  # 使用已经考虑链路占用的图
                
                # 移除已使用的边（但如果链路未饱和，仍可作为备选）
                for u, v in used_edges:
                    if G_temp.has_edge(u, v):
                        capacity = self.G[u][v].get('capacity', 1000)
                        used_flow = self.edge_usage.get((u, v), 0)
                        utilization = used_flow / capacity if capacity > 0 else 0
                        
                        # 如果链路已接近饱和（>95%），则移除；否则保留但增加惩罚
                        if utilization >= 0.95:
                            G_temp.remove_edge(u, v)
                        else:
                            # 继续增加惩罚，避免重复使用
                            G_temp[u][v]['weight'] *= 5
                
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

            # 策略2：对已使用边增加权重惩罚（同时考虑链路占用率）
            if len(paths) < k:
                edge_penalty = {}
                for path in paths:
                    for i in range(len(path) - 1):
                        e = (path[i], path[i + 1])
                        edge_penalty[e] = edge_penalty.get(e, 0) + 1

                for _ in range(len(paths), k):
                    G_temp = G_weighted.copy()  # 基于已考虑链路占用的图
                    for (u, v), penalty in edge_penalty.items():
                        if G_temp.has_edge(u, v):
                            # 检查链路占用率
                            capacity = self.G[u][v].get('capacity', 1000)
                            used_flow = self.edge_usage.get((u, v), 0)
                            utilization = used_flow / capacity if capacity > 0 else 0
                            
                            # 如果接近饱和，大幅增加惩罚；否则适度增加
                            if utilization >= 0.95:
                                G_temp[u][v]['weight'] *= (1 + penalty * 100)
                            else:
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


def _determine_optimal_k(balancer, source, target, total_flow, max_k, edge_usage):
    """
    智能确定最优的路径数量k
    
    策略：
    1. 逐步增加k，计算每个 k 下的总可用容量
    2. 当总可用容量足以满足流量需求时停止
    3. 或者当新增路径的边际收益太小时停止
    4. 或者达到最大k值时停止
    
    Args:
        balancer: LoadBalancer实例
        source: 源节点
        target: 目标节点
        total_flow: 总流量需求
        max_k: 最大路径数
        edge_usage: 边使用情况
    
    Returns:
        最优的k值（最小为3）
    """
    MIN_K = 3  # 最小路径数设为3
    MARGINAL_BENEFIT_THRESHOLD = 0.1  # 边际收益阈值（10%）
    
    best_k = MIN_K
    prev_capacity = 0
    
    for k in range(MIN_K, max_k + 1):
        # 尝试找到 k 条路径
        paths = balancer.find_k_shortest_paths(source, target, k)
        
        if len(paths) < k:
            # 无法找到更多路径，返回当前k
            best_k = len(paths)
            break
        
        # 计算当前k下的总可用容量
        total_available = 0
        for path in paths:
            min_available = float('inf')
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                capacity = balancer.G[u][v].get('capacity', 1000)
                used_flow = max(
                    edge_usage.get((u, v), 0) if edge_usage else 0,
                    edge_usage.get((v, u), 0) if edge_usage else 0
                )
                available = max(0, capacity - used_flow)
                min_available = min(min_available, available)
            total_available += min_available
        
        # 判断是否需要继续增加k
        
        # 条件1：容量已足够（留有20%缓冲）
        if total_available >= total_flow * 1.2:
            best_k = k
            break
        
        # 条件2：边际收益太小
        if k > 1:
            marginal_benefit = (total_available - prev_capacity) / prev_capacity if prev_capacity > 0 else 1
            if marginal_benefit < MARGINAL_BENEFIT_THRESHOLD:
                # 新增路径的收益小于10%，不值得继续
                best_k = max(k - 1, MIN_K)  # 保证不低于MIN_K
                break
        
        prev_capacity = total_available
        best_k = k
    
    return best_k


def calculate_paths_with_allocation(
    nodes,
    edges,
    source,
    target,
    total_flow,
    strategy='balanced',
    num_paths=3,
    edge_usage=None,
    auto_k=True,
):
    """
    计算路径和流量分配（供 /api/traffic/calculate-paths 使用）
    
    Args:
        nodes: 节点列表
        edges: 边列表
        source: 源节点
        target: 目标节点
        total_flow: 总流量需求
        strategy: 分配策略 ('single' 或 'balanced')
        num_paths: 路径数量上限（当auto_k=True时作为最大值）
        edge_usage: 当前边使用情况字典 {(u,v): used_flow}，用于多次调用时累积
        auto_k: 是否智能选择k值（默认True）
    """
    balancer = LoadBalancer(nodes, edges, edge_usage)

    # 根据策略确定路径数量
    if strategy == 'single':
        k = 1
    else:
        # 智能选择k值
        if auto_k:
            k = _determine_optimal_k(balancer, source, target, total_flow, num_paths, edge_usage)
        else:
            k = num_paths

    # 查找 k 条路径
    paths = balancer.find_k_shortest_paths(source, target, k)
    if not paths:
        return {'error': 'No path found', 'paths': [], 'path_allocations': []}

    # 计算每条路径的可用容量（考虑已占用的流量）
    path_capacities = []
    path_available_capacities = []  # 实际可用容量
    
    for path in paths:
        min_capacity = float('inf')  # 路径的原始容量
        min_available = float('inf')  # 路径的实际可用容量
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            
            # 获取边的总容量
            capacity = balancer.G[u][v].get('capacity', 1000)
            min_capacity = min(min_capacity, capacity)
            
            # 计算剩余容量（考虑当前占用）
            # 无向图，需要检查两个方向
            used_flow = max(
                edge_usage.get((u, v), 0) if edge_usage else 0,
                edge_usage.get((v, u), 0) if edge_usage else 0
            )
            available = max(0, capacity - used_flow)  # 确保不为负
            min_available = min(min_available, available)
        
        path_capacities.append(min_capacity)  # 原始容量（用于显示）
        path_available_capacities.append(min_available)  # 实际可用容量（用于分配）

    # 使用实际可用容量计算总容量
    total_available_capacity = sum(path_available_capacities)
    actual_flow = min(total_flow, total_available_capacity)
    is_limited = actual_flow < total_flow

    # 识别共享边（被多条路径使用的边）
    edge_to_paths = {}  # {(u,v): [path_indices]}
    for path_idx, path in enumerate(paths):
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            # 无向图，统一表示
            edge_key = tuple(sorted([u, v]))
            if edge_key not in edge_to_paths:
                edge_to_paths[edge_key] = []
            edge_to_paths[edge_key].append(path_idx)
    
    # 找到所有共享边（被多条路径使用）
    shared_edges = {k: v for k, v in edge_to_paths.items() if len(v) > 1}
    
    # 分配流量（基于实际可用容量）
    path_allocations = []
    if strategy == 'single':
        # 单路径策略：使用第一条路径的可用容量
        available = path_available_capacities[0]
        flow = min(actual_flow, available)
        path_allocations.append({
            'flow': flow,
            'capacity': path_capacities[0],  # 原始容量
            'available_capacity': available,  # 实际可用容量
            'utilization': flow / path_capacities[0] if path_capacities[0] > 0 else 0,
        })
    else:
        # 多路径负载均衡策略：按照可用容量比例分配流量，并考虑共享边约束
        
        # 初始分配：按照可用容量比例
        flow_allocations = []
        for i, (capacity, available) in enumerate(zip(path_capacities, path_available_capacities)):
            if total_available_capacity > 0:
                flow = (available / total_available_capacity) * actual_flow
                flow = min(flow, available)
            else:
                flow = 0
            flow_allocations.append(flow)
        
        # 如果有共享边，需要调整流量分配
        if shared_edges:
            # 迭代调整，确保所有共享边不超限
            max_iterations = 10
            for iteration in range(max_iterations):
                violated = False
                
                for edge_key, path_indices in shared_edges.items():
                    # 计算这条共享边的总流量
                    total_edge_flow = sum(flow_allocations[idx] for idx in path_indices)
                    
                    # 获取这条边的可用容量
                    u, v = edge_key
                    edge = next((e for e in edges if 
                               (e['from'] == u and e['to'] == v) or 
                               (e['from'] == v and e['to'] == u)), None)
                    
                    if edge:
                        capacity = edge['capacity']
                        used_flow = max(
                            edge_usage.get((u, v), 0) if edge_usage else 0,
                            edge_usage.get((v, u), 0) if edge_usage else 0
                        )
                        available_capacity = max(0, capacity - used_flow)
                        
                        # 如果总流量超过可用容量，需要按比例减少
                        if total_edge_flow > available_capacity + 0.01:
                            violated = True
                            scale_factor = available_capacity / total_edge_flow if total_edge_flow > 0 else 0
                            
                            # 按比例减少所有使用这条边的路径的流量
                            for idx in path_indices:
                                flow_allocations[idx] *= scale_factor
                
                # 如果没有违规，结束迭代
                if not violated:
                    break
        
        # 生成最终分配结果
        for i, (capacity, available, flow) in enumerate(zip(path_capacities, path_available_capacities, flow_allocations)):
            path_allocations.append({
                'flow': flow,
                'capacity': capacity,  # 原始容量
                'available_capacity': available,  # 实际可用容量
                'utilization': flow / capacity if capacity > 0 else 0,
            })
        
        # 更新实际流量
        actual_flow = sum(flow_allocations)
        
        # 重新检查是否被限制（共享边约束可能导致流量被减少）
        is_limited = actual_flow < total_flow

    return {
        'paths': paths,
        'path_allocations': path_allocations,
        'total_capacity': sum(path_capacities),  # 原始总容量
        'total_available_capacity': total_available_capacity,  # 实际可用总容量
        'requested_flow': total_flow,
        'actual_flow': actual_flow,
        'is_limited': is_limited,
        'num_paths': len(paths),
    }
