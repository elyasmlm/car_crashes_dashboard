import dash
from dash import html, dcc

from src.components.histogramme.lumin_histo import generate_luminosite_histogram
from src.components.histogramme.meteo_histo import generate_meteo_histogram
from src.components.histogramme.hours_histo import generate_hours_histogram

dash.register_page(__name__, path="/", name="Accueil")

def layout():
    fig = generate_luminosite_histogram(2005, 2024)
    fig2 = generate_meteo_histogram(2005, 2024)
    fig3 = generate_hours_histogram(2005, 2024)
    return html.Div([
        html.H1("Dashboard des accidents"),
        html.Div(
            [
                html.H2("Histogramme de la luminosité"),
                dcc.Graph(figure=fig),
            ],
            style={"padding": "16px"}
        ),
        html.Div(
            [
                html.H2("Histogramme de la météo"),
                dcc.Graph(figure=fig2),
            ],
            style={"padding": "16px"}
        ),
        html.Div(
            [
                html.H2("Histogramme des heures de la journée"),
                dcc.Graph(figure=fig3),
            ],
            style={"padding": "16px"}
        ),
    ])
