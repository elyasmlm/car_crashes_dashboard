import dash
from dash import html, dcc

from src.components.histogramme.lumin_histo import generate_luminosite_histogram

dash.register_page(__name__, path="/", name="Accueil")

def layout():
    fig = generate_luminosite_histogram(2005, 2023)
    return html.Div(
        [
            html.H1("Dashboard des accidents"),
            html.H2("Histogramme de la luminosité"),
            dcc.Graph(figure=fig),
        ],
        style={"padding": "16px"},
    )
