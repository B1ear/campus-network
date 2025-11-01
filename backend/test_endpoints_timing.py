"""调用后端端点，校验时间字段"""
from app import app
from algorithms.generate_graph import generate_random_planar_network

with app.test_client() as c:
    G, pos, adj = generate_random_planar_network(n=20, seed=42)
    nodes = [{'id': i} for i in range(20)]
    edges = [{'from': u, 'to': v, 'capacity': G.edges[u, v]['capacity']} for u, v in G.edges()]

    payload = {'nodes': nodes, 'edges': edges, 'source': 0, 'sink': 19}

    r1 = c.post('/api/maxflow/edmonds-karp', json=payload)
    r2 = c.post('/api/maxflow/dinic', json=payload)

    ek = r1.get_json()
    dn = r2.get_json()

    print('EK status:', r1.status_code)
    print('EK fields:', {k: type(ek[k]).__name__ for k in ['time','visualization_time','total_time','max_flow']})
    print('EK times:', ek['time'], ek['visualization_time'], ek['total_time'])

    print('Dinic status:', r2.status_code)
    print('Dinic fields:', {k: type(dn[k]).__name__ for k in ['time','visualization_time','total_time','max_flow']})
    print('Dinic times:', dn['time'], dn['visualization_time'], dn['total_time'])
