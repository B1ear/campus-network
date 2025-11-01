"""验证 treat_as_undirected 展开为双向后，20节点图最大流是否非零"""
from app import app
from algorithms.generate_graph import generate_random_planar_network

with app.test_client() as c:
    G, pos, adj = generate_random_planar_network(n=20, seed=42)
    nodes = [{'id': int(i)} for i in range(20)]
    edges = [{'from': int(u), 'to': int(v), 'capacity': int(G.edges[u, v]['capacity'])} for u, v in G.edges()]
    payload = {
        'nodes': nodes,
        'edges': edges,
        'source': 0,
        'sink': 19,
        'treat_as_undirected': True,
    }
    r1 = c.post('/api/maxflow/edmonds-karp', json=payload)
    r2 = c.post('/api/maxflow/dinic', json=payload)
    ek = r1.get_json()
    dn = r2.get_json()
    print('EK status:', r1.status_code, 'flow=', ek.get('max_flow'))
    print('Dinic status:', r2.status_code, 'flow=', dn.get('max_flow'))
    print('EK times:', ek.get('time'), ek.get('visualization_time'), ek.get('total_time'))
    print('DN times:', dn.get('time'), dn.get('visualization_time'), dn.get('total_time'))
