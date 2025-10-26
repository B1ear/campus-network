"""
网络鲁棒性分析模块
包括：
1. 识别关键边（桥 Bridge）- 删除后导致网络断开的边
2. 识别关键节点（割点 Articulation Point）- 删除后导致网络断开的节点
3. 网络连通性评估
4. 鲁棒性指标计算
"""

import networkx as nx
from collections import defaultdict


class RobustnessAnalyzer:
    """网络鲁棒性分析器"""
    
    def __init__(self, nodes, edges):
        """
        初始化分析器
        Args:
            nodes: 节点列表 [{'id': 0, 'label': '0'}, ...]
            edges: 边列表 [{'from': 0, 'to': 1, 'weight': 10}, ...]
        """
        self.nodes = nodes
        self.edges = edges
        self.G = self._build_graph()
    
    def _build_graph(self):
        """构建NetworkX图对象"""
        G = nx.Graph()
        for node in self.nodes:
            G.add_node(node['id'])
        for edge in self.edges:
            G.add_edge(edge['from'], edge['to'], 
                      weight=edge.get('weight', 0),
                      capacity=edge.get('capacity', 0))
        return G
    
    def find_bridges(self):
        """
        寻找所有桥（关键边）
        Returns:
            list: [(u, v), ...] 桥的列表
        """
        if not nx.is_connected(self.G):
            # 如果图本身不连通，返回空列表
            return []
        
        # NetworkX提供了直接查找桥的函数
        bridges = list(nx.bridges(self.G))
        return bridges
    
    def find_articulation_points(self):
        """
        寻找所有割点（关键节点）
        Returns:
            list: [node_id, ...] 割点的列表
        """
        if not nx.is_connected(self.G):
            # 如果图本身不连通，返回空列表
            return []
        
        # NetworkX提供了直接查找割点的函数
        articulation_points = list(nx.articulation_points(self.G))
        return articulation_points
    
    def evaluate_edge_criticality(self):
        """
        评估每条边的关键性
        Returns:
            dict: {(u,v): {'is_bridge': bool, 'criticality_score': float}}
        """
        bridges = set(self.find_bridges())
        edge_criticality = {}
        
        for edge in self.edges:
            u, v = edge['from'], edge['to']
            edge_tuple = tuple(sorted([u, v]))
            
            # 判断是否为桥
            is_bridge = edge_tuple in bridges or (v, u) in bridges
            
            # 计算关键性得分（基于度数和是否为桥）
            degree_u = self.G.degree(u)
            degree_v = self.G.degree(v)
            
            # 关键性得分：桥权重更高，连接低度数节点的边更关键
            criticality_score = 0.0
            if is_bridge:
                criticality_score = 1.0
            else:
                # 非桥边的关键性基于连接节点的度数
                criticality_score = 1.0 / ((degree_u + degree_v) / 2.0)
            
            edge_criticality[(u, v)] = {
                'is_bridge': is_bridge,
                'criticality_score': criticality_score,
                'degree_product': degree_u * degree_v
            }
        
        return edge_criticality
    
    def evaluate_node_criticality(self):
        """
        评估每个节点的关键性
        Returns:
            dict: {node_id: {'is_articulation': bool, 'criticality_score': float}}
        """
        articulation_points = set(self.find_articulation_points())
        node_criticality = {}
        
        for node in self.nodes:
            node_id = node['id']
            is_articulation = node_id in articulation_points
            
            # 计算关键性得分
            degree = self.G.degree(node_id)
            betweenness = nx.betweenness_centrality(self.G).get(node_id, 0)
            
            # 关键性得分：割点权重最高，然后考虑度数和介数中心性
            if is_articulation:
                criticality_score = 1.0
            else:
                # 结合度数和介数中心性
                criticality_score = (degree / max(dict(self.G.degree()).values()) * 0.5 +
                                    betweenness * 0.5)
            
            node_criticality[node_id] = {
                'is_articulation': is_articulation,
                'criticality_score': criticality_score,
                'degree': degree,
                'betweenness': betweenness
            }
        
        return node_criticality
    
    def compute_robustness_metrics(self):
        """
        计算网络鲁棒性指标
        Returns:
            dict: 包含多个鲁棒性指标
        """
        bridges = self.find_bridges()
        articulation_points = self.find_articulation_points()
        
        num_nodes = self.G.number_of_nodes()
        num_edges = self.G.number_of_edges()
        
        # 基本连通性指标
        is_connected = nx.is_connected(self.G)
        num_components = nx.number_connected_components(self.G)
        
        # 鲁棒性指标
        metrics = {
            'is_connected': is_connected,
            'num_components': num_components,
            'num_bridges': len(bridges),
            'num_articulation_points': len(articulation_points),
            'bridge_ratio': len(bridges) / num_edges if num_edges > 0 else 0,
            'articulation_ratio': len(articulation_points) / num_nodes if num_nodes > 0 else 0,
            'average_degree': sum(dict(self.G.degree()).values()) / num_nodes if num_nodes > 0 else 0,
            'density': nx.density(self.G),
            'average_clustering': nx.average_clustering(self.G),
        }
        
        # 计算节点连通性（平均最短路径长度）
        if is_connected:
            metrics['average_shortest_path'] = nx.average_shortest_path_length(self.G)
            metrics['diameter'] = nx.diameter(self.G)
        else:
            metrics['average_shortest_path'] = float('inf')
            metrics['diameter'] = float('inf')
        
        # 鲁棒性得分（0-1之间，越高越鲁棒）
        # 综合考虑：桥比例、割点比例、平均度数、密度、聚类系数
        robustness_score = (
            (1 - metrics['bridge_ratio']) * 0.25 +
            (1 - metrics['articulation_ratio']) * 0.25 +
            min(metrics['average_degree'] / 4.0, 1.0) * 0.2 +
            metrics['density'] * 0.15 +
            metrics['average_clustering'] * 0.15
        )
        metrics['robustness_score'] = robustness_score
        
        return metrics
    
    def simulate_edge_removal(self, edge_from, edge_to):
        """
        模拟移除一条边后的网络状态
        Args:
            edge_from: 边的起点
            edge_to: 边的终点
        Returns:
            dict: 移除后的网络状态信息
        """
        G_copy = self.G.copy()
        
        # 检查边是否存在
        if not G_copy.has_edge(edge_from, edge_to):
            return {'error': 'Edge does not exist'}
        
        # 移除边
        G_copy.remove_edge(edge_from, edge_to)
        
        # 分析移除后的状态
        is_connected = nx.is_connected(G_copy)
        num_components = nx.number_connected_components(G_copy)
        
        result = {
            'is_connected': is_connected,
            'num_components': num_components,
            'was_bridge': num_components > 1,
            'components': list(nx.connected_components(G_copy))
        }
        
        return result
    
    def simulate_node_removal(self, node_id):
        """
        模拟移除一个节点后的网络状态
        Args:
            node_id: 要移除的节点ID
        Returns:
            dict: 移除后的网络状态信息
        """
        G_copy = self.G.copy()
        
        # 检查节点是否存在
        if not G_copy.has_node(node_id):
            return {'error': 'Node does not exist'}
        
        # 移除节点
        G_copy.remove_node(node_id)
        
        # 分析移除后的状态
        is_connected = nx.is_connected(G_copy) if G_copy.number_of_nodes() > 0 else False
        num_components = nx.number_connected_components(G_copy)
        
        result = {
            'is_connected': is_connected,
            'num_components': num_components,
            'was_articulation': num_components > 1,
            'components': list(nx.connected_components(G_copy)) if G_copy.number_of_nodes() > 0 else []
        }
        
        return result
    
    def get_redundant_paths(self, source, target):
        """
        获取两个节点之间的冗余路径数量
        Args:
            source: 源节点
            target: 目标节点
        Returns:
            dict: 包含路径数量和路径列表
        """
        try:
            # 查找所有简单路径（限制最多10条，避免计算过久）
            all_paths = list(nx.all_simple_paths(self.G, source, target, cutoff=15))
            
            # 限制返回的路径数量
            if len(all_paths) > 10:
                all_paths = all_paths[:10]
            
            return {
                'num_paths': len(all_paths),
                'paths': all_paths,
                'has_redundancy': len(all_paths) > 1
            }
        except nx.NetworkXNoPath:
            return {
                'num_paths': 0,
                'paths': [],
                'has_redundancy': False
            }


def analyze_network_robustness(nodes, edges):
    """
    执行完整的网络鲁棒性分析
    Args:
        nodes: 节点列表
        edges: 边列表
    Returns:
        dict: 完整的分析结果
    """
    analyzer = RobustnessAnalyzer(nodes, edges)
    
    bridges = analyzer.find_bridges()
    articulation_points = analyzer.find_articulation_points()
    edge_criticality = analyzer.evaluate_edge_criticality()
    node_criticality = analyzer.evaluate_node_criticality()
    metrics = analyzer.compute_robustness_metrics()
    
    return {
        'bridges': [{'from': u, 'to': v} for u, v in bridges],
        'articulation_points': articulation_points,
        'edge_criticality': {f"{u}-{v}": val for (u, v), val in edge_criticality.items()},
        'node_criticality': node_criticality,
        'metrics': metrics
    }
