"""Module de chargement de la configuration et des secrets d'Oscar."""

import json
import os
from pathlib import Path

# Répertoire racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Dossier de données
DOSSIER_DATA = BASE_DIR / "data"
DOSSIER_DATA.mkdir(parents=True, exist_ok=True)

# Chemins des fichiers JSON de configuration
FICHIER_CONFIG = BASE_DIR / "config_oscar.json"
FICHIER_SECRETS = BASE_DIR / "secrets.json"

# Fichiers de données persistantes
FICHIER_MEMOIRE = DOSSIER_DATA / "journal_de_bord.txt"
FICHIER_FLOTTE = DOSSIER_DATA / "flotte_cmdr.json"
FICHIER_COMMANDES = DOSSIER_DATA / "commandes_vaisseau.txt"
FICHIER_POSITIONS_HUD = DOSSIER_DATA / "hud_positions.json"
FICHIER_CODEX_ED = DOSSIER_DATA / "codex_ed.json"
FICHIER_CODEX_CMDR = DOSSIER_DATA / "codex_cmdr.json"

# Valeurs par défaut de secours
_CONFIG_DEFAUT = {
    "nom_ia": "Oscar",
    "personnalite_ia": "Tu es Oscar, copilote sarcastique et concis.",
    "tts": {
        "voix": "fr-FR-HenriNeural",
        "vitesse": "+8%"
    },
    "raccourci_ptt": "ctrl+shift+f9",
    "delais_clavier": {
        "delai_apres_ptt_relachement": 0.06,
        "delai_frappe_down": 0.025,
        "delai_frappe_up": 0.015,
        "delai_ctrl_combinaison": 0.035,
        "delai_clipboard_injection": 0.04
    },
    "noms_vaisseaux": {},
    "commandes_modes": {},
    "hud": {
        "actif_au_demarrage": False,
        "couleur_fond": "#120904",
        "opacite": 0.72,
        "bordure": False,
        "couleur_bordure": "#FF7100",
        "epaisseur_bordure": 1,
        "police": "Consolas",
        "taille_police": 12,
        "couleur_texte": "#FF7100",
        "nb_caracteres_ligne": 25,
        "nb_lignes_max": 10,
        "inclinaison_cockpit": False,
        "angle_cockpit_degres": 3.5,
        "perspective_cockpit": 0.07,
        "positions_par_vue": {
            "cockpit": [80, 120],
            "carte_systeme": [80, 120],
            "carte_galactique": [80, 120],
            "a_pied": [80, 120]
        },
        "commandes_afficher": [
            "affiche ton hud", "afficher ton hud", "affiche le hud",
            "ouvre ton hud", "montre ton hud", "active ton hud"
        ],
        "commandes_masquer": [
            "efface ton hud", "effacer ton hud", "supprime ton hud",
            "supprimer ton hud", "enleve ton hud", "enlève ton hud",
            "enlever ton hud", "masque ton hud", "cache ton hud",
            "retire ton hud", "ferme ton hud"
        ]
    },
    "vision": {
        "actif": False,
        "photo_active": True,
        "moteur": "ollama",
        "modele_openai": "gpt-4o-mini",
        "detail_openai": "high",
        "ollama_url": "http://127.0.0.1:11434",
        "modele": "qwen2.5vl:7b",
        "keep_alive": 0,
        "num_ctx": 6144,
        "timeout_secondes": 60,
        "largeur_max_analyse": 1600,
        "qualite_jpeg_analyse": 85,
        "zoom_ath_ultrawide": True,
        "codex_maj_auto_jours": 30,
        "dossier_photos": r"%USERPROFILE%\Pictures\Frontier Developments\Elite Dangerous",
        "prefixe_nom_photo": "Oscar",
        "verifier_ath_photo": True,
        "commande_va_masquer_ath": "Désactiver ATH",
        "delai_apres_masquage_ath": 3.5,
        "reactiver_ath_apres_photo": True,
        "delai_masquage_hud_oscar": 0.15,
        "phrase_attente_analyse": "Je regarde.",
        "prefixes_analyse": [
            "regarde", "regardes", "regardez",
            "analyse mon ecran", "analyse l ecran"
        ],
        "commandes_photo": [
            "prendre une photo", "prends une photo", "prend une photo", "prenez une photo",
            "faire une photo", "fais une photo", "fait une photo",
            "prendre photo", "prends photo", "photo", "une photo",
            "prendre un screenshot", "prends un screenshot", "screenshot",
            "capture d ecran", "capture ecran",
            "prendre une capture", "prends une capture"
        ]
    },
    "navigation_proactive": {
        "actif": True,
        "systeme_maison": "auto",
        "annoncer_arrivee_systeme": True,
        "annoncer_honk": True
    },
    "synonymes_verbes": {
        "ouvrir_activer": [
            "activer", "afficher", "ouvrir", "lancer", "éjecter", "mettre",
            "passer", "allumer", "démarrer", "montrer", "rétablir", "remettre"
        ],
        "fermer_desactiver": [
            "désactiver", "fermer", "enlever", "masquer", "cacher", "supprimer",
            "effacer", "couper", "éteindre", "quitter", "retirer", "arrêter"
        ],
        "sortir_prendre": [
            "sortir", "prendre", "équiper", "déployer", "dégainer"
        ],
        "ranger_rentrer": [
            "ranger", "rengainer", "rentrer", "rétracter", "cacher"
        ],
        "changer_suivant": [
            "changer", "basculer", "alterner", "inverser"
        ],
        "charger_utiliser": [
            "utiliser", "charger", "recharger"
        ]
    },
    "synonymes_objets": {
        "roue insight": "menu insight",
        "roue d insight": "menu insight",
        "roue emoticone": "roue d emoticomes",
        "roue emoticones": "roue d emoticomes",
        "roue d emoticone": "roue d emoticomes",
        "roue d emoticones": "roue d emoticomes",
        "fss": "acs",
        "mode fss": "mode acs",
        "torche": "phares",
        "lampe": "phares",
        "lampe torche": "phares"
    }
}

_SECRETS_DEFAUT = {
    "openai_api_key": "",
    "edsm_api_key": "",
    "cmdr_name": "Commandant",
    "chemins": {
        "dossier_journaux_ed": r"%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous",
        "chemin_voiceattack": r"C:\Program Files (x86)\Steam\steamapps\common\VoiceAttack\VoiceAttack.exe"
    }
}


def _charger_json(chemin: Path, defaut: dict) -> dict:
    if not chemin.exists():
        return defaut
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Configuration] Attention, échec de lecture de {chemin.name} ({e}), valeurs par défaut utilisées.")
        return defaut


# Chargement effectif
config_data = _charger_json(FICHIER_CONFIG, _CONFIG_DEFAUT)
secrets_data = _charger_json(FICHIER_SECRETS, _SECRETS_DEFAUT)

# Paramètres généraux de l'IA
NOM_IA: str = config_data.get("nom_ia", "Oscar")
PERSONNALITE_IA: str = config_data.get("personnalite_ia", "")

# Synthèse vocale TTS
TTS_CONFIG = config_data.get("tts", {})
VOIX_NEURALE: str = TTS_CONFIG.get("voix", "fr-FR-HenriNeural")
VOIX_VITESSE: str = TTS_CONFIG.get("vitesse", "+8%")

# Contrôles et simulation clavier
TOUCHE_MICRO: str = config_data.get("raccourci_ptt", "ctrl+shift+f9")
DELAIS_CLAVIER: dict = config_data.get("delais_clavier", _CONFIG_DEFAUT["delais_clavier"])
NOMS_VAISSEAUX: dict = config_data.get("noms_vaisseaux", {})
COMMANDES_MODES: dict = config_data.get("commandes_modes", {})
HUD_CONFIG: dict = {**_CONFIG_DEFAUT["hud"], **config_data.get("hud", {})}
VISION_CONFIG: dict = {**_CONFIG_DEFAUT["vision"], **config_data.get("vision", {})}
NAVIGATION_CONFIG: dict = {**_CONFIG_DEFAUT["navigation_proactive"], **config_data.get("navigation_proactive", {})}
SYNONYMES_VERBES: dict = {**_CONFIG_DEFAUT["synonymes_verbes"], **config_data.get("synonymes_verbes", {})}
SYNONYMES_OBJETS: dict = {**_CONFIG_DEFAUT["synonymes_objets"], **config_data.get("synonymes_objets", {})}
DOSSIER_PHOTOS_ED: str = os.path.expandvars(
    VISION_CONFIG.get("dossier_photos", _CONFIG_DEFAUT["vision"]["dossier_photos"])
)

# Secrets et API
CLE_API_OPENAI: str = secrets_data.get("openai_api_key", "")
EDSM_API_KEY: str = secrets_data.get("edsm_api_key", "")
CMDR_NAME: str = secrets_data.get("cmdr_name", "Commandant")

# Chemins système
chemins_secrets = secrets_data.get("chemins", {})
dossier_ed_raw = chemins_secrets.get("dossier_journaux_ed", _SECRETS_DEFAUT["chemins"]["dossier_journaux_ed"])
DOSSIER_JOURNAUX_ED: str = os.path.expandvars(dossier_ed_raw)
CHEMIN_VOICEATTACK: str = chemins_secrets.get("chemin_voiceattack", _SECRETS_DEFAUT["chemins"]["chemin_voiceattack"])

# En-têtes HTTP pour les requêtes EDSM et Spansh
HEADERS_HTTP = {
    "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) {NOM_IA}Copilot/16.0"
}


def formater_nom_vaisseau(code_vaisseau: str) -> str:
    """Traduit le nom technique de vaisseau en appellation officielle lisible."""
    if not code_vaisseau:
        return "Inconnu"
    cle = str(code_vaisseau).lower().strip()
    return NOMS_VAISSEAUX.get(cle, code_vaisseau)
