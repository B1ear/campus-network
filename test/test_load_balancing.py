"""
测试负载均衡路径计算功能
"""
import sys
import json

# 添加当前目录到路径
sys.path.insert(0, '.')

from algorithms.traffic import calculate_paths_with_allocation

# 创建简单的测试网络
nodes = [
    {'id': 0, 'label': '0'},
    {'id': 1, 'label': '1'},
    {'id': 2, 'label': '2'},
    {'id': 3, 'label': '3'},
]

edges = [
    {'from': 0, 'to': 1, 'weight': 10, 'capacity': 100},
    {'from': 1, 'to': 3, 'weight': 10, 'capacity': 100},
    {'from': 0, 'to': 2, 'weight': 15, 'capacity': 150},
    {'from': 2, 'to': 3, 'weight': 15, 'capacity': 150},
]

print("测试网络:")
print(f"节点: {[n['id'] for n in nodes]}")
print(f"边数: {len(edges)}")
print()

# 测试单路径
print("=" * 50)
print("测试 1: 单路径模式")
print("=" * 50)
result = calculate_paths_with_allocation(
    nodes, edges, 
    source=0, 
    target=3, 
    total_flow=80, 
    strategy='single', 
    num_paths=3
)

print(f"错误: {result.get('error', '无')}")
print(f"找到路径数: {len(result.get('paths', []))}")
if result.get('paths'):
    for i, path in enumerate(result['paths']):
        allocation = result['path_allocations'][i]
        print(f"  路径 {i+1}: {' -> '.join(map(str, path))}")
        print(f"    流量: {allocation['flow']:.1f}, 容量: {allocation['capacity']}, 利用率: {allocation['utilization']:.2%}")

print(f"总容量: {result.get('total_capacity', 0)}")
print(f"请求流量: {result.get('requested_flow', 0)}")
print(f"实际流量: {result.get('actual_flow', 0)}")
print(f"是否受限: {result.get('is_limited', False)}")
print()

# 测试负载均衡
print("=" * 50)
print("测试 2: 负载均衡模式")
print("=" * 50)
result = calculate_paths_with_allocation(
    nodes, edges, 
    source=0, 
    target=3, 
    total_flow=200, 
    strategy='balanced', 
    num_paths=3
)

print(f"错误: {result.get('error', '无')}")
print(f"找到路径数: {len(result.get('paths', []))}")
if result.get('paths'):
    for i, path in enumerate(result['paths']):
        allocation = result['path_allocations'][i]
        print(f"  路径 {i+1}: {' -> '.join(map(str, path))}")
        print(f"    流量: {allocation['flow']:.1f}, 容量: {allocation['capacity']}, 利用率: {allocation['utilization']:.2%}")

print(f"总容量: {result.get('total_capacity', 0)}")
print(f"请求流量: {result.get('requested_flow', 0)}")
print(f"实际流量: {result.get('actual_flow', 0)}")
print(f"是否受限: {result.get('is_limited', False)}")
print()

# 测试超容量情况
print("=" * 50)
print("测试 3: 超容量情况（请求流量 > 总容量）")
print("=" * 50)
result = calculate_paths_with_allocation(
    nodes, edges, 
    source=0, 
    target=3, 
    total_flow=500,  # 远超容量
    strategy='balanced', 
    num_paths=3
)

print(f"错误: {result.get('error', '无')}")
print(f"找到路径数: {len(result.get('paths', []))}")
if result.get('paths'):
    total_allocated = 0
    for i, path in enumerate(result['paths']):
        allocation = result['path_allocations'][i]
        total_allocated += allocation['flow']
        print(f"  路径 {i+1}: {' -> '.join(map(str, path))}")
        print(f"    流量: {allocation['flow']:.1f}, 容量: {allocation['capacity']}, 利用率: {allocation['utilization']:.2%}")
    print(f"  总分配流量: {total_allocated:.1f}")

print(f"总容量: {result.get('total_capacity', 0)}")
print(f"请求流量: {result.get('requested_flow', 0)}")
print(f"实际流量: {result.get('actual_flow', 0)}")
print(f"是否受限: {result.get('is_limited', False)}")
print()

print("✅ 所有测试完成！")
