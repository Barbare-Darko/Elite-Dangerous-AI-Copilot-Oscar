================================================================================
VERSION FRANÇAISE (FR) — PRÉSENTATION POUR LA PAGE D'ACCUEIL GITHUB (README.md)
================================================================================

# OSCAR — Copilote IA Vocal & Télémétrique pour Elite Dangerous

**Oscar** est un assistant vocal intelligent, sarcastique et proactif conçu pour **Elite Dangerous**. Co-développé en collaboration avec **Gemini (Google)**, ce projet repose sur une architecture hybride combinant la puissance du calcul GPU local (pour la reconnaissance vocale instantanée), les journaux de télémétrie en direct du jeu, les bases de données galactiques communautaires et l'intelligence artificielle générative.

Contrairement aux packs vocaux classiques limités à des phrases préenregistrées, Oscar comprend le langage naturel, analyse l'état réel de votre vaisseau en temps réel et pilote vos commandes via VoiceAttack.

---

## Composants nécessaires & Budget estimé

| Composant | Rôle dans l'architecture | Coût estimé | Où l'obtenir |
| :--- | :--- | :--- | :--- |
| **Elite Dangerous** (Odyssey / Horizons) | Jeu de base et source des fichiers journaux (`Journal.*.log`, `Status.json`, `Cargo.json`, `ModulesInfo.json`) | ~6 € à 25 € (selon promotions) | Steam / Epic Games / Frontier Store |
| **VoiceAttack** | Interface d'écoute, activation par mot-clé ou Push-to-Talk et exécution des macros clavier/HOTAS | **Payant** (~10 € à 12 € / licence unique à vie) | Site officiel VoiceAttack (`voiceattack.com`) ou Steam |
| **Clé API OpenAI (`gpt-4o-mini`)** | Cerveau conversationnel, interprétation des intentions et déclenchement des outils (Function Calling) | **Payant à l'usage** (~0,50 $ pour 1 000 requêtes ; 0 jeton consommé en veille) | Plateforme développeur OpenAI (`platform.openai.com`) |
| **Python 3.10+** | Environnement d'exécution du script principal | **100 % Gratuit** | Site officiel Python (`python.org`) ou Microsoft Store |
| **Faster-Whisper (CUDA / GPU)** | Transcription vocale ultra-rapide et précise en local sur carte graphique NVIDIA | **100 % Gratuit** (Open Source) | Bibliothèque Python (`pip install faster-whisper`) |
| **Edge-TTS (Microsoft Neural)** | Synthèse vocale neurale haute qualité (voix française *Henri* ou *Vivienne* / *Denise*) | **100 % Gratuit** | Bibliothèque Python (`pip install edge-tts`) |
| **APIs EDSM & Spansh** | Données galactiques (distances 3D, systèmes voisins, stations, prix de marché et disponibilité des modules) | **100 % Gratuit** (sans clé API) | Bases communautaires `edsm.net` et `spansh.co.uk` |

---

## Fonctionnalités principales

### 1. Double mode d'activation & Voix Neurale Expressive
* **Activation flexible** : Parlez à Oscar soit par **mot-clé vocal** (ex. *« Oscar... »* via la reconnaissance Windows/VoiceAttack), soit par bouton **Push-to-Talk** dédié sur votre HOTAS, joystick ou clavier (`Ctrl+Shift+Alt+F9`).
* **Compréhension en langage naturel** : Grâce au modèle Whisper exécuté sur GPU, Oscar comprend vos demandes même dans le feu de l'action et corrige automatiquement les approximations phonétiques.
* **Voix neurale naturelle** : Utilise les voix neurales de Microsoft Edge-TTS (voix masculine posée *Henri* ou voix féminine *Vivienne*/*Denise*) avec nettoyage automatique des symboles et intonation naturelle.

### 2. Contrôle complet du vaisseau, du VRS et à pied (125+ commandes)
* Pilote toutes vos actions en jeu via VoiceAttack : train d'atterrissage, points d'emport, écope à cargaison, phares, vision nocturne, mode combat/analyse, gestion des pips, super-navigation, saut hyperespace, cartes système/galactique, lancement de drones, dissipateurs thermiques, paillettes, déploiement du VRS, etc.

### 3. Gestion de carrière, de flotte et d'équipement
* **Suivi de carrière en direct** : Crédits disponibles, progression détaillée de vos rangs (Combat, Commerce, Exploration, Exobiologie, Mercenaire, Empire, Fédération) et inventaire complet de vos matériaux d'ingénieurs.
* **Suivi intégral de la flotte** : Connaît tous vos vaisseaux (actif et stockés en station), leurs noms personnalisés, leur station d'attache exacte, leurs modules équipés, leur portée de saut maximale et leur capacité de soute exacte en tonnes.

### 4. Télémétrie temps réel & Alertes autonomes (0 jeton OpenAI en veille)
* **Consultation à la demande** : Niveau exact de carburant, place libre restante en soute (`Cargo.json`), état actif/inactif et santé de vos modules (`ModulesInfo.json`), répartition des pips et destination verrouillée.
* **Surveillance proactive en arrière-plan** : Un thread dédié analyse `Status.json` et le journal actif plusieurs fois par seconde sans consommer de jetons OpenAI. Oscar vous alerte spontanément par la voix en cas de :
  * Chute ou perte des boucliers.
  * Alerte thermique précoce et surchauffe critique.
  * Carburant bas.
  * Tentative d'interdiction ou attaque ennemie.
  * Dégâts de coque ou module tombant sous 50 % de santé.

### 5. Navigation galactique, Commerce & Équipement (EDSM & Spansh)
* **Calcul de distances 3D** : Calcule la distance exacte en années-lumière entre votre position actuelle et n'importe quel système de la galaxie (Sol, Colonia, systèmes colonisés, etc.).
* **Recherche commerciale et d'équipement intelligente** : Trouve les meilleures stations pour vendre vos minerais au plus cher ou acheter des marchandises et modules (ex. *FSD 5A*, *Fuel Scoop 6A*) en filtrant automatiquement sur la **taille de piste adaptée à votre vaisseau actif** (PAD Large ou Moyen) et votre rayon de recherche (en années-lumière ou en nombre de sauts).
* **Copie automatique dans le presse-papiers** : Dès qu'une station cible est identifiée, le nom du système stellaire est automatiquement copié dans le presse-papiers Windows (`Ctrl+V` prêt à l'emploi dans la carte galactique).

### 6. Mémoire persistante légère
* Conserve un résumé condensé de vos préférences de pilote (`journal_de_bord.txt`) et met en cache les configurations de vos vaisseaux (`flotte_cmdr.json`) afin de limiter la consommation de jetons et garantir des réponses instantanées.


================================================================================
ENGLISH VERSION (EN) — GITHUB HOMEPAGE PRESENTATION (README.md)
================================================================================

# OSCAR — AI Voice & Telemetry Co-Pilot for Elite Dangerous

**Oscar** is a smart, sarcastic, and proactive AI co-pilot built for **Elite Dangerous**. Co-designed in collaboration with **Gemini (Google)**, this project features a hybrid architecture combining local GPU speech recognition, real-time game telemetry logs, community galactic databases, and generative AI.

Unlike traditional voice packs restricted to pre-recorded audio lines, Oscar understands natural language, monitors your ship's live telemetry, and triggers your ship controls through VoiceAttack.

---

## Required Components & Estimated Cost

| Component | Role in the Architecture | Estimated Cost | Where to Get It |
| :--- | :--- | :--- | :--- |
| **Elite Dangerous** (Odyssey / Horizons) | Base game and real-time source for local log files (`Journal.*.log`, `Status.json`, `Cargo.json`, `ModulesInfo.json`) | ~$6 to $25 (depending on sales) | Steam / Epic Games / Frontier Store |
| **VoiceAttack** | Wake-word / Push-to-Talk listener and keyboard/HOTAS macro execution engine | **Paid** (~$10–$12 / one-time lifetime license) | Official VoiceAttack website (`voiceattack.com`) or Steam |
| **OpenAI API Key (`gpt-4o-mini`)** | Conversational brain, intent parsing, and tool execution (Function Calling) | **Pay-as-you-go** (~$0.50 per 1,000 requests; 0 tokens used while idle) | OpenAI Developer Platform (`platform.openai.com`) |
| **Python 3.10+** | Runtime environment for the main assistant script | **100% Free** | Official Python website (`python.org`) or Microsoft Store |
| **Faster-Whisper (CUDA / GPU)** | Ultra-fast, high-accuracy local speech-to-text running on NVIDIA GPUs | **100% Free** (Open Source) | Python package (`pip install faster-whisper`) |
| **Edge-TTS (Microsoft Neural)** | High-quality neural text-to-speech synthesis (natural voices like *Henri*, *Vivienne*, or *Denise*) | **100% Free** | Python package (`pip install edge-tts`) |
| **EDSM & Spansh APIs** | Galactic databases (3D distances, nearby systems, stations, market prices, and outfitting availability) | **100% Free** (no API key required) | Community databases `edsm.net` and `spansh.co.uk` |

---

## Key Features

### 1. Dual Activation Mode & Expressive Neural Voice
* **Flexible Activation**: Trigger Oscar either by **vocal wake-word** (e.g., *"Oscar..."* via Windows/VoiceAttack speech recognition) or via a dedicated **Push-to-Talk button** mapped to your HOTAS, joystick, or keyboard (`Ctrl+Shift+Alt+F9`).
* **Natural Language Understanding**: Powered by GPU-accelerated Whisper, Oscar accurately understands your commands even during intense combat or mining sessions and automatically corrects phonetic transcription quirks.
* **Neural Text-to-Speech**: Uses Microsoft Edge-TTS neural voices for natural intonation, pacing, and expressive delivery without robotic artifacts.

### 2. Full Ship, SRV & On-Foot Control (125+ Commands)
* Controls all your in-game bindings through VoiceAttack: landing gear, hardpoints, cargo scoop, ship lights, night vision, combat/analysis modes, power distributor pips, supercruise, hyperspace jumps, system/galaxy maps, limpets, heat sinks, chaff, SRV deployment, and more.

### 3. Career, Fleet & Outfitting Management
* **Live Career Tracking**: Real-time credit balance, detailed rank progression (Combat, Trade, Exploration, Exobiology, Mercenary, Empire, Federation), and full engineering materials inventory.
* **Complete Fleet Awareness**: Tracks every ship you own (active and stored), custom ship names, exact home stations, outfitted modules, maximum jump range, and exact cargo capacity in tons.

### 4. Real-Time Telemetry & Autonomous Alerts (0 OpenAI Tokens While Idle)
* **On-Demand Status**: Exact fuel levels, remaining free cargo space (`Cargo.json`), active/inactive module states and module health (`ModulesInfo.json`), pip distribution, and locked destination.
* **Proactive Background Monitoring**: A dedicated background thread polls `Status.json` and the active journal multiple times per second with zero OpenAI token usage. Oscar automatically warns you by voice when:
  * Shields go offline.
  * Early thermal warning or critical overheating occurs.
  * Fuel reserves drop low.
  * An interdiction or enemy attack begins.
  * Hull integrity drops or any module health falls below 50%.

### 5. Galactic Navigation, Trading & Outfitting (EDSM & Spansh)
* **3D Distance Calculator**: Computes exact light-year distances between your current location and any star system in the galaxy (Sol, Colonia, newly colonized systems, etc.).
* **Smart Trade & Outfitting Search**: Finds the best stations to sell mined minerals at top prices or buy commodities and ship modules (e.g., *5A Frame Shift Drive*, *6A Fuel Scoop*), automatically filtering by **landing pad size compatible with your active ship** (Large or Medium pad) and your search radius (in light-years or max jumps).
* **Automatic Clipboard Copy**: Whenever a target station is found, the destination star system name is automatically copied to your Windows clipboard, ready to paste (`Ctrl+V`) directly into the Galaxy Map.

### 6. Lightweight Persistent Memory
* Maintains a condensed summary of your pilot preferences (`journal_de_bord.txt`) and caches your fleet loadouts (`flotte_cmdr.json`) to keep token usage minimal and responses instantaneous.
