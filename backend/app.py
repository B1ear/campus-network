from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import base64
from algorithms.mst import kruskal_mst, prim_mst, parse_input
from algorithms.maxflow import main as maxflow_main
from algorithms.aes_encrypt import AES128
from algorithms.utils import validate_graph_data, save_plot

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


@app.route('/api/mst/kruskal', methods=['POST'])
def calculate_kruskal():
    """计算最小生成树 - Kruskal算法"""
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
        
        return jsonify({
            'algorithm': 'Kruskal',
            'mst_edges': mst_result,
            'total_weight': total_weight
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
        
        return jsonify({
            'algorithm': 'Prim',
            'mst_edges': mst_result,
            'total_weight': total_weight
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
        result = maxflow_main(edge_str, source=source, sink=sink, do_plot=False)
        
        return jsonify({
            'algorithm': 'Edmonds-Karp',
            'max_flow': result['ek']['maxflow'],
            'flow_edges': [{'from': u, 'to': v, 'flow': f} for (u, v), f in result['ek']['flows'].items() if f > 0],
            'source': source,
            'sink': sink,
            'time': result['ek']['time']
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
        result = maxflow_main(edge_str, source=source, sink=sink, do_plot=False)
        
        return jsonify({
            'algorithm': 'Dinic',
            'max_flow': result['dinic']['maxflow'],
            'flow_edges': [{'from': u, 'to': v, 'flow': f} for (u, v), f in result['dinic']['flows'].items() if f > 0],
            'source': source,
            'sink': sink,
            'time': result['dinic']['time']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/aes/encrypt', methods=['POST'])
def aes_encrypt():
    """AES加密"""
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
        encrypted = base64.b64encode(encrypted_bytes).decode('utf-8')
        
        return jsonify({
            'plaintext': plaintext,
            'encrypted': encrypted,
            'key_length': len(key)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/aes/decrypt', methods=['POST'])
def aes_decrypt():
    """AES解密"""
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
        encrypted_bytes = base64.b64decode(encrypted)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        decrypted = decrypted_bytes.decode('utf-8')
        
        return jsonify({
            'encrypted': encrypted,
            'decrypted': decrypted
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/plots/<filename>')
def get_plot(filename):
    """获取生成的图像文件"""
    return send_from_directory(app.config['PLOT_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
