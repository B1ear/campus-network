"""
测试JSON序列化修复
"""
import json
from algorithms.traffic import simulate_traffic_load_balancing

# 创建测试数据
nodes = [{'id': i, 'label': str(i)} for i in range(6)]
edges = [
    {'from': 0, 'to': 1, 'weight': 10, 'capacity': 100},
    {'from': 0, 'to': 2, 'weight': 15, 'capacity': 150},
    {'from': 1, 'to': 3, 'weight': 12, 'capacity': 120},
    {'from': 2, 'to': 3, 'weight': 10, 'capacity': 100},
    {'from': 1, 'to': 4, 'weight': 8, 'capacity': 80},
    {'from': 2, 'to': 4, 'weight': 20, 'capacity': 200},
    {'from': 3, 'to': 5, 'weight': 15, 'capacity': 150},
    {'from': 4, 'to': 5, 'weight': 10, 'capacity': 100},
]

print("测试负载均衡仿真...")
result = simulate_traffic_load_balancing(
    nodes, edges, 
    source=0, target=5, 
    total_flow=100,
    enable_load_balancing=True,
    enable_congestion_avoidance=True,
    num_paths=3
)

print("结果类型:", type(result))
print("\n尝试JSON序列化...")
try:
    json_str = json.dumps(result, indent=2)
    print("✅ JSON序列化成功!")
    print("\n主要键:", list(result.keys()))
    print("\nedge_flows类型:", type(result.get('edge_flows')))
    if result.get('edge_flows'):
        print("edge_flows示例键:", list(result['edge_flows'].keys())[:3])
except Exception as e:
    print("❌ JSON序列化失败:")
    print(f"错误: {e}")
    print(f"\n问题键:")
    for key, value in result.items():
        try:
            json.dumps({key: value})
        except Exception as ke:
            print(f"  - {key}: {type(value)} - {ke}")
