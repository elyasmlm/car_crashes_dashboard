from __future__ import annotations
import re
from pathlib import Path
import requests

# params
DATASET_SLUG = "bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024"
YEAR_START, YEAR_END = 2005, 2024
TABLES = ("caracteristiques", "lieux", "usagers", "vehicules")
API_BASE = "https://www.data.gouv.fr/api/1"
OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

def get_dataset(slug: str) -> dict:
    """Récupère les métadonnées du dataset via l’API data.gouv.fr."""
    r = requests.get(f"{API_BASE}/datasets/{slug}/", timeout=60)
    r.raise_for_status()
    return r.json()

def pick_resources(dataset: dict):
    """Sélectionne les ressources CSV du dataset par année et par type de table."""
    out = {}
    years = set(range(YEAR_START, YEAR_END + 1))
    for res in dataset.get("resources", []) or []:
        fmt = (res.get("format") or "").lower()
        title = (res.get("title") or res.get("name") or "").lower()
        if fmt != "csv":
            continue
        # detecte l'année
        m = re.search(r"(20\d{2}|19\d{2})", title)
        year = int(m.group(1)) if m else None
        if year not in years:
            # si l'année n'est pas dans le titre -> url
            um = re.search(r"(20\d{2}|19\d{2})", (res.get("url") or ""))
            year = int(um.group(1)) if um else None
        if year not in years:
            continue
        # detecte la table (caracteristiques/lieux/usagers/vehicules)
        table = None
        for t in TABLES:
            if t in title:
                table = t
                break
        if not table:
            if re.search(r"\bcarac", title) or re.search(r"\bcarct", title): table = "caracteristiques"
            elif re.search(r"\blieu", title): table = "lieux"
            elif re.search(r"\busag", title): table = "usagers"
            elif re.search(r"\bveh", title): table = "vehicules"
        if not table:
            continue
        out.setdefault(year, {})[table] = res["id"]
    return out

def download_resource(resource_id: str, dataset_slug: str, dest: Path):
    """
    Télécharge via l’endpoint de redirection officiel :
    GET /api/1/datasets/r/{id}?dataset=<slug>
    → redirige vers l’URL fichier courante (évite les UUID périmés).
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"[SKIP] {dest.name} existe déjà")
        return
    with requests.get(f"{API_BASE}/datasets/r/{resource_id}", params={"dataset": dataset_slug},
                      stream=True, timeout=120, allow_redirects=True) as r:
        r.raise_for_status()
        tmp = dest.with_suffix(dest.suffix + ".part")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
        tmp.rename(dest)
    print(f"[OK] {dest}")

def main():
    print(f"[INFO] Dataset: {DATASET_SLUG}")
    dataset = get_dataset(DATASET_SLUG)
    selection = pick_resources(dataset)
    if not selection:
        print("[WARN] Aucune ressource trouvée (vérifie le slug ou la période).")
        return
    for year in sorted(selection):
        year_dir = OUT_DIR / str(year)
        for table in TABLES:
            res_id = selection.get(year, {}).get(table)
            if not res_id:
                print(f"[MISS] {year} — {table} introuvable")
                continue
            dest = year_dir / f"{table}_{year}.csv"
            try:
                download_resource(res_id, DATASET_SLUG, dest)
            except requests.HTTPError as e:
                print(f"[ERROR] {year}/{table}: {e}")

if __name__ == "__main__":
    main()
