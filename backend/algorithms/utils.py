"""
工具函数
包括数据验证和图形保存
"""
import os


def validate_graph_data(nodes, edges):
    """
    验证图数据的有效性
    
    Args:
        nodes: 节点列表
        edges: 边列表
    
    Returns:
        bool: 数据是否有效
    """
    if not nodes or not edges:
        return False
    
    node_set = set(nodes)
    
    for edge in edges:
        if 'from' not in edge or 'to' not in edge:
            return False
        if edge['from'] not in node_set or edge['to'] not in node_set:
            return False
        if 'weight' not in edge and 'capacity' not in edge:
            return False
    
    return True


def save_plot(filename):
    """
    保存图像的辅助函数
    
    Args:
        filename: 文件名
    
    Returns:
        完整的文件路径
    """
    plot_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'plots')
    os.makedirs(plot_folder, exist_ok=True)
    return os.path.join(plot_folder, filename)


def format_graph_info(nodes, edges):
    """
    格式化图的基本信息
    
    Args:
        nodes: 节点列表
        edges: 边列表
    
    Returns:
        字典包含图的统计信息
    """
    total_weight = sum(edge.get('weight', 0) for edge in edges)
    
    return {
        'node_count': len(nodes),
        'edge_count': len(edges),
        'total_weight': total_weight,
        'nodes': nodes,
        'edges': edges
    }