"""Module de synthèse vocale (Edge-TTS) et gestion de l'état d'élocution anti-écho."""

import asyncio
import os
import re
import subprocess
import tempfile
import threading
import time

import edge_tts

from modules.config_loader import VOIX_NEURALE, VOIX_VITESSE

_verrou_parole = threading.Lock()
_verrou_etat = threading.Lock()
_en_train_de_parler = False
_process_audio_actif = None
_id_parole = 0


def est_en_train_de_parler() -> bool:
    """Indique si l'IA est actuellement en train de parler."""
    return _en_train_de_parler


def arreter_parole() -> bool:
    """Interrompt immédiatement la synthèse vocale en cours (barge-in au PTT / 'Oscar').

    Retourne True si une parole ou génération audio était en cours et a été coupée.
    """
    global _id_parole, _process_audio_actif, _en_train_de_parler
    interrompu = False
    proc = None
    with _verrou_etat:
        _id_parole += 1
        if _en_train_de_parler or _process_audio_actif is not None:
            interrompu = True
        proc = _process_audio_actif
        _process_audio_actif = None

    if proc is not None:
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=0.3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    if interrompu:
        print("[TTS] Parole interrompue immédiatement (prise de parole Commandant).")
    return interrompu


def _lire_vocal_bloquant(texte: str, mon_id: int):
    """Exécute la génération Edge-TTS et la lecture interruptible dans le thread courant."""
    global _en_train_de_parler, _process_audio_actif
    with _verrou_parole:
        with _verrou_etat:
            if mon_id != _id_parole:
                return
            _en_train_de_parler = True

        chemin_mp3 = None
        proc = None
        try:
            # Nettoyage Markdown et symboles résiduels avant synthèse vocale
            texte_vocal = texte.replace("**", "").replace("__", "").replace("*", "").replace("#", "").replace("`", "")
            texte_vocal = re.sub(r'^\s*[-•]\s*', '', texte_vocal, flags=re.MULTILINE)
            texte_vocal = re.sub(r'\s*\(\s*\d[\d\s,.]*\s*[kMG]?\s*Cr\s*\)', '', texte_vocal, flags=re.IGNORECASE)
            texte_vocal = re.sub(r'\s+', ' ', texte_vocal).strip()

            if not texte_vocal:
                return

            async def _generer_audio():
                communicate = edge_tts.Communicate(texte_vocal, VOIX_NEURALE, rate=VOIX_VITESSE)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    chemin_temp = tmp.name
                await communicate.save(chemin_temp)
                return chemin_temp

            chemin_mp3 = asyncio.run(_generer_audio())

            # Si le Commandant a pressé PTT pendant la génération du MP3, on annule avant même de jouer
            with _verrou_etat:
                if mon_id != _id_parole:
                    return

            chemin_ps = chemin_mp3.replace("\\", "/")
            commande_ps = (
                "Add-Type -AssemblyName presentationCore; "
                "$player = New-Object System.Windows.Media.MediaPlayer; "
                f'$player.Open([Uri]"{chemin_ps}"); '
                "$player.Play(); "
                "Start-Sleep -Milliseconds 300; "
                "while ($player.Position -lt $player.NaturalDuration.TimeSpan) { Start-Sleep -Milliseconds 100 }; "
                "$player.Close();"
            )
            proc = subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", commande_ps],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            with _verrou_etat:
                if mon_id != _id_parole:
                    proc.terminate()
                    return
                _process_audio_actif = proc

            # Attente réactive permettant une coupure quasi instantanée (< 50 ms)
            while proc.poll() is None:
                if mon_id != _id_parole:
                    try:
                        proc.terminate()
                    except Exception:
                        pass
                    break
                time.sleep(0.05)

            try:
                proc.wait(timeout=0.3)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        except Exception as audio_err:
            print(f"[TTS] Erreur audio neurale : {audio_err}")
        finally:
            with _verrou_etat:
                if _process_audio_actif is proc:
                    _process_audio_actif = None
                _en_train_de_parler = False
            if chemin_mp3 and os.path.exists(chemin_mp3):
                for _ in range(5):
                    try:
                        os.remove(chemin_mp3)
                        break
                    except Exception:
                        time.sleep(0.05)


def dire_vocal(texte: str, bloquant: bool = True, interrompre_precedent: bool = False):
    """Génère la parole via Edge-TTS et la lit via MediaPlayer Windows (interruptible via arreter_parole).

    - bloquant=True : attend la fin de la lecture (ou l'interruption par arreter_parole).
    - bloquant=False : lance la lecture en arrière-plan pour laisser la boucle PTT immédiatement réactive.
    """
    global _id_parole
    if not texte or not texte.strip():
        return

    if interrompre_precedent:
        arreter_parole()

    with _verrou_etat:
        mon_id = _id_parole

    if bloquant:
        _lire_vocal_bloquant(texte, mon_id)
    else:
        threading.Thread(
            target=_lire_vocal_bloquant,
            args=(texte, mon_id),
            name="OscarTTS",
            daemon=True
        ).start()
