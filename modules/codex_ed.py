"""Module Codex local Elite Dangerous (base encyclopédique + historique personnel du Commandant).

Fournit :
1. Une base encyclopédique locale légère (data/codex_ed.json, ~50–250 Ko) regroupant :
   - Les 15 genres et ~75 espèces d'exobiologie Odyssey (apparence visuelle, habitat,
     valeur exacte Vista Genomics en crédits, distance minimale entre prélèvements).
   - Les grands types géologiques reliés au volcanisme planétaire.
   - Les nébuleuses, amas et POIs galactiques (synchronisés automatiquement tous les
     30 jours en arrière-plan depuis le Galactic Mapping Project d'EDSM).
2. Un index personnel du Commandant (data/codex_cmdr.json, ignoré par Git) construit
   en lecture seule à partir des fichiers Journal.*.log locaux (CodexEntry + ScanOrganic)
   pour indiquer à Oscar si le Commandant a déjà rencontré une espèce/géologie ou s'il
   s'agit d'une première personnelle (et si la planète est vierge ou déjà visitée).
"""

from __future__ import annotations

import glob
import json
import math
import os
import re
import threading
import time
import unicodedata

import requests

from modules.config_loader import (
    DOSSIER_JOURNAUX_ED,
    FICHIER_CODEX_CMDR,
    FICHIER_CODEX_ED,
    FICHIER_FLOTTE,
    HEADERS_HTTP,
    NAVIGATION_CONFIG,
    VISION_CONFIG
)

URL_EDSM_GMP = "https://edastro.com/gec/json/combined"

# Catégories EDAstro GEC + EDSM GMP visuellement utiles dans le ciel d'Elite Dangerous
CATEGORIES_EDSM_UTILES = {
    "nebula": "nébuleuse",
    "Nebulae": "nébuleuse",
    "planetaryNebula": "nébuleuse planétaire",
    "starCluster": "amas stellaire",
    "blackHole": "trou noir remarquable",
    "pulsar": "pulsar / étoile à neutrons",
    "stellarRemnant": "rémanent stellaire",
    "Notable Stellar Phenomena": "phénomène stellaire notable"
}

# Correspondances entre les noms de genres traduits en français dans Elite Dangerous et leur clé Codex
ALIAS_GENRES_FR = {
    "touradon": "Tussock",
    "tussock": "Tussock",
    "bacterie": "Bacterium",
    "bacteries": "Bacterium",
    "bacterium": "Bacterium",
    "fumerolle": "Fumerola",
    "fumerola": "Fumerola"
}

# ==============================================================================
# BASE ENCYCLOPÉDIQUE PAR DÉFAUT (EXOBIOLOGIE ODYSSEY, GÉOLOGIE & NÉBULEUSES)
# ==============================================================================
NEBULEUSES_DEFAUT = [
    {"nom": "Boucle de Barnard", "coords": [617.0, -422.0, -1225.0], "type": "nébuleuse", "aspect": "immense arc rouge-orangé en demi-cercle"},
    {"nom": "Nébuleuse d'Orion", "coords": [610.0, -430.0, -1210.0], "type": "nébuleuse", "aspect": "tache brillante rose/blanche au cœur de la Boucle de Barnard"},
    {"nom": "Nébuleuse de la Tête de Cheval", "coords": [560.0, -370.0, -1170.0], "type": "nébuleuse", "aspect": "nuage sombre et rouge près de la Boucle de Barnard"},
    {"nom": "Nébuleuse de la Flamme", "coords": [565.0, -370.0, -1165.0], "type": "nébuleuse", "aspect": "nuage rouge-orangé brillant contre la Tête de Cheval"},
    {"nom": "Nébuleuse de l'Homme qui court", "coords": [605.0, -435.0, -1215.0], "type": "nébuleuse", "aspect": "voile bleu/violet collé à Orion"},
    {"nom": "Nébuleuse de la Tête de Sorcière", "coords": [360.0, -718.0, -386.0], "type": "nébuleuse", "aspect": "voile bleuté-violet"},
    {"nom": "Nébuleuse des Pléiades", "coords": [-78.0, -149.0, -340.0], "type": "nébuleuse", "aspect": "amas d'étoiles bleues brillantes"},
    {"nom": "Nébuleuse de la Californie", "coords": [-304.0, -236.0, -861.0], "type": "nébuleuse", "aspect": "filament rouge allongé"},
    {"nom": "Nébuleuse de la Mouette", "coords": [2680.0, -155.0, -2704.0], "type": "nébuleuse", "aspect": "nuage rouge allongé en forme d'oiseau"},
    {"nom": "Nébuleuse de la Rosette", "coords": [2050.0, -100.0, -4800.0], "type": "nébuleuse", "aspect": "couronne/nuage rougeoyant"},
    {"nom": "Nébuleuse de la Méduse", "coords": [1090.0, 90.0, -4900.0], "type": "nébuleuse", "aspect": "nuage rouge-rosé"},
    {"nom": "Nébuleuse de la Tête de Singe", "coords": [1050.0, 20.0, -6100.0], "type": "nébuleuse", "aspect": "nuage rouge compact"},
    {"nom": "Nébuleuse du Crabe", "coords": [450.0, -600.0, -6950.0], "type": "nébuleuse", "aspect": "rémanent de supernova bleuté-orangé"},
    {"nom": "Nébuleuse du Sac à Charbon (Coalsack)", "coords": [405.0, 53.0, 304.0], "type": "nébuleuse", "aspect": "grande nébuleuse obscure noire sur la Voie Lactée"},
    {"nom": "Nébuleuse du Voile Ouest", "coords": [-1400.0, -250.0, 500.0], "type": "nébuleuse", "aspect": "filaments bleus et roses"},
    {"nom": "Nébuleuse du Voile Est", "coords": [-1470.0, -220.0, 460.0], "type": "nébuleuse", "aspect": "filaments rouges et bleus"},
    {"nom": "Nébuleuse de l'Amérique du Nord", "coords": [-1920.0, -15.0, 250.0], "type": "nébuleuse", "aspect": "grand nuage rouge-rose"},
    {"nom": "Nébuleuse du Pélican", "coords": [-1900.0, -15.0, 240.0], "type": "nébuleuse", "aspect": "nuage rouge voisin de l'Amérique du Nord"},
    {"nom": "Nébuleuse de la Lagune", "coords": [-460.0, -120.0, 4460.0], "type": "nébuleuse", "aspect": "nuage rose-rouge brillant"},
    {"nom": "Nébuleuse Trifide", "coords": [-465.0, -70.0, 5130.0], "type": "nébuleuse", "aspect": "nuage rouge et bleu"},
    {"nom": "Nébuleuse Oméga", "coords": [-1350.0, -80.0, 5400.0], "type": "nébuleuse", "aspect": "nuage rouge-orangé"},
    {"nom": "Nébuleuse de l'Aigle", "coords": [-1740.0, 80.0, 6780.0], "type": "nébuleuse", "aspect": "nuage doré-rouge (Piliers de la Création)"},
    {"nom": "Nébuleuse de la Carène", "coords": [6300.0, -200.0, 3800.0], "type": "nébuleuse", "aspect": "immense nuage rouge et bleu"},
    {"nom": "Nébuleuse du Cœur", "coords": [-4550.0, 280.0, -5650.0], "type": "nébuleuse", "aspect": "grand nuage rouge"},
    {"nom": "Nébuleuse de l'Âme", "coords": [-4350.0, 310.0, -5950.0], "type": "nébuleuse", "aspect": "grand nuage rouge voisin du Cœur"},
    {"nom": "NGC 7822", "coords": [-2100.0, 290.0, -1720.0], "type": "amas stellaire", "aspect": "chapelet très lumineux d'étoiles bleues alignées"}
]

EXOBIOLOGIE_DEFAUT = {
    "Aleoida": {
        "distance_m": 150,
        "apparence": "plantes basses charnues en couronne ou éventail évasé au ras du sol",
        "habitat": "plaines et vallées sur planètes rocheuses ou riches en métaux",
        "especes": {
            "Aleoida Arcus": 7252500,
            "Aleoida Coronamus": 6284600,
            "Aleoida Gravis": 12934900,
            "Aleoida Laminiae": 3385200,
            "Aleoida Spica": 3385200
        }
    },
    "Bacterium": {
        "distance_m": 500,
        "apparence": "taches, croûtes ou flaques plates collées au sol (parfois discrètes ou légèrement lumineuses)",
        "habitat": "terrains plats et ouverts, presque tous types de mondes atmosphériques",
        "especes": {
            "Bacterium Acies": 1000000,
            "Bacterium Alcyoneum": 1658500,
            "Bacterium Aurasus": 1000000,
            "Bacterium Bullaris": 1152500,
            "Bacterium Cerbrus": 1689800,
            "Bacterium Informem": 8418000,
            "Bacterium Nebulus": 5289900,
            "Bacterium Omentum": 4638900,
            "Bacterium Scopulum": 4934500,
            "Bacterium Tela": 1949000,
            "Bacterium Verrata": 3897000,
            "Bacterium Vesicula": 1000000,
            "Bacterium Volu": 7774700
        }
    },
    "Cactoida": {
        "distance_m": 300,
        "apparence": "grands cactus épais bulbeux ou ramifiés avec nervures/pointes, taille humaine",
        "habitat": "terrains vallonnés et rocheux, atmosphères CO2/ammoniac/eau",
        "especes": {
            "Cactoida Cortexum": 3667600,
            "Cactoida Lapis": 2483600,
            "Cactoida Peperatis": 2483600,
            "Cactoida Pullulanta": 3667600,
            "Cactoida Vermis": 16202800
        }
    },
    "Clypeus": {
        "distance_m": 150,
        "apparence": "grands champignons ou coupes-parasols évasées montées sur une tige épaisse",
        "habitat": "plaines rocheuses (atmosphères CO2 ou eau)",
        "especes": {
            "Clypeus Lacrimam": 8418000,
            "Clypeus Margaritus": 11873200,
            "Clypeus Speculumi": 16202800
        }
    },
    "Concha": {
        "distance_m": 150,
        "apparence": "coquilles ou conques charnues ouvertes en coupe posées bas sur le sol",
        "habitat": "terrains accidentés, canyons et pentes rocheuses",
        "especes": {
            "Concha Aureolas": 7774700,
            "Concha Biconcavis": 16777215,
            "Concha Labiata": 2352400,
            "Concha Renibus": 4572400
        }
    },
    "Electricae": {
        "distance_m": 1000,
        "apparence": "grands filaments ou tiges fluorescentes/électriques très lumineuses",
        "habitat": "mondes glacés à atmosphère argon/néon proches de nébuleuses ou étoiles chaudes",
        "especes": {
            "Electricae Pluma": 6284600,
            "Electricae Radialem": 6284600
        }
    },
    "Fonticulua": {
        "distance_m": 500,
        "apparence": "colonnes, dômes ou bulbes charnus/translucides poussant sur la glace",
        "habitat": "mondes glacés et rocheux-glacés",
        "especes": {
            "Fonticulua Campestris": 1000000,
            "Fonticulua Digitos": 1804100,
            "Fonticulua Fluctus": 20000000,
            "Fonticulua Lapida": 3111000,
            "Fonticulua Segmentatus": 19010800,
            "Fonticulua Upupam": 5727600
        }
    },
    "Frutexa": {
        "distance_m": 150,
        "apparence": "arbustes bas ligneux, petits buissons ramifiés ou éventails secs",
        "habitat": "zones rocheuses, collines et contreforts montagneux",
        "especes": {
            "Frutexa Acus": 7774700,
            "Frutexa Coelum": 1639800,
            "Frutexa Collum": 1639800,
            "Frutexa Fera": 1639800,
            "Frutexa Flabellum": 1808900,
            "Frutexa Flammasis": 10326000,
            "Frutexa Metallicum": 1639800,
            "Frutexa Sponsae": 5988000
        }
    },
    "Fumerola": {
        "distance_m": 100,
        "apparence": "colonies organiques tubulaires poussant directement sur ou contre les évents volcaniques",
        "habitat": "exclusivement autour des fumerolles et sites volcaniques actifs",
        "especes": {
            "Fumerola Aquatis": 6284600,
            "Fumerola Carbosis": 6284600,
            "Fumerola Extremus": 16202800,
            "Fumerola Nitris": 7500900
        }
    },
    "Fungoida": {
        "distance_m": 300,
        "apparence": "champignons bulbeux, grappes fongiques ou tiges coiffées de chapeaux",
        "habitat": "terrains escarpés, montagnes et crêtes rocheuses",
        "especes": {
            "Fungoida Bullarum": 3703200,
            "Fungoida Gelata": 3330300,
            "Fungoida Setisis": 1670100,
            "Fungoida Stabitis": 2680300
        }
    },
    "Osseus": {
        "distance_m": 800,
        "apparence": "structures rigides osseuses ou coralliennes pâles, disques ou spirales calcaires",
        "habitat": "terrains rocheux dégagés",
        "especes": {
            "Osseus Cornibus": 1483000,
            "Osseus Discus": 12934900,
            "Osseus Fractus": 4027800,
            "Osseus Pellebantus": 9739000,
            "Osseus Pumice": 3156300,
            "Osseus Spiralis": 2404700
        }
    },
    "Recepta": {
        "distance_m": 150,
        "apparence": "grandes coupes/urnes géométriques alvéolées ou bulbes striés très reconnaissables",
        "habitat": "mondes à atmosphère SO2/CO2",
        "especes": {
            "Recepta Conditivus": 14313700,
            "Recepta Deltahedronix": 16202800,
            "Recepta Umbrux": 12934900
        }
    },
    "Stratum": {
        "distance_m": 500,
        "apparence": "larges plaques plates circulaires, disques ou dômes bas posés à même les plaines",
        "habitat": "grandes plaines plates sur mondes riches en métaux ou rocheux",
        "especes": {
            "Stratum Araneamus": 2448900,
            "Stratum Cucumisis": 16202800,
            "Stratum Excutitus": 2448900,
            "Stratum Frigus": 2637500,
            "Stratum Laminamus": 2788300,
            "Stratum Limaxus": 1362000,
            "Stratum Paleas": 1362000,
            "Stratum Tectonicas": 19010800
        }
    },
    "Tubus": {
        "distance_m": 800,
        "apparence": "grands tubes ou arbres cylindriques verticaux très hauts (plus grands qu'un humain)",
        "habitat": "plaines sur mondes rocheux / riches en métaux (CO2 ou ammoniac)",
        "especes": {
            "Tubus Cavas": 11873200,
            "Tubus Compagibus": 7774700,
            "Tubus Conifer": 2415500,
            "Tubus Rosarium": 2637500,
            "Tubus Sororibus": 5727600
        }
    },
    "Tussock": {
        "distance_m": 200,
        "apparence": "touffes d'herbe, joncs fins ou petits buissons herbacés groupés au sol",
        "habitat": "plaines sablonneuses ou rocheuses",
        "especes": {
            "Tussock Albata": 3252500,
            "Tussock Capillum": 7025800,
            "Tussock Caputus": 3472400,
            "Tussock Catena": 1766600,
            "Tussock Cultro": 1766600,
            "Tussock Divisa": 1766600,
            "Tussock Ignis": 1849000,
            "Tussock Pennata": 5853800,
            "Tussock Pennatis": 1000000,
            "Tussock Propagito": 1000000,
            "Tussock Serrati": 4447100,
            "Tussock Stigmasis": 19010800,
            "Tussock Triticum": 7774700,
            "Tussock Ventusa": 3227700,
            "Tussock Virgam": 14313700
        }
    }
}

GEOLOGIE_DEFAUT = [
    {
        "id": "lava_spout",
        "nom": "Cheminée / Évent de lave (Lava Spout)",
        "mots_cles_volcanisme": ["magma", "silicate", "iron", "fer", "lave"],
        "mots_cles_codex": ["lava", "lave", "magma", "spout", "cheminee"],
        "apparence": "petit cratère ou fissure projetant un jet lumineux orange-jaune incandescent de magma avec étincelles"
    },
    {
        "id": "geyser",
        "nom": "Geyser",
        "mots_cles_volcanisme": ["geyser", "water", "eau", "ice", "glace", "vapour", "vapeur", "nitrogen", "azote", "methane", "ammonia"],
        "mots_cles_codex": ["geyser"],
        "apparence": "jet vertical brillant de vapeur blanche/bleutée ou de cristaux de glace projeté haut au-dessus du sol"
    },
    {
        "id": "fumarole",
        "nom": "Fumerolle",
        "mots_cles_volcanisme": ["fumarole", "silicate", "sulphur", "soufre", "carbon", "methane", "ammonia", "nitrogen", "water", "vapour"],
        "mots_cles_codex": ["fumarole", "fumerolle"],
        "apparence": "petite cheminée conique rocheuse ou glacée laissant échapper un panache continu de fumée/vapeur"
    },
    {
        "id": "gas_vent",
        "nom": "Évent gazeux (Gas Vent)",
        "mots_cles_volcanisme": ["gas", "gaz", "sulphur", "soufre", "carbon", "dioxyde", "methane", "water", "silicate"],
        "mots_cles_codex": ["gas vent", "event gazeux", "event"],
        "apparence": "bouche ou orifice minéral au sol soufflant un flux de gaz ou de vapeur dense"
    }
]

_codex_ed_cache = None
_codex_cmdr_cache = None
_verrou_codex = threading.Lock()


def _norm(texte: str) -> str:
    """Normalise une chaîne pour comparaisons insensibles aux accents et à la casse."""
    if not texte:
        return ""
    sans_acc = "".join(
        c for c in unicodedata.normalize("NFD", str(texte))
        if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", sans_acc.lower())).strip()


def _ecrire_json_atomique(chemin, data: dict):
    """Écrit un fichier JSON de façon atomique (.tmp -> replace)."""
    tmp = str(chemin) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, chemin)


def _formater_credits_courts(valeur: int) -> str:
    """Formate un montant en crédits compact pour le HUD (ex: 19 010 800 -> '19,0 M Cr')."""
    if valeur >= 1_000_000:
        return f"{valeur / 1_000_000:.1f} M Cr".replace(".", ",")
    if valeur >= 1_000:
        return f"{int(round(valeur / 1_000))} k Cr"
    return f"{valeur} Cr"


def _formater_credits_vocaux(valeur: int) -> str:
    """Formate un montant en crédits sans abréviation piégeuse pour la synthèse vocale.

    Exemples :
    - 95 100 000 -> '95,1 millions de crédits'
    - 197 000 -> '197 000 crédits'
    - 0 -> '0 crédit'
    """
    val = int(round(valeur or 0))
    if val >= 1_000_000_000:
        txt = f"{val / 1_000_000_000:.2f}".rstrip("0").rstrip(".").replace(".", ",")
        return f"{txt} milliards de crédits"
    if val >= 1_000_000:
        txt = f"{val / 1_000_000:.1f}".replace(".0", "").replace(".", ",")
        return f"{txt} millions de crédits"
    if val >= 1_000:
        arrondi = int(round(val / 100.0) * 100)
        return f"{arrondi:,}".replace(",", " ") + " crédits"
    if val == 0:
        return "0 crédit"
    return f"{val} crédits"


# ==============================================================================
# 1. BASE ENCYCLOPÉDIQUE LOCALE (data/codex_ed.json) + SYNCHRO EDSM GMP
# ==============================================================================
def _construire_codex_defaut() -> dict:
    return {
        "version": 1,
        "derniere_maj_edsm": 0,
        "source_edsm": URL_EDSM_GMP,
        "exobiologie": EXOBIOLOGIE_DEFAUT,
        "geologie": GEOLOGIE_DEFAUT,
        "nebuleuses_pois": list(NEBULEUSES_DEFAUT)
    }


def charger_codex_ed() -> dict:
    """Charge data/codex_ed.json (le crée automatiquement s'il n'existe pas encore)."""
    global _codex_ed_cache
    with _verrou_codex:
        if _codex_ed_cache is not None:
            return _codex_ed_cache
        if FICHIER_CODEX_ED.exists():
            try:
                with open(FICHIER_CODEX_ED, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "exobiologie" in data:
                    _codex_ed_cache = data
                    return _codex_ed_cache
            except Exception as e:
                print(f"[Codex] Erreur lecture {FICHIER_CODEX_ED.name} ({e}), régénération par défaut.")

        data = _construire_codex_defaut()
        try:
            _ecrire_json_atomique(FICHIER_CODEX_ED, data)
        except Exception as e:
            print(f"[Codex] Impossible d'écrire {FICHIER_CODEX_ED.name} : {e}")
        _codex_ed_cache = data
        return _codex_ed_cache


def synchroniser_nebuleuses_edsm(forcer: bool = False) -> tuple[bool, str]:
    """Met à jour les nébuleuses et POIs galactiques depuis le Galactic Mapping Project d'EDSM."""
    global _codex_ed_cache
    codex = charger_codex_ed()
    jours_intervalle = max(1, int(VISION_CONFIG.get("codex_maj_auto_jours", 30)))
    dernier_ts = float(codex.get("derniere_maj_edsm", 0) or 0)
    age_jours = (time.time() - dernier_ts) / 86400.0 if dernier_ts > 0 else 9999.0

    if not forcer and age_jours < jours_intervalle:
        return False, f"Base galactique déjà à jour ({age_jours:.1f} j < {jours_intervalle} j)."

    try:
        rep = requests.get(URL_EDSM_GMP, headers=HEADERS_HTTP, timeout=20)
        if rep.status_code != 200:
            return False, f"EDSM GMP a répondu HTTP {rep.status_code}."
        entrees_brutes = rep.json()
        if not isinstance(entrees_brutes, list):
            return False, "Format EDSM GMP inattendu."

        # Conserve en priorité nos 26 grandes nébuleuses avec leurs descriptions visuelles FR
        par_nom = {}
        for item in NEBULEUSES_DEFAUT:
            par_nom[_norm(item["nom"])] = dict(item)

        ajoutes = 0
        for e in entrees_brutes:
            if not isinstance(e, dict):
                continue
            type_edsm = str(e.get("type") or "").strip()
            if type_edsm not in CATEGORIES_EDSM_UTILES:
                continue
            coords = e.get("coordinates")
            nom = str(e.get("name") or "").strip()
            if not nom or not isinstance(coords, list) or len(coords) != 3:
                continue
            try:
                c_xyz = [round(float(coords[0]), 1), round(float(coords[1]), 1), round(float(coords[2]), 1)]
            except Exception:
                continue

            cle = _norm(nom)
            if cle in par_nom:
                continue
            # Évite les doublons anglais des 26 grandes nébuleuses déjà présentes en FR (proches à < 45 AL)
            doublon_proche = False
            for ref in NEBULEUSES_DEFAUT:
                rx, ry, rz = ref["coords"]
                if math.sqrt((c_xyz[0] - rx) ** 2 + (c_xyz[1] - ry) ** 2 + (c_xyz[2] - rz) ** 2) < 45.0 and type_edsm in ("nebula", "Nebulae"):
                    doublon_proche = True
                    break
            if doublon_proche:
                continue

            resume_court = str(e.get("summary") or "").strip()
            aspect = CATEGORIES_EDSM_UTILES[type_edsm]
            if resume_court:
                aspect = f"{aspect} — {resume_court[:90].rstrip('. ')}"

            par_nom[cle] = {
                "nom": nom,
                "coords": c_xyz,
                "type": CATEGORIES_EDSM_UTILES[type_edsm],
                "aspect": aspect
            }
            ajoutes += 1

        nouveau_codex = dict(codex)
        nouveau_codex["derniere_maj_edsm"] = int(time.time())
        nouveau_codex["nebuleuses_pois"] = list(par_nom.values())

        with _verrou_codex:
            _ecrire_json_atomique(FICHIER_CODEX_ED, nouveau_codex)
            _codex_ed_cache = nouveau_codex

        taille_ko = round(os.path.getsize(FICHIER_CODEX_ED) / 1024.0, 1)
        msg = f"Base galactique EDSM mise à jour ({len(nouveau_codex['nebuleuses_pois'])} nébuleuses/POIs, {taille_ko} Ko)."
        print(f"[Codex] {msg}")
        return True, msg
    except Exception as e:
        return False, f"Synchro EDSM ignorée ({e})."


def lancer_maj_codex_async():
    """Lance au démarrage la vérification/mise à jour silencieuse du Codex et de l'historique CMDR."""
    def _tache():
        try:
            indexer_codex_commandant()
            synchroniser_nebuleuses_edsm(forcer=False)
        except Exception as e:
            print(f"[Codex] Erreur initialisation asynchrone : {e}")

    threading.Thread(target=_tache, name="OscarCodexSync", daemon=True).start()


# ==============================================================================
# 2. INDEX PERSONNEL DU COMMANDANT (data/codex_cmdr.json, LECTURE SEULE JOURNAUX)
# ==============================================================================
def _structure_cmdr_vide() -> dict:
    return {
        "derniere_maj": 0,
        "fichiers_indexes": {},
        "systemes_visites": {},
        "biologie_vue": {},
        "genres_bio_vus": {},
        "geologie_vue": {},
        "astronomie_vue": {}
    }


def _charger_codex_cmdr_brut() -> dict:
    global _codex_cmdr_cache
    if _codex_cmdr_cache is not None:
        return _codex_cmdr_cache
    if FICHIER_CODEX_CMDR.exists():
        try:
            with open(FICHIER_CODEX_CMDR, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "biologie_vue" in data:
                data.setdefault("systemes_visites", {})
                _codex_cmdr_cache = data
                return _codex_cmdr_cache
        except Exception:
            pass
    _codex_cmdr_cache = _structure_cmdr_vide()
    return _codex_cmdr_cache


def _enregistrer_rencontre(dico: dict, nom: str, systeme: str, date_iso: str, extra: dict = None):
    cle = _norm(nom)
    if not cle:
        return
    entree = dico.get(cle)
    date_courte = str(date_iso or "")[:10]
    if entree is None:
        nouv = {
            "nom": nom,
            "premiere_date": date_courte,
            "systeme": systeme or "Inconnu",
            "compteur": 1
        }
        if extra:
            nouv.update(extra)
        dico[cle] = nouv
    else:
        entree["compteur"] = int(entree.get("compteur", 1)) + 1


def indexer_codex_commandant(forcer_complet: bool = False) -> dict:
    """Scanne en lecture seule les Journal.*.log locaux pour mémoriser ce que le CMDR a déjà vu."""
    global _codex_cmdr_cache
    if not os.path.isdir(DOSSIER_JOURNAUX_ED):
        return _charger_codex_cmdr_brut()

    with _verrou_codex:
        brut = _charger_codex_cmdr_brut()
        # Si l'ancien cache n'avait pas encore indexé les systèmes visités, on force une réindexation unique
        besoin_complet = forcer_complet or (bool(brut.get("fichiers_indexes")) and not brut.get("systemes_visites"))
        data = _structure_cmdr_vide() if besoin_complet else brut
        data.setdefault("systemes_visites", {})
        fichiers = sorted(
            glob.glob(os.path.join(DOSSIER_JOURNAUX_ED, "Journal.*.log")),
            key=os.path.getmtime
        )
        indexes = data.setdefault("fichiers_indexes", {})
        modifie = False

        for chemin in fichiers:
            nom_f = os.path.basename(chemin)
            try:
                taille = os.path.getsize(chemin)
            except OSError:
                continue
            # Saute les anciens journaux déjà intégralement indexés (taille inchangée)
            if indexes.get(nom_f) == taille:
                continue

            systeme_courant = "Inconnu"
            try:
                with open(chemin, "r", encoding="utf-8", errors="ignore") as f:
                    for ligne in f:
                        if not ligne or "{" not in ligne:
                            continue
                        if not any(k in ligne for k in ('"CodexEntry"', '"ScanOrganic"', '"FSDJump"', '"Location"')):
                            continue
                        try:
                            ev = json.loads(ligne)
                        except Exception:
                            continue

                        etype = ev.get("event", "")
                        ts = ev.get("timestamp", "")
                        if etype in ("FSDJump", "Location"):
                            if ev.get("StarSystem"):
                                systeme_courant = str(ev["StarSystem"])
                                _enregistrer_rencontre(data["systemes_visites"], systeme_courant, systeme_courant, ts)

                        elif etype == "ScanOrganic":
                            genre = str(ev.get("Genus_Localised") or ev.get("Genus") or "").strip()
                            espece = str(ev.get("Species_Localised") or ev.get("Species") or "").strip()
                            variante = str(ev.get("Variant_Localised") or ev.get("Variant") or "").strip()
                            if genre:
                                genre_canon = ALIAS_GENRES_FR.get(_norm(genre), genre)
                                _enregistrer_rencontre(data["genres_bio_vus"], genre_canon, systeme_courant, ts)
                            if espece:
                                _enregistrer_rencontre(
                                    data["biologie_vue"], espece, systeme_courant, ts,
                                    {"genre": genre, "variante": variante}
                                )

                        elif etype == "CodexEntry":
                            nom_c = str(ev.get("Name_Localised") or ev.get("Name") or "").strip()
                            cat = str(ev.get("Category") or "").lower()
                            sub = str(ev.get("SubCategory") or "").lower()
                            sys_ev = str(ev.get("System") or systeme_courant)
                            if not nom_c:
                                continue
                            # Vérifier la géologie AVANT la biologie (ED met les deux sous Category_Biology)
                            if "geolog" in sub or "geolog" in cat or any(
                                k in _norm(nom_c) for k in ("geyser", "fumeroll", "fumarol", "lave", "lava", "magma", "event", "vent", "cheminee")
                            ):
                                _enregistrer_rencontre(data["geologie_vue"], nom_c, sys_ev, ts)
                            elif "biology" in cat or "organic" in sub:
                                _enregistrer_rencontre(data["biologie_vue"], nom_c, sys_ev, ts)
                                # Enregistre aussi le genre canonique (ex: "Touradon Virgam" -> "Tussock")
                                premier_mot = nom_c.split()[0] if nom_c.split() else ""
                                genre_canon = ALIAS_GENRES_FR.get(_norm(premier_mot), premier_mot)
                                if genre_canon and genre_canon in EXOBIOLOGIE_DEFAUT:
                                    _enregistrer_rencontre(data["genres_bio_vus"], genre_canon, sys_ev, ts)
                            else:
                                _enregistrer_rencontre(data["astronomie_vue"], nom_c, sys_ev, ts)
            except Exception:
                continue

            indexes[nom_f] = taille
            modifie = True

        if modifie or not FICHIER_CODEX_CMDR.exists():
            data["derniere_maj"] = int(time.time())
            try:
                _ecrire_json_atomique(FICHIER_CODEX_CMDR, data)
            except Exception as e:
                print(f"[Codex] Erreur sauvegarde {FICHIER_CODEX_CMDR.name} : {e}")
            _codex_cmdr_cache = data
            print(
                f"[Codex] Historique CMDR synchronisé ({len(indexes)} journaux : "
                f"{len(data['systemes_visites'])} systèmes, {len(data['biologie_vue'])} bio, "
                f"{len(data['geologie_vue'])} géo, {len(data['astronomie_vue'])} astro)."
            )

        return data


def obtenir_systeme_maison() -> str:
    """Retourne le système 'maison' (configuré dans config_oscar.json ou détecté via la flotte)."""
    cfg_maison = str(NAVIGATION_CONFIG.get("systeme_maison", "auto") or "auto").strip()
    if cfg_maison and cfg_maison.lower() != "auto":
        return cfg_maison

    # Détection automatique : système abritant le plus grand nombre de vaisseaux stockés
    if FICHIER_FLOTTE.exists():
        try:
            with open(FICHIER_FLOTTE, "r", encoding="utf-8") as f:
                flotte = json.load(f)
            compteurs = {}
            for v in flotte.get("vaisseaux_stockes", []):
                sys_v = str(v.get("systeme") or "").strip()
                if sys_v:
                    compteurs[sys_v] = compteurs.get(sys_v, 0) + 1
            if compteurs:
                return max(compteurs.items(), key=lambda x: x[1])[0]
        except Exception:
            pass
    return ""


def systeme_deja_visite_par_cmdr(nom_systeme: str) -> bool:
    """Indique si le Commandant a déjà visité ce système dans son historique local."""
    cle = _norm(nom_systeme)
    if not cle:
        return False
    data = _charger_codex_cmdr_brut()
    if not data.get("systemes_visites") and os.path.isdir(DOSSIER_JOURNAUX_ED):
        data = indexer_codex_commandant(forcer_complet=False)
    return cle in (data.get("systemes_visites") or {})


def enregistrer_visite_systeme_cmdr(nom_systeme: str):
    """Mémorise immédiatement la visite d'un système dans le cache local du Commandant."""
    if not nom_systeme:
        return
    with _verrou_codex:
        data = _charger_codex_cmdr_brut()
        data.setdefault("systemes_visites", {})
        _enregistrer_rencontre(data["systemes_visites"], nom_systeme, nom_systeme, time.strftime("%Y-%m-%d"))
        data["derniere_maj"] = int(time.time())
        try:
            _ecrire_json_atomique(FICHIER_CODEX_CMDR, data)
        except Exception:
            pass


# ==============================================================================
# 3. REQUÊTES CIBLÉES POUR LA VISION D'OSCAR (NÉBULEUSES, GÉO, EXOBIO, HISTORIQUE)
# ==============================================================================
MOTS_NEBULEUSE_ROUGE = (
    "rouge", "orang", "rose", "crimson", "red", "pink", "barnard", "orion",
    "flamme", "flame", "cheval", "horsehead", "californi", "rosette",
    "mouette", "seagull", "meduse", "jellyfish", "singe", "monkey",
    "lagune", "lagoon", "omega", "aigle", "eagle", "carene", "carina",
    "coeur", "heart", "ame", "soul", "amerique", "pelican", "trifid", "lambda orionis"
)
MOTS_NEBULEUSE_BLEUE = (
    "bleu", "violet", "cyan", "blue", "sorciere", "witch head", "pleiades",
    "homme qui court", "running man", "ngc 7822", "voile", "veil", "crabe", "crab", "messier 78"
)
MOTS_NEBULEUSE_SOMBRE = (
    "sombre", "noire", "obscur", "dark", "charbon", "coalsack"
)


def _couleurs_nebuleuse(nom: str, aspect: str) -> set[str]:
    """Identifie les dominantes de couleur connues d'une nébuleuse à partir de son nom et aspect."""
    txt = _norm(f"{nom} {aspect}")
    couleurs = set()
    if any(m in txt for m in MOTS_NEBULEUSE_ROUGE):
        couleurs.add("rouge")
    if any(m in txt for m in MOTS_NEBULEUSE_BLEUE):
        couleurs.add("bleu")
    if any(m in txt for m in MOTS_NEBULEUSE_SOMBRE):
        couleurs.add("sombre")
    return couleurs


def calculer_nebuleuses_proches_codex(
    star_pos: list | tuple | None,
    top_n: int = 8,
    couleur_filtre: str = ""
) -> list[str]:
    """Calcule les grandes nébuleuses et POIs galactiques les plus proches depuis data/codex_ed.json.

    Si `couleur_filtre` ('rouge', 'bleu' ou 'sombre') est précisé, exclut les nébuleuses
    de couleur strictement incompatible (ex: évite de proposer la Tête de Sorcière bleue
    quand le pilote demande d'identifier une nébuleuse rouge) et priorise les candidates cohérentes.
    """
    if not star_pos or len(star_pos) != 3:
        return []
    try:
        sx, sy, sz = float(star_pos[0]), float(star_pos[1]), float(star_pos[2])
    except Exception:
        return []

    filtre = _norm(couleur_filtre)
    codex = charger_codex_ed()
    items = codex.get("nebuleuses_pois", NEBULEUSES_DEFAUT)
    grandes_match = []
    grandes_neutres = []
    autres = []

    for item in items:
        coords = item.get("coords")
        if not coords or len(coords) != 3:
            continue
        nom = str(item.get("nom") or "").strip()
        aspect = str(item.get("aspect") or item.get("type") or "").strip()
        d = math.sqrt((sx - coords[0]) ** 2 + (sy - coords[1]) ** 2 + (sz - coords[2]) ** 2)
        couleurs = _couleurs_nebuleuse(nom, aspect)

        # Filtrage strict par couleur si le pilote en a précisé une
        if filtre == "rouge" and "bleu" in couleurs and "rouge" not in couleurs:
            continue
        if filtre == "bleu" and "rouge" in couleurs and "bleu" not in couleurs:
            continue
        if filtre == "sombre" and ("rouge" in couleurs or "bleu" in couleurs) and "sombre" not in couleurs:
            continue

        entree = (d, nom, aspect)
        if item.get("type") in ("nébuleuse", "amas stellaire"):
            if filtre and filtre in couleurs:
                grandes_match.append(entree)
            else:
                grandes_neutres.append(entree)
        else:
            autres.append(entree)

    grandes_match.sort(key=lambda x: x[0])
    grandes_neutres.sort(key=lambda x: x[0])
    autres.sort(key=lambda x: x[0])

    if filtre and grandes_match:
        # Priorise d'abord les nébuleuses confirmées de la bonne couleur, puis complète si besoin
        selection = list(grandes_match[:top_n])
        if len(selection) < top_n:
            selection.extend(grandes_neutres[:top_n - len(selection)])
    else:
        grandes = sorted(grandes_match + grandes_neutres, key=lambda x: x[0])
        selection = grandes[:max(6, top_n - 2)]
        for d, nom, aspect in autres[:2]:
            if d <= 350.0 and len(selection) < top_n:
                selection.append((d, nom, aspect))
        if len(selection) < top_n:
            for ent in grandes[len(selection):]:
                if len(selection) >= top_n:
                    break
                selection.append(ent)
        selection.sort(key=lambda x: x[0])

    return [f"{nom} (~{int(round(d))} AL, {aspect})" for d, nom, aspect in selection[:top_n]]


def _trouver_rencontre_cmdr(dico: dict, mots_cles: list[str]) -> dict | None:
    """Cherche dans l'historique personnel du CMDR si un élément correspondant a déjà été vu."""
    for cle, info in (dico or {}).items():
        if any(mk in cle for mk in mots_cles if mk):
            return info
    return None


def construire_dossier_codex_vision(contexte: dict) -> str:
    """Construit un condensé Codex ultra-ciblé (exobio, géo, historique CMDR et statut planète)."""
    if not contexte:
        return ""

    codex = charger_codex_ed()
    # Rafraîchit rapidement le journal courant si de nouveaux scans ont eu lieu pendant le vol
    cmdr = indexer_codex_commandant(forcer_complet=False)
    lignes = []

    # 1. Statut de première découverte de la planète actuelle
    # Uniquement pertinent à pied, en VRS, en DSS ou en approche planétaire (pas quand on regarde le ciel en supercruise)
    est_surface_ou_approche = contexte.get("est_surface_ou_approche", True)
    if not est_surface_ou_approche:
        return ""

    was_disc = contexte.get("was_discovered")
    was_map = contexte.get("was_mapped")
    was_foot = contexte.get("was_footfalled")
    statuts_planete = []
    if was_disc is False:
        statuts_planete.append("Système/Planète JAMAIS DÉCOUVERTE avant toi (Première découverte !)")
    elif was_disc is True:
        statuts_planete.append("Planète déjà découverte par un autre Commandant")
    if was_map is False:
        statuts_planete.append("Non cartographiée avant toi")
    if was_foot is False:
        statuts_planete.append("VIERGE DE TOUT PAS HUMAIN -> Bonus Première Empreinte x5 en exobiologie !")
    elif was_foot is True:
        statuts_planete.append("Un autre Commandant a DÉJÀ posé le pied ici (tu n'es pas le premier malheureusement)")
    if statuts_planete:
        lignes.append("Statut découverte planète : " + " | ".join(statuts_planete))

    # 2. Exobiologie filtrée sur les genres présents sur la planète (si scannée au DSS)
    genres_planete = contexte.get("genres_biologiques") or []
    exobio_ref = codex.get("exobiologie", EXOBIOLOGIE_DEFAUT)
    if genres_planete:
        lignes.append("Fiches Codex Exobiologie pour les genres présents sur CETTE planète :")
        for g_raw in genres_planete:
            g_norm = _norm(g_raw)
            g_alias = ALIAS_GENRES_FR.get(g_norm, g_raw)
            g_alias_norm = _norm(g_alias)
            fiche_nom = None
            fiche_data = None
            for nom_g, d_g in exobio_ref.items():
                if _norm(nom_g) in (g_norm, g_alias_norm) or _norm(nom_g) in g_norm:
                    fiche_nom = nom_g
                    fiche_data = d_g
                    break
            if not fiche_data:
                continue

            especes = fiche_data.get("especes", {})
            val_min = min(especes.values()) if especes else 0
            val_max = max(especes.values()) if especes else 0
            prix_txt = (
                f"{_formater_credits_courts(val_min)} à {_formater_credits_courts(val_max)}"
                if val_min != val_max else _formater_credits_courts(val_max)
            )
            # Statut personnel du Commandant sur ce genre (accepte aussi alias FR ex: Touradon = Tussock)
            mots_genre = [_norm(fiche_nom)]
            if g_norm and g_norm not in mots_genre:
                mots_genre.append(g_norm)
            deja_genre = _trouver_rencontre_cmdr(cmdr.get("genres_bio_vus", {}), mots_genre)
            especes_deja_vues = [
                info.get("nom", "") for cle, info in (cmdr.get("biologie_vue") or {}).items()
                if any(mg in cle for mg in mots_genre)
            ]
            if deja_genre or especes_deja_vues:
                ex_str = ", ".join(especes_deja_vues[:3]) if especes_deja_vues else deja_genre.get("nom", fiche_nom)
                statut_cmdr = f"DÉJÀ RENCONTRÉ par le Commandant ({ex_str})"
            else:
                statut_cmdr = "NOUVEAU POUR LE COMMANDANT (jamais scanné dans ses journaux !)"

            top_especes = ", ".join(
                f"{nom_e.split()[-1]} ({_formater_credits_courts(val)})"
                for nom_e, val in sorted(especes.items(), key=lambda x: x[1], reverse=True)[:4]
            )
            lignes.append(
                f"- {fiche_nom} ({fiche_data.get('apparence')}) | Échantillons tous les {fiche_data.get('distance_m')}m | "
                f"Vista Genomics : {prix_txt} (x5 si 1ère empreinte ; ex: {top_especes}) | Codex CMDR : {statut_cmdr}"
            )

    # 3. Géologie filtrée selon le volcanisme exact du Scan (si présent)
    volcanisme = str(contexte.get("volcanisme") or "").strip()
    if volcanisme or contexte.get("signaux_geologiques"):
        volc_norm = _norm(volcanisme)
        geo_trouves = []
        for g in codex.get("geologie", GEOLOGIE_DEFAUT):
            # Exclure "Cheminée de lave" sur les mondes glacés à "water magma" (magma d'eau = geysers/glace, pas de lave)
            if g.get("id") == "lava_spout" and ("water" in volc_norm or "eau" in volc_norm or "ice" in volc_norm or "glace" in volc_norm):
                continue
            if not volc_norm or any(mk in volc_norm for mk in g.get("mots_cles_volcanisme", [])):
                deja_geo = _trouver_rencontre_cmdr(cmdr.get("geologie_vue", {}), g.get("mots_cles_codex", []))
                if deja_geo:
                    statut_g = f"DÉJÀ VU par le Commandant ({deja_geo.get('nom')} dans {deja_geo.get('systeme')})"
                else:
                    statut_g = "NOUVEAU POUR LE COMMANDANT (absent de son Codex local !)"
                geo_trouves.append(f"- {g['nom']} : {g['apparence']} | Codex CMDR : {statut_g}")
        if geo_trouves:
            lignes.append("Fiches Codex Géologie compatibles avec cette planète :")
            lignes.extend(geo_trouves[:3])

    return "\n".join(lignes)


# ==============================================================================
# 4. ANALYSE COMPLÈTE DU SYSTÈME APRÈS FSS (DSS, TERRAFORMABLES, BIO, MINERAIS)
# ==============================================================================
MATERIAUX_SURFACE_FR = {
    "iron": "Fer",
    "nickel": "Nickel",
    "carbon": "Carbone",
    "phosphorus": "Phosphore",
    "sulphur": "Soufre",
    "lead": "Plomb",
    "rhenium": "Rhénium",
    "chromium": "Chrome",
    "manganese": "Manganèse",
    "vanadium": "Vanadium",
    "germanium": "Germanium",
    "zinc": "Zinc",
    "arsenic": "Arsenic",
    "zirconium": "Zirconium",
    "niobium": "Niobium",
    "tungsten": "Tungstène",
    "cadmium": "Cadmium",
    "molybdenum": "Molybdène",
    "tin": "Étain",
    "mercury": "Mercure",
    "boron": "Bore",
    "polonium": "Polonium",
    "ruthenium": "Ruthénium",
    "tellurium": "Tellure",
    "technetium": "Technétium",
    "yttrium": "Yttrium",
    "antimony": "Antimoine",
    "selenium": "Sélénium"
}

MATERIAUX_RARES_G4 = {"polonium", "ruthenium", "tellurium", "technetium", "yttrium", "antimony", "selenium"}

CLASSES_ANNEAUX_INFO = {
    "eRingClass_Metalic": ("Métallique", "Platine, Osmium, Painite"),
    "eRingClass_Metallic": ("Métallique", "Platine, Osmium, Painite"),
    "eRingClass_MetalRich": ("Riche en métaux", "Monazite, Painite, Platine"),
    "eRingClass_Rocky": ("Rocheux", "Monazite, Musgravite, Bénitoïte"),
    "eRingClass_Icy": ("Glacé", "Tritium, Diamants Basse Température, Alexandrite")
}


def _estimer_valeurs_carto_corps(sc: dict, deja_mappee_cmdr: bool = False) -> dict:
    """Estime la valeur FSS acquise et le gain DSS (Universal Cartographics) d'une planète ou étoile."""
    premiere_dec = not bool(sc.get("WasDiscovered", False))
    premiere_carto = not bool(sc.get("WasMapped", False))

    # Cas d'une étoile
    if sc.get("StarType") and not sc.get("PlanetClass"):
        st = str(sc.get("StarType") or "").upper()
        if st in ("N", "H"):  # Étoile à neutrons / Trou noir
            base_etoile = 54_000
        elif st.startswith("D"):  # Naine blanche
            base_etoile = 33_000
        else:
            base_etoile = 2_900
        val_fss = int(round(base_etoile * (2.6 if premiere_dec else 1.0)))
        return {
            "libelle": f"Étoile ({st})",
            "valeur_fss": val_fss,
            "valeur_dss": val_fss,
            "gain_dss_net": 0,
            "valeur_acquise": val_fss
        }

    pclass = str(sc.get("PlanetClass") or "")
    pc = pclass.lower()
    terraformable = str(sc.get("TerraformState") or "").lower() == "terraformable"

    # Valeurs moyennes officielles Elite Dangerous Odyssey (FSS seul vs DSS avec bonus d'efficacité)
    if "earthlike" in pc:
        fss_base, dss_base, libelle = 270_000, 1_126_000, "Planète tellurique (ELW)"
    elif "water world" in pc:
        if terraformable:
            fss_base, dss_base, libelle = 268_000, 1_119_000, "Monde aquatique terraformable"
        else:
            fss_base, dss_base, libelle = 100_000, 415_000, "Monde aquatique"
    elif "ammonia" in pc:
        fss_base, dss_base, libelle = 143_000, 597_000, "Monde d'ammoniac"
    elif "high metal content" in pc:
        if terraformable:
            fss_base, dss_base, libelle = 164_000, 683_000, "HMC terraformable"
        else:
            fss_base, dss_base, libelle = 14_000, 58_000, "Riche en métaux (HMC)"
    elif "rocky body" in pc:
        if terraformable:
            fss_base, dss_base, libelle = 130_000, 539_000, "Rocheuse terraformable"
        else:
            fss_base, dss_base, libelle = 600, 2_500, "Planète rocheuse"
    elif "metal rich" in pc:
        fss_base, dss_base, libelle = 32_000, 131_000, "Corps riche en métaux"
    elif "sudarsky class ii" in pc:
        fss_base, dss_base, libelle = 28_000, 118_000, "Géante gazeuse classe II"
    elif "sudarsky class" in pc or "gas giant" in pc:
        fss_base, dss_base, libelle = 3_900, 16_000, "Géante gazeuse"
    elif "icy body" in pc:
        fss_base, dss_base, libelle = 500, 2_100, "Corps glacé"
    else:
        fss_base, dss_base, libelle = 1_200, 5_000, pclass or "Planète"

    # Multiplicateurs officiels Première Découverte / Première Cartographie
    val_fss = int(round(fss_base * (2.6 if premiere_dec else 1.0)))
    if premiere_dec and premiere_carto:
        val_dss = int(round(dss_base * 2.6))
    elif premiere_carto:
        val_dss = int(round(dss_base * 2.1))
    else:
        val_dss = dss_base

    gain_dss_net = max(0, val_dss - val_fss)
    valeur_acquise = val_dss if deja_mappee_cmdr else val_fss
    return {
        "libelle": libelle,
        "valeur_fss": val_fss,
        "valeur_dss": val_dss,
        "gain_dss_net": gain_dss_net,
        "valeur_acquise": valeur_acquise
    }


def _estimer_valeur_dss_planete(planet_class: str, terraformable: bool, premiere_decouverte: bool, premiere_carto: bool) -> tuple[int, str]:
    """Wrapper rétrocompatible retournant (valeur_dss_credits, libelle)."""
    d = _estimer_valeurs_carto_corps({
        "PlanetClass": planet_class,
        "TerraformState": "Terraformable" if terraformable else "",
        "WasDiscovered": not premiere_decouverte,
        "WasMapped": not premiere_carto
    })
    return d["valeur_dss"], d["libelle"]


def _formater_millions_compact_hud(valeur: int) -> str:
    """Formate un montant en millions ultra-compact pour le HUD 25 car. (ex: 95 100 000 -> '95M')."""
    if valeur >= 10_000_000:
        return f"{int(round(valeur / 1_000_000))}M"
    if valeur >= 1_000_000:
        val_m = round(valeur / 1_000_000.0, 1)
        return f"{int(val_m)}M" if val_m == int(val_m) else f"{val_m:.1f}M".replace(".", ",")
    if valeur >= 1_000:
        return f"{int(round(valeur / 1_000))}k"
    return f"{valeur}"


def _predire_exobiologie_fss(planet_class: str, atmo: str, temp_k: float | None, gravite_g: float | None, nb_bio: int, premiere_empreinte: bool) -> dict:
    """Prédit les genres biologiques probables et une fourchette réaliste Vista Genomics dès le FSS."""
    if nb_bio <= 0:
        return {
            "genres_probables": [],
            "potentiel_estime_credits": 0,
            "potentiel_max_credits": 0,
            "potentiel_max_texte": "0 Cr",
            "fourchette_hud": "0",
            "fourchette_vocale": "0 crédit",
            "alerte_jackpot": ""
        }

    pc = (planet_class or "").lower()
    at = (atmo or "").lower()
    tk = float(temp_k) if temp_k is not None else 200.0
    mult = 5 if premiere_empreinte else 1

    # Estimations de base (sans multiplicateur x5) : (min_probable, max_probable, max_theorique_rare)
    candidats = []
    alerte = ""
    base_prob_min = 1_000_000
    base_prob_max = 2_000_000
    base_rare_max = 2_000_000

    # Cas jackpot emblématique : HMC atterrissable, T° >= 165 K, atmosphère fine -> Stratum Tectonicas (19M / 95M)
    if "high metal content" in pc and tk >= 165.0:
        candidats.append("Stratum Tectonicas (très probable)")
        base_prob_min = 19_010_800
        base_prob_max = 19_010_800
        base_rare_max = 19_010_800
        alerte = f"JACKPOT Stratum Tectonicas probable ({_formater_credits_vocaux(19_010_800 * mult)})"
        if nb_bio >= 2 and any(k in at for k in ("co2", "carbon", "ammonia", "water", "oxygen", "sulphur")):
            candidats.append("Aleoida, Tussock ou Bacterium")
    elif "rocky ice" in pc or "icy body" in pc:
        if nb_bio == 1:
            # Avec 1 seul signal sur un corps glacé, c'est très majoritairement du Bacterium (1 à 2 M base)
            candidats.append("Bacterium (le plus probable)")
            base_prob_min = 1_000_000
            base_prob_max = 1_949_000
            if "neon" in at or "oxygen" in at:
                candidats.append("Fonticulua (plus rare)")
                base_rare_max = 19_010_800
            elif any(k in at for k in ("argon", "nitrogen", "methane", "water")):
                candidats.append("Fonticulua ou Electricae (plus rare)")
                base_rare_max = 6_284_600
            else:
                base_rare_max = 1_949_000
        else:
            # 2+ signaux sur corps glacé : Fonticulua / Electricae deviennent nettement plus crédibles
            if "neon" in at or "oxygen" in at:
                candidats.append("Fonticulua (jusqu'à 19 millions de base)")
                candidats.append("Bacterium ou Electricae")
                base_prob_min = 2_000_000
                base_prob_max = 6_284_600
                base_rare_max = 19_010_800
            elif any(k in at for k in ("argon", "nitrogen", "methane", "water")):
                candidats.append("Fonticulua ou Electricae")
                candidats.append("Bacterium")
                base_prob_min = 1_800_000
                base_prob_max = 5_727_600
                base_rare_max = 6_284_600
            else:
                candidats.append("Bacterium")
                base_prob_min = 1_000_000
                base_prob_max = 3_897_000
                base_rare_max = 4_934_500
    elif "rocky body" in pc:
        if nb_bio == 1:
            candidats.append("Bacterium, Tussock ou Frutexa")
            base_prob_min = 1_000_000
            base_prob_max = 3_472_400
            base_rare_max = 7_774_700
        else:
            if any(k in at for k in ("water", "co2", "carbon")):
                candidats.append("Clypeus")
                base_prob_min = 3_500_000
                base_prob_max = 11_873_200
                base_rare_max = 16_202_800
            elif any(k in at for k in ("sulphur", "so2")):
                candidats.append("Recepta ou Concha")
                base_prob_min = 4_500_000
                base_prob_max = 12_934_900
                base_rare_max = 16_202_800
            else:
                candidats.append("Tussock, Frutexa, Osseus ou Cactoida")
                base_prob_min = 2_500_000
                base_prob_max = 7_774_700
                base_rare_max = 14_313_700
    else:
        candidats.append("Bacterium ou espèces variées")
        base_prob_min = 1_000_000
        base_prob_max = 3_500_000
        base_rare_max = 5_000_000

    prob_min = base_prob_min * mult
    prob_max = base_prob_max * mult
    rare_max = max(prob_max, base_rare_max * mult)

    # Formatage compact HUD (ex: '~5-10M' ou '95M')
    if prob_min == prob_max:
        fourchette_hud = _formater_millions_compact_hud(prob_max)
        fourchette_vocale = _formater_credits_vocaux(prob_max)
    else:
        m_min = _formater_millions_compact_hud(prob_min).rstrip("M")
        m_max = _formater_millions_compact_hud(prob_max)
        fourchette_hud = f"~{m_min}-{m_max}"
        fourchette_vocale = f"environ {_formater_credits_vocaux(prob_min)} à {_formater_credits_vocaux(prob_max)}"
        if rare_max >= prob_max * 2:
            fourchette_vocale += f" (exceptionnellement jusqu'à {_formater_credits_vocaux(rare_max)} si espèce rare)"

    # Formulation claire selon le nombre de signaux (1 seul signal = 'ou', jamais 'et')
    if nb_bio == 1 and len(candidats) > 1:
        genres_formates = [" ou ".join(candidats[:2])]
    else:
        genres_formates = candidats[:3]

    return {
        "genres_probables": genres_formates,
        "potentiel_estime_credits": prob_max,
        "potentiel_max_credits": rare_max,
        "potentiel_max_texte": _formater_credits_courts(prob_max),
        "fourchette_hud": fourchette_hud,
        "fourchette_vocale": fourchette_vocale,
        "alerte_jackpot": alerte
    }


def _nom_court_corps(nom_corps: str, systeme: str) -> str:
    """Raccourcit 'Synuefe PG-O c9-7 2 a' en '2 A' (MAJUSCULES, cohérent avec l'interface du jeu)."""
    if not nom_corps:
        return "Inconnu"
    if systeme and nom_corps.lower().startswith(systeme.lower()):
        reste = nom_corps[len(systeme):].strip()
        if reste:
            return reste.upper()
    return nom_corps


def analyser_systeme_fss(filtre_objectif: str = "tout", filtre_materiau: str = "") -> dict:
    """Analyse toutes les planètes scannées au FSS/DSS dans le système stellaire actuel.

    Identifie :
    - Les cibles DSS prioritaires (telluriques, aquatiques, ammoniac, terraformables non encore cartographiées)
    - Les planètes à fort potentiel biologique (avec prédiction Vista Genomics et bonus x5 1ère empreinte)
    - Les meilleures planètes pour un matériau brut précis (ou matériaux rares Grade 4)
    - Les anneaux minables intéressants (Métallique, Riche en métaux, Rocheux, Glacé) + hotspots DSS
    """
    fichiers = sorted(
        glob.glob(os.path.join(DOSSIER_JOURNAUX_ED, "Journal.*.log")),
        key=os.path.getmtime
    )
    if not fichiers:
        return {"erreur": "Aucun journal Elite Dangerous trouvé."}

    # 1. Déterminer le système actuel (dernier FSDJump / Location dans les journaux les plus récents)
    systeme_actuel = ""
    for chemin in reversed(fichiers[-5:]):
        try:
            with open(chemin, "r", encoding="utf-8", errors="ignore") as f:
                for ligne in f:
                    if '"FSDJump"' in ligne or '"Location"' in ligne:
                        try:
                            ev = json.loads(ligne)
                            if ev.get("event") in ("FSDJump", "Location") and ev.get("StarSystem"):
                                systeme_actuel = str(ev["StarSystem"])
                        except Exception:
                            continue
            if systeme_actuel:
                break
        except Exception:
            continue

    if not systeme_actuel:
        return {"erreur": "Système actuel introuvable dans les journaux récents."}

    # 2. Collecter tous les scans FSS/DSS du système actuel (sur les 5 derniers journaux, résiste aux redémarrages)
    scans = {}
    scans_etoiles = {}
    fss_signaux = {}
    saa_genres = {}
    saa_hotspots = {}
    corps_mappes_cmdr = set()
    corps_total_systeme = 0

    for chemin in fichiers[-5:]:
        sys_courant = ""
        try:
            with open(chemin, "r", encoding="utf-8", errors="ignore") as f:
                for ligne in f:
                    if not ligne or "{" not in ligne:
                        continue
                    if not any(k in ligne for k in (
                        '"FSDJump"', '"Location"', '"FSSDiscoveryScan"',
                        '"Scan"', '"FSSBodySignals"', '"SAASignalsFound"', '"SAAScanComplete"'
                    )):
                        continue
                    try:
                        ev = json.loads(ligne)
                    except Exception:
                        continue

                    etype = ev.get("event", "")
                    if etype in ("FSDJump", "Location"):
                        sys_courant = str(ev.get("StarSystem") or "")
                        continue

                    sys_ev = str(ev.get("StarSystem") or sys_courant)
                    bname = str(ev.get("BodyName") or "").strip()
                    meme_systeme = (
                        sys_ev.lower() == systeme_actuel.lower()
                        or (bname and bname.lower().startswith(systeme_actuel.lower()))
                    )
                    if not meme_systeme:
                        continue

                    if etype == "FSSDiscoveryScan":
                        corps_total_systeme = max(corps_total_systeme, int(ev.get("BodyCount", 0) or 0))
                    elif etype == "Scan" and bname:
                        if ev.get("PlanetClass"):
                            scans[bname] = ev
                        elif ev.get("StarType"):
                            scans_etoiles[bname] = ev
                    elif etype == "FSSBodySignals" and bname:
                        s_bio, s_geo = fss_signaux.get(bname, (0, 0))
                        for sig in ev.get("Signals", []):
                            st = str(sig.get("Type", "")).lower()
                            cnt = int(sig.get("Count", 0) or 0)
                            if "biological" in st:
                                s_bio = max(s_bio, cnt)
                            elif "geological" in st:
                                s_geo = max(s_geo, cnt)
                        fss_signaux[bname] = (s_bio, s_geo)
                    elif etype == "SAAScanComplete" and bname:
                        corps_mappes_cmdr.add(bname.lower())
                    elif etype == "SAASignalsFound" and bname:
                        s_bio, s_geo = fss_signaux.get(bname, (0, 0))
                        hotspots = []
                        for sig in ev.get("Signals", []):
                            st = str(sig.get("Type", "")).lower()
                            cnt = int(sig.get("Count", 0) or 0)
                            if "biological" in st:
                                s_bio = max(s_bio, cnt)
                            elif "geological" in st:
                                s_geo = max(s_geo, cnt)
                            elif "ring" in bname.lower():
                                nom_hs = sig.get("Type_Localised") or sig.get("Type") or ""
                                if nom_hs:
                                    hotspots.append(f"{nom_hs} (x{cnt})")
                        if "ring" not in bname.lower():
                            fss_signaux[bname] = (s_bio, s_geo)
                        if hotspots:
                            saa_hotspots[bname] = hotspots
                        genres = [
                            str(g.get("Genus_Localised") or g.get("Genus") or "")
                            for g in ev.get("Genuses", [])
                            if g.get("Genus_Localised") or g.get("Genus")
                        ]
                        if genres:
                            saa_genres[bname] = genres
                            corps_mappes_cmdr.add(bname.lower())
        except Exception:
            continue

    if not scans:
        return {
            "systeme": systeme_actuel,
            "nb_planetes_scannees": 0,
            "nb_corps_total": corps_total_systeme,
            "info": "Aucune planète scannée au FSS trouvée pour ce système dans tes journaux récents. Lance d'abord un scan FSS."
        }

    # Normalisation éventuelle du filtre matériau demandé par le pilote (FR ou EN)
    mat_cible_en = ""
    mat_cible_fr = ""
    if filtre_materiau:
        fm_norm = _norm(filtre_materiau)
        for en, fr in MATERIAUX_SURFACE_FR.items():
            if fm_norm == en or fm_norm == _norm(fr) or fm_norm in _norm(fr) or fm_norm in en:
                mat_cible_en = en
                mat_cible_fr = fr
                break

    cmdr = indexer_codex_commandant(forcer_complet=False)
    cibles_dss_carto = []
    cibles_biologie = []
    cibles_materiaux = []
    anneaux_minables = []

    # Bilan financier Universal Cartographics : étoiles déjà scannées
    valeur_acquis_uc = sum(_estimer_valeurs_carto_corps(e)["valeur_acquise"] for e in scans_etoiles.values())
    gain_dss_recommandes_uc = 0
    potentiel_bio_total = 0

    for bname, sc in scans.items():
        nom_court = _nom_court_corps(bname, systeme_actuel)
        pclass = str(sc.get("PlanetClass") or "")
        terraformable = str(sc.get("TerraformState") or "").lower() == "terraformable"
        atterrissable = bool(sc.get("Landable", False))
        dist_brut = float(sc.get("DistanceFromArrivalLS", 0.0) or 0.0)
        dist_sl = round(dist_brut, 1) if dist_brut < 10.0 else int(round(dist_brut))
        atmo = str(sc.get("Atmosphere_Localised") or sc.get("Atmosphere") or sc.get("AtmosphereType") or "Aucune")
        temp_k = round(float(sc["SurfaceTemperature"])) if sc.get("SurfaceTemperature") else None
        grav_g = round(float(sc["SurfaceGravity"]) / 9.80665, 2) if sc.get("SurfaceGravity") else None
        volc = str(sc.get("Volcanism_Localised") or sc.get("Volcanism") or "")

        deja_mappee_autre = bool(sc.get("WasMapped", False))
        deja_foulee_autre = bool(sc.get("WasFootfalled", False))
        deja_mappee_cmdr = bname.lower() in corps_mappes_cmdr

        # A. Valeur cartographique FSS acquise + gain DSS (Universal Cartographics)
        eval_uc = _estimer_valeurs_carto_corps(sc, deja_mappee_cmdr=deja_mappee_cmdr)
        valeur_acquis_uc += eval_uc["valeur_acquise"]
        val_dss = eval_uc["valeur_dss"]
        gain_dss_net = eval_uc["gain_dss_net"]
        lib_planete = eval_uc["libelle"]

        if terraformable or any(k in pclass.lower() for k in ("earthlike", "water world", "ammonia")):
            if not deja_mappee_cmdr:
                gain_dss_recommandes_uc += gain_dss_net
            cibles_dss_carto.append({
                "planete": nom_court,
                "nom_complet": bname,
                "type": lib_planete,
                "terraformable": terraformable,
                "distance_sl": dist_sl,
                "deja_scannee_dss_par_moi": deja_mappee_cmdr,
                "premiere_cartographie_possible": not deja_mappee_autre,
                "valeur_fss_texte": _formater_credits_courts(eval_uc["valeur_fss"]),
                "gain_dss_supplementaire_credits": gain_dss_net,
                "gain_dss_supplementaire_texte": f"+{_formater_credits_courts(gain_dss_net)}",
                "gain_dss_supplementaire_vocal": _formater_credits_vocaux(gain_dss_net),
                "valeur_dss_credits": val_dss,
                "valeur_dss_texte": _formater_credits_courts(val_dss),
                "valeur_dss_vocal": _formater_credits_vocaux(val_dss)
            })

        # B. Signaux biologiques & prédiction Vista Genomics
        nb_bio, nb_geo = fss_signaux.get(bname, (0, 0))
        if nb_bio > 0 and atterrissable:
            genres_connus = saa_genres.get(bname, [])
            pred = _predire_exobiologie_fss(pclass, atmo, temp_k, grav_g, nb_bio, not deja_foulee_autre)
            potentiel_bio_total += pred["potentiel_estime_credits"]

            # Vérifie si des genres connus (après DSS) sont nouveaux pour le CMDR
            genres_nouveaux = []
            for g in genres_connus:
                gn = _norm(g)
                ga = _norm(ALIAS_GENRES_FR.get(gn, g))
                if not _trouver_rencontre_cmdr(cmdr.get("genres_bio_vus", {}), [gn, ga]):
                    genres_nouveaux.append(g)

            cibles_biologie.append({
                "planete": nom_court,
                "nom_complet": bname,
                "type": lib_planete,
                "distance_sl": dist_sl,
                "signaux_biologiques": nb_bio,
                "signaux_geologiques": nb_geo,
                "note_nb_signaux": (
                    "1 seul signal biologique : une seule espèce présente parmi les candidats (dire 'soit... soit...', jamais 'et')."
                    if nb_bio == 1 else f"{nb_bio} signaux biologiques distincts."
                ),
                "atmosphere": atmo,
                "temperature_k": temp_k,
                "gravite_g": grav_g,
                "deja_scannee_dss_par_moi": deja_mappee_cmdr,
                "premiere_empreinte_x5_possible": not deja_foulee_autre,
                "genres_confirmes_dss": genres_connus,
                "genres_nouveaux_pour_moi": genres_nouveaux,
                "prediction_fss": pred["genres_probables"] if not genres_connus else [],
                "potentiel_estime_credits": pred["potentiel_estime_credits"],
                "potentiel_max_credits": pred["potentiel_max_credits"],
                "potentiel_max_texte": pred["potentiel_max_texte"],
                "fourchette_hud": pred["fourchette_hud"],
                "estimation_vocale": pred["fourchette_vocale"],
                "alerte_jackpot": pred["alerte_jackpot"]
            })

        # C. Matériaux de surface (planètes atterrissables)
        mats = sc.get("Materials") or []
        if atterrissable and mats:
            if mat_cible_en:
                for m in mats:
                    mn = str(m.get("Name", "")).lower()
                    if mn == mat_cible_en:
                        pct = round(float(m.get("Percent", 0.0) or 0.0), 2)
                        cibles_materiaux.append({
                            "planete": nom_court,
                            "materiau": mat_cible_fr,
                            "pourcentage": pct,
                            "distance_sl": dist_sl,
                            "gravite_g": grav_g,
                            "volcanisme": bool(volc)
                        })
            else:
                rares_trouves = []
                for m in mats:
                    mn = str(m.get("Name", "")).lower()
                    if mn in MATERIAUX_RARES_G4:
                        pct = round(float(m.get("Percent", 0.0) or 0.0), 2)
                        rares_trouves.append((pct, MATERIAUX_SURFACE_FR.get(mn, mn)))
                if rares_trouves:
                    rares_trouves.sort(reverse=True)
                    cibles_materiaux.append({
                        "planete": nom_court,
                        "materiaux_rares": [f"{nom} ({pct}%)" for pct, nom in rares_trouves[:3]],
                        "meilleur_nom": rares_trouves[0][1],
                        "meilleur_pct": rares_trouves[0][0],
                        "distance_sl": dist_sl,
                        "volcanisme": bool(volc)
                    })

        # D. Anneaux minables
        rings = sc.get("Rings") or []
        reserve = str(sc.get("ReserveLevel") or "").replace("Resources", "").strip()
        for r in rings:
            rclass = str(r.get("RingClass") or "")
            rname = str(r.get("Name") or "")
            if rclass in CLASSES_ANNEAUX_INFO:
                type_fr, minerais_cles = CLASSES_ANNEAUX_INFO[rclass]
                anneaux_minables.append({
                    "planete": nom_court,
                    "anneau": _nom_court_corps(rname, systeme_actuel),
                    "type_anneau": type_fr,
                    "reserves": reserve or "Inconnues",
                    "minerais_potentiels": minerais_cles,
                    "distance_sl": dist_sl,
                    "hotspots_dss": saa_hotspots.get(rname, [])
                })

    # Tris par intérêt décroissant puis distance croissante (cohérent avec Carte Système / Navigation)
    cibles_dss_carto.sort(
        key=lambda x: (not x["deja_scannee_dss_par_moi"], x["valeur_dss_credits"], -x["distance_sl"]),
        reverse=True
    )
    cibles_biologie.sort(
        key=lambda x: (
            not x["deja_scannee_dss_par_moi"],
            x["potentiel_estime_credits"],
            x["signaux_biologiques"],
            -x["distance_sl"]
        ),
        reverse=True
    )
    if mat_cible_en:
        cibles_materiaux.sort(key=lambda x: (x["pourcentage"], -x["distance_sl"]), reverse=True)
    else:
        cibles_materiaux.sort(key=lambda x: (len(x["materiaux_rares"]), x["meilleur_pct"], -x["distance_sl"]), reverse=True)

    ordre_anneaux = {"Métallique": 4, "Riche en métaux": 3, "Glacé": 2, "Rocheux": 1}
    anneaux_minables.sort(key=lambda x: (ordre_anneaux.get(x["type_anneau"], 0), -x["distance_sl"]), reverse=True)

    total_potentiel = valeur_acquis_uc + gain_dss_recommandes_uc + potentiel_bio_total
    resultat = {
        "systeme": systeme_actuel,
        "nb_planetes_scannees_fss": len(scans),
        "nb_etoiles_scannees": len(scans_etoiles),
        "nb_corps_total_systeme": corps_total_systeme,
        "objectif": filtre_objectif,
        "materiau_recherche": mat_cible_fr or filtre_materiau,
        "bilan_financier": {
            "deja_acquis_carto_credits": valeur_acquis_uc,
            "deja_acquis_carto_texte": _formater_credits_courts(valeur_acquis_uc),
            "deja_acquis_carto_vocal": _formater_credits_vocaux(valeur_acquis_uc),
            "gain_dss_recommandes_credits": gain_dss_recommandes_uc,
            "gain_dss_recommandes_texte": f"+{_formater_credits_courts(gain_dss_recommandes_uc)}",
            "gain_dss_recommandes_vocal": _formater_credits_vocaux(gain_dss_recommandes_uc),
            "potentiel_exobiologie_systeme_credits": potentiel_bio_total,
            "potentiel_exobiologie_systeme_vocal": _formater_credits_vocaux(potentiel_bio_total),
            "total_potentiel_systeme_credits": total_potentiel,
            "total_potentiel_systeme_vocal": _formater_credits_vocaux(total_potentiel)
        },
        "cibles_dss_cartographie": cibles_dss_carto[:5],
        "cibles_exobiologie": cibles_biologie[:5],
        "cibles_materiaux_surface": cibles_materiaux[:4],
        "anneaux_minables": anneaux_minables[:4]
    }
    return resultat


def _trouver_prix_espece_exobio(nom_espece: str, nom_genre: str = "") -> int:
    """Retourne le prix Vista Genomics de base (en Crédits) d'une espèce biologique Odyssey."""
    codex = charger_codex_ed()
    exobio = codex.get("exobiologie", EXOBIOLOGIE_DEFAUT)
    esp_norm = _norm(nom_espece)
    # Remplace un éventuel préfixe FR ("touradon cultro" -> "tussock cultro")
    mots = esp_norm.split()
    if mots and mots[0] in ALIAS_GENRES_FR:
        esp_canon = _norm(ALIAS_GENRES_FR[mots[0]]) + (" " + " ".join(mots[1:]) if len(mots) > 1 else "")
    else:
        esp_canon = esp_norm

    for genre_cle, data_g in exobio.items():
        for nom_e, prix in (data_g.get("especes") or {}).items():
            ne_norm = _norm(nom_e)
            if ne_norm == esp_canon or ne_norm == esp_norm or (len(mots) >= 2 and mots[-1] in ne_norm and _norm(genre_cle) in esp_canon):
                return int(prix)

    # Fallback : moyenne du genre si espèce inconnue
    g_canon = ALIAS_GENRES_FR.get(_norm(nom_genre), nom_genre)
    for genre_cle, data_g in exobio.items():
        if _norm(genre_cle) == _norm(g_canon):
            vals = list((data_g.get("especes") or {}).values())
            if vals:
                return int(round(sum(vals) / len(vals)))
    return 1_000_000


def calculer_portefeuille_exploration(nb_journaux: int = 20) -> dict:
    """Calcule la valeur estimée des données d'exploration NON VENDUES actuellement à bord.

    Prend en compte :
    - Universal Cartographics (Scans FSS + cartographies DSS) depuis la dernière vente ou mort
    - Vista Genomics (Exobiologie : prélèvements 'Analyse' complets x5 si 1ère empreinte)
    - Bons Codex (Géologie / Biologie / Astronomie : VoucherAmount) depuis le dernier encaissement
    """
    fichiers = sorted(
        glob.glob(os.path.join(DOSSIER_JOURNAUX_ED, "Journal.*.log")),
        key=os.path.getmtime
    )
    if not fichiers:
        return {"erreur": "Aucun journal Elite Dangerous trouvé."}

    scans_non_vendus = {}          # cle (systeme, corps) -> event Scan
    dss_non_vendus = set()         # cle (systeme, corps)
    footfall_par_corps = {}        # cle (systeme, corps) -> WasFootfalled (bool)
    footfall_par_body_id = {}      # cle (systeme, str(BodyID)) -> WasFootfalled (bool)
    exo_completes = []             # liste d'espèces finalisées ('Analyse') non vendues
    exo_en_cours = {}              # cle (systeme, corps, espece) -> nb échantillons (1 ou 2)
    bons_codex_geo = 0
    bons_codex_bio = 0
    bons_codex_astro = 0
    nb_codex_non_encaisses = 0
    derniere_raz_carto = "Aucune vente/mort récente dans les journaux scannés"
    derniere_raz_exo = "Aucune vente/mort récente dans les journaux scannés"

    for chemin in fichiers[-nb_journaux:]:
        sys_courant = ""
        est_docke = False
        try:
            with open(chemin, "r", encoding="utf-8", errors="ignore") as f:
                for ligne in f:
                    if not ligne or "{" not in ligne:
                        continue
                    if not any(k in ligne for k in (
                        '"FSDJump"', '"Location"', '"Docked"', '"Undocked"', '"Resurrect"',
                        '"Scan"', '"SAAScanComplete"',
                        '"SellExplorationData"', '"MultiSellExplorationData"',
                        '"ScanOrganic"', '"SellOrganicData"',
                        '"CodexEntry"', '"RedeemVoucher"', '"Died"'
                    )):
                        continue
                    try:
                        ev = json.loads(ligne)
                    except Exception:
                        continue

                    etype = ev.get("event", "")
                    ts_court = str(ev.get("timestamp") or "")[:16].replace("T", " ")

                    if etype == "FSDJump":
                        est_docke = False
                        if ev.get("StarSystem"):
                            sys_courant = str(ev["StarSystem"])
                    elif etype == "Location":
                        est_docke = bool(ev.get("Docked", False))
                        if ev.get("StarSystem"):
                            sys_courant = str(ev["StarSystem"])
                    elif etype == "Docked":
                        est_docke = True
                    elif etype == "Undocked":
                        est_docke = False

                    elif etype == "Scan":
                        scan_type = str(ev.get("ScanType") or "")
                        # Ignore les scans de balise de navigation (0 Cr) et les AutoScan passifs dans le hangar
                        if scan_type == "NavBeaconDetail" or (est_docke and scan_type == "AutoScan"):
                            continue
                        bname = str(ev.get("BodyName") or "").strip()
                        if bname:
                            sys_ev = str(ev.get("StarSystem") or sys_courant)
                            cle = (sys_ev.lower(), bname.lower())
                            scans_non_vendus[cle] = ev
                            if "WasFootfalled" in ev:
                                was_ff = bool(ev.get("WasFootfalled"))
                                footfall_par_corps[cle] = was_ff
                                if ev.get("BodyID") is not None:
                                    footfall_par_body_id[(sys_ev.lower(), str(ev.get("BodyID")))] = was_ff

                    elif etype == "SAAScanComplete":
                        bname = str(ev.get("BodyName") or "").strip()
                        if bname:
                            cle = (sys_courant.lower(), bname.lower())
                            dss_non_vendus.add(cle)

                    elif etype in ("SellExplorationData", "MultiSellExplorationData"):
                        scans_non_vendus.clear()
                        dss_non_vendus.clear()
                        derniere_raz_carto = f"Vente Universal Cartographics ({ts_court})"

                    elif etype == "ScanOrganic":
                        stype = str(ev.get("ScanType") or "")
                        genre = str(ev.get("Genus_Localised") or ev.get("Genus") or "").strip()
                        espece = str(ev.get("Species_Localised") or ev.get("Species") or "").strip()
                        body_id = str(ev.get("Body") or "")
                        cle_exo = (sys_courant.lower(), body_id, _norm(espece))

                        if stype == "Analyse":
                            exo_en_cours.pop(cle_exo, None)
                            prix_base = _trouver_prix_espece_exobio(espece, genre)
                            # Vérifie prioritairement le WasFootfalled exact du BodyID concerné (évite de confondre planète et lune !)
                            cle_bid = (sys_courant.lower(), body_id)
                            if body_id and cle_bid in footfall_par_body_id:
                                vierge = (footfall_par_body_id[cle_bid] is False)
                            else:
                                vierge = False
                                for (s_k, _b_k), was_ff in footfall_par_corps.items():
                                    if s_k == sys_courant.lower() and was_ff is False:
                                        vierge = True
                                        break
                            mult = 5 if vierge else 1
                            exo_completes.append({
                                "espece": espece or genre or "Inconnue",
                                "systeme": sys_courant,
                                "prix_base": prix_base,
                                "bonus_x5": vierge,
                                "valeur_estimee": prix_base * mult
                            })
                        elif stype in ("Log", "Sample"):
                            exo_en_cours[cle_exo] = exo_en_cours.get(cle_exo, 0) + 1

                    elif etype == "SellOrganicData":
                        exo_completes.clear()
                        exo_en_cours.clear()
                        derniere_raz_exo = f"Vente Vista Genomics ({ts_court})"

                    elif etype == "CodexEntry":
                        montant = int(ev.get("VoucherAmount", 0) or 0)
                        if montant > 0:
                            nb_codex_non_encaisses += 1
                            cat = str(ev.get("Category") or "").lower()
                            sub = str(ev.get("SubCategory") or "").lower()
                            if "geolog" in sub or "geolog" in cat:
                                bons_codex_geo += montant
                            elif "biology" in cat or "organic" in sub:
                                bons_codex_bio += montant
                            else:
                                bons_codex_astro += montant

                    elif etype == "RedeemVoucher":
                        vtype = str(ev.get("Type") or "").lower()
                        if vtype == "codex":
                            bons_codex_geo = 0
                            bons_codex_bio = 0
                            bons_codex_astro = 0
                            nb_codex_non_encaisses = 0

                    elif etype == "Died":
                        # La destruction du vaisseau fait perdre les données carto & exobio non vendues
                        scans_non_vendus.clear()
                        dss_non_vendus.clear()
                        exo_completes.clear()
                        exo_en_cours.clear()
                        derniere_raz_carto = f"Destruction du vaisseau ({ts_court})"
                        derniere_raz_exo = f"Destruction du vaisseau ({ts_court})"
        except Exception:
            continue

    # Calcul des totaux
    total_carto = 0
    nb_systemes_carto = set()
    nb_dss_faits = 0
    for cle, sc in scans_non_vendus.items():
        nb_systemes_carto.add(cle[0])
        est_mappe = cle in dss_non_vendus
        if est_mappe:
            nb_dss_faits += 1
        total_carto += _estimer_valeurs_carto_corps(sc, deja_mappee_cmdr=est_mappe)["valeur_acquise"]

    total_exo = sum(e["valeur_estimee"] for e in exo_completes)
    total_codex = bons_codex_geo + bons_codex_bio + bons_codex_astro
    total_general = total_carto + total_exo + total_codex

    return {
        "cartographie_universal_cartographics": {
            "credits_estimes": total_carto,
            "texte": _formater_credits_courts(total_carto),
            "vocal": _formater_credits_vocaux(total_carto),
            "nb_corps_scannes": len(scans_non_vendus),
            "nb_dss_complets": nb_dss_faits,
            "nb_systemes": len(nb_systemes_carto),
            "depuis": derniere_raz_carto
        },
        "exobiologie_vista_genomics": {
            "credits_estimes": total_exo,
            "texte": _formater_credits_courts(total_exo),
            "vocal": _formater_credits_vocaux(total_exo),
            "nb_especes_pretes": len(exo_completes),
            "nb_especes_en_cours": len(exo_en_cours),
            "details": exo_completes[-5:],
            "depuis": derniere_raz_exo
        },
        "bons_codex": {
            "total_credits": total_codex,
            "texte": _formater_credits_courts(total_codex),
            "vocal": _formater_credits_vocaux(total_codex),
            "geologie_credits": bons_codex_geo,
            "biologie_credits": bons_codex_bio,
            "astronomie_credits": bons_codex_astro,
            "nb_entrees": nb_codex_non_encaisses
        },
        "total_general_credits": total_general,
        "total_general_texte": _formater_credits_courts(total_general),
        "total_general_vocal": _formater_credits_vocaux(total_general)
    }


# ==============================================================================
# MODE TEST AUTONOME (py -m modules.codex_ed)
# ==============================================================================
if __name__ == "__main__":
    print("=== TEST AUTONOME DU MODULE CODEX LOCAL OSCAR ===")
    codex = charger_codex_ed()
    print(f"[Codex ED] {len(codex['exobiologie'])} genres bio, {len(codex['geologie'])} types géo, {len(codex['nebuleuses_pois'])} nébuleuses/POIs.")
    ok, msg = synchroniser_nebuleuses_edsm(forcer=False)
    print(f"[Synchro EDSM] {msg}")
    cmdr = indexer_codex_commandant(forcer_complet=True)
    print(
        f"[Codex CMDR] {len(cmdr['fichiers_indexes'])} journaux scannés -> "
        f"{len(cmdr['biologie_vue'])} bio, {len(cmdr['geologie_vue'])} géo, {len(cmdr['astronomie_vue'])} astro."
    )
    if cmdr["biologie_vue"]:
        print("  Exemples bio vues :", list(cmdr["biologie_vue"].keys())[:5])
    if cmdr["geologie_vue"]:
        print("  Exemples géo vues :", list(cmdr["geologie_vue"].keys())[:5])
