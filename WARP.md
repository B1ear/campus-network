# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## 💻 Project Overview

**校园网络算法可视化平台** (Campus Network Algorithm Visualization Platform)

A comprehensive full-stack web application for network algorithm visualization and interactive simulation.

**Key Features:**
- 🌲 Minimum Spanning Tree algorithms (Kruskal & Prim)
- 💧 Maximum Flow algorithms (Edmonds-Karp & Dinic)
- 🎮 Interactive traffic simulation with real-time visualization
- 🔐 AES-128 encryption/decryption implementation
- 🌐 Random planar network generation
- 📊 Real-time congestion detection and load balancing

**Tech Stack:**
- **Backend**: Flask 3.0 + NetworkX + NumPy + Matplotlib
- **Frontend**: Vue 3 Composition API + Vite 5.0
- **Visualization**: Server-side (Matplotlib) + Client-side (SVG)
- **State Management**: Vue provide/inject pattern

## Common Development Commands

### Backend (Flask)

```bash
# Start backend server
cd backend
python app.py
# Runs on http://localhost:5000

# Install dependencies
pip install -r requirements.txt

# Check backend health
curl http://localhost:5000/api/health
```

### Frontend (Vue 3 + Vite)

```bash
# Development server
cd frontend
npm run dev
# Runs on http://localhost:3000

# Install dependencies
npm install

# Production build
npm run build

# Preview production build
npm run preview
```

## Architecture Overview

### Backend Structure (`backend/`)

**Main Entry Point:**
- `app.py` - Flask application with CORS-enabled REST API endpoints

**Algorithm Modules (`algorithms/`):**
- `mst.py` - Minimum Spanning Tree (Kruskal & Prim algorithms)
- `maxflow.py` - Maximum Flow (Edmonds-Karp & Dinic algorithms)
- `aes_encrypt.py` - AES-128 encryption/decryption implementation
- `robustness.py` - Network robustness analysis (bridges, articulation points, metrics)
- `traffic.py` - Traffic monitoring and load balancing (multi-path, congestion avoidance)
- `generate_graph.py` - Random planar network generation with cost/capacity assignment
- `utils.py` - Visualization utilities (networkx + matplotlib -> base64 encoded images)

**Configuration (`config/`):**
- `network_config.py` - Network parameter management and default configurations

**Key Design Patterns:**
- All visualizations are returned as base64-encoded images (no file storage needed)
- Graph data uses standardized format: `nodes` array and `edges` array with `from`, `to`, `weight`/`capacity`
- Algorithms support both 0-indexed and 1-indexed node numbering

### Frontend Structure (`frontend/src/`)

**Main Components:**
- `App.vue` - Root component with tabbed navigation and global state management
- `NetworkConfigPanel.vue` - Configure and generate network topologies
- `MSTPanel.vue` - Minimum Spanning Tree visualization (Kruskal vs Prim)
- `MaxFlowPanel.vue` - Maximum Flow visualization (Edmonds-Karp vs Dinic)
- `AESPanel.vue` - AES encryption/decryption interface
- `NetworkSimulationPanel.vue` - Network analysis (robustness, load balancing)
- `InteractiveTrafficPanel.vue` - Interactive traffic flow simulation
- `EdgeEditor.vue` - Manual edge editing component
- `ImageViewer.vue` - Display base64 images from backend

**Global State Management:**
- Uses Vue 3's `provide`/`inject` for sharing network configuration across components
- `globalNetwork` - shared network topology state
- `setGlobalNetwork` - function to update global network

**API Integration (`api/backend.js`):**
- Centralized backend API calls with base URL configuration
- All endpoints return JSON with optional base64 visualization data

### Data Flow Architecture

1. **Network Configuration Workflow:**
   - User configures parameters in NetworkConfigPanel
   - Generates random planar network via `/api/network/generate`
   - Applies network as default config via `/api/network/apply`
   - Network stored in `config/network_config.py` DEFAULT_CONFIG

2. **Algorithm Execution Workflow:**
   - Component loads network from global state or default config
   - Sends graph data to backend API endpoint
   - Backend runs algorithm and generates visualization
   - Returns result with base64 image + metrics
   - Frontend displays results and image

3. **Simulation Workflow:**
   - NetworkSimulationPanel provides three analysis modes:
     - Robustness Analysis: identifies bridges/articulation points
     - Load Balancing: multi-path traffic distribution
     - Max Flow: quick flow calculation
   - Results include metrics and color-coded visualizations

## 🔌 API Endpoint Patterns

All endpoints follow REST conventions with JSON request/response.

### Network Configuration

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/api/network/generate` | POST | Generate random planar network | `{num_nodes, cost_range, capacity_range, seed}` | `{nodes, edges, topology_image, stats}` |
| `/api/network/config/default` | GET | Get default network config | - | `{num_nodes, cost_range, capacity_range, seed}` |
| `/api/graph/preview` | POST | Preview graph visualization | `{nodes, edges, label_mode}` | `{visualization, node_count, edge_count}` |

### Minimum Spanning Tree

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/api/mst/compare` | POST | Compare Kruskal vs Prim | `{nodes, edges}` | `{kruskal: {...}, prim: {...}, comparison}` |

Response includes: `mst_edges`, `total_weight`, `time_ms`, `visualization`, `steps[]`

### Maximum Flow

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/api/maxflow/edmonds-karp` | POST | Edmonds-Karp algorithm | `{nodes, edges, source, sink}` | `{max_flow, flow_edges, time, steps[], visualization}` |
| `/api/maxflow/dinic` | POST | Dinic algorithm | `{nodes, edges, source, sink}` | `{max_flow, flow_edges, time, steps[], visualization}` |

### Interactive Traffic Simulation

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/api/traffic/calculate-paths` | POST | Path calculation with flow allocation | `{nodes, edges, source, target, total_flow, strategy, num_paths, edge_usage}` | `{paths, path_allocations, total_capacity, actual_flow}` |

**Strategy Options:**
- `"single"` - Single shortest path
- `"balanced"` - Multi-path load balancing

**Edge Usage Format:** `[{from, to, flow}, ...]`

### Encryption

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/api/aes/encrypt` | POST | AES-128 encryption | `{plaintext, key}` | `{encrypted: "hex_string", format: "hex"}` |
| `/api/aes/decrypt` | POST | AES-128 decryption | `{encrypted: "hex_string", key}` | `{decrypted: "plaintext"}` |

### Utility

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/plots/<filename>` | GET | Retrieve generated plot image |
| `/api/health` | GET | Health check endpoint |

## Important Implementation Details

### Graph Data Format

All components use this standardized format:

```python
{
  "nodes": [
    {"id": 0, "label": "0"},
    {"id": 1, "label": "1"}
  ],
  "edges": [
    {"from": 0, "to": 1, "weight": 10, "capacity": 100}
  ]
}
```

### Visualization Generation

Backend uses matplotlib to generate graphs, converts to base64:

```python
# In utils.py
buffer = io.BytesIO()
plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
return f"data:image/png;base64,{image_base64}"
```

Frontend displays with `<img :src="visualization">` where `visualization` is the base64 string.

### Network Configuration Persistence

The system maintains a default network configuration in `backend/config/network_config.py`:
- User generates network in NetworkConfigPanel
- Clicks "应用到算法" to save as DEFAULT_CONFIG
- Other panels load this config when no network is explicitly provided
- Config includes nodes, edges, and generation parameters

### Algorithm Implementation Notes

**MST Algorithms:**
- Both Kruskal and Prim support 0-indexed and 1-indexed nodes (auto-detection)
- Union-Find (disjoint set) used in Kruskal
- Priority queue pattern in Prim

**Max Flow Algorithms:**
- Edmonds-Karp: BFS-based augmenting paths
- Dinic: level graph + DFS blocking flow
- Both use adjacency list representation

**Robustness Analysis:**
- Uses NetworkX's `bridges()` and `articulation_points()` functions
- Calculates composite robustness score from multiple metrics
- Visualizes critical nodes/edges in different colors

**Traffic Load Balancing:**
- Finds k-shortest paths using modified Yen's algorithm
- Three distribution strategies: equal, weighted by capacity, congestion-aware
- Real-time utilization monitoring with configurable threshold

## Common Development Tasks

When adding new algorithm features:
1. Implement algorithm in new/existing module under `backend/algorithms/`
2. Add visualization function in `utils.py` following base64 pattern
3. Create API endpoint in `app.py` following existing patterns
4. Create or update Vue component in `frontend/src/components/`
5. Add tab entry in `App.vue` if needed

When modifying network structure:
- Update both frontend data format and backend parsing
- Ensure backward compatibility with existing saved configs
- Update NetworkConfig class and DEFAULT_CONFIG

When debugging visualization issues:
- Check matplotlib backend and font configuration in utils.py
- Verify base64 encoding is complete (check for truncation)
- Use browser dev tools to inspect base64 image data
- Test image generation independently in Python REPL

## Windows-Specific Notes

This project is developed on Windows with PowerShell:
- Use `python` not `python3`
- Path separators automatically handled by os.path
- Virtual environment: `python -m venv venv` then `.\venv\Scripts\Activate.ps1`
- Use `Get-ChildItem` instead of `ls` in PowerShell scripts

## Dependencies

**Python packages** (see `backend/requirements.txt`):
- Flask 3.0.0 with flask-cors 4.0.0
- networkx 3.2.1 for graph algorithms
- matplotlib 3.8.2 for visualization
- numpy 1.26.2 for numerical operations

**NPM packages** (see `frontend/package.json`):
- vue 3.4.0
- vite 5.0.0
- @vitejs/plugin-vue 5.0.0

## ✨ Latest Features (2025-11-02)

### Interactive Traffic Simulation
- **Real-time SVG animation**: Particle-based flow visualization
- **Smart path selection**: Utilization-aware routing (80% threshold)
- **Congestion control**: Dynamic link avoidance based on capacity
- **Load balancing**: Single-path and balanced multi-path strategies
- **Shared edge handling**: Automatic flow adjustment for converging paths
- **Statistics dashboard**: Real-time throughput, utilization, congestion metrics

### Algorithm Performance Tracking
- **Separated timing**: Pure algorithm time vs visualization time
- **Step-by-step visualization**: Frame-by-frame algorithm execution
- **Comparison mode**: Side-by-side algorithm benchmarking

### Enhanced Visualization
- **Fixed layout**: Consistent node positioning across frames
- **High-resolution output**: 150 DPI PNG images
- **Base64 encoding**: No server-side file storage required
- **Chinese font support**: Automatic font fallback configuration

## 📄 Documentation

- [Technical Report](docs/技术报告.md) - Complete technical analysis
- [Update Summary](UPDATE_SUMMARY.md) - Recent feature updates
- [Backend README](backend/README.md) - API documentation
- [Frontend README](frontend/README.md) - Component guide
