from __future__ import annotations

import pandas as pd
import plotly.express as px


def generate_meteo_histogram(df: pd.DataFrame):
    """
    Retourne une figure Plotly pour être affichée dans Dash via dcc.Graph.
    """
    if "meteo" not in df.columns:
        raise KeyError("La colonne 'meteo' n'existe pas dans les données nettoyées.")

    counts = df["meteo"].dropna().value_counts().sort_index()
    if counts.empty:
        return px.bar(title="Aucune donnée de meteo entre 2005 et 2024.")

    fig = px.bar(
        x=counts.index.astype(str),
        y=counts.values,
        labels={"x": "Météo", "y": "Nombre d'accidents"},
        title="Répartition des accidents selon la météo (2005-2024)",
    )
    fig.update_layout(xaxis_tickangle=30)
    return fig