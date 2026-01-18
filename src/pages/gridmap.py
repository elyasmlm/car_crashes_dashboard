from __future__ import annotations

import dash
import pandas as pd
from dash import Input, Output, dcc, html

from src.components.gridmap.accidents_gridmap import build_grid_map
from src.utils.data_loader import available_years, load_cleaned_range


dash.register_page(__name__, path="/gridmap", name="Carte (grille)")
YEARS = available_years()
DEFAULT_START = YEARS[0] if YEARS else 2005
DEFAULT_END = YEARS[-1] if YEARS else 2024


layout = html.Div(
    [
        html.H2("Carte des accidents (agrégation en grille)"),

        html.Div(
            [
                html.Label("Année (plage)"),
                dcc.RangeSlider(
                    id="grid-year-range",
                    min=DEFAULT_START,
                    max=DEFAULT_END,
                    step=1,
                    value=[max(DEFAULT_START, DEFAULT_END - 2), DEFAULT_END],
                    marks={y: str(y) for y in YEARS[::2]} if YEARS else None,
                    allowCross=False,
                ),
            ],
            style={"maxWidth": "800px", "marginBottom": "12px"},
        ),

        html.Div(
        [
            html.Div(
                [
                    html.Label("Département"),
                    dcc.Dropdown(
                        id="grid-dep",
                        options=[{"label": "Tous", "value": "ALL"}],
                        value=["ALL"],
                        multi=True,
                        clearable=False,
                        style={"maxWidth": "520px", "minWidth": "240px"},
                    ),
                ],
                style={"marginBottom": "12px"},
            ),
            html.Div(
                [
                    html.Label("Type de collision"),
                    dcc.Dropdown(
                        id="grid-collision",
                        options=[{"label": "Tous", "value": "ALL"}],
                        value=["ALL"],
                        multi=True,
                        clearable=False,
                        style={"maxWidth": "520px", "minWidth": "240px"},
                    ),
                ],
                style={"marginBottom": "12px"},
            ),

            html.Div(
                [
                    html.Label("Nombre de véhicules"),
                    dcc.Dropdown(
                        id="grid-nb-vehicules",
                        options=[
                            {"label": "Tous", "value": "ALL"},
                            {"label": "1", "value": "1"},
                            {"label": "2", "value": "2"},
                            {"label": "3", "value": "3"},
                            {"label": "4", "value": "4"},
                            {"label": "5", "value": "5"},
                            {"label": "6+", "value": "6+"},
                        ],
                        value="ALL",
                        clearable=False,
                        style={"maxWidth": "520px", "minWidth": "240px"},
                    ),
                ],
                style={"marginBottom": "12px"},
            ),

            html.Div(
                [
                    html.Label("Gravité"),
                    dcc.Checklist(
                        id="grid-severity",
                        options=[
                            {"label": "Accidents mortels", "value": "FATAL"},
                            {"label": "Accidents avec blessés", "value": "INJURED"},
                        ],
                        value=[],
                        style={"display": "flex", "gap": "16px"},
                    ),
                ],
                style={"marginBottom": "12px"},
            ),
        ],
            style={
                "display": "flex",
                "gap": "16px",
                "alignItems": "flex-end",
                "flexWrap": "wrap",
                "marginBottom": "16px",
            },
        ),


        html.Div(id="grid-map-container"),
    ],
    style={"padding": "12px"},
)


@dash.callback(
    Output("grid-dep", "options"),
    Input("grid-year-range", "value"),
)
def update_departements(year_range):
    start_y, end_y = map(int, year_range)
    df = load_cleaned_range(start_y, end_y)

    if "departement" not in df.columns:
        return [{"label": "Tous", "value": "ALL"}]

    deps = (
        df["departement"]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .unique()
        .tolist()
    )

    def _key(x):
        try:
            return int(x)
        except Exception:
            return 10_000

    deps = sorted(deps, key=_key)

    return [{"label": "Tous", "value": "ALL"}] + [{"label": d, "value": d} for d in deps]

@dash.callback(
    Output("grid-collision", "options"),
    Input("grid-year-range", "value"),
    Input("grid-dep", "value"),
)
def update_collision_options(year_range, dep_list):
    start_y, end_y = map(int, year_range)
    df = load_cleaned_range(start_y, end_y)

    dep_list = dep_list or ["ALL"]
    if "ALL" not in dep_list and "departement" in df.columns:
        deps = [str(d).strip() for d in dep_list]
        df = df[df["departement"].astype(str).str.strip().isin(deps)]

    if "collision" not in df.columns:
        return [{"label": "Tous", "value": "ALL"}]

    collisions = (
        df["collision"]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .unique()
        .tolist()
    )
    collisions = sorted(collisions)

    return [{"label": "Tous", "value": "ALL"}] + [{"label": c, "value": c} for c in collisions]

@dash.callback(
    Output("grid-map-container", "children"),
    Input("grid-year-range", "value"),
    Input("grid-dep", "value"),
    Input("grid-collision", "value"),
    Input("grid-nb-vehicules", "value"),
    Input("grid-severity", "value"),
)
def render_grid_map(year_range, dep_list, collision_list, nb_veh_choice, severity_flags):
    start_y, end_y = map(int, year_range)
    df = load_cleaned_range(start_y, end_y)

    # Departements (multi)
    dep_list = dep_list or ["ALL"]
    if "ALL" not in dep_list and "departement" in df.columns:
        deps = [str(d).strip() for d in dep_list]
        df = df[df["departement"].astype(str).str.strip().isin(deps)]

    # Collision (multi)
    collision_list = collision_list or ["ALL"]
    if "ALL" not in collision_list and "collision" in df.columns:
        cols = [str(c).strip() for c in collision_list]
        df = df[df["collision"].astype(str).str.strip().isin(cols)]

    # Nombre de vehicules: preferer nb_vehicules, sinon nbv
    veh_col = "nb_vehicules" if "nb_vehicules" in df.columns else ("nbv" if "nbv" in df.columns else None)
    if veh_col and nb_veh_choice and nb_veh_choice != "ALL":
        s = pd.to_numeric(df[veh_col], errors="coerce")

        if nb_veh_choice == "6+":
            df = df[s >= 6]
        else:
            target = int(nb_veh_choice)
            df = df[s == target]

    # Accidents mortels
    severity_flags = severity_flags or []
    if "FATAL" in severity_flags and "nb_tues" in df.columns:
        df = df[pd.to_numeric(df["nb_tues"], errors="coerce").fillna(0) > 0]

    # Accidents avec blesses (hosp ou legers)
    if "INJURED" in severity_flags:
        hosp = pd.to_numeric(df["nb_blesses_hosp"], errors="coerce").fillna(0) if "nb_blesses_hosp" in df.columns else 0
        leg = pd.to_numeric(df["nb_blesses_legers"], errors="coerce").fillna(0) if "nb_blesses_legers" in df.columns else 0
        df = df[(hosp + leg) > 0]

    # Zoom auto: si au moins un departement selectionne, zoom un peu
    zoom = 6.2 if "ALL" not in dep_list else 5.0

    return build_grid_map(df, precision=0.005, zoom=zoom)
