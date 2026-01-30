from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

import requests

SYTADIN_EVENEMENTS_URL = "https://www.sytadin.fr/diffusion/xml/evenements.xml"


@dataclass(frozen=True)
class LiveAccident:
    id: str
    qualification: str | None
    localisation: str | None
    axe: str | None
    date_debut: str | None
    segment_id: str | None = None 


def _text(node: ET.Element | None) -> str | None:
    if node is None:
        return None
    t = (node.text or "").strip()
    return t or None


def fetch_sytadin_evenements_xml(timeout_s: int = 10) -> str:
    # Certains serveurs refusent les user agents vides
    headers = {"User-Agent": "car-crashes-dashboard/1.0"}
    r = requests.get(SYTADIN_EVENEMENTS_URL, headers=headers, timeout=timeout_s)
    r.raise_for_status()
    return r.text

def _localname(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag

def _first_text_by_path_local(root, path: list[str]) -> str | None:
    """
    Recherche le premier texte en suivant une suite de noms de tags (sans namespace).
    Exemple path = ["Localisation", "Segments", "Segment"]
    """
    cur = root
    for wanted in path:
        found = None
        for ch in list(cur):
            if _localname(ch.tag) == wanted:
                found = ch
                break
        if found is None:
            return None
        cur = found
    txt = cur.text.strip() if cur.text else None
    return txt or None

def _first_segment_id(ev) -> str | None:
    # Cherche le noeud Localisation puis Segments (namespace agnostic)
    loc = None
    for ch in list(ev):
        if _localname(ch.tag) == "Localisation":
            loc = ch
            break
    if loc is None:
        return None

    segs = None
    for ch in list(loc):
        if _localname(ch.tag) == "Segments":
            segs = ch
            break
    if segs is None:
        return None

    # Cherche le premier <Segment ...>
    for s in list(segs):
        if _localname(s.tag) != "Segment":
            continue

        # 1) cas "texte": <Segment>12017889</Segment>
        if s.text and s.text.strip():
            return s.text.strip()

        # 2) cas "attribut": <Segment ID_SEGMENT="12017889" />
        # On accepte plusieurs noms d’attributs possibles, selon les variantes
        for k in ("ID_SEGMENT", "IdSegment", "ID_SEG", "id", "ID"):
            v = s.get(k)
            if v and v.strip():
                return v.strip()

    return None


def parse_live_accidents(xml_text: str) -> list[LiveAccident]:
    root = ET.fromstring(xml_text)
    accidents: list[LiveAccident] = []

    # On cible uniquement les noeuds Evenement (namespace agnostic)
    evenements = [n for n in root.iter() if _localname(n.tag) == "Evenement"]

    for ev in evenements:
        # Type accident : souvent dans TypeEvenement/QualificationTypeEvenement
        qtype = _first_text_by_path_local(ev, ["TypeEvenement", "QualificationTypeEvenement"])
        if not qtype or "accident" not in qtype.lower():
            continue

        ev_id = ev.get("ID_EVT") or _first_text_by_path_local(ev, ["ID_EVT"]) or f"acc_{len(accidents)}"
        qualification = _first_text_by_path_local(ev, ["QualificationEvenement"]) or qtype
        date_debut = _first_text_by_path_local(ev, ["DateDebut"])

        # Axe (dans Localisation/SectionCourante/Axe)
        axe = _first_text_by_path_local(ev, ["Localisation", "SectionCourante", "Axe"])

        # Localisation : on peut afficher secteur si dispo
        localisation = _first_text_by_path_local(ev, ["Localisation", "SecteursLocalisations", "SecteurLocalisation"])

        seg_id = _first_segment_id(ev)

        a = LiveAccident(
            id=str(ev_id),
            qualification=qualification,
            localisation=localisation,
            axe=axe,
            date_debut=date_debut,
            segment_id=seg_id,
        )

        accidents.append(a)


    return accidents
