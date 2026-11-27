"""Module cerveau de l'IA (OpenAI GPT-4o-mini, Function Calling, Prompts et Mémoire)."""

import json
import os
import re
import threading
import time
from openai import OpenAI

from modules.api_clients import (
    calculer_distance_systemes,
    interroger_edsm_position,
    interroger_edsm_stations,
    interroger_edsm_systemes_proches,
    rechercher_marche_ou_equipement
)
from modules.codex_ed import analyser_systeme_fss, calculer_portefeuille_exploration
from modules.config_loader import (
    CLE_API_OPENAI,
    CMDR_NAME,
    EDSM_API_KEY,
    FICHIER_MEMOIRE,
    NOM_IA,
    PERSONNALITE_IA,
    SYNONYMES_OBJETS,
    SYNONYMES_VERBES,
    VISION_CONFIG
)
from modules.telemetry_ed import (
    analyser_journaux_locaux,
    charger_cache_flotte,
    lire_systeme_actuel_rapide,
    lire_telemetrie_temps_reel,
    normaliser_texte
)

_client_openai = None


def get_openai_client() -> OpenAI:
    """Initialise et retourne le client OpenAI."""
    global _client_openai
    if _client_openai is None:
        _client_openai = OpenAI(api_key=CLE_API_OPENAI)
    return _client_openai


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
    },
    {
        "type": "function",
        "function": {
            "name": "analyser_systeme_fss",
            "description": "Analyse toutes les planètes scannées au FSS/DSS dans le système actuel pour recommander où faire un DSS (planètes terraformables, telluriques, aquatiques, ammoniac non encore cartographiées et leur valeur en crédits), quelles planètes ont du biologique rentable (prédiction Stratum Tectonicas, bonus première empreinte x5, espèces nouvelles), où trouver un matériau/minerai brut en surface (ex: Arsenic, Sélénium, Polonium) ou quels anneaux miner.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filtre_objectif": {
                        "type": "string",
                        "enum": ["tout", "dss", "biologie", "materiaux", "anneaux"],
                        "description": "Type de recommandation recherché ('tout' pour un bilan complet après FSS, 'dss' pour les terraformables/carto, 'biologie' pour l'exobio, 'materiaux' pour les minerais de surface, 'anneaux' pour le minage)."
                    },
                    "filtre_materiau": {
                        "type": "string",
                        "description": "Optionnel : nom d'un matériau de surface précis cherché dans le système (ex: Arsenic, Sélénium, Polonium, Fer, Technétium)."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtenir_portefeuille_exploration",
            "description": "Calcule le montant estimé en crédits des données d'exploration NON ENCORE VENDUES actuellement à bord du vaisseau : Cartographie (Universal Cartographics), Exobiologie (Vista Genomics avec bonus première empreinte x5) et bons Codex (géologie, biologie, astronomie) depuis la dernière vente ou destruction.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]


def executer_outil_ia(nom_fonction: str, arguments_json: str) -> str:
    """Exécute l'outil demandé par OpenAI et retourne le résultat sérialisé en JSON."""
    args = json.loads(arguments_json) if arguments_json else {}
    print(f"[API/Outil] Exécution de {nom_fonction} avec {args}...")

    if nom_fonction == "obtenir_etat_vaisseau_et_ressources":
        donnees = analyser_journaux_locaux()
        if donnees.get("systeme") == "Inconnu" and EDSM_API_KEY:
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
            nb_sauts_max=args.get("nb_sauts_max"),
            rayon_al_max=args.get("rayon_al_max")
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

        for cle, detail in configs.items():
            if cible and normaliser_texte(detail.get("nom", "")) == cible:
                return json.dumps(detail, ensure_ascii=False)
        for cle, detail in configs.items():
            if cible and cible in normaliser_texte(cle):
                return json.dumps(detail, ensure_ascii=False)
        return json.dumps({
            "info": "Configuration détaillée non trouvée dans les journaux récents.",
            "configurations_disponibles": list(configs.keys())
        }, ensure_ascii=False)

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

    elif nom_fonction == "analyser_systeme_fss":
        res = analyser_systeme_fss(
            filtre_objectif=args.get("filtre_objectif", "tout"),
            filtre_materiau=args.get("filtre_materiau", "")
        )
        return json.dumps(res, ensure_ascii=False)

    elif nom_fonction == "obtenir_portefeuille_exploration":
        return json.dumps(calculer_portefeuille_exploration(), ensure_ascii=False)

    return json.dumps({"erreur": "Outil inconnu"})


def charger_journal_de_bord() -> str:
    """Charge le journal de bord persistant ou initialise un message par défaut."""
    if os.path.exists(FICHIER_MEMOIRE):
        try:
            with open(FICHIER_MEMOIRE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return "Première initialisation du vaisseau."


def generer_accueil_initial(memoire_long_terme: str) -> str:
    """Génère la première phrase d'accueil sarcastique au lancement."""
    client = get_openai_client()
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
        return res_accueil.choices[0].message.content
    except Exception as e:
        print(f"[Accueil] Erreur : {e}")
        return f"{NOM_IA} en ligne. Systèmes parés, Commandant."


MOTS_VIDES_COHERENCE = {
    "le", "la", "les", "de", "du", "des", "un", "une", "en", "au", "aux", "et", "ou",
    "sur", "dans", "pour", "par", "avec", "sans", "mon", "ma", "mes", "ton", "ta", "tes",
    "son", "sa", "ses", "ce", "cet", "cette", "ces", "moi", "toi", "vous", "nous", "mode"
}

SYNONYMES_COMMANDES_ED = {
    "acs": ("fss", "scanner", "spectre"),
    "dss": ("surface", "sonde", "sondage", "carto"),
    "phares": ("torche", "lumiere", "lampe", "feux", "phare"),
    "orbite": ("orbites", "ligne", "lignes"),
    "itineraire": ("route", "destination", "saut", "prochain"),
    "combinaison": ("outil", "bio", "biologique", "genetique", "echantillonneur", "decoupeur"),
    "outil": ("outils", "bio", "biologique", "genetique", "echantillonneur", "decoupeur", "energiseur", "analyseur"),
    "ranger": ("rang", "rengain", "cach", "mains"),
    "energiseur": ("energie", "liaison", "recharge"),
    "analyseur": ("profil", "scanner", "composition"),
    "arme": ("armes", "pistolet", "fusil", "canon", "herbe"),
    "armes": ("arme", "groupe", "feu"),
    "recharge": ("recharg", "munitions", "chargeur"),
    "train": ("atterrissage", "train"),
    "cargaison": ("cargo", "ecope", "soute"),
    "recuperateur": ("ecope", "cargo", "cargaison"),
    "emport": ("emports", "point", "points", "armes"),
    "stationnement": ("frein", "parking"),
    "galactique": ("galaxie", "galactique"),
    "systeme": ("systeme", "planetes"),
    "planete": ("planete", "face", "avant", "arriere", "cote"),
    "arriere": ("arriere", "avant", "face", "dos"),
    "ath": ("ath", "interface", "affichage", "hud"),
    "bouclier": ("bouclier", "boucliers", "shield"),
    "nocturne": ("nocturne", "nuit", "vision"),
    "dissipateur": ("dissipateur", "thermique", "chaleur", "heatsink"),
    "paillettes": ("paillette", "paillettes", "chaff"),
    "sante": ("soin", "soigne", "medkit", "kit", "sante"),
    "soigne": ("soin", "soigne", "medkit", "kit", "sante"),
    "furtif": ("furtif", "furtive", "silencieux", "silent"),
    "suivant": ("suivant", "suivante", "autre", "chang", "bascul"),
    "suivante": ("suivant", "suivante", "autre", "chang"),
    "secondaire": ("secondaire", "autre", "deuxieme"),
    "principale": ("principale", "principal", "arme"),
    "change": ("chang", "bascul", "autre", "invers"),
    "quitter": ("quitt", "sort", "ferm", "coup", "arret", "kit", "keep"),
    "activer": ("activ", "lanc", "pass", "met", "allum", "ouvr", "affich"),
    "desactiver": ("desactiv", "coup", "etein", "enlev", "masqu", "ferm", "arret"),
    "afficher": ("affich", "montr", "ouvr", "activ", "met", "remet"),
    "supprimer": ("supprim", "enlev", "masqu", "cach", "coup", "retir", "desactiv"),
    "sortir": ("sort", "deploi", "ouvr", "baiss", "met"),
    "rentrer": ("rentr", "relev", "ferm", "rang", "retract"),
    "allumer": ("allum", "activ", "met"),
    "eteindre": ("etein", "coup", "desactiv"),
    "enleve": ("enlev", "ferm", "masqu", "desactiv", "cach", "retir", "quitt", "effac"),
    "roue": ("roue", "inventaire", "emoticome", "emoticone", "emote", "insight"),
    "emoticomes": ("emoticome", "emoticone", "emote"),
    "inventaire": ("inventaire", "roue"),
    "insight": ("insight", "roue", "menu", "acces"),
    "menu": ("menu", "roue", "insight"),
    "ouvre": ("ouvr", "affich", "activ", "lanc", "montr", "met"),
    "ferme": ("ferm", "enlev", "masqu", "desactiv", "cach", "retir", "quitt", "effac"),
    "effacer": ("effac", "supprim", "vid", "retir"),
    "ejecter": ("eject", "lanc", "activ"),
    "utilise": ("utilis", "charg", "prend", "met", "active", "batterie", "cellule")
}


def _generer_formes_verbe(verbe_inf: str) -> set[str]:
    """Génère automatiquement les formes conjuguées courantes (impératif/présent) d'un verbe français."""
    v = normaliser_texte(verbe_inf)
    formes = {v}
    if not v:
        return formes

    # Cas particuliers fréquents du 3e groupe
    irreguliers = {
        "sortir": {"sors", "sort", "sortez", "sortons"},
        "prendre": {"prends", "prend", "prenez", "prenons"},
        "mettre": {"mets", "met", "mettez", "mettons"},
        "remettre": {"remets", "remet", "remettez", "remettons"},
        "eteindre": {"eteins", "eteint", "eteignez", "eteignons"},
        "ouvrir": {"ouvre", "ouvres", "ouvrez", "ouvrons"},
        "retablir": {"retabli", "retablis", "retablit", "retablissez"},
        "deployer": {"deploie", "deploies", "deployez"},
    }
    if v in irreguliers:
        formes.update(irreguliers[v])
        return formes

    if v.endswith("er") and len(v) > 3:
        rad = v[:-2]
        formes.update({rad + "e", rad + "es", rad + "ez", rad + "ons"})
    elif v.endswith("ir") and len(v) > 3:
        rad = v[:-2]
        formes.update({rad + "i", rad + "is", rad + "it", rad + "e", rad + "ez"})
    elif v.endswith("re") and len(v) > 3:
        rad = v[:-2]
        formes.update({rad + "s", rad, rad + "e", rad + "ez"})
    return formes


def _familles_verbe(mot_verbe: str, table_verbes: dict | None = None) -> set[str]:
    """Retourne les familles synonymes auxquelles appartient un verbe (conjugué ou infinitif)."""
    m = normaliser_texte(mot_verbe)
    if not m:
        return set()
    table = table_verbes if table_verbes is not None else SYNONYMES_VERBES
    trouvees = set()
    for famille, liste_verbes in table.items():
        for v_inf in liste_verbes:
            if m in _generer_formes_verbe(v_inf):
                trouvees.add(famille)
                break
    return trouvees


def _normaliser_objet_commande(texte_objet: str, table_objets: dict | None = None) -> str:
    """Normalise l'objet d'une commande (sans articles ni pluriels superflus + alias d'objets)."""
    obj = normaliser_texte(texte_objet).replace("'", " ").replace("’", " ")
    obj = re.sub(r"[^a-z0-9\s]", " ", obj)
    obj = re.sub(r"\s+", " ", obj).strip()
    if not obj:
        return ""

    aliases = table_objets if table_objets is not None else SYNONYMES_OBJETS
    if obj in aliases:
        obj = normaliser_texte(aliases[obj]).replace("'", " ")

    mots_ignores = {"le", "la", "les", "l", "de", "du", "des", "d", "un", "une", "mode"}
    mots = [m for m in obj.split() if m not in mots_ignores]
    canon = " ".join(mots)
    if canon in aliases:
        canon = normaliser_texte(aliases[canon]).replace("'", " ")
        mots = [m for m in canon.split() if m not in mots_ignores]

    # Tolère le pluriel simple sur les noms longs (ex: 'orbites' <-> 'orbite', 'phares' <-> 'phare')
    mots_sing = [m[:-1] if len(m) >= 5 and m.endswith("s") and m not in ("acs", "fss", "dss") else m for m in mots]
    return " ".join(mots_sing)


def resoudre_commande_voiceattack(
    nom_action_va: str,
    lignes_cmd_vaisseau: list[str],
    table_verbes: dict | None = None,
    table_objets: dict | None = None
) -> str | None:
    """Résout une commande retournée par le LLM vers son nom exact dans commandes_vaisseau.txt.

    Ordre de priorité :
    1. Correspondance exacte (insensible à la casse/accents/'_'), y compris 'Outil suivant'.
    2. Tolérance infinitif simple ('Affiche Orbite' -> 'Afficher Orbite').
    3. Correspondance par famille de verbes synonymes + objet équivalent
       (ex: 'Masque Roue d'inventaire' -> 'Enlève Roue d'inventaire', 'Affiche Roue Insight' -> 'Ouvre Menu Insight').
    4. Sécurité systématique 'Range Outil' -> 'Ranger Outil'.
    """
    if not nom_action_va:
        return None

    nom_action_resolu = None
    action_norm = normaliser_texte(nom_action_va.replace("_", " "))

    if action_norm == "outil suivant":
        return "Outil suivant"

    # 1. Correspondance exacte
    for cmd_ref in lignes_cmd_vaisseau:
        if normaliser_texte(cmd_ref.replace("_", " ")) == action_norm:
            nom_action_resolu = cmd_ref
            break

    # 2. Tolérance oubli du 'r' final sur le 1er verbe
    if not nom_action_resolu and action_norm:
        mots_act = action_norm.split()
        if mots_act:
            action_inf = " ".join([mots_act[0] + "r"] + mots_act[1:])
            for cmd_ref in lignes_cmd_vaisseau:
                if normaliser_texte(cmd_ref.replace("_", " ")) == action_inf:
                    nom_action_resolu = cmd_ref
                    break

    # 3. Correspondance par famille de verbes synonymes + même objet canonique
    if not nom_action_resolu and action_norm:
        mots_act = action_norm.split()
        if len(mots_act) >= 2:
            fams_act = _familles_verbe(mots_act[0], table_verbes)
            obj_act = _normaliser_objet_commande(" ".join(mots_act[1:]), table_objets)
            if fams_act and obj_act:
                for cmd_ref in lignes_cmd_vaisseau:
                    ref_norm = normaliser_texte(cmd_ref.replace("_", " "))
                    mots_ref = ref_norm.split()
                    if len(mots_ref) < 2:
                        continue
                    fams_ref = _familles_verbe(mots_ref[0], table_verbes)
                    if not (fams_act & fams_ref):
                        continue
                    obj_ref = _normaliser_objet_commande(" ".join(mots_ref[1:]), table_objets)
                    if obj_ref and obj_ref == obj_act:
                        nom_action_resolu = cmd_ref
                        break

    # 4. Sécurité : "Range Outil" (sans 'r') sort l'arme utilitaire (Ctrl+I),
    # alors que "Ranger Outil" (avec 'r') rengaine vraiment (Ctrl+^) !
    if nom_action_resolu and normaliser_texte(nom_action_resolu) == "range outil":
        for cmd_ref in lignes_cmd_vaisseau:
            if normaliser_texte(cmd_ref) == "ranger outil":
                nom_action_resolu = cmd_ref
                break

    return nom_action_resolu


def verifier_autorisation_mode_special(texte_pilote: str, mode_special: str) -> bool:
    """Vérifie qu'un passage en MODE_EPELLATION ou MODE_DICTEE est explicitement demandé par le pilote."""
    t = normaliser_texte(texte_pilote).replace("'", " ").replace("’", " ")
    if mode_special == "EPELLATION":
        return any(k in t for k in ("epel", "lettre par lettre", "lettre a lettre"))
    if mode_special == "DICTEE":
        return any(k in t for k in ("dict", "ecri", "redig", "message"))
    return True


def verifier_coherence_commande_pilote(texte_pilote: str, nom_commande: str) -> bool:
    """Filet de sécurité lexical : bloque une commande devinée sur une phrase incomprise ou absurde.

    Exige qu'au moins un mot significatif (ou synonyme de domaine) de la commande VoiceAttack
    se retrouve dans la phrase prononcée par le pilote.
    """
    t = normaliser_texte(texte_pilote).replace("'", " ").replace("’", " ")
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if not t:
        return False

    cmd_norm = normaliser_texte(nom_commande).replace("'", " ").replace("’", " ")
    cmd_norm = re.sub(r"[^a-z0-9\s]", " ", cmd_norm)

    # Garde-fou anti-inversion : 'Ranger Outil/Arme' exige une intention de rangement (évite 'Sur/Pour l'outil' -> Ranger)
    if cmd_norm in ("ranger outil", "ranger arme"):
        return any(v in t for v in ("rang", "rengain", "cach", "rentr", "mains", "enlev", "pose", "remet", "orange"))

    # Garde-fou anti-inversion : ne jamais activer l'ACS si le pilote tente de le quitter ('quitte/kit/keep')
    if cmd_norm == "activer mode acs" and re.match(r"^(?:quitt\w*|kit\w*|keep\w*)\b", t):
        return False

    mots_cmd = [m for m in cmd_norm.split() if len(m) >= 3 and m not in MOTS_VIDES_COHERENCE]
    if not mots_cmd:
        return True

    mots_pilote = t.split()
    for mc in mots_cmd:
        # 1. Correspondance directe ou par radical (4+ car. pour absorber conjugaisons/pluriels)
        radical = mc[:4] if len(mc) >= 5 else mc
        if any(mp.startswith(radical) or mc.startswith(mp[:4]) for mp in mots_pilote if len(mp) >= 3):
            return True
        # 2. Correspondance via synonymes de domaine Elite Dangerous
        for syn in SYNONYMES_COMMANDES_ED.get(mc, ()):
            if syn in t:
                return True

    return False


def _detecter_outil_obligatoire(texte_actuel: str) -> str | None:
    """Force l'appel Function Calling sur les questions d'analyse système ou de portefeuille.

    Évite que GPT-4o-mini réponde de mémoire avec d'anciennes données ou lance l'ACS par erreur.
    """
    t = normaliser_texte(texte_actuel).replace("'", " ").replace("’", " ")
    t = re.sub(r"\s+", " ", t).strip()
    if not t:
        return None

    # 1. Portefeuille d'exploration (tolère les variantes Whisper "explo", "explos", "expo", "exploration")
    if (
        ("portefeuille" in t and any(m in t for m in ("explo", "expo", "carto", "bio", "codex", "donnee", "valeur", "montant", "combien")))
        or re.search(r"\b(?:combien|valeur|montant)\b.*\b(?:donnees d exploration|exploration|exobiologie|vista genomics|universal cartographics)\b", t)
    ):
        return "obtenir_portefeuille_exploration"

    # 2. Analyse des planètes / choses intéressantes dans le système actuel après FSS
    if (
        re.search(r"\b(?:interessant\w*|vaut le coup|valent le coup|a scanner|a cartographier|a explorer)\b.*\b(?:systeme|ici|planete|corps)\b", t)
        or re.search(r"\b(?:planete\w*|chose\w*|quelque chose|truc\w*)\b.*\b(?:interessant\w*|vaut le coup|valent le coup)\b", t)
        or re.search(r"\b(?:bilan|analyse|resume|valeur|rapporte)\b.*\b(?:systeme|fss|acs)\b", t)
        or re.search(r"\b(?:ou faire un dss|quelles? planetes?.*dss|y a t il.*(?:terraformable|biologique|exobio|materiau|anneau))", t)
    ):
        return "analyser_systeme_fss"

    return None


def construire_instructions_systeme(
    memoire_long_terme: str,
    liste_commandes_va: str,
    systeme_actuel: str = ""
) -> str:
    """Compose le prompt système complet d'Oscar."""
    bloc_position = (
        f"POSITION TEMPS RÉEL : Le Commandant se trouve actuellement dans le système '{systeme_actuel}'. "
        "Si les échanges précédents de la conversation parlent d'un autre système ou d'anciennes planètes, "
        "considère-les comme OBSOLÈTES et mets impérativement tes données à jour en appelant l'outil correspondant. "
        if systeme_actuel
        else ""
    )
    return (
        f"Tu es l'IA de bord {NOM_IA} du Commandant {CMDR_NAME}. Personnalité : {PERSONNALITE_IA} "
        f"ARCHIVES : {memoire_long_terme} "
        f"{bloc_position}"
        "Tu disposes d'outils pour consulter l'état du vaisseau (crédits, rangs, position, planète, flotte complète, équipement des vaisseaux, matériaux), "
        "analyser le système actuel après FSS, calculer le portefeuille d'exploration et consulter EDSM/Spansh. Utilise-les dès que le pilote pose une question sur sa situation. "
        "Prononce toujours 'années-lumière' et 'secondes-lumière' en toutes lettres. "
        "FORMAT VOCAL STRICT : réponds UNIQUEMENT en texte brut naturel parlé ; N'UTILISE JAMAIS de gras (**), de listes à puces (- ), de numérotation ni de parenthèses abrégées comme '(10,1 M Cr)'. "
        "RÈGLE ABSOLUE : Ne te fie JAMAIS aux ARCHIVES ni à l'historique de conversation pour la position, le système actuel, les planètes intéressantes, le portefeuille d'exploration, les crédits, les matériaux, les rangs ou la flotte. Appelle OBLIGATOIREMENT l'outil correspondant à chaque question pour lire les données en temps réel. "
        "RÈGLE QUESTION VS COMMANDE : Toute question d'information ('est-ce que tu vois...', 'y a-t-il...', 'combien...', 'où est...', 'quel est...', 'qu'est-ce que...') ne doit JAMAIS déclencher de balise [EXECUTE:...] (réponds ou appelle un outil JSON uniquement). Seule une demande d'action explicite (ex: 'sors le train', 'peux-tu ouvrir la carte système ?') peut utiliser [EXECUTE:...]. "
        "Si une donnée n'est pas présente dans la télémétrie (comme la vitesse instantanée en m/s, le temps d'arrivée exact ou l'altitude lorsque le capteur est inactif), ne l'invente JAMAIS : précise simplement avec sarcasme que l'ordinateur de bord du vaisseau ne transmet pas cette télémétrie. "
        "Pour l'état On/Off ou la santé d'un module, précise toujours si l'information provient du 'dernier Loadout' (Elite Dangerous ne transmet pas en temps réel dans ModulesInfo.json lorsqu'un module est désactivé manuellement en vol). "
        "Quand tu donnes un résultat de commerce ou d'équipement, cite TOUJOURS pour la meilleure station : son nom, le système, le prix unitaire en crédits, le stock ou la demande en tonnes, et le nombre de sauts approximatifs (ne cite pas les stations secondaires sauf si demandé). "
        "Si le résultat de commerce ou d'équipement contient 'hors_rayon_initial': true, précise TOUJOURS d'abord que tu n'as rien trouvé dans la distance initiale demandée (en citant le rayon initial en années-lumière), puis annonce que la station la plus proche se trouve à la distance indiquée. "
        "Après un FSS, si le Commandant demande quelles planètes ou choses sont intéressantes dans le système, combien rapporte ce système, où faire un DSS, s'il y a des terraformables, du biologique, des matériaux ou des anneaux à miner, appelle OBLIGATOIREMENT la fonction JSON analyser_systeme_fss (via Function Calling, JAMAIS dans une balise [EXECUTE:...] et JAMAIS en ouvrant l'ACS !). "
        "Si le Commandant demande simplement où chercher une plante ou un genre précis sur la planète actuelle (ex: 'où trouver du bactérium ?'), réponds directement avec un conseil d'habitat/terrain (ex: plaines plates pour Bacterium, zones rocheuses pour Frutexa) SANS jamais exécuter de commande de vaisseau. "
        "Dans ta réponse après analyser_systeme_fss : "
        "(1) cite le nom du système UNE SEULE FOIS au début, puis utilise uniquement les noms courts ('Planète 1', 'Lune 8 A') dans l'ordre exact retourné (aligné avec le HUD et le panneau Navigation) ; "
        "(2) lis les montants EXCLUSIVEMENT depuis les champs '*_vocal' / 'estimation_vocale' en toutes lettres (sans jamais confondre le total du système avec une planète seule) ; "
        "(3) donne la valeur carto déjà acquise (deja_acquis_carto_vocal), les cibles prioritaires (top 3-4 max : nom court, distance arrondie en secondes-lumière et estimation réaliste), et mentionne les matériaux rares s'il y en a ; "
        "(4) quand une planète n'a qu'1 seul signal biologique (signaux_biologiques == 1), dis toujours 'soit ... soit ...' (JAMAIS 'et' entre deux genres). Reste concis (3 à 4 phrases fluides max). "
        "Si le Commandant demande combien il a en portefeuille d'exploration (données cartographiques, exobiologie, géologie ou bons Codex non encore vendus à bord), appelle OBLIGATOIREMENT obtenir_portefeuille_exploration et lis les champs 'vocal' / 'total_general_vocal' en détaillant Cartographie, Exobiologie, bons Codex et total. "
        "Si le Commandant demande EXPLICITEMENT à écrire, dicter du texte ou passer en mode dictée (ex: 'mode dictée', 'active la dictée', 'je veux dicter'), réponds très brièvement et ajoute [MODE_DICTEE] à la fin (SANS jamais exécuter de commande de vaisseau). N'ajoute JAMAIS [MODE_DICTEE] pour une photo ou une question ordinaire. "
        "Si le Commandant demande EXPLICITEMENT à épeler ou passer en mode lettre à lettre (ex: 'mode épellation', 'active l'épellation', 'lettre par lettre'), réponds très brièvement et ajoute [MODE_EPELLATION] à la fin. N'ajoute JAMAIS [MODE_EPELLATION] sur une phrase incomprise ou une commande de vaisseau. "
        "RÈGLE ANTI-DEVINETTE SUR COMMANDES : Pour exécuter une commande physique [EXECUTE:...], la phrase du pilote doit contenir un VERBE D'ACTION clair (prends, sors, active, allume, éteins, ouvre, affiche, quitte, rentre, rengaine, range, recharge, change, bascule, cible...) et un objet cohérent. "
        "Si tu reçois une phrase déformée, tronquée ou incompréhensible (erreur de micro) qui ressemble à une tentative de commande mais dont le sens n'est pas certain, NE DEVINE JAMAIS de commande [EXECUTE:...] et réponds sobrement sans fioriture : 'Je n'ai pas compris, tu peux répéter ?' "
        "Si le pilote demande EXPLICITEMENT une action physique claire sur le vaisseau ou à pied, fais une réponse très courte (5-6 mots max) "
        "AU PRÉSENT OU AU PASSÉ COMPOSÉ (ex: 'C'est fait !', 'Carte ouverte !', 'FSS activé !', 'Orbites masquées !') — JAMAIS au futur ('je vais...', 'seront...'), car l'action s'exécute immédiatement ! "
        "Puis ajoute à la fin l'action EXACTE (avec espaces, sans jamais remplacer par des underscores '_') entre crochets parmi : "
        f"{liste_commandes_va} Exemple : [EXECUTE:Ouvrir Carte Galactique]. N'écris JAMAIS le nom d'une fonction/outil Python (comme analyser_systeme_fss ou obtenir_ma_flotte) dans [EXECUTE:...]. "
        "IMPORTANT : Quand tu ajoutes une balise [EXECUTE:...], tu EXÉCUTES réellement la commande sur le vaisseau ! Ne dis JAMAIS 'je ne peux pas le faire', 'je ne peux pas l'ouvrir' ou 'une tâche que je ne peux pas exécuter' ! "
        "RÈGLE DE SÉCURITÉ VITALE : N'ajoute JAMAIS de balise [EXECUTE:...] pour une simple remarque ou fin de discussion (ex: 'c'est bon j'y vais', 'merci', 'ok'). "
        "N'exécute JAMAIS [EXECUTE:Passer Mode Furtif] ni [EXECUTE:Larguer Cargaison] sauf ordre littéral et explicite du Commandant. "
        "ÉQUIVALENCES DE VERBES (utilise ces familles de synonymes pour trouver la commande exacte dans la liste, y compris conjugués à l'impératif) : "
        "Ouvrir/Activer/Afficher/Lancer/Éjecter/Mettre/Allumer ; Fermer/Désactiver/Enlever/Masquer/Cacher/Supprimer/Effacer/Couper/Éteindre/Quitter ; "
        "Sortir/Prendre/Équiper/Déployer ; Ranger/Rengainer/Rentrer/Rétracter ; Changer/Basculer/Alterner ; Utiliser/Charger/Recharger. "
        "Exemples de correspondance stricte : 'afficher les orbites' -> [EXECUTE:Afficher Orbite] ; 'masquer/enlever/couper les orbites' -> [EXECUTE:Supprimer Orbite] ; "
        "'allumer les phares / la torche / la lampe' -> [EXECUTE:Allumer Phares] ; 'éteindre les phares / la torche / la lampe' -> [EXECUTE:Eteindre Phares] ; "
        "'afficher/activer/réactiver/rétablir l'ATH' -> [EXECUTE:Activer ATH] ; 'désactiver/masquer/enlever/couper l'ATH' -> [EXECUTE:Désactiver ATH] ; "
        "'afficher/ouvrir/activer/lancer le FSS ou l'ACS' -> [EXECUTE:Activer Mode ACS] (uniquement FSS/ACS, JAMAIS pour le DSS qui se tire au groupe d'armes) ; 'quitter le FSS ou l'ACS' -> [EXECUTE:Quitter ACS] ; 'quitter le DSS' -> [EXECUTE:Quitter DSS] ; "
        "'afficher/ouvrir la roue d'inventaire' -> [EXECUTE:Affiche Roue d'inventaire] ; 'enlever/fermer/masquer/désactiver la roue d'inventaire' -> [EXECUTE:Enlève Roue d'inventaire] ; "
        "'afficher/ouvrir la roue d'émoticônes' -> [EXECUTE:Affiche Roue d'émoticomes] ; 'enlever/fermer/masquer/désactiver la roue d'émoticônes' -> [EXECUTE:Enlève Roue d'émoticomes] ; "
        "'afficher/ouvrir la roue ou le menu Insight' -> [EXECUTE:Ouvre Menu Insight] ; 'enlever/fermer/masquer/désactiver la roue ou le menu Insight' -> [EXECUTE:Ferme Menu Insight] ; "
        "'utiliser/charger une batterie / cellule d'énergie à pied' -> [EXECUTE:Utilise Cellule Energie] ; "
        "SÉPARATION STRICTE OUTILS VS ARMES À PIED (ne jamais dégainer une arme si le pilote demande un outil !) : "
        "OUTILS : 'sors/prends l'outil de la combinaison / l'outil bio / l'échantillonneur génétique / l'échantillonneur' -> [EXECUTE:Prend Outil Combinaison] ; "
        "'sors/prends l'analyseur de profil / l'analyseur' -> TOUJOURS [EXECUTE:Active Analyseur Profil] ; "
        "'sors/prends l'énergiseur' -> TOUJOURS [EXECUTE:Active énergiseur] (JAMAIS Prend Outil Combinaison) ; "
        "'change/bascule le mode de l'outil' -> [EXECUTE:Change Mode Outil] ; "
        "'prends l'autre outil / l'outil suivant' -> [EXECUTE:Outil suivant] ; "
        "'rengaine/cache/range l'outil' -> [EXECUTE:Ranger Outil] (TOUJOURS avec le 'r', JAMAIS 'Range Outil'). "
        "ARMES : 'sors/prends l'arme / l'arme principale' -> [EXECUTE:Arme principale] ; "
        "'sors/prends l'arme secondaire' -> [EXECUTE:Arme secondaire] ; "
        "'prends l'autre arme / change d'arme' -> [EXECUTE:Change Arme] ; "
        "'recharge l'arme' -> [EXECUTE:Recharge Arme] ; "
        "'prends l'arme suivante' -> [EXECUTE:Arme suivante] ; "
        "'rengaine/cache/range l'arme' -> [EXECUTE:Ranger Arme]. "
        f"Date et heure actuelles : {time.strftime('%d/%m/%Y %H:%M')}. "
    )


def _alleger_resultat_outil_pour_llm(nom_outil: str, resultat_json: str) -> str:
    """Épure les entiers bruts redondants dans le JSON envoyé à GPT-4o-mini pour une lecture vocale exacte.

    Le HUD reçoit toujours les données brutes complètes AVANT cet allègement.
    """
    if nom_outil not in ("obtenir_portefeuille_exploration", "analyser_systeme_fss"):
        return resultat_json
    try:
        data = json.loads(resultat_json)
        if not isinstance(data, dict) or "erreur" in data:
            return resultat_json

        if nom_outil == "obtenir_portefeuille_exploration":
            uc = data.get("cartographie_universal_cartographics") or {}
            vg = data.get("exobiologie_vista_genomics") or {}
            cx = data.get("bons_codex") or {}
            epure = {
                "total_general_vocal": data.get("total_general_vocal", "0 crédit"),
                "cartographie_universal_cartographics": {
                    "vocal": uc.get("vocal", "0 crédit"),
                    "nb_corps_scannes": uc.get("nb_corps_scannes", 0),
                    "nb_dss_complets": uc.get("nb_dss_complets", 0),
                    "nb_systemes": uc.get("nb_systemes", 0),
                    "depuis": uc.get("depuis", "")
                },
                "exobiologie_vista_genomics": {
                    "vocal": vg.get("vocal", "0 crédit"),
                    "nb_especes_pretes": vg.get("nb_especes_pretes", 0),
                    "nb_especes_en_cours": vg.get("nb_especes_en_cours", 0),
                    "especes_pretes": [
                        {"espece": e.get("espece"), "bonus_x5": e.get("bonus_x5", False)}
                        for e in (vg.get("details") or [])
                    ],
                    "depuis": vg.get("depuis", "")
                },
                "bons_codex": {
                    "vocal": cx.get("vocal", "0 crédit"),
                    "nb_entrees": cx.get("nb_entrees", 0)
                }
            }
            return json.dumps(epure, ensure_ascii=False)

        if nom_outil == "analyser_systeme_fss":
            bilan = data.get("bilan_financier")
            if isinstance(bilan, dict):
                data["bilan_financier"] = {
                    k: v for k, v in bilan.items() if k.endswith("_vocal")
                }
            return json.dumps(data, ensure_ascii=False)
    except Exception:
        pass
    return resultat_json


def executer_echange_openai(
    texte_actuel: str,
    memoire_long_terme: str,
    historique_conversation: list,
    liste_commandes_va: str,
    on_outil_execute_func=None
) -> str:
    """Interroge OpenAI avec Function Calling et résout les éventuels appels d'outils."""
    client = get_openai_client()
    systeme_actuel = lire_systeme_actuel_rapide()
    instructions = construire_instructions_systeme(
        memoire_long_terme,
        liste_commandes_va,
        systeme_actuel=systeme_actuel
    )
    messages_api = [{"role": "system", "content": instructions}] + historique_conversation + [{"role": "user", "content": texte_actuel}]

    outil_force = _detecter_outil_obligatoire(texte_actuel)
    choix_outil = {"type": "function", "function": {"name": outil_force}} if outil_force else "auto"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_api,
        tools=OUTILS_OPENAI,
        tool_choice=choix_outil
    )
    message_reponse = response.choices[0].message

    if message_reponse.tool_calls:
        messages_api.append(message_reponse)
        for tool_call in message_reponse.tool_calls:
            nom_outil = tool_call.function.name
            args_str = tool_call.function.arguments
            resultat_outil = executer_outil_ia(nom_outil, args_str)

            # Transmission des données brutes factuelles au HUD (sans sarcasme IA)
            if on_outil_execute_func:
                try:
                    args_dict = json.loads(args_str) if args_str else {}
                    donnees_brutes = json.loads(resultat_outil)
                    on_outil_execute_func(nom_outil, args_dict, donnees_brutes, texte_actuel)
                except Exception:
                    pass

            messages_api.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": _alleger_resultat_outil_pour_llm(nom_outil, resultat_outil)
            })
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_api
        )
        return second_response.choices[0].message.content

    contenu_direct = message_reponse.content or ""
    # Filet de sécurité : si GPT-4o-mini a écrit par erreur [EXECUTE:analyser_systeme_fss] au lieu d'appeler l'outil
    if "analyser_systeme_fss" in contenu_direct.lower():
        resultat_outil = executer_outil_ia("analyser_systeme_fss", "{}")
        if on_outil_execute_func:
            try:
                on_outil_execute_func("analyser_systeme_fss", {}, json.loads(resultat_outil), texte_actuel)
            except Exception:
                pass
        messages_api.append({
            "role": "system",
            "content": (
                "Voici le résultat réel de l'outil analyser_systeme_fss pour le système actuel. "
                "Réponds maintenant directement au Commandant avec ces données exactes (sans aucune balise [EXECUTE:...]) :\n"
                + resultat_outil
            )
        })
        rattrapage = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_api
        )
        return rattrapage.choices[0].message.content

    return contenu_direct


def _construire_instructions_vision_ed(memoire_long_terme: str, vision_directe: bool = False) -> str:
    """Construit le prompt système d'Oscar pour l'analyse visuelle enrichie Elite Dangerous."""
    intro = (
        "Tu regardes directement en temps réel par la verrière, la caméra libre ou la visière du Commandant "
        "(ne mentionne jamais de capture d'écran ni d'image envoyée). "
        if vision_directe
        else "Tes capteurs optiques de bord viennent d'analyser en temps réel ce qui s'affiche devant le Commandant. "
             "Réponds comme si tu regardais directement par la verrière, la caméra ou la visière (ne mentionne jamais d'IA locale ni de capture d'écran). "
    )
    regle_hud = (
        "6. Ajoute tout à la fin de ta réponse une balise [HUD: synthèse factuelle ultra-courte séparée par ' | '] "
        "(ex: [HUD: Cheminee de lave | Magma silicate | 0.22G] ou [HUD: Boucle de Barnard | ~420 AL]). "
        "Cette balise ne sera pas prononcée à voix haute : écris-la de façon factuelle sans humour."
        if vision_directe
        else ""
    )
    return (
        f"Tu es l'IA de bord {NOM_IA} du Commandant {CMDR_NAME}. Personnalité : {PERSONNALITE_IA} "
        f"ARCHIVES : {memoire_long_terme} "
        f"{intro}"
        "RÈGLES STRICTES : "
        "1. Base-toi uniquement sur ce qui est visible et sur le contexte scientifique Elite Dangerous fourni (ne mentionne jamais une température en Kelvin négative, impossible physiquement). "
        "2. Prononce toujours 'années-lumière' et 'secondes-lumière' en toutes lettres dans le texte parlé. "
        "3. CALCUL DE TEMPS DE TRAJET : Le chrono Elite Dangerous au format M:SS (2 nombres, ex: '3:14' ou '0:06') signifie TOUJOURS minutes:secondes (jamais heures:minutes ; les heures n'apparaissent qu'avec 3 nombres H:MM:SS). "
        "Si tu disposes de la distance ET de la vitesse, vérifie toujours avec distance / vitesse "
        "(1 c = 1 seconde-lumière par seconde = 299 792 km/s ; 1 ksl = 1 000 secondes-lumière ; 1 Mm = 1 000 km ; 1 année-lumière = 31 557 600 secondes-lumière). "
        "4. GÉOLOGIE & EXOBIOLOGIE ELITE DANGEROUS ODYSSEY : "
        "Croise TOUJOURS ce qui est visible avec les données du Scan planétaire fournies (Volcanisme exact, Atmosphère, Signaux et Genres exobiologie). "
        "En géologie : ne parle de cheminée/évent de lave QUE si tu vois réellement une lueur ou un jet orange-rouge incandescent de magma sur l'image (jamais sur un simple rocher ni sur une planète glacée à magma d'eau, qui produit plutôt des geysers ou fumerolles de vapeur/glace). "
        "En exobiologie : sois STRICTEMENT HONNÊTE et ne cède JAMAIS au biais de confirmation quand le pilote demande 'est-ce que c'est du bactérium / une plante ?'. "
        "Un rocher, caillou ou éboulis présentant du relief 3D, des arêtes et une ombre portée n'est JAMAIS du Bacterium (le Bacterium est une tache/flaque 100 % plate collée à la texture du sol, sans aucun relief). Si tu ne vois qu'un rocher ou rien d'organique clair, dis franchement NON avec humour ! "
        "Quand un organisme est réellement visible, appuie-toi sur les 'Fiches Codex Exobiologie' fournies (apparence, genres présents, prix Vista Genomics, distance d'échantillonnage) pour l'identifier précisément. "
        "HISTORIQUE PERSONNEL CODEX CMDR & PREMIÈRE DÉCOUVERTE : "
        "Ne mentionne le statut d'une planète ou le bonus Première Empreinte x5 QUE si la ligne 'Statut découverte planète' est présente dans le contexte (jamais lorsque le pilote observe le ciel ou une nébuleuse en vol). "
        "Quand le Commandant regarde une espèce biologique ou un phénomène géologique et que les fiches Codex indiquent son statut personnel : "
        "- si 'DÉJÀ RENCONTRÉ' / 'DÉJÀ VU' : glisse une pique du style 'rien de nouveau, tu as déjà croisé ça !' ; "
        "- si 'NOUVEAU POUR LE COMMANDANT' : signale-lui que c'est une première pour lui ! Et croise avec 'Statut découverte planète' : si un autre Commandant a déjà posé le pied ici, taquine-le ('belle découverte personnelle, mais tu n'es pas le premier malheureusement !') ; si la planète est vierge ('Première Empreinte x5'), félicite-le en rappelant le bonus x5 Vista Genomics ! "
        "5. ASTRONOMIE ELITE DANGEROUS : "
        "Croise OBLIGATOIREMENT la COULEUR et la FORME visibles sur l'image avec le champ descriptif des 'Grandes nébuleuses Elite Dangerous proches de ta position' fournies dans le contexte : "
        "une nébuleuse ROUGE/ORANGÉE (grand arc = Boucle de Barnard ; tache rose/blanche au cœur = Nébuleuse d'Orion ; nuage rouge-orangé = Nébuleuse de la Flamme, Californie, Rosette ou Amérique du Nord) n'est JAMAIS la Nébuleuse de la Tête de Sorcière (Witch Head, qui est bleutée-violette) ! "
        "Ne cède JAMAIS au biais de confirmation : si le pilote demande 'est-ce que cette nébuleuse rouge est la Tête de Sorcière ?', réponds franchement NON (la Tête de Sorcière est bleue) et propose la vraie candidate rouge de la liste fournie ! "
        "Autres repères : grande bande lumineuse = Voie Lactée ; nuage sombre = Sac à Charbon ; nuage bleuté isolé = Grand ou Petit Nuage de Magellan ; petite spirale = galaxie d'Andromède. Cite toujours les nébuleuses connues en français. "
        "Ignore le petit encart HUD d'Oscar dans un coin et les éventuelles pop-ups Windows. "
        "Reste ultra-concis (1 à 2 phrases parlées maximum), sarcastique comme à ton habitude, en texte brut naturel sans gras ni liste. "
        f"{regle_hud}"
    )


def executer_echange_vision_openai(
    question_pilote: str,
    analyse_visuelle: str,
    contexte_jeu: dict,
    memoire_long_terme: str,
    historique_conversation: list,
    bloc_contexte_scientifique: str = "",
    ignorer_historique: bool = False
) -> str:
    """Transmet uniquement le texte de l'analyse visuelle locale (Ollama) à Oscar (0 token image)."""
    client = get_openai_client()
    instructions_vision = _construire_instructions_vision_ed(memoire_long_terme, vision_directe=False)

    contexte_txt = bloc_contexte_scientifique or (
        f"Vue {(contexte_jeu or {}).get('vue', 'écran')}, "
        f"Système {(contexte_jeu or {}).get('systeme', 'Inconnu')}, "
        f"Corps {(contexte_jeu or {}).get('corps_celeste', 'Inconnu')}, "
        f"Vaisseau {(contexte_jeu or {}).get('vaisseau', 'Inconnu')}"
    )
    message_utilisateur = (
        f"Question du Commandant : {question_pilote}\n"
        f"Contexte scientifique Elite Dangerous :\n{contexte_txt}\n"
        f"Relevé visuel des capteurs optiques :\n{analyse_visuelle}"
    )

    hist = [] if ignorer_historique else historique_conversation
    messages_api = (
        [{"role": "system", "content": instructions_vision}]
        + hist
        + [{"role": "user", "content": message_utilisateur}]
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_api
    )
    return response.choices[0].message.content


def executer_echange_vision_directe_openai(
    question_pilote: str,
    image_b64: str,
    bloc_contexte_scientifique: str,
    memoire_long_terme: str,
    historique_conversation: list,
    ignorer_historique: bool = False
) -> tuple[str, str]:
    """Envoie directement l'image + le contexte scientifique ED à OpenAI Vision (0 VRAM, ultra-rapide).

    Retourne (reponse_vocale_propre, resume_hud).
    """
    client = get_openai_client()
    modele_oa = str(VISION_CONFIG.get("modele_openai", "gpt-4o-mini")).strip() or "gpt-4o-mini"
    detail_oa = str(VISION_CONFIG.get("detail_openai", "high")).strip().lower()
    if detail_oa not in ("low", "high", "auto"):
        detail_oa = "high"

    instructions_vision = _construire_instructions_vision_ed(memoire_long_terme, vision_directe=True)
    texte_user = (
        f"Question du Commandant : {question_pilote}\n"
        f"Contexte scientifique Elite Dangerous (journaux temps réel) :\n{bloc_contexte_scientifique}"
    )

    hist = [] if ignorer_historique else historique_conversation
    messages_api = (
        [{"role": "system", "content": instructions_vision}]
        + hist
        + [{
            "role": "user",
            "content": [
                {"type": "text", "text": texte_user},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_b64}",
                        "detail": detail_oa
                    }
                }
            ]
        }]
    )

    response = client.chat.completions.create(
        model=modele_oa,
        messages=messages_api,
        max_tokens=260
    )
    brut = (response.choices[0].message.content or "").strip()

    # Extraction de la balise facultative [HUD: ...] (affichée sur le HUD, jamais lue à voix haute)
    resume_hud = ""
    m_hud = re.search(r"\[HUD\s*:\s*([^\]]+)\]", brut, flags=re.IGNORECASE)
    if m_hud:
        resume_hud = m_hud.group(1).strip()
        reponse_vocale = (brut[:m_hud.start()] + brut[m_hud.end():]).strip()
    else:
        reponse_vocale = brut
        resume_hud = re.split(r"(?<=[.!?])\s+", brut)[0][:150].strip() if brut else ""

    return reponse_vocale, resume_hud


def sauvegarder_journal_async(ech_pilote: str, ech_ia: str, memoire_actuelle: str, on_maj_memoire_func=None):
    """Met à jour le journal de bord de manière asynchrone via un résumé condensé."""
    def _tache():
        try:
            client = get_openai_client()
            prompt_archive = (
                f"Archives actuelles :\n{memoire_actuelle}\n"
                f"Nouvel échange réel : Pilote: '{ech_pilote}' / {NOM_IA}: '{ech_ia}'\n"
                "Résume uniquement les faits marquants et préférences du pilote en 50 lignes maximum, sans jamais inventer d'échanges fictifs ni stocker de position/flotte temporaire."
            )
            res_archive = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt_archive}]
            )
            nouvelle_memoire = res_archive.choices[0].message.content
            with open(FICHIER_MEMOIRE, "w", encoding="utf-8") as f:
                f.write(nouvelle_memoire)
            if on_maj_memoire_func:
                on_maj_memoire_func(nouvelle_memoire)
        except Exception:
            pass

    threading.Thread(target=_tache, daemon=True).start()
