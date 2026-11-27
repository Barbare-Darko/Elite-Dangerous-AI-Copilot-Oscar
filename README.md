[🇫🇷 Version Française](#-oscar--copilote-vocal-ia-pour-elite-dangerous-odyssey--horizons) | [🇬🇧 English Version](#-oscar--ai-voice-copilot-for-elite-dangerous-odyssey--horizons)

---

# 🚀 OSCAR — Copilote Vocal IA pour Elite Dangerous (Odyssey & Horizons)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![VoiceAttack](https://img.shields.io/badge/VoiceAttack-Compatible-purple.svg)](https://voiceattack.com/)
[![Whisper GPU](https://img.shields.io/badge/STT-Faster--Whisper%20CUDA-green.svg)](https://github.com/SYSTRAN/faster-whisper)
[![OpenAI](https://img.shields.io/badge/Brain-GPT--4o--mini-orange.svg)](https://openai.com/)
[![TTS](https://img.shields.io/badge/TTS-Edge--TTS%20Neural-teal.svg)](https://github.com/rany2/edge-tts)

**Oscar** est un copilote vocal intelligent, autonome et sarcastique conçu pour les commandants d'**Elite Dangerous** (*écran plat + Tobii Eye Tracker 5* ou *VR Meta Quest 3*). Connecté en direct à la télémétrie locale du jeu et aux bases galactiques (**Spansh**, **EDSM**, **EDAstro**), il pilote votre vaisseau, votre VRS et votre combinaison à la voix, surveille vos constantes vitales, analyse vos systèmes d'exploration, observe votre écran et vous assiste en temps réel — le tout **sans aucun droit Administrateur** et sans toucher à vos commandes HOTAS.

> 💡 **Budget :** Tous les composants sont **100 % gratuits** (projet open-source, Faster-Whisper GPU, Edge-TTS, HUD, APIs galactiques), à l'exception de **VoiceAttack** (~10–12 € en achat unique) et du crédit prépayé **API OpenAI `gpt-4o-mini`** (~0,05 à 0,15 € par heure de jeu actif).

---

### 📚 Documentation Complète (Tout-en-un)

Toute la documentation (Présentation, Installation pas-à-pas, Guide d'utilisation avec exemples concrets, Personnalisation et Tableau complet des 110 actions) est regroupée dans **un seul manuel autonome complet** :

- 🇫🇷 **[Documentation Complète en Français (DOCUMENTATION_FR.md)](DOCUMENTATION_FR.md)** — *(version PDF imprimable : **[DOCUMENTATION_FR.pdf](DOCUMENTATION_FR.pdf)**)*

---

## ✨ Points forts & Innovations (v17.1)

- **🧠 Cerveau Naturel GPT-4o-mini & Sécurité Absolue :** Compréhension fluide de vos phrases en langage naturel grâce aux familles de verbes synonymes (y compris conjugués), distinction stricte *Question vs Commande*, déclenchement automatique d'outils temps réel (analyse FSS, portefeuille d'exploration, commerce, flotte, distances) et **verrou de sécurité** bloquant les actions critiques (`Passer Mode Furtif`, `Larguer Cargaison`) sans ordre explicite.
- **⚡ Reconnaissance Vocale Locale GPU (Faster-Whisper CUDA) :** Exécutée localement sur votre carte NVIDIA (`large-v3-turbo`) avec vocabulaire Elite Dangerous intégré, marge de fin PTT (*Push-To-Talk*) anti-coupure et filtre anti-hallucination (en cas de bruit ambiant, Oscar demande simplement de répéter à 0 jeton).
- **🗣️ Voix Neurale Gratuite & *Barge-in* Instantané (Edge-TTS) :** Voix naturelle Microsoft Neural (`fr-FR-HenriNeural` ou toute autre voix Edge-TTS) avec **interruption vocale instantanée (< 50 ms)** dès que vous appuyez sur votre bouton PTT (*Push-To-Talk*).
- **🥾 Mode À Pied (Odyssey) Complet & Sécurisé :** Suivi temps réel de l'équipement tenu en main, séparation stricte **Outils vs Armes** (protection anti-toggle, cycle *Outil suivant* limité aux 3 outils de combinaison), bascule sans superposition des **3 roues radiales** (*Inventaire*, *Émoticônes*, *Insight*), *Cellule d'énergie* adaptative (batterie à pied ↔ bouclier en vaisseau) et **alertes de survie autonomes** (Oxygène ≤ 30 % / ≤ 15 %, Santé ≤ 40 %).
- **🖥️ HUD Overlay Transparent (Mode *Sans bordure*) :** Fenêtre holographique `tkinter` sans bordure, transparente aux clics et sans vol de focus (`25 car. × 10 lignes`), pilotable à la voix à **0 jeton** (*« Affiche / Enlève le HUD »*), séparation stricte `HUD` (Oscar) vs `ATH` (jeu), voyant micro rouge/vert et positions mémorisées indépendamment par vue (`cockpit`, `carte_systeme`, `carte_galactique`, `a_pied`).
- **👁️ Vision Hybride (OpenAI / Ollama) & Mode Photo Automatisé :** Dites *« Regarde ! … »* pour faire analyser votre écran (instruments cockpit avec recadrage ultrawide, plantes Odyssey vérifiées contre votre Codex personnel, nébuleuses filtrées par couleur), ou *« Prends une photo »* (0 jeton) pour sauvegarder un PNG natif propre en masquant puis rétablissant automatiquement le HUD Oscar et l'ATH caméra.
- **🔭 Codex Local, Analyse FSS & Portefeuille Exploration :** Base locale `data/codex_ed.json` (979 nébuleuses/POIs EDAstro+EDSM synchronisés tous les 30 jours, 15 genres exobiologiques, géologie), historique personnel `data/codex_cmdr.json`, analyse FSS triée par pertinence et distance en secondes-lumière (avec fourchettes Vista Genomics réalistes, matériaux rares, anneaux) et calcul en direct du portefeuille d'exploration non vendu à bord (bonus ×5 vérifié planète par planète).
- **🧭 Navigation Proactive & Rattrapage d'Itinéraire (0 jeton) :** Surveillance temps réel (`0,4 s`) des journaux Elite Dangerous : alertes vocales (boucliers, surchauffe, interdiction, carburant, coque, modules), accueil spontané au retour dans votre système maison, annonces d'arrivée et de Honk sur les nouveaux systèmes, et **rattrapage automatique `NavRoute.json`** via la Carte Galactique quand Odyssey oublie votre route après un débarquement.
- **🎙️ Modes Texte Gratuits (0 jeton consommé) :**
  - **Mode Dictée :** Idéal pour envoyer un message dans le chat en jeu ou sur Discord sans lâcher votre HOTAS (en terminant par *« Envoi »*).
  - **Mode Épellation :** Pour saisir des noms de systèmes complexes dans la Carte Galactique (lettres normales ou alphabet OTAN/français, gestion explicite du tiret `-`).
- **📊 Commerce, Équipement (Spansh) & Flotte :** Recherche marchande et d'équipement filtrée par taille de PAD avec relance automatique sans limite de distance et copie du système cible dans le presse-papiers ; consultation complète de votre flotte et de ses configurations (`Chantier Naval` + `Loadout`).
- **🔒 Zéro Droit Administrateur & Respect Strict du HOTAS :** Fonctionne intégralement en mode utilisateur normal ; `sync_binds.py` injecte les touches d'Oscar uniquement dans la colonne **Secondaire (`<Secondary>`)** d'une copie dédiée de votre profil `.binds`.

---

## 🗺️ Prochaines évolutions prévues

Le projet évolue activement par grandes étapes structurées :

- **🚀 v18.0 — Installateur Windows autonome & Paramétreur graphique :** un installateur unique (sans droit Administrateur) et une interface graphique complète pour configurer Oscar en quelques clics, sans jamais avoir à éditer un fichier `.json` à la main.
- **🔓 v19.0 — Suppression complète de VoiceAttack :** Oscar 100 % autonome (zéro logiciel tiers payant), détection directe de votre bouton PTT HOTAS en Python, lecture automatique de votre fichier `.binds` actif et envoi DirectInput natif.
- **🇬🇧 v20.0 — Version anglaise intégrale :** internationalisation complète du copilote (voix, reconnaissance vocale, commandes, prompts, interface, installateur et documentation bilingue FR/EN).
- **🐧 v21.0 — Portage Linux (Steam / Proton) :** rendu possible par la sortie de VoiceAttack en v19, pour permettre aux commandants sous Linux de voler avec Oscar.

> [!IMPORTANT]
> 🧪 **Appel aux testeurs — Commandants recherchés !**  
> Nous sommes activement à la recherche de **pilotes volontaires (bêta-testeurs)** pour tester Oscar sur différentes configurations matérielles et logicielles, **en particulier pour les prochaines versions à venir** (installateur v18, mode sans VoiceAttack v19, version anglaise v20 et portage Linux v21).  
> Si vous souhaitez participer, faire des retours ou signaler un souci, n'hésitez pas à ouvrir une **Issue** sur ce dépôt GitHub !

---

## 🛠️ Prérequis

1. **Système :** Windows 10 ou Windows 11 (64-bit), en mode utilisateur normal (non-Administrateur).
2. **Python :** Python **3.10+** (option `Add Python to PATH` cochée) et dépendances via `pip install -r requirements.txt`.
3. **Carte Graphique :** GPU NVIDIA (GTX 1060 / RTX, 6 Go+ VRAM recommandés avec CUDA pour une transcription < 0,2 s).
4. **Elite Dangerous :** Mode d'affichage **Sans bordure** (*Borderless*) pour le HUD Overlay et la Vision / Mode Photo.
5. **VoiceAttack :** v1.16+ (Steam ou Standalone, licence complète recommandée, **mode Non-Administrateur obligatoire**).
6. **Clé API OpenAI :** Compte prépayé avec accès à `gpt-4o-mini` (cerveau + Vision OpenAI Direct recommandée).
7. **Optionnels :** Clé API **EDSM** (gratuite) ; **Ollama** uniquement si vous souhaitez tester la Vision 100 % locale *(performances visuelles nettement inférieures à OpenAI)*.

---

## 📦 Installation en bref

Retrouvez la procédure complète pas-à-pas et le dépannage dans **[DOCUMENTATION_FR.md (Chapitre 1)](DOCUMENTATION_FR.md#chapitre-1--installation--mise-en-service)** :

1. **Placez le projet** dans un dossier utilisateur standard (ex. `C:\Users\<VotreNom>\Documents\IA Elite` — jamais dans `Program Files`).
2. **Installez les dépendances Python :** `pip install -r requirements.txt`.
3. **Créez `secrets.json`** à partir de `secrets.example.json` avec vos clés API et vos chemins locaux.
4. **Configurez VoiceAttack** en mode **Non-Administrateur**, importez `data/Barbare Darko-Profile.vap` et liez votre bouton PTT (*Push-To-Talk*) à `COM_IA_ON` / `COM_IA_OFF`.
5. **Exécutez `py sync_binds.py`** pour créer votre copie sécurisée `..._Oscar.4.2.binds`, puis sélectionnez ce profil dans les **4 onglets de commandes** d'Elite Dangerous (*Général*, *Vaisseau*, *VRS*, *À pied*) et passez l'affichage en **Sans bordure**.
6. **Lancez `IA_Elite.bat`** !

---

## 📂 Architecture modulaire du projet (v17.1)

```text
Elite-Dangerous-AI-Copilot-Oscar/
├── IA_Elite.py              # Orchestrateur principal (boucle PTT, Barge-in, HUD, Vision, sécurité, itinéraire)
├── IA_Elite.bat             # Lanceur Windows utilisateur standard
├── sync_binds.py            # Utilitaire non destructif de synchronisation des touches .binds
├── config_oscar.json        # Paramètres personnalisables (identité, voix, HUD, Vision/Photo, navigation, synonymes)
├── secrets.json             # Clés d'API et chemins locaux protégés (ignoré par git)
├── secrets.example.json     # Modèle vierge de configuration
├── requirements.txt         # Dépendances Python nécessaires
├── README.md                # Présentation générale (FR / EN)
├── DOCUMENTATION_FR.md      # Manuel complet tout-en-un en français
├── DOCUMENTATION_FR.pdf     # Version PDF du manuel français
├── data/                    # Données persistantes, Codex et profils de référence
│   ├── commandes_vaisseau.txt           # Liste des macros VoiceAttack reconnues
│   ├── journal_de_bord.txt              # Mémoire conversationnelle condensée
│   ├── flotte_cmdr.json                 # Cache local de votre flotte et configurations
│   ├── hud_positions.json               # Positions mémorisées du HUD par vue ED
│   ├── codex_ed.json                    # Codex local (979 nébuleuses/POIs EDAstro+EDSM, exobio, géologie)
│   ├── codex_cmdr.json                  # Historique personnel CMDR scanné des journaux
│   ├── Barbare Darko-Profile.vap        # Profil VoiceAttack complet (121 macros + 4 commandes PTT)
│   └── HOTAS TOUS MODES.4.2.binds       # Profil de touches de référence multi-contextes
└── modules/                 # Package Python des moteurs découplés
    ├── config_loader.py     # Chargement typé des configurations et secrets
    ├── stt_engine.py        # Reconnaissance vocale Faster-Whisper GPU CUDA + anti-hallucination
    ├── tts_engine.py        # Synthèse vocale Edge-TTS interruptible (Barge-in < 50 ms)
    ├── input_engine.py      # Simulation clavier DirectX SendInput x64 et presse-papiers
    ├── telemetry_ed.py      # Analyse journaux ED, alertes 0,4 s, équipement à pied & navigation proactive
    ├── api_clients.py       # Requêtes EDSM & Spansh (commerce, modules, PAD, relance auto)
    ├── oscar_brain.py       # Cerveau OpenAI GPT-4o-mini, synonymes, Vision directe & Function Calling
    ├── text_modes.py        # Modes Dictée et Épellation déterministes (0 jeton)
    ├── hud_overlay.py       # HUD Overlay transparent tkinter (sans vol de focus, clics traversants)
    ├── vision_engine.py     # Vision hybride OpenAI/Ollama, capture DPI-aware & Mode Photo
    └── codex_ed.py          # Codex local/personnel, analyse FSS & portefeuille exploration
```

---

## 📜 Licence & Droits

Projet open-source partagé pour la communauté des pilotes d'Elite Dangerous.  
Elite Dangerous est une marque déposée de Frontier Developments plc.  
VoiceAttack est un logiciel édité par VoiceAttack LLC.

---
---

# 🚀 OSCAR — AI Voice Copilot for Elite Dangerous (Odyssey & Horizons)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![VoiceAttack](https://img.shields.io/badge/VoiceAttack-Compatible-purple.svg)](https://voiceattack.com/)
[![Whisper GPU](https://img.shields.io/badge/STT-Faster--Whisper%20CUDA-green.svg)](https://github.com/SYSTRAN/faster-whisper)
[![OpenAI](https://img.shields.io/badge/Brain-GPT--4o--mini-orange.svg)](https://openai.com/)
[![TTS](https://img.shields.io/badge/TTS-Edge--TTS%20Neural-teal.svg)](https://github.com/rany2/edge-tts)

**Oscar** is an intelligent, autonomous, and sarcastic AI voice copilot designed for **Elite Dangerous** commanders (*flat screen + Tobii Eye Tracker 5* or *Meta Quest 3 VR*). Connected live to your local game telemetry and community galactic databases (**Spansh**, **EDSM**, **EDAstro**), Oscar pilots your ship, SRV, and Odyssey suit by voice, watches your vitals, analyzes explored systems, inspects your screen, and assists you in real time — **with zero Administrator privileges** and without ever touching your primary HOTAS bindings.

> 💡 **Budget:** Almost every component is **100% free** (open-source project, Faster-Whisper GPU, Edge-TTS, HUD overlay, galactic APIs), except **VoiceAttack** (~$10–12 one-time) and pay-as-you-go **OpenAI `gpt-4o-mini` API credits** (~$0.05–$0.15 per hour of active play).

---

> [!NOTE]
> 🚧 **English Version Under Development!**  
> For now, **only the French version of Oscar (voice commands, prompts, and full documentation) is available**. A complete, native **English version (v20.0)** — covering voice commands, neural voice, STT, UI, installer, and full English documentation — is actively planned on the roadmap!  
> 🔔 **Want to be notified when it lands?** Click **Watch → Custom → Releases** (and **Star** the repo) at the top of this GitHub page to receive an automatic alert on new releases.

### 📚 Complete Documentation (All-in-One)

Everything (Overview, Step-by-Step Installation, User Guide with real voice examples, Customization, and the full 110-Action Command Matrix) is bundled into **one complete standalone manual** *(currently in French)*:

- 🇫🇷 **[Complete Manual — French only for now (`DOCUMENTATION_FR.md`)](DOCUMENTATION_FR.md)** — *(printable PDF: **[DOCUMENTATION_FR.pdf](DOCUMENTATION_FR.pdf)**)*

---

## ✨ Key Features & Innovations (v17.1)

- **🧠 Natural GPT-4o-mini Brain & Hard Safety Locks:** Natural command phrasing powered by verb synonym families, strict *Question vs Command* separation, live tool calling (FSS analyzer, exploration wallet, trading, fleet, 3D distances), and **hard safety locks** blocking dangerous commands (`Passer Mode Furtif`, `Larguer Cargaison`) unless explicitly spoken.
- **⚡ Ultra-Fast Local GPU STT (Faster-Whisper CUDA):** Runs locally on your NVIDIA GPU (`large-v3-turbo`) with Elite Dangerous vocabulary prompting, PTT (*Push-To-Talk*) end-buffer protection, and anti-hallucination filtering (on noisy audio, Oscar simply asks you to repeat at 0 tokens).
- **🗣️ Free Neural Voice & Instant Barge-In (Edge-TTS):** High-fidelity Microsoft Neural voice (`fr-FR-HenriNeural` or any Edge-TTS voice) with **instant speech interruption (< 50 ms)** whenever you press your PTT (*Push-To-Talk*) button.
- **🥾 Full & Safe Odyssey On-Foot Mode:** Live active-equipment tracking, strict **Tools vs Weapons** separation (anti-toggle protection, safe *Next Tool* cycle restricted to your 3 suit tools), conflict-free switching across all **3 radial wheels** (*Item*, *Emote*, *Insight*), adaptive *Energy Cell* (Suit Battery on foot ↔ Shield Cell Bank in ship), and **autonomous survival alerts** (Oxygen ≤ 30% / ≤ 15%, Health ≤ 40%).
- **🖥️ Transparent HUD Overlay (*Borderless* Mode):** Frameless, click-through, non-focus-stealing holographic `tkinter` overlay (`25 chars × 10 lines`), voice-toggled at **0 tokens**, strict separation between Oscar's HUD and the game's Free Camera HUD, red/green mic indicator, and independently saved positions per view (`cockpit`, `carte_systeme`, `carte_galactique`, `a_pied`).
- **👁️ Hybrid Vision (OpenAI / Ollama) & Automated Photo Mode:** Ask Oscar to look at your screen (cockpit gauges with ultrawide 16:9 crop, Odyssey plants checked against your personal Codex, nebulae filtered by color), or trigger **Photo Mode** (0 tokens) to capture a clean native PNG while automatically hiding and restoring both Oscar's HUD and the game's Free Camera UI.
- **🔭 Local Codex, FSS Analyzer & Exploration Wallet:** Local `data/codex_ed.json` (979 EDAstro+EDSM nebulae/POIs auto-synced every 30 days, 15 exobiology genera, geology), personal `data/codex_cmdr.json`, FSS profitability analyzer sorted by relevance and light-seconds distance (realistic Vista Genomics ranges, rare raw materials, rings), and live unsold exploration wallet tracking (per-body verified ×5 first-footfall bonus).
- **🧭 Proactive Navigation & Route Recovery (0 Tokens):** High-frequency (`0.4 s`) journal watcher with autonomous alerts (shields, heat, interdiction, fuel, hull, modules), spontaneous home-system welcome, new-system arrival and Honk briefings, and **automatic `NavRoute.json` recovery** via the Galaxy Map when Odyssey forgets your active route after disembarking.
- **🎙️ Free Text Input Modes (0 Tokens Consumed):**
  - **Dictation Mode:** Send messages directly into in-game chat or Discord without letting go of your HOTAS.
  - **Spelling Mode:** Type complex star system names in the Galaxy Map (plain letters or NATO/French phonetic alphabets, deterministic hyphen handling).
- **📊 Pad-Aware Trading, Outfitting (Spansh) & Fleet:** Commodity and module lookups honoring your ship's landing pad size, automatic distance-cap fallback, clipboard copy of the target system, and full fleet/loadout tracking (`Shipyard` + `Loadout`).
- **🔒 Zero Administrator Rights & Strict HOTAS Safety:** Runs completely in standard user mode; `sync_binds.py` only writes Oscar's keys into empty **Secondary (`<Secondary>`)** slots on a dedicated copy of your `.binds` file.

---

## 🗺️ Upcoming Roadmap

The project is actively evolving across major planned milestones:

- **🚀 v18.0 — Standalone Windows Installer & Graphical Configurator:** A single non-Admin Windows installer plus a full GUI settings tool so you can configure Oscar in a few clicks without ever editing `.json` files manually.
- **🔓 v19.0 — Complete Removal of VoiceAttack:** 100% standalone Oscar (zero paid third-party software), native Python HOTAS Push-To-Talk detection, live reading of your active `.binds` file, and native DirectInput keystrokes.
- **🇬🇧 v20.0 — Full Native English Version:** End-to-end internationalization (English voice commands, TTS, STT, AI prompts, GUI, installer, and full FR/EN documentation).
- **🐧 v21.0 — Linux Port (Steam / Proton):** Unlocked by removing VoiceAttack in v19, bringing Oscar to Linux commanders.

> [!IMPORTANT]
> 🧪 **Call for Beta Testers — Commanders Wanted!**  
> We are actively looking for **volunteer commanders / beta testers** across different hardware and software setups, **especially for upcoming releases** (v18 installer, v19 standalone mode without VoiceAttack, v20 English version, and v21 Linux port).  
> Want to help test or share feedback? Feel free to open an **Issue** on this GitHub repository!

---

## 🛠️ Prerequisites

1. **OS:** Windows 10 or Windows 11 (64-bit), running in standard user mode (non-Administrator).
2. **Python:** Python **3.10+** (`Add Python to PATH` checked) + dependencies via `pip install -r requirements.txt`.
3. **Graphics Card:** NVIDIA GPU (GTX 1060 / RTX, 6 GB+ VRAM recommended with CUDA for < 0.2 s transcription).
4. **Elite Dangerous:** **Borderless** display mode for the HUD Overlay and Vision / Photo Mode capture.
5. **VoiceAttack:** v1.16+ (Steam or Standalone, full version recommended, **Non-Administrator mode mandatory**).
6. **OpenAI API Key:** Pay-as-you-go account with access to `gpt-4o-mini` (brain + recommended OpenAI Direct Vision).
7. **Optional:** Free **EDSM** API key; **Ollama** only if you want to experiment with 100% local Vision *(visual accuracy is significantly lower than OpenAI)*.

---

## 📦 Quick Installation Overview

See the full step-by-step guide and troubleshooting in **[DOCUMENTATION_FR.md (Chapter 1 — French)](DOCUMENTATION_FR.md#chapitre-1--installation--mise-en-service)**:

1. **Place the project** in a standard user folder (e.g. `C:\Users\<YourName>\Documents\IA Elite` — never inside `Program Files`).
2. **Install Python dependencies:** `pip install -r requirements.txt`.
3. **Create `secrets.json`** from `secrets.example.json` with your API keys and local paths.
4. **Configure VoiceAttack** in **Non-Administrator** mode, import `data/Barbare Darko-Profile.vap`, and bind your PTT (*Push-To-Talk*) button to `COM_IA_ON` / `COM_IA_OFF`.
5. **Run `py sync_binds.py`** to create your safe `..._Oscar.4.2.binds` preset, apply it to **all 4 control tabs** in Elite Dangerous (*General*, *Ship*, *SRV*, *On Foot*), and set Display mode to **Borderless**.
6. **Launch `IA_Elite.bat`**!

---

## 📂 Modular Project Structure (v17.1)

```text
Elite-Dangerous-AI-Copilot-Oscar/
├── IA_Elite.py              # Main orchestrator (PTT loop, Barge-in, HUD, Vision, safety, route recovery)
├── IA_Elite.bat             # Standard-user Windows launcher
├── sync_binds.py            # Non-destructive .binds secondary key synchronization tool
├── config_oscar.json        # Customizable settings (identity, voice, HUD, Vision/Photo, navigation, synonyms)
├── secrets.json             # Protected API keys and local paths (ignored by git)
├── secrets.example.json     # Blank configuration template
├── requirements.txt         # Required Python dependencies
├── README.md                # Project overview (FR / EN)
├── DOCUMENTATION_FR.md      # Complete standalone manual (French)
├── DOCUMENTATION_FR.pdf     # PDF version of the French manual
├── data/                    # Persistent data, Codex, and reference profiles
│   ├── commandes_vaisseau.txt           # List of recognized VoiceAttack macros
│   ├── journal_de_bord.txt              # Condensed conversational flight memory
│   ├── flotte_cmdr.json                 # Local fleet and loadout cache
│   ├── hud_positions.json               # Saved HUD coordinates per ED view
│   ├── codex_ed.json                    # Local Codex (979 EDAstro+EDSM nebulae/POIs, exobio, geology)
│   ├── codex_cmdr.json                  # Personal CMDR history scanned from journals
│   ├── Barbare Darko-Profile.vap        # Full VoiceAttack profile (121 macros + 4 PTT commands)
│   └── HOTAS TOUS MODES.4.2.binds       # Multi-context reference keybindings
└── modules/                 # Decoupled Python engine package
    ├── config_loader.py     # Typed loader for configuration and secrets
    ├── stt_engine.py        # Faster-Whisper GPU CUDA speech recognition + anti-hallucination
    ├── tts_engine.py        # Interruptible Edge-TTS neural synthesis (Barge-in < 50 ms)
    ├── input_engine.py      # DirectX x64 SendInput keyboard simulation & clipboard
    ├── telemetry_ed.py      # ED log parser, 0.4s alerts, on-foot equipment & proactive navigation
    ├── api_clients.py       # EDSM & Spansh queries (trading, modules, pads, auto-retry)
    ├── oscar_brain.py       # OpenAI GPT-4o-mini brain, synonyms, direct Vision & Function Calling
    ├── text_modes.py        # Deterministic Dictation and Spelling modes (0 tokens)
    ├── hud_overlay.py       # Transparent tkinter HUD overlay (non-focus, click-through)
    ├── vision_engine.py     # Hybrid OpenAI/Ollama vision, DPI-aware capture & Photo Mode
    └── codex_ed.py          # Local/personal Codex, FSS analyzer & exploration wallet
```

---

## 📜 License & Trademarks

Open-source project shared for the Elite Dangerous commander community.  
Elite Dangerous is a registered trademark of Frontier Developments plc.  
VoiceAttack is a software product by VoiceAttack LLC.
