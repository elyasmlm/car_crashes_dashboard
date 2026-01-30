from __future__ import annotations

import pandas as pd
import plotly.express as px


def generate_seasons_pie(df: pd.DataFrame):
    """
    Camembert : répartition des accidents par saison (basé sur le mois).
    """
    if "mois" not in df.columns:
        raise KeyError("La colonne 'mois' n'existe pas dans les données nettoyées.")

    mois = pd.to_numeric(df["mois"], errors="coerce").dropna().astype(int)

    if mois.empty:
        return px.pie(title="Aucune donnée de mois entre 2005 et 2024.")

    season_map = {
        12: "Hiver", 1: "Hiver", 2: "Hiver",
        3: "Printemps", 4: "Printemps", 5: "Printemps",
        6: "Été", 7: "Été", 8: "Été",
        9: "Automne", 10: "Automne", 11: "Automne",
    }

    saisons = mois.map(season_map).dropna()
    counts = saisons.value_counts()

    order = ["Hiver", "Printemps", "Été", "Automne"]
    pie_df = pd.DataFrame({
        "Saison": [s for s in order if s in counts.index],
        "Nombre d'accidents": [int(counts[s]) for s in order if s in counts.index],
    })

    fig = px.pie(
        pie_df,
        names="Saison",
        values="Nombre d'accidents",
        title="Répartition des accidents par saison (2005-2024)",
    )
    fig.update_traces(textinfo="percent+label")
    return fig
