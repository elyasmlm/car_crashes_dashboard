from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_DIR = PROJECT_ROOT / "data" / "cleaned"


def available_years() -> list[int]:
    years: list[int] = []
    for p in CLEAN_DIR.glob("accidents_*.csv"):
        try:
            years.append(int(p.stem.split("_")[1]))
        except Exception:
            continue
    return sorted(set(years))


@lru_cache(maxsize=32)
def load_cleaned_year(year: int) -> pd.DataFrame:
    path = CLEAN_DIR / f"accidents_{year}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {path}")
    return pd.read_csv(path)


def load_cleaned_range(start_year: int, end_year: int) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for y in range(start_year, end_year + 1):
        try:
            frames.append(load_cleaned_year(y))
        except FileNotFoundError:
            continue
    if not frames:
        raise FileNotFoundError(f"Aucun fichier trouvé entre {start_year} et {end_year} dans {CLEAN_DIR}")
    return pd.concat(frames, ignore_index=True)
