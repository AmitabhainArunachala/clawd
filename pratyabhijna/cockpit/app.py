"""
Live MI Cockpit - Real-time Mechanistic Interpretability Dashboard
Receives RVMetric JSON via WebSocket from Rust core
"""
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import websocket
import json
import threading
import time
from collections import deque
from datetime import datetime

# Import components
from components.metric_cards import MetricCards
from components.rv_chart import RVChart
from components.heatmap import CircuitHeatmap
from components.model_comparison import ModelComparison

# Global state for real-time data
data_buffer = {
    'timestamps': deque(maxlen=1000),
    'rv_values': deque(maxlen=1000),
    'pr_early': deque(maxlen=1000),
    'pr_late': deque(maxlen=1000),
    'layer_activations': {},
    'models': {
        'model_a': {'rv': [], 'pr_early': [], 'pr_late': []},
        'model_b': {'rv': [], 'pr_early': [], 'pr_late': []},
        'model_c': {'rv': [], 'pr_early': [], 'pr_late': []}
    },
    'connected': False,
    'last_update': None
}

# Mock data generator for testing
def generate_mock_data():
    """Generate mock RVMetric data for testing"""
    import random
    import math
    
    t = time.time()
    base_rv = 0.5 + 0.3 * math.sin(t * 0.5)
    
    return {
        'timestamp': t,
        'model_id': random.choice(['model_a', 'model_b', 'model_c']),
        'layer': random.randint(0, 11),
        'metrics': {
            'r_v': base_rv + random.gauss(0, 0.05),
            'pr_early': 0.3 + random.gauss(0, 0.1),
            'pr_late': 0.7 + random.gauss(0, 0.1),
            'confidence': 0.85 + random.gauss(0, 0.05)
        },
        'activations': [random.random() for _ in range(12)],
        'circuit_id': f'circuit_{random.randint(1, 5)}'
    }

# WebSocket client
def on_message(ws, message):
    """Handle incoming WebSocket message"""
    try:
        data = json.loads(message)
        update_data_buffer(data)
    except Exception as e:
        print(f"Error parsing message: {e}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")
    data_buffer['connected'] = False

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")
    data_buffer['connected'] = False

def on_open(ws):
    print("WebSocket connection opened")
    data_buffer['connected'] = True

def update_data_buffer(data):
    """Update global data buffer with new metrics"""
    global data_buffer
    
    timestamp = data.get('timestamp', time.time())
    model_id = data.get('model_id', 'unknown')
    metrics = data.get('metrics', {})
    
    data_buffer['timestamps'].append(timestamp)
    data_buffer['rv_values'].append(metrics.get('r_v', 0))
    data_buffer['pr_early'].append(metrics.get('pr_early', 0))
    data_buffer['pr_late'].append(metrics.get('pr_late', 0))
    
    # Update per-model data
    if model_id in data_buffer['models']:
        data_buffer['models'][model_id]['rv'].append(metrics.get('r_v', 0))
        data_buffer['models'][model_id]['pr_early'].append(metrics.get('pr_early', 0))
        data_buffer['models'][model_id]['pr_late'].append(metrics.get('pr_late', 0))
    
    # Update layer activations
    layer = data.get('layer', 0)
    activations = data.get('activations', [])
    if activations:
        data_buffer['layer_activations'][layer] = activations
    
    data_buffer['last_update'] = timestamp

def start_websocket_client(url="ws://localhost:8765"):
    """Start WebSocket client in background thread"""
    def run():
        ws = websocket.WebSocketApp(
            url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        ws.run_forever()
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread

def start_mock_data_stream():
    """Start mock data generator for testing"""
    def run():
        while True:
            data = generate_mock_data()
            update_data_buffer(data)
            time.sleep(0.5)  # 2Hz update rate
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="Live MI Cockpit"
)

# Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🧠 Live MI Cockpit", className="text-primary mt-3 mb-2"),
            html.P("Real-time Mechanistic Interpretability Dashboard", className="text-muted"),
            html.Div(id="connection-status", children=[
                html.Span("● ", className="text-success"),
                html.Span("Connected", className="text-success")
            ], className="mb-3")
        ])
    ]),
    
    # Metric Cards Row
    dbc.Row([
        dbc.Col([
            html.Div(id="metric-cards-container")
        ], width=12)
    ], className="mb-4"),
    
    # Main Charts Row
    dbc.Row([
        # R_V Time Series
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("R_V Over Tokens"),
                dbc.CardBody([
                    dcc.Graph(id="rv-chart", style={'height': '400px'}),
                    dcc.Interval(id="rv-interval", interval=500, n_intervals=0)
                ])
            ])
        ], width=8),
        
        # Circuit Heatmap
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Layer Activations"),
                dbc.CardBody([
                    dcc.Graph(id="heatmap-chart", style={'height': '400px'}),
                    dcc.Interval(id="heatmap-interval", interval=1000, n_intervals=0)
                ])
            ])
        ], width=4)
    ], className="mb-4"),
    
    # Model Comparison Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Model Comparison"),
                dbc.CardBody([
                    dcc.Graph(id="comparison-chart", style={'height': '300px'}),
                    dcc.Interval(id="comparison-interval", interval=1000, n_intervals=0)
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Raw Data Debug
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Latest Metrics (Debug)"),
                dbc.CardBody([
                    html.Pre(id="debug-output", children="Waiting for data...")
                ])
            ])
        ], width=12)
    ])
    
], fluid=True, style={'backgroundColor': '#1a1a1a', 'minHeight': '100vh'})

# Callbacks
@app.callback(
    Output("metric-cards-container", "children"),
    Input("rv-interval", "n_intervals")
)
def update_metric_cards(n):
    """Update metric cards with latest values"""
    if not data_buffer['rv_values']:
        return html.Div("No data yet...")
    
    latest_rv = list(data_buffer['rv_values'])[-1] if data_buffer['rv_values'] else 0
    latest_pr_early = list(data_buffer['pr_early'])[-1] if data_buffer['pr_early'] else 0
    latest_pr_late = list(data_buffer['pr_late'])[-1] if data_buffer['pr_late'] else 0
    
    cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("R_V", className="card-title text-info"),
                    html.H2(f"{latest_rv:.4f}", className="text-white"),
                    html.Small("Current Value", className="text-muted")
                ])
            ], color="dark", outline=True)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("PR_early", className="card-title text-warning"),
                    html.H2(f"{latest_pr_early:.4f}", className="text-white"),
                    html.Small("Early Circuit Probability", className="text-muted")
                ])
            ], color="dark", outline=True)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("PR_late", className="card-title text-success"),
                    html.H2(f"{latest_pr_late:.4f}", className="text-white"),
                    html.Small("Late Circuit Probability", className="text-muted")
                ])
            ], color="dark", outline=True)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Samples", className="card-title text-primary"),
                    html.H2(f"{len(data_buffer['rv_values'])}", className="text-white"),
                    html.Small("Total Data Points", className="text-muted")
                ])
            ], color="dark", outline=True)
        ], width=3)
    ])
    
    return cards

@app.callback(
    Output("rv-chart", "figure"),
    Input("rv-interval", "n_intervals")
)
def update_rv_chart(n):
    """Update R_V time series chart"""
    fig = go.Figure()
    
    if data_buffer['timestamps'] and data_buffer['rv_values']:
        timestamps = list(data_buffer['timestamps'])
        rv_values = list(data_buffer['rv_values'])
        pr_early = list(data_buffer['pr_early'])
        pr_late = list(data_buffer['pr_late'])
        
        # R_V trace
        fig.add_trace(go.Scatter(
            x=list(range(len(rv_values))),
            y=rv_values,
            mode='lines',
            name='R_V',
            line=dict(color='#00bc8c', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 188, 140, 0.1)'
        ))
        
        # PR_early trace
        fig.add_trace(go.Scatter(
            x=list(range(len(pr_early))),
            y=pr_early,
            mode='lines',
            name='PR_early',
            line=dict(color='#f39c12', width=1),
            opacity=0.7
        ))
        
        # PR_late trace
        fig.add_trace(go.Scatter(
            x=list(range(len(pr_late))),
            y=pr_late,
            mode='lines',
            name='PR_late',
            line=dict(color='#3498db', width=1),
            opacity=0.7
        ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis_title="Token Index",
        yaxis_title="Value",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        uirevision=True  # Preserve zoom/pan on update
    )
    
    return fig

@app.callback(
    Output("heatmap-chart", "figure"),
    Input("heatmap-interval", "n_intervals")
)
def update_heatmap(n):
    """Update layer activation heatmap"""
    fig = go.Figure()
    
    if data_buffer['layer_activations']:
        # Prepare heatmap data
        layers = sorted(data_buffer['layer_activations'].keys())
        if layers:
            max_len = max(len(data_buffer['layer_activations'][l]) for l in layers)
            z_data = []
            
            for layer in layers:
                acts = data_buffer['layer_activations'][layer]
                # Pad or truncate to consistent length
                if len(acts) < max_len:
                    acts = acts + [0] * (max_len - len(acts))
                z_data.append(acts[:max_len])
            
            fig.add_trace(go.Heatmap(
                z=z_data,
                x=list(range(max_len)),
                y=[f"Layer {l}" for l in layers],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Activation")
            ))
    else:
        # Empty heatmap
        fig.add_trace(go.Heatmap(
            z=[[0]],
            colorscale='Viridis'
        ))
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis_title="Neuron Index",
        yaxis_title="Layer",
        uirevision=True
    )
    
    return fig

@app.callback(
    Output("comparison-chart", "figure"),
    Input("comparison-interval", "n_intervals")
)
def update_comparison(n):
    """Update model comparison chart"""
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('R_V Comparison', 'PR_early Comparison', 'PR_late Comparison'),
        shared_yaxes=False
    )
    
    colors = {'model_a': '#e74c3c', 'model_b': '#3498db', 'model_c': '#2ecc71'}
    
    for model_id, model_data in data_buffer['models'].items():
        if model_data['rv']:
            x_vals = list(range(len(model_data['rv'])))
            
            # R_V subplot
            fig.add_trace(
                go.Scatter(
                    x=x_vals, y=model_data['rv'],
                    mode='lines',
                    name=f'{model_id} R_V',
                    line=dict(color=colors.get(model_id, '#fff'), width=2),
                    showlegend=False
                ),
                row=1, col=1
            )
            
            # PR_early subplot
            if model_data['pr_early']:
                fig.add_trace(
                    go.Scatter(
                        x=list(range(len(model_data['pr_early']))), 
                        y=model_data['pr_early'],
                        mode='lines',
                        name=f'{model_id} PR_early',
                        line=dict(color=colors.get(model_id, '#fff'), width=2, dash='dash'),
                        showlegend=False
                    ),
                    row=1, col=2
                )
            
            # PR_late subplot
            if model_data['pr_late']:
                fig.add_trace(
                    go.Scatter(
                        x=list(range(len(model_data['pr_late']))), 
                        y=model_data['pr_late'],
                        mode='lines',
                        name=f'{model_id} PR_late',
                        line=dict(color=colors.get(model_id, '#fff'), width=2, dash='dot'),
                        showlegend=False
                    ),
                    row=1, col=3
                )
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=40),
        height=300,
        uirevision=True
    )
    
    return fig

@app.callback(
    Output("debug-output", "children"),
    Input("rv-interval", "n_intervals")
)
def update_debug(n):
    """Update debug output with latest data"""
    debug_info = {
        'connected': data_buffer['connected'],
        'last_update': data_buffer['last_update'],
        'buffer_size': len(data_buffer['rv_values']),
        'latest_rv': list(data_buffer['rv_values'])[-1] if data_buffer['rv_values'] else None,
        'layer_count': len(data_buffer['layer_activations']),
        'models': {k: {'rv_count': len(v['rv'])} for k, v in data_buffer['models'].items()}
    }
    return json.dumps(debug_info, indent=2, default=str)

# Initialize
def init_app():
    """Initialize the app and start data sources"""
    # Start mock data stream (for testing without Rust core)
    start_mock_data_stream()
    
    # Optionally connect to real WebSocket server
    # start_websocket_client("ws://localhost:8765")
    
    print("🚀 Live MI Cockpit starting...")
    print("Dashboard available at: http://localhost:8050")

if __name__ == '__main__':
    init_app()
    app.run(debug=True, host='0.0.0.0', port=8050)
