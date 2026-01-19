from __future__ import annotations

import pandas as pd
import plotly.express as px
from dash import dcc, html


def _prepare_points(df: pd.DataFrame) -> pd.DataFrame:
    needed = {"accident_id", "latitude", "longitude"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes: {missing}. Colonnes dispo: {list(df.columns)}")

    work = df.copy()
    work["latitude"] = pd.to_numeric(work["latitude"], errors="coerce")
    work["longitude"] = pd.to_numeric(work["longitude"], errors="coerce")
    work = work.dropna(subset=["latitude", "longitude"])

    # 1 point par accident (évite doublons)
    work = work.drop_duplicates(subset=["accident_id"])
    return work


def build_grid_map(df: pd.DataFrame, precision: float = 0.02, zoom: float = 5.0) -> html.Div:
    """
    Carte agrégée en grille:
    - precision: taille de cellule en degrés (ex 0.01 fin, 0.05 grossier)
    - zoom: niveau de zoom map
    """
    points = _prepare_points(df)

    if points.empty:
        return html.Div(
            [
                html.H3("Carte agrégée par grille"),
                html.Div("Aucun accident géolocalisé pour les filtres sélectionnés."),
            ]
        )

    # Binning (arrondi à une grille)
    points["lat_bin"] = (points["latitude"] / precision).round() * precision
    points["lon_bin"] = (points["longitude"] / precision).round() * precision

    agg = (
        points.groupby(["lat_bin", "lon_bin"], as_index=False)
        .size()
        .rename(columns={"size": "nb_accidents"})
    )

    center = {"lat": float(agg["lat_bin"].mean()), "lon": float(agg["lon_bin"].mean())}

    fig = px.scatter_map(
        agg,
        lat="lat_bin",
        lon="lon_bin",
        size="nb_accidents",
        size_max=40,
        zoom=zoom,
        center=center,
        map_style="open-street-map",
        height=650,
    )
    fig.update_traces(
        hovertemplate="Nombre d'accidents : %{marker.size}<extra></extra>",
    )

    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))

    return html.Div(
        [
            html.H3("Carte des accidents (agrégée par grille)"),
            html.P(
                f"Accidents géolocalisés: {len(points):,} | Cellules: {len(agg):,} | "
                f"Taille de grille: {precision}"
            ),
            dcc.Graph(figure=fig, config={"displayModeBar": True}),
        ]
    )
