"""
R_V Chart Component
Real-time line chart for R_V visualization
"""
import plotly.graph_objects as go
from dash import dcc

class RVChart:
    """R_V time series chart component"""
    
    @staticmethod
    def create(timestamps=None, rv_values=None, pr_early=None, pr_late=None):
        """Create R_V chart"""
        fig = go.Figure()
        
        if rv_values:
            x_vals = list(range(len(rv_values)))
            
            # R_V trace
            fig.add_trace(go.Scatter(
                x=x_vals,
                y=list(rv_values),
                mode='lines',
                name='R_V',
                line=dict(color='#00bc8c', width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 188, 140, 0.1)'
            ))
        
        if pr_early:
            fig.add_trace(go.Scatter(
                x=list(range(len(pr_early))),
                y=list(pr_early),
                mode='lines',
                name='PR_early',
                line=dict(color='#f39c12', width=1),
                opacity=0.7
            ))
        
        if pr_late:
            fig.add_trace(go.Scatter(
                x=list(range(len(pr_late))),
                y=list(pr_late),
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
            uirevision=True
        )
        
        return dcc.Graph(figure=fig, style={'height': '400px'})
