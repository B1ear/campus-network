"""
流量监控和负载均衡算法模块
包括：
1. 实时流量监控和统计
2. 多路径负载均衡（基于容量和权重）
3. 拥塞避免算法
4. 流量分配优化
"""

import networkx as nx
from collections import defaultdict, deque
import heapq
import copy


class TrafficMonitor:
    """流量监控器"""
    
    def __init__(self, nodes, edges):
        """
        初始化流量监控器
        Args:
            nodes: 节点列表
            edges: 边列表（包含capacity信息）
        """
        self.nodes = nodes
        self.edges = edges
        self.G = self._build_graph()
        self.traffic_data = defaultdict(lambda: {'current': 0, 'capacity': 0, 'utilization': 0.0})
        self._initialize_traffic()
    
    def _build_graph(self):
        """构建有向图"""
        G = nx.DiGraph()
        for node in self.nodes:
            G.add_node(node['id'])
        for edge in self.edges:
            G.add_edge(edge['from'], edge['to'], 
                      weight=edge.get('weight', 0),
                      capacity=edge.get('capacity', 1000))
        return G
    
    def _initialize_traffic(self):
        """初始化流量数据"""
        for edge in self.edges:
            u, v = edge['from'], edge['to']
            capacity = edge.get('capacity', 1000)
            self.traffic_data[(u, v)] = {
                'current': 0,
                'capacity': capacity,
                'utilization': 0.0
            }
    
    def update_traffic(self, edge_flows):
        """
        更新流量数据
        Args:
            edge_flows: dict {(u,v): flow_value}
        """
        for (u, v), flow in edge_flows.items():
            if (u, v) in self.traffic_data:
                capacity = self.traffic_data[(u, v)]['capacity']
                self.traffic_data[(u, v)]['current'] = flow
                self.traffic_data[(u, v)]['utilization'] = flow / capacity if capacity > 0 else 0
    
    def get_congested_links(self, threshold=0.8):
        """
        获取拥塞链路（利用率超过阈值）
        Args:
            threshold: 拥塞阈值（0-1之间）
        Returns:
            list: 拥塞链路列表
        """
        congested = []
        for (u, v), data in self.traffic_data.items():
            if data['utilization'] >= threshold:
                congested.append({
                    'from': u,
                    'to': v,
                    'utilization': data['utilization'],
                    'current': data['current'],
                    'capacity': data['capacity']
                })
        return congested
    
    def get_traffic_statistics(self):
        """
        获取流量统计信息
        Returns:
            dict: 统计信息
        """
        if not self.traffic_data:
            return {
                'total_traffic': 0,
                'total_capacity': 0,
                'average_utilization': 0,
                'max_utilization': 0,
                'num_congested': 0
            }
        
        utilizations = [data['utilization'] for data in self.traffic_data.values()]
        total_traffic = sum(data['current'] for data in self.traffic_data.values())
        total_capacity = sum(data['capacity'] for data in self.traffic_data.values())
        
        return {
            'total_traffic': total_traffic,
            'total_capacity': total_capacity,
            'average_utilization': sum(utilizations) / len(utilizations),
            'max_utilization': max(utilizations) if utilizations else 0,
            'num_congested': len(self.get_congested_links(0.8)),
            'num_links': len(self.traffic_data)
        }


class LoadBalancer:
    """多路径负载均衡器"""
    
    def __init__(self, nodes, edges):
        """
        初始化负载均衡器
        Args:
            nodes: 节点列表
            edges: 边列表
        """
        self.nodes = nodes
        self.edges = edges
        self.G = self._build_graph()
    
    def _build_graph(self):
        """构建带权重的有向图"""
        G = nx.DiGraph()
        for node in self.nodes:
            G.add_node(node['id'])
        for edge in self.edges:
            G.add_edge(edge['from'], edge['to'],
                      weight=edge.get('weight', 1),
                      capacity=edge.get('capacity', 1000),
                      cost=edge.get('cost', edge.get('weight', 1)))
        return G
    
    def find_k_shortest_paths(self, source, target, k=3):
        """
        寻找k条最短路径（用于负载均衡）
        Args:
            source: 源节点
            target: 目标节点
            k: 路径数量
        Returns:
            list: 路径列表
        """
        try:
            # 使用Yen's算法找k条最短路径
            paths = []
            
            # 先找最短路径
            try:
                shortest = nx.shortest_path(self.G, source, target, weight='weight')
                paths.append(shortest)
            except nx.NetworkXNoPath:
                return []
            
            # 寻找其他短路径（简化版本）
            for i in range(1, k):
                # 使用简单的替代方法：暂时移除已使用的边
                G_temp = self.G.copy()
                
                # 移除之前路径的一些边
                if i < len(paths):
                    for j in range(len(paths[-1]) - 1):
                        u, v = paths[-1][j], paths[-1][j+1]
                        if G_temp.has_edge(u, v):
                            G_temp.remove_edge(u, v)
                
                try:
                    path = nx.shortest_path(G_temp, source, target, weight='weight')
                    if path not in paths:
                        paths.append(path)
                except nx.NetworkXNoPath:
                    break
            
            return paths
        except Exception:
            return []
    
    def allocate_flow_equal(self, source, target, total_flow, k=3):
        """
        等分流量到k条路径
        Args:
            source: 源节点
            target: 目标节点
            total_flow: 总流量
            k: 路径数量
        Returns:
            dict: 流量分配结果
        """
        paths = self.find_k_shortest_paths(source, target, k)
        
        if not paths:
            return {'error': 'No path found', 'paths': [], 'edge_flows': {}}
        
        # 等分流量
        flow_per_path = total_flow / len(paths)
        edge_flows = defaultdict(float)
        
        for path in paths:
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                edge_flows[(u, v)] += flow_per_path
        
        return {
            'paths': paths,
            'flow_per_path': flow_per_path,
            'edge_flows': dict(edge_flows),
            'num_paths': len(paths)
        }
    
    def allocate_flow_weighted(self, source, target, total_flow, k=3):
        """
        按容量权重分配流量到k条路径
        Args:
            source: 源节点
            target: 目标节点
            total_flow: 总流量
            k: 路径数量
        Returns:
            dict: 流量分配结果
        """
        paths = self.find_k_shortest_paths(source, target, k)
        
        if not paths:
            return {'error': 'No path found', 'paths': [], 'edge_flows': {}}
        
        # 计算每条路径的瓶颈容量
        path_capacities = []
        for path in paths:
            min_capacity = float('inf')
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                capacity = self.G[u][v].get('capacity', 1000)
                min_capacity = min(min_capacity, capacity)
            path_capacities.append(min_capacity)
        
        # 按容量加权分配流量
        total_capacity = sum(path_capacities)
        if total_capacity == 0:
            # 如果容量为0，回退到等分
            return self.allocate_flow_equal(source, target, total_flow, k)
        
        edge_flows = defaultdict(float)
        path_flows = []
        
        for path, capacity in zip(paths, path_capacities):
            flow = total_flow * (capacity / total_capacity)
            path_flows.append(flow)
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                edge_flows[(u, v)] += flow
        
        return {
            'paths': paths,
            'path_flows': path_flows,
            'path_capacities': path_capacities,
            'edge_flows': dict(edge_flows),
            'num_paths': len(paths)
        }
    
    def optimize_with_congestion_avoidance(self, source, target, total_flow, current_traffic, k=3):
        """
        基于拥塞避免的流量优化分配
        Args:
            source: 源节点
            target: 目标节点
            total_flow: 总流量
            current_traffic: 当前流量状态 {(u,v): {'current': x, 'capacity': y}}
            k: 路径数量
        Returns:
            dict: 优化后的流量分配
        """
        paths = self.find_k_shortest_paths(source, target, k)
        
        if not paths:
            return {'error': 'No path found', 'paths': [], 'edge_flows': {}}
        
        # 计算每条路径的可用容量（考虑当前流量）
        path_available_capacities = []
        for path in paths:
            min_available = float('inf')
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                capacity = self.G[u][v].get('capacity', 1000)
                current = current_traffic.get((u, v), {}).get('current', 0)
                available = capacity - current
                min_available = min(min_available, available)
            path_available_capacities.append(max(0, min_available))
        
        # 按可用容量分配流量
        total_available = sum(path_available_capacities)
        if total_available == 0:
            return {'error': 'No available capacity', 'paths': paths, 'edge_flows': {}}
        
        edge_flows = defaultdict(float)
        path_flows = []
        
        for path, available in zip(paths, path_available_capacities):
            if total_available > 0:
                flow = min(total_flow * (available / total_available), available)
            else:
                flow = 0
            path_flows.append(flow)
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                edge_flows[(u, v)] += flow
        
        return {
            'paths': paths,
            'path_flows': path_flows,
            'path_available_capacities': path_available_capacities,
            'edge_flows': dict(edge_flows),
            'num_paths': len(paths),
            'total_allocated': sum(path_flows)
        }


class CongestionController:
    """拥塞控制器"""
    
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.G = self._build_graph()
    
    def _build_graph(self):
        """构建图"""
        G = nx.DiGraph()
        for node in self.nodes:
            G.add_node(node['id'])
        for edge in self.edges:
            G.add_edge(edge['from'], edge['to'],
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
