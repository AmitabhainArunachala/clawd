# Live MI Cockpit

Real-time Mechanistic Interpretability Dashboard for visualizing R_V metrics from transformer models.

## Quick Start

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Start the Dashboard

```bash
python3 app.py
```

The dashboard will be available at: http://localhost:8050

### 3. (Optional) Start Mock WebSocket Server

For testing without the Rust core:

```bash
pip3 install websockets
python3 mock_server.py
```

Then modify `app.py` to connect to the real WebSocket:
```python
# In init_app():
start_websocket_client("ws://localhost:8765")
```

## Features

- **Real-time R_V Visualization**: Line chart showing R_V, PR_early, and PR_late over tokens
- **Circuit Activation Heatmap**: Visualize layer-wise neuron activations
- **Model Comparison**: Side-by-side comparison of 2-3 models
- **Live Metrics Cards**: Current values for all key metrics
- **WebSocket Integration**: Receives RVMetric JSON from Rust core

## Architecture

```
cockpit/
├── app.py                    # Main Dash application
├── mock_server.py            # Mock WebSocket server for testing
├── requirements.txt          # Python dependencies
├── components/
│   ├── __init__.py
│   ├── metric_cards.py       # Metric display component
│   ├── rv_chart.py           # R_V time series chart
│   ├── heatmap.py            # Layer activation heatmap
│   └── model_comparison.py   # Multi-model comparison
```

## WebSocket Protocol

The dashboard expects JSON messages in this format:

```json
{
  "timestamp": 1708000000.0,
  "model_id": "model_a",
  "layer": 5,
  "metrics": {
    "r_v": 0.65,
    "pr_early": 0.32,
    "pr_late": 0.78,
    "confidence": 0.91
  },
  "activations": [0.1, 0.5, 0.9, ...],
  "circuit_id": "circuit_3",
  "token_idx": 42
}
```

## Configuration

- WebSocket URL: Edit `init_app()` in `app.py`
- Update interval: Change `interval` prop in `dcc.Interval` components (milliseconds)
- Buffer size: Modify `maxlen` in `deque` declarations

## License

MIT
