from __future__ import annotations

import pandas as pd
import plotly.express as px

def generate_collisions_pie(df: pd.DataFrame):
    """
    Camembert : camembert sur les types de collisions.
    """
    if "collision" not in df.columns:
        raise KeyError("La colonne 'collision' n'existe pas dans les données nettoyées.")

    collision = (df["collision"].astype(str).str.strip().replace({"": pd.NA, "nan": pd.NA, "None": pd.NA}).dropna())

    if collision.empty:
        return px.pie(title=f"Aucune donnée de collision entre 2005 et 2024.")

    counts = collision.value_counts()

    pie_df = counts.reset_index()
    pie_df.columns = ["Collision", "Nombre d'accidents"]

    fig = px.pie(
        pie_df,
        names="Collision",
        values="Nombre d'accidents",
        title=f"Répartition des accidents par type de collision (2005-2024)",
    )
    fig.update_traces(textinfo="percent+label")
    return fig
