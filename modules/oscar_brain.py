"""Module cerveau de l'IA (OpenAI GPT-4o-mini, Function Calling, Prompts et Mémoire)."""

import json
import os
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
from modules.config_loader import (
    CLE_API_OPENAI,
    CMDR_NAME,
    EDSM_API_KEY,
    FICHIER_MEMOIRE,
    NOM_IA,
    PERSONNALITE_IA
)
from modules.telemetry_ed import (
    analyser_journaux_locaux,
    charger_cache_flotte,
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


def construire_instructions_systeme(memoire_long_terme: str, liste_commandes_va: str) -> str:
    """Compose le prompt système complet d'Oscar."""
    return (
        f"Tu es l'IA de bord {NOM_IA} du Commandant {CMDR_NAME}. Personnalité : {PERSONNALITE_IA} "
        f"ARCHIVES : {memoire_long_terme} "
        "Tu disposes d'outils pour consulter l'état du vaisseau (crédits, rangs, position, planète, flotte complète, équipement des vaisseaux, matériaux) "
        "et les systèmes/stations proches via EDSM. Utilise-les dès que le pilote pose une question sur sa situation. "
        "Prononce toujours 'années-lumière' et 'secondes-lumière' en toutes lettres. "
        "RÈGLE ABSOLUE : Ne te fie JAMAIS aux ARCHIVES ni à ta mémoire pour la position, la station actuelle, les crédits, les matériaux, les rangs ou la flotte. Appelle OBLIGATOIREMENT l'outil correspondant à chaque question sur le vaisseau, la station ou la flotte pour lire les données en temps réel. "
        "Si une donnée n'est pas présente dans la télémétrie (comme la vitesse instantanée en m/s, le temps d'arrivée exact ou l'altitude lorsque le capteur est inactif), ne l'invente JAMAIS : précise simplement avec sarcasme que l'ordinateur de bord du vaisseau ne transmet pas cette télémétrie. "
        "Quand tu donnes un résultat de commerce ou d'équipement, cite TOUJOURS pour la meilleure station : son nom, le système, le prix unitaire en crédits, le stock ou la demande en tonnes, et le nombre de sauts approximatifs (ne cite pas les stations secondaires sauf si demandé). "
        "Si le Commandant demande à écrire, dicter du texte ou passer en mode dictée (même avec une faute d'audition comme 'mode dicté' ou 'notre dictée'), réponds très brièvement et ajoute [MODE_DICTEE] à la fin (SANS jamais exécuter de commande de vaisseau). "
        "S'il demande à épeler ou passer en mode lettre à lettre, réponds très brièvement et ajoute [MODE_EPELLATION] à la fin. "
        "Si le pilote demande une action physique sur le vaisseau, fais une réponse très courte (5-6 mots max), "
        "puis ajoute à la fin l'action exacte entre crochets parmi : "
        f"{liste_commandes_va} Exemple : [EXECUTE:Allumer les phares]. "
        f"Date et heure actuelles : {time.strftime('%d/%m/%Y %H:%M')}. "
    )


def executer_echange_openai(texte_actuel: str, memoire_long_terme: str, historique_conversation: list, liste_commandes_va: str) -> str:
    """Interroge OpenAI avec Function Calling et résout les éventuels appels d'outils."""
    client = get_openai_client()
    instructions = construire_instructions_systeme(memoire_long_terme, liste_commandes_va)
    messages_api = [{"role": "system", "content": instructions}] + historique_conversation + [{"role": "user", "content": texte_actuel}]

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
        return second_response.choices[0].message.content
    return message_reponse.content


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
