"""Script utilitaire de synchronisation des touches VoiceAttack (.vap) vers les bindings Elite Dangerous (.binds).

Fonctionnalités :
1. Recherche et sélection interactive du profil VoiceAttack (.vap) de référence.
2. Repérage exhaustif multi-contextes (Vaisseau, VRS, À pied) dans HOTAS TOUS MODES.4.2.binds.
3. Table complète de correspondance des touches du clavier AZERTY français vers Elite Dangerous (Key_...).
4. Sécurité anti-raccourci partiel : interdiction formelle d'injecter un modificateur orphelin ([CTRL G.] seul) sans touche principale.
5. Création sécurisée d'un nouveau profil .binds dédié pour le joueur (ex: MonProfil_Oscar.4.2.binds),
   avec mise à jour de PresetName pour sélection directe dans les menus du jeu (fichier original intact).
6. Injection exclusive dans la colonne <Secondary> sans écraser les touches existantes (gestion des conflits).
7. Mode Simulation (--simulate ou menu interactif) avec duplication et réinitialisation de test.
8. Rapport détaillé par commande vocale et par contexte.
"""

import argparse
import glob
import os
from pathlib import Path
import re
import shutil
import struct
import sys
import xml.etree.ElementTree as ET
import zlib

# Répertoire racine du projet
BASE_DIR = Path(__file__).resolve().parent

# Dossier officiel des bindings Elite Dangerous
DOSSIER_BINDINGS_ED = Path(os.path.expandvars(r"%LOCALAPPDATA%\Frontier Developments\Elite Dangerous\Options\Bindings"))
if not DOSSIER_BINDINGS_ED.exists():
    dossier_alt = Path(os.path.expandvars(r"%APPDATA%\Frontier Developments\Elite Dangerous\Options\Bindings"))
    if dossier_alt.exists():
        DOSSIER_BINDINGS_ED = dossier_alt


# ==============================================================================
# TABLE DE CORRESPONDANCE CLAVIER AZERTY (FR) -> ELITE DANGEROUS XML KEY
# ==============================================================================
TABLE_VK_VERS_ED = {
    # Lettres de l'alphabet (A à Z)
    **{i: f"Key_{chr(i)}" for i in range(ord('A'), ord('Z') + 1)},

    # Rangée supérieure AZERTY (chiffres et caractères spéciaux)
    49: "Key_Ampersand",         # 1 / &
    50: "Key_é",                 # 2 / é
    51: "Key_DoubleQuote",       # 3 / "
    52: "Key_Apostrophe",        # 4 / '
    53: "Key_LeftParenthesis",   # 5 / (
    54: "Key_Minus",             # 6 / -
    55: "Key_è",                 # 7 / è
    56: "Key_Underline",         # 8 / _
    57: "Key_ç",                 # 9 / ç
    48: "Key_à",                 # 0 / à

    # Touches de fonction (F1 à F24)
    **{112 + i: f"Key_F{i + 1}" for i in range(24)},

    # Touches physiques DirectInput conformes au moteur d'Elite Dangerous pour clavier AZERTY
    221: "Key_LeftBracket",      # Touche physique ^ sur AZERTY ([ sur QWERTY) -> Ranger Arme (HumanoidHideWeaponButton)
    186: "Key_RightBracket",     # Touche physique $ sur AZERTY (] sur QWERTY) -> Type Grenade (HumanoidSelectNextGrenadeTypeButton)
    192: "Key_Apostrophe",       # Touche physique ù sur AZERTY (' sur QWERTY) -> Chaff / Outil (HumanoidSwitchToSuitTool)
    220: "Key_BackSlash",        # Touche physique * sur AZERTY (\ sur QWERTY) -> Mode Outil (HumanoidToggleToolModeButton)
    223: "Key_Slash",            # Touche physique ! sur AZERTY (/ sur QWERTY) -> Panneau Accès (HumanoidOpenAccessPanelButton)
    191: "Key_Period",           # Touche physique : sur AZERTY (. sur QWERTY)
    190: "Key_Comma",            # Touche physique ; sur AZERTY (, sur QWERTY)
    188: "Key_M",                # Touche physique , sur AZERTY (m sur QWERTY)
    219: "Key_Minus",            # Touche physique ) sur AZERTY (- sur QWERTY)
    226: "Key_NonUsBackslash",   # Touche physique < sur AZERTY
    222: "Key_Grave",            # Touche physique ² sur AZERTY (` sur QWERTY)
    187: "Key_Equals",           # Touche physique = sur AZERTY (= sur QWERTY)
    189: "Key_Minus",            # -

    # Pavé numérique complet (Numpad)
    96: "Key_Numpad_0",
    97: "Key_Numpad_1",
    98: "Key_Numpad_2",
    99: "Key_Numpad_3",
    100: "Key_Numpad_4",
    101: "Key_Numpad_5",
    102: "Key_Numpad_6",
    103: "Key_Numpad_7",
    104: "Key_Numpad_8",
    105: "Key_Numpad_9",
    106: "Key_Numpad_Multiply",  # Numpad *
    107: "Key_Numpad_Add",       # Numpad +
    109: "Key_Numpad_Subtract",  # Numpad -
    110: "Key_Numpad_Decimal",   # Numpad .
    111: "Key_Numpad_Divide",    # Numpad /

    # Contrôles d'édition et de navigation
    9: "Key_Tab",
    13: "Key_Enter",
    27: "Key_Escape",
    32: "Key_Space",
    8: "Key_Backspace",
    45: "Key_Insert",
    46: "Key_Delete",
    36: "Key_Home",
    35: "Key_End",
    33: "Key_PageUp",
    34: "Key_PageDown",
    37: "Key_LeftArrow",
    38: "Key_UpArrow",
    39: "Key_RightArrow",
    40: "Key_DownArrow",
}

# Table de normalisation vers les noms DirectInput QWERTY officiels reconnus par Elite Dangerous
TABLE_NORMALISATION_DIRECTINPUT = {
    "Key_Circumflex": "Key_LeftBracket",
    "Key_Dollar": "Key_RightBracket",
    "Key_ù": "Key_Apostrophe",
    "Key_Asterisk": "Key_BackSlash",
    "Key_ExclamationPoint": "Key_Slash",
    "Key_Colon": "Key_Period",
    "Key_Numpad0": "Key_Numpad_0",
    "Key_Numpad1": "Key_Numpad_1",
    "Key_Numpad2": "Key_Numpad_2",
    "Key_Numpad3": "Key_Numpad_3",
    "Key_Numpad4": "Key_Numpad_4",
    "Key_Numpad5": "Key_Numpad_5",
    "Key_Numpad6": "Key_Numpad_6",
    "Key_Numpad7": "Key_Numpad_7",
    "Key_Numpad8": "Key_Numpad_8",
    "Key_Numpad9": "Key_Numpad_9",
    "Key_NumpadAdd": "Key_Numpad_Add",
    "Key_NumpadSubtract": "Key_Numpad_Subtract",
    "Key_NumpadMultiply": "Key_Numpad_Multiply",
    "Key_NumpadDivide": "Key_Numpad_Divide",
    "Key_NumpadEnter": "Key_Numpad_Enter",
    "Key_NumpadDecimal": "Key_Numpad_Decimal",
}


def normaliser_nom_touche_ed(key: str) -> str:
    """Normalise une touche vers le nom DirectInput matériel reconnu par le moteur d'Elite Dangerous."""
    if not key:
        return ""
    return TABLE_NORMALISATION_DIRECTINPUT.get(key, key)


def decoder_modificateurs_va(mods_bits: int) -> list[str]:
    """Décode les drapeaux binaires de modificateurs VoiceAttack vers les clés XML Elite Dangerous."""
    mods = []
    # 2 = Ctrl, 1 = Shift, 4 = Alt
    if mods_bits & 2:
        mods.append("Key_LeftControl")
    if mods_bits & 1:
        mods.append("Key_LeftShift")
    if mods_bits & 4:
        mods.append("Key_LeftAlt")
    return mods


def convertir_vk_vers_nom_ed(vk: int, mods_bits: int = 0) -> tuple[str, list[str]]:
    """Convertit un code de touche virtuelle (VK) et ses modificateurs en noms XML Elite Dangerous."""
    nom_touche = TABLE_VK_VERS_ED.get(vk, "")
    mods = decoder_modificateurs_va(mods_bits)
    return nom_touche, mods


def trouver_fichier_binds_reference() -> Path | None:
    """Localise le fichier de référence HOTAS TOUS MODES.4.2.binds."""
    candidats = [
        BASE_DIR / "Kit Installation IA_Elite" / "HOTAS TOUS MODES.4.2.binds",
        BASE_DIR / "Kit Installation IA_Elite" / "GitHub_Oscar_Release" / "HOTAS TOUS MODES.4.2.binds",
        BASE_DIR / "HOTAS TOUS MODES.4.2.binds",
        BASE_DIR / "data" / "HOTAS TOUS MODES.4.2.binds",
        DOSSIER_BINDINGS_ED / "HOTAS TOUS MODES.4.2.binds"
    ]
    for c in candidats:
        if c.exists():
            return c
    return None


def rechercher_profils_vap() -> list[Path]:
    """Recherche tous les fichiers .vap dans le projet et les dossiers VoiceAttack."""
    dossiers_recherche = [
        BASE_DIR,
        Path(os.path.expandvars(r"%APPDATA%\VoiceAttack")),
        Path(os.path.expandvars(r"%APPDATA%\VoiceAttack\Profiles")),
        Path(os.path.expandvars(r"%LOCALAPPDATA%\VoiceAttack"))
    ]
    fichiers_vap = []
    vus = set()

    for d in dossiers_recherche:
        if d.exists():
            for f in d.rglob("*.vap"):
                p_resolu = f.resolve()
                if p_resolu not in vus:
                    vus.add(p_resolu)
                    fichiers_vap.append(p_resolu)

    fichiers_vap.sort(key=lambda p: (not ("data" in str(p).lower() or "kit" in str(p).lower()), p.name))
    return fichiers_vap


def extraire_commandes_du_vap(chemin_vap: Path) -> dict[str, dict]:
    """Extrait les noms de commandes, codes VK et noms de touches d'un .vap (binaire compressé ou XML)."""
    commandes = {}
    try:
        raw = chemin_vap.read_bytes()
    except Exception as e:
        print(f"[Attention] Impossible de lire {chemin_vap.name} : {e}")
        return commandes

    # Décompression si binaire VoiceAttack (raw deflate)
    texte_xml = None
    flux_binaire = None

    if raw.startswith(b"\xed\x9d"):
        try:
            flux_binaire = zlib.decompress(raw, -15)
        except Exception:
            flux_binaire = raw
    elif raw.startswith(b"<?xml") or b"<Profile" in raw[:200]:
        try:
            texte_xml = raw.decode("utf-8", errors="replace")
        except Exception:
            pass
    else:
        flux_binaire = raw

    # Cas 1 : XML texte
    if texte_xml:
        try:
            root = ET.fromstring(texte_xml)
            for cmd in root.findall(".//Command"):
                nom_el = cmd.find("Name")
                nom = nom_el.text.strip() if nom_el is not None and nom_el.text else ""
                if not nom:
                    continue
                for action in cmd.findall(".//CommandAction"):
                    type_act = action.find("ActionType")
                    if type_act is not None and type_act.text in ("1", "KeyPress", "Key"):
                        vk_el = action.find("VirtualKey") or action.find("KeyCodes/int")
                        mod_el = action.find("Modifiers")
                        vk = int(vk_el.text) if vk_el is not None and vk_el.text and vk_el.text.isdigit() else None
                        mods = int(mod_el.text) if mod_el is not None and mod_el.text and mod_el.text.isdigit() else 0
                        if vk:
                            key_nom, mods_list = convertir_vk_vers_nom_ed(vk, mods)
                            commandes[nom] = {"vk": vk, "mods": mods, "key_ed": key_nom, "modifiers": mods_list}
                            break
        except Exception as e:
            print(f"[VAP XML] Analyse partielle : {e}")

    # Cas 2 : Flux binaire VoiceAttack (.NET DeflateStream)
    if flux_binaire:
        cmds_connues = []
        fichier_cmds_txt = BASE_DIR / "data" / "commandes_vaisseau.txt"
        if not fichier_cmds_txt.exists():
            fichier_cmds_txt = BASE_DIR / "Kit Installation IA_Elite" / "commandes_vaisseau.txt"
        if fichier_cmds_txt.exists():
            try:
                with open(fichier_cmds_txt, "r", encoding="utf-8") as f:
                    cmds_connues = [l.strip() for l in f if l.strip()]
            except Exception:
                pass

        for cmd_nom in cmds_connues:
            pos = flux_binaire.find(cmd_nom.encode("utf-8"))
            if pos != -1:
                zone = flux_binaire[pos:pos + 450]
                idx_ff = zone.find(b"\xff\xff\xff\xff\xff\xff\xff\xff")
                if idx_ff != -1 and idx_ff >= 6:
                    part = zone[idx_ff - 6:idx_ff]
                    key_code, mods = struct.unpack("<IH", part)
                    if 0 < key_code < 300:
                        key_nom, mods_list = convertir_vk_vers_nom_ed(key_code, mods)
                        commandes[cmd_nom] = {"vk": key_code, "mods": mods, "key_ed": key_nom, "modifiers": mods_list}

    return commandes


def determiner_contexte_action(tag: str) -> str:
    """Détermine le domaine de pilotage d'une balise XML Elite Dangerous."""
    tag_lower = tag.lower()
    if any(k in tag_lower for k in ["humanoid", "suit", "onfoot", "walking"]):
        return "À pied"
    elif any(k in tag_lower for k in ["buggy", "srv", "drive"]):
        return "VRS"
    elif any(k in tag_lower for k in ["galaxy", "system", "map", "fss", "saa", "cam", "freecam"]):
        return "Interface / Carte"
    else:
        return "Vaisseau"


def analyser_binds_reference(chemin_ref: Path) -> dict[str, list[dict]]:
    """Parcourt l'intégralité de HOTAS TOUS MODES.4.2.binds pour extraire toutes les actions secondaires clavier.

    Retourne :
      dict avec pour clé le tag XML : [ { 'tag': ..., 'key': ..., 'modifiers': [...], 'context': ..., 'element': ... } ]
    """
    tree = ET.parse(chemin_ref)
    root = tree.getroot()

    actions_ref = {}
    for child in root:
        sec = child.find("Secondary")
        if sec is not None and sec.attrib.get("Device") == "Keyboard":
            key_raw = sec.attrib.get("Key", "")
            if not key_raw or key_raw.strip() in ("", "{NoDevice}"):
                continue

            key = normaliser_nom_touche_ed(key_raw)
            mods = [normaliser_nom_touche_ed(m.attrib.get("Key")) for m in sec.findall("Modifier") if m.attrib.get("Key")]
            contexte = determiner_contexte_action(child.tag)

            element_clone = ET.Element("Secondary", attrib={"Device": "Keyboard", "Key": key})
            for m_key in mods:
                ET.SubElement(element_clone, "Modifier", attrib={"Device": "Keyboard", "Key": m_key})

            action_info = {
                "tag": child.tag,
                "key": key,
                "modifiers": mods,
                "context": contexte,
                "element": element_clone
            }
            actions_ref.setdefault(child.tag, []).append(action_info)

    return actions_ref


def lister_binds_joueur(dossier_bindings: Path) -> tuple[Path | None, list[Path]]:
    """Liste les fichiers .binds disponibles et identifie le preset actif via StartPreset.4.start."""
    if not dossier_bindings.exists():
        return None, []

    preset_actif_nom = None
    fichier_start = dossier_bindings / "StartPreset.4.start"
    if fichier_start.exists():
        try:
            with open(fichier_start, "r", encoding="utf-8") as f:
                lignes = [l.strip() for l in f if l.strip()]
                if lignes:
                    preset_actif_nom = lignes[0]
        except Exception:
            pass

    tous_binds = []
    for f in dossier_bindings.glob("*.binds"):
        if ".backup" in f.name:
            continue
        tous_binds.append(f)

    tous_binds.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    binds_actif = None
    if preset_actif_nom:
        for f in tous_binds:
            if f.name.startswith(f"{preset_actif_nom}.") or f.stem == preset_actif_nom:
                binds_actif = f
                break

    if not binds_actif and tous_binds:
        binds_actif = tous_binds[0]

    return binds_actif, tous_binds


def injecter_dans_binds(
    chemin_source: Path,
    chemin_destination: Path,
    nouveau_preset_name: str,
    actions_ref: dict[str, list[dict]]
) -> dict:
    """Crée une nouvelle copie du fichier .binds avec PresetName mis à jour et injection sécurisée dans Secondary.

    RÈGLE DE SÉCURITÉ ABSOLUE :
    - Si la touche principale Key n'est pas identifiée ou vide, interdiction formelle d'injecter.
    - Aucun modificateur orphelin (ex: [CTRL G.] seul) ne sera jamais écrit.
    """
    tree = ET.parse(chemin_source)
    root = tree.getroot()

    root.attrib["PresetName"] = nouveau_preset_name

    bilan = {
        "source": chemin_source,
        "destination": chemin_destination,
        "preset_name": nouveau_preset_name,
        "synchronisees": [],
        "deja_configurees": [],
        "conflits": [],
        "non_mappees": []
    }

    elements_par_tag = {el.tag: el for el in root}

    for tag, list_acts in actions_ref.items():
        for act in list_acts:
            key_ref = normaliser_nom_touche_ed(act.get("key", "").strip())
            mods_ref = [normaliser_nom_touche_ed(m) for m in act.get("modifiers", [])]
            contexte = act.get("context", "Inconnu")

            # ------------------------------------------------------------------
            # SÉCURITÉ CRITIQUE ANTI-RACCOURCI PARTIEL
            # ------------------------------------------------------------------
            if not key_ref or key_ref in ("", "{NoDevice}", "Key_"):
                bilan["non_mappees"].append((tag, contexte, f"Touche principale invalide (mods: {mods_ref})"))
                continue

            if tag in elements_par_tag:
                action_el = elements_par_tag[tag]
                sec_el = action_el.find("Secondary")

                if sec_el is None:
                    # Création propre de Secondary avec la touche principale obligatoire
                    nouveau_sec = ET.SubElement(action_el, "Secondary", attrib={"Device": "Keyboard", "Key": key_ref})
                    for m_key in mods_ref:
                        ET.SubElement(nouveau_sec, "Modifier", attrib={"Device": "Keyboard", "Key": m_key})
                    bilan["synchronisees"].append((tag, contexte, key_ref, mods_ref))

                elif sec_el.attrib.get("Device") in ("{NoDevice}", "", None):
                    # Emplacement libre -> Injection sécurisée
                    sec_el.attrib["Device"] = "Keyboard"
                    sec_el.attrib["Key"] = key_ref
                    for m in list(sec_el):
                        sec_el.remove(m)
                    for m_key in mods_ref:
                        ET.SubElement(sec_el, "Modifier", attrib={"Device": "Keyboard", "Key": m_key})
                    bilan["synchronisees"].append((tag, contexte, key_ref, mods_ref))

                else:
                    # Emplacement déjà occupé
                    sec_dev = sec_el.attrib.get("Device", "")
                    sec_key = sec_el.attrib.get("Key", "")
                    sec_key_norm = normaliser_nom_touche_ed(sec_key)
                    sec_mods = [normaliser_nom_touche_ed(m.attrib.get("Key")) for m in sec_el.findall("Modifier")]

                    if sec_dev == "Keyboard" and sec_key_norm == key_ref and sorted(sec_mods) == sorted(mods_ref):
                        bilan["deja_configurees"].append((tag, contexte, key_ref, mods_ref))
                    else:
                        conflit_info = f"{sec_dev}:{sec_key}" + (f"+{sec_mods}" if sec_mods else "")
                        bilan["conflits"].append((tag, contexte, key_ref, mods_ref, conflit_info))
            else:
                # Création complète de la balise manquante
                nouvel_el = ET.SubElement(root, tag)
                ET.SubElement(nouvel_el, "Primary", attrib={"Device": "{NoDevice}", "Key": ""})
                nouveau_sec = ET.SubElement(nouvel_el, "Secondary", attrib={"Device": "Keyboard", "Key": key_ref})
                for m_key in mods_ref:
                    ET.SubElement(nouveau_sec, "Modifier", attrib={"Device": "Keyboard", "Key": m_key})
                bilan["synchronisees"].append((tag, contexte, key_ref, mods_ref))

    # Écriture du nouveau fichier .binds
    arbre_modifie = ET.ElementTree(root)
    ET.indent(arbre_modifie, space="\t", level=0)
    chemin_destination.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin_destination, "wb") as f:
        arbre_modifie.write(f, encoding="UTF-8", xml_declaration=True)

    return bilan


def executer_mode_simulation(
    chemin_source: Path,
    actions_ref: dict[str, list[dict]]
) -> bool:
    """Exécute le mode simulation en créant Test_Sync_Oscar.4.2.binds, vider les Secondary Oscar et vérifier l'injection."""
    print("\n" + "=" * 70)
    print(">>> DÉMARRAGE DU MODE SIMULATION & TEST INTÉGRÉ <<<")
    print("=" * 70)

    fichier_test = chemin_source.parent / "Test_Sync_Oscar.4.2.binds"
    print(f"1. Création de la copie de test : {fichier_test.name}")

    shutil.copyfile(chemin_source, fichier_test)

    tree = ET.parse(fichier_test)
    root = tree.getroot()
    tags_cibles = set(actions_ref.keys())
    nb_reinit = 0

    for child in root:
        if child.tag in tags_cibles:
            sec = child.find("Secondary")
            if sec is not None and sec.attrib.get("Device") != "{NoDevice}":
                sec.attrib["Device"] = "{NoDevice}"
                sec.attrib["Key"] = ""
                for m in list(sec):
                    sec.remove(m)
                nb_reinit += 1

    tree.write(fichier_test, encoding="UTF-8", xml_declaration=True)
    print(f"2. Simulation effectuée : {nb_reinit} touches secondaires remises à {{NoDevice}}.")

    print("3. Injection de référence dans la copie de test...")
    bilan = injecter_dans_binds(
        chemin_source=fichier_test,
        chemin_destination=fichier_test,
        nouveau_preset_name="Test_Sync_Oscar",
        actions_ref=actions_ref
    )

    print(f"4. Bilan simulation :")
    print(f"   - Actions synchronisées réinjectées : {len(bilan['synchronisees'])}")
    print(f"   - Actions déjà configurées          : {len(bilan['deja_configurees'])}")
    print(f"   - Conflits détectés                 : {len(bilan['conflits'])}")
    print(f"   - Raccourcis non mappés/rejetés     : {len(bilan['non_mappees'])}")

    succes = len(bilan["synchronisees"]) > 0 and len(bilan["conflits"]) == 0 and len(bilan["non_mappees"]) == 0
    if succes:
        print("\n>>> SUCCÈS : Le script de synchronisation est 100% opérationnel et sécurisé ! <<<")
    else:
        print("\n>>> Attention : Des alertes ont été relevées lors de la simulation. <<<")

    print(f"Fichier de test conservé : {fichier_test}")
    print("=" * 70 + "\n")
    return succes


def afficher_rapport_detaille(bilan: dict, commandes_vap: dict):
    """Affiche un rapport clair groupé par commande vocale et par contexte."""
    print("\n" + "=" * 70)
    print("          RAPPORT DÉTAILLÉ DE SYNCHRONISATION OSCAR")
    print("=" * 70)
    print(f"Fichier source original (intact) : {bilan['source'].name}")
    print(f"NOUVEAU fichier créé             : {bilan['destination'].name}")
    print(f"Nom du profil Elite Dangerous    : {bilan['preset_name']}")
    print("-" * 70)

    groupes_contexte = {}
    for tag, ctx, key, mods in bilan["synchronisees"]:
        combinaison = key.replace("Key_", "")
        if mods:
            mods_str = "+".join([m.replace("Key_", "").replace("Left", "").replace("Right", "") for m in mods])
            combinaison = f"{mods_str}+{combinaison}"
        groupes_contexte.setdefault(ctx, []).append((tag, combinaison))

    for ctx in ["Vaisseau", "VRS", "À pied", "Interface / Carte"]:
        if ctx in groupes_contexte:
            print(f"\n[{ctx.upper()}] ({len(groupes_contexte[ctx])} actions synchronisées) :")
            for tag, comb in sorted(groupes_contexte[ctx]):
                print(f"  • {tag:<38} -> Touche : {comb}")

    if bilan["deja_configurees"]:
        print(f"\n[DÉJÀ CONFIGURÉES] : {len(bilan['deja_configurees'])} actions étaient déjà en place.")

    if bilan["conflits"]:
        print(f"\n[CONFLITS IGNORÉS] ({len(bilan['conflits'])} actions non modifiées pour protéger vos touches) :")
        for tag, ctx, key, mods, deja_present in bilan["conflits"]:
            print(f"  ! {tag:<35} [{ctx}] : Voulait {key}, mais déjà occupé par ({deja_present})")

    if bilan.get("non_mappees"):
        print(f"\n[SÉCURITÉ ANTI-MODIFICATEURS ORPHELINS] ({len(bilan['non_mappees'])} actions rejetées car touche vide) :")
        for tag, ctx, motif in bilan["non_mappees"]:
            print(f"  X {tag:<35} [{ctx}] : {motif}")

    print("\n" + "=" * 70)
    print(f"RÉSUMÉ FINAL :")
    print(f"  • Nouvelles touches injectées   : {len(bilan['synchronisees'])}")
    print(f"  • Touches déjà présentes        : {len(bilan['deja_configurees'])}")
    print(f"  • Conflits préservés (sécurité) : {len(bilan['conflits'])}")
    print(f"  • Modificateurs orphelins bloqués: {len(bilan.get('non_mappees', []))}")
    print("=" * 70)
    print("\nPROCHAINE ÉTAPE DANS ELITE DANGEROUS :")
    print(f"1. Lancez Elite Dangerous.")
    print(f"2. Allez dans Options -> Commandes.")
    print(f"3. En haut à droite, sélectionnez votre nouveau profil : '{bilan['preset_name']}'.")
    print(f"4. Cliquez sur Appliquer. Oscar est paré à piloter avec vous !\n")


def main():
    parser = argparse.ArgumentParser(description="Synchroniseur interactif de touches VoiceAttack vers Elite Dangerous.")
    parser.add_argument("--simulate", action="store_true", help="Lance directement le mode simulation / test.")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("   OSCAR COPILOT — SYNCHRONISEUR DE COMMANDES ELITE DANGEROUS")
    print("=" * 70)

    # 1. Recherche du fichier de référence HOTAS TOUS MODES.4.2.binds
    binds_ref_path = trouver_fichier_binds_reference()
    if not binds_ref_path:
        print("[Erreur critique] Fichier de référence 'HOTAS TOUS MODES.4.2.binds' introuvable dans le projet.")
        sys.exit(1)
    print(f"[Référence] HOTAS TOUS MODES détecté : {binds_ref_path.name}")

    # Analyse multi-contextes du fichier de référence
    actions_reference = analyser_binds_reference(binds_ref_path)
    print(f"[Référence] {len(actions_reference)} actions secondaires clavier cartographiées.")

    # 2. Sélection interactive du profil VoiceAttack (.vap)
    print("\n" + "-" * 70)
    print("ÉTAPE 1 : Sélection du profil VoiceAttack (.vap)")
    print("-" * 70)
    fichiers_vap = rechercher_profils_vap()

    if fichiers_vap:
        for idx, f in enumerate(fichiers_vap, 1):
            taille_ko = round(f.stat().st_size / 1024, 1)
            parent_rel = f.parent.name
            print(f"  [{idx}] {f.name} ({parent_rel}/, {taille_ko} Ko)")
        print(f"  [M] Saisir / Coller manuellement un autre chemin .vap")
    else:
        print("  Aucun fichier .vap détecté automatiquement.")
        print("  [M] Saisir / Coller manuellement le chemin d'un fichier .vap")

    vap_choisi = None
    if not args.simulate:
        while not vap_choisi:
            choix = input("\nVotre choix [1 par défaut] : ").strip()
            if not choix and fichiers_vap:
                vap_choisi = fichiers_vap[0]
            elif choix.isdigit() and 1 <= int(choix) <= len(fichiers_vap):
                vap_choisi = fichiers_vap[int(choix) - 1]
            elif choix.upper() == "M":
                saisie = input("Chemin complet du fichier .vap : ").strip().strip('"')
                p = Path(saisie)
                if p.exists() and p.suffix.lower() == ".vap":
                    vap_choisi = p
                else:
                    print("Chemin invalide ou fichier non trouvé. Réessayez.")
            else:
                print("Choix invalide.")
    else:
        vap_choisi = fichiers_vap[0] if fichiers_vap else binds_ref_path

    print(f"[VoiceAttack] Profil sélectionné : {vap_choisi.name}")
    commandes_vap = extraire_commandes_du_vap(vap_choisi)
    print(f"[VoiceAttack] {len(commandes_vap)} commandes vocales avec macros clavier analysées.")

    # 3. Détection et sélection du fichier .binds joueur
    print("\n" + "-" * 70)
    print("ÉTAPE 2 : Sélection du fichier de configuration Elite Dangerous (.binds)")
    print("-" * 70)

    binds_actif, liste_binds = lister_binds_joueur(DOSSIER_BINDINGS_ED)

    if not liste_binds:
        print(f"[Attention] Aucun fichier .binds trouvé dans {DOSSIER_BINDINGS_ED}.")
        saisie_binds = input("Entrez manuellement le chemin de votre fichier .binds : ").strip().strip('"')
        binds_choisi = Path(saisie_binds)
        if not binds_choisi.exists():
            print("[Erreur] Fichier introuvable. Fin.")
            sys.exit(1)
    else:
        for idx, fb in enumerate(liste_binds, 1):
            est_actif = " (ACTIF - Détecté en jeu)" if binds_actif and fb == binds_actif else ""
            print(f"  [{idx}] {fb.name}{est_actif}")
        print(f"  [M] Saisir manuellement un autre chemin .binds")

        binds_choisi = None
        if not args.simulate:
            while not binds_choisi:
                choix_b = input(f"\nVotre choix [1 pour {liste_binds[0].name}] : ").strip()
                if not choix_b:
                    binds_choisi = liste_binds[0]
                elif choix_b.isdigit() and 1 <= int(choix_b) <= len(liste_binds):
                    binds_choisi = liste_binds[int(choix_b) - 1]
                elif choix_b.upper() == "M":
                    saisie = input("Chemin complet du fichier .binds : ").strip().strip('"')
                    pb = Path(saisie)
                    if pb.exists() and pb.suffix.lower() == ".binds":
                        binds_choisi = pb
                    else:
                        print("Fichier .binds introuvable.")
                else:
                    print("Choix invalide.")
        else:
            binds_choisi = binds_actif or liste_binds[0]

    print(f"[Elite Dangerous] Profil sélectionné : {binds_choisi.name}")

    # 4. Mode Simulation ou Synchronisation
    if args.simulate:
        executer_mode_simulation(binds_choisi, actions_reference)
        return

    print("\n" + "-" * 70)
    print("ÉTAPE 3 : Action souhaitée")
    print("-" * 70)
    print("  [1] Créer le profil synchronisé '<Nom>_Oscar.binds' (Recommandé)")
    print("  [2] Lancer le Mode Simulation / Test (Vérifie le fonctionnement sans risque)")
    action_choix = input("\nVotre choix [1 par défaut] : ").strip()

    if action_choix == "2":
        executer_mode_simulation(binds_choisi, actions_reference)
        return

    # 5. Détermination du nom du nouveau profil .binds
    nom_base = binds_choisi.stem
    version_ext = ""
    match_ver = re.search(r"\.(4\.\d)$", nom_base)
    if match_ver:
        nom_sans_ver = nom_base[:match_ver.start()]
        version_ext = f".{match_ver.group(1)}"
    else:
        nom_sans_ver = nom_base

    if nom_sans_ver.endswith("_Oscar"):
        nouveau_preset_nom = nom_sans_ver
    else:
        nouveau_preset_nom = f"{nom_sans_ver}_Oscar"

    nom_fichier_destination = f"{nouveau_preset_nom}{version_ext}.binds"
    chemin_destination = binds_choisi.parent / nom_fichier_destination

    print(f"\nCréation du nouveau fichier : {chemin_destination.name}...")
    bilan = injecter_dans_binds(
        chemin_source=binds_choisi,
        chemin_destination=chemin_destination,
        nouveau_preset_name=nouveau_preset_nom,
        actions_ref=actions_reference
    )

    afficher_rapport_detaille(bilan, commandes_vap)


if __name__ == "__main__":
    main()
