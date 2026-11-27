"""Module HUD Overlay transparent pour Oscar (Copilote IA Elite Dangerous).

Fournit une fenêtre overlay Windows sans bordure, toujours au premier plan (topmost),
transparente aux clics hors barre de déplacement, avec :
- Fond translucide et typographie entièrement paramétrables via config_oscar.json
- Gabarit calibré 25 caractères x 10 lignes maximum
- Témoin/icône micro en haut à droite (rouge en écoute, vert au repos)
- Petite barre de déplacement affichée au survol souris (clic-glisser fluide)
- Effet légèrement couché / perspective 3D en mode cockpit (via Pillow si installé)
- Persistance et sauvegarde automatique de la position par vue Elite Dangerous
  (cockpit, carte_systeme, carte_galactique, a_pied)
- Formateurs factuels condensés (0 humour, 0 jeton) pour chaque mode d'Oscar
"""

import ctypes
from ctypes import wintypes
import json
import math
import os
import queue
import re
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
import unicodedata

from modules.config_loader import (
    FICHIER_POSITIONS_HUD,
    HUD_CONFIG
)

# Dépendance optionnelle Pillow pour l'effet perspective 3D en mode cockpit
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False

# ==============================================================================
# CONSTANTES WIN32 & VUES ELITE DANGEROUS
# ==============================================================================
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000

LWA_COLORKEY = 0x00000001
LWA_ALPHA = 0x00000002

HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020

# Couleur clé invisible utilisée pour découper le polygone 3D incliné
COULEUR_CLE_HEX = "#010203"
COULEUR_CLE_RGB = (1, 2, 3)
COULEUR_CLE_BGR = 0x00030201  # Format COLORREF Win32 (0x00BBGGRR)

VUE_COCKPIT = "cockpit"
VUE_CARTE_SYSTEME = "carte_systeme"
VUE_CARTE_GALACTIQUE = "carte_galactique"
VUE_A_PIED = "a_pied"

VUES_VALIDES = (VUE_COCKPIT, VUE_CARTE_SYSTEME, VUE_CARTE_GALACTIQUE, VUE_A_PIED)
LIBELLES_VUES = {
    VUE_COCKPIT: "COCKPIT",
    VUE_CARTE_SYSTEME: "SYSTEME",
    VUE_CARTE_GALACTIQUE: "GALAXIE",
    VUE_A_PIED: "A PIED"
}

# Abréviations compactes des modèles de vaisseaux pour l'affichage 25 car.
ABREV_VAISSEAUX = {
    "diamondback explorer": "DBX",
    "diamondback scout": "DBS",
    "type-6 transporter": "Type-6",
    "type-7 transporter": "Type-7",
    "type-8 transporter": "Type-8",
    "type-9 heavy": "Type-9",
    "type-10 defender": "Type-10",
    "imperial cutter": "Cutter",
    "imperial clipper": "Clipper",
    "imperial courier": "Courier",
    "imperial eagle": "Imp.Eagle",
    "federal corvette": "Corvette",
    "federal dropship": "Dropship",
    "federal assault ship": "FAS",
    "federal gunship": "Gunship",
    "alliance chieftain": "Chieftain",
    "alliance challenger": "Challenger",
    "alliance crusader": "Crusader",
    "krait mk ii": "Krait2",
    "krait phantom": "Phantom",
    "asp explorer": "AspX",
    "fer-de-lance": "FDL",
    "beluga liner": "Beluga",
    "caspian explorer": "Caspian",
    "python mk ii": "Python2",
    "cobra mk iii": "Cobra3",
    "cobra mk iv": "Cobra4",
    "cobra mk v": "Cobra5",
    "viper mk iii": "Viper3",
    "viper mk iv": "Viper4"
}


# ==============================================================================
# UTILITAIRES DE TEXTE, NORMALISATION ET DÉTECTION DES COMMANDES VOCALES HUD
# ==============================================================================
def _normaliser_simple(texte: str) -> str:
    """Normalise une chaîne (sans accents, minuscules, ponctuation nettoyée)."""
    if not texte:
        return ""
    sans_acc = "".join(
        c for c in unicodedata.normalize("NFD", str(texte))
        if unicodedata.category(c) != "Mn"
    )
    t = sans_acc.lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def detecter_commande_hud(texte: str, config_hud: dict = None) -> str | None:
    """Détecte une commande vocale d'affichage ou de masquage du HUD (0 jeton OpenAI).

    Retourne "AFFICHER", "MASQUER" ou None.
    """
    if not texte:
        return None
    cfg = config_hud or HUD_CONFIG
    t = _normaliser_simple(texte)

    # Tolérance aux variantes de transcription Whisper pour "HUD" uniquement
    # (Le mot "ATH" est réservé aux commandes VoiceAttack 'Activer ATH' / 'Désactiver ATH' du jeu)
    t_canon = re.sub(r"\bh\s+u\s+d\b", "hud", t)
    t_canon = re.sub(r"\b(?:eud|ude|hude|heud|hu\s+de|eude|aude)\b", "hud", t_canon)

    cmds_aff = {_normaliser_simple(c) for c in cfg.get("commandes_afficher", [])}
    cmds_masq = {_normaliser_simple(c) for c in cfg.get("commandes_masquer", [])}

    if t_canon in cmds_aff or t in cmds_aff:
        return "AFFICHER"
    if t_canon in cmds_masq or t in cmds_masq:
        return "MASQUER"

    # Détection par motif souple réservée à "HUD" (jamais "ATH" pour ne pas bloquer l'ATH du jeu)
    if re.search(r"\b(?:affiche[rz]?|ouvre[rz]?|montre[rz]?|active[rz]?|remet[sz]?|allume[rz]?)\s+(?:ton|le|l|mon)?\s*hud\b", t_canon):
        return "AFFICHER"
    if re.search(r"\b(?:efface[rz]?|supprime[rz]?|enleve[rz]?|masque[rz]?|cache[rz]?|retire[rz]?|ferme[rz]?|desactive[rz]?|etein[ds]?)\s+(?:ton|le|l|mon)?\s*hud\b", t_canon):
        return "MASQUER"

    return None


def _tronquer(texte: str, max_len: int) -> str:
    """Tronque proprement une chaîne si elle dépasse max_len caractères."""
    s = str(texte or "").strip()
    if len(s) <= max_len:
        return s
    if max_len <= 1:
        return s[:max_len]
    return s[:max_len - 1].rstrip() + "."


def envelopper_lignes(texte: str, largeur: int = 25) -> list[str]:
    """Découpe un texte en lignes d'au plus `largeur` caractères en préservant les mots."""
    if not texte:
        return []
    lignes_sortie = []
    for paragraphe in str(texte).splitlines():
        p = paragraphe.rstrip()
        if not p:
            lignes_sortie.append("")
            continue
        while len(p) > largeur:
            # Cherche le dernier espace dans la fenêtre [0..largeur]
            coupe = p.rfind(" ", 0, largeur + 1)
            if coupe <= 0:
                # Mot trop long sans espace : découpe nette à `largeur`
                lignes_sortie.append(p[:largeur])
                p = p[largeur:]
            else:
                lignes_sortie.append(p[:coupe].rstrip())
                p = p[coupe + 1:].lstrip()
        if p:
            lignes_sortie.append(p)
    return lignes_sortie


def formater_bloc_lignes(lignes: list[str], largeur: int = 25, max_lignes: int = 10) -> list[str]:
    """Enveloppe une liste de lignes brutes dans le gabarit `largeur` x `max_lignes`."""
    resultat = []
    for ligne in lignes:
        if ligne is None:
            continue
        sous_lignes = envelopper_lignes(str(ligne), largeur)
        if not sous_lignes:
            resultat.append("")
        else:
            resultat.extend(sous_lignes)
        if len(resultat) >= max_lignes:
            break
    return resultat[:max_lignes]


def paginer_dictee(texte_complet: str, largeur: int = 25, max_lignes: int = 10) -> list[str]:
    """Enveloppe le texte dicté et renvoie la page courante (max 10 lignes).

    Si le texte dépasse 10 lignes, efface la page précédente et reprend à la ligne 1.
    """
    if not texte_complet:
        return []
    toutes = envelopper_lignes(texte_complet, largeur)
    if not toutes:
        return []
    index_page = (len(toutes) - 1) // max_lignes
    debut = index_page * max_lignes
    return toutes[debut:debut + max_lignes]


def formater_epellation(buffer_texte: str, largeur: int = 25, max_lignes: int = 10) -> list[str]:
    """Formate le texte épelé directement dès la ligne 1 (comme dans un champ texte)."""
    if not buffer_texte:
        return []
    lignes = [buffer_texte[i:i + largeur] for i in range(0, len(buffer_texte), largeur)]
    if len(lignes) > max_lignes:
        lignes = lignes[-max_lignes:]
    return lignes


def _abreger_modele(modele: str) -> str:
    """Raccourcit un nom de modèle de vaisseau pour gagner de la place sur 25 car."""
    if not modele:
        return "?"
    cle = str(modele).lower().strip()
    return ABREV_VAISSEAUX.get(cle, modele)


def _formater_prix_kcr(prix_credits) -> str:
    """Convertit un prix unitaire en crédits vers un format lisible en Kcr."""
    try:
        val = float(prix_credits)
    except (TypeError, ValueError):
        return "N/C"
    kcr = val / 1000.0
    if kcr >= 100:
        return f"{kcr:,.1f} Kcr".replace(",", " ").replace(".0 ", " ")
    if kcr >= 1:
        txt = f"{kcr:.2f}".rstrip("0").rstrip(".")
        return f"{txt} Kcr"
    txt = f"{kcr:.3f}".rstrip("0").rstrip(".")
    return f"{txt} Kcr"


def _formater_entier_espaces(nombre) -> str:
    """Formate un entier avec séparateurs d'espaces (ex: 12500 -> '12 500')."""
    try:
        return f"{int(round(float(nombre))):,}".replace(",", " ")
    except (TypeError, ValueError):
        return str(nombre)


# ==============================================================================
# FORMATEURS FACTUELS CONDENSÉS POUR CHAQUE MODE D'OSCAR
# ==============================================================================
def formater_commande_vaisseau(nom_commande: str, largeur: int = 25, max_lignes: int = 10) -> list[str]:
    """Formate l'affichage d'une commande vaisseau [EXECUTE:commande]."""
    lignes = [
        "[EXECUTE]",
        str(nom_commande or "").strip()
    ]
    return formater_bloc_lignes(lignes, largeur, max_lignes)


def formater_commerce_spansh(donnees: dict, largeur: int = 25, max_lignes: int = 10) -> list[str]:
    """Synthèse Spansh : Système, Station, Distance, Volume, Prix en Kcr (1 info/ligne)."""
    if not isinstance(donnees, dict):
        return formater_bloc_lignes(["== COMMERCE ==", str(donnees)], largeur, max_lignes)
    if "erreur" in donnees:
        return formater_bloc_lignes(["== COMMERCE (ERR) ==", donnees["erreur"]], largeur, max_lignes)

    mode = str(donnees.get("mode", "vendre")).lower()
    objet = donnees.get("recherche", "")

    if mode == "module":
        titre = "== EQUIPEMENT =="
    elif mode == "acheter":
        titre = "== COMMERCE (ACHAT) =="
    else:
        titre = "== COMMERCE (VENTE) =="

    if "info" in donnees:
        if objet:
            rayon = donnees.get("rayon_recherche_al")
            ref = donnees.get("systeme_reference")
            pad = donnees.get("pad_requis")
            lignes_vide = [titre, f"Objet: {objet}"]
            if pad:
                lignes_vide.append(f"Pad: {pad}")
            if ref:
                lignes_vide.append(f"Ref: {ref}")
            if rayon is not None:
                lignes_vide.append(f"Rayon: {int(round(float(rayon)))} AL")
            lignes_vide.append("Resultat: Aucune station")
            return formater_bloc_lignes(lignes_vide, largeur, max_lignes)
        return formater_bloc_lignes([titre, donnees["info"]], largeur, max_lignes)

    stations = donnees.get("meilleures_stations", [])
    if not stations:
        return formater_bloc_lignes([titre, "Resultat: Aucune station"], largeur, max_lignes)

    st = stations[0]
    dist_al = st.get("distance_annees_lumiere", "?")
    sauts = st.get("sauts_approximatifs")
    txt_dist = f"Dist: {dist_al} AL"
    if sauts is not None:
        unite_s = "saut" if sauts == 1 else "sauts"
        txt_dist = f"Dist: {dist_al} AL ({sauts} {unite_s})"

    lignes = [
        titre,
        f"Objet: {objet}",
        f"Sys: {st.get('systeme', '?')}",
        f"Stn: {st.get('station', '?')}",
        txt_dist
    ]

    if mode != "module":
        qte = st.get("quantite_tonnes")
        prix = st.get("prix_par_tonne_credits")
        tag_vol = "stock" if mode == "acheter" else "demande"
        vol_str = f"{_formater_entier_espaces(qte)} t ({tag_vol})" if qte is not None else "N/C"
        prix_str = _formater_prix_kcr(prix) if prix is not None else "N/C"
        lignes.append(f"Vol: {vol_str}")
        lignes.append(f"Prix: {prix_str}")
    else:
        sl = st.get("distance_etoile_secondes_lumiere")
        pad = st.get("pad_compatible", "?")
        lignes.append(f"Pad: {pad}")
        if sl is not None:
            lignes.append(f"Etoile: {_formater_entier_espaces(sl)} SL")

    return formater_bloc_lignes(lignes, largeur, max_lignes)


def formater_destination(donnees: dict, largeur: int = 25, max_lignes: int = 10) -> list[str]:
    """Synthèse Destination : Départ, Arrivée, Distance AL, Nombre de sauts estimé."""
    if not isinstance(donnees, dict):
        return formater_bloc_lignes(["DESTINATION", str(donnees)], largeur, max_lignes)
    if "erreur" in donnees:
        return formater_bloc_lignes(["DESTINATION - ERREUR", donnees["erreur"]], largeur, max_lignes)

    dep = donnees.get("depart", "?")
    arr = donnees.get("arrivee", "?")
    dist = donnees.get("distance_annees_lumiere", "?")
    sauts = donnees.get("sauts_estimes")

    lignes = [
        "DESTINATION",
        f"Dep: {dep}",
        f"Arr: {arr}",
        f"Dist: {dist} AL",
        f"Sauts estimes: {sauts}" if sauts is not None else "Sauts estimes: N/C"
    ]
    return formater_bloc_lignes(lignes, largeur, max_lignes)


def formater_systemes_proches(donnees, systeme_ref: str = "", largeur: int = 25, max_lignes: int = 10) -> list[str]:
    """Synthèse compacte des systèmes stellaires proches (EDSM)."""
    if isinstance(donnees, dict):
        msg = donnees.get("erreur") or donnees.get("info") or "Aucun resultat."
        return formater_bloc_lignes(["SYSTEMES PROCHES", msg], largeur, max_lignes)
    if not isinstance(donnees, list) or not donnees:
        return formater_bloc_lignes(["SYSTEMES PROCHES", "Aucun systeme trouve."], largeur, max_lignes)

    lignes = [f"PROCHES: {systeme_ref}" if systeme_ref else "SYSTEMES PROCHES"]
    for s in donnees[:max_lignes - 1]:
        nom = s.get("nom", "?")
        dist = s.get("distance_annees_lumiere", "?")
        suffixe = f" {dist}AL"
        nom_court = _tronquer(nom, max(6, largeur - len(suffixe)))
        lignes.append(f"{nom_court}{suffixe}")
    return formater_bloc_lignes(lignes, largeur, max_lignes)


def formater_stations_systeme(donnees: dict, largeur: int = 25, max_lignes: int = 10) -> list[str]:
    """Synthèse compacte des stations d'un système (EDSM)."""
    if not isinstance(donnees, dict):
        return formater_bloc_lignes(["STATIONS", str(donnees)], largeur, max_lignes)
    if "erreur" in donnees or "info" in donnees:
        return formater_bloc_lignes(["STATIONS", donnees.get("erreur") or donnees.get("info")], largeur, max_lignes)

    sys_nom = donnees.get("systeme", "")
    stations = donnees.get("stations", [])
    lignes = [f"STATIONS: {sys_nom}" if sys_nom else "STATIONS"]
    for st in stations[:max_lignes - 1]:
        nom = st.get("nom", "?")
        sl = st.get("distance_secondes_lumiere")
        suffixe = f" {int(round(sl))}SL" if isinstance(sl, (int, float)) else ""
        nom_court = _tronquer(nom, max(6, largeur - len(suffixe)))
        lignes.append(f"{nom_court}{suffixe}")
    return formater_bloc_lignes(lignes, largeur, max_lignes)


def formater_alerte_proactive(cle_alerte: str, detail: str = "", largeur: int = 25, max_lignes: int = 10) -> list[str]:
    """Condensé factuel d'une alerte autonome (sans blabla)."""
    cle = str(cle_alerte or "").lower()
    if cle == "bouclier_tombe":
        lignes = ["ALERTE: BOUCLIERS", "Boucliers hors ligne !", "Coque exposee."]
    elif cle == "surchauffe":
        lignes = ["ALERTE: SURCHAUFFE", "Temperature critique !", "Dissipateur conseille."]
    elif cle == "carburant_bas":
        lignes = ["ALERTE: CARBURANT BAS", "Reservoir critique !"]
    elif cle == "interdiction":
        lignes = ["ALERTE: INTERDICTION", "Aligner le vecteur !"]
    elif cle == "danger":
        lignes = ["ALERTE: COMBAT", "Sous le feu ennemi !"]
    elif cle == "coque":
        lignes = ["ALERTE: COQUE", detail or "Degats coque detectes !"]
    elif cle == "oxygene_critique":
        lignes = ["ALERTE: OXYGENE !", detail or "Oxygene critique !", "Retour VRS / Vaisseau !"]
    elif cle == "oxygene_bas":
        lignes = ["ALERTE: OXYGENE BAS", detail or "Oxygene combinaison bas."]
    elif cle == "sante_basse":
        lignes = ["ALERTE: SANTE BASSE", detail or "Sante critique a pied !"]
    elif cle.startswith("mod_") or cle == "module":
        lignes = ["ALERTE: MODULE", detail or "Module endommage !"]
    elif cle == "retour_maison":
        lignes = ["RETOUR MAISON"] + [x for x in str(detail or "").splitlines() if x.strip()]
    elif cle == "nouveau_systeme":
        lignes = ["NOUVEAU SYSTEME"] + [x for x in str(detail or "").splitlines() if x.strip()]
    elif cle == "honk_systeme":
        lignes = ["HONK SYSTEME"] + [x for x in str(detail or "").splitlines() if x.strip()]
    else:
        lignes = ["ALERTE SYSTEME", detail or cle_alerte]
    return formater_bloc_lignes(lignes, largeur, max_lignes)


def formater_flotte(donnees: dict, question_pilote: str = "", largeur: int = 25, max_lignes: int = 10) -> list[str]:
    """Condensé factuel de la flotte ou fiche d'un vaisseau spécifique demandé."""
    if not isinstance(donnees, dict):
        return formater_bloc_lignes(["FLOTTE", str(donnees)], largeur, max_lignes)

    v_actif = donnees.get("vaisseau_actuel_pilote", {}) or {}
    stockes = donnees.get("vaisseaux_stockes_en_station", []) or []
    total = donnees.get("nombre_total_vaisseaux", 1 + len(stockes))

    q = _normaliser_simple(question_pilote)

    # Recherche si la question vise un vaisseau précis de la flotte
    tous_vaisseaux = []
    if v_actif:
        tous_vaisseaux.append({
            "nom": v_actif.get("nom") or v_actif.get("modele", "?"),
            "modele": v_actif.get("modele", "?"),
            "systeme": v_actif.get("systeme_actuel", "?"),
            "station": v_actif.get("station_ou_position_actuelle", "?"),
            "statut": "ACTIF (pilote)"
        })
    for v in stockes:
        tous_vaisseaux.append({
            "nom": v.get("nom") or v.get("modele", "?"),
            "modele": v.get("modele", "?"),
            "systeme": v.get("systeme", "?"),
            "station": v.get("station", "?"),
            "statut": "EN TRANSIT" if v.get("en_transit") else "Stocke"
        })

    if q and not any(m in q for m in ("toute", "tous", "liste", "inventaire", "combien", "flotte")):
        correspondances = []
        for v in tous_vaisseaux:
            nom_n = _normaliser_simple(v["nom"])
            mod_n = _normaliser_simple(v["modele"])
            abrev_n = _normaliser_simple(_abreger_modele(v["modele"]))
            if (nom_n and len(nom_n) >= 3 and nom_n in q) or (mod_n and len(mod_n) >= 3 and mod_n in q) or (abrev_n and len(abrev_n) >= 3 and abrev_n in q):
                correspondances.append(v)
        if len(correspondances) == 1:
            v = correspondances[0]
            lignes = [
                f"FLOTTE: {v['nom']}",
                f"Mod: {v['modele']}",
                f"Sys: {v['systeme']}",
                f"Stn: {v['station']}",
                f"Etat: {v['statut']}"
            ]
            return formater_bloc_lignes(lignes, largeur, max_lignes)

    # Déduplication si le vaisseau actif apparaît encore dans le cache des vaisseaux stockés
    nom_actif_norm = _normaliser_simple(v_actif.get("nom", ""))
    mod_actif_norm = _normaliser_simple(v_actif.get("modele", ""))
    stockes_filtres = [
        v for v in stockes
        if not (
            nom_actif_norm
            and _normaliser_simple(v.get("nom", "")) == nom_actif_norm
            and _normaliser_simple(v.get("modele", "")) == mod_actif_norm
        )
    ]

    # Vue globale condensée de la flotte (calibrée 10 lignes max)
    total_effectif = (1 if v_actif else 0) + len(stockes_filtres)
    lignes = [f"FLOTTE ({total_effectif} vaisseaux)"]
    if v_actif:
        nom_a = v_actif.get("nom") or v_actif.get("modele", "?")
        mod_a = _abreger_modele(v_actif.get("modele", ""))
        lignes.append(_tronquer(f"*{nom_a} ({mod_a})", largeur))
        lignes.append(_tronquer(f" @{v_actif.get('systeme_actuel', '?')}", largeur))

    places_restantes = max_lignes - len(lignes)
    if len(stockes_filtres) > places_restantes:
        a_afficher = stockes_filtres[:max(0, places_restantes - 1)]
        restants = len(stockes_filtres) - len(a_afficher)
    else:
        a_afficher = stockes_filtres
        restants = 0

    for v in a_afficher:
        nom = v.get("nom") or v.get("modele", "?")
        mod = _abreger_modele(v.get("modele", ""))
        sys_v = v.get("systeme", "")
        sys_actif = v_actif.get("systeme_actuel", "")
        # Si garé dans un autre système que le vaisseau actif, on indique le système
        if sys_v and sys_v != sys_actif:
            entree = f"-{nom} @{sys_v}"
        else:
            entree = f"-{nom} ({mod})"
        lignes.append(_tronquer(entree, largeur))

    if restants > 0:
        lignes.append(f"+{restants} autre(s) vaisseau(x)")

    return formater_bloc_lignes(lignes, largeur, max_lignes)


def formater_telemetrie(nom_outil: str, donnees: dict, question_pilote: str = "", largeur: int = 25, max_lignes: int = 10) -> list[str]:
    """Extrait un condensé 100% factuel de la télémétrie/état selon la question posée."""
    if not isinstance(donnees, dict):
        return formater_bloc_lignes(["TELEMETRIE", str(donnees)], largeur, max_lignes)
    if "erreur" in donnees:
        return formater_bloc_lignes(["TELEMETRIE - ERREUR", donnees["erreur"]], largeur, max_lignes)

    q = _normaliser_simple(question_pilote)

    # 1. Configuration d'un vaisseau spécifique
    if nom_outil == "obtenir_configuration_vaisseau":
        if "info" in donnees:
            return formater_bloc_lignes(["CONFIG VAISSEAU", donnees["info"]], largeur, max_lignes)
        nom = donnees.get("nom", "?")
        mod = donnees.get("modele", "?")
        ident = donnees.get("identifiant", "")
        saut = donnees.get("portee_saut_max", "?")
        soute = donnees.get("capacite_soute_tonnes", 0)
        mods = donnees.get("modules", [])
        lignes = [
            f"CONFIG: {nom}",
            f"Mod: {mod}",
            f"Saut max: {saut} AL",
            f"Soute: {soute} t"
        ]
        if ident:
            lignes.insert(2, f"ID: {ident}")
        lignes.append(f"Modules: {len(mods)}")
        return formater_bloc_lignes(lignes, largeur, max_lignes)

    # 2. Télémétrie temps réel (Status.json + Cargo.json + ModulesInfo.json)
    if nom_outil == "obtenir_telemetrie_temps_reel":
        soute = donnees.get("soute", {}) or {}
        sys_etat = donnees.get("etat_systemes", {}) or {}
        mods = donnees.get("modules", {}) or {}

        # Formatage compact du nom du vaisseau pour éviter les troncatures
        vaiss_brut = str(donnees.get("vaisseau", "")).strip()
        m_v = re.match(r"^(.*?)\s*\(([^)]+)\)$", vaiss_brut)
        vaiss_court = f"{m_v.group(1)} ({_abreger_modele(m_v.group(2))})" if m_v else vaiss_brut

        # Question ciblée : modules / santé / dégâts / actifs (TESTÉ AVANT carburant pour 'récupérateur de carburant' !)
        if any(m in q for m in ("module", "recuperateur", "scoop", "sante", "degat", "endommage", "inactif", "actif", "desactive", "allume", "eteint", "repar", "panne", "afmu")):
            inactifs = mods.get("modules_inactifs", [])
            endom = mods.get("modules_endommages_sous_50_pourcent", [])
            tous_mods = mods.get("tous_les_modules", [])

            # Vérifie si un module spécifique est mentionné dans la question
            cibles_modules = [
                ("recuperateur", "Récupérateur de carburant"),
                ("scoop", "Récupérateur de carburant"),
                ("bouclier", "Générateur de bouclier"),
                ("fsd", "Réacteur FSD"),
                ("booster", "Accélérateur FSD Guardian"),
                ("afmu", "Unité de maintenance"),
                ("maintenance", "Unité de maintenance"),
                ("propulseur", "Propulseurs"),
                ("survie", "Système de survie"),
                ("capteur", "Capteurs"),
                ("raffinerie", "Raffinerie"),
                ("appontage", "Ordinateur d'appontage"),
                ("super navigation", "Assistance de super-navigation"),
                ("vrs", "hangar à VRS"),
                ("dissipateur", "dissipateurs thermiques"),
            ]
            mod_trouve = None
            for mot_q, nom_m in cibles_modules:
                if mot_q in q:
                    for entree in tous_mods:
                        if _normaliser_simple(nom_m) in _normaliser_simple(entree):
                            mod_trouve = entree
                            break
                    if mod_trouve:
                        break

            if mod_trouve:
                nom_part, _, detail_part = mod_trouve.partition(" : ")
                nom_sans_slot = re.sub(r"\s*\([^)]*\)$", "", nom_part).strip()
                lignes = ["TELEMETRIE: MODULE", nom_sans_slot]
                for morceau in detail_part.split(", "):
                    if morceau.strip():
                        lignes.append(morceau.strip())
                return formater_bloc_lignes(lignes, largeur, max_lignes)

            lignes = [
                "TELEMETRIE: MODULES",
                f"Inactifs (Loadout): {len(inactifs)}",
                f"Endommages <50%: {len(endom)}"
            ]
            for item in endom[:3]:
                lignes.append(f"!{item}")
            for item in inactifs[:3]:
                lignes.append(f"-OFF: {item}")
            if not endom and not inactifs:
                lignes.append("Tous nominaux (Loadout)")
            return formater_bloc_lignes(lignes, largeur, max_lignes)

        # Question ciblée : carburant
        if any(m in q for m in ("carburant", "essence", "fuel", "reservoir", "plein")):
            carb_txt = str(donnees.get("carburant", "Inconnu"))
            m_carb = re.search(r"([\d.]+)\s*tonnes.*r[ée]serve\s*:\s*([\d.]+)", carb_txt, re.IGNORECASE)
            lignes = ["TELEMETRIE: CARBURANT", _tronquer(vaiss_court, largeur)]
            if m_carb:
                lignes.append(f"Principal: {m_carb.group(1)} t")
                lignes.append(f"Reserve: {m_carb.group(2)} t")
            else:
                lignes.append(carb_txt)
            if sys_etat.get("carburant_bas"):
                lignes.append("ALERTE: NIVEAU BAS !")
            return formater_bloc_lignes(lignes, largeur, max_lignes)

        # Question ciblée : soute / cargaison
        if any(m in q for m in ("soute", "cargaison", "cargo", "place", "tonnes", "transporte")):
            cap = soute.get("capacite_totale_tonnes", 0)
            util = soute.get("utilisee_tonnes", 0)
            lib = soute.get("place_libre_tonnes", "?")
            lignes = [
                "TELEMETRIE: SOUTE",
                f"Utilise: {util} / {cap} t",
                f"Libre: {lib} t"
            ]
            contenu = soute.get("contenu", [])
            if contenu:
                for item in contenu[:max_lignes - 3]:
                    lignes.append(f"-{item}")
            else:
                lignes.append("Soute vide.")
            return formater_bloc_lignes(lignes, largeur, max_lignes)

        # Question ciblée : boucliers / énergie / pips / altitude / destination
        if any(m in q for m in ("pip", "energie", "puissance", "bouclier", "altitude", "destination", "cible")):
            lignes = ["TELEMETRIE: SYSTEMES"]
            if "boucliers_actifs" in sys_etat:
                lignes.append(f"Boucliers: {'ON' if sys_etat['boucliers_actifs'] else 'OFF'}")
            if donnees.get("repartition_energie_pips"):
                lignes.append(donnees["repartition_energie_pips"])
            if "altitude_surface_metres" in donnees:
                lignes.append(f"Altitude: {donnees['altitude_surface_metres']} m")
            if donnees.get("destination_verrouillee"):
                lignes.append(f"Dest: {donnees['destination_verrouillee']}")
            return formater_bloc_lignes(lignes, largeur, max_lignes)

        # Tableau de bord général temps réel
        carb_court = str(donnees.get("carburant", "?"))
        m_c = re.search(r"([\d.]+)\s*tonnes", carb_court)
        if m_c:
            carb_court = f"{m_c.group(1)} t"
        cap = soute.get("capacite_totale_tonnes", 0)
        util = soute.get("utilisee_tonnes", 0)
        bcl = "ON" if sys_etat.get("boucliers_actifs") else "OFF"
        lignes = [
            "TELEMETRIE",
            _tronquer(vaiss_court, largeur),
            f"Sys: {donnees.get('systeme', '?')}",
            f"Carb: {carb_court}",
            f"Soute: {util}/{cap} t",
            f"Boucliers: {bcl}"
        ]
        if donnees.get("destination_verrouillee") and donnees["destination_verrouillee"] != "Aucune":
            lignes.append(f"Dest: {donnees['destination_verrouillee']}")
        if mods.get("modules_endommages_sous_50_pourcent"):
            lignes.append(f"Mod <50%: {len(mods['modules_endommages_sous_50_pourcent'])}")
        return formater_bloc_lignes(lignes, largeur, max_lignes)

    # 3. État vaisseau et ressources (Crédits, Rangs, Position, Matériaux)
    if nom_outil == "obtenir_etat_vaisseau_et_ressources":
        # Crédits
        if any(m in q for m in ("credit", "argent", "solde", "fortune", "riche", "compte", "banque")):
            cr = donnees.get("credits", "Inconnus")
            lignes = ["ETAT: CREDITS"]
            if isinstance(cr, (int, float)):
                lignes.append(f"{_formater_entier_espaces(cr)} cr")
                if cr >= 1_000_000_000:
                    lignes.append(f"({cr / 1_000_000_000:.2f} Gcr)")
                elif cr >= 1_000_000:
                    lignes.append(f"({cr / 1_000_000:.1f} Mcr)")
            else:
                lignes.append(str(cr))
            return formater_bloc_lignes(lignes, largeur, max_lignes)

        # Rangs
        if any(m in q for m in ("rang", "grade", "reputation", "combat", "commerce", "exploration", "empire", "federation", "exobiolog")):
            rangs = donnees.get("rangs", {}) or {}
            lignes = ["RANGS COMMANDANT"]
            trad_dom = {
                "Combat": "Comb", "Trade": "Comm", "Explore": "Expl",
                "Soldier": "Merc", "Exobiologist": "Exob",
                "Empire": "Emp", "Federation": "Fed"
            }
            for dom, val in rangs.items():
                lignes.append(f"{trad_dom.get(dom, dom)}: {val}")
            if len(lignes) == 1:
                lignes.append("Non disponibles.")
            return formater_bloc_lignes(lignes, largeur, max_lignes)

        # Matériaux
        mats = donnees.get("materiaux")
        if isinstance(mats, list) or isinstance(mats, str) or any(m in q for m in ("materiau", "materiaux", "composant", "element", "stock")):
            lignes = ["MATERIAUX"]
            if isinstance(mats, str):
                lignes.append(mats)
            elif isinstance(mats, list):
                for item in mats[:max_lignes - 1]:
                    lignes.append(f"-{item}")
            elif isinstance(mats, dict):
                lignes.append(f"Bruts (Raw): {len(mats.get('Raw', []))}")
                lignes.append(f"Fabriques: {len(mats.get('Manufactured', []))}")
                lignes.append(f"Encodes: {len(mats.get('Encoded', []))}")
            return formater_bloc_lignes(lignes, largeur, max_lignes)

        # Position / résumé général
        v = donnees.get("vaisseau_actif", {}) or {}
        nom_v = v.get("nom") or v.get("modele", "?")
        cr = donnees.get("credits", "?")
        cr_str = f"{cr / 1_000_000:.1f} Mcr" if isinstance(cr, (int, float)) and cr >= 1_000_000 else str(cr)
        lignes = [
            "POSITION & ETAT",
            f"Sys: {donnees.get('systeme', '?')}",
            f"Corps: {donnees.get('corps_celeste', '?')}",
            f"Stn: {donnees.get('station_ou_base', '?')}",
            f"Vaiss: {nom_v}",
            f"Credits: {cr_str}"
        ]
        return formater_bloc_lignes(lignes, largeur, max_lignes)

    return formater_bloc_lignes(["INFO", str(donnees)], largeur, max_lignes)


def formater_resultat_outil_hud(
    nom_outil: str,
    args: dict,
    donnees,
    question_pilote: str = "",
    largeur: int = 25,
    max_lignes: int = 10
) -> list[str] | None:
    """Aiguille le résultat brut d'un outil OpenAI vers son formateur HUD condensé."""
    if nom_outil == "rechercher_commerce_ou_equipement":
        return formater_commerce_spansh(donnees, largeur, max_lignes)
    if nom_outil == "calculer_distance_entre_systemes":
        return formater_destination(donnees, largeur, max_lignes)
    if nom_outil == "chercher_systemes_proches":
        return formater_systemes_proches(donnees, (args or {}).get("systeme", ""), largeur, max_lignes)
    if nom_outil == "chercher_stations_systeme":
        return formater_stations_systeme(donnees, largeur, max_lignes)
    if nom_outil == "obtenir_ma_flotte":
        return formater_flotte(donnees, question_pilote, largeur, max_lignes)
    if nom_outil in (
        "obtenir_telemetrie_temps_reel",
        "obtenir_etat_vaisseau_et_ressources",
        "obtenir_configuration_vaisseau"
    ):
        return formater_telemetrie(nom_outil, donnees, question_pilote, largeur, max_lignes)
    if nom_outil == "analyser_systeme_fss":
        return formater_analyse_fss(donnees, largeur, max_lignes)
    if nom_outil == "obtenir_portefeuille_exploration":
        return formater_portefeuille_exploration(donnees, largeur, max_lignes)
    return None


def formater_portefeuille_exploration(donnees: dict, largeur: int = 25, max_lignes: int = 10) -> list[str]:
    """Formate le portefeuille de données d'exploration non vendues pour le HUD."""
    if not isinstance(donnees, dict) or "erreur" in donnees:
        return formater_bloc_lignes(["PORTEFEUILLE EXPLO", str(donnees)], largeur, max_lignes)

    uc = donnees.get("cartographie_universal_cartographics", {})
    vg = donnees.get("exobiologie_vista_genomics", {})
    cx = donnees.get("bons_codex", {})

    lignes = [
        "PORTEFEUILLE A BORD",
        f"TOTAL: {donnees.get('total_general_texte', '0 Cr')}",
        f"Carto: {uc.get('texte', '0 Cr')} ({uc.get('nb_systemes', 0)} sys)",
        f"Exobio: {vg.get('texte', '0 Cr')} ({vg.get('nb_especes_pretes', 0)} esp)"
    ]
    if vg.get("nb_especes_en_cours", 0) > 0:
        lignes.append(f"En cours: {vg['nb_especes_en_cours']} prelev.")
    if cx.get("total_credits", 0) > 0:
        lignes.append(f"Codex: {cx.get('texte', '0 Cr')} ({cx.get('nb_entrees', 0)})")
    else:
        lignes.append("Codex: 0 Cr")
    return formater_bloc_lignes(lignes, largeur, max_lignes)


ABREV_MATERIAUX_HUD = {
    "selenium": "Sel.",
    "polonium": "Polo",
    "technetium": "Tech",
    "ruthenium": "Ruth",
    "tellure": "Tell",
    "yttrium": "Yttr",
    "antimoine": "Anti"
}


def _abreger_materiau_hud(nom: str) -> str:
    """Raccourcit un nom de matériau pour tenir proprement sur une ligne HUD 25 car."""
    cle = _normaliser_simple(nom)
    return ABREV_MATERIAUX_HUD.get(cle, _tronquer(nom, 5))


def _formater_corps_hud(nom_court: str) -> str:
    """Préfixe clairement un nom court de planète/lune (ex: '1' -> 'P.1', '8 A' -> 'P.8 A')."""
    s = str(nom_court or "?").strip().upper()
    if s.startswith("P."):
        return s
    return f"P.{s}"


def formater_analyse_fss(donnees: dict, largeur: int = 25, max_lignes: int = 10) -> list[str]:
    """Formate les priorités DSS / Exobio / Matériaux / Anneaux du système après FSS (aligné Navigation)."""
    if not isinstance(donnees, dict):
        return formater_bloc_lignes(["ANALYSE FSS", "Aucune donnee"], largeur, max_lignes)
    if donnees.get("erreur") or donnees.get("info"):
        return formater_bloc_lignes(["ANALYSE FSS", donnees.get("erreur") or donnees.get("info")], largeur, max_lignes)

    nb_plan = donnees.get("nb_planetes_scannees_fss", 0)
    bilan = donnees.get("bilan_financier") or {}
    acq_court = str(bilan.get("deja_acquis_carto_texte") or "").replace(" Cr", "").replace(" ", "")
    if acq_court:
        entete = _tronquer(f"FSS: {nb_plan} plan. | Acq {acq_court}", largeur)
    else:
        entete = f"FSS: {nb_plan} planetes"
    lignes = [entete]
    if bilan.get("gain_dss_recommandes_credits", 0) > 0:
        gain_txt = str(bilan.get("gain_dss_recommandes_texte") or "").replace(" Cr", "")
        lignes.append(_tronquer(f"Gain DSS: {gain_txt}", largeur))

    objectif = donnees.get("objectif", "tout")
    carto = donnees.get("cibles_dss_cartographie", [])
    bio = donnees.get("cibles_exobiologie", [])
    mats = donnees.get("cibles_materiaux_surface", [])
    anneaux = donnees.get("anneaux_minables", [])

    if objectif in ("tout", "dss") and carto:
        lignes.append("DSS CARTO:")
        for c in carto[:2]:
            etat = "OK" if c.get("deja_scannee_dss_par_moi") else "DSS"
            corps = _formater_corps_hud(c.get("planete"))
            dist = int(round(float(c.get("distance_sl", 0) or 0)))
            val = str(c.get("valeur_dss_texte") or "").replace(" Cr", "").replace(" ", "")
            lignes.append(_tronquer(f" {corps} {dist}SL {val} {etat}", largeur))

    if objectif in ("tout", "biologie") and bio:
        toutes_x5 = all(b.get("premiere_empreinte_x5_possible") for b in bio[:3])
        lignes.append("EXOBIO (x5):" if toutes_x5 else "EXOBIO:")
        for b in bio[:3]:
            corps = _formater_corps_hud(b.get("planete"))
            dist = int(round(float(b.get("distance_sl", 0) or 0)))
            nb_b = b.get("signaux_biologiques", 1)
            fourchette = b.get("fourchette_hud") or str(b.get("potentiel_max_texte") or "").replace(" Cr", "").replace(" ", "")
            tag_x5 = "" if toutes_x5 else ("*" if b.get("premiere_empreinte_x5_possible") else "")
            lignes.append(_tronquer(f" {corps} {dist}SL {nb_b}b {fourchette}{tag_x5}", largeur))

    if objectif in ("tout", "materiaux") and mats:
        mat_q = donnees.get("materiau_recherche")
        lignes.append(_tronquer(f"MAT: {mat_q}", largeur) if mat_q else "MAT. RARES:")
        for m in mats[:2]:
            corps = _formater_corps_hud(m.get("planete"))
            dist = int(round(float(m.get("distance_sl", 0) or 0)))
            if mat_q and "pourcentage" in m:
                lignes.append(_tronquer(f" {corps} {m['pourcentage']}% {dist}SL", largeur))
            elif m.get("meilleur_nom") and "meilleur_pct" in m:
                abrev = _abreger_materiau_hud(m["meilleur_nom"])
                pct = f"{float(m['meilleur_pct']):.1f}%"
                lignes.append(_tronquer(f" {corps} {abrev} {pct} {dist}SL", largeur))
            elif m.get("materiaux_rares"):
                lignes.append(_tronquer(f" {corps} {m['materiaux_rares'][0]}", largeur))

    if objectif in ("tout", "anneaux") and anneaux:
        lignes.append("ANNEAUX:")
        for a in anneaux[:2]:
            corps = _formater_corps_hud(a.get("planete"))
            dist = int(round(float(a.get("distance_sl", 0) or 0)))
            lignes.append(_tronquer(f" {corps} {a['type_anneau']} {dist}SL", largeur))

    if len(lignes) == 1:
        lignes.append("Aucune cible prioritaire")
    return formater_bloc_lignes(lignes, largeur, max_lignes)


def formater_vision_attente(
    question: str = "",
    largeur: int = 25,
    max_lignes: int = 10
) -> list[str]:
    """Formate l'indicateur d'attente pendant l'analyse vision locale."""
    lignes = ["VISION LOCALE", "Analyse ecran..."]
    if question and len(question.strip()) > 1:
        lignes.append("")
        lignes.append(question.strip())
    return formater_bloc_lignes(lignes, largeur, max_lignes)


def formater_vision_resultat(
    resume_hud: str,
    reponse_ia: str = "",
    erreur: str = "",
    largeur: int = 25,
    max_lignes: int = 10
) -> list[str]:
    """Formate un retour synthétique factuel après une analyse visuelle."""
    if erreur:
        return formater_bloc_lignes(["VISION : ERREUR", erreur], largeur, max_lignes)

    lignes = ["VISION"]
    source = (resume_hud or "").strip() or (reponse_ia or "").strip()
    if source:
        # Découpe propre sur les séparateurs '|' éventuels renvoyés par RESUME_HUD
        morceaux = [m.strip() for m in source.split("|") if m.strip()]
        if len(morceaux) > 1:
            lignes.extend(morceaux)
        else:
            lignes.append(source)
    else:
        lignes.append("Analyse terminee")
    return formater_bloc_lignes(lignes, largeur, max_lignes)


def formater_photo_enregistree(
    nom_fichier: str,
    resolution: str = "",
    ath_masque: bool = False,
    erreur: str = "",
    largeur: int = 25,
    max_lignes: int = 10
) -> list[str]:
    """Formate la confirmation synthétique d'une capture photo (0 jeton)."""
    if erreur:
        return formater_bloc_lignes(["PHOTO : ERREUR", erreur], largeur, max_lignes)

    lignes = ["PHOTO ENREGISTREE"]
    if nom_fichier:
        lignes.append(nom_fichier)
    if resolution:
        lignes.append(f"Res: {resolution}")
    if ath_masque:
        lignes.append("ATH masque auto")
    return formater_bloc_lignes(lignes, largeur, max_lignes)


# ==============================================================================
# HELPERS GÉOMÉTRIE 3D PERSPECTIVE (PILLOW) & POLICES WINDOWS
# ==============================================================================
def _hex_vers_rgb(couleur_hex: str, defaut=(18, 9, 4)) -> tuple[int, int, int]:
    """Convertit '#RRGGBB' en tuple (R, G, B)."""
    try:
        h = str(couleur_hex).strip().lstrip("#")
        if len(h) == 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except Exception:
        pass
    return defaut


def _calculer_coeffs_perspective(pts_dst: list[tuple[float, float]], pts_src: list[tuple[float, float]]) -> list[float]:
    """Résout le système linéaire 8x8 pour Image.Transform.PERSPECTIVE (pur Python).

    PIL mappe chaque coordonnée destination (x, y) vers la coordonnée source (u, v) :
        u = (a*x + b*y + c) / (g*x + h*y + 1)
        v = (d*x + e*y + f) / (g*x + h*y + 1)
    """
    matrice = []
    vecteur = []
    for (x, y), (u, v) in zip(pts_dst, pts_src):
        matrice.append([x, y, 1.0, 0.0, 0.0, 0.0, -u * x, -u * y])
        vecteur.append(u)
        matrice.append([0.0, 0.0, 0.0, x, y, 1.0, -v * x, -v * y])
        vecteur.append(v)

    # Élimination de Gauss avec pivot partiel
    n = 8
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(matrice[r][i]))
        matrice[i], matrice[pivot] = matrice[pivot], matrice[i]
        vecteur[i], vecteur[pivot] = vecteur[pivot], vecteur[i]

        diag = matrice[i][i]
        if abs(diag) < 1e-12:
            return [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]

        for j in range(i, n):
            matrice[i][j] /= diag
        vecteur[i] /= diag

        for k in range(n):
            if k != i:
                facteur = matrice[k][i]
                for j in range(i, n):
                    matrice[k][j] -= facteur * matrice[i][j]
                vecteur[k] -= facteur * vecteur[i]

    return vecteur


def _charger_police_pil(famille: str, taille_px: int):
    """Recherche le fichier TTF Windows correspondant à la police configurée."""
    if not PIL_DISPONIBLE:
        return None
    dossier_fonts = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    correspondances = {
        "consolas": ["consola.ttf", "consolab.ttf"],
        "courier new": ["cour.ttf", "courbd.ttf"],
        "lucida console": ["lucon.ttf"],
        "cascadia mono": ["CascadiaMono.ttf", "CascadiaCode.ttf"],
        "cascadia code": ["CascadiaCode.ttf", "CascadiaMono.ttf"],
        "segoe ui": ["segoeui.ttf", "segoeuib.ttf"],
        "arial": ["arial.ttf"],
        "calibri": ["calibri.ttf"],
        "bahnschrift": ["bahnschrift.ttf"],
        "tahoma": ["tahoma.ttf"],
        "verdana": ["verdana.ttf"]
    }
    cle = str(famille or "Consolas").strip().lower()
    candidats = list(correspondances.get(cle, []))
    # Ajoute aussi le nom direct au cas où l'utilisateur fournit un fichier TTF
    if cle.endswith(".ttf"):
        candidats.insert(0, famille)
    else:
        candidats.append(f"{cle.replace(' ', '')}.ttf")
    # Polices de secours garanties sur Windows
    candidats.extend(["consola.ttf", "cour.ttf", "segoeui.ttf", "arial.ttf"])

    for nom_f in candidats:
        chemin = nom_f if os.path.isabs(nom_f) else os.path.join(dossier_fonts, nom_f)
        if os.path.exists(chemin):
            try:
                return ImageFont.truetype(chemin, taille_px)
            except Exception:
                continue
    return ImageFont.load_default()


# ==============================================================================
# GESTIONNAIRE DE LA FENÊTRE HUD OVERLAY TRANSPARENT
# ==============================================================================
class HudOverlay:
    """Fenêtre Overlay HUD transparente, thread-safe et persistante par vue."""

    HAUTEUR_BARRE_DRAG = 18

    def __init__(self, config_hud: dict = None):
        self.cfg = dict(HUD_CONFIG)
        if config_hud:
            self.cfg.update(config_hud)

        self.nb_car_ligne = max(15, int(self.cfg.get("nb_caracteres_ligne", 25)))
        self.nb_lignes_max = max(4, int(self.cfg.get("nb_lignes_max", 10)))

        # Sécurisation couleur fond contre collision avec couleur clé transparente
        self.couleur_fond = str(self.cfg.get("couleur_fond", "#120904"))
        if self.couleur_fond.lower() == COULEUR_CLE_HEX:
            self.couleur_fond = "#120904"
        self.opacite = min(1.0, max(0.15, float(self.cfg.get("opacite", 0.82))))
        self.bordure = bool(self.cfg.get("bordure", False))
        self.couleur_bordure = str(self.cfg.get("couleur_bordure", "#FF7100"))
        self.epaisseur_bordure = max(1, int(self.cfg.get("epaisseur_bordure", 1)))
        self.police = str(self.cfg.get("police", "Consolas"))
        self.taille_police = max(8, int(self.cfg.get("taille_police", 12)))
        self.couleur_texte = str(self.cfg.get("couleur_texte", "#FF7100"))
        self.inclinaison_cockpit = bool(self.cfg.get("inclinaison_cockpit", True))
        self.angle_cockpit = float(self.cfg.get("angle_cockpit_degres", 3.5))
        self.perspective_cockpit = min(0.18, max(0.0, float(self.cfg.get("perspective_cockpit", 0.07))))

        # États internes
        self._visible = bool(self.cfg.get("actif_au_demarrage", False))
        self._vue_actuelle = VUE_COCKPIT
        self._micro_actif = False
        self._lignes_actuelles: list[str] = []
        self._survol_hud = False
        self._click_through_actif = True
        self._en_glisser = False
        self._drag_offset_x = 0
        self._drag_offset_y = 0

        # Positions mémorisées par vue
        self._positions_par_vue = self._charger_positions()

        # File de commandes thread-safe vers le thread Tkinter
        self._file_actions: queue.Queue = queue.Queue()
        self._pret_event = threading.Event()
        self._arret_demande = False
        self._thread_ui = None

        # Références UI (manipulées uniquement dans le thread Tkinter)
        self._root = None
        self._canvas = None
        self._hwnd = None
        self._tk_font = None
        self._tk_font_petite = None
        self._photo_pil_ref = None
        self._largeur_fenetre = 260
        self._hauteur_fenetre = 220
        self._pad_x = 12
        self._pad_y = 8
        self._marge_3d = 18

    # --------------------------------------------------------------------------
    # PERSISTANCE DES POSITIONS PAR VUE
    # --------------------------------------------------------------------------
    def _charger_positions(self) -> dict:
        """Charge les positions depuis data/hud_positions.json avec fallback sur config."""
        defauts_cfg = self.cfg.get("positions_par_vue", {})
        positions = {}
        for vue in VUES_VALIDES:
            pos = defauts_cfg.get(vue, [80, 120])
            if isinstance(pos, (list, tuple)) and len(pos) == 2:
                positions[vue] = [int(pos[0]), int(pos[1])]
            else:
                positions[vue] = [80, 120]

        if os.path.exists(FICHIER_POSITIONS_HUD):
            try:
                with open(FICHIER_POSITIONS_HUD, "r", encoding="utf-8") as f:
                    sauvegardees = json.load(f)
                if isinstance(sauvegardees, dict):
                    for vue in VUES_VALIDES:
                        pos = sauvegardees.get(vue)
                        if isinstance(pos, (list, tuple)) and len(pos) == 2:
                            positions[vue] = [int(pos[0]), int(pos[1])]
            except Exception as e:
                print(f"[HUD] Impossible de lire {FICHIER_POSITIONS_HUD.name} : {e}")
        return positions

    def _sauvegarder_positions(self):
        """Enregistre atomiquement les positions par vue dans data/hud_positions.json."""
        try:
            chemin_tmp = str(FICHIER_POSITIONS_HUD) + ".tmp"
            with open(chemin_tmp, "w", encoding="utf-8") as f:
                json.dump(self._positions_par_vue, f, ensure_ascii=False, indent=2)
            os.replace(chemin_tmp, FICHIER_POSITIONS_HUD)
        except Exception as e:
            print(f"[HUD] Erreur sauvegarde positions : {e}")

    # --------------------------------------------------------------------------
    # API PUBLIQUE THREAD-SAFE
    # --------------------------------------------------------------------------
    def demarrer(self):
        """Lance la boucle Tkinter du HUD dans un thread daemon dédié."""
        if self._thread_ui and self._thread_ui.is_alive():
            return
        self._thread_ui = threading.Thread(target=self._boucle_tk, name="OscarHUD", daemon=True)
        self._thread_ui.start()
        self._pret_event.wait(timeout=3.0)

    def arreter(self):
        """Ferme proprement la fenêtre HUD."""
        self._arret_demande = True
        self._file_actions.put(("ARRETER", None))
        if self._thread_ui and self._thread_ui.is_alive() and threading.current_thread() != self._thread_ui:
            self._thread_ui.join(timeout=1.5)

    def afficher(self):
        """Affiche la fenêtre HUD (conserve le dernier texte affiché)."""
        self._file_actions.put(("AFFICHER", None))

    def masquer(self):
        """Masque la fenêtre HUD sans effacer le dernier contenu mémorisé."""
        self._file_actions.put(("MASQUER", None))

    def est_visible(self) -> bool:
        """Indique si la fenêtre HUD est actuellement affichée à l'écran."""
        return bool(self._visible)

    def definir_etat_micro(self, en_ecoute: bool):
        """Met à jour le témoin micro : rouge si en écoute, vert sinon."""
        self._file_actions.put(("MICRO", bool(en_ecoute)))

    def changer_vue(self, nouvelle_vue: str):
        """Change la vue active Elite Dangerous (repositionne + adapte le rendu 3D)."""
        if nouvelle_vue in VUES_VALIDES:
            self._file_actions.put(("VUE", nouvelle_vue))

    def afficher_lignes(self, lignes: list[str]):
        """Efface l'affichage précédent et affiche les nouvelles lignes (25 car x 10 lignes)."""
        propres = formater_bloc_lignes(lignes or [], self.nb_car_ligne, self.nb_lignes_max)
        self._file_actions.put(("TEXTE", propres))

    def afficher_texte(self, texte: str):
        """Efface l'affichage précédent et affiche un texte brut enveloppé."""
        propres = envelopper_lignes(texte or "", self.nb_car_ligne)[:self.nb_lignes_max]
        self._file_actions.put(("TEXTE", propres))

    def afficher_dictee(self, texte_complet: str):
        """Affiche la dictée avec pagination automatique par blocs de 10 lignes."""
        lignes = paginer_dictee(texte_complet or "", self.nb_car_ligne, self.nb_lignes_max)
        self._file_actions.put(("TEXTE", lignes))

    def afficher_epellation(self, buffer_texte: str):
        """Affiche les caractères épelés dès la première ligne."""
        lignes = formater_epellation(buffer_texte or "", self.nb_car_ligne, self.nb_lignes_max)
        self._file_actions.put(("TEXTE", lignes))

    def afficher_commande_vaisseau(self, nom_commande: str):
        """Affiche le nom de la commande vaisseau [EXECUTE:commande]."""
        lignes = formater_commande_vaisseau(nom_commande, self.nb_car_ligne, self.nb_lignes_max)
        self._file_actions.put(("TEXTE", lignes))

    def afficher_alerte(self, cle_alerte: str, detail: str = ""):
        """Affiche le condensé factuel d'une alerte proactive."""
        lignes = formater_alerte_proactive(cle_alerte, detail, self.nb_car_ligne, self.nb_lignes_max)
        self._file_actions.put(("TEXTE", lignes))

    def afficher_resultat_outil(self, nom_outil: str, args: dict, donnees, question_pilote: str = ""):
        """Formate et affiche le condensé factuel d'un résultat d'outil OpenAI."""
        lignes = formater_resultat_outil_hud(
            nom_outil, args, donnees, question_pilote,
            self.nb_car_ligne, self.nb_lignes_max
        )
        if lignes is not None:
            self._file_actions.put(("TEXTE", lignes))

    def effacer_contenu(self):
        """Vide explicitement le texte affiché."""
        self._file_actions.put(("TEXTE", []))

    def afficher_vision_en_cours(self, question: str = ""):
        """Affiche l'état d'attente Vision (visible uniquement si le HUD est actif)."""
        lignes = formater_vision_attente(question, self.nb_car_ligne, self.nb_lignes_max)
        self._file_actions.put(("TEXTE", lignes))

    def afficher_vision_resultat(self, resume_hud: str, reponse_ia: str = "", erreur: str = ""):
        """Affiche un retour synthétique factuel Vision (visible uniquement si le HUD est actif)."""
        lignes = formater_vision_resultat(
            resume_hud, reponse_ia, erreur,
            self.nb_car_ligne, self.nb_lignes_max
        )
        self._file_actions.put(("TEXTE", lignes))

    def afficher_photo_enregistree(
        self,
        nom_fichier: str,
        resolution: str = "",
        ath_masque: bool = False,
        erreur: str = ""
    ):
        """Affiche la confirmation synthétique de photo (visible uniquement si le HUD est actif)."""
        lignes = formater_photo_enregistree(
            nom_fichier, resolution, ath_masque, erreur,
            self.nb_car_ligne, self.nb_lignes_max
        )
        self._file_actions.put(("TEXTE", lignes))

    # --------------------------------------------------------------------------
    # UTILITAIRES WIN32 (TRANSPARENCE, CLICK-THROUGH, FOCUS, POSITION CURSEUR)
    # --------------------------------------------------------------------------
    def _obtenir_hwnd(self):
        """Récupère le handle natif Win32 (HWND) de la fenêtre Tkinter."""
        if not self._root:
            return None
        try:
            self._root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self._root.winfo_id())
            if not hwnd:
                hwnd = self._root.winfo_id()
            return hwnd
        except Exception:
            return None

    def _appliquer_styles_win32(self, click_through: bool = True, utiliser_colorkey: bool = False):
        """Configure les flags Win32 (layered, topmost, noactivate, click-through, opacité)."""
        if not self._hwnd:
            self._hwnd = self._obtenir_hwnd()
        if not self._hwnd:
            return
        try:
            user32 = ctypes.windll.user32
            style = user32.GetWindowLongW(self._hwnd, GWL_EXSTYLE)
            nouveau_style = style | WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
            if click_through:
                nouveau_style |= WS_EX_TRANSPARENT
            else:
                nouveau_style &= ~WS_EX_TRANSPARENT

            if nouveau_style != style:
                user32.SetWindowLongW(self._hwnd, GWL_EXSTYLE, nouveau_style)

            alpha_byte = int(round(self.opacite * 255))
            if utiliser_colorkey:
                user32.SetLayeredWindowAttributes(
                    self._hwnd, COULEUR_CLE_BGR, alpha_byte, LWA_COLORKEY | LWA_ALPHA
                )
            else:
                user32.SetLayeredWindowAttributes(
                    self._hwnd, 0, alpha_byte, LWA_ALPHA
                )

            user32.SetWindowPos(
                self._hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_FRAMECHANGED
            )
            self._click_through_actif = click_through
        except Exception:
            pass

    def _position_curseur(self) -> tuple[int, int] | None:
        """Retourne la position absolue (x, y) du pointeur souris sous Windows."""
        try:
            pt = wintypes.POINT()
            if ctypes.windll.user32.GetCursorPos(ctypes.byref(pt)):
                return (pt.x, pt.y)
        except Exception:
            pass
        return None

    def _cliquer_gauche_enfonce(self) -> bool:
        """Indique si le bouton gauche de la souris est actuellement maintenu."""
        try:
            return bool(ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000)
        except Exception:
            return False

    # --------------------------------------------------------------------------
    # BOUCLE TKINTER ET RENDU GRAPHIQUE
    # --------------------------------------------------------------------------
    def _utiliser_rendu_3d(self) -> bool:
        """Indique si le rendu perspective 3D cockpit est actif pour la vue courante."""
        return (
            self.inclinaison_cockpit
            and self._vue_actuelle == VUE_COCKPIT
        )

    def _calculer_dimensions(self):
        """Calcule la taille exacte du panneau pour 25 caractères x 10 lignes."""
        self._tk_font = tkfont.Font(family=self.police, size=self.taille_police)
        self._tk_font_petite = tkfont.Font(family=self.police, size=max(7, self.taille_police - 3))

        # Mesure fiable pour 25 caractères (monospace ou proportionnel)
        largeur_echantillon = self._tk_font.measure("0" * self.nb_car_ligne)
        largeur_m = self._tk_font.measure("M" * self.nb_car_ligne)
        largeur_texte = max(largeur_echantillon, int(largeur_m * 0.92))
        hauteur_ligne = max(14, int(self._tk_font.metrics("linespace") + 2))

        self._hauteur_ligne = hauteur_ligne
        marge_persp = int(largeur_texte * self.perspective_cockpit * 1.4) if self.inclinaison_cockpit else 0
        self._largeur_panneau = largeur_texte + self._pad_x * 2 + marge_persp
        self._hauteur_panneau = self.HAUTEUR_BARRE_DRAG + (hauteur_ligne * self.nb_lignes_max) + self._pad_y * 2

        # Marge externe supplémentaire pour accueillir l'inclinaison 3D sans rognage
        self._marge_3d = 18 if self.inclinaison_cockpit else 0
        self._largeur_fenetre = self._largeur_panneau + self._marge_3d * 2
        self._hauteur_fenetre = self._hauteur_panneau + self._marge_3d * 2

    def _boucle_tk(self):
        """Point d'entrée du thread Tkinter (création fenêtre + boucle d'événements)."""
        try:
            self._root = tk.Tk()
            self._root.title("Oscar HUD")
            self._root.overrideredirect(True)
            self._root.attributes("-topmost", True)
            self._root.configure(bg=COULEUR_CLE_HEX)

            self._calculer_dimensions()

            self._canvas = tk.Canvas(
                self._root,
                width=self._largeur_fenetre,
                height=self._hauteur_fenetre,
                bg=COULEUR_CLE_HEX,
                highlightthickness=0,
                bd=0
            )
            self._canvas.pack(fill="both", expand=True)

            # Événements de glisser-déposer sur la barre de déplacement
            self._canvas.bind("<ButtonPress-1>", self._on_drag_start)
            self._canvas.bind("<B1-Motion>", self._on_drag_motion)
            self._canvas.bind("<ButtonRelease-1>", self._on_drag_end)

            # Position initiale selon la vue cockpit
            self._appliquer_position_vue(self._vue_actuelle)
            self._hwnd = self._obtenir_hwnd()
            self._redessiner()

            if self._visible:
                self._root.deiconify()
                self._appliquer_styles_win32(click_through=True, utiliser_colorkey=self._utiliser_rendu_3d())
            else:
                self._root.withdraw()

            self._pret_event.set()
            self._root.after(40, self._traiter_file_actions)
            self._root.after(60, self._verifier_survol_souris)
            self._root.mainloop()
        except Exception as e:
            print(f"[HUD] Erreur fatale interface HUD : {e}")
            self._pret_event.set()
        finally:
            # Libération propre des références Tcl/Tk dans le thread créateur
            self._photo_pil_ref = None
            self._tk_font = None
            self._tk_font_petite = None
            self._canvas = None
            self._root = None

    def _appliquer_position_vue(self, vue: str):
        """Positionne la fenêtre aux coordonnées mémorisées pour `vue`."""
        pos = self._positions_par_vue.get(vue, [80, 120])
        x, y = int(pos[0]), int(pos[1])
        self._root.geometry(f"{self._largeur_fenetre}x{self._hauteur_fenetre}+{x}+{y}")

    def _traiter_file_actions(self):
        """Consomme les messages envoyés par les autres threads d'Oscar."""
        if self._arret_demande:
            try:
                self._root.destroy()
            except Exception:
                pass
            return

        doit_redessiner = False
        try:
            while True:
                action, payload = self._file_actions.get_nowait()
                if action == "ARRETER":
                    self._root.destroy()
                    return
                elif action == "AFFICHER":
                    self._visible = True
                    self._appliquer_position_vue(self._vue_actuelle)
                    self._root.deiconify()
                    self._appliquer_styles_win32(click_through=True, utiliser_colorkey=self._utiliser_rendu_3d())
                    doit_redessiner = True
                elif action == "MASQUER":
                    self._visible = False
                    self._survol_hud = False
                    self._en_glisser = False
                    self._root.withdraw()
                elif action == "MICRO":
                    if self._micro_actif != payload:
                        self._micro_actif = payload
                        doit_redessiner = True
                elif action == "VUE":
                    if self._vue_actuelle != payload:
                        self._vue_actuelle = payload
                        self._appliquer_position_vue(self._vue_actuelle)
                        doit_redessiner = True
                elif action == "TEXTE":
                    self._lignes_actuelles = list(payload)
                    doit_redessiner = True
        except queue.Empty:
            pass

        if doit_redessiner:
            self._redessiner()

        self._root.after(40, self._traiter_file_actions)

    def _verifier_survol_souris(self):
        """Détecte le survol souris pour afficher la barre de déplacement et gérer le click-through."""
        if self._arret_demande:
            return

        if self._visible and self._root:
            pt = self._position_curseur()
            if pt:
                mx, my = pt
                wx = self._root.winfo_x()
                wy = self._root.winfo_y()
                m = self._marge_3d
                # Zone utile du panneau HUD
                px1 = wx + m
                py1 = wy + m
                px2 = px1 + self._largeur_panneau
                py2 = py1 + self._hauteur_panneau

                dans_hud = (px1 <= mx <= px2) and (py1 <= my <= py2)
                # Zone de saisie : la barre supérieure (+ petite tolérance verticale)
                dans_barre = (px1 <= mx <= px2) and (py1 - 4 <= my <= py1 + self.HAUTEUR_BARRE_DRAG + 6)

                # Sécurité si le bouton gauche a été relâché hors fenêtre
                if self._en_glisser and not self._cliquer_gauche_enfonce():
                    self._en_glisser = False
                    self._enregistrer_position_courante()

                nouveau_survol = dans_hud or self._en_glisser
                if nouveau_survol != self._survol_hud:
                    self._survol_hud = nouveau_survol
                    self._redessiner()

                # On désactive WS_EX_TRANSPARENT uniquement sur la barre de déplacement ou pendant le drag
                doit_etre_click_through = not (dans_barre or self._en_glisser)
                if doit_etre_click_through != self._click_through_actif:
                    self._appliquer_styles_win32(
                        click_through=doit_etre_click_through,
                        utiliser_colorkey=self._utiliser_rendu_3d()
                    )

        self._root.after(60, self._verifier_survol_souris)

    def _on_drag_start(self, event):
        """Démarre le déplacement du HUD si le clic est sur la barre supérieure."""
        m = self._marge_3d
        if event.y <= m + self.HAUTEUR_BARRE_DRAG + 10:
            self._en_glisser = True
            self._drag_offset_x = event.x_root - self._root.winfo_x()
            self._drag_offset_y = event.y_root - self._root.winfo_y()
            self._canvas.configure(cursor="fleur")

    def _on_drag_motion(self, event):
        """Déplace la fenêtre en temps réel pendant le glisser-déposer."""
        if not self._en_glisser:
            return
        nx = event.x_root - self._drag_offset_x
        ny = event.y_root - self._drag_offset_y
        self._root.geometry(f"+{nx}+{ny}")

    def _on_drag_end(self, _event):
        """Termine le déplacement et sauvegarde la position pour la vue active."""
        if self._en_glisser:
            self._en_glisser = False
            self._canvas.configure(cursor="")
            self._enregistrer_position_courante()

    def _enregistrer_position_courante(self):
        """Mémorise la position actuelle de la fenêtre pour la vue courante."""
        if not self._root:
            return
        nx = self._root.winfo_x()
        ny = self._root.winfo_y()
        self._positions_par_vue[self._vue_actuelle] = [nx, ny]
        self._sauvegarder_positions()
        print(f"[HUD] Position sauvegardée pour la vue '{self._vue_actuelle}' : ({nx}, {ny})")

    # --------------------------------------------------------------------------
    # DESSIN : RENDU 3D COCKPIT (PILLOW) ET RENDU PLAT NATIF (TKINTER CANVAS)
    # --------------------------------------------------------------------------
    def _redessiner(self):
        """Redessine entièrement le panneau HUD selon la vue et l'état courants."""
        if not self._canvas:
            return
        self._canvas.delete("all")

        if self._utiliser_rendu_3d():
            if PIL_DISPONIBLE and self._dessiner_pil_cockpit_3d():
                self._appliquer_styles_win32(
                    click_through=self._click_through_actif,
                    utiliser_colorkey=True
                )
                return
            # Rendu 3D vectoriel natif Tkinter (trapèze couché + texte incliné, 0 dépendance)
            self._dessiner_canvas_cockpit_3d()
            self._appliquer_styles_win32(
                click_through=self._click_through_actif,
                utiliser_colorkey=True
            )
            return

        self._dessiner_canvas_plat()
        self._appliquer_styles_win32(
            click_through=self._click_through_actif,
            utiliser_colorkey=False
        )

    def _dessiner_canvas_cockpit_3d(self):
        """Rendu 3D légèrement couché 100% natif Tkinter (polygone perspective + texte incliné)."""
        c = self._canvas
        m = self._marge_3d
        wp = float(self._largeur_panneau)
        hp = float(self._hauteur_panneau)

        persp_x = wp * self.perspective_cockpit
        # Inclinaison verticale douce selon l'angle configuré
        dy_tilt = math.tan(math.radians(self.angle_cockpit)) * wp * 0.45

        # 4 sommets du panneau holographique légèrement couché vers le tableau de bord
        x_hg, y_hg = m + persp_x, m + max(0.0, dy_tilt)
        x_hd, y_hd = m + wp - persp_x * 0.35, m + max(0.0, -dy_tilt)
        x_bd, y_bd = m + wp, m + hp - max(0.0, dy_tilt * 0.5)
        x_bg, y_bg = m, m + hp

        contour = self.couleur_bordure if self.bordure else self.couleur_fond
        ep = self.epaisseur_bordure if self.bordure else 0
        c.create_polygon(
            x_hg, y_hg, x_hd, y_hd, x_bd, y_bd, x_bg, y_bg,
            fill=self.couleur_fond, outline=contour, width=ep
        )

        # Angle réel de l'arête supérieure (Tkinter : positif = anti-horaire)
        angle_tk = -math.degrees(math.atan2(y_hd - y_hg, x_hd - x_hg))

        # Barre de déplacement au survol (suit le haut du trapèze)
        t_barre = self.HAUTEUR_BARRE_DRAG / hp
        if self._survol_hud:
            bx_bg = x_hg + (x_bg - x_hg) * t_barre
            by_bg = y_hg + (y_bg - y_hg) * t_barre
            bx_bd = x_hd + (x_bd - x_hd) * t_barre
            by_bd = y_hd + (y_bd - y_hd) * t_barre
            c.create_polygon(
                x_hg + 1, y_hg + 1, x_hd - 1, y_hd + 1,
                bx_bd - 1, by_bd, bx_bg + 1, by_bg,
                fill="#2E1A0B", outline=""
            )
            lib_vue = LIBELLES_VUES.get(self._vue_actuelle, "")
            c.create_text(
                (x_hg + bx_bg) / 2.0 + 8,
                (y_hg + by_bg) / 2.0,
                text=f"=== DEPLACER [{lib_vue}]",
                anchor="w",
                fill=self.couleur_texte,
                font=self._tk_font_petite,
                angle=angle_tk
            )

        # Icône micro en haut à droite du panneau incliné
        self._dessiner_icone_micro_canvas(c, int(x_hd - 14), int(y_hd + 10))

        # Lignes de texte alignées le long de l'arête gauche et inclinées à l'angle du panneau
        for idx, ligne in enumerate(self._lignes_actuelles[:self.nb_lignes_max]):
            y_rel = self.HAUTEUR_BARRE_DRAG + self._pad_y + idx * self._hauteur_ligne
            t = min(1.0, y_rel / hp)
            lx = x_hg + (x_bg - x_hg) * t + self._pad_x
            ly = y_hg + (y_bg - y_hg) * t
            c.create_text(
                lx, ly,
                text=ligne,
                anchor="nw",
                fill=self.couleur_texte,
                font=self._tk_font,
                angle=angle_tk
            )

    def _dessiner_canvas_plat(self):
        """Dessin vectoriel natif Tkinter (vues Cartes / À pied ou si Pillow absent)."""
        c = self._canvas
        m = self._marge_3d
        x1, y1 = m, m
        x2, y2 = m + self._largeur_panneau, m + self._hauteur_panneau

        # Fond translucide du panneau
        contour = self.couleur_bordure if self.bordure else self.couleur_fond
        ep = self.epaisseur_bordure if self.bordure else 0
        c.create_rectangle(x1, y1, x2, y2, fill=self.couleur_fond, outline=contour, width=ep)

        # Barre de déplacement discrète (visible uniquement au survol souris)
        if self._survol_hud:
            c.create_rectangle(
                x1 + 1, y1 + 1, x2 - 1, y1 + self.HAUTEUR_BARRE_DRAG,
                fill="#2E1A0B", outline=""
            )
            lib_vue = LIBELLES_VUES.get(self._vue_actuelle, "")
            c.create_text(
                x1 + 8, y1 + self.HAUTEUR_BARRE_DRAG // 2,
                text=f"=== DEPLACER [{lib_vue}]",
                anchor="w",
                fill=self.couleur_texte,
                font=self._tk_font_petite
            )

        # Icône micro en haut à droite (Rouge = écoute, Vert = repos)
        self._dessiner_icone_micro_canvas(c, x2 - 14, y1 + 10)

        # Lignes de texte (max 10 lignes x 25 caractères)
        y_depart = y1 + self.HAUTEUR_BARRE_DRAG + self._pad_y
        for idx, ligne in enumerate(self._lignes_actuelles[:self.nb_lignes_max]):
            c.create_text(
                x1 + self._pad_x,
                y_depart + idx * self._hauteur_ligne,
                text=ligne,
                anchor="nw",
                fill=self.couleur_texte,
                font=self._tk_font
            )

    def _dessiner_icone_micro_canvas(self, c: tk.Canvas, cx: int, cy: int):
        """Dessine une petite icône micro vectorielle (rouge actif / vert inactif)."""
        couleur = "#FF2B2B" if self._micro_actif else "#2EE050"
        # Corps (capsule) du micro
        c.create_oval(cx - 3, cy - 6, cx + 3, cy + 1, fill=couleur, outline=couleur)
        # Berceau U autour du micro
        c.create_arc(cx - 5, cy - 3, cx + 5, cy + 4, start=180, extent=180, style="arc", outline=couleur, width=1.5)
        # Pied du micro
        c.create_line(cx, cy + 4, cx, cy + 7, fill=couleur, width=1.5)
        c.create_line(cx - 3, cy + 7, cx + 3, cy + 7, fill=couleur, width=1.5)

    def _dessiner_pil_cockpit_3d(self) -> bool:
        """Rend le panneau HUD avec une légère perspective 3D couchée pour le cockpit."""
        try:
            scale = 2  # Supersampling x2 pour un texte parfaitement net
            wp = self._largeur_panneau * scale
            hp = self._hauteur_panneau * scale
            wf = self._largeur_fenetre * scale
            hf = self._hauteur_fenetre * scale
            ms = self._marge_3d * scale

            rgb_fond = _hex_vers_rgb(self.couleur_fond, (18, 9, 4))
            rgb_texte = _hex_vers_rgb(self.couleur_texte, (255, 113, 0))
            rgb_bord = _hex_vers_rgb(self.couleur_bordure, rgb_texte)
            rgb_barre = (
                min(255, rgb_fond[0] + 34),
                min(255, rgb_fond[1] + 20),
                min(255, rgb_fond[2] + 10)
            )

            # 1. Dessin haute résolution du panneau droit dans un buffer RGBA
            panneau = Image.new("RGBA", (wp, hp), (0, 0, 0, 0))
            draw = ImageDraw.Draw(panneau)

            # Fond du panneau (avec léger biseau HUD aux coins supérieurs/inférieurs)
            draw.rectangle([0, 0, wp - 1, hp - 1], fill=(*rgb_fond, 255))

            if self.bordure:
                ep = self.epaisseur_bordure * scale
                draw.rectangle([0, 0, wp - 1, hp - 1], outline=(*rgb_bord, 255), width=ep)

            # Polices TrueType calibrées à la taille Tkinter (conversion pt -> px à 96 DPI)
            taille_px = max(10, int(round(self.taille_police * 96.0 / 72.0 * scale)))
            taille_petite_px = max(9, int(round(max(7, self.taille_police - 3) * 96.0 / 72.0 * scale)))
            font_pil = _charger_police_pil(self.police, taille_px)
            font_petite = _charger_police_pil(self.police, taille_petite_px)

            # Barre de déplacement au survol
            h_barre = self.HAUTEUR_BARRE_DRAG * scale
            if self._survol_hud:
                draw.rectangle([scale, scale, wp - scale - 1, h_barre], fill=(*rgb_barre, 255))
                lib_vue = LIBELLES_VUES.get(self._vue_actuelle, "")
                draw.text(
                    (8 * scale, 3 * scale),
                    f"=== DEPLACER [{lib_vue}]",
                    fill=(*rgb_texte, 255),
                    font=font_petite
                )

            # Icône micro en haut à droite
            cx = wp - 14 * scale
            cy = 10 * scale
            col_mic = (255, 43, 43, 255) if self._micro_actif else (46, 224, 80, 255)
            draw.rounded_rectangle(
                [cx - 3 * scale, cy - 6 * scale, cx + 3 * scale, cy + 1 * scale],
                radius=3 * scale,
                fill=col_mic
            )
            draw.arc(
                [cx - 5 * scale, cy - 3 * scale, cx + 5 * scale, cy + 4 * scale],
                start=0, end=180, fill=col_mic, width=max(2, scale)
            )
            draw.line([cx, cy + 4 * scale, cx, cy + 7 * scale], fill=col_mic, width=max(2, scale))
            draw.line([cx - 3 * scale, cy + 7 * scale, cx + 3 * scale, cy + 7 * scale], fill=col_mic, width=max(2, scale))

            # Texte des 10 lignes max
            y_deb = h_barre + self._pad_y * scale
            h_lig = self._hauteur_ligne * scale
            for idx, ligne in enumerate(self._lignes_actuelles[:self.nb_lignes_max]):
                draw.text(
                    (self._pad_x * scale, y_deb + idx * h_lig),
                    ligne,
                    fill=(*rgb_texte, 255),
                    font=font_pil
                )

            # 2. Projection perspective 3D légèrement couchée (style console de cockpit)
            persp_x = wp * self.perspective_cockpit
            tilt_y = math.tan(math.radians(self.angle_cockpit)) * wp * 0.25

            # Quadrilatère source (panneau droit) -> destination (légèrement couché et incliné)
            pts_src = [(0.0, 0.0), (float(wp), 0.0), (float(wp), float(hp)), (0.0, float(hp))]
            pts_dst = [
                (ms + persp_x, ms + max(0.0, tilt_y)),
                (ms + wp - persp_x * 0.45, ms + max(0.0, -tilt_y)),
                (ms + wp, ms + hp - max(0.0, tilt_y * 0.6)),
                (ms, ms + hp)
            ]

            coeffs = _calculer_coeffs_perspective(pts_dst, pts_src)
            projetee = panneau.transform(
                (wf, hf),
                Image.Transform.PERSPECTIVE,
                coeffs,
                resample=Image.Resampling.BICUBIC
            )

            # 3. Réduction anti-aliasée vers 1x
            finale_rgba = projetee.resize(
                (self._largeur_fenetre, self._hauteur_fenetre),
                resample=Image.Resampling.LANCZOS
            )

            # 4. Compositing propre sur la couleur clé transparente (sans halo de bordure)
            # On pré-mélange les bords semi-transparents avec la couleur du fond, puis masque net
            fond_uni = Image.new("RGB", finale_rgba.size, rgb_fond)
            alpha = finale_rgba.getchannel("A")
            masque_net = alpha.point(lambda a: 255 if a >= 96 else 0)
            panneau_rgb = Image.composite(finale_rgba.convert("RGB"), fond_uni, alpha)

            sortie = Image.new("RGB", finale_rgba.size, COULEUR_CLE_RGB)
            sortie.paste(panneau_rgb, (0, 0), masque_net)

            self._photo_pil_ref = ImageTk.PhotoImage(sortie)
            self._canvas.create_image(0, 0, image=self._photo_pil_ref, anchor="nw")
            return True
        except Exception as e:
            print(f"[HUD] Fallback rendu plat (erreur perspective 3D : {e})")
            return False


# ==============================================================================
# MODE TEST / DÉMO AUTONOME (py -m modules.hud_overlay)
# ==============================================================================
if __name__ == "__main__":
    print("=== MODE TEST AUTONOME DU HUD OSCAR ===")
    print("Survole le HUD pour faire apparaître la barre de déplacement.")
    print("Ferme la console (Ctrl+C) pour quitter le test.")

    hud = HudOverlay({"actif_au_demarrage": True})
    hud.demarrer()
    hud.afficher()

    scenarios = [
        ("Commande vaisseau", lambda: hud.afficher_commande_vaisseau("Sortir Train Atterrissage")),
        ("Micro ROUGE (écoute)", lambda: hud.definir_etat_micro(True)),
        ("Micro VERT (repos)", lambda: hud.definir_etat_micro(False)),
        ("Commerce Spansh", lambda: hud.afficher_resultat_outil(
            "rechercher_commerce_ou_equipement",
            {},
            {
                "recherche": "Platinum",
                "mode": "vendre",
                "meilleures_stations": [{
                    "systeme": "Popocassa",
                    "station": "Heaviside Dock",
                    "distance_annees_lumiere": 24.5,
                    "sauts_approximatifs": 1,
                    "quantite_tonnes": 4250,
                    "prix_par_tonne_credits": 285400
                }]
            }
        )),
        ("Destination + Vue Galaxie (plat)", lambda: (
            hud.changer_vue(VUE_CARTE_GALACTIQUE),
            hud.afficher_resultat_outil(
                "calculer_distance_entre_systemes",
                {},
                {"depart": "Popocassa", "arrivee": "Sol", "distance_annees_lumiere": 84.32, "sauts_estimes": 2}
            )
        )),
        ("Mode Épeler (ligne 1)", lambda: hud.afficher_epellation("SYNUEFE EN-H D11-96")),
        ("Retour Cockpit 3D + Alerte", lambda: (
            hud.changer_vue(VUE_COCKPIT),
            hud.afficher_alerte("bouclier_tombe")
        )),
        ("Mode Dictée (pagination >10 lignes)", lambda: hud.afficher_dictee(
            "Ceci est un test complet du mode dictee sur le HUD transparent d Oscar. "
            "Lorsque le texte depasse dix lignes de vingt cinq caracteres, la fenetre "
            "s efface automatiquement et continue en recommencant proprement a la premiere ligne !"
        ))
    ]

    try:
        idx = 0
        while True:
            nom, action = scenarios[idx % len(scenarios)]
            print(f"[Démo HUD] -> {nom}")
            action()
            idx += 1
            time.sleep(3.5)
    except KeyboardInterrupt:
        hud.arreter()
        print("\n[Démo HUD] Arrêt propre.")
