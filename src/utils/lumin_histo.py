# lumin_histo.py
from __future__ import annotations

from pathlib import Path
import os

import pandas as pd
import plotly.express as px
import plotly.io as pio

from .clean_data import load_cleaned_range


OUTPUT_PATH = Path(__file__).resolve().parents[2] / "static" / "img" / "luminosite.png"


def generate_luminosite_histogram(
    start_year: int = 2005,
    end_year: int = 2024,
) -> str:
    """
    Charge les données nettoyées et renvoie un fragment HTML Plotly (div + script)
    représentant l'histogramme de la luminosité. Le fragment inclut la
    référence à Plotly via le CDN pour être inséré directement dans une page.
    """
    df: pd.DataFrame = load_cleaned_range(start_year, end_year)

    if "luminosite" not in df.columns:
        raise KeyError("La colonne 'luminosite' n'existe pas dans les données nettoyées.")

    counts = df["luminosite"].dropna().value_counts().sort_index()
    if counts.empty:
        # Retourne un petit message HTML si pas de données
        return f"<p>Aucune donnée de luminosité entre {start_year} et {end_year}.</p>"

    fig = px.bar(
        x=counts.index.astype(str),
        y=counts.values,
        labels={"x": "Luminosité", "y": "Nombre d'accidents"},
        title=f"Répartition des accidents selon la luminosité ({start_year}-{end_year})",
    )
    fig.update_layout(xaxis_tickangle=30)

    # Génère un fragment HTML (div + script) utilisant le CDN Plotly
    html_fragment = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
    return html_fragment
