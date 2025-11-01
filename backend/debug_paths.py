"""
调试路径查找 - 查看网络中实际有多少条路径
"""
import sys
sys.path.insert(0, '.')

from algorithms.generate_graph import generate_random_planar_network
from algorithms.traffic import LoadBalancer
import networkx as nx

# 生成一个测试网络
print("生成测试网络...")
G, pos, adjacency = generate_random_planar_network(n=10, seed=42)

# 转换为API格式
nodes = [{'id': i, 'label': str(i)} for i in range(10)]
edges = []
for u, v in G.edges():
    edges.append({
        'from': int(u),
        'to': int(v),
        'cost': int(G.edges[u, v]['cost']),
        'capacity': int(G.edges[u, v]['capacity']),
        'weight': int(G.edges[u, v]['cost'])
    })

print(f"节点数: {len(nodes)}")
print(f"边数: {len(edges)}")
print()

# 测试几对节点
test_pairs = [(0, 5), (0, 9), (1, 7), (2, 8)]

for source, target in test_pairs:
    print("=" * 60)
    print(f"测试: 节点 {source} -> 节点 {target}")
    print("=" * 60)
    
    # 创建LoadBalancer
    balancer = LoadBalancer(nodes, edges)
    
    # 查找路径
    paths = balancer.find_k_shortest_paths(source, target, k=5)
    
    print(f"找到 {len(paths)} 条路径:")
    for i, path in enumerate(paths):
        # 计算路径长度
        length = 0
        capacity = float('inf')
        for j in range(len(path) - 1):
            u, v = path[j], path[j+1]
            if balancer.G.has_edge(u, v):
                length += balancer.G[u][v]['weight']
                capacity = min(capacity, balancer.G[u][v]['capacity'])
        
        print(f"  路径 {i+1}: {' -> '.join(map(str, path))}")
        print(f"    长度: {length}, 瓶颈容量: {capacity}")
    
    # 使用NetworkX内置方法验证
    try:
        # 将有向图转为无向图来计算所有简单路径
        G_undirected = balancer.G.to_undirected()
        all_simple_paths = list(nx.all_simple_paths(G_undirected, source, target, cutoff=10))
        print(f"\n  NetworkX找到的所有简单路径数: {len(all_simple_paths)} (截断长度10)")
        if len(all_simple_paths) > len(paths):
            print(f"  ⚠️ 我们的算法可以改进！还有 {len(all_simple_paths) - len(paths)} 条路径未找到")
    except Exception as e:
        print(f"  NetworkX验证失败: {e}")
    
    print()

print("✅ 调试完成")
