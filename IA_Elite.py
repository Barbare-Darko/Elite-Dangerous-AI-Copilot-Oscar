"""Point d'entrée principal du copilote vocal Oscar pour Elite Dangerous."""

import json
import os
import re
import site
import socket
import subprocess
import sys
import threading
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
from modules.codex_ed import lancer_maj_codex_async
from modules.config_loader import (
    CHEMIN_VOICEATTACK,
    COMMANDES_MODES,
    DOSSIER_JOURNAUX_ED,
    FICHIER_COMMANDES,
    NOM_IA,
    TOUCHE_MICRO,
    VISION_CONFIG
)
from modules.hud_overlay import (
    HudOverlay,
    detecter_commande_hud
)
from modules.oscar_brain import (
    charger_journal_de_bord,
    executer_echange_openai,
    executer_echange_vision_directe_openai,
    executer_echange_vision_openai,
    generer_accueil_initial,
    resoudre_commande_voiceattack,
    sauvegarder_journal_async,
    verifier_autorisation_mode_special,
    verifier_coherence_commande_pilote
)
from modules.stt_engine import STT_INCOMPRIS, enregistrer_et_transcrire, initialiser_whisper
from modules.telemetry_ed import (
    analyser_journaux_locaux,
    lancer_surveillance_alertes,
    normaliser_texte,
    resoudre_bascule_roues_a_pied,
    resoudre_garde_fou_equipement_a_pied
)
from modules.text_modes import (
    MODE_DICTEE,
    MODE_EPELLATION,
    GestionnaireModesTexte
)
from modules.tts_engine import arreter_parole, dire_vocal
from modules.vision_engine import (
    analyser_ecran_pour_oscar,
    demarrer_ollama_si_besoin,
    detecter_commande_photo,
    detecter_commande_vision,
    formater_contexte_scientifique_ed,
    obtenir_moteur_vision,
    prendre_photo_jeu,
    preparer_capture_vision
)

# ==============================================================================
# INITIALISATION DES COMPOSANTS
# ==============================================================================
print(f"=== COPILOTE IA ELITE DANGEROUS ({NOM_IA.upper()} - V17.1 MODULAIRE + HUD + VISION) ===")
initialiser_whisper()
lancer_maj_codex_async()

if VISION_CONFIG.get("actif", False):
    moteur_vision = obtenir_moteur_vision()
    if moteur_vision == "openai":
        print(
            f"[Vision] Moteur OpenAI direct prêt (modèle : {VISION_CONFIG.get('modele_openai', 'gpt-4o-mini')}, "
            f"détail={VISION_CONFIG.get('detail_openai', 'high')}, 0 VRAM)."
        )
    else:
        ok_ollama, msg_ollama = demarrer_ollama_si_besoin()
        if ok_ollama:
            print(f"[Vision] Moteur Ollama local prêt (modèle : {VISION_CONFIG.get('modele')}, keep_alive={VISION_CONFIG.get('keep_alive')}).")
        else:
            print(f"[Vision] Avertissement : {msg_ollama}")
else:
    print("[Vision] Analyse visuelle IA désactivée dans config_oscar.json (0 VRAM / sans Ollama).")

hud = HudOverlay()
hud.demarrer()

gestionnaire_modes = GestionnaireModesTexte(hud=hud)
lancer_surveillance_alertes(
    get_mode_actuel_func=lambda: gestionnaire_modes.mode_actuel,
    on_alerte_hud_func=hud.afficher_alerte,
    on_changement_vue_func=hud.changer_vue
)

memoire_long_terme = charger_journal_de_bord()


def maj_memoire_locale(nouvelle_memoire):
    global memoire_long_terme
    memoire_long_terme = nouvelle_memoire


def verifier_et_recharger_itineraire_async():
    """Rattrapage Odyssey : si 'Cibler prochain système de l'itinéraire' n'a pas verrouillé
    le prochain saut de NavRoute.json (route oubliée en RAM après débarquement à pied/VRS ou
    redémarrage), fait un aller-retour éclair sur la Carte Galactique pour recharger la route."""
    def _tache():
        try:
            time.sleep(0.6)
            chemin_route = os.path.join(DOSSIER_JOURNAUX_ED, "NavRoute.json")
            chemin_status = os.path.join(DOSSIER_JOURNAUX_ED, "Status.json")
            if not os.path.exists(chemin_route) or not os.path.exists(chemin_status):
                return

            with open(chemin_route, "r", encoding="utf-8") as fr:
                route = (json.load(fr) or {}).get("Route") or []
            if len(route) < 2:
                return

            # Identifie le système actuel puis le saut suivant dans NavRoute.json
            sys_actuel = normaliser_texte(analyser_journaux_locaux(nb_journaux=1).get("systeme", ""))
            prochain_sys = ""
            for idx, etape in enumerate(route[:-1]):
                if normaliser_texte(etape.get("StarSystem", "")) == sys_actuel:
                    prochain_sys = str(route[idx + 1].get("StarSystem") or "").strip()
                    break
            if not prochain_sys:
                prochain_sys = str(route[1].get("StarSystem") or "").strip()
            if not prochain_sys:
                return

            def _lire_status():
                try:
                    with open(chemin_status, "r", encoding="utf-8") as fs:
                        return json.load(fs)
                except Exception:
                    return {}

            st = _lire_status()
            dest_actuelle = normaliser_texte(((st.get("Destination") or {}).get("Name") or ""))
            # Si déjà ciblé ou déjà dans la Carte Galactique (GuiFocus == 6), rien à faire
            if dest_actuelle == normaliser_texte(prochain_sys) or st.get("GuiFocus") == 6:
                return

            print(f"[Navigation] Itinéraire oublié par Odyssey -> aller-retour éclair Carte Galactique ({prochain_sys})...")
            subprocess.Popen([CHEMIN_VOICEATTACK, "-command", "Ouvrir Carte Galactique"])

            # Attend que la Carte Galactique s'ouvre et recalcule la route (max 4.5s)
            t0 = time.time()
            carte_ouverte_ts = None
            while time.time() - t0 < 4.5:
                time.sleep(0.25)
                st2 = _lire_status()
                if st2.get("GuiFocus") == 6 and carte_ouverte_ts is None:
                    carte_ouverte_ts = time.time()
                dest2 = normaliser_texte(((st2.get("Destination") or {}).get("Name") or ""))
                if dest2 == normaliser_texte(prochain_sys) and carte_ouverte_ts and (time.time() - carte_ouverte_ts) >= 0.7:
                    break
                if carte_ouverte_ts and (time.time() - carte_ouverte_ts) >= 2.2:
                    break

            # Referme la Carte Galactique uniquement si elle est bien ouverte
            if _lire_status().get("GuiFocus") == 6:
                subprocess.Popen([CHEMIN_VOICEATTACK, "-command", "Ouvrir Carte Galactique"])
                time.sleep(0.6)

            # Vérification finale et ciblage direct si nécessaire
            dest_fin = normaliser_texte(((_lire_status().get("Destination") or {}).get("Name") or ""))
            if dest_fin != normaliser_texte(prochain_sys):
                subprocess.Popen([CHEMIN_VOICEATTACK, "-command", "Cibler prochain système de l'itinéraire"])
            else:
                print(f"[Navigation] Prochain saut verrouillé automatiquement : {prochain_sys}.")
        except Exception as e_nav:
            print(f"[Navigation] Erreur rattrapage itinéraire : {e_nav}")

    threading.Thread(target=_tache, name="OscarReplotRoute", daemon=True).start()


accueil = generer_accueil_initial(memoire_long_terme)
print(f"[{NOM_IA}] : {accueil}")
dire_vocal(accueil, bloquant=False)

historique_conversation = []
MAX_HISTORIQUE = 10

print(f"[Oscar] En écoute sur le raccourci PTT : {TOUCHE_MICRO.upper()}")

# ==============================================================================
# BOUCLE PRINCIPALE PUSH-TO-TALK & MACHINE D'ÉTATS
# ==============================================================================
while True:
    try:
        if keyboard.is_pressed(TOUCHE_MICRO):
            # Interruption immédiate (barge-in) si Oscar est en train de parler
            if arreter_parole():
                time.sleep(0.05)

            texte_actuel = enregistrer_et_transcrire(
                TOUCHE_MICRO,
                nom_ia=NOM_IA,
                mode_actuel=gestionnaire_modes.mode_actuel,
                on_debut_ecoute=lambda: hud.definir_etat_micro(True),
                on_fin_ecoute=lambda: hud.definir_etat_micro(False)
            )

            if texte_actuel == STT_INCOMPRIS:
                print("[Oscar] : Je n'ai pas compris, tu peux répéter ?")
                dire_vocal("Je n'ai pas compris, tu peux répéter ?", bloquant=False, interrompre_precedent=True)
                continue

            if texte_actuel and len(texte_actuel) > 1:
                print(f"[Vous ({gestionnaire_modes.mode_actuel})] : {texte_actuel}")

                # 1. Aiguillage des modes spéciaux sans jetons OpenAI
                if gestionnaire_modes.est_mode_special():
                    if gestionnaire_modes.mode_actuel == MODE_DICTEE:
                        gestionnaire_modes.traiter_segment_dictee(texte_actuel)
                    elif gestionnaire_modes.mode_actuel == MODE_EPELLATION:
                        gestionnaire_modes.traiter_segment_epellation(texte_actuel)
                    continue

                # 1b. Commandes vocales locales d'affichage / masquage du HUD (0 jeton)
                cmd_hud = detecter_commande_hud(texte_actuel)
                if cmd_hud == "AFFICHER":
                    print("[HUD] Affichage demandé par commande vocale.")
                    hud.afficher()
                    dire_vocal("HUD affiché.", bloquant=False, interrompre_precedent=True)
                    continue
                if cmd_hud == "MASQUER":
                    print("[HUD] Masquage demandé par commande vocale.")
                    hud.masquer()
                    dire_vocal("HUD masqué.", bloquant=False, interrompre_precedent=True)
                    continue

                # 1c. Mode Photo local (0 jeton OpenAI, masquage auto HUD Oscar & ATH caméra)
                if detecter_commande_photo(texte_actuel, nom_ia=NOM_IA):
                    print("[Vision/Photo] Prise de photo demandée par commande vocale.")
                    res_photo = prendre_photo_jeu(hud=hud)
                    hud.afficher_photo_enregistree(
                        nom_fichier=res_photo.get("nom_fichier", ""),
                        resolution=res_photo.get("resolution", ""),
                        ath_masque=res_photo.get("ath_masque", False),
                        erreur="" if res_photo.get("succes") else res_photo.get("avertissement_ollama", "Erreur")
                    )
                    dire_vocal(res_photo.get("message_vocal", "Photo enregistrée."), bloquant=False, interrompre_precedent=True)
                    continue

                # 1d. Mode Vision ("Regarde ! ...") -> OpenAI direct OU Ollama local + contexte scientifique ED
                est_vision, question_vision = detecter_commande_vision(texte_actuel, nom_ia=NOM_IA)
                if est_vision:
                    moteur_v = obtenir_moteur_vision()
                    print(f"[Vision ({moteur_v})] Analyse demandée : {question_vision}")
                    hud.afficher_vision_en_cours(question_vision)

                    phrase_attente = str(VISION_CONFIG.get("phrase_attente_analyse", "Je regarde.")).strip()
                    thread_attente = None
                    if phrase_attente:
                        thread_attente = threading.Thread(
                            target=dire_vocal,
                            args=(phrase_attente,),
                            daemon=True
                        )
                        thread_attente.start()

                    reponse_ia = ""
                    resume_hud = ""
                    err_vision = ""

                    if moteur_v == "openai":
                        cap = preparer_capture_vision(question_vision)
                        if cap.get("succes"):
                            ctx_v = cap.get("contexte_jeu", {})
                            bloc_sci = formater_contexte_scientifique_ed(ctx_v)
                            try:
                                reponse_ia, resume_hud = executer_echange_vision_directe_openai(
                                    question_pilote=question_vision,
                                    image_b64=cap["image_b64"],
                                    bloc_contexte_scientifique=bloc_sci,
                                    memoire_long_terme=memoire_long_terme,
                                    historique_conversation=historique_conversation,
                                    ignorer_historique=bool(ctx_v.get("est_question_ciel"))
                                )
                                duree_v = round(time.time() - cap.get("debut", time.time()), 2)
                                tag_z = "+zoom16:9" if cap.get("zoom_applique") else ""
                                print(
                                    f"[Vision] Analyse OpenAI ({VISION_CONFIG.get('modele_openai', 'gpt-4o-mini')}) "
                                    f"en {duree_v}s [{cap.get('resolution', '')}{tag_z}]"
                                )
                            except Exception as e_oa:
                                err_vision = f"Erreur OpenAI Vision : {e_oa}"
                            finally:
                                cap["image_b64"] = ""
                        else:
                            err_vision = cap.get("erreur", "Échec de capture d'écran.")
                    else:
                        res_vision = analyser_ecran_pour_oscar(question_vision)
                        if res_vision.get("succes"):
                            ctx_v = res_vision.get("contexte_jeu", {})
                            bloc_sci = formater_contexte_scientifique_ed(ctx_v)
                            reponse_ia = executer_echange_vision_openai(
                                question_pilote=question_vision,
                                analyse_visuelle=res_vision.get("description", ""),
                                contexte_jeu=ctx_v,
                                memoire_long_terme=memoire_long_terme,
                                historique_conversation=historique_conversation,
                                bloc_contexte_scientifique=bloc_sci,
                                ignorer_historique=bool(ctx_v.get("est_question_ciel"))
                            )
                            resume_hud = res_vision.get("resume_hud", "")
                        else:
                            err_vision = res_vision.get("erreur", "Capteurs optiques indisponibles.")

                    if thread_attente and thread_attente.is_alive():
                        thread_attente.join(timeout=6.0)

                    if reponse_ia and not err_vision:
                        print(f"[{NOM_IA} (Vision)] : {reponse_ia}")
                        historique_conversation = (
                            historique_conversation +
                            [{"role": "user", "content": texte_actuel}, {"role": "assistant", "content": reponse_ia}]
                        )[-MAX_HISTORIQUE:]

                        hud.afficher_vision_resultat(resume_hud, reponse_ia=reponse_ia)
                        dire_vocal(reponse_ia, bloquant=False, interrompre_precedent=True)
                        sauvegarder_journal_async(
                            texte_actuel,
                            reponse_ia,
                            memoire_long_terme,
                            on_maj_memoire_func=maj_memoire_locale
                        )
                    else:
                        err_msg = err_vision or "Capteurs optiques indisponibles."
                        print(f"[Vision] Échec : {err_msg}")
                        hud.afficher_vision_resultat("", erreur=err_msg)
                        dire_vocal(f"Mes capteurs optiques sont hors ligne. {err_msg}", bloquant=False, interrompre_precedent=True)
                    continue

                # 2. Interrogation du Cerveau OpenAI (GPT-4o-mini gère l'intention)
                lignes_cmd_vaisseau = []
                liste_cmd_vaisseau = ""
                if os.path.exists(FICHIER_COMMANDES):
                    with open(FICHIER_COMMANDES, "r", encoding="utf-8") as f:
                        lignes_cmd_vaisseau = [l.strip() for l in f.readlines() if l.strip()]
                    # Masque les doublons ambigus 'Prend Outil' / 'Range Outil' (Ctrl+I) au LLM
                    # et expose la commande virtuelle sécurisée 'Outil suivant' (gérée via Status.json)
                    lignes_cmd_pour_ia = [
                        c for c in lignes_cmd_vaisseau
                        if normaliser_texte(c) not in ("prend outil", "range outil")
                    ]
                    if not any(normaliser_texte(c) == "outil suivant" for c in lignes_cmd_pour_ia):
                        lignes_cmd_pour_ia.append("Outil suivant")
                    liste_cmd_vaisseau = ";".join(lignes_cmd_pour_ia)

                reponse_ia = executer_echange_openai(
                    texte_actuel=texte_actuel,
                    memoire_long_terme=memoire_long_terme,
                    historique_conversation=historique_conversation,
                    liste_commandes_va=liste_cmd_vaisseau,
                    on_outil_execute_func=hud.afficher_resultat_outil
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

                # Verrou sécurité sur les modes spéciaux (empêche une bascule involontaire sur phrase incomprise)
                if mode_special in ("DICTEE", "EPELLATION"):
                    if not verifier_autorisation_mode_special(texte_actuel, mode_special):
                        print(f"[SÉCURITÉ] Mode {mode_special} BLOQUÉ (non demandé explicitement dans : '{texte_actuel}').")
                        mode_special = None
                        reponse_ia = "Je n'ai pas compris, tu peux répéter ?"

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
                    # Résolution robuste (exacte, infinitif, familles de verbes synonymes & alias d'objets)
                    nom_action_resolu = resoudre_commande_voiceattack(nom_action_va, lignes_cmd_vaisseau)

                    # Verrou de sécurité absolu sur les commandes dangereuses (anti-HAL-9000)
                    # Empêche le LLM de déclencher Mode Furtif ou Larguer Cargaison sans ordre explicite du pilote
                    COMMANDES_CRITIQUES_MOTS_CLES = {
                        "passer mode furtif": ("furtif", "furtive", "silencieux", "silent"),
                        "larguer cargaison": ("largu", "cargaison", "cargo")
                    }
                    if nom_action_resolu:
                        cle_crit = normaliser_texte(nom_action_resolu)
                        mots_requis = COMMANDES_CRITIQUES_MOTS_CLES.get(cle_crit)
                        if mots_requis:
                            texte_pilote_norm = normaliser_texte(texte_actuel)
                            if cle_crit == "larguer cargaison":
                                autorise = any(v in texte_pilote_norm for v in ("largu", "jette", "jeter", "vide", "vider")) and any(
                                    o in texte_pilote_norm for o in ("cargaison", "cargo", "soute")
                                )
                            else:
                                autorise = any(m in texte_pilote_norm for m in mots_requis)
                            if not autorise:
                                print(
                                    f"[SÉCURITÉ] Commande critique '{nom_action_resolu}' BLOQUÉE "
                                    f"(non demandée explicitement dans : '{texte_actuel}')."
                                )
                                nom_action_resolu = None

                    # Filet de cohérence lexicale : bloque une commande devinée sur une phrase incomprise
                    if nom_action_resolu and not verifier_coherence_commande_pilote(texte_actuel, nom_action_resolu):
                        print(
                            f"[SÉCURITÉ] Commande '{nom_action_resolu}' BLOQUÉE "
                            f"(aucun lien cohérent avec : '{texte_actuel}')."
                        )
                        nom_action_resolu = None
                        reponse_ia = "Je n'ai pas compris, tu peux répéter ?"

                    # Garde-fou outils/armes à pied via Status.json (anti-toggle + cycle 'Outil suivant')
                    action_evitee_etat = False
                    if nom_action_resolu:
                        nom_action_resolu, msg_remplacement = resoudre_garde_fou_equipement_a_pied(nom_action_resolu)
                        if msg_remplacement:
                            print(f"[Équipement à pied] Action évitée (déjà dans l'état demandé) : {msg_remplacement}")
                            reponse_ia = msg_remplacement
                            action_evitee_etat = True

                    # Bascule propre entre roues radiales Odyssey (ferme d'abord la roue active avant d'ouvrir la suivante)
                    actions_a_executer = []
                    if nom_action_resolu:
                        actions_a_executer, msg_roue = resoudre_bascule_roues_a_pied(nom_action_resolu)
                        if msg_roue:
                            print(f"[Roues Odyssey] Action évitée : {msg_roue}")
                            reponse_ia = msg_roue
                            action_evitee_etat = True

                    if actions_a_executer:
                        hud.afficher_commande_vaisseau(actions_a_executer[-1])
                        for idx_act, act_va in enumerate(actions_a_executer):
                            if idx_act > 0:
                                time.sleep(0.25)
                            print(f"[VoiceAttack] Exécution de : {act_va}")
                            subprocess.Popen([CHEMIN_VOICEATTACK, "-command", act_va])
                        if normaliser_texte(actions_a_executer[-1]) == "cibler prochain systeme de l'itineraire":
                            verifier_et_recharger_itineraire_async()
                    elif action_evitee_etat:
                        pass
                    elif not lignes_cmd_vaisseau:
                        hud.afficher_commande_vaisseau(nom_action_va)
                        print(f"[VoiceAttack] Exécution de : {nom_action_va}")
                        subprocess.Popen([CHEMIN_VOICEATTACK, "-command", nom_action_va])
                    else:
                        print(f"[VoiceAttack] Commande ignorée (inconnue ou bloquée par sécurité) : {nom_action_va}")

                dire_vocal(reponse_ia, bloquant=False, interrompre_precedent=True)

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
