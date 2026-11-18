[🇫🇷 Version Française](#-oscar--copilote-vocal-ia-pour-elite-dangerous-odyssey--horizons) | [🇬🇧 English Version](#-oscar--ai-voice-copilot-for-elite-dangerous-odyssey--horizons)

---

# 🚀 OSCAR — Copilote Vocal IA pour Elite Dangerous (Odyssey & Horizons)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![VoiceAttack](https://img.shields.io/badge/VoiceAttack-Compatible-purple.svg)](https://voiceattack.com/)
[![Whisper GPU](https://img.shields.io/badge/STT-Faster--Whisper%20CUDA-green.svg)](https://github.com/SYSTRAN/faster-whisper)
[![OpenAI](https://img.shields.io/badge/Brain-GPT--4o--mini-orange.svg)](https://openai.com/)
[![TTS](https://img.shields.io/badge/TTS-Edge--TTS%20Neural-teal.svg)](https://github.com/rany2/edge-tts)

**Oscar** est un copilote vocal intelligent, autonome et sarcastique conçu pour les commandants d'**Elite Dangerous**. Doté d'une mémoire persistance et d'une connexion directe à la télémétrie locale du jeu ainsi qu'aux bases de données galactiques (Spansh & EDSM), Oscar vous assiste en temps réel au combat, en exploration et en commerce, tout en taquinant volontiers vos talents de pilotage.

---

### 📚 Accès Rapide à la Documentation
- 🛠️ **[Guide d'Installation Complet (INSTALLATION.md)](INSTALLATION.md)** — Prérequis, installation pas-à-pas des dépendances, règle Non-Admin de VoiceAttack, synchronisation `.binds` et dépannage.
- 📖 **[Guide d'Utilisation Complet (GUIDE_UTILISATEUR.md)](GUIDE_UTILISATEUR.md)** — Flux d'interprétation, activation Mains Libres, modes Dictée & Épellation, catalogue des ordres vocaux et télémétrie.
- ⚙️ **[Guide de Personnalisation (PERSONNALISATION.md)](PERSONNALISATION.md)** — Modifier le nom du copilote, sa voix, sa personnalité et ajouter de nouvelles commandes VoiceAttack.

---

## ✨ Points forts & Innovations

- **🧠 Cerveau Hybride GPT-4o-mini & Function Calling :** Interprétation sémantique naturelle des intentions du pilote et déclenchement automatique d'outils temps réel (télémétrie, calculs de sauts, consultation de la flotte, etc.).
- **⚡ STT Local Ultra-Rapide (Faster-Whisper sur GPU) :** Reconnaissance vocale exécutée en local sur votre carte graphique NVIDIA via CUDA (modèle `large-v3-turbo`) avec amorçage contextuel anti-hallucinations.
- **🗣️ Synthèse Vocale Neurale Gratuite (Edge-TTS) :** Voix haute fidélité naturelle Microsoft Henri Neural (`fr-FR-HenriNeural`), sans aucun coût d'API vocale et sans bloquer l'audio du jeu.
- **🎙️ Modes de Saisie Directe Gratuits (0 jeton consommé) :**
  - **Mode Dictée :** Dictez vocalement vos messages dans le chat du jeu ou sur Discord, avec ponctuation automatique et injection fluide par presse-papiers.
  - **Mode Épellation :** Épelez lettre par lettre les systèmes stellaires dans la carte galactique (alphabets OTAN et français acceptés, gestion déterministe des tirets et des codes alphanumériques).
- **📡 Télémétrie & Alertes Autonomes :** Thread haute fréquence (0.4s) surveillant en continu l'état du vaisseau (`Status.json`, `ModulesInfo.json`, `Cargo.json`, journaux d'événements). Oscar vous avertit de vive voix lors des ruptures de boucliers, surchauffes, interdictions ou pannes de modules critiques.
- **📊 Recherche Marché & Modules par PAD (Spansh) :** Recherche de stations vendant ou achetant des minerais/marchandises au meilleur prix, ou proposant l'équipement désiré, en vérifiant automatiquement la compatibilité du PAD (Large/Moyen) de votre vaisseau actif et en copiant directement le système cible dans votre presse-papiers.
- **🔒 Zéro Mode Administrateur & Respect Strict du HOTAS :** Tourne entièrement dans le répertoire utilisateur et intègre l'utilitaire `sync_binds.py` pour configurer les touches du copilote sans jamais modifier ni écraser vos commandes HOTAS/manette originales.

---

## 🛠️ Prérequis

1. **Système :** Windows 10 ou Windows 11 (64-bit).
2. **Python :** Python 3.10 ou supérieur (avec option `Add Python to PATH` cochée lors de l'installation).
3. **Carte Graphique :** GPU NVIDIA (série GTX 1060 / RTX avec un minimum de 6 Go de VRAM recommandée avec pilotes à jour et support CUDA).
4. **VoiceAttack :** Logiciel VoiceAttack v1.16+ installé (version Steam ou Standalone).
5. **Clé API OpenAI :** Clé d'API valide avec accès au modèle `gpt-4o-mini`.
6. **Clé API EDSM (Optionnelle) :** Gratuite, disponible sur votre compte [EDSM.net](https://edsm.net).

---

## 📦 Étapes d'installation

Le **[Guide d'Installation Complet (INSTALLATION.md)](INSTALLATION.md)** vous donne la procédure détaillée pas-à-pas pour chaque composant. Les grandes étapes à prévoir sont les suivantes :

1. **Cloner ou télécharger le projet** et le placer dans un dossier utilisateur standard (exemple : `C:\Users\<VotreNom>\Documents\IA Elite`).
2. **Télécharger et installer VoiceAttack v1.16+** (version complète) si vous ne l'avez pas déjà, en veillant à le laisser en mode utilisateur normal (non-Administrateur).
3. **Installer Python (3.10+) et ses dépendances**.
4. **Installer Whisper GPU** (`faster-whisper` ainsi que les bibliothèques NVIDIA CUDA/cuDNN).
5. **Installer Edge-TTS** (`edge-tts`) pour la synthèse vocale neurale gratuite.
6. **Créer des comptes OpenAI et EDSM** pour obtenir les clés API correspondantes (si vous ne les avez pas déjà).
7. **Configurer un fichier `secrets.json`** (modèle `secrets.example.json` fourni) avec vos clés API et les chemins vers vos journaux de vol et `VoiceAttack.exe`.
8. **Importer le profil fourni (`/data/Barbare Darko-Profile.vap`)** dans VoiceAttack.
9. **Synchroniser automatiquement les 121 commandes VoiceAttack** avec votre fichier `.binds` actif dans Elite Dangerous grâce au petit utilitaire `sync_binds.py` fourni (sans toucher à vos touches principales).
10. **Mettre à jour les commandes `Oscar`, `Terminé`, `COM_IA_ON` et `COM_IA_OFF`** dans VoiceAttack pour correspondre à votre bouton Push-To-Talk et au nom de l'IA choisi.
11. **Lancer `IA_Elite.bat`** pour démarrer le copilote !

---

## 📚 Documentation complémentaire

- 🛠️ **[Guide d'Installation Complet (INSTALLATION.md)](INSTALLATION.md) :**
  - Installation détaillée de tous les composants, règle Non-Admin VoiceAttack, lancement du copilote et résolution des problèmes fréquents.
- 📖 **[Guide d'Utilisation Complet (GUIDE_UTILISATEUR.md)](GUIDE_UTILISATEUR.md) :**
  - Architecture détaillée, mode Mains Libres, mode d'emploi des modes **Dictée** et **Épellation**, catalogue exhaustif des requêtes et ordres vocaux.
- ⚙️ **[Guide de Personnalisation (PERSONNALISATION.md)](PERSONNALISATION.md) :**
  - Comment modifier le nom, la voix, la personnalité d'Oscar, ajouter de nouveaux vaisseaux et créer de nouvelles commandes VoiceAttack.
- 🗺️ **[Tableau des Commandes & Raccourcis (TABLEAU_COMMANDES.md)](TABLEAU_COMMANDES.md) :**
  - Matrice intégrale de correspondance entre les 121 macros VoiceAttack/IA, les touches émulées, les modes du jeu (Vaisseau, VRS, À pied, Général) et les balises XML dans `.binds`.

---

## 📂 Architecture modulaire du projet

```text
IA Elite/
├── IA_Elite.py              # Orchestrateur principal léger (~150 lignes, boucle PTT & états)
├── IA_Elite.bat             # Lanceur Windows utilisateur standard
├── sync_binds.py            # Utilitaire interactif de synchronisation des touches .binds
├── config_oscar.json        # Paramètres personnalisables (nom, personnalité, voix, vaisseaux)
├── secrets.json             # Clés d'API et chemins locaux protégés (ignoré par git)
├── secrets.example.json     # Modèle vierge de configuration pour GitHub
├── requirements.txt         # Dépendances Python nécessaires
├── README.md                # Présentation et aperçu général (FR / EN)
├── INSTALLATION.md          # Guide d'installation pas-à-pas et dépannage
├── GUIDE_UTILISATEUR.md     # Manuel complet des commandes vocales et modes de saisie
├── PERSONNALISATION.md      # Guide des personnalisations avancées
├── TABLEAU_COMMANDES.md     # Matrice complète des commandes VA / .binds / modes ED
├── data/                    # Données persistantes et profils de référence
│   ├── commandes_vaisseau.txt           # Liste des macros VoiceAttack
│   ├── journal_de_bord.txt              # Archives et mémoires de session
│   ├── flotte_cmdr.json                 # Cache local de la flotte et configurations
│   ├── Barbare Darko-Profile.vap        # Profil VoiceAttack complet (121 macros)
│   └── HOTAS TOUS MODES.4.2.binds       # Profil de touches de référence multi-contextes
└── modules/                 # Package Python des moteurs découplés
    ├── config_loader.py     # Chargement typé des configurations et secrets
    ├── stt_engine.py        # Reconnaissance vocale Faster-Whisper GPU CUDA
    ├── tts_engine.py        # Synthèse vocale Edge-TTS et anti-écho
    ├── input_engine.py      # Simulation clavier DirectX SendInput x64 et presse-papiers
    ├── telemetry_ed.py      # Analyse journaux ED et thread d'alertes autonomes
    ├── api_clients.py       # Requêtes EDSM & Spansh (commerce, modules, PAD)
    ├── oscar_brain.py       # Cerveau OpenAI GPT-4o-mini & Function Calling
    └── text_modes.py        # Logique des modes Dictée et Épellation déterministes
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

**Oscar** is an intelligent, autonomous, and sarcastic AI voice copilot built for **Elite Dangerous** commanders. Equipped with persistent flight memory and direct integration with local game telemetry as well as galactic databases (Spansh & EDSM), Oscar assists you in real time across combat, exploration, and trading—while happily teasing your piloting skills.

---

### 📚 Quick Documentation Access
- 🛠️ **[Complete Installation Guide (INSTALLATION.md)](INSTALLATION.md)** — Prerequisites, step-by-step dependency setup, VoiceAttack Non-Admin rule, `.binds` synchronization, and troubleshooting.
- 📖 **[Complete User Guide (GUIDE_UTILISATEUR.md)](GUIDE_UTILISATEUR.md)** — Processing pipeline, Hands-Free activation, Dictation & Spelling modes, voice command catalog, and telemetry.
- ⚙️ **[Customization Guide (PERSONNALISATION.md)](PERSONNALISATION.md)** — Changing the copilot's name, voice, personality, and adding custom VoiceAttack macros.

---

## ✨ Key Features & Innovations

- **🧠 Hybrid GPT-4o-mini Brain & Function Calling:** Natural semantic understanding of pilot intent with automatic real-time tool execution (ship telemetry, 3D jump calculations, fleet lookup, etc.).
- **⚡ Ultra-Fast Local STT (Faster-Whisper on GPU):** Local speech-to-text running directly on your NVIDIA GPU via CUDA (`large-v3-turbo` model) with contextual anti-hallucination prompting.
- **🗣️ Free Neural Text-to-Speech (Edge-TTS):** High-fidelity neural voice synthesis (`fr-FR-HenriNeural` or any Edge-TTS voice), with zero voice API costs and non-blocking game audio.
- **🎙️ Free Direct Input Modes (0 OpenAI Tokens Consumed):**
  - **Dictation Mode:** Dictate messages directly into the in-game chat or Discord with automatic punctuation and smooth clipboard injection.
  - **Spelling Mode:** Spell complex star system names character by character in the Galaxy Map (supports NATO and French phonetic alphabets, deterministic hyphen handling, and alphanumeric codes).
- **📡 Real-Time Telemetry & Autonomous Alerts:** High-frequency background thread (0.4s) continuously monitoring ship status (`Status.json`, `ModulesInfo.json`, `Cargo.json`, and Player Journals). Oscar warns you aloud upon shield drops, overheating, interdictions, or critical module malfunctions.
- **📊 Pad-Aware Commodity & Module Search (Spansh):** Finds stations buying or selling commodities at the best price—or stocking desired modules—while automatically checking landing pad compatibility (Large/Medium) for your current ship and copying the target system straight to your clipboard.
- **🔒 Zero Administrator Privileges & Strict HOTAS Safety:** Runs entirely inside your user directory and includes `sync_binds.py` to map secondary keyboard bindings without ever modifying or overwriting your primary HOTAS/controller binds.

---

## 🛠️ Prerequisites

1. **Operating System:** Windows 10 or Windows 11 (64-bit).
2. **Python:** Python 3.10 or higher (make sure `Add Python to PATH` is checked during installation).
3. **Graphics Card:** NVIDIA GPU (GTX 1060 / RTX series with a minimum of 6 GB VRAM recommended, updated drivers, and CUDA support).
4. **VoiceAttack:** VoiceAttack v1.16+ installed (Steam or Standalone full version).
5. **OpenAI API Key:** Valid API key with access to the `gpt-4o-mini` model.
6. **EDSM API Key (Optional):** Free key available from your [EDSM.net](https://edsm.net) account settings.

---

## 📦 Installation Steps

The **[Complete Installation Guide (INSTALLATION.md)](INSTALLATION.md)** provides detailed step-by-step instructions for every component. Here is an overview of the main steps:

1. **Clone or download the project** into a standard user folder (example: `C:\Users\<YourName>\Documents\IA Elite`).
2. **Download and install VoiceAttack v1.16+** (full version) if not already installed, ensuring it runs in standard user mode (non-Administrator).
3. **Install Python (3.10+) and its dependencies**.
4. **Install Whisper GPU** (`faster-whisper` along with the NVIDIA CUDA/cuDNN runtime libraries).
5. **Install Edge-TTS** (`edge-tts`) for free neural voice synthesis.
6. **Create OpenAI and EDSM accounts** to obtain your API keys (if you do not already have them).
7. **Configure a `secrets.json` file** (template `secrets.example.json` provided) with your API keys and local paths to your Elite Dangerous journals and `VoiceAttack.exe`.
8. **Import the provided profile (`/data/Barbare Darko-Profile.vap`)** into VoiceAttack.
9. **Automatically synchronize all 121 VoiceAttack commands** with your active Elite Dangerous `.binds` file using the included `sync_binds.py` utility (without touching your primary controls).
10. **Update the `Oscar`, `Terminé`, `COM_IA_ON`, and `COM_IA_OFF` commands** in VoiceAttack to match your Push-To-Talk button and chosen AI name.
11. **Launch `IA_Elite.bat`** to start your copilot!

---

## 📚 Additional Documentation

- 🛠️ **[Complete Installation Guide (INSTALLATION.md)](INSTALLATION.md):**
  - Detailed setup for all components, VoiceAttack Non-Admin rule, copilot launch, and troubleshooting.
- 📖 **[Complete User Guide (GUIDE_UTILISATEUR.md)](GUIDE_UTILISATEUR.md):**
  - Detailed processing architecture, Hands-Free mode, **Dictation** & **Spelling** manuals, and full voice command catalog.
- ⚙️ **[Customization Guide (PERSONNALISATION.md)](PERSONNALISATION.md):**
  - How to change Oscar's name, voice, personality, add new ships, and create custom VoiceAttack macros.
- 🗺️ **[Command & Keybinding Matrix (TABLEAU_COMMANDES.md)](TABLEAU_COMMANDES.md):**
  - Complete mapping matrix between all 121 VoiceAttack/AI macros, simulated keys, in-game modes (Ship, SRV, On Foot, General), and `.binds` XML tags.

---

## 📂 Modular Project Structure

~~~text
IA Elite/
├── IA_Elite.py              # Lightweight main orchestrator (~150 lines, PTT & state loop)
├── IA_Elite.bat             # Standard-user Windows launcher
├── sync_binds.py            # Interactive .binds secondary key synchronization tool
├── config_oscar.json        # Customizable settings (name, personality, voice, ships)
├── secrets.json             # Protected API keys and local paths (ignored by git)
├── secrets.example.json     # Blank configuration template for GitHub
├── requirements.txt         # Required Python dependencies
├── README.md                # Project overview and installation summary (FR / EN)
├── INSTALLATION.md          # Step-by-step installation guide and troubleshooting
├── GUIDE_UTILISATEUR.md     # Full manual of voice commands and text input modes
├── PERSONNALISATION.md      # Advanced customization guide
├── TABLEAU_COMMANDES.md     # Complete VA / .binds / ED modes command matrix
├── data/                    # Persistent data and reference profiles
│   ├── commandes_vaisseau.txt           # List of VoiceAttack macros
│   ├── journal_de_bord.txt              # Session archives and flight memories
│   ├── flotte_cmdr.json                 # Local fleet and loadout cache
│   ├── Barbare Darko-Profile.vap        # Complete VoiceAttack profile (121 macros)
│   └── HOTAS TOUS MODES.4.2.binds       # Multi-context reference keybindings
└── modules/                 # Decoupled Python engine package
    ├── config_loader.py     # Typed loader for configuration and secrets
    ├── stt_engine.py        # Faster-Whisper GPU CUDA speech recognition
    ├── tts_engine.py        # Edge-TTS neural voice synthesis and anti-echo
    ├── input_engine.py      # DirectX x64 SendInput keyboard simulation & clipboard
    ├── telemetry_ed.py      # Elite Dangerous log parser and autonomous alert thread
    ├── api_clients.py       # EDSM & Spansh queries (trading, modules, landing pads)
    ├── oscar_brain.py       # OpenAI GPT-4o-mini brain & Function Calling
    └── text_modes.py        # Deterministic Dictation and Spelling mode logic
~~~

---

## 📜 License & Trademarks

Open-source project shared for the Elite Dangerous commander community.
Elite Dangerous is a registered trademark of Frontier Developments plc.
VoiceAttack is a software product by VoiceAttack LLC.

