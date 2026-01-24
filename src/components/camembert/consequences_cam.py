from __future__ import annotations

import pandas as pd
import plotly.express as px

def generate_gravite_usagers_pie(df: pd.DataFrame):
    """
    Camembert : répartition des USAGERS par gravité (sommes sur la période).
    """
    required = ["nb_indemnes", "nb_tues", "nb_blesses_hosp", "nb_blesses_legers"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Colonnes manquantes : {missing}")

    totals = {
        "Indemnes": int(pd.to_numeric(df["nb_indemnes"], errors="coerce").fillna(0).sum()),
        "Tués": int(pd.to_numeric(df["nb_tues"], errors="coerce").fillna(0).sum()),
        "Blessés graves (hospitalisés)": int(pd.to_numeric(df["nb_blesses_hosp"], errors="coerce").fillna(0).sum()),
        "Blessés légers": int(pd.to_numeric(df["nb_blesses_legers"], errors="coerce").fillna(0).sum()),
    }

    pie_df = pd.DataFrame({
        "Gravité": list(totals.keys()),
        "Nombre": list(totals.values()),
    })

    if pie_df["Nombre"].sum() == 0:
        return px.pie(title=f"Aucune donnée de gravité entre 2005 et 2024.")

    fig = px.pie(
        pie_df,
        names="Gravité",
        values="Nombre",
        title=f"Répartition des usagers par gravité (2005-2024)",
    )
    fig.update_traces(textinfo="percent+label")
    return fig
