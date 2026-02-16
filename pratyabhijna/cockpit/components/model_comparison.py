"""
Model Comparison Component
Side-by-side model comparison charts
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dcc

class ModelComparison:
    """Model comparison component"""
    
    @staticmethod
    def create(models_data=None):
        """Create model comparison charts"""
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('R_V Comparison', 'PR_early Comparison', 'PR_late Comparison'),
            shared_yaxes=False
        )
        
        colors = {'model_a': '#e74c3c', 'model_b': '#3498db', 'model_c': '#2ecc71'}
        
        if models_data:
            for model_id, model_data in models_data.items():
                color = colors.get(model_id, '#fff')
                
                if model_data.get('rv'):
                    x_vals = list(range(len(model_data['rv'])))
                    fig.add_trace(
                        go.Scatter(
                            x=x_vals, 
                            y=model_data['rv'],
                            mode='lines',
                            name=f'{model_id}',
                            line=dict(color=color, width=2),
                            showlegend=True
                        ),
                        row=1, col=1
                    )
                
                if model_data.get('pr_early'):
                    fig.add_trace(
                        go.Scatter(
                            x=list(range(len(model_data['pr_early']))), 
                            y=model_data['pr_early'],
                            mode='lines',
                            name=f'{model_id}',
                            line=dict(color=color, width=2, dash='dash'),
                            showlegend=False
                        ),
                        row=1, col=2
                    )
                
                if model_data.get('pr_late'):
                    fig.add_trace(
                        go.Scatter(
                            x=list(range(len(model_data['pr_late']))), 
                            y=model_data['pr_late'],
                            mode='lines',
                            name=f'{model_id}',
                            line=dict(color=color, width=2, dash='dot'),
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
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            uirevision=True
        )
        
        return dcc.Graph(figure=fig, style={'height': '300px'})
