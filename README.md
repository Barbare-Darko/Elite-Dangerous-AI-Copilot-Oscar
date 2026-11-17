# 🚀 OSCAR — Copilote Vocal IA pour Elite Dangerous (Odyssey & Horizons)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![VoiceAttack](https://img.shields.io/badge/VoiceAttack-Compatible-purple.svg)](https://voiceattack.com/)
[![Whisper GPU](https://img.shields.io/badge/STT-Faster--Whisper%20CUDA-green.svg)](https://github.com/SYSTRAN/faster-whisper)
[![OpenAI](https://img.shields.io/badge/Brain-GPT--4o--mini-orange.svg)](https://openai.com/)
[![TTS](https://img.shields.io/badge/TTS-Edge--TTS%20Neural-teal.svg)](https://github.com/rany2/edge-tts)

**Oscar** est un copilote vocal intelligent, autonome et sarcastique conçu pour les commandants d'**Elite Dangerous**. Doté d'une mémoire persistance et d'une connexion directe à la télémétrie locale du jeu ainsi qu'aux bases de données galactiques (Spansh & EDSM), Oscar vous assiste en temps réel au combat, en exploration et en commerce, tout en taquinant volontiers vos talents de pilotage.

---

### 📚 Accès Rapide à la Documentation
- 🛠️ **[Guide d'Installation Complet (INSTALLATION.md)](INSTALLATION.md)** — Prérequis, installation des dépendances, règle Non-Admin de VoiceAttack, synchronisation `.binds` et dépannage.
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
3. **Carte Graphique :** GPU NVIDIA (série GTX 1060 / RTX recommandée avec pilotes à jour et support CUDA).
4. **VoiceAttack :** Logiciel VoiceAttack installé (version Steam ou Standalone).
5. **Clé API OpenAI :** Clé d'API valide avec accès au modèle `gpt-4o-mini`.
6. **Clé API EDSM (Optionnelle) :** Gratuite, disponible sur votre compte [EDSM.net](https://www.edsm.net/).

---

## 📦 Installation pas-à-pas

### 1. Cloner ou télécharger le projet
Placez l'ensemble des fichiers dans votre dossier utilisateur, par exemple :
```text
C:\Users\<VotreNom>\Documents\IA Elite
```

### 2. Installer les dépendances Python
Ouvrez une invite de commandes ou PowerShell dans le dossier du projet et exécutez :
```cmd
pip install -r requirements.txt
```
*(Si vous n'avez pas de fichier requirements.txt, installez : `pip install faster-whisper sounddevice numpy keyboard openai edge-tts pywin32 requests`)*

### 3. Configurer vos clés secrètes (`secrets.json`)
Copiez le modèle `secrets.example.json` pour créer votre fichier personnel `secrets.json` :
```cmd
copy secrets.example.json secrets.json
```
Ouvrez `secrets.json` avec un éditeur de texte et renseignez vos informations :
```json
{
  "openai_api_key": "sk-proj-VOTRE_CLE_API_OPENAI",
  "edsm_api_key": "VOTRE_CLE_API_EDSM_OPTIONNELLE",
  "cmdr_name": "VotreNomCommandant",
  "chemins": {
    "dossier_journaux_ed": "%USERPROFILE%\\Saved Games\\Frontier Developments\\Elite Dangerous",
    "chemin_voiceattack": "C:\\Program Files (x86)\\Steam\\steamapps\\common\\VoiceAttack\\VoiceAttack.exe"
  }
}
```
> 🛡️ **Sécurité :** `secrets.json` est strictement ignoré par `.gitignore` et ne sera jamais publié sur GitHub.

### 4. Importer le profil VoiceAttack
1. Lancez **VoiceAttack**.
2. Cliquez sur l'icône de gestion des profils (icône dossier) $\rightarrow$ **Importer un profil**.
3. Sélectionnez le fichier `data/Profil IA ELite Dangerous-Profile.vap` (ou situé à la racine).
4. Assurez-vous que le raccourci d'écoute micro (Push-To-Talk) est configuré sur **`Ctrl + Shift + F9`** (sans Alt).

### 5. Synchroniser vos commandes de jeu (`sync_binds.py`)
Avant de lancer le jeu, exécutez l'utilitaire interactif de synchronisation :
```cmd
py sync_binds.py
```
- L'utilitaire détecte votre configuration actuelle (ex: `HOTAS TOUS MODES`, `Custom`, etc.).
- Il crée une **nouvelle copie dédiée** (ex: `Custom_Oscar.4.2.binds`) en injectant les 110 raccourcis nécessaires dans la colonne secondaire (`<Secondary>`), sans écraser aucune de vos touches principales existantes.
- En jeu, dans `Options -> Commandes`, sélectionnez simplement votre nouveau profil `..._Oscar`.

---

## 🎮 Lancement du Copilote

Oscar fonctionne **exclusivement en mode utilisateur standard** (aucun droit Administrateur n'est requis ni sollicité).

Lancez simplement le fichier de démarrage :
```cmd
IA_Elite.bat
```
Ou en ligne de commande :
```cmd
py IA_Elite.py
```

Le script démarre automatiquement VoiceAttack, initialise le modèle Faster-Whisper sur votre GPU, analyse vos journaux de vol récents et vous accueille de vive voix dès qu'il est prêt.

### Deux méthodes d'interaction au choix :
- **Mode Push-To-Talk HOTAS (Contrôle absolu) :**  
  Maintenez enfoncé votre bouton micro (`Ctrl + Shift + F9`), énoncez votre ordre ou question, puis relâchez.
- **Mode Mains Libres (100 % vocal via VoiceAttack) :**  
  Dites simplement **« Oscar »** (le canal s'ouvre avec confirmation vocale) $\rightarrow$ parlez $\rightarrow$ terminez en disant **« Terminé »** (le canal se ferme et déclenche l'analyse).

```text
       [ Pilote (Voix) ]
              │  (PTT relâché ou « Terminé »)
              ▼
   [ Faster-Whisper CUDA ] ──> [ GPT-4o-mini ]
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
       [ Télémétrie / EDSM / Spansh ]           [ Action de bord VoiceAttack ]
          (Function Calling Python)                [EXECUTE:Nom_Commande]
                 │                                       │
                 ▼                                       ▼
       [ Réponse Edge-TTS ]                 [ Simulation Touche .binds ]
```

---

## 📚 Documentation complémentaire

- 🛠️ **[Guide d'Installation Complet (INSTALLATION.md)](INSTALLATION.md) :**
  - Prérequis système, installation des dépendances, règle Non-Admin VoiceAttack et résolution des problèmes fréquents.
- 📖 **[Guide d'Utilisation Complet (GUIDE_UTILISATEUR.md)](GUIDE_UTILISATEUR.md) :**
  - Architecture détaillée, mode Mains Libres, mode d'emploi des modes **Dictée** et **Épellation**, catalogue exhaustif des requêtes et ordres vocaux.
- ⚙️ **[Guide de Personnalisation (PERSONNALISATION.md)](PERSONNALISATION.md) :**
  - Comment modifier le nom, la voix, la personnalité d'Oscar, ajouter de nouveaux vaisseaux et créer de nouvelles commandes VoiceAttack.

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
├── README.md                # Présentation et guide d'installation général
├── INSTALLATION.md          # Guide d'installation pas-à-pas et dépannage
├── GUIDE_UTILISATEUR.md     # Manuel complet des commandes vocales et modes de saisie
├── PERSONNALISATION.md      # Guide des personnalisations avancées
├── data/                    # Données persistantes
│   ├── commandes_vaisseau.txt           # Liste des macros VoiceAttack
│   ├── journal_de_bord.txt              # Archives et mémoires de session
│   ├── flotte_cmdr.json                 # Cache local de la flotte et configurations
│   └── Profil IA ELite Dangerous-Profile.vap  # Profil VoiceAttack
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
