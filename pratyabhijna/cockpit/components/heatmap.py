"""
Circuit Heatmap Component
Layer activation heatmap visualization
"""
import plotly.graph_objects as go
from dash import dcc

class CircuitHeatmap:
    """Circuit activation heatmap component"""
    
    @staticmethod
    def create(layer_activations=None):
        """Create layer activation heatmap"""
        fig = go.Figure()
        
        if layer_activations:
            layers = sorted(layer_activations.keys())
            if layers:
                max_len = max(len(layer_activations[l]) for l in layers)
                z_data = []
                
                for layer in layers:
                    acts = layer_activations[layer]
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
            # Empty state
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
        
        return dcc.Graph(figure=fig, style={'height': '400px'})
