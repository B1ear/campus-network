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


class CongestionController:
    """拥塞控制器"""
    
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.G = self._build_graph()
    
    def _build_graph(self):
        """构建图（对于无向边，双向添加）"""
        G = nx.DiGraph()
        for node in self.nodes:
            G.add_node(node['id'])
        for edge in self.edges:
            G.add_edge(edge['from'], edge['to'],
                      capacity=edge.get('capacity', 1000))
            # 添加反向边（支持无向图）
            G.add_edge(edge['to'], edge['from'],
                      capacity=edge.get('capacity', 1000))
        return G
    
    def detect_congestion(self, traffic_data, threshold=0.8):
        """
        检测拥塞
        Args:
            traffic_data: 流量数据
            threshold: 拥塞阈值
        Returns:
            dict: 拥塞检测结果
        """
        congested_links = []
        warning_links = []
        
        for (u, v), data in traffic_data.items():
            utilization = data.get('utilization', 0)
            if utilization >= threshold:
                congested_links.append({
                    'from': u,
                    'to': v,
                    'utilization': utilization
                })
            elif utilization >= threshold * 0.7:
                warning_links.append({
                    'from': u,
                    'to': v,
                    'utilization': utilization
                })
        
        return {
            'congested_links': congested_links,
            'warning_links': warning_links,
            'num_congested': len(congested_links),
            'num_warning': len(warning_links),
            'is_congested': len(congested_links) > 0
        }
    
    def suggest_rerouting(self, traffic_data, threshold=0.8):
        """
        建议重路由方案
        Args:
            traffic_data: 流量数据
            threshold: 拥塞阈值
        Returns:
            list: 重路由建议
        """
        congestion = self.detect_congestion(traffic_data, threshold)
        suggestions = []
        
        for link in congestion['congested_links']:
            u, v = link['from'], link['to']
            
            # 尝试找替代路径
            G_temp = self.G.copy()
            if G_temp.has_edge(u, v):
                G_temp.remove_edge(u, v)
                
                try:
                    # 找一条不经过该边的路径
                    alt_path = nx.shortest_path(G_temp, u, v, weight='capacity')
                    suggestions.append({
                        'congested_link': {'from': u, 'to': v},
                        'alternative_path': alt_path,
                        'suggestion': f"将部分流量从 {u}->{v} 重路由到路径 {alt_path}"
                    })
                except nx.NetworkXNoPath:
                    suggestions.append({
                        'congested_link': {'from': u, 'to': v},
                        'alternative_path': None,
                        'suggestion': f"链路 {u}->{v} 拥塞，但无可用替代路径"
                    })
        
        return suggestions


def calculate_paths_with_allocation(nodes, edges, source, target, total_flow, 
                                      strategy='balanced', num_paths=3):
    """
    计算路径和流量分配（用于交互式仿真）
    Args:
        nodes: 节点列表
        edges: 边列表
        source: 源节点
        target: 目标节点
        total_flow: 总流量
        strategy: 策略 'single' 或 'balanced'
        num_paths: 使用的路径数量
    Returns:
        dict: 包含路径列表和分配结果
    """
    balancer = LoadBalancer(nodes, edges)
    
    # 根据策略确定路径数量
    k = 1 if strategy == 'single' else num_paths
    
    # 查找k条最短路径
    paths = balancer.find_k_shortest_paths(source, target, k)
    
    if not paths:
        return {'error': 'No path found', 'paths': [], 'path_allocations': []}
    
    # 计算每条路径的瓶颈容量
    path_capacities = []
    for path in paths:
        min_capacity = float('inf')
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            capacity = balancer.G[u][v].get('capacity', 1000)
            min_capacity = min(min_capacity, capacity)
        path_capacities.append(min_capacity)
    
    # 计算总容量
    total_capacity = sum(path_capacities)
    
    # 检查是否超过容量
    actual_flow = min(total_flow, total_capacity)
    is_limited = actual_flow < total_flow
    
    # 按策略分配流量
    path_allocations = []
    if strategy == 'single':
        # 单路径：使用实际流量，但不超过路径容量
        flow = min(actual_flow, path_capacities[0])
        path_allocations.append({
            'flow': flow,
            'capacity': path_capacities[0],
            'utilization': flow / path_capacities[0] if path_capacities[0] > 0 else 0
        })
    else:
        # 负载均衡：按容量比例分配
        for capacity in path_capacities:
            if total_capacity > 0:
                flow = (capacity / total_capacity) * actual_flow
                flow = min(flow, capacity)
            else:
                flow = 0
            path_allocations.append({
                'flow': flow,
                'capacity': capacity,
                'utilization': flow / capacity if capacity > 0 else 0
            })
    
    return {
        'paths': paths,
        'path_allocations': path_allocations,
        'total_capacity': total_capacity,
        'requested_flow': total_flow,
        'actual_flow': actual_flow,
        'is_limited': is_limited,
        'num_paths': len(paths)
    }


def simulate_traffic_load_balancing(nodes, edges, source, target, total_flow, 
                                    enable_load_balancing=True,
                                    enable_congestion_avoidance=True,
                                    num_paths=3):
    """
    模拟流量负载均衡
    Args:
        nodes: 节点列表
        edges: 边列表
        source: 源节点
        target: 目标节点
        total_flow: 总流量
        enable_load_balancing: 是否启用负载均衡
        enable_congestion_avoidance: 是否启用拥塞避免
        num_paths: 使用的路径数量
    Returns:
        dict: 模拟结果
    """
    monitor = TrafficMonitor(nodes, edges)
    balancer = LoadBalancer(nodes, edges)
    controller = CongestionController(nodes, edges)
    
    # 根据配置选择不同的策略
    if not enable_load_balancing:
        # 单路径传输（最短路径）
        paths = balancer.find_k_shortest_paths(source, target, k=1)
        if not paths:
            return {'error': 'No path found'}
        
        edge_flows = defaultdict(float)
        path = paths[0]
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            edge_flows[(u, v)] = total_flow
        
        result = {
            'strategy': 'single_path',
            'paths': paths,
            'edge_flows': dict(edge_flows),
            'num_paths': 1
        }
    elif enable_congestion_avoidance:
        # 启用拥塞避免的负载均衡
        result = balancer.optimize_with_congestion_avoidance(
            source, target, total_flow, monitor.traffic_data, num_paths
        )
        result['strategy'] = 'load_balancing_with_congestion_avoidance'
    else:
        # 基本的加权负载均衡
        result = balancer.allocate_flow_weighted(source, target, total_flow, num_paths)
        result['strategy'] = 'weighted_load_balancing'
    
    # 转换edge_flows的键为字符串格式（用于JSON序列化）
    if 'edge_flows' in result:
        edge_flows_dict = result['edge_flows']
        # 保存原始格式用于内部使用
        edge_flows_for_monitor = edge_flows_dict.copy()
        # 转换为字符串格式用于JSON
        edge_flows_json = {f"{u}-{v}": flow for (u, v), flow in edge_flows_dict.items()}
        result['edge_flows'] = edge_flows_json
        result['edge_flows_tuple'] = edge_flows_for_monitor  # 保留元组格式供可视化使用
        
        # 更新流量监控
        monitor.update_traffic(edge_flows_for_monitor)
    
    # 检测拥塞
    congestion = controller.detect_congestion(monitor.traffic_data)
    
    # 获取统计信息
    stats = monitor.get_traffic_statistics()
    
    # 转换traffic_data的键为字符串
    traffic_data_json = {f"{u}-{v}": data for (u, v), data in monitor.traffic_data.items()}
    
    return {
        **result,
        'congestion': congestion,
        'statistics': stats,
        'traffic_data': traffic_data_json
    }
