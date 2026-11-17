"""Module de simulation clavier DirectX, raccourcis et gestion du presse-papiers sous Windows."""

import ctypes
from ctypes import wintypes
import time
import subprocess
import win32clipboard
import win32con

from modules.config_loader import DELAIS_CLAVIER

user32 = ctypes.windll.user32

# Codes touches virtuelles Windows
VK_BACK = 0x08
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12       # Touche Alt
VK_DELETE = 0x2E
VK_LEFT = 0x25
VK_A = 0x41
VK_V = 0x56

# Touches spécifiques pour contrôle des modificateurs
VK_LSHIFT = 0xA0
VK_RSHIFT = 0xA1
VK_LCONTROL = 0xA2
VK_RCONTROL = 0xA3

# Drapeaux SendInput
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

# ==============================================================================
# STRUCTURES CTYPES WIN32 COMPATIBLES X64 (EXACTEMENT 40 OCTETS POUR INPUT)
# ==============================================================================
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t)
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t)
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD)
    ]


class _INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT)
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", _INPUT_UNION)
    ]


# Validation formelle du dimensionnement x64
assert ctypes.sizeof(INPUT) == 40, f"Erreur critique de dimensionnement INPUT x64: {ctypes.sizeof(INPUT)} != 40"

user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT


def verifier_et_fermer_menu_windows():
    """Fonction de compatibilité (inactive car Alt n'est plus sollicité)."""
    pass


def relacher_modificateurs(attente_max: float = 0.2):
    """Attend le relâchement physique de Ctrl et Shift et force leur KEYUP si nécessaire."""
    t_start = time.time()
    # 1. Attente que l'utilisateur ou VoiceAttack relâche physiquement Ctrl et Shift
    while (user32.GetAsyncKeyState(VK_CONTROL) & 0x8000 or user32.GetAsyncKeyState(VK_SHIFT) & 0x8000) and (time.time() - t_start < attente_max):
        time.sleep(0.01)

    # 2. Relâchement forcé au cas où Windows garderait l'état logique pressé
    touches_mod = [
        VK_LCONTROL, VK_RCONTROL, VK_CONTROL,
        VK_LSHIFT, VK_RSHIFT, VK_SHIFT
    ]
    for vk in touches_mod:
        if user32.GetAsyncKeyState(vk) & 0x8000:
            sc = user32.MapVirtualKeyW(vk, 0)
            inp_up = INPUT(type=1, union=_INPUT_UNION(ki=KEYBDINPUT(vk, sc, KEYEVENTF_KEYUP, 0, 0)))
            user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(INPUT))
    time.sleep(0.01)


def appuyer_touche_vk(vk, nb_fois=1):
    """Envoie une frappe matérielle via SendInput compatible DirectX / Elite Dangerous et Windows GUI."""
    sc = user32.MapVirtualKeyW(vk, 0)
    flags_down = 0
    flags_up = KEYEVENTF_KEYUP
    if vk in (VK_DELETE, VK_LEFT):
        flags_down |= KEYEVENTF_EXTENDEDKEY
        flags_up |= KEYEVENTF_EXTENDEDKEY

    t_down = DELAIS_CLAVIER.get("delai_frappe_down", 0.025)
    t_up = DELAIS_CLAVIER.get("delai_frappe_up", 0.015)

    for _ in range(nb_fois):
        inp_down = INPUT(type=1, union=_INPUT_UNION(ki=KEYBDINPUT(vk, sc, flags_down, 0, 0)))
        inp_up = INPUT(type=1, union=_INPUT_UNION(ki=KEYBDINPUT(vk, sc, flags_up, 0, 0)))
        user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(INPUT))
        time.sleep(t_down)
        user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(INPUT))
        time.sleep(t_up)


def envoyer_raccourci_ctrl(vk):
    """Envoie une combinaison Ctrl + Touche via SendInput compatible DirectX et Windows GUI."""
    sc_ctrl = user32.MapVirtualKeyW(VK_CONTROL, 0)
    sc_key = user32.MapVirtualKeyW(vk, 0)
    t_ctrl = DELAIS_CLAVIER.get("delai_ctrl_combinaison", 0.035)
    t_down = DELAIS_CLAVIER.get("delai_frappe_down", 0.025)

    inp_ctrl_down = INPUT(type=1, union=_INPUT_UNION(ki=KEYBDINPUT(VK_CONTROL, sc_ctrl, 0, 0, 0)))
    inp_key_down = INPUT(type=1, union=_INPUT_UNION(ki=KEYBDINPUT(vk, sc_key, 0, 0, 0)))
    inp_key_up = INPUT(type=1, union=_INPUT_UNION(ki=KEYBDINPUT(vk, sc_key, KEYEVENTF_KEYUP, 0, 0)))
    inp_ctrl_up = INPUT(type=1, union=_INPUT_UNION(ki=KEYBDINPUT(VK_CONTROL, sc_ctrl, KEYEVENTF_KEYUP, 0, 0)))

    user32.SendInput(1, ctypes.byref(inp_ctrl_down), ctypes.sizeof(INPUT))
    time.sleep(t_down)
    user32.SendInput(1, ctypes.byref(inp_key_down), ctypes.sizeof(INPUT))
    time.sleep(t_ctrl)
    user32.SendInput(1, ctypes.byref(inp_key_up), ctypes.sizeof(INPUT))
    time.sleep(t_down)
    user32.SendInput(1, ctypes.byref(inp_ctrl_up), ctypes.sizeof(INPUT))
    time.sleep(t_down)


def taper_caractere_unicode(car):
    """Injecte un caractère Unicode directement via SendInput (indépendant du layout AZERTY/QWERTY et de Shift)."""
    code_point = ord(car)
    inp_down = INPUT(type=1, union=_INPUT_UNION(ki=KEYBDINPUT(0, code_point, KEYEVENTF_UNICODE, 0, 0)))
    inp_up = INPUT(type=1, union=_INPUT_UNION(ki=KEYBDINPUT(0, code_point, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, 0)))
    t_down = DELAIS_CLAVIER.get("delai_frappe_down", 0.025)
    t_up = DELAIS_CLAVIER.get("delai_frappe_up", 0.015)

    user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(INPUT))
    time.sleep(t_down)
    user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(INPUT))
    time.sleep(t_up)


def coller_texte_via_presse_papier(texte):
    """Copie le texte dans le presse-papiers Windows en mémoire et simule Ctrl+V."""
    if not texte:
        return
    try:
        t_ptt = DELAIS_CLAVIER.get("delai_apres_ptt_relachement", 0.06)
        t_clip = DELAIS_CLAVIER.get("delai_clipboard_injection", 0.04)
        time.sleep(t_ptt)
        relacher_modificateurs()
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, texte)
        finally:
            win32clipboard.CloseClipboard()
        time.sleep(t_clip)
        envoyer_raccourci_ctrl(VK_V)
        time.sleep(t_clip)
    except Exception as e:
        print(f"[Presse-papiers] Erreur injection : {e}")


def effacer_dernier_bloc_exact(nb_caracteres):
    """Efface les nb_caracteres derniers caractères saisis via Backspace matériel SendInput."""
    if nb_caracteres <= 0:
        return
    appuyer_touche_vk(VK_BACK, nb_fois=nb_caracteres)


def copier_presse_papiers(texte):
    """Place une chaîne de caractères dans le presse-papiers Windows (pour navigation / systèmes)."""
    if not texte:
        return
    try:
        subprocess.run(["clip"], input=texte.strip().encode("utf-16le"), check=True)
        print(f"[Presse-papiers] Système copié : {texte.strip()}")
    except Exception as e:
        print(f"[Presse-papiers] Erreur : {e}")


# ==============================================================================
# TEST AUTONOME INTERACTIF (POUR BLOC-NOTES)
# ==============================================================================
if __name__ == "__main__":
    print("\n=== TEST DE SIMULATION CLAVIER DIRECTX & SENDINPUT X64 ===")
    print("Veuillez cliquer dans votre fenêtre Bloc-notes (Notepad) maintenant !")
    print("Démarrage de l'injection dans 3 secondes...")
    for i in range(3, 0, -1):
        print(f"  [{i}]...")
        time.sleep(1)

    print("\n[1/3] Injection mode Épellation : 'TEST_EPELLATION'...")
    for ch in "TEST_EPELLATION":
        taper_caractere_unicode(ch)
        time.sleep(0.02)

    print("[2/3] Validation avec la touche Entrée...")
    appuyer_touche_vk(VK_RETURN, 1)
    time.sleep(0.1)

    print("[3/3] Injection mode Dictée (Presse-papiers + Ctrl+V) : 'Test dictée réussi.'...")
    coller_texte_via_presse_papier("Test dictée réussi.")

    print("\n>>> TEST TERMINÉ AVEC SUCCÈS : Vérifiez votre Bloc-notes ! <<<\n")
