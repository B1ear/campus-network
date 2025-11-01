import requests
import json

url = 'http://localhost:5000/api/traffic/calculate-paths'

data = {
    'nodes': [{'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}],
    'edges': [
        {'from': 0, 'to': 1, 'weight': 10, 'capacity': 100},
        {'from': 1, 'to': 3, 'weight': 10, 'capacity': 100},
        {'from': 0, 'to': 2, 'weight': 15, 'capacity': 150},
        {'from': 2, 'to': 3, 'weight': 15, 'capacity': 150}
    ],
    'source': 0,
    'target': 3,
    'total_flow': 200,
    'strategy': 'balanced',
    'num_paths': 3
}

print("测试 API: /api/traffic/calculate-paths")
print("=" * 60)

try:
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应:")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"错误: {e}")
