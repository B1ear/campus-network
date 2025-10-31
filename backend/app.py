from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import base64
from algorithms.mst import kruskal_mst, prim_mst, parse_input
from algorithms.maxflow import main as maxflow_main
from algorithms.aes_encrypt import AES128
from algorithms.utils import validate_graph_data, save_plot, draw_mst_result, draw_maxflow_result, draw_original_graph
from algorithms.generate_graph import generate_random_planar_network, draw_campus_network
from config.network_config import NetworkConfig, DEFAULT_CONFIG
from algorithms.robustness import RobustnessAnalyzer, analyze_network_robustness
from algorithms.traffic import simulate_traffic_load_balancing
from algorithms.utils import draw_robustness_result, draw_traffic_load_balancing

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 静态文件路径
PLOT_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'plots')
os.makedirs(PLOT_FOLDER, exist_ok=True)
app.config['PLOT_FOLDER'] = PLOT_FOLDER


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': 'Backend is running'})


@app.route('/api/mst/compare', methods=['POST'])
def compare_mst():
    """比较两种最小生成树算法"""
    try:
        data = request.get_json()
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        
        if not validate_graph_data(nodes, edges):
            return jsonify({'error': 'Invalid graph data'}), 400
        
        # 转换为原有格式 [(u, v, w), ...]
        n = len(nodes) if nodes else max(max(e['from'], e['to']) for e in edges)
        edge_list = [(e['from'], e['to'], e['weight']) for e in edges]
        
        # 运行Kruskal算法并计时（只计时算法本身）
        import time
        start_time = time.perf_counter()
        kruskal_edges, kruskal_weight = kruskal_mst(n, edge_list, return_steps=False)
        kruskal_time = (time.perf_counter() - start_time) * 1000  # 转换为毫秒
        
        # 运行Prim算法并计时（只计时算法本身）
        start_time = time.perf_counter()
        prim_edges, prim_weight = prim_mst(n, edge_list, return_steps=False)
        prim_time = (time.perf_counter() - start_time) * 1000  # 转换为毫秒
        
        # 生成步骤（不计入算法运行时间）
        _, _, kruskal_steps = kruskal_mst(
            n, edge_list, return_steps=True, nodes_list=nodes, edges_list=edges
        )
        _, _, prim_steps = prim_mst(
            n, edge_list, return_steps=True, nodes_list=nodes, edges_list=edges
        )
        
        # 转换回前端格式
        kruskal_result = [{'from': u, 'to': v, 'weight': w} for u, v, w in kruskal_edges]
        prim_result = [{'from': u, 'to': v, 'weight': w} for u, v, w in prim_edges]
        
        # 生成可视化图片
        kruskal_viz = draw_mst_result(nodes, edges, kruskal_result, "Kruskal")
        prim_viz = draw_mst_result(nodes, edges, prim_result, "Prim")
        
        return jsonify({
            'kruskal': {
                'algorithm': 'Kruskal',
                'mst_edges': kruskal_result,
                'total_weight': kruskal_weight,
                'time_ms': round(kruskal_time, 4),
                'visualization': kruskal_viz,
                'steps': kruskal_steps
            },
            'prim': {
                'algorithm': 'Prim',
                'mst_edges': prim_result,
                'total_weight': prim_weight,
                'time_ms': round(prim_time, 4),
                'visualization': prim_viz,
                'steps': prim_steps
            },
            'comparison': {
                'weights_match': kruskal_weight == prim_weight,
                'faster_algorithm': 'Kruskal' if kruskal_time < prim_time else 'Prim',
                'time_difference_ms': abs(round(kruskal_time - prim_time, 4))
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/mst/kruskal', methods=['POST'])
def calculate_kruskal():
    """计算最小生成树 - Kruskal算法（保留兼容）"""
    try:
        data = request.get_json()
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        
        if not validate_graph_data(nodes, edges):
            return jsonify({'error': 'Invalid graph data'}), 400
        
        # 转换为原有格式 [(u, v, w), ...]
        n = len(nodes) if nodes else max(max(e['from'], e['to']) for e in edges)
        edge_list = [(e['from'], e['to'], e['weight']) for e in edges]
        
        mst_edges, total_weight = kruskal_mst(n, edge_list)
        
        # 转换回前端格式
        mst_result = [{'from': u, 'to': v, 'weight': w} for u, v, w in mst_edges]
        
        # 生成可视化图片
        visualization = draw_mst_result(nodes, edges, mst_result, "Kruskal")
        
        return jsonify({
            'algorithm': 'Kruskal',
            'mst_edges': mst_result,
            'total_weight': total_weight,
            'visualization': visualization
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/graph/preview', methods=['POST'])
def preview_graph():
    """绘制原始图（不包含算法结果）"""
    try:
        data = request.get_json()
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        
        if not validate_graph_data(nodes, edges):
            return jsonify({'error': 'Invalid graph data'}), 400
        
        # 绘制原始图
        visualization = draw_original_graph(nodes, edges)
        
        return jsonify({
            'visualization': visualization,
            'node_count': len(nodes),
            'edge_count': len(edges)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/mst/prim', methods=['POST'])
def calculate_prim():
    """计算最小生成树 - Prim算法"""
    try:
        data = request.get_json()
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        
        if not validate_graph_data(nodes, edges):
            return jsonify({'error': 'Invalid graph data'}), 400
        
        # 转换为原有格式
        n = len(nodes) if nodes else max(max(e['from'], e['to']) for e in edges)
        edge_list = [(e['from'], e['to'], e['weight']) for e in edges]
        
        mst_edges, total_weight = prim_mst(n, edge_list)
        
        # 转换回前端格式
        mst_result = [{'from': u, 'to': v, 'weight': w} for u, v, w in mst_edges]
        
        # 生成可视化图片
        visualization = draw_mst_result(nodes, edges, mst_result, "Prim")
        
        return jsonify({
            'algorithm': 'Prim',
            'mst_edges': mst_result,
            'total_weight': total_weight,
            'visualization': visualization
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/maxflow/edmonds-karp', methods=['POST'])
def calculate_edmonds_karp():
    """计算最大流 - Edmonds-Karp算法"""
    try:
        data = request.get_json()
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        source = data.get('source')
        sink = data.get('sink')
        
        if not all([nodes, edges, source is not None, sink is not None]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # 构建输入字符串格式
        edge_str = ''.join([f"({e['from']},{e['to']},{e.get('capacity', e.get('weight', 0))})" for e in edges])
        
        # 调用最大流算法
        result = maxflow_main(edge_str, source=source, sink=sink, do_plot=False, return_steps=True)
        
        flow_edges_list = [{'from': u, 'to': v, 'flow': f} for (u, v), f in result['ek']['flows'].items() if f > 0]
        
        # 生成可视化图片
        visualization = draw_maxflow_result(nodes, edges, flow_edges_list, source, sink, result['ek']['maxflow'], "Edmonds-Karp")
        
        return jsonify({
            'algorithm': 'Edmonds-Karp',
            'max_flow': result['ek']['maxflow'],
            'flow_edges': flow_edges_list,
            'source': source,
            'sink': sink,
            'time': result['ek']['time'],
            'visualization': visualization,
            'steps': result['ek'].get('steps', [])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/maxflow/dinic', methods=['POST'])
def calculate_dinic():
    """计算最大流 - Dinic算法"""
    try:
        data = request.get_json()
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        source = data.get('source')
        sink = data.get('sink')
        
        if not all([nodes, edges, source is not None, sink is not None]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # 构建输入字符串格式
        edge_str = ''.join([f"({e['from']},{e['to']},{e.get('capacity', e.get('weight', 0))})" for e in edges])
        
        # 调用最大流算法
        result = maxflow_main(edge_str, source=source, sink=sink, do_plot=False, return_steps=True)
        
        flow_edges_list = [{'from': u, 'to': v, 'flow': f} for (u, v), f in result['dinic']['flows'].items() if f > 0]
        
        # 生成可视化图片
        visualization = draw_maxflow_result(nodes, edges, flow_edges_list, source, sink, result['dinic']['maxflow'], "Dinic")
        
        return jsonify({
            'algorithm': 'Dinic',
            'max_flow': result['dinic']['maxflow'],
            'flow_edges': flow_edges_list,
            'source': source,
            'sink': sink,
            'time': result['dinic']['time'],
            'visualization': visualization,
            'steps': result['dinic'].get('steps', [])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/aes/encrypt', methods=['POST'])
def aes_encrypt():
    """AES加密，返回十六进制字符串"""
    try:
        data = request.get_json()
        plaintext = data.get('plaintext', '')
        key = data.get('key', '')
        
        if not plaintext or not key:
            return jsonify({'error': 'Plaintext and key are required'}), 400
        
        # 确保key是16字节
        key_bytes = key.encode('utf-8')
        if len(key_bytes) < 16:
            key_bytes = key_bytes + b'\x00' * (16 - len(key_bytes))
        elif len(key_bytes) > 16:
            key_bytes = key_bytes[:16]
        
        cipher = AES128(key_bytes)
        encrypted_bytes = cipher.encrypt(plaintext)
        # 直接返回十六进制字符串
        encrypted_hex = encrypted_bytes.hex()
        
        return jsonify({
            'plaintext': plaintext,
            'encrypted': encrypted_hex,
            'key_length': len(key),
            'format': 'hex'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/aes/decrypt', methods=['POST'])
def aes_decrypt():
    """AES解密，输入十六进制字符串"""
    try:
        data = request.get_json()
        encrypted = data.get('encrypted', '')
        key = data.get('key', '')
        
        if not encrypted or not key:
            return jsonify({'error': 'Encrypted text and key are required'}), 400
        
        # 确保key是16字节
        key_bytes = key.encode('utf-8')
        if len(key_bytes) < 16:
            key_bytes = key_bytes + b'\x00' * (16 - len(key_bytes))
        elif len(key_bytes) > 16:
            key_bytes = key_bytes[:16]
        
        cipher = AES128(key_bytes)
        # 从十六进制转换回字节
        try:
            encrypted_bytes = bytes.fromhex(encrypted)
        except ValueError:
            return jsonify({'error': '无效的十六进制字符串'}), 400
        
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        decrypted = decrypted_bytes.decode('utf-8')
        
        return jsonify({
            'encrypted': encrypted,
            'decrypted': decrypted,
            'format': 'hex'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/plots/<filename>')
def get_plot(filename):
    """获取生成的图像文件"""
    return send_from_directory(app.config['PLOT_FOLDER'], filename)


@app.route('/api/network/config/default', methods=['GET'])
def get_default_config():
    """获取默认网络配置"""
    return jsonify(DEFAULT_CONFIG)


@app.route('/api/network/generate', methods=['POST'])
def generate_network():
    """生成网络拓扑"""
    try:
        data = request.get_json() or {}
        
        # 创建配置对象
        config = NetworkConfig(**data) if data else NetworkConfig.default()
        
        # 生成网络
        G, pos, adjacency = generate_random_planar_network(
            n=config.num_nodes,
            cost_range=tuple(config.cost_range),
            cap_range=tuple(config.capacity_range),
            seed=config.seed
        )
        
        # 转换为前端格式
        nodes = [{'id': i, 'label': str(i)} for i in range(config.num_nodes)]
        edges = []
        for u, v in G.edges():
            edges.append({
                'from': int(u),
                'to': int(v),
                'cost': int(G.edges[u, v]['cost']),
                'capacity': int(G.edges[u, v]['capacity']),
                'weight': int(G.edges[u, v]['cost'])  # 用于MST
            })
        
        # 生成拓扑图
        topology_image = draw_campus_network(G, pos, return_base64=True)
        
        return jsonify({
            'config': config.to_dict(),
            'nodes': nodes,
            'edges': edges,
            'topology_image': topology_image,
            'stats': {
                'num_nodes': len(nodes),
                'num_edges': len(edges),
                'avg_cost': sum(e['cost'] for e in edges) / len(edges) if edges else 0,
                'avg_capacity': sum(e['capacity'] for e in edges) / len(edges) if edges else 0
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/robustness/analyze', methods=['POST'])
def analyze_robustness():
    """分析网络鲁棒性"""
    try:
        data = request.get_json()
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        
        if not validate_graph_data(nodes, edges):
            return jsonify({'error': 'Invalid graph data'}), 400
        
        # 执行鲁棒性分析
        result = analyze_network_robustness(nodes, edges)
        
        # 生成可视化
        visualization = draw_robustness_result(
            nodes, edges, 
            result['bridges'], 
            result['articulation_points']
        )
        
        return jsonify({
            **result,
            'visualization': visualization
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/robustness/simulate-edge-removal', methods=['POST'])
def simulate_edge_removal():
    """模拟边移除"""
    try:
        data = request.get_json()
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        edge_from = data.get('edge_from')
        edge_to = data.get('edge_to')
        
        if not validate_graph_data(nodes, edges):
            return jsonify({'error': 'Invalid graph data'}), 400
        
        if edge_from is None or edge_to is None:
            return jsonify({'error': 'Missing edge_from or edge_to'}), 400
        
        analyzer = RobustnessAnalyzer(nodes, edges)
        result = analyzer.simulate_edge_removal(edge_from, edge_to)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/robustness/simulate-node-removal', methods=['POST'])
def simulate_node_removal():
    """模拟节点移除"""
    try:
        data = request.get_json()
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        node_id = data.get('node_id')
        
        if not validate_graph_data(nodes, edges):
            return jsonify({'error': 'Invalid graph data'}), 400
        
        if node_id is None:
            return jsonify({'error': 'Missing node_id'}), 400
        
        analyzer = RobustnessAnalyzer(nodes, edges)
        result = analyzer.simulate_node_removal(node_id)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/robustness/redundant-paths', methods=['POST'])
def get_redundant_paths():
    """获取冗余路径"""
    try:
        data = request.get_json()
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        source = data.get('source')
        target = data.get('target')
        
        if not validate_graph_data(nodes, edges):
            return jsonify({'error': 'Invalid graph data'}), 400
        
        if source is None or target is None:
            return jsonify({'error': 'Missing source or target'}), 400
        
        analyzer = RobustnessAnalyzer(nodes, edges)
        result = analyzer.get_redundant_paths(source, target)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/traffic/simulate-load-balancing', methods=['POST'])
def simulate_load_balancing():
    """模拟流量负载均衡"""
    try:
        data = request.get_json()
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        source = data.get('source')
        target = data.get('target')
        total_flow = data.get('total_flow', 1000)
        enable_load_balancing = data.get('enable_load_balancing', True)
        enable_congestion_avoidance = data.get('enable_congestion_avoidance', True)
        num_paths = data.get('num_paths', 3)
        
        if not validate_graph_data(nodes, edges):
            return jsonify({'error': 'Invalid graph data'}), 400
        
        if source is None or target is None:
            return jsonify({'error': 'Missing source or target'}), 400
        
        # 执行负载均衡模拟
        result = simulate_traffic_load_balancing(
            nodes, edges, source, target, total_flow,
            enable_load_balancing=enable_load_balancing,
            enable_congestion_avoidance=enable_congestion_avoidance,
            num_paths=num_paths
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        # 生成可视化
        # 使用保留的元组格式edge_flows
        edge_flows_tuple = result.get('edge_flows_tuple', {})
        paths = result.get('paths', [])
        
        visualization = draw_traffic_load_balancing(
            nodes, edges, paths, edge_flows_tuple, source, target,
            strategy_name=result.get('strategy', '负载均衡')
        )
        
        # 从结果中移除内部使用的edge_flows_tuple
        if 'edge_flows_tuple' in result:
            del result['edge_flows_tuple']
        
        return jsonify({
            **result,
            'visualization': visualization
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
