"""比较有/无步骤可视化的计时差异"""
from algorithms.generate_graph import generate_random_planar_network
from algorithms.maxflow import main as maxflow_main

# 生成图
n = 20
G, pos, adj = generate_random_planar_network(n=n, seed=42)

# 构造双向边字符串
parts = []
for u, v in G.edges():
    c = G.edges[u, v]["capacity"]
    parts.append(f"({u},{v},{c})")
    parts.append(f"({v},{u},{c})")
edge_str = ''.join(parts)

# 仅算法时间（不生成步骤）
res_plain = maxflow_main(edge_str, source=0, sink=n-1, do_plot=False, return_steps=False)

# 含步骤可视化（当前API端点使用的方式）
res_steps = maxflow_main(edge_str, source=0, sink=n-1, do_plot=False, return_steps=True)

print('不含步骤: EK={:.6f}s, Dinic={:.6f}s'.format(res_plain['ek']['time'], res_plain['dinic']['time']))
print('含步骤  : EK={:.6f}s, Dinic={:.6f}s'.format(res_steps['ek']['time'], res_steps['dinic']['time']))
print('maxflow 一致性: EK={}, Dinic={}'
      .format(res_plain['ek']['maxflow'] == res_steps['ek']['maxflow'],
              res_plain['dinic']['maxflow'] == res_steps['dinic']['maxflow']))
