"""Module de reconnaissance vocale locale (STT) avec Faster-Whisper et capture Sounddevice."""

import time
import numpy as np
import sounddevice as sd
import keyboard
from faster_whisper import WhisperModel

FREQUENCE_AUDIO = 16000
_modele_whisper = None

PROMPTS_WHISPER = {
    "DICTEE": "Envoi, envoyer le message, poster le message, valider le message, expédier, paragraphe suivant, à la ligne, nouvelle ligne, corriger, effacer, stop.",
    "EPELLATION": "Alpha, Bravo, Charlie, Delta, Echo, Foxtrot, Golf, Hotel, India, Juliett, Kilo, Lima, Mike, November, Olivier, Papa, Quebec, Romeo, Sierra, Tango, Uniform, Victor, Whiskey, X-ray, Yankee, Zulu. Point, tiret, trait d'union, underscore, envoi, valider, corriger, effacer, stop."
}


def initialiser_whisper(model_size="large-v3-turbo", device="cuda", compute_type="float16") -> WhisperModel:
    """Initialise et met en cache le modèle Faster-Whisper sur GPU."""
    global _modele_whisper
    if _modele_whisper is None:
        print(f"[STT] Chargement du modèle Faster-Whisper ({model_size} sur {device})...")
        _modele_whisper = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("[STT] Modèle Faster-Whisper prêt.")
    return _modele_whisper


def enregistrer_et_transcrire(touche_micro: str, nom_ia: str = "Oscar", mode_actuel: str = "NORMAL") -> str:
    """Enregistre le son tant que la touche micro est enfoncée et transcrit le résultat avec prompt guidé."""
    modele = initialiser_whisper()
    blocs_audio = []

    def callback_audio(indata, frames, time_info, status):
        blocs_audio.append(indata.copy())

    with sd.InputStream(samplerate=FREQUENCE_AUDIO, channels=1, dtype='float32', callback=callback_audio):
        while keyboard.is_pressed(touche_micro):
            time.sleep(0.04)

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

    segments, _ = modele.transcribe(
        audio_complet,
        language="fr",
        task="transcribe",
        beam_size=5,
        initial_prompt=initial_prompt,
        condition_on_previous_text=False
    )
    texte = " ".join([segment.text for segment in segments]).strip()

    # Filtrage des hallucinations courantes de Whisper
    texte_lower = texte.lower()
    hallucinations = ["sous-titrage", "sous-titres", "amara.org", "merci d'avoir regardé", "merci d'avoir visionné"]
    if any(h in texte_lower for h in hallucinations):
        return ""

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

    return texte
