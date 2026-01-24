from __future__ import annotations

import pandas as pd
import plotly.express as px

def generate_age_histogram(df: pd.DataFrame):
    """
    Retourne une figure Plotly pour être affichée dans Dash via dcc.Graph.
    """
    needed = {"age_cond_1", "age_cond_2"}
    missing = needed - set(df.columns)
    if missing:
        raise KeyError(f"Colonnes manquantes dans les données nettoyées: {sorted(missing)}")

    ages = pd.concat(
        [
            pd.to_numeric(df["age_cond_1"], errors="coerce"),
            pd.to_numeric(df["age_cond_2"], errors="coerce"),
        ],
        ignore_index=True,
    ).dropna()

    ages = ages[(ages > 17) & (ages <= 100)]
    if ages.empty:
        return px.histogram(title=f"Aucune donnée d'âge conducteur valide entre 2005 et 2024.")

    fig = px.histogram(
        ages,
        x=ages,
        nbins=100,
        labels={"x": "Âge du conducteur", "y": "Nombre d'accidents"},
        title=f"Répartition des âges des conducteurs (2005-2024)",
    )
    fig.update_layout(xaxis_tickangle=30)

    return fig