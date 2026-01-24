import dash
from dash import html, dcc

from src.components.histogramme.lumin_histo import generate_luminosite_histogram
from src.components.histogramme.meteo_histo import generate_meteo_histogram
from src.components.histogramme.hours_histo import generate_hours_histogram
from src.components.histogramme.age_histo import generate_age_histogram
from src.components.camembert.saison_cam import generate_seasons_pie
from src.components.camembert.type_collision_cam import generate_collisions_pie
from src.components.camembert.consequences_cam import generate_gravite_usagers_pie
from src.components.camembert.type_vehicules_cam import generate_vehicle_types_pie
from src.utils.clean_data import load_cleaned_range

dash.register_page(__name__, path="/", name="Accueil")

def layout():
    datas = load_cleaned_range(2005, 2024)

    histo = generate_luminosite_histogram(datas)
    histo2 = generate_meteo_histogram(datas)
    histo3 = generate_hours_histogram(datas)
    histo4 = generate_age_histogram(datas)

    camembert1 = generate_seasons_pie(datas)
    camembert2 = generate_collisions_pie(datas)
    camembert3 = generate_gravite_usagers_pie(datas)
    camembert4 = generate_vehicle_types_pie(datas)

    return html.Div([
        html.H1("Dashboard des accidents"),
        html.Div(
            [
                html.H2("Histogramme de la luminosité"),
                dcc.Graph(figure=histo),
            ],
            style={"padding": "16px"}
        ),
        html.Div(
            [
                html.H2("Histogramme de la météo"),
                dcc.Graph(figure=histo2),
            ],
            style={"padding": "16px"}
        ),
        html.Div(
            [
                html.H2("Histogramme des heures de la journée"),
                dcc.Graph(figure=histo3),
            ],
            style={"padding": "16px"}
        ),
        html.Div(
            [
                html.H2("Histogramme des ages des conducteurs qui ont fait un accident"),
                dcc.Graph(figure=histo4),
            ],
            style={"padding": "16px"}
        ),
        html.Div(
            [
                html.H2("Camembert des accidents par saison"),
                dcc.Graph(figure=camembert1),
            ],
            style={"padding": "16px"}
        ),
        html.Div(
            [
                html.H2("Camembert des accidents par type de collision"),
                dcc.Graph(figure=camembert2),
            ],
            style={"padding": "16px"}
        ),
        html.Div(
            [
                html.H2("Camembert des conséquences des accidents"),
                dcc.Graph(figure=camembert3),
            ],
            style={"padding": "16px"}
        ),
        html.Div(
            [
                html.H2("Camembert des types de véhicules impliqués dans les accidents"),
                dcc.Graph(figure=camembert4),
            ],
            style={"padding": "16px"}
        )
    ])
