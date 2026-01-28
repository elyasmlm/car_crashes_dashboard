import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc

from src.components.histogramme.lumin_histo import generate_luminosite_histogram
from src.components.histogramme.meteo_histo import generate_meteo_histogram
from src.components.histogramme.hours_histo import generate_hours_histogram
from src.components.histogramme.age_histo import generate_age_histogram
from src.components.camembert.saison_cam import generate_seasons_pie
from src.components.camembert.type_collision_cam import generate_collisions_pie
from src.components.camembert.consequences_cam import generate_gravite_usagers_pie
from src.components.camembert.type_vehicules_cam import generate_vehicle_types_pie
from src.components.evolution.evolution_per_year import generate_accidents_per_year_line
from src.utils.clean_data import load_cleaned_range

dash.register_page(__name__, path="/", name="Accueil")

def layout():
    def build_carousel_structure(prefix):
        return dbc.Card(
            [
                dbc.CardHeader(
                    html.H5(id=f"{prefix}-title", className="m-0 text-center"),
                    className="bg-white border-bottom-0 pt-3"
                ),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Button(
                                        html.I(className="bi bi-chevron-left"),
                                        id=f"{prefix}-prev",
                                        n_clicks=0,
                                        className="nav-btn"
                                    ),
                                    width="auto",
                                    className="d-flex align-items-center"
                                ),
                                dbc.Col(
                                    dcc.Graph(
                                        id=f"{prefix}-graph",
                                        config={"displayModeBar": False},
                                        style={"height": "400px"}
                                    ),
                                    className="flex-grow-1"
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        html.I(className="bi bi-chevron-right"),
                                        id=f"{prefix}-next",
                                        n_clicks=0,
                                        className="nav-btn"
                                    ),
                                    width="auto",
                                    className="d-flex align-items-center"
                                ),

                            ],
                            className="align-items-center justify-content-center"
                        ),
                        dcc.Store(id=f"{prefix}-store"),
                    ]
                )
            ],
            className="shadow-sm mb-4 hover-lift"
        )

    return html.Div(
        [
            html.Div(
                [
                    html.H2("Tableau de bord", className="page-title text-center"),
                    html.Div("Analyse et tendances des accidents (2005–2024).", className="page-subtitle text-center"),
                ],
                className="mb-3"
            ),

            dcc.Loading(
                id="loading-home",
                type="circle",
                children=[
                    dbc.Row(
                        [
                            dbc.Col(build_carousel_structure("histo"), md=6, sm=12),
                            dbc.Col(build_carousel_structure("pie"), md=6, sm=12),
                        ]
                    ),
                    dbc.Row(
                        dbc.Col(
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Évolution temporelle", className="m-0")),
                                    dbc.CardBody(dcc.Graph(id="evolution-graph"))
                                ],
                                className="shadow-sm"
                            ),
                            width=12
                        )
                    )
                ]
            )
        ]
    )

@callback(
    Output("histo-store", "data"),
    Output("pie-store", "data"),
    Output("evolution-graph", "figure"),
    Input("loading-home", "loading_state"),
)
def load_all_graphs_data(_):
    datas = load_cleaned_range(2005, 2024)
    
    h1 = generate_luminosite_histogram(datas)
    h2 = generate_meteo_histogram(datas)
    h3 = generate_hours_histogram(datas)
    h4 = generate_age_histogram(datas)
    
    histo_data = {
        "index": 0,
        "items": [
            {"title": "Luminosité", "fig": h1},
            {"title": "Météo", "fig": h2},
            {"title": "Heure", "fig": h3},
            {"title": "Âge conducteur", "fig": h4},
        ]
    }

    c1 = generate_seasons_pie(datas)
    c2 = generate_collisions_pie(datas)
    c3 = generate_gravite_usagers_pie(datas)
    c4 = generate_vehicle_types_pie(datas)
    
    pie_data = {
        "index": 0,
        "items": [
            {"title": "Saisonnalité", "fig": c1},
            {"title": "Collisions", "fig": c2},
            {"title": "Gravité", "fig": c3},
            {"title": "Véhicules", "fig": c4},
        ]
    }

    evol_fig = generate_accidents_per_year_line(datas)
    return histo_data, pie_data, evol_fig

@callback(
    Output("histo-title", "children"),
    Output("histo-graph", "figure"),
    Output("histo-store", "data", allow_duplicate=True),
    Input("histo-prev", "n_clicks"),
    Input("histo-next", "n_clicks"),
    State("histo-store", "data"),
    prevent_initial_call=True
)
def navigate_histo(prev_clicks, next_clicks, store):
    if not store: return dash.no_update, dash.no_update, dash.no_update
    items = store["items"]
    idx = store["index"]
    ctx_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if ctx_id == "histo-prev":
        idx = (idx - 1) % len(items)
    else:
        idx = (idx + 1) % len(items)
    store["index"] = idx
    return items[idx]["title"], items[idx]["fig"], store

@callback(
    Output("pie-title", "children"),
    Output("pie-graph", "figure"),
    Output("pie-store", "data", allow_duplicate=True),
    Input("pie-prev", "n_clicks"),
    Input("pie-next", "n_clicks"),
    State("pie-store", "data"),
    prevent_initial_call=True
)
def navigate_pie(prev_clicks, next_clicks, store):
    if not store: return dash.no_update, dash.no_update, dash.no_update
    items = store["items"]
    idx = store["index"]
    ctx_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if ctx_id == "pie-prev":
        idx = (idx - 1) % len(items)
    else:
        idx = (idx + 1) % len(items)
    store["index"] = idx
    return items[idx]["title"], items[idx]["fig"], store

@callback(
    Output("histo-title", "children", allow_duplicate=True),
    Output("histo-graph", "figure", allow_duplicate=True),
    Output("pie-title", "children", allow_duplicate=True),
    Output("pie-graph", "figure", allow_duplicate=True),
    Input("histo-store", "data"),
    Input("pie-store", "data"),
    prevent_initial_call=True
)
def init_display_from_store(histo_store, pie_store):
    res = ["", {}, "", {}]
    if histo_store:
        h = histo_store["items"][histo_store["index"]]
        res[0], res[1] = h["title"], h["fig"]
    if pie_store:
        p = pie_store["items"][pie_store["index"]]
        res[2], res[3] = p["title"], p["fig"]
    return res[0], res[1], res[2], res[3]