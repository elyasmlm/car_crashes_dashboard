# lumin_histo.py
from __future__ import annotations

from pathlib import Path
import os

import pandas as pd
import matplotlib.pyplot as plt

from clean_data import load_cleaned_range


OUTPUT_PATH = Path(__file__).resolve().parents[2] / "static" / "img" / "luminosite.png"


def generate_luminosite_histogram(
    start_year: int = 2005,
    end_year: int = 2024,
    output_path: Path | str = OUTPUT_PATH,
) -> str:
    # 1) Charger toutes les années déjà nettoyées
    df: pd.DataFrame = load_cleaned_range(start_year, end_year)

    # 2) On utilise la colonne "luminosite" créée dans le clean
    if "luminosite" not in df.columns:
        raise KeyError("La colonne 'luminosite' n'existe pas dans les données nettoyées.")

    lumi = df["luminosite"].dropna()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 3) Générer l'histogramme
    fig, ax = plt.subplots(figsize=(8, 5))
    (
        lumi.value_counts()
        .sort_index()
        .plot(kind="bar", ax=ax)
    )

    ax.set_title(f"Répartition des accidents selon la luminosité ({start_year}-{end_year})")
    ax.set_xlabel("Luminosité")
    ax.set_ylabel("Nombre d'accidents")
    plt.xticks(rotation=30, ha="right")

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)

    return str(output_path)
