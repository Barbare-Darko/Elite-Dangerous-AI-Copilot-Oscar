"""Point d'entrée principal du copilote vocal Oscar pour Elite Dangerous."""

import os
import re
import site
import socket
import subprocess
import sys
import time
import types
import keyboard

# ==============================================================================
# CONTRÔLE D'INSTANCE UNIQUE
# ==============================================================================
try:
    verrou_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    verrou_instance.bind(("127.0.0.1", 47291))
except OSError:
    print("Une instance d'Oscar tourne déjà en arrière-plan ! Fermeture.")
    sys.exit(0)

# ==============================================================================
# CONTOURNEMENT RUNTIME PYTHON 3.15 & CUDA (NVIDIA DLLs)
# ==============================================================================
sys.modules['av'] = types.ModuleType('av')
yaml_faux = types.ModuleType('yaml')
yaml_faux.safe_load = lambda *args, **kwargs: {}
yaml_faux.load = lambda *args, **kwargs: {}
yaml_faux.dump = lambda *args, **kwargs: ""
yaml_faux.safe_dump = lambda *args, **kwargs: ""
sys.modules['yaml'] = yaml_faux

for dossier_site in site.getsitepackages():
    dossier_nvidia = os.path.join(dossier_site, "nvidia")
    if os.path.exists(dossier_nvidia):
        for sous_dossier in os.listdir(dossier_nvidia):
            chemin_bin = os.path.join(dossier_nvidia, sous_dossier, "bin")
            if os.path.exists(chemin_bin):
                os.environ["PATH"] = chemin_bin + os.pathsep + os.environ["PATH"]
                os.add_dll_directory(chemin_bin)

# ==============================================================================
# IMPORTS DES MODULES PROPRES
# ==============================================================================
from modules.config_loader import (
    CHEMIN_VOICEATTACK,
    COMMANDES_MODES,
    FICHIER_COMMANDES,
    NOM_IA,
    TOUCHE_MICRO
)
from modules.oscar_brain import (
    charger_journal_de_bord,
    executer_echange_openai,
    generer_accueil_initial,
    sauvegarder_journal_async
)
from modules.stt_engine import enregistrer_et_transcrire, initialiser_whisper
from modules.telemetry_ed import lancer_surveillance_alertes, normaliser_texte
from modules.text_modes import (
    MODE_DICTEE,
    MODE_EPELLATION,
    GestionnaireModesTexte
)
from modules.tts_engine import dire_vocal

# ==============================================================================
# INITIALISATION DES COMPOSANTS
# ==============================================================================
print(f"=== COPILOTE IA ELITE DANGEROUS ({NOM_IA.upper()} - V16.0 MODULAIRE) ===")
initialiser_whisper()

gestionnaire_modes = GestionnaireModesTexte()
lancer_surveillance_alertes(get_mode_actuel_func=lambda: gestionnaire_modes.mode_actuel)

memoire_long_terme = charger_journal_de_bord()


def maj_memoire_locale(nouvelle_memoire):
    global memoire_long_terme
    memoire_long_terme = nouvelle_memoire


accueil = generer_accueil_initial(memoire_long_terme)
print(f"[{NOM_IA}] : {accueil}")
dire_vocal(accueil)

historique_conversation = []
MAX_HISTORIQUE = 10

print(f"[Oscar] En écoute sur le raccourci PTT : {TOUCHE_MICRO.upper()}")

# ==============================================================================
# BOUCLE PRINCIPALE PUSH-TO-TALK & MACHINE D'ÉTATS
# ==============================================================================
while True:
    try:
        if keyboard.is_pressed(TOUCHE_MICRO):
            texte_actuel = enregistrer_et_transcrire(
                TOUCHE_MICRO,
                nom_ia=NOM_IA,
                mode_actuel=gestionnaire_modes.mode_actuel
            )

            if texte_actuel and len(texte_actuel) > 1:
                print(f"[Vous ({gestionnaire_modes.mode_actuel})] : {texte_actuel}")

                # 1. Aiguillage des modes spéciaux sans jetons OpenAI
                if gestionnaire_modes.est_mode_special():
                    if gestionnaire_modes.mode_actuel == MODE_DICTEE:
                        gestionnaire_modes.traiter_segment_dictee(texte_actuel)
                    elif gestionnaire_modes.mode_actuel == MODE_EPELLATION:
                        gestionnaire_modes.traiter_segment_epellation(texte_actuel)
                    continue

                # 2. Interrogation du Cerveau OpenAI (GPT-4o-mini gère l'intention)
                liste_cmd_vaisseau = ""
                if os.path.exists(FICHIER_COMMANDES):
                    with open(FICHIER_COMMANDES, "r", encoding="utf-8") as f:
                        lignes = [l.strip() for l in f.readlines() if l.strip()]
                    liste_cmd_vaisseau = ";".join(lignes)

                reponse_ia = executer_echange_openai(
                    texte_actuel=texte_actuel,
                    memoire_long_terme=memoire_long_terme,
                    historique_conversation=historique_conversation,
                    liste_commandes_va=liste_cmd_vaisseau
                )

                print(f"[{NOM_IA}] : {reponse_ia}")
                historique_conversation = (
                    historique_conversation +
                    [{"role": "user", "content": texte_actuel}, {"role": "assistant", "content": reponse_ia}]
                )[-MAX_HISTORIQUE:]

                # 3. Parsing des balises d'action ou de mode spécial
                nom_action_va = None
                mode_special = None
                if "[" in reponse_ia and "]" in reponse_ia:
                    idx_deb = reponse_ia.find("[")
                    idx_fin = reponse_ia.find("]", idx_deb)
                    balise = reponse_ia[idx_deb + 1:idx_fin].strip()

                    if balise.upper() == "MODE_DICTEE":
                        mode_special = "DICTEE"
                    elif balise.upper() == "MODE_EPELLATION":
                        mode_special = "EPELLATION"
                    elif balise.upper().startswith("EXECUTE:"):
                        nom_action_va = balise[8:].strip()
                    else:
                        nom_action_va = balise
                    reponse_ia = (reponse_ia[:idx_deb] + reponse_ia[idx_fin + 1:]).strip()

                # Transition vers un mode spécial avec confirmation vocale systématique
                if mode_special == "DICTEE":
                    phrase_vocale = f"{reponse_ia} Mode dictée activé.".strip() if reponse_ia else "Mode dictée activé."
                    gestionnaire_modes.activer_dictee(phrase_vocale)
                    continue
                if mode_special == "EPELLATION":
                    phrase_vocale = f"{reponse_ia} Mode épellation activé.".strip() if reponse_ia else "Mode épellation activé."
                    gestionnaire_modes.activer_epellation(phrase_vocale)
                    continue

                # Déclenchement VoiceAttack si commande vaisseau détectée
                if nom_action_va:
                    print(f"[VoiceAttack] Exécution de : {nom_action_va}")
                    subprocess.Popen([CHEMIN_VOICEATTACK, "-command", nom_action_va])

                dire_vocal(reponse_ia)

                # Archivage asynchrone du journal de bord
                sauvegarder_journal_async(
                    texte_actuel,
                    reponse_ia,
                    memoire_long_terme,
                    on_maj_memoire_func=maj_memoire_locale
                )

    except Exception as e:
        print(f"[Oscar] Erreur boucle principale : {e}")
    time.sleep(0.05)
