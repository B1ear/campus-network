# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

校园网络算法可视化平台 (Campus Network Algorithm Visualization Platform) - A full-stack web application implementing network algorithms including Minimum Spanning Tree (MST), Maximum Flow, and AES encryption with interactive visualization and simulation capabilities.

**Tech Stack:**
- Backend: Flask 3.0 + NetworkX + NumPy + Matplotlib
- Frontend: Vue 3 + Vite

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

## API Endpoint Patterns

All endpoints follow REST conventions with JSON request/response:

**MST Endpoints:**
- `POST /api/mst/compare` - Compare Kruskal vs Prim
- `POST /api/mst/kruskal` - Kruskal only
- `POST /api/mst/prim` - Prim only

**Max Flow Endpoints:**
- `POST /api/maxflow/edmonds-karp` - Edmonds-Karp algorithm
- `POST /api/maxflow/dinic` - Dinic algorithm
- `POST /api/maxflow/compare` - Compare both algorithms

**Network Configuration:**
- `POST /api/network/generate` - Generate random network
- `POST /api/network/apply` - Save as default config
- `GET /api/network/config` - Get current config

**Simulation Endpoints:**
- `POST /api/robustness/analyze` - Robustness analysis
- `POST /api/robustness/simulate-edge-removal` - Edge removal simulation
- `POST /api/robustness/simulate-node-removal` - Node removal simulation
- `POST /api/traffic/simulate-load-balancing` - Load balancing simulation

**Other:**
- `POST /api/aes/encrypt` - AES encryption
- `POST /api/aes/decrypt` - AES decryption
- `POST /api/graph/preview` - Preview graph without algorithm
- `GET /api/health` - Health check

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

## Project Features

See `SIMULATION_FEATURES.md` for detailed documentation on:
- Network robustness analysis
- Multi-path load balancing
- Congestion avoidance
- Interactive traffic simulation
