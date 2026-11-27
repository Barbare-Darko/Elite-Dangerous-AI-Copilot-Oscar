"""Module de vision locale à la demande (Ollama) et mode Photo pour Oscar.

Fonctionnalités :
- Capture ciblée de la fenêtre Elite Dangerous en résolution native complète
  (DPI-aware sur le thread courant uniquement, compatible multi-écrans & VR).
- Détection vocale déterministe (0 jeton OpenAI) :
  * Mode Analyse ("Regarde ! ...") : analyse visuelle locale via Ollama
    (qwen2.5vl:3b par défaut, keep_alive: 0 pour libérer immédiatement la VRAM)
    puis transmission uniquement du texte extrait à oscar_brain.py (0 token image).
  * Mode Photo ("Prendre une photo") : 0 jeton OpenAI. Masque temporairement
    le HUD d'Oscar, vérifie via Ollama si les commandes ATH de la caméra libre
    sont visibles (si oui, déclenche 'Désactiver ATH' via VoiceAttack et reprend
    la photo), sauvegarde en PNG résolution native dans le dossier Photos ED,
    confirme localement à la voix et vide immédiatement la RAM et la VRAM.
"""

from __future__ import annotations

import base64
import ctypes
from ctypes import wintypes
import gc
import glob
from io import BytesIO
import json
import math
import os
import re
import subprocess
import time
import unicodedata

import requests

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from PIL import Image, ImageGrab
    PIL_VISION_DISPONIBLE = True
except ImportError:
    Image = None
    ImageGrab = None
    PIL_VISION_DISPONIBLE = False

from modules.codex_ed import (
    calculer_nebuleuses_proches_codex,
    construire_dossier_codex_vision
)
from modules.config_loader import (
    CHEMIN_VOICEATTACK,
    CLE_API_OPENAI,
    DOSSIER_JOURNAUX_ED,
    DOSSIER_PHOTOS_ED,
    NOM_IA,
    VISION_CONFIG
)
from modules.telemetry_ed import analyser_journaux_locaux

# Constante Windows pour obtenir la résolution physique réelle sur ce thread uniquement
# sans impacter le rendu Tkinter du HUD Overlay.
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = ctypes.c_void_p(-4)

QUESTION_DEFAUT_VISION = (
    "Décris ce que tu vois à l'écran (environnement, cible, plante, roche, vaisseau, "
    "panneau ou informations clés affichées)."
)


# ==============================================================================
# NORMALISATION & DÉTECTION VOCALE DÉTERMINISTE (0 JETON OPENAI)
# ==============================================================================
def _normaliser_phrase(texte: str) -> str:
    """Supprime les accents, passe en minuscules et nettoie la ponctuation."""
    if not texte:
        return ""
    sans_acc = "".join(
        c for c in unicodedata.normalize("NFD", str(texte))
        if unicodedata.category(c) != "Mn"
    )
    propre = re.sub(r"[^a-z0-9\s]", " ", sans_acc.lower())
    return re.sub(r"\s+", " ", propre).strip()


def _retirer_prefixe_nom_ia(texte_original: str, nom_ia: str = NOM_IA) -> str:
    """Retire un éventuel appel initial du nom de l'IA (ex: 'Oscar, regarde !')."""
    if not texte_original:
        return ""
    nom_norm = _normaliser_phrase(nom_ia)
    if not nom_norm:
        return texte_original.strip()
    motif = rf"^\s*(?:(?:hey|eh|dis|salut)\s+)?{re.escape(nom_norm)}\b[\s,!:.\-–—]*"
    # On applique le match sur une version sans accents pour tolérer les variations
    sans_acc = "".join(
        c for c in unicodedata.normalize("NFD", texte_original)
        if unicodedata.category(c) != "Mn"
    )
    m = re.match(motif, sans_acc, flags=re.IGNORECASE)
    if m:
        # On retire le même nombre de mots au début du texte original
        nb_mots = len(re.findall(r"\w+", sans_acc[:m.end()]))
        if nb_mots > 0:
            motif_orig = r"^\s*" + r"\W+".join([r"[^\W_]+"] * nb_mots) + r"[\s,!:.\-–—]*"
            return re.sub(motif_orig, "", texte_original, count=1).strip()
    return texte_original.strip()


def detecter_commande_photo(texte: str, nom_ia: str = NOM_IA) -> bool:
    """Détecte une commande vocale directe de prise de photo (0 jeton OpenAI)."""
    if not VISION_CONFIG.get("photo_active", True) or not PIL_VISION_DISPONIBLE or not texte:
        return False

    sans_nom = _retirer_prefixe_nom_ia(texte, nom_ia)
    norm = _normaliser_phrase(sans_nom)
    if not norm:
        return False

    # Retire les formules de politesse fréquentes en fin de commande
    norm = re.sub(
        r"\b(?:s il te plait|sil te plait|s il vous plait|stp|svp|merci|maintenant|vite)\b$",
        "",
        norm
    ).strip()
    # Second passage si cumul (ex: "maintenant merci")
    norm = re.sub(
        r"\b(?:s il te plait|sil te plait|s il vous plait|stp|svp|merci|maintenant|vite)\b$",
        "",
        norm
    ).strip()

    commandes = VISION_CONFIG.get("commandes_photo", [])
    commandes_norm = {_normaliser_phrase(c) for c in commandes if c}
    return norm in commandes_norm


def detecter_commande_vision(texte: str, nom_ia: str = NOM_IA) -> tuple[bool, str]:
    """Détecte une demande d'analyse visuelle commençant par 'Regarde' (0 jeton de routage).

    Retourne (est_vision, question_extraite).
    """
    if not VISION_CONFIG.get("actif", False) or not PIL_VISION_DISPONIBLE or not texte:
        return False, ""

    sans_nom = _retirer_prefixe_nom_ia(texte, nom_ia)
    if not sans_nom:
        return False, ""

    sans_acc = "".join(
        c for c in unicodedata.normalize("NFD", sans_nom)
        if unicodedata.category(c) != "Mn"
    )
    prefixes = VISION_CONFIG.get("prefixes_analyse", ["regarde", "regardes", "regardez"])
    # Trier du plus long au plus court pour matcher les préfixes composés en premier
    prefixes_tries = sorted(
        [_normaliser_phrase(p) for p in prefixes if p],
        key=len,
        reverse=True
    )

    for pref in prefixes_tries:
        # Remplace les espaces par \s+ ou apostrophe pour tolérer "l'écran" / "l ecran"
        motif_pref = r"[\s']+".join(re.escape(mot) for mot in pref.split())
        motif = rf"^\s*{motif_pref}\b[\s,!:.\-–—?]*"
        m = re.match(motif, sans_acc, flags=re.IGNORECASE)
        if m:
            nb_mots_pref = len(pref.split())
            # Extrait le reste sur la chaîne originale (conserve accents & ponctuation)
            motif_orig = (
                r"^\s*"
                + r"[\s'\-]+".join([r"[^\W_]+"] * nb_mots_pref)
                + r"[\s,!:.\-–—?]*"
            )
            reste = re.sub(motif_orig, "", sans_nom, count=1).strip()
            question = reste if len(reste) >= 2 else QUESTION_DEFAUT_VISION
            return True, question

    return False, ""


# ==============================================================================
# CAPTURE D'ÉCRAN CIBLÉE ELITE DANGEROUS (RÉSOLUTION NATIVE INITIALE)
# ==============================================================================
def _trouver_rect_fenetre_ed() -> tuple[int, int, int, int] | None:
    """Recherche la fenêtre client d'Elite Dangerous et renvoie ses coordonnées écran exactes."""
    user32 = ctypes.windll.user32
    rect_trouve = []

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def _callback(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
            return True
        longueur = user32.GetWindowTextLengthW(hwnd)
        if longueur <= 0:
            return True
        buf = ctypes.create_unicode_buffer(longueur + 1)
        user32.GetWindowTextW(hwnd, buf, longueur + 1)
        titre = buf.value.lower()
        if "elite - dangerous" in titre or "elite dangerous" in titre:
            # Récupère la zone cliente exacte (sans bordures ni barre de titre)
            rect_client = wintypes.RECT()
            if user32.GetClientRect(hwnd, ctypes.byref(rect_client)):
                pt_hg = wintypes.POINT(rect_client.left, rect_client.top)
                pt_bd = wintypes.POINT(rect_client.right, rect_client.bottom)
                if user32.ClientToScreen(hwnd, ctypes.byref(pt_hg)) and user32.ClientToScreen(hwnd, ctypes.byref(pt_bd)):
                    largeur = pt_bd.x - pt_hg.x
                    hauteur = pt_bd.y - pt_hg.y
                    if largeur >= 320 and hauteur >= 240:
                        rect_trouve.append((pt_hg.x, pt_hg.y, pt_bd.x, pt_bd.y))
                        return False
        return True

    try:
        user32.EnumWindows(EnumWindowsProc(_callback), 0)
    except Exception as e:
        print(f"[Vision] Erreur énumération fenêtres Windows : {e}")

    return rect_trouve[0] if rect_trouve else None


def capturer_ecran_jeu() -> tuple[Image.Image, dict]:
    """Capture la fenêtre d'Elite Dangerous en résolution native (fallback écran principal).

    Active temporairement Per-Monitor DPI Awareness v2 uniquement sur le thread
    courant afin d'obtenir les vrais pixels natifs sans affecter le HUD Tkinter.
    """
    user32 = ctypes.windll.user32
    ancien_dpi_ctx = None
    set_thread_dpi = getattr(user32, "SetThreadDpiAwarenessContext", None)
    if set_thread_dpi is not None:
        try:
            set_thread_dpi.argtypes = [ctypes.c_void_p]
            set_thread_dpi.restype = ctypes.c_void_p
            ancien_dpi_ctx = set_thread_dpi(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
        except Exception:
            ancien_dpi_ctx = None

    try:
        rect_ed = _trouver_rect_fenetre_ed()
        if rect_ed:
            try:
                img = ImageGrab.grab(bbox=rect_ed, all_screens=True)
                meta = {
                    "source": "elite_dangerous",
                    "largeur": img.width,
                    "hauteur": img.height,
                    "bbox": rect_ed
                }
                return img, meta
            except Exception as e:
                print(f"[Vision] Fallback écran principal (capture fenêtre ED échouée : {e})")

        img = ImageGrab.grab()
        meta = {
            "source": "ecran_principal",
            "largeur": img.width,
            "hauteur": img.height,
            "bbox": None
        }
        return img, meta
    finally:
        if set_thread_dpi is not None and ancien_dpi_ctx:
            try:
                set_thread_dpi(ancien_dpi_ctx)
            except Exception:
                pass


def _encoder_image_base64(image: Image.Image, largeur_max: int = 1280, qualite_jpeg: int = 85) -> str:
    """Redimensionne une copie en mémoire et l'encode en base64 JPEG pour Ollama."""
    copie = image.convert("RGB")
    tampon = BytesIO()
    try:
        if largeur_max and copie.width > largeur_max:
            ratio = largeur_max / float(copie.width)
            nouvelle_hauteur = max(1, int(round(copie.height * ratio)))
            copie = copie.resize((largeur_max, nouvelle_hauteur), Image.Resampling.LANCZOS)
        copie.save(tampon, format="JPEG", quality=int(qualite_jpeg), optimize=True)
        return base64.b64encode(tampon.getvalue()).decode("ascii")
    finally:
        try:
            copie.close()
        except Exception:
            pass
        try:
            tampon.close()
        except Exception:
            pass


def liberer_memoire_vision(*images):
    """Ferme explicitement les images PIL en RAM et force la collecte mémoire."""
    for img in images:
        if img is not None:
            try:
                img.close()
            except Exception:
                pass
    gc.collect()


# ==============================================================================
# COMMUNICATION OLLAMA LOCALE (GPU NVIDIA / VRAM CONTRÔLÉE)
# ==============================================================================
def _url_ollama(endpoint: str) -> str:
    base = str(VISION_CONFIG.get("ollama_url", "http://127.0.0.1:11434")).rstrip("/")
    return f"{base}{endpoint}"


def verifier_ollama_disponible() -> tuple[bool, str]:
    """Vérifie qu'Ollama tourne en local et que le modèle vision configuré est installé."""
    modele_cible = str(VISION_CONFIG.get("modele", "qwen2.5vl:7b")).strip()
    try:
        rep = requests.get(_url_ollama("/api/tags"), timeout=2.5)
        if rep.status_code != 200:
            return False, f"Ollama a répondu avec le code HTTP {rep.status_code}."
        data = rep.json()
        modeles_dispos = [m.get("name", "") for m in data.get("models", [])]
        # Tolère l'absence de ':latest' si le nom de base correspond
        trouve = any(
            m == modele_cible or m.split(":")[0] == modele_cible and ":" not in modele_cible
            for m in modeles_dispos
        )
        if not trouve:
            return False, (
                f"Le modèle vision '{modele_cible}' n'est pas installé dans Ollama. "
                f"Exécutez : ollama pull {modele_cible}"
            )
        return True, "OK"
    except requests.ConnectionError:
        return False, "Le service local Ollama ne répond pas (vérifiez qu'Ollama est lancé)."
    except Exception as e:
        return False, f"Erreur de vérification Ollama : {e}"


def _trouver_executable_ollama() -> str | None:
    """Localise l'exécutable ollama.exe sans droit administrateur."""
    import shutil
    dans_path = shutil.which("ollama")
    if dans_path:
        return dans_path
    candidat = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe")
    if os.path.exists(candidat):
        return candidat
    return None


def demarrer_ollama_si_besoin(attente_max_s: float = 8.0) -> tuple[bool, str]:
    """Vérifie Ollama et tente un démarrage silencieux de 'ollama serve' s'il est installé."""
    ok, msg = verifier_ollama_disponible()
    if ok:
        return True, msg

    # Si Ollama répond déjà mais qu'il manque le modèle, inutile de le relancer
    if "n'est pas installé dans Ollama" in msg:
        return False, msg

    exe_ollama = _trouver_executable_ollama()
    if not exe_ollama:
        return False, msg

    try:
        print("[Vision] Service Ollama arrêté : démarrage automatique en arrière-plan...")
        subprocess.Popen(
            [exe_ollama, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        debut = time.time()
        while time.time() - debut < attente_max_s:
            time.sleep(0.5)
            ok2, msg2 = verifier_ollama_disponible()
            if ok2 or "n'est pas installé dans Ollama" in msg2:
                return ok2, msg2
    except Exception as e:
        return False, f"Impossible de démarrer Ollama automatiquement : {e}"

    return verifier_ollama_disponible()


def decharger_modele_ollama(modele: str = None):
    """Force le déchargement immédiat du modèle vision de la VRAM NVIDIA."""
    modele_cible = modele or str(VISION_CONFIG.get("modele", "qwen2.5vl:7b")).strip()
    try:
        requests.post(
            _url_ollama("/api/generate"),
            json={"model": modele_cible, "prompt": "", "keep_alive": 0, "stream": False},
            timeout=5
        )
    except Exception:
        pass


def _appeler_ollama_vision(
    image_b64: str,
    prompt_systeme: str,
    prompt_utilisateur: str,
    num_predict: int = 260,
    temperature: float = 0.2,
    forcer_keep_alive_zero: bool = False
) -> tuple[bool, str]:
    """Envoie une image encodée en base64 à l'API locale /api/chat d'Ollama."""
    modele = str(VISION_CONFIG.get("modele", "qwen2.5vl:7b")).strip()
    timeout_s = max(10, int(VISION_CONFIG.get("timeout_secondes", 60)))
    num_ctx = max(4096, int(VISION_CONFIG.get("num_ctx", 6144)))
    keep_alive = 0 if forcer_keep_alive_zero else VISION_CONFIG.get("keep_alive", 0)

    payload = {
        "model": modele,
        "stream": False,
        "keep_alive": keep_alive,
        "messages": [
            {"role": "system", "content": prompt_systeme},
            {
                "role": "user",
                "content": prompt_utilisateur,
                "images": [image_b64]
            }
        ],
        "options": {
            "temperature": float(temperature),
            "num_ctx": num_ctx,
            "num_predict": int(num_predict),
            "repeat_penalty": 1.15,
            "repeat_last_n": 64
        }
    }

    # Désactive le mode 'thinking' lent si l'utilisateur configure Qwen3-VL
    if "qwen3" in modele.lower():
        payload["think"] = False

    try:
        rep = requests.post(_url_ollama("/api/chat"), json=payload, timeout=timeout_s)
        if rep.status_code == 404:
            return False, (
                f"Modèle '{modele}' introuvable dans Ollama. "
                f"Lancez 'ollama pull {modele}' pour l'installer."
            )
        if rep.status_code != 200:
            return False, f"Erreur Ollama HTTP {rep.status_code} : {rep.text[:200]}"
        data = rep.json()
        contenu = (data.get("message") or {}).get("content", "").strip()
        if not contenu:
            return False, "Ollama a renvoyé une analyse vide."
        return True, contenu
    except requests.ConnectionError:
        return False, "Ollama local est hors ligne ou non démarré (127.0.0.1:11434)."
    except requests.Timeout:
        return False, f"Délai dépassé ({timeout_s}s) lors de l'analyse vision locale."
    except Exception as e:
        return False, f"Erreur lors de l'appel Ollama Vision : {e}"


# ==============================================================================
# SÉLECTION DU MOTEUR VISION ("openai" OU "ollama") & CATALOGUE ASTRONOMIQUE ED
# ==============================================================================
_client_openai_vision = None


def obtenir_moteur_vision() -> str:
    """Retourne le moteur vision configuré : 'openai' (direct, 0 VRAM) ou 'ollama' (local)."""
    m = str(VISION_CONFIG.get("moteur", "ollama")).strip().lower()
    return "openai" if m == "openai" else "ollama"


def _get_client_openai_vision():
    """Initialise paresseusement le client OpenAI pour la détection ATH / vision directe."""
    global _client_openai_vision
    if _client_openai_vision is None and OpenAI is not None and CLE_API_OPENAI:
        _client_openai_vision = OpenAI(api_key=CLE_API_OPENAI)
    return _client_openai_vision


# Coordonnées galactiques 3D EDSM (x, y, z en AL depuis Sol) des grandes nébuleuses d'Elite Dangerous
NEBULEUSES_ELITE_DANGEROUS = [
    ("Boucle de Barnard", (617.0, -422.0, -1225.0), "immense arc rouge-orangé en demi-cercle"),
    ("Nébuleuse d'Orion", (610.0, -430.0, -1210.0), "tache brillante rose/blanche au cœur de la Boucle de Barnard"),
    ("Nébuleuse de la Tête de Cheval", (560.0, -370.0, -1170.0), "nuage sombre et rouge près de la Boucle de Barnard"),
    ("Nébuleuse de la Flamme", (565.0, -370.0, -1165.0), "nuage rouge-orangé brillant contre la Tête de Cheval"),
    ("Nébuleuse de l'Homme qui court", (605.0, -435.0, -1215.0), "voile bleu/violet collé à Orion"),
    ("Nébuleuse de la Tête de Sorcière", (360.0, -718.0, -386.0), "voile bleuté-violet"),
    ("Nébuleuse des Pléiades", (-78.0, -149.0, -340.0), "amas d'étoiles bleues brillantes"),
    ("Nébuleuse de la Californie", (-304.0, -236.0, -861.0), "filament rouge allongé"),
    ("Nébuleuse de la Mouette", (2680.0, -155.0, -2704.0), "nuage rouge allongé en forme d'oiseau"),
    ("Nébuleuse de la Rosette", (2050.0, -100.0, -4800.0), "couronne/nuage rougeoyant"),
    ("Nébuleuse de la Méduse", (1090.0, 90.0, -4900.0), "nuage rouge-rosé"),
    ("Nébuleuse de la Tête de Singe", (1050.0, 20.0, -6100.0), "nuage rouge compact"),
    ("Nébuleuse du Crabe", (450.0, -600.0, -6950.0), "rémanent de supernova bleuté-orangé"),
    ("Nébuleuse du Sac à Charbon (Coalsack)", (405.0, 53.0, 304.0), "grande nébuleuse obscure noire sur la Voie Lactée"),
    ("Nébuleuse du Voile Ouest", (-1400.0, -250.0, 500.0), "filaments bleus et roses"),
    ("Nébuleuse du Voile Est", (-1470.0, -220.0, 460.0), "filaments rouges et bleus"),
    ("Nébuleuse de l'Amérique du Nord", (-1920.0, -15.0, 250.0), "grand nuage rouge-rose"),
    ("Nébuleuse du Pélican", (-1900.0, -15.0, 240.0), "nuage rouge voisin de l'Amérique du Nord"),
    ("Nébuleuse de la Lagune", (-460.0, -120.0, 4460.0), "nuage rose-rouge brillant"),
    ("Nébuleuse Trifide", (-465.0, -70.0, 5130.0), "nuage rouge et bleu"),
    ("Nébuleuse Oméga", (-1350.0, -80.0, 5400.0), "nuage rouge-orangé"),
    ("Nébuleuse de l'Aigle", (-1740.0, 80.0, 6780.0), "nuage doré-rouge (Piliers de la Création)"),
    ("Nébuleuse de la Carène", (6300.0, -200.0, 3800.0), "immense nuage rouge et bleu"),
    ("Nébuleuse du Cœur", (-4550.0, 280.0, -5650.0), "grand nuage rouge"),
    ("Nébuleuse de l'Âme", (-4350.0, 310.0, -5950.0), "grand nuage rouge voisin du Cœur"),
    ("NGC 7822", (-2100.0, 290.0, -1720.0), "chapelet très lumineux d'étoiles bleues alignées")
]


def _calculer_nebuleuses_proches(star_pos: list | tuple | None, top_n: int = 4) -> list[str]:
    """Calcule les grandes nébuleuses d'Elite Dangerous les plus proches des coordonnées StarPos."""
    if not star_pos or len(star_pos) != 3:
        return []
    try:
        sx, sy, sz = float(star_pos[0]), float(star_pos[1]), float(star_pos[2])
    except Exception:
        return []
    distances = []
    for nom, (nx, ny, nz), aspect in NEBULEUSES_ELITE_DANGEROUS:
        d = math.sqrt((sx - nx) ** 2 + (sy - ny) ** 2 + (sz - nz) ** 2)
        distances.append((d, nom, aspect))
    distances.sort(key=lambda item: item[0])
    return [f"{nom} (~{int(round(d))} AL, {aspect})" for d, nom, aspect in distances[:top_n]]


def _lire_donnees_scientifiques_journal(corps_cible: str = "") -> dict:
    """Extrait StarPos, Scan planétaire (volcanisme, atmosphère, gravité, T°), signaux SAA/FSS et Codex du dernier journal."""
    infos = {
        "star_pos": None,
        "classe_planete": "",
        "volcanisme": "",
        "atmosphere": "",
        "gravite_g": None,
        "temperature_k": None,
        "temperature_c": None,
        "was_discovered": None,
        "was_mapped": None,
        "was_footfalled": None,
        "signaux_biologiques": 0,
        "signaux_geologiques": 0,
        "genres_biologiques": [],
        "codex_recents": []
    }
    try:
        fichiers = sorted(
            glob.glob(os.path.join(DOSSIER_JOURNAUX_ED, "Journal.*.log")),
            key=os.path.getmtime
        )
        if not fichiers:
            return infos

        corps_norm = (corps_cible or "").strip().lower()
        scans_par_corps = {}
        signaux_par_corps = {}
        genres_par_corps = {}
        dernier_corps_approche = ""

        with open(fichiers[-1], "r", encoding="utf-8", errors="ignore") as f:
            for ligne in f:
                if not ligne or "{" not in ligne:
                    continue
                if not any(k in ligne for k in (
                    '"StarPos"', '"Scan"', '"SAASignalsFound"', '"FSSBodySignals"',
                    '"CodexEntry"', '"ApproachBody"', '"Touchdown"', '"Disembark"'
                )):
                    continue
                try:
                    ev = json.loads(ligne)
                except Exception:
                    continue

                etype = ev.get("event", "")
                if "StarPos" in ev and isinstance(ev["StarPos"], list) and len(ev["StarPos"]) == 3:
                    infos["star_pos"] = ev["StarPos"]

                if etype in ("ApproachBody", "Touchdown", "Disembark"):
                    b = ev.get("Body") or ev.get("BodyName") or ""
                    if b:
                        dernier_corps_approche = str(b)

                elif etype == "Scan":
                    bname = str(ev.get("BodyName") or "").strip()
                    if bname:
                        scans_par_corps[bname.lower()] = ev

                elif etype in ("SAASignalsFound", "FSSBodySignals"):
                    bname = str(ev.get("BodyName") or "").strip()
                    if bname:
                        cle = bname.lower()
                        s_bio = 0
                        s_geo = 0
                        for sig in ev.get("Signals", []):
                            stype = str(sig.get("Type", "")).lower()
                            cnt = int(sig.get("Count", 0) or 0)
                            if "biological" in stype:
                                s_bio = max(s_bio, cnt)
                            elif "geological" in stype:
                                s_geo = max(s_geo, cnt)
                        prev = signaux_par_corps.get(cle, (0, 0))
                        signaux_par_corps[cle] = (max(prev[0], s_bio), max(prev[1], s_geo))

                        genres = []
                        for g in ev.get("Genuses", []):
                            nom_g = g.get("Genus_Localised") or g.get("Genus") or ""
                            if nom_g:
                                genres.append(str(nom_g))
                        if genres:
                            genres_par_corps[cle] = genres

                elif etype == "CodexEntry":
                    nom_c = ev.get("Name_Localised") or ev.get("Name") or ""
                    if nom_c and nom_c not in infos["codex_recents"]:
                        infos["codex_recents"].append(str(nom_c))

        cle_corps = corps_norm or dernier_corps_approche.lower()
        if cle_corps and cle_corps in scans_par_corps:
            sc = scans_par_corps[cle_corps]
            infos["classe_planete"] = str(sc.get("PlanetClass") or "")
            infos["volcanisme"] = str(sc.get("Volcanism_Localised") or sc.get("Volcanism") or "")
            infos["atmosphere"] = str(sc.get("Atmosphere_Localised") or sc.get("Atmosphere") or sc.get("AtmosphereType") or "")
            if sc.get("SurfaceGravity"):
                infos["gravite_g"] = round(float(sc["SurfaceGravity"]) / 9.80665, 2)
            if sc.get("SurfaceTemperature"):
                tk = float(sc["SurfaceTemperature"])
                infos["temperature_k"] = round(tk)
                infos["temperature_c"] = round(tk - 273.15)
            if "WasDiscovered" in sc:
                infos["was_discovered"] = bool(sc.get("WasDiscovered"))
            if "WasMapped" in sc:
                infos["was_mapped"] = bool(sc.get("WasMapped"))
            if "WasFootfalled" in sc:
                infos["was_footfalled"] = bool(sc.get("WasFootfalled"))

        if cle_corps and cle_corps in signaux_par_corps:
            infos["signaux_biologiques"], infos["signaux_geologiques"] = signaux_par_corps[cle_corps]
        if cle_corps and cle_corps in genres_par_corps:
            infos["genres_biologiques"] = genres_par_corps[cle_corps]
        infos["codex_recents"] = infos["codex_recents"][-5:]
    except Exception:
        pass
    return infos


# ==============================================================================
# CONTEXTE TÉLÉMÉTRIQUE & SCIENTIFIQUE POUR GUIDER L'ANALYSE ELITE DANGEROUS
# ==============================================================================
def _question_concerne_ciel(question: str) -> bool:
    """Détecte si la question visuelle porte sur le ciel profond (nébuleuse, galaxie, étoile lointaine)."""
    norm = _normaliser_phrase(question)
    mots_ciel = (
        "nebuleuse", "nemuleuse", "nubleuse", "galaxie", "voie lactee", "ciel", "etoile",
        "constellation", "nuage", "magellan", "andromede", "barnard", "orion", "amas",
        "pulsar", "trou noir", "tache rouge", "tache bleue", "arc rouge", "point lumineux",
        "tete de sorciere", "witch head"
    )
    return any(m in norm for m in mots_ciel)


def _detecter_couleur_question_ciel(question: str) -> str:
    """Extrait une éventuelle couleur explicite dans une question d'astronomie ('rouge', 'bleu', 'sombre' ou '')."""
    norm = _normaliser_phrase(question)
    if any(m in norm for m in ("rouge", "orange", "orangee", "rose", "rougeo")):
        return "rouge"
    if any(m in norm for m in ("bleu", "bleue", "bleute", "bleutee", "violet", "violette", "cyan")):
        return "bleu"
    if any(m in norm for m in ("sombre", "noir", "noire", "obscur", "obscure")):
        return "sombre"
    return ""


def _construire_contexte_ed_vision(question_pilote: str = "") -> dict:
    """Collecte le contexte temps réel + données scientifiques planétaires et nébuleuses proches."""
    est_ciel = _question_concerne_ciel(question_pilote)
    couleur_ciel = _detecter_couleur_question_ciel(question_pilote) if est_ciel else ""
    contexte = {
        "vue": "cockpit ou caméra",
        "est_surface_ou_approche": False,
        "est_question_ciel": est_ciel,
        "couleur_ciel": couleur_ciel,
        "systeme": "Inconnu",
        "corps_celeste": "Inconnu",
        "vaisseau": "Inconnu",
        "destination_ciblee": "",
        "classe_planete": "",
        "volcanisme": "",
        "atmosphere": "",
        "gravite_g": None,
        "temperature_k": None,
        "temperature_c": None,
        "was_discovered": None,
        "was_mapped": None,
        "was_footfalled": None,
        "signaux_biologiques": 0,
        "signaux_geologiques": 0,
        "genres_biologiques": [],
        "codex_recents": [],
        "nebuleuses_proches": []
    }

    # 1. Lecture ultra-rapide de Status.json
    chemin_status = os.path.join(DOSSIER_JOURNAUX_ED, "Status.json")
    body_status = ""
    est_pose_ou_proche = False
    if os.path.exists(chemin_status):
        try:
            with open(chemin_status, "r", encoding="utf-8") as f:
                st = json.load(f)
            flags = st.get("Flags", 0)
            flags2 = st.get("Flags2", 0)
            gui_focus = st.get("GuiFocus", 0)

            est_a_pied = bool(flags2 & 1)
            est_vrs = bool(flags & 67108864)
            est_pose = bool(flags & 2)
            en_supercruise = bool(flags & 16)
            a_altitude = "Altitude" in st

            if gui_focus == 6:
                contexte["vue"] = "carte galactique"
            elif gui_focus == 7:
                contexte["vue"] = "carte du système"
            elif gui_focus == 9:
                contexte["vue"] = "scanner ACS (FSS)"
            elif gui_focus == 10:
                contexte["vue"] = "scanner de surface (DSS)"
            elif est_a_pied:
                contexte["vue"] = "à pied (Odyssey / exobiologie)"
            elif est_vrs:
                contexte["vue"] = "VRS (véhicule planétaire)"
            elif en_supercruise:
                contexte["vue"] = "cockpit en super-navigation"
            else:
                contexte["vue"] = "cockpit / vol normal ou caméra"

            est_pose_ou_proche = (
                est_a_pied or est_vrs or est_pose or gui_focus == 10
                or (a_altitude and not en_supercruise)
            )

            dest = st.get("Destination")
            if isinstance(dest, dict) and dest.get("Name"):
                contexte["destination_ciblee"] = str(dest.get("Name"))
            if st.get("BodyName"):
                body_status = str(st.get("BodyName"))
        except Exception:
            pass

    contexte["est_surface_ou_approche"] = est_pose_ou_proche and not _question_concerne_ciel(question_pilote)

    # 2. Infos de base des journaux locaux
    try:
        j = analyser_journaux_locaux()
        contexte["systeme"] = j.get("systeme", "Inconnu")
        contexte["corps_celeste"] = body_status or j.get("corps_celeste", "Inconnu")
        v = j.get("vaisseau_actif", {})
        if v.get("modele"):
            contexte["vaisseau"] = (
                f"{v['nom']} ({v['modele']})" if v.get("nom") else v["modele"]
            )
    except Exception:
        if body_status:
            contexte["corps_celeste"] = body_status

    # 3. Données scientifiques locales (Volcanisme, Bio/Géo, StarPos -> nébuleuses proches)
    corps_ref = contexte["corps_celeste"] if contexte["corps_celeste"] != "Inconnu" else ""
    sci = _lire_donnees_scientifiques_journal(corps_ref)
    for k in (
        "classe_planete", "volcanisme", "atmosphere", "gravite_g",
        "temperature_k", "temperature_c", "was_discovered", "was_mapped",
        "was_footfalled", "signaux_biologiques",
        "signaux_geologiques", "genres_biologiques", "codex_recents"
    ):
        contexte[k] = sci.get(k, contexte[k])
    contexte["nebuleuses_proches"] = calculer_nebuleuses_proches_codex(
        sci.get("star_pos"),
        top_n=8,
        couleur_filtre=contexte.get("couleur_ciel", "")
    )

    return contexte


def formater_contexte_scientifique_ed(contexte: dict) -> str:
    """Construit un bloc texte compact et riche des données télémétriques/scientifiques locales."""
    if not contexte:
        return ""
    lignes = [
        f"Vue : {contexte.get('vue', 'écran')} | Système : {contexte.get('systeme', 'Inconnu')} | "
        f"Corps : {contexte.get('corps_celeste', 'Inconnu')} | Vaisseau : {contexte.get('vaisseau', 'Inconnu')}"
    ]
    if contexte.get("destination_ciblee"):
        lignes.append(f"Destination ciblée (télémétrie) : {contexte['destination_ciblee']}")

    if contexte.get("est_surface_ou_approche", True):
        details_planete = []
        if contexte.get("classe_planete"):
            details_planete.append(f"Type : {contexte['classe_planete']}")
        if contexte.get("volcanisme"):
            details_planete.append(f"Volcanisme exact : {contexte['volcanisme']}")
        if contexte.get("atmosphere"):
            details_planete.append(f"Atmosphère : {contexte['atmosphere']}")
        if contexte.get("gravite_g") is not None:
            details_planete.append(f"Gravité : {contexte['gravite_g']} G")
        if contexte.get("temperature_k") is not None:
            details_planete.append(f"Température surface : {contexte['temperature_k']} K ({contexte['temperature_c']} °C)")
        if details_planete:
            lignes.append("Données planète (Scan ED) : " + " | ".join(details_planete))

        if contexte.get("signaux_geologiques") or contexte.get("signaux_biologiques") or contexte.get("genres_biologiques"):
            s_parts = []
            if contexte.get("signaux_geologiques"):
                s_parts.append(f"{contexte['signaux_geologiques']} signaux géologiques")
            if contexte.get("signaux_biologiques"):
                s_parts.append(f"{contexte['signaux_biologiques']} signaux biologiques")
            if contexte.get("genres_biologiques"):
                s_parts.append("Genres exobiologie présents sur cette planète : " + ", ".join(contexte["genres_biologiques"]))
            lignes.append("Signaux planète : " + " | ".join(s_parts))

        if contexte.get("codex_recents"):
            lignes.append("Entrées Codex récentes : " + ", ".join(contexte["codex_recents"]))

        dossier_codex = construire_dossier_codex_vision(contexte)
        if dossier_codex:
            lignes.append(dossier_codex)

    if contexte.get("nebuleuses_proches"):
        lignes.append("Grandes nébuleuses / POIs Elite Dangerous proches de ta position : " + " ; ".join(contexte["nebuleuses_proches"]))

    return "\n".join(lignes)


# ==============================================================================
# WORKFLOW 1 : ANALYSE VISUELLE ("REGARDE ! ...") -> TEXTE SEUL POUR OSCAR
# ==============================================================================
def _question_concerne_ath(question: str) -> bool:
    """Détecte si la question porte sur la lecture de chiffres/textes sur l'ATH cockpit."""
    norm = _normaliser_phrase(question)
    mots_cles = (
        "temps", "combien", "distance", "vitesse", "destination", "arriver", "arrivee",
        "cible", "eta", "heure", "minute", "seconde", "sl", "al", "km", "vitesse",
        "carburant", "temperature", "bouclier", "coque", "panneau", "lis", "lire",
        "affiche", "ecrit", "prix", "credit", "mission", "altitude", "gravite"
    )
    return any(re.search(rf"\b{re.escape(m)}\b", norm) for m in mots_cles)


def _recadrer_zone_ath_ultrawide(image: Image.Image) -> Image.Image:
    """Recadre la zone centrale 16:9 d'un écran ultrawide (ex: 3440x1440 -> 2560x1440).

    Dans Elite Dangerous, 100 % des instruments ATH du cockpit (panneau cible bas-gauche,
    réticule central avec distance/chrono, radar et jauge de vitesse) se situent dans la
    zone centrale 16:9. Ce recadrage double quasiment la netteté OCR pour Ollama.
    """
    w, h = image.size
    if h <= 0 or (w / float(h)) <= 1.9:
        return image
    largeur_16_9 = min(w, int(round(h * (16.0 / 9.0))))
    marge_x = max(0, (w - largeur_16_9) // 2)
    return image.crop((marge_x, 0, marge_x + largeur_16_9, h))


def _extraire_resume_hud(texte_analyse: str) -> tuple[str, str]:
    """Sépare la description complète et la ligne éventuelle RESUME_HUD (jamais vide)."""
    if not texte_analyse:
        return "", ""
    lignes = texte_analyse.splitlines()
    lignes_desc = []
    resume_hud = ""
    for ligne in lignes:
        m = re.match(r"^\s*RESUME_HUD\s*:\s*(.+)$", ligne, flags=re.IGNORECASE)
        if m:
            resume_hud = m.group(1).strip()
        else:
            lignes_desc.append(ligne)
    desc_propre = "\n".join(lignes_desc).strip()
    # Garde-fou critique : si Ollama a tout mis sur RESUME_HUD, on ne renvoie jamais une chaîne vide
    if not desc_propre:
        desc_propre = resume_hud or texte_analyse.strip()
    if not resume_hud:
        # Fallback : première phrase concise
        premiere = re.split(r"(?<=[.!?])\s+", desc_propre)[0] if desc_propre else ""
        resume_hud = premiere[:160].strip()
    return desc_propre, resume_hud


def preparer_capture_vision(question_pilote: str) -> dict:
    """Capture l'écran de jeu, prépare l'image JPEG base64 et collecte le contexte scientifique ED."""
    t0 = time.time()
    question = (question_pilote or "").strip() or QUESTION_DEFAUT_VISION
    contexte = _construire_contexte_ed_vision(question)
    est_question_ath = _question_concerne_ath(question)

    image_capture = None
    image_travail = None
    zoom_applique = False
    try:
        image_capture, meta = capturer_ecran_jeu()
        largeur_max = int(VISION_CONFIG.get("largeur_max_analyse", 1600))
        qualite = int(VISION_CONFIG.get("qualite_jpeg_analyse", 85))
        zoom_autorise = bool(VISION_CONFIG.get("zoom_ath_ultrawide", True))

        # Sur écran ultrawide (ex: 3440x1440), recadre la zone cockpit 16:9 centrale pour l'OCR ATH
        if zoom_autorise and est_question_ath and "carte" not in contexte.get("vue", ""):
            image_travail = _recadrer_zone_ath_ultrawide(image_capture)
            zoom_applique = image_travail is not image_capture
        else:
            image_travail = image_capture

        image_b64 = _encoder_image_base64(image_travail, largeur_max, qualite)
        return {
            "succes": True,
            "erreur": "",
            "image_b64": image_b64,
            "question": question,
            "contexte_jeu": contexte,
            "est_question_ath": est_question_ath,
            "zoom_applique": zoom_applique,
            "resolution": f"{meta['largeur']}x{meta['hauteur']}",
            "debut": t0
        }
    except Exception as e:
        return {
            "succes": False,
            "erreur": f"Échec de capture d'écran : {e}",
            "image_b64": "",
            "question": question,
            "contexte_jeu": contexte,
            "est_question_ath": est_question_ath,
            "zoom_applique": False,
            "resolution": "",
            "debut": t0
        }
    finally:
        if image_travail is not None and image_travail is not image_capture:
            liberer_memoire_vision(image_travail, image_capture)
        else:
            liberer_memoire_vision(image_capture)


def analyser_ecran_pour_oscar(question_pilote: str, capture_prete: dict = None) -> dict:
    """Capture l'écran de jeu, l'analyse localement via Ollama et renvoie uniquement du texte."""
    cap = capture_prete or preparer_capture_vision(question_pilote)
    t0 = cap.get("debut", time.time())
    question = cap.get("question", QUESTION_DEFAUT_VISION)
    contexte = cap.get("contexte_jeu", {})

    if not cap.get("succes"):
        return {
            "succes": False,
            "erreur": cap.get("erreur", "Échec de capture d'écran."),
            "description": "",
            "resume_hud": "Erreur capture ecran",
            "question": question,
            "contexte_jeu": contexte,
            "resolution": cap.get("resolution", ""),
            "duree_secondes": round(time.time() - t0, 2)
        }

    image_b64 = cap["image_b64"]
    est_question_ath = cap.get("est_question_ath", False)
    zoom_applique = cap.get("zoom_applique", False)
    resolution = cap.get("resolution", "")

    consigne_ath_spe = ""
    if est_question_ath:
        consigne_ath_spe = (
            "Zones ATH à lire si présentes : bas-gauche (cible et distance en sl/ksl/km/al), "
            "haut-droite du radar central (vitesse en km/s, m/s ou c), haut-gauche du radar (température %), "
            "centre/viseur (distance et chrono : format M:SS = minutes:secondes, jamais heures sauf s'il y a 3 nombres H:MM:SS). "
            "Recopie exactement les nombres et unités lus.\n"
        )

    prompt_systeme = (
        "Tu es un capteur optique factuel pour le jeu Elite Dangerous (Odyssey). "
        "Réponds en français, de façon directe, honnête et précise (2 à 4 phrases max, sans humour).\n"
        "- Décris D'ABORD visuellement l'objet principal au centre de la scène (forme, couleur, lumière, texture) AVANT les données HUD.\n"
        "- Géologie / Exobiologie : distingue clairement un jet de lave orange/rouge incandescent (cheminée/évent de lave/magma), "
        "un panache de vapeur ou glace blanche (geyser/fumerolle), un cratère, une roche, ou une plante/organisme (décris sa forme et couleur exacte).\n"
        "- Astronomie : décris précisément la forme et couleur (ex: 'grand arc rouge en demi-cercle', 'large bande lumineuse de la Voie Lactée', "
        "'petite galaxie bleutée', 'nuage rouge compact') sans jamais affirmer que l'objet n'a pas de nom dans le jeu.\n"
        "- N'invente JAMAIS un texte, un chiffre ni une température impossible (les Kelvin sont toujours > 0 K).\n"
        "- En cockpit : 'CARB. X/h' est la consommation horaire ; 'CHAMP GRAVIT.', 'TRAIN D'ATTERR.' et 'RÉCUP. CARG.' "
        "sont des voyants inactifs quand leurs cases sont vides.\n"
        "- Ignore l'encart HUD d'Oscar dans un coin et les notifications Windows.\n"
        f"{consigne_ath_spe}"
        "Termine toujours par une dernière ligne : RESUME_HUD: <résumé factuel très court séparé par ' | '>"
    )

    bloc_contexte = formater_contexte_scientifique_ed(contexte)
    prompt_utilisateur = (
        f"Contexte scientifique Elite Dangerous :\n{bloc_contexte}\n"
        f"Question du Commandant : {question}"
    )

    succes, reponse_brute = _appeler_ollama_vision(
        image_b64=image_b64,
        prompt_systeme=prompt_systeme,
        prompt_utilisateur=prompt_utilisateur,
        num_predict=280,
        temperature=0.15
    )
    del image_b64
    gc.collect()

    duree = round(time.time() - t0, 2)
    tag_zoom = "+zoom16:9" if zoom_applique else ""

    if not succes:
        return {
            "succes": False,
            "erreur": reponse_brute,
            "description": "",
            "resume_hud": "Ollama hors ligne",
            "question": question,
            "contexte_jeu": contexte,
            "resolution": resolution,
            "duree_secondes": duree
        }

    description, resume_hud = _extraire_resume_hud(reponse_brute)
    print(f"[Vision] Analyse Ollama ({VISION_CONFIG.get('modele')}) en {duree}s [{resolution}{tag_zoom}] : {description}")
    return {
        "succes": True,
        "erreur": "",
        "description": description,
        "resume_hud": resume_hud,
        "question": question,
        "contexte_jeu": contexte,
        "resolution": resolution,
        "duree_secondes": duree
    }


# ==============================================================================
# WORKFLOW 2 : MODE PHOTO ("PRENDRE UNE PHOTO")
# ==============================================================================
def _detecter_ath_via_openai(image_b64: str, prompt_systeme: str, prompt_utilisateur: str) -> tuple[bool, str]:
    """Détection ultra-légère des commandes ATH caméra via OpenAI (detail='low', 0 VRAM)."""
    client = _get_client_openai_vision()
    if client is None:
        return False, "Client OpenAI indisponible (clé API manquante)."
    modele_oa = str(VISION_CONFIG.get("modele_openai", "gpt-4o-mini")).strip() or "gpt-4o-mini"
    try:
        rep = client.chat.completions.create(
            model=modele_oa,
            max_tokens=40,
            temperature=0.0,
            messages=[
                {"role": "system", "content": prompt_systeme},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_utilisateur},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}",
                                "detail": "low"
                            }
                        }
                    ]
                }
            ]
        )
        txt = (rep.choices[0].message.content or "").strip()
        return (True, txt) if txt else (False, "Réponse OpenAI vide.")
    except Exception as e:
        return False, f"Erreur OpenAI ATH : {e}"


def _detecter_ath_camera_visible(image_native: Image.Image) -> tuple[bool | None, str]:
    """Vérifie si les commandes ATH / caméra libre sont visibles (selon le moteur configuré).

    Exige la citation de mots réellement lus pour éliminer les faux positifs (yes-bias).
    Retourne :
    - (True, reponse) si des commandes ATH sont détectées
    - (False, reponse) si l'image est propre sans commandes ATH caméra
    - (None, message_erreur) si le moteur est indisponible
    """
    moteur = obtenir_moteur_vision()
    largeur = 960 if moteur == "openai" else 1024
    image_b64 = _encoder_image_base64(image_native, largeur_max=largeur, qualite_jpeg=80)
    prompt_systeme = (
        "Tu es un détecteur OCR strict pour les captures d'écran du jeu Elite Dangerous. "
        "N'invente JAMAIS de texte qui n'est pas réellement écrit sur l'image."
    )
    prompt_utilisateur = (
        "Observe attentivement cette image du jeu Elite Dangerous (en particulier le bas et le haut de l'écran, "
        "en ignorant d'éventuelles pop-ups Windows blanches dans un coin). "
        "Vois-tu affichées des commandes texte de l'interface caméra / ATH du jeu "
        "(par exemple des légendes de touches ou bandeaux comme 'CAMÉRA LIBRE', 'MASQUER ATH', "
        "'QUITTER', 'ZOOM', 'FLOU', 'VITESSE CAMÉRA', '[1]', 'IU [JOYSTICK...]') ?\n"
        "- Si OUI : recopie exactement 2 ou 3 mots que tu lis puis termine par 'ATH: OUI'.\n"
        "- S'il n'y a AUCUN texte d'interface de commande du jeu visible : réponds UNIQUEMENT 'ATH: NON'."
    )
    try:
        if moteur == "openai":
            succes, rep = _detecter_ath_via_openai(image_b64, prompt_systeme, prompt_utilisateur)
        else:
            succes, rep = _appeler_ollama_vision(
                image_b64=image_b64,
                prompt_systeme=prompt_systeme,
                prompt_utilisateur=prompt_utilisateur,
                num_predict=45,
                temperature=0.0,
                forcer_keep_alive_zero=True
            )
    finally:
        del image_b64
        gc.collect()

    if not succes:
        return None, rep

    norm = _normaliser_phrase(rep)
    if "ath non" in norm:
        return False, rep
    if "ath oui" in norm:
        return True, rep
    if norm.startswith("oui") and "aucun" not in norm:
        return True, rep
    return False, rep


def _generer_chemin_photo(dossier_photos: str) -> str:
    """Génère un chemin de fichier PNG horodaté unique dans le dossier photos ED."""
    os.makedirs(dossier_photos, exist_ok=True)
    prefixe = str(VISION_CONFIG.get("prefixe_nom_photo", "Oscar")).strip() or "Oscar"
    horodatage = time.strftime("%Y%m%d_%H%M%S")
    candidat = os.path.join(dossier_photos, f"{prefixe}_{horodatage}.png")
    compteur = 1
    while os.path.exists(candidat):
        candidat = os.path.join(dossier_photos, f"{prefixe}_{horodatage}_{compteur}.png")
        compteur += 1
    return candidat


def _declencher_commande_va_ath(nom_commande: str) -> bool:
    """Envoie la commande VoiceAttack pour masquer/afficher l'ATH (ex: 'Désactiver ATH')."""
    if not nom_commande or not os.path.exists(CHEMIN_VOICEATTACK):
        print(f"[Vision/Photo] VoiceAttack introuvable ou commande vide ({nom_commande}).")
        return False
    try:
        print(f"[Vision/Photo] Exécution VoiceAttack : {nom_commande}")
        subprocess.Popen([CHEMIN_VOICEATTACK, "-command", nom_commande])
        return True
    except Exception as e:
        print(f"[Vision/Photo] Erreur lancement VoiceAttack ({nom_commande}) : {e}")
        return False


def prendre_photo_jeu(hud=None) -> dict:
    """Capture et enregistre une photo pleine résolution dans le dossier Photos ED (0 jeton OpenAI).

    - Masque temporairement le HUD d'Oscar s'il était affiché.
    - Détecte via Ollama si les commandes ATH (mode caméra) sont visibles ;
      si oui, désactive l'ATH via VoiceAttack et reprend la photo en résolution native.
    - Enregistre le PNG en résolution initiale, réaffiche le HUD d'Oscar si besoin,
      puis libère immédiatement la mémoire RAM et VRAM.
    """
    t0 = time.time()
    hud_etait_visible = bool(hud and hasattr(hud, "est_visible") and hud.est_visible())
    delai_hud = max(0.05, float(VISION_CONFIG.get("delai_masquage_hud_oscar", 0.15)))
    # La détection IA des commandes ATH n'est exécutée que si la vision Ollama est activée
    verifier_ath = bool(VISION_CONFIG.get("actif", False)) and bool(VISION_CONFIG.get("verifier_ath_photo", True))
    cmd_masquer_ath = str(VISION_CONFIG.get("commande_va_masquer_ath", "Désactiver ATH")).strip()
    delai_ath = max(0.2, float(VISION_CONFIG.get("delai_apres_masquage_ath", 3.5)))
    reactiver_ath = bool(VISION_CONFIG.get("reactiver_ath_apres_photo", True))

    img_native = None
    ath_masque = False
    avertissement_ollama = ""

    try:
        # 1. Masquage temporaire du HUD Oscar pour ne pas apparaître sur la photo
        if hud_etait_visible:
            hud.masquer()
            time.sleep(delai_hud)

        # 2. Première capture en résolution native complète
        img_native, meta = capturer_ecran_jeu()

        # 3. Détection locale des commandes ATH (mode caméra) via Ollama
        if verifier_ath:
            ath_present, info_ath = _detecter_ath_camera_visible(img_native)
            if ath_present is None:
                avertissement_ollama = info_ath
                print(f"[Vision/Photo] Vérification ATH ignorée ({info_ath}).")
            elif ath_present is True:
                print(f"[Vision/Photo] Commandes ATH détectées ({info_ath}) -> masquage ATH et nouvelle capture...")
                liberer_memoire_vision(img_native)
                img_native = None

                if _declencher_commande_va_ath(cmd_masquer_ath):
                    ath_masque = True
                    print(f"[Vision/Photo] Attente {delai_ath}s pour disparition complète du rappel IU...")
                    time.sleep(delai_ath)
                img_native, meta = capturer_ecran_jeu()

                if ath_masque and reactiver_ath:
                    _declencher_commande_va_ath("Activer ATH")

        # 4. Sauvegarde en résolution native initiale (PNG sans perte)
        chemin_photo = _generer_chemin_photo(DOSSIER_PHOTOS_ED)
        img_native.save(chemin_photo, format="PNG")
        resolution = f"{meta['largeur']}x{meta['hauteur']}"
        nom_fichier = os.path.basename(chemin_photo)
        duree = round(time.time() - t0, 2)
        print(f"[Vision/Photo] Photo enregistrée ({resolution}) en {duree}s : {chemin_photo}")

        if ath_masque and reactiver_ath:
            message_vocal = "Photo enregistrée. ATH rétabli."
        elif ath_masque:
            message_vocal = "ATH masqué. Photo enregistrée."
        elif avertissement_ollama:
            message_vocal = "Photo enregistrée. Vérification ATH ignorée car Ollama est hors ligne."
        else:
            message_vocal = "Photo enregistrée."

        return {
            "succes": True,
            "chemin": chemin_photo,
            "nom_fichier": nom_fichier,
            "resolution": resolution,
            "ath_masque": ath_masque,
            "avertissement_ollama": avertissement_ollama,
            "message_vocal": message_vocal,
            "duree_secondes": duree
        }
    except Exception as e:
        print(f"[Vision/Photo] Erreur lors de la prise de photo : {e}")
        return {
            "succes": False,
            "chemin": "",
            "nom_fichier": "",
            "resolution": "",
            "ath_masque": ath_masque,
            "avertissement_ollama": str(e),
            "message_vocal": "Impossible de prendre la photo, erreur de capture.",
            "duree_secondes": round(time.time() - t0, 2)
        }
    finally:
        # 5. Vidage immédiat de la mémoire (RAM + VRAM Ollama uniquement si utilisé)
        liberer_memoire_vision(img_native)
        if verifier_ath and obtenir_moteur_vision() == "ollama" and not avertissement_ollama:
            decharger_modele_ollama()

        # 6. Réaffichage du HUD d'Oscar uniquement s'il était visible avant la photo
        if hud_etait_visible:
            hud.afficher()


# ==============================================================================
# MODE TEST AUTONOME (py -m modules.vision_engine)
# ==============================================================================
if __name__ == "__main__":
    print("=== TEST AUTONOME DU MODULE VISION LOCALE OSCAR ===")
    ok_ollama, msg_ollama = verifier_ollama_disponible()
    print(f"[Ollama] Statut : {'OK' if ok_ollama else 'INDISPONIBLE'} ({msg_ollama})")
    print(f"[Config] Modèle : {VISION_CONFIG.get('modele')} | keep_alive : {VISION_CONFIG.get('keep_alive')}")
    print(f"[Config] Dossier photos : {DOSSIER_PHOTOS_ED}")

    # Test de détection vocale
    exemples = [
        "Regarde ! Qu'est-ce que tu vois ?",
        "Oscar, regarde ! Quelle est cette plante ?",
        "Regarde ! Combien on va mettre de temps pour atteindre notre cible ?",
        "Prendre une photo",
        "Oscar, prends une photo s'il te plaît",
        "C'est quoi ma flotte actuelle ?"
    ]
    for ex in exemples:
        v, q = detecter_commande_vision(ex)
        p = detecter_commande_photo(ex)
        print(f"  '{ex}' -> vision={v} (q='{q}') | photo={p}")

    if ok_ollama:
        print("\n[Test] Capture + analyse visuelle en cours...")
        res = analyser_ecran_pour_oscar("Décris brièvement ce qui est affiché à l'écran.")
        print(json.dumps(res, ensure_ascii=False, indent=2))
