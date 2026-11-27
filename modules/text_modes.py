"""Module de gestion des modes de saisie textuelle (Dictée dans le chat et Épellation galactique)."""

import re
import time

from modules.config_loader import COMMANDES_MODES
from modules.input_engine import (
    VK_A,
    VK_BACK,
    VK_DELETE,
    VK_RETURN,
    appuyer_touche_vk,
    coller_texte_via_presse_papier,
    effacer_dernier_bloc_exact,
    envoyer_raccourci_ctrl,
    relacher_modificateurs,
    taper_caractere_unicode
)
from modules.telemetry_ed import normaliser_texte
from modules.tts_engine import dire_vocal

MODE_NORMAL = "NORMAL"
MODE_DICTEE = "DICTEE"
MODE_EPELLATION = "EPELLATION"

COMMANDES_SORTIE = set(COMMANDES_MODES.get("commandes_sortie", []))
ALPHABET_PHONETIQUE = COMMANDES_MODES.get("alphabet_phonetique", {})

# Motif regex pour détecter un ordre de saut de ligne en fin de phrase dictée
REGEX_SAUT_LIGNE_FIN = re.compile(
    r'[,.;:\s]*(?:paragraphe?\s+suivant|nouveau\s+paragraphe|[aà]\s+la\s+ligne|nouvelle\s+ligne|ligne\s+suivante)\s*[.!?]*$',
    re.IGNORECASE
)


def formater_ponctuation_dictee(texte: str) -> str:
    """Convertit les mots de ponctuation dictés en vrais symboles et nettoie les collisions."""
    t = " " + texte.strip() + " "
    remplacements = [
        (r"\bpoint d'interrogation\b", "?"),
        (r"\bpoint d'exclamation\b", "!"),
        (r"\bpoints de suspension\b", "..."),
        (r"\bdeux points\b", ":"),
        (r"\bpoint virgule\b", ";"),
        (r"\bpoint\b", "."),
        (r"\bvirgule\b", ","),
        (r"\btiret\b", "-"),
        (r"\bdi[èe]se\b", "#"),
        (r"\bunderscore\b", "_"),
        (r"\btiret du bas\b", "_"),
        (r"\bà la ligne\b", "\n")
    ]
    for motif, symbole in remplacements:
        t = re.sub(motif, symbole, t, flags=re.IGNORECASE)

    # Nettoyage des espaces avant la ponctuation
    t = re.sub(r"\s+([.,;:!?])", r"\1", t)
    t = re.sub(r"\s*([-_#])\s*", r"\1", t)

    # Nettoyage des collisions de ponctuation (ex: ".," ou ",." -> ".")
    t = re.sub(r'([.!?])\s*[,;:]+', r'\1', t)
    t = re.sub(r'[,;:]+\s*([.!?])', r'\1', t)
    t = re.sub(r',+', ',', t)

    return t.strip()


class GestionnaireModesTexte:
    """Gère l'état et l'aiguillage des modes de saisie directe (Dictée et Épellation)."""

    def __init__(self, hud=None):
        self.mode_actuel = MODE_NORMAL
        self.historique_blocs_dictee = []
        self.premier_bloc_dictee = True
        self.buffer_epellation = ""
        self.hud = hud

    def _maj_hud_dictee(self):
        """Met à jour la prévisualisation HUD du mode Dictée."""
        if self.hud:
            self.hud.afficher_dictee("".join(self.historique_blocs_dictee))

    def _maj_hud_epellation(self):
        """Met à jour la prévisualisation HUD du mode Épellation dès la ligne 1."""
        if self.hud:
            self.hud.afficher_epellation(self.buffer_epellation)

    def est_mode_special(self) -> bool:
        return self.mode_actuel != MODE_NORMAL

    def activer_dictee(self, reponse_vocale="Mode dictée activé."):
        self.mode_actuel = MODE_DICTEE
        self.historique_blocs_dictee.clear()
        self.premier_bloc_dictee = True
        if self.hud:
            self.hud.effacer_contenu()
        dire_vocal(reponse_vocale)
        print("[Mode Dictée] ACTIF (Talkie-walkie HOTAS. Ordres : Stop | Corriger | Effacer | Envoi / Envoyer le message)")

    def activer_epellation(self, reponse_vocale="Mode épellation activé."):
        self.mode_actuel = MODE_EPELLATION
        self.buffer_epellation = ""
        if self.hud:
            self.hud.effacer_contenu()
        dire_vocal(reponse_vocale)
        print("[Mode Épellation] ACTIF (Talkie-walkie HOTAS. Ordres : Stop | Corriger | Effacer | Envoi / Valider)")

    def quitter_vers_normal(self, message_vocal="Retour au mode commande."):
        self.mode_actuel = MODE_NORMAL
        self.historique_blocs_dictee.clear()
        self.premier_bloc_dictee = True
        self.buffer_epellation = ""
        dire_vocal(message_vocal)

    def traiter_segment_dictee(self, seg_brut: str):
        """Injecte le texte dicté ou exécute un ordre de commande vocale du mode dictée."""
        time.sleep(0.06)
        relacher_modificateurs()
        cmd = normaliser_texte(seg_brut).strip()
        cmd_propre = re.sub(r'[«»"\'.,!?]', '', cmd).strip().lower()

        val_dictee = set(COMMANDES_MODES.get("validation_dictee", [])) | {
            "envoi", "envoyer", "envoie", "envoi et fin", "envoyer le message",
            "envoi du message", "poster le message", "valider le message",
            "expédier", "expedier", "valider", "valide", "poster"
        }
        corr_dictee = set(COMMANDES_MODES.get("correction_dictee", []))
        eff_dictee = set(COMMANDES_MODES.get("effacer_dictee", []))
        paragraphe_dictee = set(COMMANDES_MODES.get("paragraphe_dictee", [])) | {
            "paragraphe suivant", "paragraph suivant", "nouveau paragraphe",
            "a la ligne", "à la ligne", "nouvelle ligne", "ligne suivante"
        }

        # 1. Sortie du mode
        if cmd_propre in COMMANDES_SORTIE:
            self.quitter_vers_normal("Retour au mode commande.")
            print("[Mode Dictée] Quitté. Retour au mode commande.")
            return

        # 2. Validation / Envoi (Entrée via SendInput + retour mode commande)
        if cmd_propre in val_dictee:
            appuyer_touche_vk(VK_RETURN, 1)
            self.quitter_vers_normal("Retour au mode commande.")
            print("[Mode Dictée] Message validé. Retour au mode commande.")
            return

        # 3. Correction du dernier bloc injecté
        if cmd_propre in corr_dictee:
            if self.historique_blocs_dictee:
                dernier_texte = self.historique_blocs_dictee.pop()
                effacer_dernier_bloc_exact(len(dernier_texte))
                if not self.historique_blocs_dictee:
                    self.premier_bloc_dictee = True
                self._maj_hud_dictee()
                print(f"[Mode Dictée] Dernier bloc supprimé ({len(dernier_texte)} car.) : '{dernier_texte}'")
            else:
                print("[Mode Dictée] Aucun bloc à corriger.")
            return

        # 4. Effacer tout le texte
        if cmd_propre in eff_dictee:
            envoyer_raccourci_ctrl(VK_A)
            appuyer_touche_vk(VK_DELETE, 1)
            self.historique_blocs_dictee.clear()
            self.premier_bloc_dictee = True
            self._maj_hud_dictee()
            print("[Mode Dictée] Tout le texte a été effacé.")
            return

        # 5. Saut de ligne / Paragraphe (commande isolée)
        if cmd_propre in paragraphe_dictee:
            appuyer_touche_vk(VK_RETURN, 1)
            self.historique_blocs_dictee.append("\n")
            self.premier_bloc_dictee = True
            self._maj_hud_dictee()
            print("[Mode Dictée] Paragraphe suivant.")
            return

        # Détection d'un saut de ligne en fin de phrase dictée (ex: "...sera bon. Paragraphe suivant.")
        match_saut_fin = REGEX_SAUT_LIGNE_FIN.search(seg_brut)
        texte_source = seg_brut
        doit_sauter_ligne_apres = False
        if match_saut_fin:
            texte_avant = REGEX_SAUT_LIGNE_FIN.sub('', seg_brut).strip()
            if texte_avant:
                texte_source = texte_avant
                doit_sauter_ligne_apres = True
            else:
                appuyer_touche_vk(VK_RETURN, 1)
                self.historique_blocs_dictee.append("\n")
                self.premier_bloc_dictee = True
                self._maj_hud_dictee()
                print("[Mode Dictée] Paragraphe suivant.")
                return

        # 6. Texte dicté normal
        texte_propre = formater_ponctuation_dictee(texte_source)

        # Gestion propre de l'espacement initial
        if not self.premier_bloc_dictee:
            dernier_a_espace = bool(self.historique_blocs_dictee and self.historique_blocs_dictee[-1].endswith((" ", "\n")))
            if not dernier_a_espace and not texte_propre.startswith(("\n", ".", ",", "!", "?", ";", ":")):
                texte_propre = " " + texte_propre

        # Espacement automatique après ponctuation finale si pas de saut de ligne immédiat
        if not doit_sauter_ligne_apres and texte_propre.endswith((".", "!", "?", ",")):
            texte_propre += " "

        coller_texte_via_presse_papier(texte_propre)
        self.historique_blocs_dictee.append(texte_propre)
        self.premier_bloc_dictee = False
        print(f"[Dictée -> Écrit] {texte_propre}")

        # Exécution du saut de ligne si demandé en fin de phrase
        if doit_sauter_ligne_apres:
            time.sleep(0.04)
            appuyer_touche_vk(VK_RETURN, 1)
            self.historique_blocs_dictee.append("\n")
            self.premier_bloc_dictee = True
            print("[Mode Dictée] Paragraphe suivant (enchaîné).")

        self._maj_hud_dictee()

    def traiter_segment_epellation(self, seg_brut: str):
        """Épelle les lettres/chiffres dans le champ de recherche ou exécute un ordre vocal."""
        time.sleep(0.06)
        relacher_modificateurs()
        cmd = normaliser_texte(seg_brut).strip()
        cmd_propre = re.sub(r'[«»"\'.,!?]', '', cmd).strip().lower()

        val_epel = set(COMMANDES_MODES.get("validation_epellation", [])) | {
            "envoi", "envoyer", "envoie", "valider", "valide",
            "envoyer le message", "valider le message", "expédier", "expedier"
        }
        corr_epel = set(COMMANDES_MODES.get("correction_epellation", []))
        eff_epel = set(COMMANDES_MODES.get("effacer_epellation", []))

        # 1. Sortie du mode
        if cmd_propre in COMMANDES_SORTIE:
            self.quitter_vers_normal("Retour au mode commande.")
            print("[Mode Épellation] Quitté. Retour au mode commande.")
            return

        # 2. Validation / Envoi
        if cmd_propre in val_epel:
            appuyer_touche_vk(VK_RETURN, 1)
            self.quitter_vers_normal("Retour au mode commande.")
            print("[Mode Épellation] Validé. Retour au mode commande.")
            return

        # 3. Corrections rapides (par mot, multiple X lettres, ou simple)
        nombres_fr = {
            "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5,
            "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10
        }

        # 3a. Correction de mot ("corriger mot", "effacer mot", "efface mot")
        if re.search(r'\b(?:corriger|effacer|efface)\s+(?:le\s+)?mot\b', cmd_propre):
            envoyer_raccourci_ctrl(VK_BACK)
            self.buffer_epellation = re.sub(r'\s*\S+\s*$', '', self.buffer_epellation)
            self._maj_hud_epellation()
            print("[Épellation] Mot précédent effacé (Ctrl+Retour arrière).")
            return

        # 3b. Correction multiple ("corriger 3", "effacer 4 lettres", "corriger deux", etc.)
        match_mult = re.search(
            r'\b(?:corriger|effacer|efface)\s+(\d+|un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix)(?:\s+(?:lettres?|caract[eè]res?|chiffres?))?\b',
            cmd_propre
        )
        if match_mult:
            val_str = match_mult.group(1).lower()
            nb_fois = int(val_str) if val_str.isdigit() else nombres_fr.get(val_str, 1)
            nb_fois = min(max(nb_fois, 1), 20)
            appuyer_touche_vk(VK_BACK, nb_fois)
            self.buffer_epellation = self.buffer_epellation[:-nb_fois] if nb_fois < len(self.buffer_epellation) else ""
            self._maj_hud_epellation()
            print(f"[Épellation] Correction multiple : {nb_fois} caractères effacés.")
            return

        # 3c. Correction simple d'un caractère ("corriger", "retour", "effacer lettre")
        if cmd_propre in corr_epel:
            appuyer_touche_vk(VK_BACK, 1)
            self.buffer_epellation = self.buffer_epellation[:-1]
            self._maj_hud_epellation()
            print("[Épellation] Dernier caractère effacé.")
            return

        # 4. Effacer tout le champ
        if cmd_propre in eff_epel:
            envoyer_raccourci_ctrl(VK_A)
            appuyer_touche_vk(VK_DELETE, 1)
            self.buffer_epellation = ""
            self._maj_hud_epellation()
            print("[Épellation] Champ effacé.")
            return

        # 5. RÈGLE DU SEGMENT ISOLÉ TIRET (-)
        mots_tiret_isole = {"tiret", "tirer", "tirez", "trait dunion", "trait d'union", "moins", "-"}
        if cmd_propre in mots_tiret_isole or seg_brut.strip() == "-":
            taper_caractere_unicode("-")
            self.buffer_epellation += "-"
            self._maj_hud_epellation()
            print("[Épellation -> Tapé] -")
            return

        # 6. RÈGLE DU SEGMENT ISOLÉ POINT (.)
        mots_point_isole = {"point", "."}
        if cmd_propre in mots_point_isole or seg_brut.strip() == ".":
            taper_caractere_unicode(".")
            self.buffer_epellation += "."
            self._maj_hud_epellation()
            print("[Épellation -> Tapé] .")
            return

        # 7. RÈGLE DU SEGMENT ISOLÉ ESPACE
        if cmd_propre in {"espace", "espace."}:
            taper_caractere_unicode(" ")
            self.buffer_epellation += " "
            self._maj_hud_epellation()
            print("[Épellation -> Tapé] [Espace]")
            return

        # 8. TOUS LES AUTRES CAS : ÉPELLATION DE LETTRES ET CHIFFRES
        # A. Suppression systématique de TOUS les tirets parasites générés par Whisper (ex: "S-Y-N-U-E-F-E" -> "SYNUEFE", "B-025" -> "B025")
        t_travail = seg_brut.replace("-", "")

        # B. Conservation du point '.' s'il est situé ENTRE deux lettres ou chiffres (ex: "C012.3", "C23.SA")
        t_travail = re.sub(r'([A-Za-z0-9])\.([A-Za-z0-9])', r'\1 tokenpoint \2', t_travail)

        # C. Suppression de tous les points '.' et virgules ',' finaux ou isolés (ex: "B025." -> "B025")
        t_travail = t_travail.replace(".", " ").replace(",", " ")

        # D. Protection des mots oraux d'underscore (_)
        t_travail = re.sub(r"\btiret\s+(?:du\s+)?bas\b", " tokenunderscore ", t_travail, flags=re.IGNORECASE)
        t_travail = re.sub(r"\bsoulign[ée]\b", " tokenunderscore ", t_travail, flags=re.IGNORECASE)
        t_travail = re.sub(r"_", " tokenunderscore ", t_travail)

        # E. Éclatement des blocs alphanumériques mixtes (ex: "C025" -> "C 0 2 5", "B025" -> "B 0 2 5", "C23" -> "C 2 3")
        t_travail = re.sub(r'\b(?=[A-Za-z0-9]*[A-Za-z])(?=[A-Za-z0-9]*[0-9])[A-Za-z0-9]{2,12}\b', lambda m: ' '.join(list(m.group(0))), t_travail)

        # F. Éclatement des blocs de majuscules pures collées (ex: "SYNUEFE" -> "S Y N U E F E", "BOY" -> "B O Y")
        t_travail = re.sub(r'\b([A-Z]{2,20})\b', lambda m: ' '.join(list(m.group(1))), t_travail)

        # G. Prise en charge de la tournure "Lettre X" (ex: "Lettre P", "Lettre B", "Lettre O")
        t_travail = re.sub(r"\blettre\s+([a-zA-Z])\b", r" \1 ", t_travail, flags=re.IGNORECASE)
        t_travail = re.sub(r"\blettre\s+", " ", t_travail, flags=re.IGNORECASE)

        # H. Nettoyage de la ponctuation résiduelle automatique de Whisper
        t_travail = re.sub(r'[«»"\'!?]', ' ', t_travail)

        # Découpage en tokens
        mots = [m for m in re.split(r"\s+", t_travail) if m]

        # Table phonétique fusionnée OTAN + Français (sans Oscar, uniquement Olivier pour O)
        table_phonetique = {
            # Symboles garantis
            "tokentiret": "-", "tiret": "-", "tirer": "-", "tirez": "-", "trait_union": "-", "moins": "-",
            "tokenpoint": ".", "point": ".", "mot_point": ".",
            "tokenunderscore": "_", "underscore": "_", "tiret_bas": "_", "souligne": "_", "souligné": "_",
            "espace": " ", "virgule": ",", "diese": "#", "dièse": "#", "slash": "/",
            # Alphabet Français + OTAN (A à Z)
            "antoine": "A", "anatole": "A", "alpha": "A", "alfa": "A",
            "bernard": "B", "berthe": "B", "bravo": "B", "bé": "B", "be": "B", "bo": "B",
            "charles": "C", "celestine": "C", "célestine": "C", "charlie": "C", "cé": "C", "ce": "C",
            "denis": "D", "desire": "D", "désiré": "D", "delta": "D", "dé": "D", "de": "D",
            "emile": "E", "émile": "E", "eugene": "E", "eugène": "E", "echo": "E", "écho": "E",
            "francois": "F", "françois": "F", "fernand": "F", "foxtrot": "F", "effe": "F",
            "gaston": "G", "georges": "G", "golf": "G", "gé": "G", "ge": "G",
            "henri": "H", "henry": "H", "hotel": "H", "hôtel": "H", "hache": "H",
            "irma": "I", "isidore": "I", "india": "I",
            "jules": "J", "joseph": "J", "juliett": "J", "juliet": "J", "juliette": "J", "ji": "J",
            "kleber": "K", "kléber": "K", "kilo": "K", "ka": "K",
            "louis": "L", "lucien": "L", "lima": "L", "elle": "L",
            "marcel": "M", "maurice": "M", "mike": "M", "emme": "M",
            "nicolas": "N", "noemie": "N", "noémie": "N", "november": "N", "enne": "N",
            # SÉCURITÉ O : Uniquement Olivier (ou lettre O). Pas d'Oscar pour éviter VoiceAttack.
            "olivier": "O", "octave": "O", "odile": "O",
            "paul": "P", "pierre": "P", "papa": "P", "pé": "P", "pe": "P",
            "quentin": "Q", "quebec": "Q", "québec": "Q",
            "rene": "R", "rené": "R", "robert": "R", "romeo": "R", "roméo": "R", "erre": "R", "ér": "R",
            "suzanne": "S", "simon": "S", "sierra": "S", "esse": "S",
            "therese": "T", "thérèse": "T", "thomas": "T", "tango": "T", "té": "T", "te": "T",
            "ursule": "U", "urbain": "U", "uniform": "U",
            "victor": "V", "vincent": "V", "vé": "V", "ve": "V",
            "william": "W", "whiskey": "W", "whisky": "W", "double vé": "W",
            "xavier": "X", "x-ray": "X", "xray": "X", "ixe": "X",
            "yvonne": "Y", "yves": "Y", "yankee": "Y", "i grec": "Y", "igrec": "Y",
            "zoe": "Z", "zoé": "Z", "zulu": "Z", "zoulou": "Z", "zède": "Z", "zede": "Z",
            # Chiffres
            "zero": "0", "zéro": "0", "un": "1", "une": "1", "deux": "2", "trois": "3",
            "quatre": "4", "cinq": "5", "six": "6", "sept": "7", "huit": "8", "neuf": "9", "dix": "10"
        }

        # Fusion avec la configuration utilisateur
        table_complete = {**table_phonetique, **{k: v for k, v in ALPHABET_PHONETIQUE.items() if k.lower() != "oscar"}}

        caracteres_tapes = ""
        for mot in mots:
            mot_min = mot.lower()
            mot_norm = normaliser_texte(mot_min)

            if mot_min in table_complete:
                car = table_complete[mot_min]
                taper_caractere_unicode(car)
                caracteres_tapes += car
            elif mot_norm in table_complete:
                car = table_complete[mot_norm]
                taper_caractere_unicode(car)
                caracteres_tapes += car
            elif len(mot) == 1 and mot.isalnum():
                car = mot.upper()
                taper_caractere_unicode(car)
                caracteres_tapes += car
            elif mot.isdigit():
                for ch in mot:
                    taper_caractere_unicode(ch)
                    caracteres_tapes += ch

        if caracteres_tapes:
            self.buffer_epellation += caracteres_tapes
            self._maj_hud_epellation()
            print(f"[Épellation -> Tapé] {caracteres_tapes}")
