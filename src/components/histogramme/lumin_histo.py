from __future__ import annotations

import pandas as pd
import plotly.express as px


def generate_luminosite_histogram(df: pd.DataFrame):
    """
    Retourne une figure Plotly pour être affichée dans Dash via dcc.Graph.
    """
    if "luminosite" not in df.columns:
        raise KeyError("La colonne 'luminosite' n'existe pas dans les données nettoyées.")

    counts = df["luminosite"].dropna().value_counts().sort_index()
    if counts.empty:
        return px.bar(title="Aucune donnée de luminosité entre 2005 et 2024.")

    fig = px.bar(
        x=counts.index.astype(str),
        y=counts.values,
        labels={"x": "Luminosité", "y": "Nombre d'accidents"},
        title="Répartition des accidents selon la luminosité (2005-2024)",
    )
    fig.update_layout(xaxis_tickangle=30)
    return fig
