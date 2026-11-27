"""Module de reconnaissance vocale locale (STT) avec Faster-Whisper et capture Sounddevice."""

import re
import time
import numpy as np
import sounddevice as sd
import keyboard
from faster_whisper import WhisperModel

FREQUENCE_AUDIO = 16000
MARGE_FIN_PTT_S = 0.18  # Conserve la fin de la dernière syllabe après relâchement du bouton PTT
STT_INCOMPRIS = "__STT_INCOMPRIS__"
_modele_whisper = None

PROMPTS_WHISPER = {
    "NORMAL": (
        "Glossaire français Elite Dangerous : Oscar, ACS, FSS, DSS, ATH, HUD, VRS, FSD, "
        "carte système, carte galactique, orbites, train d'atterrissage, phares, torche, "
        "outil de la combinaison, échantillonneur génétique, énergiseur, analyseur de profil, "
        "rengaine, ranger l'outil, arme principale, arme secondaire, recharger l'arme, "
        "roue d'inventaire, roue d'émoticônes, cellule d'énergie, "
        "portefeuille d'exploration, exobiologie, bactérium, stratum, fonticulua, fungoida."
    ),
    "DICTEE": "Envoi, envoyer le message, poster le message, valider le message, expédier, paragraphe suivant, à la ligne, nouvelle ligne, corriger, effacer, stop.",
    "EPELLATION": "Alpha, Bravo, Charlie, Delta, Echo, Foxtrot, Golf, Hotel, India, Juliett, Kilo, Lima, Mike, November, Olivier, Papa, Quebec, Romeo, Sierra, Tango, Uniform, Victor, Whiskey, X-ray, Yankee, Zulu. Point, tiret, trait d'union, underscore, envoi, valider, corriger, effacer, stop."
}


def _est_hallucination_whisper(texte: str, prompt_initial: str = "") -> bool:
    """Détecte les hallucinations classiques de Whisper (boucles répétées ou copie du prompt)."""
    if not texte:
        return True
    t = re.sub(r"\s+", " ", texte).strip()
    t_low = t.lower()

    # 1. Phrases parasites connues de Whisper
    hallucinations = (
        "sous-titrage", "sous-titres", "amara.org",
        "merci d'avoir regardé", "merci d'avoir visionné",
        "glossaire français elite dangerous"
    )
    if any(h in t_low for h in hallucinations):
        return True

    # 2. Copie littérale d'un long morceau du prompt initial
    if prompt_initial and len(t_low) >= 24 and t_low in prompt_initial.lower():
        return True

    # 3. Boucle de répétition exacte (ex: "Qu'il te plaît. Qu'il te plaît." ou "X. Y. X. Y.")
    segments_p = [re.sub(r"[^a-z0-9àâäéèêëïîôöùûüç\s]", "", p.lower()).strip() for p in re.split(r"[.!?]+", t) if p.strip()]
    if len(segments_p) >= 2 and len(set(segments_p)) == 1 and len(segments_p[0]) >= 5:
        return True
    if len(segments_p) >= 4 and segments_p[:2] == segments_p[2:4]:
        return True

    return False


def _corriger_termes_ed(texte: str) -> str:
    """Corrige les confusions phonétiques récurrentes de Whisper sur les acronymes Elite Dangerous."""
    if not texte:
        return texte
    # "la TH", "la T.H.", "l'AT H", "l'A.T.H." -> "l'ATH"
    texte = re.sub(r"\b(?:la\s+t\.?\s*h\.?|l['’]\s*a\.?\s*t\.?\s*h\.?|l['’]\s*at\s+h)\b", "l'ATH", texte, flags=re.IGNORECASE)
    # "ton TH" / "le TH" -> "l'ATH"
    texte = re.sub(r"\b(?:le|ton)\s+t\.?\s*h\.?\b", "l'ATH", texte, flags=re.IGNORECASE)
    # Confusions phonétiques juste après un verbe d'action d'affichage ("rétabli/affiche/masque/active la cache/tâche/hache")
    verbes_ath = (
        r"(?:active[rz]?|r[ée]active[rz]?|d[ée]sactive[rz]?|affiche[rz]?|masque[rz]?|"
        r"r[ée]tabli[rstz]?|remet[st]?|remettre|enl[èe]ve[rz]?|coupe[rz]?|cache[rz]?)"
    )
    texte = re.sub(
        rf"(\b{verbes_ath}\s+)(?:la\s+(?:cache|t[âa]che|hache|th)|l['’]at[eé]?)\b",
        r"\1l'ATH",
        texte,
        flags=re.IGNORECASE
    )
    # Confusions phonétiques autour de "l'ACS" ("la CS", "quitte la CS", "kitler-cs", "kit plus s")
    texte = re.sub(r"\b(?:la\s+c\.?\s*s\.?|l['’]\s*a\.?\s*c\.?\s*s\.?)\b", "l'ACS", texte, flags=re.IGNORECASE)
    texte = re.sub(
        r"^\s*(?:kitler[\s\-]*cs|kit\s+plus\s+s|kit\s+l[ae]\s*c\.?\s*s\.?|quitte?\s+l[ae]\s+c\.?\s*s\.?)\s*[.!?]*\s*$",
        "Quitte l'ACS.",
        texte,
        flags=re.IGNORECASE
    )
    return texte


def initialiser_whisper(model_size="large-v3-turbo", device="cuda", compute_type="float16") -> WhisperModel:
    """Initialise et met en cache le modèle Faster-Whisper sur GPU."""
    global _modele_whisper
    if _modele_whisper is None:
        print(f"[STT] Chargement du modèle Faster-Whisper ({model_size} sur {device})...")
        _modele_whisper = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("[STT] Modèle Faster-Whisper prêt.")
    return _modele_whisper


def enregistrer_et_transcrire(
    touche_micro: str,
    nom_ia: str = "Oscar",
    mode_actuel: str = "NORMAL",
    on_debut_ecoute=None,
    on_fin_ecoute=None
) -> str:
    """Enregistre le son tant que la touche micro est enfoncée et transcrit le résultat avec prompt guidé."""
    modele = initialiser_whisper()
    blocs_audio = []

    def callback_audio(indata, frames, time_info, status):
        blocs_audio.append(indata.copy())

    if on_debut_ecoute:
        try:
            on_debut_ecoute()
        except Exception:
            pass

    try:
        with sd.InputStream(samplerate=FREQUENCE_AUDIO, channels=1, dtype='float32', callback=callback_audio):
            while keyboard.is_pressed(touche_micro):
                time.sleep(0.04)
            # Petite marge après relâchement du PTT pour ne jamais tronquer la dernière syllabe
            time.sleep(MARGE_FIN_PTT_S)
    finally:
        if on_fin_ecoute:
            try:
                on_fin_ecoute()
            except Exception:
                pass

    # Attente brève de relâchement des modificateurs
    t_wait = time.time()
    while (keyboard.is_pressed('ctrl') or keyboard.is_pressed('shift')) and (time.time() - t_wait < 0.25):
        time.sleep(0.01)

    if not blocs_audio:
        return ""

    audio_complet = np.concatenate(blocs_audio, axis=0).flatten()
    if len(audio_complet) < FREQUENCE_AUDIO * 0.4:
        return ""

    # Sélection du prompt initial pour guider le vocabulaire selon le mode
    initial_prompt = PROMPTS_WHISPER.get(mode_actuel, None)

    # Transcription guidée avec filtre vocal VAD (coupe le bruit moteur/vent du jeu) et fallback sûr
    try:
        segments_iter, _ = modele.transcribe(
            audio_complet,
            language="fr",
            task="transcribe",
            beam_size=5,
            initial_prompt=initial_prompt,
            condition_on_previous_text=False,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 350},
            no_speech_threshold=0.6
        )
        segments = list(segments_iter)
    except Exception:
        segments_iter, _ = modele.transcribe(
            audio_complet,
            language="fr",
            task="transcribe",
            beam_size=5,
            initial_prompt=initial_prompt,
            condition_on_previous_text=False
        )
        segments = list(segments_iter)

    texte = " ".join([segment.text for segment in segments]).strip()
    if not texte:
        return ""

    # Filtrage des hallucinations courantes, copies du prompt et boucles répétées de Whisper
    if _est_hallucination_whisper(texte, initial_prompt or ""):
        print(f"[STT] Hallucination / boucle Whisper filtrée : '{texte}'")
        return STT_INCOMPRIS if mode_actuel == "NORMAL" else ""

    # Contrôle de confiance Whisper en mode NORMAL (évite d'envoyer du charabia ou du bruit à GPT-4o-mini)
    if mode_actuel == "NORMAL" and segments:
        logprobs = [getattr(s, "avg_logprob", 0.0) for s in segments if getattr(s, "avg_logprob", None) is not None]
        no_speechs = [getattr(s, "no_speech_prob", 0.0) for s in segments if getattr(s, "no_speech_prob", None) is not None]
        moy_logprob = sum(logprobs) / len(logprobs) if logprobs else 0.0
        max_no_speech = max(no_speechs) if no_speechs else 0.0
        if max_no_speech > 0.78 or (moy_logprob < -1.15 and len(texte) < 35):
            print(f"[STT] Confiance trop faible (logprob={moy_logprob:.2f}, no_speech={max_no_speech:.2f}) pour : '{texte}'")
            return STT_INCOMPRIS

    # Nettoyage du préfixe d'interpellation du copilote
    nom_clean = nom_ia.lower()
    for prefixe in [f"{nom_clean},", f"{nom_clean}.", nom_clean]:
        if texte.lower().startswith(prefixe):
            texte = texte[len(prefixe):].strip()
            break

    # Nettoyage de fin de communication
    for mot in ["terminé.", "terminé", "terminée.", "terminée"]:
        if texte.lower().endswith(mot):
            texte = texte[:-len(mot)].strip()
            break

    # Correction phonétique ciblée en mode normal (ex: "la TH" / "la cache" -> "l'ATH")
    if mode_actuel == "NORMAL":
        texte = _corriger_termes_ed(texte)

    return texte
