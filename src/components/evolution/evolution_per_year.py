from __future__ import annotations

import pandas as pd
import plotly.express as px


def generate_accidents_per_year_line(df: pd.DataFrame):
    """
    Courbe : évolution du nombre d'accidents par année.
    """
    if "annee" in df.columns:
        years = pd.to_numeric(df["annee"], errors="coerce").dropna().astype(int)
        years = years.apply(lambda y: 2000 + y if y < 100 else y)
        counts = years.value_counts().sort_index()
    else:
        raise KeyError("La colonne 'annee' n'existe pas dans les données nettoyées.")

    if counts.empty:
        return px.line(title="Aucune donnée entre 2005 et 2024.")

    idx = pd.Index(range(2005, 2025), dtype=int)
    counts = counts.reindex(idx, fill_value=0)

    counts = counts[counts > 0]

    fig = px.line(
        x=counts.index,
        y=counts.values,
        labels={"x": "Année", "y": "Nombre d'accidents"},
        title="Évolution du nombre d'accidents par année (2005-2024)",
        markers=True,
    )
    fig.update_layout(xaxis_tickangle=30)
    return fig
