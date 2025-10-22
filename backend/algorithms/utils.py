"""
工具函数
包括数据验证和图形保存
"""
import os
import io
import base64
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import font_manager


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


def setup_chinese_font():
    """设置中文字体"""
    try:
        zh_font = next(f for f in font_manager.fontManager.ttflist 
                    if "SimHei" in f.name or "Heiti" in f.name or "Source Han" in f.name)
        matplotlib.rcParams['font.sans-serif'] = [zh_font.name]
    except StopIteration:
        matplotlib.rcParams['font.sans-serif'] = ['Arial'] 
    matplotlib.rcParams['axes.unicode_minus'] = False


def draw_mst_result(nodes, all_edges, mst_edges, algorithm_name="MST"):
    """
    绘制最小生成树结果
    
    Args:
        nodes: 节点列表
        all_edges: 所有边的列表
        mst_edges: MST中的边列表
        algorithm_name: 算法名称
    
    Returns:
        base64编码的PNG图片
    """
    setup_chinese_font()
    
    # 创建NetworkX图
    G = nx.Graph()
    
    # 添加节点
    for node in nodes:
        G.add_node(node)
    
    # 添加所有边（用于布局）
    for edge in all_edges:
        G.add_edge(edge['from'], edge['to'], weight=edge.get('weight', 0))
    
    # 创建MST边集
    mst_edge_set = set()
    for edge in mst_edges:
        mst_edge_set.add((min(edge['from'], edge['to']), max(edge['from'], edge['to'])))
    
    # 生成布局
    pos = nx.spring_layout(G, seed=42, k=2.5, iterations=100)
    
    # 绘图
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # 绘制所有边（浅灰色）
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.2, width=1, edge_color='gray')
    
    # 绘制MST边（红色、加粗）
    mst_edges_list = [(edge['from'], edge['to']) for edge in mst_edges]
    nx.draw_networkx_edges(G, pos, edgelist=mst_edges_list, ax=ax,
                          edge_color='red', width=4, alpha=0.9)
    
    # 绘制节点
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color='lightblue', 
                          node_size=800, alpha=0.9, edgecolors='navy', linewidths=2)
    
    # 绘制节点标签（使用白色背景框）
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=11, font_weight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                    edgecolor='none', alpha=0.85))
    
    # 绘制MST边的权重标签（使用白色背景框）
    mst_edge_labels = {(e['from'], e['to']): e.get('weight', 0) for e in mst_edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=mst_edge_labels, ax=ax,
                                font_size=9, font_color='red',
                                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                         edgecolor='lightcoral', alpha=0.85))
    
    total_weight = sum(e.get('weight', 0) for e in mst_edges)
    plt.title(f"{algorithm_name} 结果 - 总权重: {total_weight}", 
             fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    plt.tight_layout()
    
    # 转换为base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return image_base64


def draw_maxflow_result(nodes, edges, flow_edges, source, sink, max_flow, algorithm_name="MaxFlow"):
    """
    绘制最大流结果
    
    Args:
        nodes: 节点列表
        edges: 所有边的列表（包含容量）
        flow_edges: 流量分配的边列表
        source: 源点
        sink: 汇点
        max_flow: 最大流值
        algorithm_name: 算法名称
    
    Returns:
        base64编码的PNG图片
    """
    setup_chinese_font()
    
    # 创建NetworkX有向图
    G = nx.DiGraph()
    
    # 添加节点
    for node in nodes:
        G.add_node(node)
    
    # 添加边
    for edge in edges:
        G.add_edge(edge['from'], edge['to'], 
                  capacity=edge.get('capacity', edge.get('weight', 0)))
    
    # 创建流量字典
    flow_dict = {}
    for flow_edge in flow_edges:
        flow_dict[(flow_edge['from'], flow_edge['to'])] = flow_edge['flow']
    
    # 生成布局
    pos = nx.spring_layout(G, seed=42, k=2.5, iterations=100)
    
    # 绘图
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # 绘制所有边（浅灰色）
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.2, width=1, edge_color='gray',
                          arrows=True, arrowsize=15, arrowstyle='->', 
                          connectionstyle='arc3,rad=0.1')
    
    # 绘制有流量的边（蓝色、粗细根据流量）
    flow_edges_list = [(e['from'], e['to']) for e in flow_edges if e['flow'] > 0]
    if flow_edges_list:
        max_flow_value = max(e['flow'] for e in flow_edges if e['flow'] > 0)
        widths = [4 * (flow_dict.get((e[0], e[1]), 0) / max_flow_value) + 2 
                 for e in flow_edges_list]
        nx.draw_networkx_edges(G, pos, edgelist=flow_edges_list, ax=ax,
                              edge_color='blue', width=widths, alpha=0.9,
                              arrows=True, arrowsize=25, arrowstyle='->',
                              connectionstyle='arc3,rad=0.1')
    
    # 绘制节点
    node_colors = []
    for node in G.nodes():
        if node == source:
            node_colors.append('lightgreen')
        elif node == sink:
            node_colors.append('lightcoral')
        else:
            node_colors.append('lightblue')
    
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, 
                          node_size=900, alpha=0.9, edgecolors='navy', linewidths=2)
    
    # 绘制节点标签（使用白色背景框）
    labels = {}
    for node in G.nodes():
        if node == source:
            labels[node] = f"{node}\n(源)"
        elif node == sink:
            labels[node] = f"{node}\n(汇)"
        else:
            labels[node] = str(node)
    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax, font_size=10, font_weight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                    edgecolor='none', alpha=0.85))
    
    # 绘制流量标签（使用白色背景框）
    flow_labels = {(e['from'], e['to']): f"{e['flow']}" 
                  for e in flow_edges if e['flow'] > 0}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=flow_labels, ax=ax,
                                font_size=9, font_color='blue',
                                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                         edgecolor='lightblue', alpha=0.85))
    
    plt.title(f"{algorithm_name} 结果 - 最大流: {max_flow}", 
             fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    plt.tight_layout()
    
    # 转换为base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return image_base64
