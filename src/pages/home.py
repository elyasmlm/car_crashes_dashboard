import dash
from dash import html, dcc, callback, Output, Input, State

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

    histogrammes = [
        {"title": "Histogramme de la luminosité", "fig": histo},
        {"title": "Histogramme de la météo", "fig": histo2},
        {"title": "Histogramme des accidents par heure", "fig": histo3},
        {"title": "Histogramme de l'age des conducteurs'", "fig": histo4},
    ]

    camemberts = [
        {"title": "Camembert des accidents par saison", "fig": camembert1},
        {"title": "Camembert des accidents par type de collision", "fig": camembert2},
        {"title": "Camembert des conséquences des accidents", "fig": camembert3},
        {"title": "Camembert des types de véhicules impliqués", "fig": camembert4},
    ]

    return html.Div(
        [
            html.H1("Dashboard des accidents"),
            html.Div(
                [
                    html.H2(id="histo-title", children=histogrammes[0]["title"]),
                    html.Div(
                        [
                            html.Button("◀", id="histo-prev", n_clicks=0, style={"marginRight": "12px"}),
                            dcc.Graph(id="histo-graph", figure=histogrammes[0]["fig"], style={"flex": "1"}),
                            html.Button("▶", id="histo-next", n_clicks=0, style={"marginLeft": "12px"}),
                        ],
                        style={"display": "flex", "alignItems": "center"},
                    ),
                    dcc.Store(
                        id="histo-store",
                        data={
                            "index": 0,
                            "items": [
                                {"title": it["title"], "fig": it["fig"]} for it in histogrammes
                            ],
                        },
                    ),
                ],
                style={"padding": "16px"},
            ),
            html.Div(
                [
                    html.H2(id="pie-title", children=camemberts[0]["title"]),
                    html.Div(
                        [
                            html.Button("◀", id="pie-prev", n_clicks=0, style={"marginRight": "12px"}),
                            dcc.Graph(id="pie-graph", figure=camemberts[0]["fig"], style={"flex": "1"}),
                            html.Button("▶", id="pie-next", n_clicks=0, style={"marginLeft": "12px"}),
                        ],
                        style={"display": "flex", "alignItems": "center"},
                    ),
                    dcc.Store(
                        id="pie-store",
                        data={
                            "index": 0,
                            "items": [
                                {"title": it["title"], "fig": it["fig"]} for it in camemberts
                            ],
                        },
                    ),
                ],
                style={"padding": "16px"},
            ),
        ]
    )

@callback(
    Output("histo-store", "data"),
    Input("histo-prev", "n_clicks"),
    Input("histo-next", "n_clicks"),
    State("histo-store", "data"),
    prevent_initial_call=True,
)
def update_histo_index(prev_clicks, next_clicks, store):
    items = store["items"]
    idx = store["index"]

    trigger = dash.callback_context.triggered_id
    if trigger == "histo-prev":
        idx = (idx - 1) % len(items)
    elif trigger == "histo-next":
        idx = (idx + 1) % len(items)

    store["index"] = idx
    return store


@callback(
    Output("histo-title", "children"),
    Output("histo-graph", "figure"),
    Input("histo-store", "data"),
)
def render_histo(store):
    idx = store["index"]
    item = store["items"][idx]
    return item["title"], item["fig"]


@callback(
    Output("pie-store", "data"),
    Input("pie-prev", "n_clicks"),
    Input("pie-next", "n_clicks"),
    State("pie-store", "data"),
    prevent_initial_call=True,
)
def update_pie_index(prev_clicks, next_clicks, store):
    items = store["items"]
    idx = store["index"]

    trigger = dash.callback_context.triggered_id
    if trigger == "pie-prev":
        idx = (idx - 1) % len(items)
    elif trigger == "pie-next":
        idx = (idx + 1) % len(items)

    store["index"] = idx
    return store


@callback(
    Output("pie-title", "children"),
    Output("pie-graph", "figure"),
    Input("pie-store", "data"),
)
def render_pie(store):
    idx = store["index"]
    item = store["items"][idx]
    return item["title"], item["fig"]
