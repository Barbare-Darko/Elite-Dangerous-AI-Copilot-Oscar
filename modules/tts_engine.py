"""Module de synthèse vocale (Edge-TTS) et gestion de l'état d'élocution anti-écho."""

import asyncio
import os
import re
import subprocess
import tempfile
import threading

import edge_tts

from modules.config_loader import VOIX_NEURALE, VOIX_VITESSE

_verrou_parole = threading.Lock()
_en_train_de_parler = False


def est_en_train_de_parler() -> bool:
    """Indique si l'IA est actuellement en train de parler."""
    return _en_train_de_parler


def dire_vocal(texte: str):
    """Génère la parole via Edge-TTS et la lit via le MediaPlayer Windows sans bloquer inutilement."""
    global _en_train_de_parler
    if not texte or not texte.strip():
        return

    with _verrou_parole:
        _en_train_de_parler = True
        chemin_mp3 = None
        try:
            # Nettoyage Markdown et symboles
            texte_vocal = texte.replace("**", "").replace("*", "").replace("#", "").replace("`", "")
            texte_vocal = re.sub(r'^\s*[-•]\s*', '', texte_vocal, flags=re.MULTILINE)
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
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", commande_ps],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as audio_err:
            print(f"[TTS] Erreur audio neurale : {audio_err}")
        finally:
            _en_train_de_parler = False
            if chemin_mp3 and os.path.exists(chemin_mp3):
                try:
                    os.remove(chemin_mp3)
                except Exception:
                    pass
