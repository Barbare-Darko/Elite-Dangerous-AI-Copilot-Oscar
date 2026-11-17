"""Module des clients d'API externes pour Elite Dangerous (EDSM et Spansh)."""

import math
import re
import requests

from modules.config_loader import (
    CMDR_NAME,
    EDSM_API_KEY,
    HEADERS_HTTP
)
from modules.input_engine import copier_presse_papiers
from modules.telemetry_ed import analyser_journaux_locaux, normaliser_texte

VAISSEAUX_GRAND_PAD = {
    "caspian explorer", "explorer_nx", "anaconda", "type-7 transporter", "type7",
    "orca", "beluga liner", "belugaliner", "imperial cutter", "cutter",
    "federal corvette", "corvette", "type-9 heavy", "type9",
    "type-10 defender", "type9_military", "imperial clipper", "empire_trader"
}

TRADUCTIONS_MARCHANDISES = {
    "or": "Gold", "argent": "Silver", "platine": "Platinum", "palladium": "Palladium",
    "iridium": "Iridium", "indium": "Indium", "osmium": "Osmium", "painite": "Painite",
    "tritium": "Tritium", "monazite": "Monazite", "musgravite": "Musgravite",
    "alexandrite": "Alexandrite", "benitoite": "Benitoite", "serendibite": "Serendibite",
    "grandidierite": "Grandidierite", "rhodplumsite": "Rhodplumsite",
    "diamants basse temperature": "Low Temperature Diamonds",
    "opales du vide": "Void Opals", "bertrandite": "Bertrandite",
    "gallite": "Gallite", "cobalt": "Cobalt", "titane": "Titanium",
    "beryllium": "Beryllium", "tantale": "Tantalum", "uranium": "Uranium",
    "superconducteurs": "Superconductors", "polymères": "Polymers",
    "dissipateurs thermiques": "Heat Sinks"
}


def interroger_edsm_position() -> dict:
    """Interroge EDSM pour connaître la position enregistrée du commandant."""
    url = "https://www.edsm.net/api-logs-v1/get-position"
    params = {"commanderName": CMDR_NAME, "apiKey": EDSM_API_KEY, "showCoordinates": 1}
    try:
        r = requests.get(url, params=params, headers=HEADERS_HTTP, timeout=6)
        return r.json()
    except Exception as e:
        return {"erreur": f"EDSM injoignable : {str(e)}"}


def interroger_edsm_systemes_proches(systeme_nom: str, rayon=30):
    """Trouve les systèmes stellaires voisins sur EDSM."""
    url = "https://www.edsm.net/api-v1/sphere-systems"
    params = {"systemName": systeme_nom, "radius": min(int(rayon), 50), "showInformation": 1}
    try:
        r = requests.get(url, params=params, headers=HEADERS_HTTP, timeout=8)
        data = r.json()
        if isinstance(data, list):
            voisins = [s for s in data if s.get("name", "").lower() != systeme_nom.lower()]
            if not voisins:
                return {"info": f"Aucun système voisin trouvé à moins de {rayon} années-lumière de {systeme_nom}."}
            voisins.sort(key=lambda x: x.get("distance", 999))
            return [
                {
                    "nom": s.get("name"),
                    "distance_annees_lumiere": s.get("distance"),
                    "allegeance": s.get("information", {}).get("allegiance", "Inconnue")
                }
                for s in voisins[:8]
            ]
        return data
    except Exception as e:
        return {"erreur": f"Erreur EDSM systèmes proches : {str(e)}"}


def interroger_edsm_stations(systeme_nom: str):
    """Liste les stations d'un système stellaire sur EDSM."""
    url = "https://www.edsm.net/api-system-v1/stations"
    params = {"systemName": systeme_nom}
    try:
        r = requests.get(url, params=params, headers=HEADERS_HTTP, timeout=8)
        data = r.json()
        if not data or not isinstance(data, dict):
            return {"info": f"Aucune donnée de station disponible sur EDSM pour {systeme_nom}."}
        stations = data.get("stations", [])
        if not stations:
            return {"info": f"Aucune station répertoriée dans {systeme_nom}."}
        resume = []
        for st in stations[:8]:
            resume.append({
                "nom": st.get("name"),
                "type": st.get("type"),
                "distance_secondes_lumiere": st.get("distanceToArrival"),
                "services": st.get("otherServices", [])
            })
        return {"systeme": systeme_nom, "stations": resume}
    except Exception as e:
        return {"erreur": f"Erreur EDSM stations : {str(e)}"}


def calculer_distance_systemes(systeme_depart: str, systeme_arrivee: str) -> dict:
    """Calcule la distance 3D euclidienne en AL entre deux systèmes via leurs coordonnées EDSM."""
    url = "https://www.edsm.net/api-v1/system"
    try:
        r1 = requests.get(url, params={"systemName": systeme_depart, "showCoordinates": 1}, headers=HEADERS_HTTP, timeout=6).json()
        r2 = requests.get(url, params={"systemName": systeme_arrivee, "showCoordinates": 1}, headers=HEADERS_HTTP, timeout=6).json()
        if "coords" not in r1:
            return {"erreur": f"Coordonnées introuvables sur EDSM pour le système {systeme_depart}."}
        if "coords" not in r2:
            return {"erreur": f"Coordonnées introuvables sur EDSM pour le système {systeme_arrivee}."}
        c1, c2 = r1["coords"], r2["coords"]
        dist = math.sqrt((c2["x"] - c1["x"])**2 + (c2["y"] - c1["y"])**2 + (c2["z"] - c1["z"])**2)
        return {
            "depart": systeme_depart,
            "arrivee": systeme_arrivee,
            "distance_annees_lumiere": round(dist, 2)
        }
    except Exception as e:
        return {"erreur": f"Erreur calcul distance EDSM : {str(e)}"}


def trouver_nom_station_par_market_id(systeme_nom: str, market_id: str) -> str:
    """Retrouve le nom d'une station distante via son MarketID sur EDSM."""
    if not systeme_nom or not market_id:
        return "Station distante inconnue"
    url = "https://edsm.net/api-system-v1/stations"
    try:
        r = requests.get(url, params={"systemName": systeme_nom}, headers=HEADERS_HTTP, timeout=6).json()
        for st in r.get("stations", []):
            if str(st.get("marketId")) == str(market_id):
                return st.get("name", "Station distante")
    except Exception:
        pass
    return f"Station distante (MarketID {market_id})"


def rechercher_marche_ou_equipement(objet: str, mode="vendre", critere_tri="prix", nb_sauts_max=None, rayon_al_max=None) -> dict:
    """Interroge Spansh pour trouver une station compatible (PAD) achetant/vendant un produit ou module."""
    etat = analyser_journaux_locaux(nb_journaux=1)
    systeme_actuel = etat.get("systeme", "Sol")
    v_actif = etat.get("vaisseau_actif", {})
    modele_actuel = normaliser_texte(v_actif.get("modele", ""))
    portee_saut = float(v_actif.get("portee_saut_max") or 30.0)

    besoin_grand_pad = any(g in modele_actuel for g in VAISSEAUX_GRAND_PAD)

    if rayon_al_max and float(rayon_al_max) > 0:
        rayon_al = float(rayon_al_max)
    elif nb_sauts_max and int(nb_sauts_max) > 0:
        rayon_al = round(int(nb_sauts_max) * portee_saut, 1)
    else:
        rayon_al = 100.0

    objet_norm = normaliser_texte(objet)
    nom_en = TRADUCTIONS_MARCHANDISES.get(objet_norm, objet.strip())

    filtres = {
        "distance": {"min": 0, "max": rayon_al}
    }
    if besoin_grand_pad:
        filtres["has_large_pad"] = {"value": True}

    mots_cles_modules = [
        "drive", "fsd", "scoop", "shield", "thruster", "plant", "distributor",
        "sensor", "refinery", "laser", "cannon", "railgun", "booster", "hangar",
        "limpet", "scanner", "hull", "reinforcement", "interdictor", "life support",
        "1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a",
        "1b", "2b", "3b", "4b", "5b", "6b", "7b", "8b",
        "1c", "2c", "3c", "4c", "5c", "6c", "7c", "8c",
        "1d", "2d", "3d", "4d", "5d", "6d", "7d", "8d"
    ]
    est_module = (mode == "module") or any(mot in objet_norm for mot in mots_cles_modules)

    if est_module:
        mode = "module"
        trad_modules = {
            "fsd": "Frame Shift Drive",
            "reacteur fsd": "Frame Shift Drive",
            "recuperateur de carburant": "Fuel Scoop",
            "fuel scoop": "Fuel Scoop",
            "bouclier": "Shield Generator",
            "generateur de bouclier": "Shield Generator",
            "propulseurs": "Thrusters",
            "generateur": "Power Plant",
            "distributeur": "Power Distributor",
            "capteurs": "Sensors",
            "raffinerie": "Refinery",
            "booster fsd": "Guardian Frame Shift Drive Booster"
        }
        match_tc = re.search(r'\b([1-8])\s*([a-e])\b', objet_norm)
        taille_mod = int(match_tc.group(1)) if match_tc else None
        classe_mod = match_tc.group(2).upper() if match_tc else None

        nom_module_propre = re.sub(r'\b[1-8]\s*[a-e]\b', '', objet_norm).strip()
        nom_spansh = trad_modules.get(nom_module_propre, nom_module_propre.title())
        if "frame shift drive" in objet_norm:
            nom_spansh = "Frame Shift Drive"

        filtre_mod = {"name": nom_spansh}
        if taille_mod:
            filtre_mod["class"] = taille_mod
        if classe_mod:
            filtre_mod["rating"] = classe_mod

        filtres["modules"] = [filtre_mod]
        tri_spansh = [{"distance": {"direction": "asc"}}]
    else:
        if mode == "vendre":
            filtres["market"] = [{"name": nom_en, "demand": {"comparison": ">", "value": 0}, "sell_price": {"comparison": ">", "value": 0}}]
            tri_spansh = [{"market_sell_price": [{"name": nom_en, "direction": "desc"}]}] if critere_tri == "prix" else [{"distance": {"direction": "asc"}}]
        else:
            filtres["market"] = [{"name": nom_en, "supply": {"comparison": ">", "value": 0}, "buy_price": {"comparison": ">", "value": 0}}]
            tri_spansh = [{"market_buy_price": [{"name": nom_en, "direction": "asc"}]}] if critere_tri == "prix" else [{"distance": {"direction": "asc"}}]

    payload = {
        "filters": filtres,
        "sort": tri_spansh,
        "size": 5,
        "page": 0,
        "reference_system": systeme_actuel
    }

    try:
        url = "https://spansh.co.uk/api/stations/search"
        r = requests.post(url, json=payload, headers=HEADERS_HTTP, timeout=10)
        data = r.json()
        resultats = [st for st in data.get("results", []) if "Carrier" not in st.get("type", "")]
        if not resultats:
            return {
                "info": f"Aucune station compatible (PAD {'Large' if besoin_grand_pad else 'Moyen/Large'}) trouvée en mode '{mode}' pour '{nom_en}' dans un rayon de {rayon_al} années-lumière autour de {systeme_actuel}."
            }

        stations_formatees = []
        for st in resultats[:3]:
            dist_al = round(st.get("distance", 0), 2)
            sauts_estimes = max(1, math.ceil(dist_al / portee_saut))
            info_st = {
                "station": st.get("name"),
                "systeme": st.get("system_name"),
                "distance_annees_lumiere": dist_al,
                "sauts_approximatifs": sauts_estimes,
                "distance_etoile_secondes_lumiere": round(st.get("distance_to_arrival", 0)),
                "pad_compatible": "Large" if st.get("has_large_pad") else "Moyen"
            }
            if not est_module:
                for m in st.get("market", []):
                    if m.get("commodity", "").lower() == nom_en.lower():
                        if mode == "vendre":
                            info_st["prix_par_tonne_credits"] = m.get("sell_price")
                            info_st["quantite_tonnes"] = m.get("demand")
                        else:
                            info_st["prix_par_tonne_credits"] = m.get("buy_price")
                            info_st["quantite_tonnes"] = m.get("supply")
                        break

            stations_formatees.append(info_st)

        meilleur_systeme = stations_formatees[0]["systeme"]
        copier_presse_papiers(meilleur_systeme)

        return {
            "recherche": nom_en,
            "mode": mode,
            "rayon_recherche_al": rayon_al,
            "portee_saut_vaisseau": portee_saut,
            "systeme_copie_presse_papiers": meilleur_systeme,
            "meilleures_stations": stations_formatees
        }
    except Exception as e:
        return {"erreur": f"Erreur lors de la recherche Spansh : {str(e)}"}
