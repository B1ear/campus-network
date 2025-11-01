"""对比EK/Dinic在纯算法与含步骤可视化两种模式下的耗时"""
from algorithms.generate_graph import generate_random_planar_network
from algorithms.maxflow import main as maxflow_main

# 生成一张20节点图，并将无向边转为双向有向边，确保有流
n = 20
G, pos, adj = generate_random_planar_network(n=n, seed=42)
parts = []
for u, v in G.edges():
    c = G.edges[u, v]["capacity"]
    parts.append(f"({u},{v},{c})")
    parts.append(f"({v},{u},{c})")
edge_str = ''.join(parts)

# 纯算法
plain = maxflow_main(edge_str, source=0, sink=n-1, do_plot=False, return_steps=False)
# 含步骤/可视化（与当前端点一致）
steps = maxflow_main(edge_str, source=0, sink=n-1, do_plot=False, return_steps=True)

print('EK plain/steps (s):', plain['ek']['time'], steps['ek']['time'])
print('Dinic plain/steps (s):', plain['dinic']['time'], steps['dinic']['time'])
print('Flows equal:', plain['ek']['maxflow'] == steps['ek']['maxflow'], plain['dinic']['maxflow'] == steps['dinic']['maxflow'])
