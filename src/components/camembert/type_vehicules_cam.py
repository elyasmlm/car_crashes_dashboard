from __future__ import annotations

import pandas as pd
import plotly.express as px


def generate_vehicle_types_pie(df: pd.DataFrame):
    """
    Camembert : répartition des types de véhicules impliqués dans les accidents
    (via veh_type_cond_1 + veh_type_cond_2).
    Un accident avec 2 conducteurs compte 2 véhicules.
    """
    needed = {"veh_type_cond_1", "veh_type_cond_2"}
    missing = needed - set(df.columns)
    if missing:
        raise KeyError(f"Colonnes manquantes : {sorted(missing)}")

    v1 = df["veh_type_cond_1"].astype("string").str.strip().replace({"": pd.NA, "nan": pd.NA, "NaN": pd.NA})
    v2 = df["veh_type_cond_2"].astype("string").str.strip().replace({"": pd.NA, "nan": pd.NA, "NaN": pd.NA})

    veh_types = pd.concat([v1, v2], ignore_index=True).dropna().str.replace("_", " ", regex=False).str.capitalize()

    if veh_types.empty:
        return px.pie(title="Aucune donnée de type véhicule entre 2005 et 2024.")

    counts = veh_types.value_counts()
    pie_df = pd.DataFrame({
        "Type de véhicule": counts.index.tolist(),
        "Nombre": counts.values.tolist(),
    })

    fig = px.pie(
        pie_df,
        names="Type de véhicule",
        values="Nombre",
        title="Types de véhicules impliqués (2005-2024)",
    )
    fig.update_traces(textinfo="percent+label")
    return fig
