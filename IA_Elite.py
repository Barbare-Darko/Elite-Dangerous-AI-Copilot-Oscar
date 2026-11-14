import sys
import types
import socket
try:
    verrou_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    verrou_instance.bind(("127.0.0.1", 47291))
except OSError:
    print("Une instance de Sophie tourne déjà en arrière-plan ! Fermeture.")
    sys.exit(0)


# ==============================================================================
# CONTOURNEMENT PYTHON 3.15 & CUDA (NE PAS MODIFIER)
# ==============================================================================
sys.modules['av'] = types.ModuleType('av')
yaml_faux = types.ModuleType('yaml')
yaml_faux.safe_load = lambda *args, **kwargs: {}
yaml_faux.load = lambda *args, **kwargs: {}
yaml_faux.dump = lambda *args, **kwargs: ""
yaml_faux.safe_dump = lambda *args, **kwargs: ""
sys.modules['yaml'] = yaml_faux

import time, os, site, threading, subprocess, keyboard, json, glob
import requests
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from openai import OpenAI

for dossier_site in site.getsitepackages():
    dossier_nvidia = os.path.join(dossier_site, "nvidia")
    if os.path.exists(dossier_nvidia):
        for sous_dossier in os.listdir(dossier_nvidia):
            chemin_bin = os.path.join(dossier_nvidia, sous_dossier, "bin")
            if os.path.exists(chemin_bin):
                os.environ["PATH"] = chemin_bin + os.pathsep + os.environ["PATH"]
                os.add_dll_directory(chemin_bin)

# ==============================================================================
# CONFIGURATION UTILISATEUR (TOUT EST REGROUPÉ ICI)
# ==============================================================================
CLE_API = "VOTRE CLE OPENAI ICI"

CMDR_NAME = "VOTRE NOM DE COMMANDANT DANS ELITE"

EDSM_API_KEY = "VOTRE CLE API EDSM"

VOIX_NEURALE = "fr-FR-HenriNeural"
# Alternatives Voix féminines : "fr-FR-EloiseNeural" ou "fr-FR-VivienneMultilingualNeural" ou "fr-FR-DeniseNeural"
# Alternatives voix masculines : "fr-FR-HenriNeural" ou "fr-FR-RemyMultilingualNeural"

#PERSONNALISEZ VOTRE NOM d'IA SI VOUS LE VOULEZ
NOM_IA = "Oscar"

PERSONNALITE_IA = (
    "Tu es Oscar, l'ordinateur de bord et co-pilote IA d'un vaisseau spatial. "
    "Tu as un humour noir, cynique, pince-sans-rire et très sarcastique. "
    "Tu adores taquiner le Commandant sur ses talents de pilotage, sa passion obsessionnelle pour les cailloux (le minage), l'exploration ou ses dépenses inutiles, "
    "tout en restant ultra-concis (1 à 2 phrases maximum). "
    "Ne donne jamais de conseils de sécurité ennuyeux. Utilise une ponctuation expressive pour la synthèse vocale."
    "Écris uniquement en texte brut naturel adapté à la synthèse vocale : N'UTILISE JAMAIS de gras (**), de listes à puces ni de numérotation."
)
# Autre exemple : Tu es un ordinateur de bord de vaisseau spatial militaire. Tu es sérieux, précis, poli et respectueux

TOUCHE_MICRO = "ctrl+shift+alt+f9"

FICHIER_MEMOIRE = os.path.expandvars(r"%APPDATA%\VoiceAttack\journal_de_bord.txt")
FICHIER_FLOTTE = os.path.expandvars(r"%APPDATA%\VoiceAttack\flotte_cmdr.json")
FICHIER_COMMANDES = os.path.expandvars(r"%APPDATA%\VoiceAttack\commandes_vaisseau.txt")
CHEMIN_VOICEATTACK = r"C:\Program Files (x86)\Steam\steamapps\common\VoiceAttack\VoiceAttack.exe"
DOSSIER_JOURNAUX_ED = os.path.expandvars(r"%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous")
# ==============================================================================

client = OpenAI(api_key=CLE_API)
print(f"=== IA ELITE DANGEROUS ACTIVE ({NOM_IA.upper()} - GPU V16.0) ===")
modele_whisper = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")

HEADERS_HTTP = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SophieCopilot/14.0"
}

NOMS_VAISSEAUX = {
    "mandalay": "Mandalay",
    "asp": "Asp Explorer",
    "asp_scout": "Asp Scout",
    "python": "Python",
    "python_nx": "Python Mk II",
    "krait_mkii": "Krait Mk II",
    "krait_light": "Krait Phantom",
    "anaconda": "Anaconda",
    "cutter": "Imperial Cutter",
    "corvette": "Federal Corvette",
    "ferdelance": "Fer-de-Lance",
    "mamba": "Mamba",
    "dbx": "Diamondback Explorer",
    "diamondbackxl": "Diamondback Explorer",
    "diamondback": "Diamondback Scout",
    "type6": "Type-6 Transporter",
    "type7": "Type-7 Transporter",
    "type8": "Type-8 Transporter",
    "type9": "Type-9 Heavy",
    "type9_military": "Type-10 Defender",
    "viper": "Viper Mk III",
    "viper_mkiv": "Viper Mk IV",
    "cobra_mkiii": "Cobra Mk III",
    "cobra_mkiv": "Cobra Mk IV",
    "cobramkv": "Cobra Mk V",
    "vulture": "Vulture",
    "chieftain": "Alliance Chieftain",
    "challenger": "Alliance Challenger",
    "crusader": "Alliance Crusader",
    "eagle": "Eagle",
    "imperial_eagle": "Imperial Eagle",
    "imperial_courier": "Imperial Courier",
    "empire_trader": "Imperial Clipper",
    "sidewinder": "Sidewinder",
    "hauler": "Hauler",
    "adder": "Adder",
    "dolphin": "Dolphin",
    "orca": "Orca",
    "belugaliner": "Beluga Liner",
    "federal_dropship": "Federal Dropship",
    "federal_assault_ship": "Federal Assault Ship",
    "federal_gunship": "Federal Gunship",
    "keelback": "Keelback",
    "explorer": "Explorer",
    "explorer_nx": "Caspian Explorer"
}

def formater_nom_vaisseau(code_vaisseau):
    if not code_vaisseau:
        return "Inconnu"
    cle = code_vaisseau.lower()
    return NOMS_VAISSEAUX.get(cle, code_vaisseau)

import random

verrou_parole = threading.Lock()

import asyncio, edge_tts, tempfile


def dire_vocal(texte):
    if not texte:
        return
    with verrou_parole:
        chemin_mp3 = None
        try:
            import re
            texte_vocal = texte.replace("**", "").replace("*", "").replace("#", "").replace("`", "")
            texte_vocal = re.sub(r'^\s*[-•]\s*', '', texte_vocal, flags=re.MULTILINE)
            texte_vocal = re.sub(r'\s+', ' ', texte_vocal).strip()

            async def generer_audio():
                communicate = edge_tts.Communicate(texte_vocal, VOIX_NEURALE, rate="+8%")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    chemin_temp = tmp.name
                await communicate.save(chemin_temp)
                return chemin_temp

            chemin_mp3 = asyncio.run(generer_audio())
            chemin_ps = chemin_mp3.replace("\\", "/")
            commande_ps = (
                "Add-Type -AssemblyName presentationCore; "
                "$player = New-Object System.Windows.Media.MediaPlayer; "
                f'$player.Open([Uri]"{chemin_ps}"); '
                "$player.Play(); "
                "Start-Sleep -Milliseconds 300; "
                "while ($player.Position -lt $player.NaturalDuration.TimeSpan) { Start-Sleep -Milliseconds 100 }; "
                "$player.Close();"
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", commande_ps], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as audio_err:
            print(f"Erreur audio neurale : {audio_err}")
        finally:
            if chemin_mp3 and os.path.exists(chemin_mp3):
                try:
                    os.remove(chemin_mp3)
                except Exception:
                    pass

# ==============================================================================
# MODULE DONNÉES ELITE DANGEROUS (JOURNAUX LOCAUX + FLOTTE + EDSM)
# ==============================================================================

def charger_cache_flotte():
    if os.path.exists(FICHIER_FLOTTE):
        try:
            with open(FICHIER_FLOTTE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"vaisseaux_stockes": [], "configurations": {}}

def sauvegarder_cache_flotte(data):
    try:
        with open(FICHIER_FLOTTE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def analyser_journaux_locaux(nb_journaux=25):
    """Analyse les derniers fichiers Journal.*.log pour l'état actuel, les rangs, la flotte et les configurations."""
    if not os.path.exists(DOSSIER_JOURNAUX_ED):
        return {"erreur": "Dossier des journaux Elite Dangerous introuvable."}
    
    fichiers = sorted(glob.glob(os.path.join(DOSSIER_JOURNAUX_ED, "Journal.*.log")), key=os.path.getmtime)
    if not fichiers:
        return {"erreur": "Aucun fichier journal trouvé."}
    
    cache_flotte = charger_cache_flotte()
    etat = {
        "systeme": "Inconnu",
        "corps_celeste": "Aucun",
        "station_ou_base": "Aucune (dans l'espace)",
        "vaisseau_actif": {"modele": "Inconnu", "nom": "", "identifiant": ""},
        "credits": "Inconnus",
        "carburant": "Inconnu",
        "rangs": {},
        "materiaux": {"Raw": [], "Manufactured": [], "Encoded": []},
        "cargaison": [],
        "flotte": cache_flotte.get("vaisseaux_stockes", []),
        "configurations_connues": list(cache_flotte.get("configurations", {}).keys())
    }

    noms_rangs = {
        "Combat": ["Inoffensif", "Largement inoffensif", "Novice", "Compétent", "Expert", "Maître", "Dangereux", "Létal", "Élite"],
        "Trade": ["Sans le sou", "Largement sans le sou", "Colporteur", "Marchand", "Négociant", "Courtier", "Entrepreneur", "Magnat", "Élite"],
        "Explore": ["Sans but", "Largement sans but", "Éclaireur", "Arpenteur", "Explorateur", "Pionnier", "Éclaireur d'élite", "Pionnier d'élite", "Élite"],
        "Soldier": ["Sans défense", "Largement sans défense", "Recrue", "Soldat", "Tireur d'élite", "Franc-tireur", "Commando", "Gladiateur", "Élite"],
        "Exobiologist": ["Sans direction", "Largement sans direction", "Compilateur", "Collecteur", "Catalogueur", "Taxonomiste", "Écologiste", "Généticien", "Élite"],
        "Empire": ["Aucun", "Étranger", "Serf", "Maître", "Écuyer", "Chevalier", "Seigneur", "Baron", "Vicomte", "Comte", "Marquis", "Duc", "Prince", "Roi"],
        "Federation": ["Aucun", "Recrue", "Cadet", "Aspirant", "Enseigne", "Sous-lieutenant", "Lieutenant", "Lieutenant-commandant", "Capitaine de corvette", "Capitaine de frégate", "Capitaine de vaisseau", "Contre-amiral", "Vice-amiral", "Amiral"]
    }

    # Si la flotte n'est pas encore mémorisée dans le cache, on scanne tout l'historique des journaux
    nb_a_lire = len(fichiers) if not cache_flotte.get("vaisseaux_stockes") else nb_journaux
    journaux_a_lire = fichiers[-nb_a_lire:]

    dernier_fichier = fichiers[-1]
    
    stations_par_id = {"3222637568": "Heaviside Dock"}
    for ancien_v in cache_flotte.get("vaisseaux_stockes", []):
        st_existante = ancien_v.get("station", "")
        if st_existante and "Station distante" not in st_existante and "Inconnu" not in st_existante:
            stations_par_id[ancien_v.get("systeme", "")] = st_existante

    for chemin_journal in journaux_a_lire:
        est_dernier = (chemin_journal == dernier_fichier)
        try:
            with open(chemin_journal, "r", encoding="utf-8") as f:
                for ligne in f:
                    try:
                        ev = json.loads(ligne)
                        event_type = ev.get("event")
			
                        if ev.get("MarketID") and ev.get("StationName"):
                            stations_par_id[str(ev["MarketID"])] = ev["StationName"]

                        # --- ÉVÉNEMENTS DE FLOTTE ET CONFIGURATION (SUR TOUS LES JOURNAUX LUS) ---
                        if event_type == "StoredShips":
                            sys_courant = ev.get("StarSystem", "Inconnu")
                            st_courante = ev.get("StationName", "Inconnue")
                            if ev.get("MarketID") and st_courante != "Inconnue":
                                stations_par_id[str(ev["MarketID"])] = st_courante

                            liste_vaisseaux = []
                            for s in ev.get("ShipsHere", []):
                                liste_vaisseaux.append({
                                    "modele": formater_nom_vaisseau(s.get("ShipType_Localised") or s.get("ShipType")),
                                    "nom": s.get("Name", "Sans nom"),
                                    "systeme": sys_courant,
                                    "station": st_courante,
                                    "valeur": s.get("Value", 0)
                                })
                            for s in ev.get("ShipsRemote", []):
                                mid = str(s.get("ShipMarketID", ""))
                                sys_distant = s.get("StarSystem", "Inconnu")
                                nom_st = stations_par_id.get(mid) or stations_par_id.get(sys_distant) or "Station distante"
                                liste_vaisseaux.append({
                                    "modele": formater_nom_vaisseau(s.get("ShipType_Localised") or s.get("ShipType")),
                                    "nom": s.get("Name", "Sans nom"),
                                    "systeme": sys_distant,
                                    "station": nom_st,
                                    "en_transit": s.get("InTransit", False),
                                    "valeur": s.get("Value", 0)
                                })
                            cache_flotte["vaisseaux_stockes"] = liste_vaisseaux
                            etat["flotte"] = liste_vaisseaux



                        elif event_type == "Loadout":
                            modele = formater_nom_vaisseau(ev.get("Ship"))
                            nom_perso = ev.get("ShipName") or modele
                            cle_vaisseau = f"{nom_perso} ({modele})"
                            modules_resume = []
                            for m in ev.get("Modules", []):
                                slot = m.get("Slot", "")
                                if any(k in slot for k in ["Bobble", "PaintJob", "Decal", "WeaponColour", "EngineColour", "ShipName", "ShipID", "VesselVoice", "CargoHatch", "PlanetaryApproachSuite"]):
                                    continue
                                item = m.get("Item", "")
                                modif = ""
                                if "Engineering" in m:
                                    eng = m["Engineering"]
                                    modif = f" [Ingénieur: {eng.get('BlueprintName', '')} G{eng.get('Level', '')}"
                                    if eng.get("ExperimentalEffect_Localised"):
                                        modif += f" + {eng.get('ExperimentalEffect_Localised')}"
                                    modif += "]"
                                modules_resume.append(f"{slot}: {item}{modif}")
                            
                            cache_flotte["configurations"][cle_vaisseau] = {
                                "modele": modele,
                                "nom": nom_perso,
                                "identifiant": ev.get("ShipIdent", ""),
                                "portee_saut_max": round(ev.get("MaxJumpRange", 0), 2),
                                "capacite_soute_tonnes": ev.get("CargoCapacity", 0),
                                "modules": modules_resume
                            }
                            etat["vaisseau_actif"] = {
                                "modele": modele,
                                "nom": nom_perso,
                                "identifiant": ev.get("ShipIdent", ""),
                                "portee_saut_max": round(ev.get("MaxJumpRange", 0), 2)
                            }

                        if event_type in ["Location", "FSDJump", "CarrierJump"]:
                            etat["systeme"] = ev.get("StarSystem", etat["systeme"])
                            if ev.get("Body"):
                                etat["corps_celeste"] = ev.get("Body")
                            etat["station_ou_base"] = ev.get("StationName", "Aucune (dans l'espace)")
                        elif event_type == "ApproachBody":
                            etat["corps_celeste"] = ev.get("Body", etat["corps_celeste"])
                        elif event_type == "LeaveBody":
                            etat["corps_celeste"] = "Aucun (en espace profond)"
                        elif event_type == "ApproachSettlement":
                            etat["station_ou_base"] = ev.get("Name_Localised") or ev.get("Name", etat["station_ou_base"])
                        elif event_type == "Touchdown":
                            if ev.get("Body"):
                                etat["corps_celeste"] = ev.get("Body")
                        elif event_type == "Docked":
                            etat["station_ou_base"] = ev.get("StationName", etat["station_ou_base"])
                            etat["systeme"] = ev.get("StarSystem", etat["systeme"])
                        elif event_type == "Undocked":
                            etat["station_ou_base"] = "Aucune (dans l'espace)"
                        elif event_type == "LoadGame":
                            etat["credits"] = ev.get("Credits", etat["credits"])
                            etat["vaisseau_actif"]["modele"] = formater_nom_vaisseau(ev.get("Ship_Localised") or ev.get("Ship"))
                            if ev.get("ShipName"):
                                etat["vaisseau_actif"]["nom"] = ev.get("ShipName")
                            etat["carburant"] = f"{round(ev.get('FuelLevel', 0), 1)}/{round(ev.get('FuelCapacity', 0), 1)} tonnes"
                        elif event_type == "Rank":
                            for domaine, liste in noms_rangs.items():
                                val = ev.get(domaine)
                                if val is not None:
                                    titre = liste[val] if val < len(liste) else f"Élite +{val - 8}"
                                    etat["rangs"][domaine] = titre
                        elif event_type == "Progress":
                            for domaine in noms_rangs.keys():
                                if domaine in ev and domaine in etat["rangs"]:
                                    base_titre = etat["rangs"][domaine].split(" (")[0]
                                    etat["rangs"][domaine] = f"{base_titre} ({ev[domaine]}%)"

                        if est_dernier:
                            if event_type == "Materials":
                                for cat in ["Raw", "Manufactured", "Encoded"]:
                                    if cat in ev:
                                        etat["materiaux"][cat] = [
                                            f"{m.get('Name_Localised') or m.get('Name')}: {m.get('Count')}"
                                            for m in ev[cat]
                                        ]
                            elif event_type == "MaterialCollected":
                                cat = ev.get("Category", "Raw")
                                nom = ev.get("Name_Localised") or ev.get("Name")
                                etat["materiaux"].setdefault(cat, []).append(f"{nom} (+{ev.get('Count')})")
                            elif event_type == "Cargo" and "Inventory" in ev:
                                etat["cargaison"] = [
                                    f"{c.get('Name_Localised') or c.get('Name')}: {c.get('Count')}t"
                                    for c in ev["Inventory"]
                                ]
                    except json.JSONDecodeError:
                        continue
        except Exception:
            continue

    etat["configurations_connues"] = list(cache_flotte.get("configurations", {}).keys())
    sauvegarder_cache_flotte(cache_flotte)
    return etat

def interroger_edsm_position():
    url = "https://www.edsm.net/api-logs-v1/get-position"
    params = {"commanderName": CMDR_NAME, "apiKey": EDSM_API_KEY, "showCoordinates": 1}
    try:
        r = requests.get(url, params=params, headers=HEADERS_HTTP, timeout=6)
        return r.json()
    except Exception as e:
        return {"erreur": f"EDSM injoignable : {str(e)}"}

def interroger_edsm_systemes_proches(systeme_nom, rayon=30):
    url = "https://www.edsm.net/api-v1/sphere-systems"
    params = {"systemName": systeme_nom, "radius": min(int(rayon), 50), "showInformation": 1}
    try:
        r = requests.get(url, params=params, headers=HEADERS_HTTP, timeout=8)
        print(f"[DEBUG EDSM Systèmes] HTTP {r.status_code}")
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

import math
import unicodedata

def normaliser_texte(texte):
    if not texte:
        return ""
    sans_acc = "".join(c for c in unicodedata.normalize("NFD", str(texte)) if unicodedata.category(c) != "Mn")
    return sans_acc.lower().replace("-", " ").strip()

def interroger_edsm_stations(systeme_nom):
    url = "https://www.edsm.net/api-system-v1/stations"
    params = {"systemName": systeme_nom}
    try:
        r = requests.get(url, params=params, headers=HEADERS_HTTP, timeout=8)
        print(f"[DEBUG EDSM Stations] HTTP {r.status_code}")
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

def calculer_distance_systemes(systeme_depart, systeme_arrivee):
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

# ==============================================================================
# MODULE PHASE 4 : COMMERCE, ÉQUIPEMENT (SPANSH) & PRESSE-PAPIERS
# ==============================================================================

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

def copier_presse_papiers(texte):
    if not texte:
        return
    try:
        subprocess.run(["clip"], input=texte.strip().encode("utf-16le"), check=True)
        print(f"[Presse-papiers] Système copié : {texte.strip()}")
    except Exception as e:
        print(f"[Presse-papiers] Erreur : {e}")

def rechercher_marche_ou_equipement(objet, mode="vendre", critere_tri="prix", nb_sauts_max=None, rayon_al_max=None):
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
        import re
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
        url = "https://spansh.co.uk" + "/api/stations/search"
        r = requests.post(url, json=payload, headers=HEADERS_HTTP, timeout=10)
        print(f"[DEBUG Spansh] HTTP {r.status_code} | Mode: {mode} | Objet: {nom_en} | Rayon: {rayon_al} AL | Grand PAD: {besoin_grand_pad}")
        data = r.json()
        resultats = data.get("results", [])
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

def trouver_nom_station_par_market_id(systeme_nom, market_id):
    if not systeme_nom or not market_id:
        return "Station distante inconnue"
    url = "https://edsm.net" + "/api-system-v1/stations"
    try:
        r = requests.get(url, params={"systemName": systeme_nom}, headers=HEADERS_HTTP, timeout=6).json()
        for st in r.get("stations", []):
            if str(st.get("marketId")) == str(market_id):
                return st.get("name", "Station distante")
    except Exception:
        pass
    return f"Station distante (MarketID {market_id})"

# ==============================================================================
# MODULE PHASE 3 (V15.2) : TÉLÉMÉTRIE TEMPS RÉEL, SANTÉ MODULES & ALERTES RAPIDES
# ==============================================================================

NOMS_MODULES_FR = {
    "fuelscoop": "Récupérateur de carburant",
    "shieldgenerator": "Générateur de bouclier",
    "hyperdrive": "Réacteur FSD",
    "powerplant": "Générateur électrique",
    "engine": "Propulseurs",
    "powerdistributor": "Répartiteur de puissance",
    "lifesupport": "Système de survie",
    "sensors": "Capteurs",
    "detailedsurfacescanner": "Détecteur de surface détaillé",
    "guardianfsdbooster": "Accélérateur FSD Guardian",
    "buggybay": "Hangar à VRS",
    "mkiilargebuggybay": "Grand hangar à VRS",
    "repairer": "Unité de maintenance de terrain (AFMU)",
    "dronecontrol_repair": "Contrôleur de drones de réparation",
    "dronecontrol_collection": "Contrôleur de drones collecteurs",
    "dronecontrol_prospector": "Contrôleur de drones prospecteurs",
    "refinery": "Raffinerie",
    "dockingcomputer": "Ordinateur d'appontage",
    "supercruiseassist": "Assistance de super-navigation",
    "heatsinklauncher": "Lanceur de dissipateurs thermiques",
    "chafflauncher": "Lanceur de paillettes",
    "plasmapointdefence": "Tourelle de défense ponctuelle",
    "railgun": "Canon électrique (Railgun)",
    "beamlaser": "Laser à faisceau",
    "pulselaser": "Laser à impulsions",
    "multicannon": "Multicanon",
    "cargorack": "Soute",
    "cargohatch": "Écoutille de cargaison"
}

def traduire_nom_module(item_brut):
    if not item_brut:
        return "Module inconnu"
    cle = item_brut.lower()
    for mot_cle, nom_fr in NOMS_MODULES_FR.items():
        if mot_cle in cle:
            return nom_fr
    return item_brut

def lire_modules_info():
    """Lit ModulesInfo.json pour obtenir la santé (%), l'état actif/inactif et la liste des modules."""
    chemin_modules = os.path.join(DOSSIER_JOURNAUX_ED, "ModulesInfo.json")
    resultat = {
        "modules_inactifs": [],
        "modules_endommages_sous_50_pourcent": [],
        "tous_les_modules": []
    }
    if not os.path.exists(chemin_modules):
        return resultat
    try:
        with open(chemin_modules, "r", encoding="utf-8") as f:
            m_data = json.load(f)
        for mod in m_data.get("Modules", []):
            slot = mod.get("Slot", "")
            item = mod.get("Item", "")
            if any(k in slot for k in ["Bobble", "PaintJob", "Decal", "WeaponColour", "EngineColour", "ShipName", "ShipID", "VesselVoice", "PlanetaryApproachSuite", "ShipCockpit"]):
                continue
            nom_fr = traduire_nom_module(item)
            sante_pct = round(mod.get("Health", 1.0) * 100)
            est_actif = mod.get("On", True)
            etat_str = "Actif" if est_actif else "Inactif (désactivé)"
            
            resultat["tous_les_modules"].append(f"{nom_fr} ({slot}) : {etat_str}, Santé {sante_pct}%")
            if not est_actif:
                resultat["modules_inactifs"].append(f"{nom_fr} ({slot})")
            if sante_pct < 50:
                resultat["modules_endommages_sous_50_pourcent"].append(f"{nom_fr} ({sante_pct}%)")
    except Exception:
        pass
    return resultat

def lire_telemetrie_temps_reel():
    """Lit Status.json, Cargo.json, ModulesInfo.json et le dernier journal pour l'état instantané."""
    etat_base = analyser_journaux_locaux(nb_journaux=1)
    v_actif = etat_base.get("vaisseau_actif", {})
    cache = charger_cache_flotte()
    
    capacite_soute = 0
    nom_v = normaliser_texte(v_actif.get("nom", ""))
    mod_v = normaliser_texte(v_actif.get("modele", ""))
    for cle, cfg in cache.get("configurations", {}).items():
        if nom_v and normaliser_texte(cfg.get("nom", "")) == nom_v:
            capacite_soute = cfg.get("capacite_soute_tonnes", 0)
            break
    if not capacite_soute and mod_v:
        for cle, cfg in cache.get("configurations", {}).items():
            if normaliser_texte(cfg.get("modele", "")) == mod_v:
                capacite_soute = cfg.get("capacite_soute_tonnes", 0)
                break


    tonnage_utilise = 0
    liste_cargo = []
    chemin_cargo = os.path.join(DOSSIER_JOURNAUX_ED, "Cargo.json")
    if os.path.exists(chemin_cargo):
        try:
            with open(chemin_cargo, "r", encoding="utf-8") as f:
                c_data = json.load(f)
                tonnage_utilise = c_data.get("Count", 0)
                liste_cargo = [f"{i.get('Name_Localised') or i.get('Name')}: {i.get('Count')}t" for i in c_data.get("Inventory", [])]
        except Exception:
            pass

    infos_modules = lire_modules_info()

    telemetrie = {
        "vaisseau": f"{v_actif.get('nom', '')} ({v_actif.get('modele', 'Inconnu')})".strip(),
        "systeme": etat_base.get("systeme"),
        "station_ou_base": etat_base.get("station_ou_base"),
        "soute": {
            "capacite_totale_tonnes": capacite_soute,
            "utilisee_tonnes": tonnage_utilise,
            "place_libre_tonnes": max(0, capacite_soute - tonnage_utilise) if capacite_soute else "Inconnue",
            "contenu": liste_cargo
        },
        "carburant": etat_base.get("carburant"),
        "etat_systemes": {},
        "modules": infos_modules,
        "destination_verrouillee": "Aucune"
    }

    chemin_status = os.path.join(DOSSIER_JOURNAUX_ED, "Status.json")
    if os.path.exists(chemin_status):
        try:
            with open(chemin_status, "r", encoding="utf-8") as f:
                st = json.load(f)
            flags = st.get("Flags", 0)
            flags2 = st.get("Flags2", 0)
            
            telemetrie["etat_systemes"] = {
                "docke": bool(flags & 1),
                "pose_sur_planete": bool(flags & 2),
                "train_atterrissage_sorti": bool(flags & 4),
                "boucliers_actifs": bool(flags & 8),
                "supercruise": bool(flags & 16),
                "assistance_vol_activee": bool(flags & 32),
                "points_emport_sortis": bool(flags & 64),
                "ecope_cargaison_ouverte": bool(flags & 512),
                "surchauffe_critique": bool(flags & 1048576),
                "carburant_bas": bool(flags & 33554432),
                "en_danger_ou_attaque": bool(flags & 67108864),
                "interdiction_en_cours": bool(flags & 8388608),
                "a_pied": bool(flags2 & 1)
            }

            fuel_info = st.get("Fuel", {})
            if "FuelMain" in fuel_info:
                reservoir_principal = round(fuel_info.get("FuelMain", 0), 2)
                reservoir_secondaire = round(fuel_info.get("FuelReservoir", 0), 2)
                telemetrie["carburant"] = f"{reservoir_principal} tonnes dans le réservoir principal (réserve : {reservoir_secondaire} t)"

            pips = st.get("Pips", [])
            if len(pips) == 3:
                telemetrie["repartition_energie_pips"] = f"Systèmes {pips[0]/2}, Moteurs {pips[1]/2}, Armes {pips[2]/2}"

            if "Altitude" in st:
                telemetrie["altitude_surface_metres"] = st["Altitude"]

            dest = st.get("Destination", {})
            if dest and dest.get("Name"):
                telemetrie["destination_verrouillee"] = dest.get("Name")
        except Exception:
            pass

    return telemetrie

def surveiller_alertes_autonomes():
    """Thread haute réactivité (0.4s) surveillant Status.json, ModulesInfo.json et le journal actif."""
    chemin_status = os.path.join(DOSSIER_JOURNAUX_ED, "Status.json")
    chemin_modules = os.path.join(DOSSIER_JOURNAUX_ED, "ModulesInfo.json")
    precedent_bouclier = None
    precedent_surchauffe = False
    precedent_carburant_bas = False
    precedent_interdiction = False
    precedent_danger = False
    derniere_alerte_temps = {}
    modules_deja_alertes = set()
    taille_journal_lue = 0
    journal_suivi = ""

    REPLIQUES_ALERTES = {
        "bouclier_tombe": [
            "Alerte Commandant, nos boucliers viennent de tomber !",
            "Boucliers hors ligne ! La coque est exposée."
        ],
        "surchauffe": [
            "Alerte thermique ! Température critique, lancez un dissipateur !",
            "Surchauffe en cours ! Éloignez-vous de la source de chaleur !"
        ],
        "carburant_bas": [
            "Alerte carburant bas ! Trouvez une étoile ou une station rapidement.",
            "Réservoir critique, Commandant."
        ],
        "interdiction": [
            "Alerte, tentative d'interdiction en cours ! Gardez le vecteur aligné !",
            "Interdiction détectée, Commandant !"
        ],
        "danger": [
            "Alerte combat, nous sommes sous le feu ennemi !",
            "Systèmes en alerte rouge, nous sommes attaqués !"
        ]
    }

    def declencher_alerte(cle_alerte, message_direct=None):
        maintenant = time.time()
        if maintenant - derniere_alerte_temps.get(cle_alerte, 0) < 20:
            return
        derniere_alerte_temps[cle_alerte] = maintenant
        phrase = message_direct or random.choice(REPLIQUES_ALERTES[cle_alerte])
        print(f"[ALERTE AUTONOME - {cle_alerte.upper()}] : {phrase}")
        threading.Thread(target=dire_vocal, args=(phrase,), daemon=True).start()

    while True:
        try:
            # 1. Surveillance ultra-rapide de Status.json
            if os.path.exists(chemin_status):
                with open(chemin_status, "r", encoding="utf-8") as f:
                    st = json.load(f)
                flags = st.get("Flags", 0)
                est_docke = bool(flags & 1)
                est_a_pied = bool(st.get("Flags2", 0) & 1)

                if not est_docke and not est_a_pied and flags > 0:
                    bouclier_actif = bool(flags & 8)
                    surchauffe = bool(flags & 1048576)
                    carburant_bas = bool(flags & 33554432)
                    interdiction = bool(flags & 8388608)
                    danger = bool(flags & 67108864)

                    if precedent_bouclier is True and not bouclier_actif:
                        declencher_alerte("bouclier_tombe")
                    precedent_bouclier = bouclier_actif

                    if surchauffe and not precedent_surchauffe:
                        declencher_alerte("surchauffe")
                    precedent_surchauffe = surchauffe

                    if carburant_bas and not precedent_carburant_bas:
                        declencher_alerte("carburant_bas")
                    precedent_carburant_bas = carburant_bas

                    if interdiction and not precedent_interdiction:
                        declencher_alerte("interdiction")
                    precedent_interdiction = interdiction

                    if danger and not precedent_danger:
                        declencher_alerte("danger")
                    precedent_danger = danger
                else:
                    precedent_bouclier = None

            # 2. Surveillance de la santé des modules (< 50%) dans ModulesInfo.json
            if os.path.exists(chemin_modules):
                with open(chemin_modules, "r", encoding="utf-8") as fm:
                    m_data = json.load(fm)
                for mod in m_data.get("Modules", []):
                    slot = mod.get("Slot", "")
                    sante = mod.get("Health", 1.0)
                    if sante < 0.50:
                        if slot not in modules_deja_alertes:
                            modules_deja_alertes.add(slot)
                            nom_fr = traduire_nom_module(mod.get("Item", ""))
                            pct = round(sante * 100)
                            declencher_alerte(f"mod_{slot}", f"Attention Commandant, la santé du module {nom_fr} est tombée à {pct} pour cent !")
                    elif sante >= 0.50 and slot in modules_deja_alertes:
                        modules_deja_alertes.remove(slot)

            # 3. Surveillance précoce du journal actif (HeatWarning, HullDamage, ModuleMalfunction)
            fichiers = glob.glob(os.path.join(DOSSIER_JOURNAUX_ED, "Journal.*.log"))
            if fichiers:
                dernier_j = max(fichiers, key=os.path.getmtime)
                if dernier_j != journal_suivi:
                    journal_suivi = dernier_j
                    taille_journal_lue = os.path.getsize(dernier_j)
                else:
                    taille_actuelle = os.path.getsize(dernier_j)
                    if taille_actuelle > taille_journal_lue:
                        with open(dernier_j, "r", encoding="utf-8") as fj:
                            fj.seek(taille_journal_lue)
                            nouvelles_lignes = fj.readlines()
                        taille_journal_lue = taille_actuelle
                        for l in nouvelles_lignes:
                            try:
                                ev = json.loads(l)
                                etype = ev.get("event")
                                if etype == "HeatWarning":
                                    declencher_alerte("surchauffe", "Alerte thermique précoce ! La température approche du seuil critique !")
                                elif etype == "HullDamage":
                                    sante = round(ev.get("Health", 1) * 100)
                                    declencher_alerte("coque", f"Alerte critique ! Intégrité de la coque descendue à {sante} pour cent !")
                                elif etype == "ModuleMalfunction":
                                    mod = traduire_nom_module(ev.get("Module", "inconnu"))
                                    declencher_alerte("module", f"Attention, dysfonctionnement critique du module {mod} !")
                            except Exception:
                                continue
        except Exception:
            pass
        time.sleep(0.4)

threading.Thread(target=surveiller_alertes_autonomes, daemon=True).start()

OUTILS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": "obtenir_ma_flotte",
            "description": "Renvoie la liste complète de tous les vaisseaux possédés par le commandant (flotte complète, vaisseaux stockés, modèles, noms personnalisés et systèmes où ils sont garés).",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rechercher_commerce_ou_equipement",
            "description": "Cherche les stations compatibles avec la taille du vaisseau actuel (PAD Large ou Moyen) qui achètent ou vendent une marchandise/minerai (ex: Iridium, Or, Tritium) ou un module/équipement, dans un rayon donné (100 AL par défaut ou calculé selon un nombre de sauts max). Copie automatiquement le meilleur système dans le presse-papiers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "objet": {"type": "string", "description": "Nom de la marchandise, du minerai ou du module recherché (ex: Iridium, Or, 5A Frame Shift Drive)."},
                    "mode": {"type": "string", "enum": ["vendre", "acheter", "module"], "description": "'vendre' si le pilote veut vendre sa cargaison, 'acheter' s'il veut acheter une marchandise, 'module' s'il cherche un équipement de vaisseau."},
                    "critere_tri": {"type": "string", "enum": ["prix", "distance"], "description": "'prix' pour le meilleur tarif (au plus cher pour vendre, au moins cher pour acheter), 'distance' pour la station la plus proche."},
                    "rayon_al_max": {"type": "number", "description": "Optionnel : distance maximale en années-lumière demandée par le pilote (ex: 100, 600)."},
                    "nb_sauts_max": {"type": "integer", "description": "Optionnel : nombre maximum de sauts demandés par le pilote (ex: 3). Laisser vide pour 100 AL par défaut."}
                },
                "required": ["objet", "mode"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtenir_telemetrie_temps_reel",
            "description": "Lit Status.json, Cargo.json et ModulesInfo.json en temps réel pour connaître l'état général du vaisseau, le niveau exact de carburant, la place libre restante en soute, la liste des modules actifs ou inactifs, l'état de santé (%) des modules, l'état des boucliers, la température, la répartition des pips, la destination verrouillée et l'altitude.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtenir_etat_vaisseau_et_ressources",
            "description": "Lit uniquement la position actuelle en temps réel du commandant (système, planète, station actuelle), ses crédits, ses rangs, sa cargaison et ses matériaux. NE PAS utiliser pour chercher où sont garés les autres vaisseaux de la flotte (utiliser obtenir_ma_flotte).",
            "parameters": {
                "type": "object",
                "properties": {
                    "filtre_materiau": {
                        "type": "string",
                        "description": "Optionnel : nom d'un matériau spécifique recherché (ex: Fer, Arsenic, Phosphore) pour filtrer la réponse."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtenir_configuration_vaisseau",
            "description": "Renvoie la configuration détaillée, les modules, la portée de saut et la CAPACITÉ DE SOUTE (taille de soute en tonnes) d'un vaisseau spécifique (actif ou stocké, ex: Déménageur, Type-7, Anaconda, Sweet Kiss, Caspian Explorer).",
            "parameters": {
                "type": "object",
                "properties": {
                    "nom_ou_modele": {
                        "type": "string",
                        "description": "Optionnel : nom personnalisé ou modèle du vaisseau à inspecter (ex: Mandalay, Python, Anaconda). Si vide, renvoie le vaisseau actif."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "chercher_systemes_proches",
            "description": "Interroge EDSM pour trouver les systèmes stellaires proches autour d'un système donné (ou de la position actuelle).",
            "parameters": {
                "type": "object",
                "properties": {
                    "systeme": {"type": "string", "description": "Nom du système stellaire de référence (ex: Sol, Shinrarta Dezhra)."},
                    "rayon": {"type": "integer", "description": "Rayon de recherche en années-lumière (max 50, défaut 25)."}
                },
                "required": ["systeme"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculer_distance_entre_systemes",
            "description": "Calcule la distance exacte en années-lumière entre deux systèmes stellaires (ex: entre 'actuel' et 'Popocassa' ou 'Sol'). Utilise TOUJOURS cet outil quand le pilote demande une distance entre systèmes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "systeme_depart": {"type": "string", "description": "Système de départ (mettre 'actuel' pour la position actuelle du pilote)."},
                    "systeme_arrivee": {"type": "string", "description": "Nom du système de destination."}
                },
                "required": ["systeme_depart", "systeme_arrivee"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "chercher_stations_systeme",
                        "description": "Interroge EDSM pour lister les autres stations d'un système stellaire. NE PAS utiliser pour savoir où le commandant est actuellement docké (utiliser obtenir_etat_vaisseau_et_ressources pour cela).",
            "parameters": {
                "type": "object",
                "properties": {
                    "systeme": {"type": "string", "description": "Nom du système stellaire à inspecter."}
                },
                "required": ["systeme"]
            }
        }
    }
]

def executer_outil_ia(nom_fonction, arguments_json):
    args = json.loads(arguments_json) if arguments_json else {}
    print(f"[API/Outil] Exécution de {nom_fonction} avec {args}...")
    
    if nom_fonction == "obtenir_etat_vaisseau_et_ressources":
        donnees = analyser_journaux_locaux()
        if donnees.get("systeme") == "Inconnu" and EDSM_API_KEY != "VOTRE_CLE_API_EDSM_ICI":
            pos_edsm = interroger_edsm_position()
            if "system" in pos_edsm:
                donnees["systeme"] = pos_edsm["system"]
        
        filtre = args.get("filtre_materiau", "").lower()
        if filtre and "materiaux" in donnees:
            trouves = []
            for cat, liste in donnees["materiaux"].items():
                for item in liste:
                    if filtre in item.lower():
                        trouves.append(f"{item} ({cat})")
            donnees["materiaux"] = trouves if trouves else f"Aucun matériau trouvé pour '{filtre}'."
        return json.dumps(donnees, ensure_ascii=False)

    elif nom_fonction == "rechercher_commerce_ou_equipement":
        res = rechercher_marche_ou_equipement(
            objet=args.get("objet", ""),
            mode=args.get("mode", "vendre"),
            critere_tri=args.get("critere_tri", "prix"),
            nb_sauts_max=args.get("nb_sauts_max")
        )
        return json.dumps(res, ensure_ascii=False)

    elif nom_fonction == "obtenir_telemetrie_temps_reel":
        return json.dumps(lire_telemetrie_temps_reel(), ensure_ascii=False)

    elif nom_fonction == "obtenir_configuration_vaisseau":
        etat = analyser_journaux_locaux()
        cache = charger_cache_flotte()
        configs = cache.get("configurations", {})
        cible = normaliser_texte(args.get("nom_ou_modele", ""))
        synonymes = {"tip 7": "type 7", "tip 6": "type 6", "tip 8": "type 8", "tip 9": "type 9", "tip 10": "type 10"}
        cible = synonymes.get(cible, cible)
        if not cible:
            v_actif = etat.get("vaisseau_actif", {})
            cible = normaliser_texte(v_actif.get("nom") or v_actif.get("modele") or "")
        # Passe 1 : correspondance exacte sur le nom personnalisé du vaisseau (ex: "EXPLORER")
        for cle, detail in configs.items():
            if cible and normaliser_texte(detail.get("nom", "")) == cible:
                return json.dumps(detail, ensure_ascii=False)
        # Passe 2 : correspondance partielle sur le modèle ou le nom complet
        for cle, detail in configs.items():
            if cible and cible in normaliser_texte(cle):
                return json.dumps(detail, ensure_ascii=False)
        return json.dumps({"info": "Configuration détaillée non trouvée dans les journaux récents.", "configurations_disponibles": list(configs.keys())}, ensure_ascii=False)



    elif nom_fonction == "chercher_systemes_proches":
        sys_ref = args.get("systeme")
        if not sys_ref or sys_ref.lower() in ["ici", "actuel", "position"]:
            sys_ref = analyser_journaux_locaux().get("systeme", "Sol")
        return json.dumps(interroger_edsm_systemes_proches(sys_ref, args.get("rayon", 25)), ensure_ascii=False)

    elif nom_fonction == "chercher_stations_systeme":
        sys_ref = args.get("systeme")
        if not sys_ref or sys_ref.lower() in ["ici", "actuel", "position"]:
            sys_ref = analyser_journaux_locaux().get("systeme", "Sol")
        return json.dumps(interroger_edsm_stations(sys_ref), ensure_ascii=False)
    
    elif nom_fonction == "obtenir_ma_flotte":
        etat = analyser_journaux_locaux()
        v_actif = etat.get("vaisseau_actif", {})
        v_actif["systeme_actuel"] = etat.get("systeme")
        v_actif["station_ou_position_actuelle"] = etat.get("station_ou_base")
        return json.dumps({
            "vaisseau_actuel_pilote": v_actif,
            "vaisseaux_stockes_en_station": etat.get("flotte", []),
            "nombre_total_vaisseaux": 1 + len(etat.get("flotte", []))
        }, ensure_ascii=False)

    elif nom_fonction == "calculer_distance_entre_systemes":
        dep = args.get("systeme_depart", "")
        if not dep or dep.lower() in ["actuel", "ici", "position"]:
            dep = analyser_journaux_locaux().get("systeme", "Sol")
        arr = args.get("systeme_arrivee", "Sol")
        return json.dumps(calculer_distance_systemes(dep, arr), ensure_ascii=False)
    
    donnees.pop("flotte", None)
    donnees.pop("configurations_connues", None)

    return json.dumps({"erreur": "Outil inconnu"})

# ==============================================================================
# INITIALISATION MÉMOIRE & ACCUEIL
# ==============================================================================
memoire_long_terme = "Première initialisation du vaisseau."
if os.path.exists(FICHIER_MEMOIRE):
    with open(FICHIER_MEMOIRE, "r", encoding="utf-8") as f:
        memoire_long_terme = f.read().strip()

try:
    etat_initial = analyser_journaux_locaux()
    v_init = etat_initial.get("vaisseau_actif", {})
    nom_v_init = f"{v_init.get('nom')} ({v_init.get('modele')})" if v_init.get("nom") else v_init.get("modele", "Inconnu")
    prompt_accueil = (
        f"Tu t'appelles {NOM_IA}. Personnalité : {PERSONNALITE_IA} "
        f"Journal de bord : {memoire_long_terme} "
        f"Position actuelle : Système {etat_initial.get('systeme')}, Corps {etat_initial.get('corps_celeste')}, Vaisseau {nom_v_init}. "
        "Formule un accueil très court (2 phrases max) selon ta personnalité."
    )
    res_accueil = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_accueil}]
    )
    accueil_ia = res_accueil.choices[0].message.content
    print(f"[{NOM_IA}] : {accueil_ia}")
    dire_vocal(accueil_ia)
except Exception as e:
    print(f"Erreur accueil : {e}")

# ==============================================================================
# BOUCLE VOCALE PRINCIPALE
# ==============================================================================
historique_conversation = []
MAX_MEMOIRE = 10
FREQUENCE_AUDIO = 16000

def enregistrer_et_transcrire():
    blocs_audio = []
    def callback_audio(indata, frames, time_info, status):
        blocs_audio.append(indata.copy())
    with sd.InputStream(samplerate=FREQUENCE_AUDIO, channels=1, dtype='float32', callback=callback_audio):
        while keyboard.is_pressed(TOUCHE_MICRO):
            time.sleep(0.05)
    if not blocs_audio:
        return ""
    audio_complet = np.concatenate(blocs_audio, axis=0).flatten()
    if len(audio_complet) < FREQUENCE_AUDIO * 0.4:
        return ""
    segments, _ = modele_whisper.transcribe(audio_complet, language="fr", beam_size=5)
    texte = " ".join([segment.text for segment in segments]).strip()
    nom_clean = NOM_IA.lower()
    for prefixe in [f"{nom_clean},", f"{nom_clean}.", nom_clean]:
        if texte.lower().startswith(prefixe):
            texte = texte[len(prefixe):].strip()
            break
    for mot in ["terminé.", "terminé", "terminée.", "terminée"]:
        if texte.lower().endswith(mot):
            texte = texte[:-len(mot)].strip()
            break
    return texte

while True:
    try:
        if keyboard.is_pressed(TOUCHE_MICRO):
            texte_actuel = enregistrer_et_transcrire()
            if texte_actuel and len(texte_actuel) > 1:
                print(f"[Vous] : {texte_actuel}")
                
                LISTE_COMMANDES_VAISSEAU = ""
                if os.path.exists(FICHIER_COMMANDES):
                    with open(FICHIER_COMMANDES, "r", encoding="utf-8") as f:
                        lignes = [l.strip() for l in f.readlines() if l.strip()]
                    LISTE_COMMANDES_VAISSEAU = ";".join(lignes)
                
                instructions_systeme = (
                    f"Tu es l'IA de bord {NOM_IA} du Commandant {CMDR_NAME}. Personnalité : {PERSONNALITE_IA} "
                    f"ARCHIVES : {memoire_long_terme} "
                    "Tu disposes d'outils pour consulter l'état du vaisseau (crédits, rangs, position, planète, flotte complète, équipement des vaisseaux, matériaux) "
                    "et les systèmes/stations proches via EDSM. Utilise-les dès que le pilote pose une question sur sa situation. "
                    "Prononce toujours 'années-lumière' et 'secondes-lumière' en toutes lettres. "
                    "RÈGLE ABSOLUE : Ne te fie JAMAIS aux ARCHIVES ni à ta mémoire pour la position, la station actuelle, les crédits, les matériaux, les rangs ou la flotte. Appelle OBLIGATOIREMENT l'outil correspondant à chaque question sur le vaisseau, la station ou la flotte pour lire les données en temps réel. "
                    "Si une donnée n'est pas présente dans la télémétrie (comme la vitesse instantanée en m/s, le temps d'arrivée exact ou l'altitude lorsque le capteur est inactif), ne l'invente JAMAIS : précise simplement avec sarcasme que l'ordinateur de bord du vaisseau ne transmet pas cette télémétrie. "
                    "Quand tu donnes un résultat de commerce ou d'équipement, cite TOUJOURS pour la meilleure station : son nom, le système, le prix unitaire en crédits, le stock ou la demande en tonnes, et le nombre de sauts approximatifs (ne cite pas les stations secondaires sauf si demandé). "
                    "Si le pilote demande une action physique sur le vaisseau, fais une réponse très courte (5-6 mots max), "
                    "puis ajoute à la fin l'action exacte entre crochets parmi : "
                    f"{LISTE_COMMANDES_VAISSEAU} Exemple : [EXECUTE:Allumer les phares]."
		    f"Date et heure actuelles : {time.strftime('%d/%m/%Y %H:%M')}. "
                )
                
                messages_api = [{"role": "system", "content": instructions_systeme}] + historique_conversation + [{"role": "user", "content": texte_actuel}]
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages_api,
                    tools=OUTILS_OPENAI,
                    tool_choice="auto"
                )
                
                message_reponse = response.choices[0].message
                
                if message_reponse.tool_calls:
                    messages_api.append(message_reponse)
                    for tool_call in message_reponse.tool_calls:
                        resultat_outil = executer_outil_ia(tool_call.function.name, tool_call.function.arguments)
                        messages_api.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": resultat_outil
                        })
                    second_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages_api
                    )
                    reponse_ia = second_response.choices[0].message.content
                else:
                    reponse_ia = message_reponse.content

                print(f"[IA] : {reponse_ia}")
                historique_conversation = (historique_conversation + [{"role": "user", "content": texte_actuel}, {"role": "assistant", "content": reponse_ia}])[-MAX_MEMOIRE:]
                
                nom_action_va = None
                if "[" in reponse_ia and "]" in reponse_ia:
                    debut_crochet = reponse_ia.find("[")
                    fin_crochet = reponse_ia.find("]", debut_crochet)
                    contenu_crochet = reponse_ia[debut_crochet + 1:fin_crochet].strip()
                    if contenu_crochet.upper().startswith("EXECUTE:"):
                        nom_action_va = contenu_crochet[8:].strip()
                    else:
                        nom_action_va = contenu_crochet
                    reponse_ia = (reponse_ia[:debut_crochet] + reponse_ia[fin_crochet + 1:]).strip()

                if nom_action_va:
                    print(f"[VoiceAttack] Exécution de : {nom_action_va}")
                    subprocess.Popen([CHEMIN_VOICEATTACK, "-command", nom_action_va])

                
                dire_vocal(reponse_ia)
                
                def sauvegarder_journal_async(ech_pilote, ech_ia, memoire_actuelle):
                    global memoire_long_terme
                    try:
                        prompt_archive = (
    			    f"Archives actuelles :\n{memoire_actuelle}\n"
    			    f"Nouvel échange réel : Pilote: '{ech_pilote}' / {NOM_IA}: '{ech_ia}'\n"
    			    "Résume uniquement les faits marquants et préférences du pilote en 50 lignes maximum, sans jamais inventer d'échanges fictifs ni stocker de position/flotte temporaire."
			)

                        res_archive = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt_archive}])
                        memoire_long_terme = res_archive.choices[0].message.content
                        with open(FICHIER_MEMOIRE, "w", encoding="utf-8") as f:
                            f.write(memoire_long_terme)
                    except Exception:
                        pass
                threading.Thread(target=sauvegarder_journal_async, args=(texte_actuel, reponse_ia, memoire_long_terme), daemon=True).start()
                
    except Exception as e:
        print(f"Erreur : {e}")
    time.sleep(0.05)
