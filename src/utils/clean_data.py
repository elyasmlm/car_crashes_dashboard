from __future__ import annotations

from pathlib import Path
import re

import numpy as np
import pandas as pd

# Répertoires du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLEAN_DIR = PROJECT_ROOT / "data" / "cleaned"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

# ==========================
#  Constantes de décodage
#  (d'après les docs ONISR)
# ==========================

MAP_LUM = {
    1: "Plein jour",
    2: "Crépuscule ou aube",
    3: "Nuit sans éclairage public",
    4: "Nuit avec éclairage non allumé",
    5: "Nuit avec éclairage allumé",
}

MAP_AGG = {
    1: "Hors agglomération",
    2: "En agglomération",
}

MAP_INT = {
    1: "Hors intersection",
    2: "Intersection en X",
    3: "Intersection en T",
    4: "Intersection en Y",
    5: "Intersection à plus de 4 branches",
    6: "Giratoire",
    7: "Place",
    8: "Passage à niveau",
    9: "Autre intersection",
}

MAP_ATM = {
    -1: "Non renseigné",
    1: "Normale",
    2: "Pluie légère",
    3: "Pluie forte",
    4: "Neige / grêle",
    5: "Brouillard / fumée",
    6: "Vent fort / tempête",
    7: "Temps éblouissant",
    8: "Temps couvert",
    9: "Autre",
}

MAP_COL = {
    -1: "Non renseigné",
    1: "Deux véhicules - frontale",
    2: "Deux véhicules - arrière",
    3: "Deux véhicules - côté",
    4: "Trois véhicules et plus - en chaîne",
    5: "Trois véhicules et plus - collisions multiples",
    6: "Autre collision",
    7: "Sans collision",
}


# ==========================
#  Fonctions utilitaires
# ==========================

def _find_year_dirs() -> list[int]:
    years: list[int] = []
    if RAW_DIR.exists():
        for p in RAW_DIR.iterdir():
            if p.is_dir() and re.fullmatch(r"\d{4}", p.name):
                years.append(int(p.name))
    return sorted(years)


def _read_csv_any(path: Path) -> pd.DataFrame:
    """Lecture robuste: teste plusieurs encodages et séparateurs."""
    encodings = ["utf-8", "latin-1", "cp1252"]
    seps = [";", ","]
    last_error: Exception | None = None

    for enc in encodings:
        for sep in seps:
            try:
                return pd.read_csv(path, sep=sep, engine="python", encoding=enc)
            except Exception as e:
                last_error = e
                continue

    print(f"[WARN] Problème de décodage pour {path.name}, fallback avec remplacement de caractères.")
    return pd.read_csv(
        path,
        sep=";",
        engine="python",
        encoding="utf-8",
        encoding_errors="replace",
    )


def _find_num_acc_column(df: pd.DataFrame) -> str | None:
    """Détecte la colonne Num_Acc, en tolérant des variantes de nom."""
    if "Num_Acc" in df.columns:
        return "Num_Acc"
    for c in df.columns:
        cleaned = re.sub(r"[^a-z0-9]", "", c.lower())
        if cleaned.startswith("numacc"):
            return c
    return None


def _ensure_num_acc(df: pd.DataFrame, strict: bool = True) -> pd.DataFrame:
    """
    Normalise la colonne Num_Acc :
    - trouve une colonne équivalente,
    - la renomme en Num_Acc,
    - force le type en string pour les merges.
    """
    col = _find_num_acc_column(df)
    if col is None:
        if strict:
            raise ValueError("Colonne Num_Acc introuvable")
        print("[WARN] Colonne Num_Acc introuvable dans un fichier secondaire, table ignorée.")
        return df

    if col != "Num_Acc":
        df = df.rename(columns={col: "Num_Acc"})

    df["Num_Acc"] = df["Num_Acc"].astype("string")
    return df

def _normalize_vehicules_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les noms de colonnes des fichiers VEHICULES
    (notamment pour 2021 où le schéma diffère).
    """
    rename_map = {}

    for c in df.columns:
        cl = c.lower().strip()

        if cl in ("id_accident"):
            rename_map[c] = "Num_Acc"

        elif cl in ("id_veh", "idveh", "veh_id"):
            rename_map[c] = "id_vehicule"

        elif cl in ("catv", "categorie_vehicule"):
            rename_map[c] = "catv"

    if rename_map:
        df = df.rename(columns=rename_map)

    return df



def _parse_hrmn(v) -> tuple[float, float]:
    """
    hrmn peut être:
    - HHMM (230 -> 02:30, 1845 -> 18:45)
    - HH:MM ("07:32")
    """
    if pd.isna(v):
        return (np.nan, np.nan)

    s = str(v).strip().strip('"').strip("'")
    if not s:
        return (np.nan, np.nan)

    if ":" in s:
        parts = s.split(":")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            try:
                hh = int(parts[0])
                mm = int(parts[1])
                if 0 <= hh <= 23 and 0 <= mm <= 59:
                    return (float(hh), float(mm))
            except Exception:
                return (np.nan, np.nan)
        return (np.nan, np.nan)

    if not s.isdigit():
        return (np.nan, np.nan)

    s = s.zfill(4)
    try:
        hh = int(s[:2])
        mm = int(s[2:])
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            return (float(hh), float(mm))
        return (np.nan, np.nan)
    except Exception:
        return (np.nan, np.nan)


def _norm_coords(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise lat/long :
    - anciens millésimes en 1e-5 degrés -> conversion,
    - 0 -> NaN.
    """
    for col in list(df.columns):
        if col.lower() == "lat" and col != "lat":
            df = df.rename(columns={col: "lat"})
        if col.lower() in ("long", "lon") and col != "long":
            df = df.rename(columns={col: "long"})

    def _to_float_fr(s: pd.Series) -> pd.Series:
        s = s.astype("string").str.strip()
        s = s.str.replace(" ", "", regex=False)
        s = s.str.replace(",", ".", regex=False)
        return pd.to_numeric(s, errors="coerce")

    for c in ("lat", "long"):
        if c in df.columns:
            df[c] = _to_float_fr(df[c])
            df.loc[df[c] == 0, c] = np.nan
            med = df[c].dropna().abs().median()
            if med > 1000:
                df[c] = df[c] / 100000.0

    return df.rename(columns={"lat": "latitude", "long": "longitude"})


def _decode_codes(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les colonnes lisibles à partir des codes (lum, agg, int, atm, col)."""
    if "lum" in df.columns:
        s = pd.to_numeric(df["lum"], errors="coerce")
        df["lum_code"] = s
        df["luminosite"] = s.map(MAP_LUM).where(s != -1, np.nan)

    if "agg" in df.columns:
        s = pd.to_numeric(df["agg"], errors="coerce")
        df["agg_code"] = s
        df["agglomeration"] = s.map(MAP_AGG).where(s != -1, np.nan)

    if "int" in df.columns:
        s = pd.to_numeric(df["int"], errors="coerce")
        df["int_code"] = s
        df["intersection"] = s.map(MAP_INT).where(s != -1, np.nan)

    if "atm" in df.columns:
        s = pd.to_numeric(df["atm"], errors="coerce")
        df["atm_code"] = s
        df["meteo"] = s.map(MAP_ATM).where(s != -1, np.nan)

    if "col" in df.columns:
        s = pd.to_numeric(df["col"], errors="coerce")
        df["col_code"] = s
        df["collision"] = s.map(MAP_COL).where(s != -1, np.nan)

    return df


def _build_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """Construit une colonne datetime à partir de an/mois/jour/hrmn."""
    if not {"an", "mois", "jour"}.issubset(df.columns):
        return df

    for c in ("an", "mois", "jour"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    if "hrmn" in df.columns:
        hhmm = df["hrmn"].apply(_parse_hrmn)
        df["heure"] = [h for h, _ in hhmm]
        df["minute"] = [m for _, m in hhmm]
    else:
        df["heure"] = np.nan
        df["minute"] = np.nan

    def _mk(row):
        try:
            h = int(row["heure"]) if not pd.isna(row["heure"]) else 0
            m = int(row["minute"]) if not pd.isna(row["minute"]) else 0
            return pd.Timestamp(int(row["an"]), int(row["mois"]), int(row["jour"]), h, m)
        except Exception:
            return pd.NaT

    df["datetime"] = df.apply(_mk, axis=1)
    return df


def _agg_usagers(usagers: pd.DataFrame) -> pd.DataFrame:
    """
    Agrège la table USAGERS par Num_Acc.
    - Si 'grav' existe : nb_usagers, nb_indemnes, nb_tues, nb_blesses_hosp, nb_blesses_legers.
    - Sinon : nb_usagers seul, le reste à NaN.
    """
    df = usagers.copy()
    df = _ensure_num_acc(df, strict=False)

    if "Num_Acc" not in df.columns:
        print("[WARN] USAGERS sans Num_Acc exploitable, agrégation impossible.")
        return pd.DataFrame(
            columns=[
                "Num_Acc",
                "nb_usagers",
                "nb_indemnes",
                "nb_tues",
                "nb_blesses_hosp",
                "nb_blesses_legers",
            ]
        )

    if "grav" not in df.columns:
        agg = (
            df.groupby("Num_Acc", as_index=False)
              .size()
              .rename(columns={"size": "nb_usagers"})
        )
        agg["nb_indemnes"] = np.nan
        agg["nb_tues"] = np.nan
        agg["nb_blesses_hosp"] = np.nan
        agg["nb_blesses_legers"] = np.nan
        return agg

    df["grav"] = pd.to_numeric(df["grav"], errors="coerce")
    agg = (
        df.assign(
            indemne=lambda x: (x["grav"] == 1).astype(int),
            tue=lambda x: (x["grav"] == 2).astype(int),
            bless_hosp=lambda x: (x["grav"] == 3).astype(int),
            bless_leger=lambda x: (x["grav"] == 4).astype(int),
        )
        .groupby("Num_Acc", as_index=False)
        .agg(
            nb_usagers=("grav", "count"),
            nb_indemnes=("indemne", "sum"),
            nb_tues=("tue", "sum"),
            nb_blesses_hosp=("bless_hosp", "sum"),
            nb_blesses_legers=("bless_leger", "sum"),
        )
    )
    return agg


def _agg_vehicules(vehicules: pd.DataFrame) -> pd.DataFrame:
    """Agrège la table VEHICULES par Num_Acc, en nb_vehicules."""
    df = vehicules.copy()
    df = _ensure_num_acc(df, strict=False)

    if "Num_Acc" not in df.columns:
        print("[WARN] VEHICULES sans Num_Acc exploitable, agrégation impossible.")
        return pd.DataFrame(columns=["Num_Acc", "nb_vehicules"])

    agg = (
        df.groupby("Num_Acc", as_index=False)
          .size()
          .rename(columns={"size": "nb_vehicules"})
    )
    return agg


def _find_csv(year_dir: Path, keyword: str) -> Path | None:
    """Premier CSV du dossier contenant keyword (ou une abréviation)."""
    kw = keyword.lower()
    for p in sorted(year_dir.glob("*.csv")):
        if kw in p.name.lower():
            return p

    aliases = {
        "caracteristiques": ("carac",),
        "vehicules": ("veh",),
        "usagers": ("usag",),
        "lieux": ("lieu",),
    }
    alias_list = aliases.get(keyword, ())
    for p in sorted(year_dir.glob("*.csv")):
        name = p.name.lower()
        if any(a in name for a in alias_list):
            return p

    return None


# ==========================
#  Pipeline par année
# ==========================

def build_year(year: int) -> Path | None:
    """Construit data/cleaned/accidents_<year>.csv à partir des fichiers bruts de l'année."""
    year_dir = RAW_DIR / str(year)
    if not year_dir.exists():
        print(f"[INFO] {year}: pas de dossier raw, ignoré.")
        return None

    # CARACTERISTIQUES (table centrale)
    f_car = _find_csv(year_dir, "caracteristiques")
    if not f_car:
        print(f"[WARN] {year}: fichier CARACTERISTIQUES introuvable, année ignorée.")
        return None
    car = _read_csv_any(f_car)
    car = _ensure_num_acc(car, strict=True)

    # LIEUX
    f_lieux = _find_csv(year_dir, "lieux")
    if f_lieux:
        lieux_raw = _read_csv_any(f_lieux)
        lieux = _ensure_num_acc(lieux_raw, strict=False)
        if "Num_Acc" in lieux.columns:
            car = car.merge(lieux, on="Num_Acc", how="left", suffixes=("", "_lieu"))
        else:
            print(f"[WARN] {year}: table LIEUX ignorée (pas de Num_Acc exploitable).")

    # USAGERS
    f_usag = _find_csv(year_dir, "usagers")
    if f_usag:
        usagers_raw = _read_csv_any(f_usag)
        usagers = _ensure_num_acc(usagers_raw, strict=False)
        if "Num_Acc" in usagers.columns:
            agg_u = _agg_usagers(usagers)
            car = car.merge(agg_u, on="Num_Acc", how="left")
        else:
            print(f"[WARN] {year}: table USAGERS ignorée (pas de Num_Acc exploitable).")
            car["nb_usagers"] = np.nan
            car["nb_indemnes"] = np.nan
            car["nb_tues"] = np.nan
            car["nb_blesses_hosp"] = np.nan
            car["nb_blesses_legers"] = np.nan
    else:
        car["nb_usagers"] = np.nan
        car["nb_indemnes"] = np.nan
        car["nb_tues"] = np.nan
        car["nb_blesses_hosp"] = np.nan
        car["nb_blesses_legers"] = np.nan

    # VEHICULES
    f_veh = _find_csv(year_dir, "vehicules")
    if f_veh:
        veh_raw = _read_csv_any(f_veh)
        veh_raw = _normalize_vehicules_columns(veh_raw)
        vehicules = _ensure_num_acc(veh_raw, strict=False)
        if "Num_Acc" in vehicules.columns:
            agg_v = _agg_vehicules(vehicules)
            car = car.merge(agg_v, on="Num_Acc", how="left")
        else:
            print(f"[WARN] {year}: table VEHICULES ignorée (pas de Num_Acc exploitable).")
            car["nb_vehicules"] = np.nan
    else:
        car["nb_vehicules"] = np.nan

    # Colonnes d'intérêt (CARACTERISTIQUES + LIEUX + agrégés)
    cols_car = [
        "Num_Acc", "an", "mois", "jour", "hrmn",
        "lum", "agg", "int", "atm", "col",
        "dep", "com", "adr", "lat", "long",
    ]
    cols_lieux = [
        "catr", "circ", "nbv", "vosp", "prof", "plan",
        "surf", "infra", "situ", "vma",
    ]
    cols_agg = [
        "nb_vehicules", "nb_usagers",
        "nb_indemnes", "nb_tues",
        "nb_blesses_hosp", "nb_blesses_legers",
    ]

    keep = [c for c in cols_car + cols_lieux + cols_agg if c in car.columns]
    df = car[keep].copy()

    # Datetime, coords, décodage
    df = _build_datetime(df)
    df = _norm_coords(df)
    df = _decode_codes(df)

    # Renommages explicites
    rename = {
        "Num_Acc": "accident_id",
        "an": "annee",
        "dep": "departement",
        "com": "commune_insee",
        "adr": "adresse",
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

    # Colonnes finales, dans un ordre pratique pour le dashboard
    final_cols = [
        "accident_id", "datetime", "annee", "mois", "jour", "heure", "minute",
        "departement", "commune_insee", "adresse",
        "latitude", "longitude",
        "luminosite", "agglomeration", "intersection", "meteo", "collision",
        "catr", "circ", "nbv", "vosp", "prof", "plan", "surf", "infra", "situ", "vma",
        "nb_vehicules", "nb_usagers", "nb_indemnes",
        "nb_tues", "nb_blesses_hosp", "nb_blesses_legers",
        "lum_code", "agg_code", "int_code", "atm_code", "col_code",
    ]
    df = df[[c for c in final_cols if c in df.columns]].copy()

    # Types numériques compacts
    for c in [
        "annee", "mois", "jour", "heure", "minute",
        "nb_vehicules", "nb_usagers", "nb_indemnes",
        "nb_tues", "nb_blesses_hosp", "nb_blesses_legers",
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce", downcast="integer")

    out_path = CLEAN_DIR / f"accidents_{year}.csv"
    df.to_csv(out_path, index=False)
    print(f"[OK] {out_path} ({len(df):,} lignes)")
    return out_path


def build_range(start_year: int, end_year: int) -> None:
    for y in range(start_year, end_year + 1):
        build_year(y)

def load_cleaned_range(start_year: int, end_year: int) -> pd.DataFrame:
    """
    Charge tous les fichiers cleaned accidents_<year>.csv
    entre start_year et end_year inclus, et retourne un seul DataFrame.
    """
    frames: list[pd.DataFrame] = []

    for y in range(start_year, end_year + 1):
        path = CLEAN_DIR / f"accidents_{y}.csv"
        if not path.exists():
            print(f"[WARN] Fichier nettoyé manquant pour {y}: {path}")
            continue
        df_y = pd.read_csv(path, low_memory=False)
        frames.append(df_y)

    if not frames:
        raise FileNotFoundError(
            f"Aucun fichier nettoyé trouvé entre {start_year} et {end_year} dans {CLEAN_DIR}"
        )

    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    years = _find_year_dirs()
    for y in years:
        build_year(y)
