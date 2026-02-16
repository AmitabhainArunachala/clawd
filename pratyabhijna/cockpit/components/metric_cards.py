"""
Metric Cards Component
Displays key metrics in card format
"""
from dash import html
import dash_bootstrap_components as dbc

class MetricCards:
    """Metric cards component for displaying R_V, PR_early, PR_late"""
    
    @staticmethod
    def create(rv_value=0.0, pr_early=0.0, pr_late=0.0, samples=0):
        """Create metric cards layout"""
        return dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("R_V", className="card-title text-info"),
                        html.H2(f"{rv_value:.4f}", className="text-white"),
                        html.Small("Current Value", className="text-muted")
                    ])
                ], color="dark", outline=True)
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("PR_early", className="card-title text-warning"),
                        html.H2(f"{pr_early:.4f}", className="text-white"),
                        html.Small("Early Circuit Probability", className="text-muted")
                    ])
                ], color="dark", outline=True)
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("PR_late", className="card-title text-success"),
                        html.H2(f"{pr_late:.4f}", className="text-white"),
                        html.Small("Late Circuit Probability", className="text-muted")
                    ])
                ], color="dark", outline=True)
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Samples", className="card-title text-primary"),
                        html.H2(f"{samples}", className="text-white"),
                        html.Small("Total Data Points", className="text-muted")
                    ])
                ], color="dark", outline=True)
            ], width=3)
        ])
