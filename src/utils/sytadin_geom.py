from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import re
from typing import Iterator
from pyproj import Transformer

# Lambert II Carto (NTF Paris) -> WGS84
_L2C_TO_WGS84 = Transformer.from_crs(27572, 4326, always_xy=True)

@dataclass(frozen=True)
class SegmentGeom:
    segment_id: str
    lat: float
    lon: float


def _parse_mid_line(line: str) -> list[str]:
    """
    MID: une ligne par objet, format CSV (souvent séparateur virgule, champs parfois quotés).
    """
    # On tente d'abord csv standard
    try:
        row = next(csv.reader([line], delimiter=",", quotechar='"', skipinitialspace=True))
        return [c.strip() for c in row]
    except Exception:
        # fallback basique
        return [c.strip().strip('"') for c in line.split(",")]


def _iter_mif_geoms(mif_path: Path) -> Iterator[list[tuple[float, float]]]:
    """
    Renvoie une liste de points (x,y) par feature, dans l'ordre du fichier MIF.
    Supporte Pline et Line (cas courant).
    """
    with mif_path.open("r", encoding="utf-8", errors="ignore") as f:
        in_data = False
        for raw in f:
            line = raw.strip()
            if not in_data:
                if line.lower() == "data":
                    in_data = True
                continue

            if not line:
                continue

            # Pline <n>
            m = re.match(r"(?i)^pline\s+(\d+)$", line)
            if m:
                n = int(m.group(1))
                pts: list[tuple[float, float]] = []
                for _ in range(n):
                    x_y = f.readline().strip().split()
                    if len(x_y) >= 2:
                        x = float(x_y[0].replace(",", "."))
                        y = float(x_y[1].replace(",", "."))
                        pts.append((x, y))
                if pts:
                    yield pts
                continue

            # Line x1 y1 x2 y2
            m = re.match(r"(?i)^line\s+(-?\d+(\.\d+)?)\s+(-?\d+(\.\d+)?)\s+(-?\d+(\.\d+)?)\s+(-?\d+(\.\d+)?)$", line)
            if m:
                parts = line.split()
                x1, y1, x2, y2 = map(float, parts[1:5])
                yield [(x1, y1), (x2, y2)]
                continue

            # Si d'autres types existent (Region, Point), on ignore pour l'instant
            # et on attend le prochain objet.
            continue


def _centroid_xy(points: list[tuple[float, float]]) -> tuple[float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def _guess_id_column(mid_rows: list[list[str]]) -> int:
    """
    Heuristique: la colonne segment_id est souvent un entier long.
    On cherche la colonne avec le plus de valeurs numériques "longues".
    """
    if not mid_rows:
        return 0
    nb_cols = max(len(r) for r in mid_rows)
    scores = [0] * nb_cols
    for r in mid_rows:
        for i in range(nb_cols):
            v = r[i] if i < len(r) else ""
            if v.isdigit() and len(v) >= 6:
                scores[i] += 1
    best = max(range(nb_cols), key=lambda i: scores[i])
    return best


def _to_wgs84(x: float, y: float) -> tuple[float, float]:
    """
    Convertit un point en WGS84 (lat, lon).
    - Si déjà en lon/lat: on le garde
    - Sinon: on suppose Lambert-93 (EPSG:2154) et on convertit
    """
    # Détection simple lon/lat
    if abs(x) <= 180 and abs(y) <= 90:
        lon, lat = x, y
        return lat, lon

    # Conversion Lambert-93 -> WGS84
    lon, lat = _L2C_TO_WGS84.transform(x, y)
    return float(lat), float(lon)



def build_segment_index_from_mif_mid(mif_path: Path, mid_path: Path) -> dict[str, SegmentGeom]:
    """
    Construit segment_id -> (lat, lon) à partir des fichiers Segment.mif / Segment.mid.
    On associe les features MIF aux lignes MID par ordre.
    """
    mid_lines = mid_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    mid_rows = [_parse_mid_line(l) for l in mid_lines if l.strip()]
    id_col = _guess_id_column(mid_rows)

    idx: dict[str, SegmentGeom] = {}

    geoms = list(_iter_mif_geoms(mif_path))
    n = min(len(geoms), len(mid_rows))

    for i in range(n):
        seg_id = mid_rows[i][id_col] if id_col < len(mid_rows[i]) else None
        if not seg_id:
            continue

        cx, cy = _centroid_xy(geoms[i])
        lat, lon = _to_wgs84(cx, cy)
        idx[str(seg_id)] = SegmentGeom(segment_id=str(seg_id), lat=float(lat), lon=float(lon))

    return idx
