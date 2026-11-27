"""Module de télémétrie locale Elite Dangerous (Journaux, Status, Modules, Flotte et Alertes)."""

import glob
import json
import os
import random
import threading
import time
import unicodedata

from modules.config_loader import (
    DOSSIER_JOURNAUX_ED,
    FICHIER_FLOTTE,
    NAVIGATION_CONFIG,
    formater_nom_vaisseau
)
from modules.tts_engine import dire_vocal

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


def normaliser_texte(texte: str) -> str:
    """Retire les accents, passe en minuscules et nettoie les tirets/espaces."""
    if not texte:
        return ""
    sans_acc = "".join(c for c in unicodedata.normalize("NFD", str(texte)) if unicodedata.category(c) != "Mn")
    return sans_acc.lower().replace("-", " ").strip()


def charger_cache_flotte() -> dict:
    """Charge le cache persistant de la flotte du commandant."""
    if os.path.exists(FICHIER_FLOTTE):
        try:
            with open(FICHIER_FLOTTE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"vaisseaux_stockes": [], "configurations": {}}


def sauvegarder_cache_flotte(data: dict):
    """Enregistre le cache de flotte sur disque."""
    try:
        with open(FICHIER_FLOTTE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def traduire_nom_module(item_brut: str) -> str:
    """Traduit le nom interne d'un module en français lisible."""
    if not item_brut:
        return "Module inconnu"
    cle = str(item_brut).lower()
    for mot_cle, nom_fr in NOMS_MODULES_FR.items():
        if mot_cle in cle:
            return nom_fr
    return item_brut


def _lire_dernier_loadout_modules() -> dict:
    """Lit le dernier événement Loadout du journal le plus récent pour obtenir On et Health réels."""
    modules_par_slot = {}
    try:
        fichiers = sorted(glob.glob(os.path.join(DOSSIER_JOURNAUX_ED, "Journal.*.log")), key=os.path.getmtime)
        if not fichiers:
            return modules_par_slot
        with open(fichiers[-1], "r", encoding="utf-8") as f:
            for ligne in f:
                if '"Loadout"' not in ligne:
                    continue
                try:
                    ev = json.loads(ligne)
                    if ev.get("event") == "Loadout":
                        modules_par_slot = {
                            m.get("Slot", ""): m
                            for m in ev.get("Modules", [])
                            if m.get("Slot")
                        }
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return modules_par_slot


def lire_modules_info() -> dict:
    """Lit ModulesInfo.json (puissance/priorité temps réel) croisé avec le dernier Loadout (On/Health)."""
    chemin_modules = os.path.join(DOSSIER_JOURNAUX_ED, "ModulesInfo.json")
    resultat = {
        "limitation_ed": (
            "ModulesInfo.json d'Elite Dangerous ne fournit que la puissance (Power) et la priorité (Priority) ; "
            "l'état On/Off et la santé (%) proviennent du dernier événement Loadout (mis à jour au chargement, "
            "changement de vaisseau ou sortie d'équipement, pas lors d'un clic manuel en vol)."
        ),
        "modules_inactifs": [],
        "modules_endommages_sous_50_pourcent": [],
        "tous_les_modules": []
    }
    loadout_par_slot = _lire_dernier_loadout_modules()

    sources_modules = []
    if os.path.exists(chemin_modules):
        try:
            with open(chemin_modules, "r", encoding="utf-8") as f:
                m_data = json.load(f)
            sources_modules = m_data.get("Modules", [])
        except Exception:
            pass

    if not sources_modules and loadout_par_slot:
        sources_modules = list(loadout_par_slot.values())

    for mod in sources_modules:
        slot = mod.get("Slot", "")
        item = mod.get("Item", "")
        if any(k in slot for k in ["Bobble", "PaintJob", "Decal", "WeaponColour", "EngineColour", "ShipName", "ShipID", "VesselVoice", "PlanetaryApproachSuite", "ShipCockpit"]):
            continue
        nom_fr = traduire_nom_module(item)
        mod_loadout = loadout_par_slot.get(slot, {})

        # On / Health ne sont présents que dans Loadout (jamais dans ModulesInfo.json)
        if "On" in mod:
            est_actif = bool(mod["On"])
            source_on = "temps reel"
        elif "On" in mod_loadout:
            est_actif = bool(mod_loadout["On"])
            source_on = "dernier Loadout"
        else:
            est_actif = None
            source_on = "inconnu"

        if "Health" in mod:
            sante_pct = round(mod["Health"] * 100)
        elif "Health" in mod_loadout:
            sante_pct = round(mod_loadout["Health"] * 100)
        else:
            sante_pct = None

        puissance = mod.get("Power")
        prio = mod.get("Priority")

        if est_actif is True:
            etat_str = f"Actif ({source_on})"
        elif est_actif is False:
            etat_str = f"Inactif ({source_on})"
        else:
            etat_str = "Etat On/Off non transmis par ED"

        details = [etat_str]
        if sante_pct is not None:
            details.append(f"Santé {sante_pct}%")
        if puissance is not None:
            details.append(f"{round(float(puissance), 2)} MW")
        if prio is not None:
            details.append(f"Prio {int(prio) + 1}")

        resultat["tous_les_modules"].append(f"{nom_fr} ({slot}) : {', '.join(details)}")
        if est_actif is False:
            resultat["modules_inactifs"].append(f"{nom_fr} ({slot})")
        if sante_pct is not None and sante_pct < 50:
            resultat["modules_endommages_sous_50_pourcent"].append(f"{nom_fr} ({sante_pct}%)")

    return resultat


def analyser_journaux_locaux(nb_journaux=25) -> dict:
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


def lire_telemetrie_temps_reel() -> dict:
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
                "en_danger_ou_attaque": bool(flags & 4194304),
                "en_vrs": bool(flags & 67108864),
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


def determiner_vue_ed(status_data: dict) -> str:
    """Détermine la vue active d'Elite Dangerous à partir de Status.json.

    Retourne l'une des valeurs : 'carte_galactique', 'carte_systeme', 'a_pied', 'cockpit'.
    """
    if not isinstance(status_data, dict):
        return "cockpit"
    gui_focus = status_data.get("GuiFocus", 0)
    if gui_focus == 6:
        return "carte_galactique"
    if gui_focus in (7, 8):
        return "carte_systeme"
    flags2 = status_data.get("Flags2", 0)
    if bool(flags2 & 1):
        return "a_pied"
    return "cockpit"


def lire_equipement_a_pied() -> dict:
    """Lit Status.json pour connaître l'outil ou l'arme actuellement en main à pied (Odyssey).

    Retourne un dictionnaire avec :
    - a_pied (bool)
    - selected_weapon (str)
    - selected_weapon_localised (str)
    - categorie (str) : 'mains_vides' | 'outil_combinaison' | 'energiseur' |
                        'analyseur_profil' | 'arme' | 'inconnu'
    """
    resultat = {
        "a_pied": False,
        "selected_weapon": "",
        "selected_weapon_localised": "",
        "categorie": "inconnu"
    }
    chemin_status = os.path.join(DOSSIER_JOURNAUX_ED, "Status.json")
    if not os.path.exists(chemin_status):
        return resultat

    try:
        with open(chemin_status, "r", encoding="utf-8") as f:
            st = json.load(f)
    except Exception:
        return resultat

    flags2 = int(st.get("Flags2", 0) or 0)
    est_a_pied = bool(flags2 & (1 | 8 | 16 | 8192 | 16384)) or ("Oxygen" in st)
    resultat["a_pied"] = est_a_pied
    if not est_a_pied:
        return resultat

    if "SelectedWeapon" not in st:
        return resultat

    arme_brut = str(st.get("SelectedWeapon") or "").strip()
    arme_loc = str(st.get("SelectedWeapon_Localised") or "").strip()
    resultat["selected_weapon"] = arme_brut
    resultat["selected_weapon_localised"] = arme_loc

    # Normalisation sans accents pour reconnaître aussi bien les clés internes ED que le français ('échantillonneur', 'énergiseur')
    cle = normaliser_texte(f"{arme_brut} {arme_loc}".replace("_", " ").replace("$", " ").replace(";", " "))

    if not arme_brut or any(k in cle for k in ("fists", "unarmed", "melee", "mains nues", "main nue", "poing", "desarme")):
        resultat["categorie"] = "mains_vides"
        return resultat

    if any(k in cle for k in ("sampletool", "bioscanner", "genetichunter", "genetic", "sampler", "echantillon", "arccutter", "arc cutter", "cutter", "decoupeur", "suittool")):
        resultat["categorie"] = "outil_combinaison"
    elif any(k in cle for k in ("rechargetool", "energylink", "energiseur", "liaison", "recharge")):
        resultat["categorie"] = "energiseur"
    elif any(k in cle for k in ("companalyser", "profileanalyser", "analyseur")):
        resultat["categorie"] = "analyseur_profil"
    else:
        resultat["categorie"] = "arme"

    return resultat


CYCLE_OUTILS_A_PIED = [
    ("outil_combinaison", "Prend Outil Combinaison"),
    ("energiseur", "Active énergiseur"),
    ("analyseur_profil", "Active Analyseur Profil"),
]

COMMANDES_EQUIPEMENT_A_PIED = {
    "outil suivant",
    "prend outil combinaison",
    "active energiseur",
    "active analyseur profil",
    "ranger outil",
    "ranger arme",
    "arme principale",
    "arme secondaire",
    "change arme",
    "arme suivante",
    "recharge arme",
    "charger cellule energie",
    "utilise cellule energie",
}


def resoudre_garde_fou_equipement_a_pied(nom_action: str, equip: dict | None = None) -> tuple[str | None, str | None]:
    """Protège les outils/armes à pied contre les toggles involontaires grâce à Status.json (SelectedWeapon).

    Retourne (action_va_a_executer, message_vocal_remplacement) :
    - Si l'action est redondante (outil déjà en main ou mains déjà vides), retourne (None, message_court).
    - Si 'Outil suivant', retourne la prochaine macro d'outil uniquement (jamais d'arme !).
    - Si 'Charger Cellule énergie' alors qu'on est à pied, remappe vers 'Utilise Cellule Energie'.
    - Sinon, retourne (nom_action, None) sans modification.
    """
    if not nom_action:
        return nom_action, None

    cle = normaliser_texte(nom_action)
    if cle not in COMMANDES_EQUIPEMENT_A_PIED:
        return nom_action, None

    etat = equip if equip is not None else lire_equipement_a_pied()
    cat = etat.get("categorie", "inconnu")

    if etat.get("a_pied"):
        print(
            f"[Équipement à pied] Status.json -> SelectedWeapon='{etat.get('selected_weapon', '')}' "
            f"(loc='{etat.get('selected_weapon_localised', '')}') => cat='{cat}'"
        )

    # 0. Remappage symétrique Cellule d'énergie : batterie combinaison à pied vs cellule bouclier en vaisseau
    if cle == "charger cellule energie" and etat.get("a_pied"):
        return "Utilise Cellule Energie", None
    if cle == "utilise cellule energie" and not etat.get("a_pied"):
        return "Charger Cellule énergie", None

    # 1. Cycle intelligent 'Outil suivant' (uniquement entre les 3 outils, zéro risque de sortir une arme)
    if cle == "outil suivant":
        ordre_cats = [c for c, _ in CYCLE_OUTILS_A_PIED]
        if cat in ordre_cats:
            idx_suiv = (ordre_cats.index(cat) + 1) % len(CYCLE_OUTILS_A_PIED)
            return CYCLE_OUTILS_A_PIED[idx_suiv][1], None
        return CYCLE_OUTILS_A_PIED[0][1], None

    # Si l'état réel SelectedWeapon n'est pas connu (pas à pied ou Status.json muet), on laisse passer normalement
    if not etat.get("a_pied") or cat == "inconnu":
        return nom_action, None

    # 2. Anti-toggle sur les outils à pied (réappuyer sur Ctrl+ù quand l'outil est déjà en main le range ou rebascule !)
    if cle == "prend outil combinaison" and cat == "outil_combinaison":
        return None, "L'outil de combinaison est déjà en main."
    if cle == "active energiseur" and cat == "energiseur":
        return None, "L'énergiseur est déjà en main."
    if cle == "active analyseur profil" and cat == "analyseur_profil":
        return None, "L'analyseur de profil est déjà en main."

    # 3. Anti-toggle sur rengainage lorsque les mains sont déjà vides
    if cle in ("ranger outil", "ranger arme") and cat == "mains_vides":
        return None, "Tes mains sont déjà vides."

    return nom_action, None


_roue_a_pied_active = None  # None | 'inventaire' | 'emoticomes' | 'insight'

ROUES_A_PIED_CONFIG = {
    "inventaire": (
        "affiche roue d'inventaire",
        "Enlève Roue d'inventaire",
        "La roue d'inventaire est déjà affichée."
    ),
    "emoticomes": (
        "affiche roue d'emoticomes",
        "Enlève Roue d'émoticomes",
        "La roue d'émoticônes est déjà affichée."
    ),
    "insight": (
        "ouvre menu insight",
        "Ferme Menu Insight",
        "Le menu Insight est déjà affiché."
    ),
}


def resoudre_bascule_roues_a_pied(nom_action: str, a_pied: bool | None = None) -> tuple[list[str], str | None]:
    """Gère proprement les 3 roues/menus radiaux Odyssey (inventaire, émoticônes, Insight) sans superposition.

    Retourne (liste_actions_va_a_executer_en_sequence, message_vocal_remplacement) :
    - Si une roue est déjà ouverte et qu'on demande une autre roue : ferme d'abord la roue active, puis ouvre la nouvelle.
    - Si la roue demandée est déjà ouverte : évite le toggle involontaire qui la refermerait.
    - Si on demande de fermer une roue : laisse toujours passer (au cas où elle ait été ouverte au HOTAS) et remet l'état à None.
    """
    global _roue_a_pied_active
    if not nom_action:
        return [], None

    est_a_pied = a_pied if a_pied is not None else lire_equipement_a_pied().get("a_pied", False)
    if not est_a_pied:
        _roue_a_pied_active = None

    cle = normaliser_texte(nom_action)

    # Ouverture d'une des 3 roues / menus radiaux
    for nom_roue, (cle_ouvrir, _cmd_fermer, msg_deja) in ROUES_A_PIED_CONFIG.items():
        if cle == cle_ouvrir:
            if _roue_a_pied_active == nom_roue:
                return [], msg_deja
            actions = []
            if _roue_a_pied_active in ROUES_A_PIED_CONFIG:
                actions.append(ROUES_A_PIED_CONFIG[_roue_a_pied_active][1])
            actions.append(nom_action)
            _roue_a_pied_active = nom_roue
            return actions, None

    # Fermeture d'une des 3 roues / menus radiaux
    cles_fermer = {normaliser_texte(cfg[1]) for cfg in ROUES_A_PIED_CONFIG.values()}
    if cle in cles_fermer:
        _roue_a_pied_active = None
        return [nom_action], None

    return [nom_action], None


def lire_systeme_actuel_rapide() -> str:
    """Lit rapidement le nom du système stellaire actuel depuis le journal le plus récent."""
    try:
        fichiers = sorted(
            glob.glob(os.path.join(DOSSIER_JOURNAUX_ED, "Journal.*.log")),
            key=os.path.getmtime
        )
        for chemin in reversed(fichiers[-3:]):
            systeme = ""
            with open(chemin, "r", encoding="utf-8", errors="ignore") as f:
                for ligne in f:
                    if '"FSDJump"' in ligne or '"Location"' in ligne or '"CarrierJump"' in ligne:
                        try:
                            ev = json.loads(ligne)
                            if ev.get("event") in ("FSDJump", "Location", "CarrierJump") and ev.get("StarSystem"):
                                systeme = str(ev["StarSystem"]).strip()
                        except Exception:
                            continue
            if systeme:
                return systeme
    except Exception:
        pass
    return ""


def surveiller_alertes_autonomes(
    get_mode_actuel_func=None,
    on_alerte_hud_func=None,
    on_changement_vue_func=None
):
    """Thread haute réactivité (0.4s) surveillant Status.json, ModulesInfo.json et le journal actif."""
    chemin_status = os.path.join(DOSSIER_JOURNAUX_ED, "Status.json")
    chemin_modules = os.path.join(DOSSIER_JOURNAUX_ED, "ModulesInfo.json")
    precedent_bouclier = None
    precedent_surchauffe = False
    precedent_carburant_bas = False
    precedent_interdiction = False
    precedent_danger = False
    precedent_oxy_bas = False
    precedent_oxy_crit = False
    precedent_sante_basse = False
    precedente_vue = None
    derniere_alerte_temps = {}
    modules_deja_alertes = set()
    taille_journal_lue = 0
    journal_suivi = ""
    # État de navigation proactive pour FSDJump (arrivée), Scan étoile et FSSDiscoveryScan (honk)
    etat_nav = {
        "systeme": "",
        "deja_visite": True,
        "was_discovered_etoile": None,
        "edsm": None,
        "event_edsm_pret": threading.Event()
    }
    repliques_maison = [
        "Enfin de retour à la maison, Commandant ! Votre flotte vous attendait sagement à {sys}.",
        "Bon retour à {sys}, Commandant ! Rien ne vaut son propre hangar.",
        "Maison douce maison ! Bienvenue à {sys}, Commandant."
    ]

    def annoncer_navigation(cle_hud: str, phrase: str, detail_hud: str = ""):
        if get_mode_actuel_func and get_mode_actuel_func() != "NORMAL":
            return
        print(f"[NAVIGATION AUTO - {cle_hud.upper()}] : {phrase}")
        if on_alerte_hud_func:
            try:
                on_alerte_hud_func(cle_hud, detail_hud or "")
            except Exception:
                pass
        threading.Thread(target=dire_vocal, args=(phrase,), daemon=True).start()

    def traiter_arrivee_systeme(ev_jump: dict):
        if not NAVIGATION_CONFIG.get("actif", True):
            return
        nom_sys = str(ev_jump.get("StarSystem") or "").strip()
        if not nom_sys:
            return
        pop_jeu = int(ev_jump.get("Population", 0) or 0)

        from modules.codex_ed import (
            enregistrer_visite_systeme_cmdr,
            obtenir_systeme_maison,
            systeme_deja_visite_par_cmdr
        )
        from modules.api_clients import interroger_edsm_resume_systeme

        sys_maison = obtenir_systeme_maison()
        est_maison = bool(sys_maison and normaliser_texte(nom_sys) == normaliser_texte(sys_maison))
        deja_visite = systeme_deja_visite_par_cmdr(nom_sys)

        etat_nav["systeme"] = nom_sys
        etat_nav["was_discovered_etoile"] = None
        etat_nav["edsm"] = None
        etat_nav["event_edsm_pret"] = threading.Event()

        # 1. Retour à la maison (ex: Popocassa)
        if est_maison:
            etat_nav["deja_visite"] = True
            etat_nav["event_edsm_pret"].set()
            enregistrer_visite_systeme_cmdr(nom_sys)
            if NAVIGATION_CONFIG.get("annoncer_arrivee_systeme", True):
                phrase = random.choice(repliques_maison).format(sys=nom_sys)
                annoncer_navigation("retour_maison", phrase, f"{nom_sys}\nFlotte a quai")
            return

        # 2. Système déjà visité par le Commandant -> silence complet (y compris sur le honk)
        if deja_visite:
            etat_nav["deja_visite"] = True
            etat_nav["event_edsm_pret"].set()
            enregistrer_visite_systeme_cmdr(nom_sys)
            print(f"[NAVIGATION AUTO] Système déjà visité ({nom_sys}) -> silence radio.")
            return

        # 3. Nouveau système pour le Commandant -> vérification EDSM en arrière-plan
        etat_nav["deja_visite"] = False
        enregistrer_visite_systeme_cmdr(nom_sys)

        def _tache_edsm():
            edsm = interroger_edsm_resume_systeme(nom_sys)
            if etat_nav["systeme"] != nom_sys:
                return
            # Laisse 0.8s max au jeu pour écrire l'AutoScan de l'étoile principale (champ officiel WasDiscovered)
            t_wait_scan = time.time()
            while etat_nav["was_discovered_etoile"] is None and (time.time() - t_wait_scan) < 0.8:
                time.sleep(0.1)

            etat_nav["edsm"] = edsm
            etat_nav["event_edsm_pret"].set()

            if not NAVIGATION_CONFIG.get("annoncer_arrivee_systeme", True):
                return

            deja_decouvert_frontier = etat_nav["was_discovered_etoile"]

            if deja_decouvert_frontier is False:
                annoncer_navigation(
                    "nouveau_systeme",
                    "Nouveau système, Commandant ! Officiellement jamais découvert avant vous : première découverte confirmée !",
                    f"{nom_sys}\n1ere decouverte !"
                )
            elif deja_decouvert_frontier is True and not edsm.get("connu_edsm"):
                annoncer_navigation(
                    "nouveau_systeme",
                    "Nouveau système pour vous, Commandant, mais déjà découvert par un autre pilote hors archives.",
                    f"{nom_sys}\nDeja decouvert\n(hors EDSM)"
                )
            elif not edsm.get("joignable"):
                annoncer_navigation(
                    "nouveau_systeme",
                    f"Nouveau système pour vous, Commandant : {nom_sys}.",
                    f"{nom_sys}\nNouveau (EDSM hors ligne)"
                )
            elif not edsm.get("connu_edsm"):
                annoncer_navigation(
                    "nouveau_systeme",
                    "Nouveau système pour vous, inconnu des archives EDSM : première découverte possible !",
                    f"{nom_sys}\nInconnu EDSM\n(1ere dec. possible)"
                )
            else:
                nb_st = edsm.get("nb_stations", 0)
                if nb_st > 0:
                    s_txt = f"{nb_st} station" if nb_st == 1 else f"{nb_st} stations"
                    phrase = f"Nouveau système pour vous, mais déjà cartographié. Il y a {s_txt} sur place."
                    det = f"{nom_sys}\nDeja visite (EDSM)\nStations: {nb_st}"
                elif pop_jeu > 0 or edsm.get("population", 0) > 0:
                    phrase = "Nouveau système pour vous, déjà visité et habité."
                    det = f"{nom_sys}\nDeja visite (habite)"
                else:
                    phrase = "Nouveau système pour vous, Commandant, mais déjà visité par d'autres pilotes."
                    det = f"{nom_sys}\nDeja visite (EDSM)\nInhabite"
                annoncer_navigation("nouveau_systeme", phrase, det)

        threading.Thread(target=_tache_edsm, daemon=True).start()

    def traiter_honk_systeme(ev_honk: dict):
        if not NAVIGATION_CONFIG.get("actif", True) or not NAVIGATION_CONFIG.get("annoncer_honk", True):
            return
        # Silence complet si le système était déjà visité (ou retour maison)
        if etat_nav.get("deja_visite", True):
            return

        nom_sys = str(ev_honk.get("SystemName") or etat_nav.get("systeme") or "").strip()
        nb_corps = int(ev_honk.get("BodyCount", 0) or 0)
        nb_non_corps = int(ev_honk.get("NonBodyCount", 0) or 0)

        def _tache_honk():
            # Attend brièvement le cache EDSM du saut (max 2.5s) pour enrichir le honk sans doublon réseau
            ev_pret = etat_nav.get("event_edsm_pret")
            if ev_pret:
                ev_pret.wait(timeout=2.5)
            edsm = etat_nav.get("edsm") or {}
            connu_edsm = bool(edsm.get("connu_edsm"))
            nb_st = int(edsm.get("nb_stations", 0) or 0)
            nb_fc = int(edsm.get("nb_porte_vaisseaux", 0) or 0)
            planetes_top = edsm.get("planetes_interessantes") or []
            nb_corps_edsm = int(edsm.get("nb_corps_edsm", 0) or 0)
            anneaux_met = int(edsm.get("anneaux_metalliques", 0) or 0)

            corps_txt = f"{nb_corps} corps"
            morceaux = [f"Honk reçu : {corps_txt}"]
            hud_lignes = [nom_sys or "Systeme", f"Corps: {nb_corps} | Sig: {nb_non_corps}"]

            if nb_st > 0:
                morceaux.append(f"{nb_st} station" if nb_st == 1 else f"{nb_st} stations")
                hud_lignes.append(f"Stations: {nb_st}")
            elif nb_fc > 0:
                morceaux.append(f"aucune station fixe mais {nb_fc} porte-vaisseaux")
                hud_lignes.append(f"Porte-vaisseaux: {nb_fc}")
            else:
                hud_lignes.append("Stations: 0")

            if not connu_edsm:
                deja_dec_frontier = etat_nav.get("was_discovered_etoile")
                if deja_dec_frontier is True:
                    if nb_corps >= 8:
                        suite = "Déjà découvert hors archives, mais riche : un scan FSS peut valoir le coup."
                        hud_lignes.append("Hors EDSM -> FSS utile")
                    else:
                        suite = "Déjà découvert par un autre pilote et peu de corps ici."
                        hud_lignes.append("Peu de corps")
                elif nb_corps >= 10:
                    suite = "Système vierge très riche : un scan FSS s'impose, Commandant !"
                    hud_lignes.append("Vierge -> FSS conseille")
                elif nb_corps >= 4:
                    suite = "Système vierge intéressant, ça mérite un coup de FSS."
                    hud_lignes.append("Vierge -> FSS utile")
                else:
                    suite = "Système vierge mais pauvre, rien d'excitant a priori."
                    hud_lignes.append("Peu de corps")
            elif planetes_top:
                # Compte synthétique des pépites connues sur EDSM
                nb_top = len(planetes_top)
                exemple = planetes_top[0]
                if nb_top == 1:
                    suite = f"Intéressant : 1 planète à haute valeur connue dans les archives, {exemple}."
                else:
                    suite = f"Système intéressant : {nb_top} planètes à haute valeur connues, dont {exemple}."
                hud_lignes.append(f"Pepites EDSM: {nb_top}")
                hud_lignes.append(exemple[:24])
            elif anneaux_met > 0:
                suite = "Des anneaux métalliques repérés pour le minage."
                hud_lignes.append("Anneaux metalliques")
            elif nb_corps > nb_corps_edsm + 2:
                suite = "Plusieurs corps ne sont pas encore dans les archives, un scan FSS peut valoir le coup."
                hud_lignes.append("Corps non archives -> FSS")
            else:
                if nb_corps <= 3:
                    suite = "Rien de bien passionnant ici, Commandant."
                else:
                    suite = "Aucune planète précieuse connue dans les archives, mais un FSS peut révéler du biologique."
                hud_lignes.append("RAS dans archives EDSM")

            phrase = ", ".join(morceaux) + ". " + suite
            annoncer_navigation("honk_systeme", phrase, "\n".join(hud_lignes))

        threading.Thread(target=_tache_honk, daemon=True).start()

    repliques_alertes = {
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

    def declencher_alerte(cle_alerte, message_direct=None, detail_hud=None):
        if get_mode_actuel_func and get_mode_actuel_func() != "NORMAL":
            return
        maintenant = time.time()
        if maintenant - derniere_alerte_temps.get(cle_alerte, 0) < 20:
            return
        derniere_alerte_temps[cle_alerte] = maintenant
        phrase = message_direct or random.choice(repliques_alertes.get(cle_alerte, ["Alerte système !"]))
        print(f"[ALERTE AUTONOME - {cle_alerte.upper()}] : {phrase}")
        if on_alerte_hud_func:
            try:
                on_alerte_hud_func(cle_alerte, detail_hud or "")
            except Exception:
                pass
        threading.Thread(target=dire_vocal, args=(phrase,), daemon=True).start()

    while True:
        try:
            # 1. Surveillance de Status.json (Alertes + Vue active pour le HUD)
            if os.path.exists(chemin_status):
                with open(chemin_status, "r", encoding="utf-8") as f:
                    st = json.load(f)

                # Notification de changement de vue (Cockpit / Système / Galaxie / À pied)
                if on_changement_vue_func:
                    vue_actuelle = determiner_vue_ed(st)
                    if vue_actuelle != precedente_vue:
                        precedente_vue = vue_actuelle
                        try:
                            on_changement_vue_func(vue_actuelle)
                        except Exception:
                            pass

                flags = st.get("Flags", 0)
                flags2 = int(st.get("Flags2", 0) or 0)
                est_docke = bool(flags & 1)
                est_a_pied = bool(flags2 & (1 | 8 | 16 | 8192 | 16384)) or ("Oxygen" in st)

                if est_a_pied:
                    precedent_bouclier = None
                    oxy = st.get("Oxygen")
                    sante_pied = st.get("Health")
                    oxy_bas = bool(flags2 & 64) or (isinstance(oxy, (int, float)) and oxy <= 0.30)
                    oxy_crit = isinstance(oxy, (int, float)) and oxy <= 0.15
                    sante_basse = bool(flags2 & 128) or (isinstance(sante_pied, (int, float)) and sante_pied <= 0.40)

                    if oxy_crit and not precedent_oxy_crit:
                        pct_o = int(round(float(oxy) * 100)) if isinstance(oxy, (int, float)) else 15
                        declencher_alerte(
                            "oxygene_critique",
                            f"Alerte critique oxygène à {pct_o} pour cent ! Remontez immédiatement dans le VRS ou le vaisseau !",
                            detail_hud=f"Oxygene: {pct_o}%"
                        )
                    elif oxy_bas and not precedent_oxy_bas:
                        pct_o = int(round(float(oxy) * 100)) if isinstance(oxy, (int, float)) else 30
                        declencher_alerte(
                            "oxygene_bas",
                            f"Attention Commandant, oxygène de combinaison bas à {pct_o} pour cent !",
                            detail_hud=f"Oxygene: {pct_o}%"
                        )
                    precedent_oxy_bas = oxy_bas
                    precedent_oxy_crit = oxy_crit

                    if sante_basse and not precedent_sante_basse:
                        pct_s = int(round(float(sante_pied) * 100)) if isinstance(sante_pied, (int, float)) else 40
                        declencher_alerte(
                            "sante_basse",
                            f"Attention Commandant, santé à pied descendue à {pct_s} pour cent !",
                            detail_hud=f"Sante: {pct_s}%"
                        )
                    precedent_sante_basse = sante_basse
                else:
                    precedent_oxy_bas = False
                    precedent_oxy_crit = False
                    precedent_sante_basse = False

                if not est_docke and not est_a_pied and flags > 0:
                    bouclier_actif = bool(flags & 8)
                    surchauffe = bool(flags & 1048576)
                    carburant_bas = bool(flags & 33554432)
                    interdiction = bool(flags & 8388608)
                    danger = bool(flags & 4194304)  # Bit 22 = BeingInDanger (Bit 26 = 67108864 est InSRV)

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

            # 2. Surveillance de la santé des modules (< 50%)
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
                            declencher_alerte(
                                f"mod_{slot}",
                                f"Attention Commandant, la santé du module {nom_fr} est tombée à {pct} pour cent !",
                                detail_hud=f"{nom_fr}: {pct}%"
                            )
                    elif sante >= 0.50 and slot in modules_deja_alertes:
                        modules_deja_alertes.remove(slot)

            # 3. Surveillance du journal actif
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
                                    declencher_alerte(
                                        "coque",
                                        f"Alerte critique ! Intégrité de la coque descendue à {sante} pour cent !",
                                        detail_hud=f"Integrite: {sante}%"
                                    )
                                elif etype == "ModuleMalfunction":
                                    mod = traduire_nom_module(ev.get("Module", "inconnu"))
                                    declencher_alerte(
                                        "module",
                                        f"Attention, dysfonctionnement critique du module {mod} !",
                                        detail_hud=f"Panne: {mod}"
                                    )
                                elif etype == "FSDJump":
                                    traiter_arrivee_systeme(ev)
                                elif etype == "Scan":
                                    # Capture le statut officiel Frontier WasDiscovered de l'étoile principale
                                    if (
                                        etat_nav.get("systeme")
                                        and etat_nav.get("was_discovered_etoile") is None
                                        and ev.get("StarType")
                                        and "WasDiscovered" in ev
                                    ):
                                        sys_scan = str(ev.get("StarSystem") or "")
                                        if not sys_scan or normaliser_texte(sys_scan) == normaliser_texte(etat_nav["systeme"]):
                                            etat_nav["was_discovered_etoile"] = bool(ev.get("WasDiscovered"))
                                elif etype == "FSSDiscoveryScan":
                                    traiter_honk_systeme(ev)
                            except Exception:
                                continue
        except Exception:
            pass
        time.sleep(0.4)


def lancer_surveillance_alertes(
    get_mode_actuel_func=None,
    on_alerte_hud_func=None,
    on_changement_vue_func=None
):
    """Démarre le thread de surveillance des alertes et de la vue ED en arrière-plan."""
    t = threading.Thread(
        target=surveiller_alertes_autonomes,
        args=(get_mode_actuel_func, on_alerte_hud_func, on_changement_vue_func),
        daemon=True
    )
    t.start()
    return t
