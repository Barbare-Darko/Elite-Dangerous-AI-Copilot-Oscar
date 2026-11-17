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
    "commandes_modes": {}
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
