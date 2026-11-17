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


def lire_modules_info() -> dict:
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


def surveiller_alertes_autonomes(get_mode_actuel_func=None):
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

    def declencher_alerte(cle_alerte, message_direct=None):
        if get_mode_actuel_func and get_mode_actuel_func() != "NORMAL":
            return
        maintenant = time.time()
        if maintenant - derniere_alerte_temps.get(cle_alerte, 0) < 20:
            return
        derniere_alerte_temps[cle_alerte] = maintenant
        phrase = message_direct or random.choice(repliques_alertes.get(cle_alerte, ["Alerte système !"]))
        print(f"[ALERTE AUTONOME - {cle_alerte.upper()}] : {phrase}")
        threading.Thread(target=dire_vocal, args=(phrase,), daemon=True).start()

    while True:
        try:
            # 1. Surveillance de Status.json
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
                            declencher_alerte(f"mod_{slot}", f"Attention Commandant, la santé du module {nom_fr} est tombée à {pct} pour cent !")
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
                                    declencher_alerte("coque", f"Alerte critique ! Intégrité de la coque descendue à {sante} pour cent !")
                                elif etype == "ModuleMalfunction":
                                    mod = traduire_nom_module(ev.get("Module", "inconnu"))
                                    declencher_alerte("module", f"Attention, dysfonctionnement critique du module {mod} !")
                            except Exception:
                                continue
        except Exception:
            pass
        time.sleep(0.4)


def lancer_surveillance_alertes(get_mode_actuel_func=None):
    """Démarre le thread de surveillance des alertes en arrière-plan."""
    t = threading.Thread(target=surveiller_alertes_autonomes, args=(get_mode_actuel_func,), daemon=True)
    t.start()
    return t
