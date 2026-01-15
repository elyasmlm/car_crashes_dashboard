from __future__ import annotations

import pandas as pd
import plotly.express as px

from src.utils.clean_data import load_cleaned_range


def generate_luminosite_histogram(
    start_year: int = 2005,
    end_year: int = 2024,
):
    """
    Retourne une figure Plotly pour être affichée dans Dash via dcc.Graph.
    """
    df: pd.DataFrame = load_cleaned_range(start_year, end_year)

    if "luminosite" not in df.columns:
        raise KeyError("La colonne 'luminosite' n'existe pas dans les données nettoyées.")

    counts = df["luminosite"].dropna().value_counts().sort_index()
    if counts.empty:
        return px.bar(title=f"Aucune donnée de luminosité entre {start_year} et {end_year}.")

    fig = px.bar(
        x=counts.index.astype(str),
        y=counts.values,
        labels={"x": "Luminosité", "y": "Nombre d'accidents"},
        title=f"Répartition des accidents selon la luminosité ({start_year}-{end_year})",
    )
    fig.update_layout(xaxis_tickangle=30)
    return fig
