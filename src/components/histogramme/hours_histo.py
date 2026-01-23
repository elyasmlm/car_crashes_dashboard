from __future__ import annotations

import pandas as pd
import plotly.express as px

from src.utils.clean_data import load_cleaned_range

def generate_hours_histogram(
    start_year: int = 2005,
    end_year: int = 2024,
):
    """
    Retourne une figure Plotly pour être affichée dans Dash via dcc.Graph.
    """
    df: pd.DataFrame = load_cleaned_range(start_year, end_year)

    if "heure" not in df.columns:
        raise KeyError("La colonne 'heure' n'existe pas dans les données nettoyées.")

    counts = df["heure"].dropna().value_counts().sort_index()
    if counts.empty:
        return px.bar(title=f"Aucune donnée d'heure entre {start_year} et {end_year}.")

    fig = px.bar(
        x=counts.index.astype(str),
        y=counts.values,
        labels={"x": "Heures de la journée", "y": "Nombre d'accidents"},
        title=f"Répartition des accidents selon l'heure ({start_year}-{end_year})",
    )
    fig.update_layout(xaxis_tickangle=30)
    return fig