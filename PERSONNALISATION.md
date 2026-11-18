# ⚙️ Guide de Personnalisation — Copilote Oscar

La majorité des options de personnalisation d'Oscar sont externalisées dans le fichier **`config_oscar.json`** situé à la racine du projet. Vous pouvez ainsi adapter le nom, la personnalité, la voix, les raccourcis et les paramètres de simulation à vos préférences.

---

## 🧭 Sommaire

1. [Changer le nom du Copilote](#1-changer-le-nom-du-copilote)
2. [Modifier la personnalité](#2-modifier-la-personnalité)
3. [Modifier la séquence de touche d'activation interne](#3-modifier-la-séquence-de-touche-dactivation-interne)
4. [Changer la voix de synthèse (Edge-TTS) et la vitesse](#4-changer-la-voix-de-synthèse-edge-tts-et-la-vitesse)
5. [Ajouter de nouveaux vaisseaux d'Elite Dangerous](#5-ajouter-de-nouveaux-vaisseaux-delite-dangerous)
6. [Ajuster les délais de simulation clavier DirectX](#6-ajuster-les-délais-de-simulation-clavier-directx)
7. [Personnaliser le vocabulaire des commandes vocales](#7-personnaliser-le-vocabulaire-des-commandes-vocales)
8. [Ajouter ou modifier des commandes physiques (VoiceAttack)](#8-ajouter-ou-modifier-des-commandes-physiques-voiceattack)

---

## 1. Changer le nom du Copilote

Par défaut, votre copilote s'appelle **Oscar**. Vous pouvez le renommer librement (par exemple *Sophie*, *Astra*, *Jarvis*, *Cortex*).

Dans `config_oscar.json`, modifiez la clé `"nom_ia"` :
~~~json
{
  "nom_ia": "Sophie"
}
~~~
> 💡 **Effet immédiat :** Whisper filtrera automatiquement le nouveau nom quand vous l'interpellez (ex: *« Sophie, quel est l'état du vaisseau ? »*), et l'IA répondra sous cette nouvelle identité.

### ⚠️ Avertissements indispensables en cas de renommage :
1. **Renommer le mot-clé dans VoiceAttack :**  
   Si vous utilisez le mode d'activation Mains Libres, ouvrez votre profil dans **VoiceAttack** et modifiez la commande de réveil qui écoute actuellement *« Oscar »* pour la remplacer par votre nouveau nom (ex: *« Sophie »*).
2. **Éviter les collisions avec le Mode Épellation :**  
   Si votre nouveau nom correspond à un prénom présent dans l'alphabet phonétique de `config_oscar.json` (par exemple *« Sophie »* → S ou *« Victor »* → V), **retirez impérativement ce prénom de la section `"alphabet_phonetique"`** pour éviter que VoiceAttack n'intercepte l'appel pendant que vous épelez un système stellaire.

---

## 2. Modifier la personnalité

La personnalité d'Oscar se règle également dans **`config_oscar.json`**, via la clé `"personnalite_ia"`. Vous pouvez la réécrire selon l'ambiance souhaitée pour votre cockpit.

### Exemples de styles :

#### Style Actuel : Sarcastique & Pince-sans-rire (Oscar par défaut)
~~~text
"Tu es Oscar, l'ordinateur de bord et co-pilote IA d'un vaisseau spatial. Tu as un humour noir, cynique, pince-sans-rire et très sarcastique. Tu adores taquiner le Commandant sur ses talents de pilotage, sa passion obsessionnelle pour les cailloux (le minage), l'exploration ou ses dépenses inutiles, tout en restant ultra-concis (1 à 2 phrases maximum). Ne donne jamais de conseils de sécurité ennuyeux."
~~~

#### Variante : Ordinateur de bord militaire strict
~~~text
"Tu es l'ordinateur de bord tactique d'un croiseur spatial de la Fédération. Tu es extrêmement formel, froid, précis et efficace. Tu réponds de manière concise (1 phrase) sans fioritures et avec le jargon militaire adapté."
~~~

#### Variante : Copilote chaleureuse et bienveillante
~~~text
"Tu es Sophie, une copilote attentive, enthousiaste et protectrice. Tu veilles sur la sécurité du Commandant avec chaleur et professionnalisme, tout en restant concise (1 à 2 phrases maximum)."
~~~

> ⚠️ **Consigne impérative à préserver :** Pour conserver le bon fonctionnement des modes Dictée et Épellation, veillez à toujours garder la consigne des balises à la fin de votre texte :
> `... Si le Commandant demande à écrire, dicter du texte ou passer en mode dictée, formule une courte réplique et termine impérativement par [MODE_DICTEE]. S'il demande à épeler ou passer en mode lettre à lettre, termine impérativement par [MODE_EPELLATION]. N'UTILISE JAMAIS de gras (**), de listes à puces ni de numérotation.`

---

## 3. Modifier la séquence de touche d'activation interne

Que vous utilisiez votre bouton HOTAS (`COM_IA_ON` / `COM_IA_OFF`) ou la commande vocale Mains Libres (*« Oscar »* / *« Terminé »*), **VoiceAttack** déclenche l'enregistrement de Whisper en simulant une combinaison de touches clavier interne (par défaut : **`Ctrl + Shift + F9`**).

Si cette combinaison entre en conflit avec l'un de vos autres logiciels (ex: GeForce Experience, Discord, OBS), vous pouvez la modifier en deux étapes :

1. **Dans `config_oscar.json` :**  
   Modifiez la clé `"raccourci_ptt"` (par exemple pour utiliser `ctrl+shift+f10`) :
   ~~~json
   "raccourci_ptt": "ctrl+shift+f10"
   ~~~
   *(Évitez d'utiliser la touche `Alt` dans cette combinaison, car elle peut activer la barre de menus des applications Windows pendant la saisie).*

2. **Dans VoiceAttack (obligatoire pour maintenir la synchronisation) :**  
   Éditez votre profil dans VoiceAttack et mettez à jour l'action clavier dans chacune des commandes de déclenchement :
   - **`COM_IA_ON`** : remplacez l'enfoncement (*Press*) de `Ctrl + Shift + F9` par votre nouvelle combinaison.
   - **`COM_IA_OFF`** : remplacez le relâchement (*Release*) de `Ctrl + Shift + F9` par votre nouvelle combinaison.
   - **`Oscar`** (et **`Terminé`**) : mettez également à jour la combinaison simulée à l'ouverture et à la fermeture de l'écoute Mains Libres.

---

## 4. Changer la voix de synthèse (Edge-TTS) et la vitesse

Oscar utilise les voix neurales haute définition de **Microsoft Edge-TTS**. Vous pouvez sélectionner n'importe quelle voix disponible et régler le débit d'élocution dans `config_oscar.json` :

~~~json
"tts": {
  "voix": "fr-FR-HenriNeural",
  "vitesse": "+8%"
}
~~~

### Principales voix françaises disponibles :

| Nom de la voix | Profil vocal | Recommandé pour |
| :--- | :--- | :--- |
| **`fr-FR-HenriNeural`** | Homme, posé, chaleureux et expressif *(Défaut)* | Oscar (sarcastique, naturel) |
| **`fr-FR-DeniseNeural`** | Femme, claire, posée et professionnelle | IA de bord féminine réaliste |
| **`fr-FR-EloiseNeural`** | Femme, dynamique et moderne | Copilote jeune et vive |
| **`fr-FR-RemyMultilingualNeural`** | Homme, moderne et polyglotte | Copilote scientifique |
| **`fr-CA-JeanNeural`** | Homme, accent québécois naturel | Ambiance personnalisée |
| **`fr-CA-SylvieNeural`** | Femme, accent québécois naturel | Ambiance personnalisée |
| **`fr-BE-GerardNeural`** | Homme, accent belge francophone | Ambiance personnalisée |
| **`fr-CH-FabriceNeural`** | Homme, accent suisse francophone | Ambiance personnalisée |

### Réglage du débit vocal (`vitesse`)
- `"+0%"` : Vitesse standard normale.
- `"+8%"` : Légèrement plus alerte et dynamique *(recommandé)*.
- `"+15%"` : Rythme rapide pour les commandants pressés.
- `"-5%"` : Élocution plus lente et solennelle.

---

## 5. Ajouter de nouveaux vaisseaux d'Elite Dangerous

Frontier Developments ajoute régulièrement de nouveaux vaisseaux (ex: *Python Mk II*, *Mandalay*, *Caspian Explorer*, *Cobra Mk V*...).

Le dictionnaire `"noms_vaisseaux"` fait correspondre le code technique interne renvoyé par les journaux du jeu avec son appellation officielle lisible :

~~~json
"noms_vaisseaux": {
  "mandalay": "Mandalay",
  "python_nx": "Python Mk II",
  "explorer_nx": "Caspian Explorer",
  "cobramkv": "Cobra Mk V",
  "votre_nouveau_code": "Nom Officiel du Vaisseau"
}
~~~

### Comment trouver le code interne d'un nouveau vaisseau ?
1. Montez à bord du nouveau vaisseau en jeu.
2. Ouvrez le dernier fichier `Journal.*.log` situé dans `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous`.
3. Recherchez l'événement `"event":"Loadout"` ou `"event":"LoadGame"`.
4. Repérez la valeur du champ `"Ship"` (ex: `"Ship":"explorer_nx"`).
5. Ajoutez simplement la ligne correspondante dans `config_oscar.json` en minuscules :
   `"explorer_nx": "Caspian Explorer"`

---

## 6. Ajuster les délais de simulation clavier DirectX

Si vous jouez sur une configuration avec une fréquence d'images (FPS) variable ou sur un écran avec V-Sync élevé, vous pouvez ajuster les temporisations matérielles dans la section `"delais_clavier"` :

~~~json
"delais_clavier": {
  "delai_apres_ptt_relachement": 0.06,
  "delai_frappe_down": 0.025,
  "delai_frappe_up": 0.015,
  "delai_ctrl_combinaison": 0.035,
  "delai_clipboard_injection": 0.04
}
~~~

- **`delai_apres_ptt_relachement` (0.06s) :** Délai d'attente après le relâchement physique du bouton Push-To-Talk avant d'injecter du texte (laisse à Windows le temps de libérer Ctrl/Shift).
- **`delai_frappe_down` (0.025s) / `delai_frappe_up` (0.015s) :** Durée d'enfoncement et de relâchement des touches matérielles (Backspace, Entrée, etc.). Une valeur trop courte (< 0.01s) pourrait être manquée par le moteur DirectX du jeu.
- **`delai_clipboard_injection` (0.04s) :** Temps de stabilisation de la mémoire tampon Windows lors d'un collage `Ctrl + V`.

---

## 7. Personnaliser le vocabulaire des commandes vocales

Dans la section `"commandes_modes"`, vous pouvez ajouter vos propres synonymes préférés pour piloter les modes :

- **`validation_dictee` :** Mots-clés pour envoyer et quitter le mode dictée (ex: ajoutez `"transmission"`, `"publier"`).
- **`correction_dictee` :** Mots-clés pour corriger le dernier bloc (ex: `"oups"`, `"gommer"`).
- **`paragraphe_dictee` :** Mots-clés pour sauter une ligne (ex: `"retour chariot"`, `"saut"`).
- **`commandes_sortie` :** Mots-clés d'annulation universelle (ex: `"rompez"`, `"stop là"`).
- **`alphabet_phonetique` :** Vous pouvez y ajouter des prénoms ou termes personnalisés pour l'épellation (ex: `"darko": "D"`, `"barbare": "B"`).

---

## 8. Ajouter ou modifier des commandes physiques (VoiceAttack)

Vous pouvez enrichir ou adapter à volonté le catalogue des commandes physiques du vaisseau *(reportez-vous au **[Tableau Récapitulatif Complet des Commandes (TABLEAU_COMMANDES.md)](TABLEAU_COMMANDES.md)** pour inspecter la matrice complète des 121 macros existantes, de leurs raccourcis clavier et de leurs balises XML correspondantes)*.

### 🚨 La Règle d'Or : Identité Syntaxique Absolue
Le nom d'une commande dans **`data/commandes_vaisseau.txt`** doit être **STRICTEMENT IDENTIQUE** (au caractère près : majuscules, accents, espaces, tirets) au nom de la macro correspondante dans votre profil **VoiceAttack**.

**Pourquoi ?**
Lorsqu'un ordre est reconnu, GPT-4o-mini pioche le nom exact dans `commandes_vaisseau.txt` et produit la balise `[EXECUTE:Nom_De_La_Commande]`. Le script Python transmet ensuite cet ordre directement à VoiceAttack via la ligne de commande :
~~~cmd
VoiceAttack.exe -command "Nom_De_La_Commande"
~~~
Si le moindre accent, majuscule ou espace diffère entre `commandes_vaisseau.txt` et VoiceAttack, VoiceAttack ignorera l'ordre !

---

### Procédure pas-à-pas pour ajouter une nouvelle commande :
1. **Dans VoiceAttack :**  
   Créez votre nouvelle macro (ex: `Lancer Sonde Reconnaissance`) et associez-lui un raccourci clavier (ex: `Ctrl + Alt + K`).
2. **Dans Elite Dangerous (Bindings) :**  
   Dans les options de commandes du jeu, assignez ce même raccourci (`Ctrl + Alt + K`) dans la colonne **Secondaire** (`<Secondary>`) de l'action souhaitée.
3. **Dans `data/commandes_vaisseau.txt` :**  
   Ajoutez simplement une nouvelle ligne contenant le nom exact de la commande :
   ~~~text
   Lancer Sonde Reconnaissance
   ~~~
4. **Relancez Oscar (`IA_Elite.bat`) :**  
   Au démarrage, Oscar charge automatiquement la liste actualisée. Vous pouvez désormais lui demander à la voix : *« Oscar, balance une sonde »* ou *« Lance la reconnaissance »*, et il déclenchera fidèlement votre macro !

---

### Procédure pas-à-pas pour modifier une commande existante :
1. **Changer uniquement le raccourci clavier d'une commande (sans changer son nom) :**  
   - Repérez la commande dans le tableau de correspondance et modifiez le raccourci clavier simulé dans **VoiceAttack**.
   - Reportez ce même raccourci dans la colonne **Secondaire** (`<Secondary>`) de l'action correspondante dans **Elite Dangerous** (ou relancez `py sync_binds.py` après avoir exporté votre profil `.vap` mis à jour).
   - Aucune modification n'est nécessaire dans `data/commandes_vaisseau.txt`.
2. **Renommer une commande existante (ou la traduire dans une autre langue) :**  
   - Renommez la macro dans **VoiceAttack** (par exemple `Allumer Phares` → `Turn On Lights`).
   - Remplacez exactement l'ancien nom par le nouveau dans **`data/commandes_vaisseau.txt`**, puis relancez `IA_Elite.bat`.

---

# ⚙️ Customization Guide — Oscar AI Copilot

Most of Oscar's customization options are externalized in the **`config_oscar.json`** file located at the root of the project. You can tailor the copilot's name, personality, voice, internal shortcuts, and language settings without touching a single line of Python code.

---

## 🧭 Table of Contents

1. [Changing the Copilot's Name](#1-changing-the-copilots-name)
2. [Modifying the Personality](#2-modifying-the-personality)
3. [Changing the Internal Activation Shortcut](#3-changing-the-internal-activation-shortcut)
4. [Changing the Synthesis Voice (Edge-TTS) & Speech Rate](#4-changing-the-synthesis-voice-edge-tts--speech-rate)
5. [Adding New Elite Dangerous Ships](#5-adding-new-elite-dangerous-ships)
6. [Adjusting DirectX Keyboard Simulation Delays](#6-adjusting-directx-keyboard-simulation-delays)
7. [Customizing Voice Mode Keywords](#7-customizing-voice-mode-keywords)
8. [Adding or Modifying Physical Commands (VoiceAttack)](#8-adding-or-modifying-physical-commands-voiceattack)
9. [Switching Oscar Completely to English](#9-switching-oscar-completely-to-english)

---

## 1. Changing the Copilot's Name

By default, your copilot is named **Oscar**. You can freely rename it (e.g., *Sophie*, *Astra*, *Jarvis*, *Cortex*).

In `config_oscar.json`, edit the `"nom_ia"` key:
~~~json
{
  "nom_ia": "Jarvis"
}
~~~
> 💡 **Immediate Effect:** Whisper automatically filters out the new name when you address it (e.g., *"Jarvis, what is the ship status?"*), and the AI responds under this new identity.

### ⚠️ Mandatory Warnings When Renaming:
1. **Rename the wake word inside VoiceAttack:**  
   If you use Hands-Free voice activation, open your profile in **VoiceAttack** and update the wake command currently listening for *"Oscar"* to your chosen name (e.g., *"Jarvis"*).
2. **Avoid collisions with Spelling Mode:**  
   If your new name matches a word listed in the phonetic alphabet inside `config_oscar.json` (for example *"Juliet"* → J or *"Victor"* → V), **be sure to remove that word from the `"alphabet_phonetique"` section** so VoiceAttack does not intercept your speech while spelling a star system.

---

## 2. Modifying the Personality

Oscar's personality is also configured inside **`config_oscar.json`**, via the `"personnalite_ia"` key. You can rewrite it to match the exact atmosphere you want on your bridge.

### Style Examples:

#### Default Style: Sarcastic & Dry-Witted (Oscar)
~~~text
"You are Oscar, the onboard computer and AI copilot of a starship. You have a dark, cynical, deadpan, and highly sarcastic sense of humor. You love teasing the Commander about their piloting skills, obsessive rock-mining habits, exploration trips, or reckless spending, while staying ultra-concise (1 to 2 sentences max). Never give boring safety advice."
~~~

#### Variant: Strict Military Starship Computer
~~~text
"You are the tactical onboard computer of a Federal Navy cruiser. You are extremely formal, cold, precise, and efficient. Answer concisely (1 sentence) without fluff, using proper military terminology."
~~~

#### Variant: Warm and Supportive Copilot
~~~text
"You are Astra, an attentive, enthusiastic, and protective copilot. You watch over the Commander's safety with warmth and professionalism while keeping replies concise (1 to 2 sentences max)."
~~~

> ⚠️ **Critical Tag Rule to Preserve:** To keep Dictation and Spelling modes working properly, always keep the control tag instructions at the end of your prompt:
> `... If the Commander asks to write, dictate text, or enter dictation mode, give a short reply and end with [MODE_DICTEE]. If they ask to spell or enter letter-by-letter mode, end with [MODE_EPELLATION]. NEVER use bold (**), bullet lists, or numbering.`

---

## 3. Changing the Internal Activation Shortcut

Whether you press your HOTAS button (`COM_IA_ON` / `COM_IA_OFF`) or speak the Hands-Free wake words (*"Oscar"* / *"Terminé"*), **VoiceAttack** triggers Whisper recording by simulating an internal keyboard combination (default: **`Ctrl + Shift + F9`**).

If this shortcut conflicts with another application (e.g., GeForce Experience, Discord, OBS), you can change it in two steps:

1. **In `config_oscar.json`:**  
   Update the `"raccourci_ptt"` key (for instance to `ctrl+shift+f10`):
   ~~~json
   "raccourci_ptt": "ctrl+shift+f10"
   ~~~
   *(Avoid using the `Alt` key in this combination, as it may trigger Windows menu bars during text injection).*

2. **In VoiceAttack (required to stay synchronized):**  
   Edit your profile in VoiceAttack and update the simulated keystroke in each trigger command:
   - **`COM_IA_ON`**: replace the key press (*Press*) of `Ctrl + Shift + F9` with your new shortcut.
   - **`COM_IA_OFF`**: replace the key release (*Release*) of `Ctrl + Shift + F9` with your new shortcut.
   - **`Oscar`** (and **`Terminé`**): also update the keystroke simulated when opening and closing Hands-Free listening.

---

## 4. Changing the Synthesis Voice (Edge-TTS) & Speech Rate

Oscar uses high-definition neural voices from **Microsoft Edge-TTS**. You can choose any available voice and adjust its speaking rate inside `config_oscar.json`:

~~~json
"tts": {
  "voix": "en-GB-RyanNeural",
  "vitesse": "+8%"
}
~~~

### Recommended English & French Neural Voices:

| Voice Name | Vocal Profile | Recommended For |
| :--- | :--- | :--- |
| **`en-GB-RyanNeural`** | Male, British English, crisp and expressive | Classic British ship AI / Jarvis style |
| **`en-GB-SoniaNeural`** | Female, British English, calm and refined | Realistic British bridge computer |
| **`en-US-GuyNeural`** | Male, American English, natural and direct | Tactical American copilot |
| **`en-US-AriaNeural`** | Female, American English, dynamic and clear | Modern sci-fi copilot |
| **`fr-FR-HenriNeural`** | Male, French, calm and expressive *(Default)* | Original French Oscar |
| **`fr-FR-DeniseNeural`** | Female, French, clear and professional | French female ship AI |

### Adjusting Speech Rate (`vitesse`)
- `"+0%"`: Standard normal speed.
- `"+8%"`: Slightly brisker and more responsive *(recommended)*.
- `"+15%"`: Fast-paced delivery for busy commanders.
- `"-5%"`: Slower, more solemn delivery.

---

## 5. Adding New Elite Dangerous Ships

Frontier Developments regularly releases new ships (e.g., *Python Mk II*, *Mandalay*, *Caspian Explorer*, *Cobra Mk V*...).

The `"noms_vaisseaux"` dictionary maps the internal technical ship ID written in game journals to its clean display name:

~~~json
"noms_vaisseaux": {
  "mandalay": "Mandalay",
  "python_nx": "Python Mk II",
  "explorer_nx": "Caspian Explorer",
  "cobramkv": "Cobra Mk V",
  "your_new_ship_code": "Official Ship Name"
}
~~~

### How to find a new ship's internal code:
1. Board the new ship in-game.
2. Open the latest `Journal.*.log` file inside `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous`.
3. Search for the `"event":"Loadout"` or `"event":"LoadGame"` entry.
4. Check the `"Ship"` field value (e.g., `"Ship":"explorer_nx"`).
5. Add the corresponding lowercase mapping inside `config_oscar.json`:
   `"explorer_nx": "Caspian Explorer"`

---

## 6. Adjusting DirectX Keyboard Simulation Delays

If you play with variable frame rates (FPS) or high refresh-rate V-Sync, you can fine-tune hardware keystroke timings in `"delais_clavier"`:

~~~json
"delais_clavier": {
  "delai_apres_ptt_relachement": 0.06,
  "delai_frappe_down": 0.025,
  "delai_frappe_up": 0.015,
  "delai_ctrl_combinaison": 0.035,
  "delai_clipboard_injection": 0.04
}
~~~

- **`delai_apres_ptt_relachement` (0.06s):** Wait delay after releasing the physical Push-To-Talk button before injecting text (gives Windows time to release Ctrl/Shift).
- **`delai_frappe_down` (0.025s) / `delai_frappe_up` (0.015s):** Hardware key press and release duration (Backspace, Enter, etc.). Values below `0.01s` may be missed by the game's DirectX input loop.
- **`delai_clipboard_injection` (0.04s):** Windows clipboard buffer stabilization time during `Ctrl + V` pasting.

---

## 7. Customizing Voice Mode Keywords

Inside `"commandes_modes"`, you can add your own preferred synonyms to control Dictation and Spelling modes:

- **`validation_dictee`:** Keywords to send the message and exit Dictation Mode (e.g., `"send"`, `"send message"`, `"post"`).
- **`correction_dictee`:** Keywords to undo the last dictated block (e.g., `"undo"`, `"backspace"`, `"correct"`).
- **`paragraphe_dictee`:** Keywords to insert a newline (e.g., `"new line"`, `"next paragraph"`).
- **`commandes_sortie`:** Universal cancel/exit keywords (e.g., `"stop"`, `"cancel"`, `"exit"`).
- **`alphabet_phonetique`:** Custom phonetic words for Spelling Mode (e.g., `"alpha": "A"`, `"bravo": "B"`).

---

## 8. Adding or Modifying Physical Commands (VoiceAttack)

You can expand or customize the catalog of physical onboard commands at will *(see the **[Command & Keybinding Matrix (TABLEAU_COMMANDES.md)](TABLEAU_COMMANDES.md)** to inspect the complete mapping of all 121 existing macros, their simulated keys, and corresponding XML tags)*.

### 🚨 The Golden Rule: Exact String Match
Every command name inside **`data/commandes_vaisseau.txt`** must be **100% IDENTICAL** (character for character: uppercase, accents, spaces, hyphens) to the corresponding macro name in your **VoiceAttack** profile.

**Why?**
When an order is recognized, GPT-4o-mini picks the exact name from `commandes_vaisseau.txt` and outputs `[EXECUTE:Command_Name]`. Python then passes that exact name to VoiceAttack via CLI:
~~~cmd
VoiceAttack.exe -command "Command_Name"
~~~
If even a single space or capital letter differs between `commandes_vaisseau.txt` and VoiceAttack, VoiceAttack will ignore the command!

---

### Step-by-step: Adding a new command
1. **In VoiceAttack:**  
   Create your new macro (e.g., `Launch Recon Limpet`) and assign it a keyboard shortcut (e.g., `Ctrl + Alt + K`).
2. **In Elite Dangerous (Bindings):**  
   In the game's Controls menu, assign that exact same shortcut (`Ctrl + Alt + K`) in the **Secondary** column (`<Secondary>`) of the desired action.
3. **In `data/commandes_vaisseau.txt`:**  
   Add a new line containing the exact macro name:
   ~~~text
   Launch Recon Limpet
   ~~~
4. **Restart Oscar (`IA_Elite.bat`):**  
   At startup, Oscar automatically loads the updated list. You can now ask aloud: *"Oscar, fire a recon limpet"*, and it will trigger your macro!

---

### Step-by-step: Modifying an existing command
1. **Changing only the keybind of a command (keeping its name):**  
   - Locate the command in the mapping table and edit its simulated keystroke inside **VoiceAttack**.
   - Apply the same keybind to the **Secondary** column (`<Secondary>`) of the corresponding action in **Elite Dangerous** (or re-run `py sync_binds.py` after exporting your updated `.vap` profile).
   - No changes are needed in `data/commandes_vaisseau.txt`.
2. **Renaming an existing command (or translating it):**  
   - Rename the macro inside **VoiceAttack** (e.g., `Allumer Phares` → `Turn On Lights`).
   - Replace the old name with the exact new name inside **`data/commandes_vaisseau.txt`**, then restart `IA_Elite.bat`.

---

## 9. Switching Oscar Completely to English

By default, Oscar is configured in French. If you want to speak **English** to your copilot and receive **English** replies, update these 4 components:

1. **Switch Faster-Whisper STT to English (`modules/stt_engine.py`):**  
   Open `modules/stt_engine.py`, locate the `model.transcribe(...)` calls, and replace `language="fr"` with `language="en"` (or remove the `language` parameter to enable automatic language detection).
2. **Switch the Neural Voice & Personality to English (`config_oscar.json`):**  
   - Set `"voix": "en-GB-RyanNeural"` (or `"en-US-GuyNeural"`, `"en-GB-SoniaNeural"`) under `"tts"`.
   - Translate the `"personnalite_ia"` prompt into English (see Section 2 above) so GPT-4o-mini always replies in English.
3. **Translate Mode Control Keywords (`config_oscar.json`):**  
   Under `"commandes_modes"`, replace or add English keywords for `"validation_dictee"` (`"send"`, `"send message"`), `"correction_dictee"` (`"correct"`, `"undo"`), `"paragraphe_dictee"` (`"new line"`, `"next paragraph"`), `"commandes_sortie"` (`"stop"`, `"cancel"`, `"exit"`), and English spoken punctuation/symbols (`"dot"`, `"dash"`, `"space"`).
4. **Update VoiceAttack Wake Words & Command Names (Optional):**  
   - In VoiceAttack, update the Hands-Free end-of-speech command `"Terminé"` to `"Over"` or `"Done"` (and `"Oscar"` if you changed `"nom_ia"`).
   - You can keep the 121 macro names in `data/commandes_vaisseau.txt` and VoiceAttack as they are (GPT-4o-mini understands English orders and maps them to French macro names automatically!), or translate them identically in **both** VoiceAttack and `data/commandes_vaisseau.txt`.
