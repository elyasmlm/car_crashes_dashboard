from __future__ import annotations

import pandas as pd
import plotly.express as px


def generate_hours_histogram(df: pd.DataFrame):
    """
    Retourne une figure Plotly pour être affichée dans Dash via dcc.Graph.
    """
    if "heure" not in df.columns:
        raise KeyError("La colonne 'heure' n'existe pas dans les données nettoyées.")

    counts = df["heure"].dropna().value_counts().sort_index()
    if counts.empty:
        return px.bar(title="Aucune donnée d'heure entre 2005 et 2024.")

    fig = px.bar(
        x=counts.index.astype(str),
        y=counts.values,
        labels={"x": "Heures de la journée", "y": "Nombre d'accidents"},
        title="Répartition des accidents selon l'heure (2005-2024)",
    )
    fig.update_layout(xaxis_tickangle=30)
    return fig