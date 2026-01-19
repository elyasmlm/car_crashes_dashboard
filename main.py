from __future__ import annotations

import math
import urllib.parse
import requests
from pathlib import Path

from dash import (
    Dash,
    html,
    dcc,
    page_container,
    page_registry,
    Input,
    Output,
    ClientsideFunction,
)
from flask_caching import Cache

from src.utils.sytadin_live import fetch_sytadin_evenements_xml, parse_live_accidents
from src.utils.sytadin_geom import build_segment_index_from_mif_mid


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _badge_style() -> dict:
    return {
        "padding": "6px 10px",
        "border": "1px solid #ddd",
        "borderRadius": "10px",
        "background": "#fff",
        "whiteSpace": "nowrap",
    }


def create_app() -> Dash:
    app = Dash(
        __name__,
        use_pages=True,
        pages_folder="src/pages",
        suppress_callback_exceptions=True,
        title="Car Crashes Dashboard",
    )

    cache = Cache(
        app.server,
        config={
            "CACHE_TYPE": "FileSystemCache",
            "CACHE_DIR": "data/.cache",
            "CACHE_DEFAULT_TIMEOUT": 60,
        },
    )

    # --------------------------------------------------
    # Géométrie segments (fichiers locaux MIF/MID)
    # --------------------------------------------------
    SEG_MIF = Path("data/sytadin_geom/Segment.mif")
    SEG_MID = Path("data/sytadin_geom/Segment.mid")

    @cache.memoize(timeout=30 * 24 * 3600)  # 30 jours
    def _get_segment_index_cached() -> dict:
        if not SEG_MIF.exists() or not SEG_MID.exists():
            # Pas de géométrie dispo -> pas de distance possible
            return {}
        return build_segment_index_from_mif_mid(SEG_MIF, SEG_MID)

    # --------------------------------------------------
    # Reverse geocoding (adresse utilisateur)
    # --------------------------------------------------
    @cache.memoize(timeout=3600)  # 1h
    def _reverse_geocode_cached(lat: float, lon: float) -> str | None:
        url = "https://data.geopf.fr/geocodage/reverse?" + urllib.parse.urlencode(
            {"lat": f"{lat:.6f}", "lon": f"{lon:.6f}"}
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        feats = data.get("features") or []
        if not feats:
            return None
        props = feats[0].get("properties") or {}
        return props.get("label") or props.get("name")

    # --------------------------------------------------
    # Accidents live (cache court)
    # --------------------------------------------------
    @cache.memoize(timeout=60)
    def _get_live_accidents_cached():
        xml_text = fetch_sytadin_evenements_xml()
        return parse_live_accidents(xml_text)

    # --------------------------------------------------
    # Géoloc navigateur via assets/geo.js
    # --------------------------------------------------
    app.clientside_callback(
        ClientsideFunction(namespace="geo", function_name="getPosition"),
        Output("user-geo", "data"),
        Input("live-accidents-interval", "n_intervals"),
    )

    # --------------------------------------------------
    # Header live : accidents + adresse + distance
    # --------------------------------------------------
    @app.callback(
        Output("live-accidents-header", "children"),
        Input("live-accidents-interval", "n_intervals"),
        Input("user-geo", "data"),
    )
    def update_live_accidents_header(_, user_geo):
        def _render(text: str):
            return html.Div(html.Strong(text), style=_badge_style())

        try:
            accidents = _get_live_accidents_cached()
            n = len(accidents)
        except Exception as e:
            print("[LIVE] erreur _get_live_accidents_cached:", repr(e))
            return _render("Accidents en cours : indisponible")

        # Géoloc non dispo / refusée
        if not user_geo or not isinstance(user_geo, dict) or not user_geo.get("ok"):
            msg = user_geo.get("error") if isinstance(user_geo, dict) else None
            base = f"Accidents en temps réel : {n} | Votre position : Indisponible | Distance de l'accident le plus proche : Indisponible"
            if msg:
                base = f"{base} ({msg})"
            return _render(base)

        # Cast coords utilisateur
        try:
            user_lat = float(user_geo.get("lat"))
            user_lon = float(user_geo.get("lon"))
        except Exception:
            return _render(f"Accidents en temps réel : {n} | Votre position : Indisponible | Distance de l'accident le plus proche : Indisponible")

        # Votre position (best effort)
        try:
            user_address = _reverse_geocode_cached(user_lat, user_lon)
        except Exception:
            user_address = None
        addr_txt = user_address if user_address else "Indisponible"

        # Si aucun accident : distance indisponible (comme demandé)
        if n == 0:
            return _render(f"Accidents en temps réel : 0 | Votre position : {addr_txt} | Distance de l'accident le plus proche : Indisponible")

        # Distance de l'accident le plus proche: nécessite geom segments + segment_id sur les accidents
        seg_idx = _get_segment_index_cached()

        if not seg_idx:
            return _render(f"Accidents en temps réel : {n} | Votre position : {addr_txt} | Distance de l'accident le plus proche : Indisponible")

        dists = []
        for a in accidents:
            seg_id = a.segment_id
            if seg_id and seg_id in seg_idx:
                geom = seg_idx[seg_id]
                d = haversine_km(user_lat, user_lon, geom.lat, geom.lon)
                dists.append(d)

        if not dists:
            return _render(
                f"Accidents en temps réel : {n} | Votre position : {addr_txt} | Distance de l'accident le plus proche : Indisponible"
            )

        dmin = min(dists)
        return _render(f"Accidents en temps réel : {n} | Votre position : {addr_txt} | Distance de l'accident le plus proche : {dmin:.1f} km")

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------
    app.layout = html.Div(
        [
            html.Header(
                [
                    html.H2("Accidents de la route en France", style={"margin": 0}),
                    html.Nav(
                        [
                            dcc.Link(page["name"], href=page["path"], style={"marginRight": "12px"})
                            for page in page_registry.values()
                        ]
                    ),
                    dcc.Store(id="user-geo", storage_type="session"),
                    html.Div(
                        id="live-accidents-header",
                        style={
                            "marginLeft": "auto",
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "10px",
                        },
                    ),
                    dcc.Interval(id="live-accidents-interval", interval=60_000, n_intervals=0),
                ],
                style={
                    "padding": "12px 16px",
                    "borderBottom": "1px solid #ddd",
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "16px",
                },
            ),
            html.Main(page_container, style={"padding": "16px"}),
        ]
    )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
