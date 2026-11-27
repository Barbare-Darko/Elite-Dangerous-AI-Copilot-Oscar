# 🚀 OSCAR — Documentation Complète (v17.1)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Windows 64-bit](https://img.shields.io/badge/OS-Windows%2010%2F11%2064--bit-0078D6.svg)](#prérequis-système--logiciels)
[![VoiceAttack](https://img.shields.io/badge/VoiceAttack-v1.16+-purple.svg)](https://voiceattack.com/)
[![Faster-Whisper CUDA](https://img.shields.io/badge/STT-Faster--Whisper%20CUDA-green.svg)](https://github.com/SYSTRAN/faster-whisper)
[![OpenAI GPT-4o-mini](https://img.shields.io/badge/Cerveau-GPT--4o--mini-orange.svg)](https://openai.com/)
[![Edge-TTS](https://img.shields.io/badge/TTS-Edge--TTS%20Neural-teal.svg)](https://github.com/rany2/edge-tts)

> **Langue :** 🇫🇷 Français *(manuel 100 % autonome : présentation, installation, guide complet d'utilisation avec exemples, personnalisation et tableau intégral des commandes).*

---

## 🧭 Sommaire

- [Introduction — Découvrir Oscar (v17.1)](#introduction--découvrir-oscar-v171)
  - [Combien coûte Oscar ? (Gratuité & budget réel)](#combien-coûte-oscar--gratuité--budget-réel)
  - [Aperçu de ce qu'Oscar sait faire](#aperçu-de-ce-quoscar-sait-faire)
  - [Prérequis système & logiciels](#prérequis-système--logiciels)
  - [Organisation des fichiers du projet](#organisation-des-fichiers-du-projet)
- [Chapitre 1 — Installation & Mise en service](#chapitre-1--installation--mise-en-service)
  - [1.1 Emplacement du projet & dépendances Python](#11-emplacement-du-projet--dépendances-python)
  - [1.2 Configuration des clés API et chemins (`secrets.json`)](#12-configuration-des-clés-api-et-chemins-secretsjson)
  - [1.3 Configuration de VoiceAttack (Règle Non-Admin)](#13-configuration-de-voiceattack-règle-non-admin)
  - [1.4 Synchronisation sécurisée des touches (`sync_binds.py`) & réglages Elite Dangerous](#14-synchronisation-sécurisée-des-touches-sync_bindspy--réglages-elite-dangerous)
  - [1.5 Optionnel — Vision Hybride (OpenAI ou Ollama local) & Mode Photo](#15-optionnel--vision-hybride-openai-ou-ollama-local--mode-photo)
  - [1.6 Premier démarrage & vérifications](#16-premier-démarrage--vérifications)
  - [1.7 Dépannage rapide](#17-dépannage-rapide)
- [Chapitre 2 — Guide d'Utilisation (En vol, en VRS & À pied)](#chapitre-2--guide-dutilisation-en-vol-en-vrs--à-pied)
  - [2.1 Tout ce que vous pouvez demander à Oscar (Exemples concrets)](#21-tout-ce-que-vous-pouvez-demander-à-oscar-exemples-concrets)
  - [2.2 Parler à Oscar : PTT, Mains Libres & interruption vocale](#22-parler-à-oscar--ptt-mains-libres--interruption-vocale)
  - [2.3 Parler naturellement : synonymes de verbes & sécurité](#23-parler-naturellement--synonymes-de-verbes--sécurité)
  - [2.4 HUD Overlay transparent (séparation stricte HUD vs ATH)](#24-hud-overlay-transparent-séparation-stricte-hud-vs-ath)
  - [2.5 Exploration, Analyse FSS, Portefeuille & Navigation proactive](#25-exploration-analyse-fss-portefeuille--navigation-proactive)
  - [2.6 Mode À pied (Odyssey) : Outils, Armes, Roues radiales & Alertes survie](#26-mode-à-pied-odyssey--outils-armes-roues-radiales--alertes-survie)
  - [2.7 Vision ("Regarde") & Mode Photo ("Prends une photo")](#27-vision-regarde--mode-photo-prends-une-photo)
  - [2.8 Commerce, Équipement (Spansh), Distances (EDSM), Flotte & Télémétrie](#28-commerce-équipement-spansh-distances-edsm-flotte--télémétrie)
  - [2.9 Modes Texte gratuits (0 jeton) : Dictée & Épellation](#29-modes-texte-gratuits-0-jeton--dictée--épellation)
- [Chapitre 3 — Personnalisation & Maintenance](#chapitre-3--personnalisation--maintenance)
  - [3.1 Identité, personnalité et voix neurale (Edge-TTS)](#31-identité-personnalité-et-voix-neurale-edge-tts)
  - [3.2 Raccourci PTT interne & délais clavier DirectX](#32-raccourci-ptt-interne--délais-clavier-directx)
  - [3.3 Personnaliser le HUD Overlay (`"hud"`)](#33-personnaliser-le-hud-overlay-hud)
  - [3.4 Configurer la Vision & le Mode Photo (`"vision"`)](#34-configurer-la-vision--le-mode-photo-vision)
  - [3.5 Configurer la Navigation proactive (`"navigation_proactive"`)](#35-configurer-la-navigation-proactive-navigation_proactive)
  - [3.6 Personnaliser les synonymes de verbes, d'objets et les modes texte](#36-personnaliser-les-synonymes-de-verbes-dobjets-et-les-modes-texte)
  - [3.7 Ajouter un nouveau vaisseau d'Elite Dangerous](#37-ajouter-un-nouveau-vaisseau-delite-dangerous)
  - [3.8 Ajouter ou modifier des commandes VoiceAttack](#38-ajouter-ou-modifier-des-commandes-voiceattack)
  - [3.9 Codex local & mise à jour galactique](#39-codex-local--mise-à-jour-galactique)
- [Annexe — Tableau Récapitulatif Complet des Commandes](#annexe--tableau-récapitulatif-complet-des-commandes)
  - [A.1 Commandes intelligentes & locales gérées directement par Oscar](#a1-commandes-intelligentes--locales-gérées-directement-par-oscar)
  - [A.2 Grand tableau des 110 actions (Vaisseau, VRS, À pied & Général)](#a2-grand-tableau-des-110-actions-vaisseau-vrs-à-pied--général)
  - [A.3 Les 4 commandes système VoiceAttack](#a3-les-4-commandes-système-voiceattack)

---

# Introduction — Découvrir Oscar (v17.1)

**Oscar** est un copilote vocal intelligent, sarcastique et réactif conçu pour les commandants d'**Elite Dangerous** (*Odyssey* & *Horizons*), utilisable aussi bien sur écran plat (avec ou sans **Tobii Eye Tracker 5**) qu'en réalité virtuelle (**Meta Quest 3**).

Connecté en direct aux journaux du jeu et aux grandes bases communautaires (**Spansh**, **EDSM**, **EDAstro**), il pilote votre vaisseau, votre VRS et votre combinaison à la voix, surveille vos constantes vitales et vos boucliers, analyse les systèmes que vous explorez, regarde à travers votre verrière et vous informe via un petit **HUD transparent** — le tout **sans aucun droit Administrateur** et sans jamais écraser vos commandes HOTAS.

## Combien coûte Oscar ? (Gratuité & budget réel)

**La quasi-totalité des briques d'Oscar est 100 % gratuite :** le projet lui-même (open-source), Python, la reconnaissance vocale locale GPU (`Faster-Whisper`), la voix neurale Microsoft (`Edge-TTS`), le HUD transparent et les APIs galactiques (Spansh, EDSM, EDAstro).

Seuls **deux éléments externes** sont payants :

| Élément | Type de coût | Ordre de prix indicatif |
| :--- | :--- | :--- |
| **VoiceAttack** | Achat unique (Steam ou site officiel) | **~10 à 12 €** une seule fois *(nécessaire pour dépasser la limite de 20 commandes de la version d'essai)*. |
| **API OpenAI (`gpt-4o-mini`)** | Facturation à l'usage (crédit prépayé sans abonnement obligatoire) | **~0,05 € à 0,15 € par heure de jeu actif** en usage normal (commandes vocales + questions + quelques analyses Vision), soit **environ 2 à 5 € pour un mois** de jeu régulier. |

> 💡 **Bon à savoir :** De nombreuses fonctions d'Oscar consomment **0 jeton OpenAI** (donc 0 €) : l'affichage/masquage du HUD, le Mode Photo, la Navigation proactive (arrivée système, honk, retour maison), les alertes automatiques (boucliers, combat, oxygène), le Mode Dictée et le Mode Épellation !

> 🔑 **Comment obtenir et créditer une clé API OpenAI (principe du pré-achat) ?**
> 1. **Attention :** l'API OpenAI est **séparée** d'un éventuel abonnement ChatGPT Plus — inutile de payer 20 €/mois !
> 2. Rendez-vous sur la plateforme dédiée **[platform.openai.com](https://platform.openai.com/)** et connectez-vous (ou créez un compte).
> 3. Cliquez sur l'icône **Engrenage (Settings)** en haut à droite → menu **Billing** → **Add to credit balance** pour pré-acheter un petit crédit (par exemple **5 $ ou 10 $**, sans abonnement mensuel). *(Astuce : laissez **Auto-recharge** désactivé pour garder une maîtrise totale de votre budget.)*
> 4. Allez ensuite dans **Dashboard → API keys** (ou *Settings → API keys*) → **Create new secret key**, copiez immédiatement la clé qui commence par `sk-proj-...` et collez-la dans votre fichier `secrets.json`.

## Aperçu de ce qu'Oscar sait faire

Voici **quelques exemples seulement** parmi tout ce qu'Oscar est capable d'accomplir. Le logiciel est conçu pour fonctionner **le plus efficacement possible en langage naturel** : inutile d'apprendre par cœur des commandes vocales rigides, parlez-lui simplement comme à un vrai copilote !

| Ce que vous demandez | Ce qu'Oscar fait / répond |
| :--- | :--- |
| *« Sors le train d'atterrissage »* / *« Affiche le FSS »* | Exécute immédiatement la commande en jeu et confirme brièvement à la voix (*« C'est fait ! »*, *« FSS activé ! »*). |
| *« Est-ce que tu vois des planètes intéressantes dans ce système ? »* | Analyse votre scan FSS, affiche sur le HUD les cibles triées par distance (`P.1 422SL 1b ~5-10M`, matériaux rares…) et vous résume quoi cartographier ou explorer. |
| *« Quel est le montant de mon portefeuille d'exploration ? »* | Calcule vos données non vendues à bord (Cartographie, Exobiologie avec bonus ×5 et prélèvements en cours, bons Codex) et les affiche sur le HUD. |
| *« Sélectionne la prochaine destination de l'itinéraire »* | Verrouille votre prochain saut — et si le jeu a oublié la route après un débarquement, fait un aller-retour éclair sur la Carte Galactique pour la recharger tout seul ! |
| *« Regarde, c'est quoi cette nébuleuse rouge ? »* / *« C'est une plante ? »* | Observe votre écran, croise avec votre position et votre Codex, identifie la nébuleuse ou la plante (ou vous dit franchement si ce n'est qu'un vulgaire caillou !). |
| *« Prends une photo »* | Masque son HUD et l'interface caméra du jeu, sauvegarde un PNG en résolution native, puis rétablit tout automatiquement. |
| *« Sors l'outil de la combinaison »* / *« Prends l'outil suivant »* | Équipe le bon outil à pied sans jamais risquer de dégainer une arme en station, et évite de le ranger par erreur si vous le tenez déjà. |
| *« Où vendre mon Platine au meilleur prix à 100 années-lumière ? »* | Interroge Spansh en vérifiant la taille de PAD de votre vaisseau, affiche la meilleure station sur le HUD et copie son système dans votre presse-papiers. |
| *« Mode dictée »* → *« Salut les commandants ! »* → *« Envoi »* | Écrit votre message dans le chat en jeu (ou Discord) et l'envoie sans toucher au clavier, à 0 jeton. |
| *(Automatique, sans rien dire)* | Vous alerte en temps réel si vos boucliers tombent, si on vous intercepte, si votre oxygène à pied baisse, ou vous salue à votre retour dans votre système maison ! |

## Prérequis système & logiciels

| Élément | Recommandation | Remarques |
| :--- | :--- | :--- |
| **OS** | Windows 10 / 11 (64-bit) | Exécution impérative en **mode utilisateur normal** (aucun droit Administrateur). |
| **Python** | Python **3.10+** | Cocher **`Add Python to PATH`** lors de l'installation ([python.org](https://www.python.org/downloads/)). |
| **Carte graphique** | NVIDIA GTX 1060 / RTX (6 Go+ VRAM) | Support **CUDA** recommandé pour une reconnaissance vocale quasi instantanée (< 0,2 s) *(fonctionne aussi sur CPU plus lentement)*. |
| **Elite Dangerous** | Mode **Sans bordure** (*Borderless*) | Requis pour afficher le HUD Overlay au-dessus du jeu et pour la Vision / Mode Photo. |
| **VoiceAttack** | v1.16+ (Steam ou Standalone) | Licence complète recommandée pour les 121 macros. **Mode Non-Administrateur obligatoire.** |
| **Clé API OpenAI** | Compte [platform.openai.com](https://platform.openai.com/) | Crédits prépayés (quelques euros suffisent pour des mois). |
| **Clé API EDSM** | *(Optionnelle, gratuite)* | Disponible sur [edsm.net](https://www.edsm.net/) pour enrichir la position et les systèmes proches. |
| **Ollama** | *(Optionnel)* | Uniquement si vous souhaitez tester la Vision 100 % locale au lieu d'OpenAI. |

## Organisation des fichiers du projet

```text
Elite-Dangerous-AI-Copilot-Oscar/
├── IA_Elite.py              # Orchestrateur principal (boucle PTT, Barge-in, HUD, Vision, sécurité, itinéraire)
├── IA_Elite.bat             # Lanceur Windows (démarre VoiceAttack puis Oscar)
├── sync_binds.py            # Assistant non destructif d'injection des touches secondaires (.binds)
├── config_oscar.json        # Paramètres personnalisables (identité, voix, HUD, Vision, navigation, synonymes)
├── secrets.json             # Vos clés API et chemins locaux (à créer depuis secrets.example.json)
├── requirements.txt         # Dépendances Python à installer
├── DOCUMENTATION_FR.md      # Ce manuel complet en français (+ version DOCUMENTATION_FR.pdf)
├── data/
│   ├── commandes_vaisseau.txt           # Liste des macros VoiceAttack reconnues par Oscar
│   ├── Barbare Darko-Profile.vap        # Profil VoiceAttack complet (121 macros + 4 commandes PTT)
│   ├── HOTAS TOUS MODES.4.2.binds       # Profil Elite Dangerous de référence multi-contextes
│   ├── codex_ed.json                    # Base locale (979 nébuleuses/POIs, 15 genres exobio, géologie)
│   ├── codex_cmdr.json                  # Historique personnel CMDR généré depuis vos journaux
│   ├── flotte_cmdr.json                 # Cache local de votre flotte et de ses configurations
│   ├── hud_positions.json               # Positions mémorisées du HUD par vue Elite Dangerous
│   └── journal_de_bord.txt              # Mémoire conversationnelle condensée d'Oscar
└── modules/                 # Moteurs Python spécialisés (STT, TTS, HUD, Vision, Codex, Télémétrie, APIs, Cerveau)
```

---

# Chapitre 1 — Installation & Mise en service

Ce chapitre vous accompagne pas-à-pas pour installer et configurer Oscar proprement, **sans droit Administrateur** et sans toucher à vos raccourcis HOTAS principaux.

## 1.1 Emplacement du projet & dépendances Python

1. **Placez le dossier dans votre espace utilisateur Windows**, par exemple :
   ```text
   C:\Users\<VotreNom>\Documents\IA Elite
   ```
   > ⚠️ **À éviter impérativement :** Ne placez jamais Oscar dans `C:\Program Files` ou `C:\Program Files (x86)`. Ces dossiers protégés forcent le mode Administrateur et provoquent des blocages Windows (UIPI) entre Python, VoiceAttack et Elite Dangerous.

2. **Installez les dépendances Python** en ouvrant un terminal (`cmd` ou PowerShell) dans ce dossier :
   ```cmd
   cd /d "C:\Users\<VotreNom>\Documents\IA Elite"
   pip install -r requirements.txt
   ```
   *Installe automatiquement : `faster-whisper`, `sounddevice`, `numpy`, `keyboard`, `openai`, `edge-tts`, `pywin32`, `requests` et `Pillow`.*

## 1.2 Configuration des clés API et chemins (`secrets.json`)

Vos clés API et chemins locaux sont regroupés dans **`secrets.json`** (ne partagez jamais ce fichier).

1. Copiez le fichier modèle fourni :
   ```cmd
   copy secrets.example.json secrets.json
   ```
2. Ouvrez `secrets.json` dans un éditeur de texte et renseignez vos paramètres :
   ```json
   {
     "openai_api_key": "sk-proj-VOTRE_CLE_API_OPENAI_ICI",
     "edsm_api_key": "VOTRE_CLE_API_EDSM_OPTIONNELLE",
     "cmdr_name": "VotreNomCommandant",
     "chemins": {
       "dossier_journaux_ed": "%USERPROFILE%\\Saved Games\\Frontier Developments\\Elite Dangerous",
       "chemin_voiceattack": "C:\\Program Files (x86)\\Steam\\steamapps\\common\\VoiceAttack\\VoiceAttack.exe"
     }
   }
   ```
   * **`openai_api_key`** : clé API OpenAI (`sk-...`).
   * **`edsm_api_key`** *(optionnelle)* : clé gratuite depuis votre compte EDSM.
   * **`cmdr_name`** : votre nom de commandant en jeu.
   * **`dossier_journaux_ed`** : laissez la valeur par défaut (emplacement officiel Frontier).
   * **`chemin_voiceattack`** : vérifiez le chemin vers votre exécutable `VoiceAttack.exe` (Steam ou Standalone).

## 1.3 Configuration de VoiceAttack (Règle Non-Admin)

1. **Désactivez impérativement le mode Administrateur :**
   * Ouvrez **VoiceAttack** → icône **Clé à molette (Options)** → onglet **System / Advanced**.
   * Vérifiez que **« Run VoiceAttack as an Administrator » est bien DÉCOCHÉE**, puis cliquez sur **OK**.
2. **Importez le profil Oscar :**
   * Dans VoiceAttack, ouvrez le gestionnaire de profils → **Import Profile**.
   * Sélectionnez **`data/Barbare Darko-Profile.vap`**.
3. **Configurez votre bouton Push-To-Talk (PTT) :**
   * Le raccourci interne entre VoiceAttack et Oscar est **`Ctrl + Shift + F9`** (sans `Alt` pour éviter tout conflit avec les menus Windows).
   * Assignez votre bouton HOTAS favori aux commandes **`COM_IA_ON`** (enfoncement → `Key Down Ctrl+Shift+F9`) et **`COM_IA_OFF`** (relâchement → `Key Up Ctrl+Shift+F9`).
   * **Mode Mains Libres (optionnel) :** les commandes vocales **`Oscar`** et **`Terminé`** pilotent ce même canal sans bouton.

> 💡 **Conseil micro :** Oscar fonctionne sur un simple micro de webcam grâce à son filtrage de bruit intégré, mais un **micro-casque** ou un micro directionnel de bureau offre une reconnaissance nettement plus confortable en environnement bruyant.

## 1.4 Synchronisation sécurisée des touches (`sync_binds.py`) & réglages Elite Dangerous

Pour qu'Oscar puisse actionner vos commandes en jeu **sans jamais écraser votre configuration HOTAS principale**, exécutez :

```cmd
py sync_binds.py
```

* **Ce que fait `sync_binds.py` :**
  * Il lit votre fichier `.binds` actif (sans le modifier), crée une **nouvelle copie dédiée** (ex. `MonProfil_Oscar.4.2.binds`), et remplit uniquement les emplacements libres de la colonne **Secondaire (`<Secondary>`)**.
  * Vous pouvez tester sans risque avant de l'appliquer avec `py sync_binds.py --simulate`.

* **Réglages indispensables dans Elite Dangerous :**
  1. **Affichage :** allez dans *Options → Graphismes → Affichage* et choisissez le mode **Sans bordure** (*Borderless*) — indispensable pour superposer le HUD et activer la Vision / Mode Photo.
  2. **Sélection du profil dans les 4 onglets de commandes :** allez dans *Options → Commandes* et sélectionnez votre nouveau profil **`..._Oscar`** dans **chacune des 4 catégories** :
     * **Commandes générales**
     * **Commandes de vaisseau**
     * **Commandes du VRS**
     * **Commandes à pied**
     
     Puis cliquez sur **Appliquer**.
  3. **Astuce HOTAS en mode ACS/FSS :** vérifiez dans *Commandes de vaisseau → Analyse complète du système (ACS)* que votre bouton PTT HOTAS (ex. `Joy_3`) n'est pas également affecté à **« Afficher l'aide »** (`ExplorationFSSShowHelp`), sinon parler pendant un scan ouvrira la fenêtre d'aide du jeu.

> ⚠️ **Important si vous utilisez des profils `.binds` différents selon les modes de jeu** (par exemple un profil HOTAS pour le vaisseau et un profil clavier/souris pour le mode À pied) :  
> Un fichier `.binds` dans Elite Dangerous contient les 4 sections, mais le jeu permet de choisir un preset différent par onglet. Si c'est votre cas, **lancez `sync_binds.py` sur chacun de vos fichiers `.binds` actifs** (en le sélectionnant dans la liste proposée par le script), puis appliquez le profil `..._Oscar` correspondant dans chaque onglet (*Général*, *Vaisseau*, *VRS*, *À pied*).

## 1.5 Optionnel — Vision Hybride (OpenAI ou Ollama local) & Mode Photo

La Vision (*« Regarde… »*) et le Mode Photo (*« Prends une photo »*) sont **100 % optionnels** et réglables dans `config_oscar.json` (section `"vision"`).

* **Option A — OpenAI Direct (`"moteur": "openai"`, fortement recommandé par défaut) :**
  * Zéro installation supplémentaire, **0 Mo de VRAM utilisée**, réponse rapide (~2–3 s) et qualité d'analyse nettement supérieure.
  * La consommation sur `gpt-4o-mini` reste **très contenue** (quelques fractions de centime par image analysée).
* **Option B — Ollama 100 % Local (`"moteur": "ollama"`) :**
  * Utile uniquement si vous souhaitez ne jamais envoyer d'image vers le cloud.
  * > ⚠️ **À savoir avant de choisir Ollama :** les performances de reconnaissance visuelle en local (lecture de l'ATH, plantes Odyssey, détails fins) sont **largement moins bonnes et plus lentes** qu'avec OpenAI Direct, tout en consommant temporairement de la VRAM sur votre GPU. Vu le coût très faible d'OpenAI, l'option A reste préférable dans la plupart des cas.
  * Si vous souhaitez tout de même le tester : installez Ollama (`winget install Ollama.Ollama`), téléchargez `ollama pull qwen2.5vl:7b` (GPU ≥ 10–12 Go VRAM) ou `qwen2.5vl:3b` (GPU 6–8 Go VRAM), puis réglez `"moteur": "ollama"` et `"keep_alive": 0` dans `config_oscar.json`.

## 1.6 Premier démarrage & vérifications

1. Double-cliquez sur **`IA_Elite.bat`** *(ou lancez `py IA_Elite.py` dans un terminal)*.
2. VoiceAttack démarre, Faster-Whisper se charge sur votre GPU, votre historique personnel est synchronisé en lecture seule et Oscar vous salue de vive voix.
3. **3 tests rapides pour vérifier que tout répond :**
   * *« Affiche le HUD »* → la fenêtre transparente apparaît par-dessus Elite Dangerous.
   * *« Affiche la carte système »* → la carte s'ouvre en jeu.
   * Appuyez sur votre PTT pendant qu'Oscar parle → il se coupe net (*Barge-in*) pour vous écouter.

## 1.7 Dépannage rapide

| Symptôme | Cause probable | Solution |
| :--- | :--- | :--- |
| Oscar parle mais rien ne se passe en jeu | VoiceAttack tourne en mode Administrateur (blocage UIPI) ou le profil `..._Oscar` n'est pas sélectionné dans les 4 onglets | Décochez *Run VoiceAttack as an Administrator*, puis sélectionnez `..._Oscar` dans *Général*, *Vaisseau*, *VRS* et *À pied*. |
| Le HUD n'apparaît pas ou la Vision capture du noir | Elite Dangerous est en *Plein écran exclusif* | Passez le jeu en mode **Sans bordure** (*Borderless*) et vérifiez `pip install Pillow`. |
| Transcription lente (> 2 s) | Faster-Whisper tourne sur CPU faute de CUDA | Vérifiez vos pilotes NVIDIA ; `IA_Elite.py` charge automatiquement les DLL CUDA de votre environnement Python. |
| Le Mode Photo garde `IU [JOYSTICK]` dans un coin | Délai de fondu de l'ATH caméra trop court | Vérifiez `"delai_apres_masquage_ath": 3.5` dans `config_oscar.json`. |
| La dictée n'écrit pas dans le chat | Le champ texte n'a pas le focus | Cliquez dans la zone de saisie du chat avant de dicter. |
| Le mot-clé *« Oscar »* ne répond pas | Mauvais micro dans VoiceAttack | VoiceAttack → *Options* → onglet *Audio* → choisissez votre micro actif Windows. |

---

# Chapitre 2 — Guide d'Utilisation (En vol, en VRS & À pied)

## 2.1 Tout ce que vous pouvez demander à Oscar (Exemples concrets)

Voici un tour d'horizon rapide des phrases naturelles que vous pouvez dire à Oscar au quotidien — n'hésitez pas à parler librement, il comprend vos variantes !

### 🛸 Pilotage, Navigation & Combat (Vaisseau & VRS)
| Vous dites | Ce qu'Oscar fait / répond |
| :--- | :--- |
| *« Sors le train d'atterrissage »* / *« Rentre le train »* | Actionne le train d'atterrissage. |
| *« Affiche les orbites »* / *« Enlève les orbites »* | Affiche ou masque les lignes d'orbite. |
| *« Allume les phares »* / *« Active la vision nocturne »* | Pilote l'éclairage et la vision nocturne (vaisseau, VRS ou à pied). |
| *« Ouvre la carte galactique »* / *« Affiche la carte système »* | Ouvre ou ferme les cartes. |
| *« Sélectionne la prochaine destination de l'itinéraire »* | Verrouille le prochain saut (et recharge automatiquement la route via la Carte Galactique si Odyssey l'a oubliée !). |
| *« Active le mode analyse »* / *« Passe en mode combat »* | Bascule l'ATH du cockpit ou du VRS. |
| *« Éjecte un dissipateur thermique »* / *« Lance les paillettes »* | Déclenche vos contre-mesures instantanément. |
| *« Charge une cellule d'énergie »* | Déclenche une cellule de bouclier en vaisseau (et automatiquement une batterie de combinaison si vous êtes à pied). |
| *« Menace principale »* / *« Sous-système suivant »* / *« Chasseur attaque ma cible »* | Pilote le ciblage et les ordres de chasseur embarqué. |
| *« Rappelle le vaisseau »* / *« Active la tourelle »* / *« Enlève le frein de stationnement »* | Pilote votre VRS sur la surface. |

### 🔭 Exploration, FSS & Exobiologie
| Vous dites | Ce qu'Oscar fait / répond |
| :--- | :--- |
| *« Affiche le FSS »* / *« Quitte le FSS »* / *« Quitte le DSS »* | Ouvre ou ferme vos scanners d'exploration. |
| *« Face arrière de la planète »* / *« Face avant de la planète »* | Bascule la vue DSS pour vérifier votre couverture de sondes. |
| *« Est-ce que tu vois des planètes intéressantes dans ce système ? »* | Analyse votre scan FSS, liste les cibles rentables (DSS, exobio avec fourchette réaliste, matériaux rares, anneaux) à la voix et sur le HUD. |
| *« Où trouver du Sélénium dans ce système ? »* | Filtre le système sur le matériau brut demandé avec pourcentage et distance en secondes-lumière. |
| *« Quel est le montant de mon portefeuille d'exploration ? »* | Donne le total non vendu à bord : Cartographie, Exobiologie (espèces prêtes, prélèvements en cours, bonus ×5) et bons Codex. |
| *« Où chercher du Bacterium / Frutexa ? »* | Donne un conseil de terrain/habitat sans toucher aux commandes du vaisseau. |

### 🥾 Mode À pied (Odyssey)
| Vous dites | Ce qu'Oscar fait / répond |
| :--- | :--- |
| *« Sors l'outil de la combinaison »* / *« Prends l'échantillonneur »* | Sort votre outil de combinaison (et vous prévient s'il est déjà en main, sans le ranger !). |
| *« Sors l'énergiseur »* / *« Prends l'analyseur de profil »* | Équipe directement l'outil demandé. |
| *« Prends l'outil suivant »* / *« Prends l'autre outil »* | Passe à l'outil suivant sans jamais risquer de sortir une arme. |
| *« Change le mode de l'outil »* | Inverse le mode actif de l'énergiseur ou de l'analyseur. |
| *« Sors l'arme principale »* / *« Arme secondaire »* / *« Recharge l'arme »* | Pilote vos armes séparément des outils. |
| *« Range l'outil »* / *« Range l'arme »* / *« Rengaine »* | Revient aux mains vides (ne ressort rien si vos mains sont déjà vides). |
| *« Allume la torche »* / *« Active le bouclier »* / *« Soigne-moi »* | Pilote lampe, bouclier personnel et Medkit. |
| *« Affiche la roue d'inventaire »* / *« Affiche la roue d'émoticônes »* / *« Affiche la roue Insight »* | Ouvre la roue demandée en refermant automatiquement la précédente s'il y en avait une d'ouverte ! |

### 👁️ Vision & Mode Photo
| Vous dites | Ce qu'Oscar fait / répond |
| :--- | :--- |
| *« Regarde, on arrive dans combien de temps ? »* | Lit le chrono, la vitesse et la distance sur votre ATH cockpit. |
| *« Regarde, c'est quoi cette plante ? »* / *« Est-ce que c'est une plante ? »* | Identifie l'espèce (ou confirme que c'est un simple rocher !), vérifie votre Codex personnel (`NOUVEAU` vs `DÉJÀ RENCONTRÉ`) et rappelle le bonus ×5 si la planète est vierge. |
| *« Regarde, c'est quoi cette nébuleuse rouge ? »* / *« …cette nébuleuse bleue ? »* | Croise la couleur et la forme visibles avec les nébuleuses proches de votre position galactique. |
| *« Prends une photo »* | Masque le HUD Oscar + l'ATH de la caméra libre, enregistre un PNG natif propre et rétablit l'affichage. |

### 💰 Commerce, Équipement, Flotte & Télémétrie
| Vous dites | Ce qu'Oscar fait / répond |
| :--- | :--- |
| *« Où vendre mon Platine au meilleur prix dans un rayon de 100 années-lumière ? »* | Trouve la meilleure station compatible avec la taille de PAD de votre vaisseau et copie son système dans votre presse-papiers. |
| *« Où acheter un Frame Shift Drive 5A au plus près ? »* | Recherche le module sur Spansh (relance sans limite de distance si rien à proximité). |
| *« Quelle est la distance entre ici et Popocassa ? »* | Calcule la distance 3D exacte et le nombre de sauts estimés. |
| *« Où est garé mon Anaconda ? »* / *« Quelle est la soute de mon Type-8 ? »* | Consulte votre flotte et la configuration mémorisée de vos vaisseaux. |
| *« Combien il me reste de carburant ? »* / *« Quelle est la place libre en soute ? »* | Lit votre télémétrie en direct (`Status.json` / `Cargo.json`). |

### 🖥️ HUD, Chat & Carte Galactique (0 jeton)
| Vous dites | Ce qu'Oscar fait / répond |
| :--- | :--- |
| *« Affiche le HUD »* / *« Enlève le HUD »* | Affiche ou masque le panneau holographique d'Oscar (sans toucher à l'ATH du jeu). |
| *« Mode dictée »* → *(vos phrases)* → *« Envoi »* | Dicte et envoie directement un message dans le chat en jeu ou sur Discord. |
| *« Mode épellation »* → *« S - O - L »* → *« Valider »* | Tape lettre par lettre un nom de système complexe dans la Carte Galactique. |

---

## 2.2 Parler à Oscar : PTT, Mains Libres & interruption vocale

* **Push-To-Talk (recommandé en vol) :** maintenez votre bouton HOTAS (`Ctrl + Shift + F9`), parlez naturellement puis relâchez (une courte marge de fin évite de couper la dernière syllabe).
* **Mains Libres :** dites *« Oscar »*, formulez votre demande, puis dites *« Terminé »*.
* **Interruption instantanée (*Barge-in*) :** pressez votre bouton PTT pendant qu'Oscar parle pour lui couper immédiatement la parole et enchaîner sur un nouvel ordre.
* **Gestion du bruit ambiant :** si un ordre est mâché ou couvert par un bruit de fond, Oscar évite de deviner une commande au hasard et vous répond sobrement : *« Je n'ai pas compris, tu peux répéter ? »*.

## 2.3 Parler naturellement : synonymes de verbes & sécurité

* **Familles de verbes synonymes :** inutile d'apprendre par cœur si telle commande VoiceAttack commence par *Ouvrir*, *Afficher*, *Activer*, *Enlever*, *Masquer*, *Supprimer* ou *Fermer*. Oscar reconnaît automatiquement les grandes familles de verbes (y compris conjugués à l'impératif : *Active*, *Ferme*, *Sors*, *Prends*, *Éteins*, *Efface*, *Éjecte*…).
* **Question vs Commande :** une question d'information (*« Est-ce que tu vois… »*, *« Combien… »*, *« Où est… »*) ne déclenche jamais une commande physique sur le vaisseau.
* **Protection des commandes critiques :** le **Mode Furtif** (`Passer Mode Furtif`) et le **Largage de cargaison** (`Larguer Cargaison`) exigent un ordre littéral explicite — Oscar ne pourra jamais vous faire rôtir ni vider votre soute par erreur.

## 2.4 HUD Overlay transparent (séparation stricte HUD vs ATH)

Le HUD d'Oscar est une petite fenêtre holographique transparente (`25 car. × 10 lignes`) qui reste toujours au-dessus d'Elite Dangerous **sans jamais bloquer vos clics ni voler le focus**.

* **Commandes vocales (0 jeton) :** *« Affiche / Active le HUD »* et *« Enlève / Efface / Ferme le HUD »*.
* **Séparation stricte `HUD` vs `ATH` :** le mot **`HUD`** pilote le panneau d'Oscar ; le mot **`ATH`** reste dédié à l'ATH du jeu (*« Désactive / Active l'ATH »*).
* **Icône micro :** **verte** au repos, **rouge** quand Oscar vous écoute.
* **Placement indépendant par vue :** survolez le haut du panneau à la souris pour le déplacer. Chaque vue (`cockpit`, `carte_systeme`, `carte_galactique`, `a_pied`) mémorise automatiquement sa propre position.

## 2.5 Exploration, Analyse FSS, Portefeuille & Navigation proactive

* **Navigation proactive (0 jeton) :**
  * Accueil spontané au retour dans votre système maison.
  * Silence radio sur les systèmes que vous avez déjà visités.
  * Annonce à l'arrivée dans un nouveau système (première découverte possible ou déjà cartographié) et bilan au Honk (nombre de corps et intérêt d'un scan FSS).
* **Analyse FSS après scan :** présente vos planètes par ordre de pertinence puis par **distance croissante en secondes-lumière** (noms courts en **MAJUSCULES** comme dans l'onglet Navigation), avec une estimation réaliste des gains cartographiques et exobiologiques :
  ```text
  FSS: 19 plan. | Acq 76k
  EXOBIO (x5):
  P.B 1 5476SL 3b ~1,8-5,7M
  MAT. RARES:
  P.B 1 A Sel. 4.1% 5476SL
  P.B 3 Sel. 3.7% 5052SL
  ```
* **Portefeuille d'exploration non vendu :** suit en temps réel vos données à bord depuis la dernière vente ou destruction — Cartographie, Exobiologie (espèces prêtes, prélèvements en cours `1/3`–`2/3`, bonus ×5 vérifié planète par planète) et bons Codex.
* **Rattrapage d'itinéraire (`NavRoute.json`) :** quand vous demandez de cibler le prochain système de l'itinéraire et qu'Odyssey a perdu la route en mémoire, Oscar fait automatiquement un aller-retour éclair sur la Carte Galactique pour reverrouiller votre saut.

## 2.6 Mode À pied (Odyssey) : Outils, Armes, Roues radiales & Alertes survie

* **Outils vs Armes sans confusion :** les 3 outils (*Outil de combinaison*, *Énergiseur*, *Analyseur de profil*) et les armes sont strictement séparés. Redemander un outil déjà en main ne le range pas ; demander *« Prends l'outil suivant »* boucle uniquement sur vos 3 outils ; redemander *« Range l'outil / l'arme »* mains vides ne le ressort pas.
* **Cellule d'énergie intelligente :** *« Utilise / Charge une cellule d'énergie »* déclenche votre batterie de combinaison à pied et votre cellule de bouclier en vaisseau.
* **3 roues radiales sans conflit :** passer directement de la *Roue d'inventaire* à la *Roue d'émoticônes* ou au *Menu / Roue Insight* referme proprement la roue active avant d'ouvrir la suivante.
* **Alertes vocales autonomes (0 jeton) :**
  * **En vol :** Boucliers tombés, Surchauffe, Carburant bas, Interdiction, Combat, Dégâts coque, Module < 50 %.
  * **À pied :** **Oxygène bas (`≤ 30 %`)**, **Oxygène critique (`≤ 15 %`)** et **Santé basse (`≤ 40 %`)** (vocal + HUD).

## 2.7 Vision ("Regarde") & Mode Photo ("Prends une photo")

* **Vision à la demande :** commencez par **`Regarde`** (ou *« Analyse mon écran »*).
  * En **cockpit ultrawide**, Oscar zoome automatiquement sur la zone centrale 16:9 pour lire précisément vos instruments.
  * En **exobiologie / géologie**, il croise l'image avec le scan de la planète et votre Codex personnel (`NOUVEAU` vs `DÉJÀ RENCONTRÉ`), et ne cède pas au biais de confirmation devant un simple rocher.
  * En **astronomie**, il croise la couleur et la forme observées avec les nébuleuses proches autour de votre position.
* **Mode Photo (0 jeton OpenAI) :** dites *« Prends une photo »* → Oscar masque son HUD, masque temporairement l'ATH Caméra Libre si présent (`3,5 s` pour la disparition du bandeau), sauvegarde le PNG pleine résolution dans votre dossier Photos Elite Dangerous, puis rétablit l'affichage.

## 2.8 Commerce, Équipement (Spansh), Distances (EDSM), Flotte & Télémétrie

* **Commerce & Équipement (Spansh) :** prend automatiquement en compte la taille de PAD de votre vaisseau, élargit la recherche sans limite de distance si rien n'est trouvé dans le rayon demandé, affiche le résumé sur le HUD et **copie le système cible dans votre presse-papiers**.
* **Distances 3D & Systèmes proches (EDSM) :** distance exacte et nombre de sauts estimés selon la portée de votre vaisseau actif.
* **Flotte & Configuration des vaisseaux — point important :**
  > 💡 **Comment Oscar connaît votre flotte :**
  > 1. Pour qu'Oscar connaisse la **liste de tous vos vaisseaux stockés et leur localisation**, vous devez avoir ouvert **au moins une fois le Chantier Naval** (*Shipyard*) d'une station en jeu (c'est à ce moment qu'Elite Dangerous écrit votre flotte complète dans les journaux).
  > 2. Pour qu'Oscar connaisse la **configuration détaillée (modules, portée de saut, capacité de soute)** d'un vaisseau précis, il faut être monté **au moins une fois à bord de ce vaisseau** en jeu. Oscar sauvegarde ensuite automatiquement ces fiches dans son cache local (`data/flotte_cmdr.json`) pour toutes vos sessions suivantes.
* **Modules en vol :** l'état On/Off et la santé (%) des modules proviennent du dernier chargement de configuration du jeu (*Loadout*), car Elite Dangerous ne publie pas en temps réel les clics manuels On/Off effectués en vol.

## 2.9 Modes Texte gratuits (0 jeton) : Dictée & Épellation

### Mode Dictée — idéal pour le chat en jeu et Discord
Très pratique pour **envoyer un message dans le chat d'Elite Dangerous** (ou sur Discord) sans lâcher votre HOTAS ni retirer votre casque VR :

1. Ouvrez le chat et placez le curseur dans le champ texte.
2. Dites *« Mode dictée »* (ou *« Active la dictée »*).
3. Dictez votre message par phrases (il s'affiche au fur et à mesure sur le HUD).
4. Dites simplement **« Envoi »** (ou *« Valider »*) à la fin : Oscar valide le message avec `Entrée` et repasse en mode normal !

*Autres commandes disponibles pendant la dictée :* **« Paragraphe suivant / À la ligne »**, **« Corriger »** (efface le dernier bloc), **« Effacer »** (vide tout), **« Stop / Annuler »** (quitte sans envoyer).

### Mode Épellation — pour la recherche dans la Carte Galactique
Conçu pour saisir rapidement des noms de systèmes complexes (ex. `SYNUEFE HW-B A40-1`) dans la Carte Galactique :

1. Cliquez dans la barre de recherche de la Carte Galactique.
2. Dites *« Mode épellation »* (ou *« Lettre par lettre »*).
3. **Épelez librement :** l'utilisation de l'alphabet phonétique (OTAN ou français) **n'est pas obligatoire** ! Vous pouvez tout à fait dicter les lettres normalement (*« S - O - L »*, *« A - B - C - tiret - 4 »*), et n'utiliser les mots phonétiques (*Alpha*, *Bravo*, *Anatole*, *Bernard*…) que pour les lettres qui passent moins bien à votre micro.
   > ⚠️ **Une seule règle si vous utilisez le mode Mains Libres :** pour la lettre **O**, préférez **« Olivier »** (ou *Octave* / *Odile*) plutôt que « Oscar », afin de ne pas réveiller VoiceAttack !
4. **Contrôle :** **« Tiret »** (`-`), **« Espace »**, **« Point »**, **« Corriger »** (efface le dernier caractère), **« Effacer »**, **« Valider / Envoi »**, **« Stop »**.

---

# Chapitre 3 — Personnalisation & Maintenance

> 💡 **Bon à savoir — Prêt à voler dès l'installation :**  
> Oscar est livré avec une **configuration de base complète et directement utilisable** (personnalité, voix neurale, HUD, Vision/Photo, navigation proactive, synonymes…). Vous n'avez **pas** besoin de toucher à `config_oscar.json` pour commencer à voler !  
> Les seuls éléments à adapter au minimum pour démarrer sont :
> 1. Votre **clé API OpenAI** (obligatoire), votre **clé API EDSM** (optionnelle), votre **nom de commandant (`cmdr_name`)** et, si besoin, le **chemin vers `VoiceAttack.exe`** (dans `secrets.json` — voir [1.2](#12-configuration-des-clés-api-et-chemins-secretsjson)).
> 2. Votre **bouton Push-To-Talk (PTT)** dans VoiceAttack (`COM_IA_ON` / `COM_IA_OFF` — voir [1.3](#13-configuration-de-voiceattack-règle-non-admin)).
> 3. La **synchronisation des touches `.binds`** via `sync_binds.py` et le passage en mode **Sans bordure** (voir [1.4](#14-synchronisation-sécurisée-des-touches-sync_bindspy--réglages-elite-dangerous)).

Si vous souhaitez ensuite façonner Oscar à votre image, toutes les options de personnalisation se trouvent dans **`config_oscar.json`** à la racine du projet (aucune ligne de Python à modifier).

## 3.1 Identité, personnalité et voix neurale (Edge-TTS)

```json
{
  "nom_ia": "Oscar",
  "personnalite_ia": "Tu es Oscar, l'ordinateur de bord...",
  "tts": {
    "voix": "fr-FR-HenriNeural",
    "vitesse": "+8%"
  }
}
```

* **Renommer Oscar (`"nom_ia"`) :** choisissez le nom de votre choix (*Sophie*, *Astra*, *Jarvis*…). Si vous utilisez le mode Mains Libres, renommez aussi la commande de réveil dans VoiceAttack et retirez ce prénom de `"alphabet_phonetique"` pour éviter toute collision en Mode Épellation.
* **Personnalité (`"personnalite_ia"`) :** adaptez le ton (sarcastique, militaire strict, bienveillant…). Conservez à la fin la consigne des balises `[MODE_DICTEE]`, `[MODE_EPELLATION]` et l'interdiction du Markdown.
* **Voix françaises Microsoft Edge-TTS recommandées :** `fr-FR-HenriNeural` (homme, défaut), `fr-FR-DeniseNeural` (femme, posée), `fr-FR-EloiseNeural` (femme, dynamique), `fr-FR-RemyMultilingualNeural` (homme), `fr-CA-JeanNeural` / `fr-CA-SylvieNeural`, `fr-BE-GerardNeural`, `fr-CH-FabriceNeural`. Vitesse réglable (ex. `"+0%"`, `"+8%"`, `"+15%"`, `"-5%"`).

## 3.2 Raccourci PTT interne & délais clavier DirectX

```json
{
  "raccourci_ptt": "ctrl+shift+f9",
  "delais_clavier": {
    "delai_apres_ptt_relachement": 0.06,
    "delai_frappe_down": 0.025,
    "delai_frappe_up": 0.015,
    "delai_ctrl_combinaison": 0.035,
    "delai_clipboard_injection": 0.04
  }
}
```

* Si `ctrl+shift+f9` entre en conflit avec un autre logiciel (Discord, OBS, GeForce Experience), modifiez `"raccourci_ptt"` (sans `Alt`) **et** reportez la nouvelle touche dans les 4 commandes VoiceAttack (`COM_IA_ON`, `COM_IA_OFF`, `Oscar`, `Terminé`).
* Augmentez légèrement `"delais_clavier"` si une frappe DirectX est manquée sur une configuration à FPS bas.

## 3.3 Personnaliser le HUD Overlay (`"hud"`)

```json
"hud": {
  "actif_au_demarrage": false,
  "couleur_fond": "#120904",
  "opacite": 0.72,
  "bordure": false,
  "couleur_bordure": "#FF7100",
  "epaisseur_bordure": 1,
  "police": "Consolas",
  "taille_police": 12,
  "couleur_texte": "#FF7100",
  "nb_caracteres_ligne": 25,
  "nb_lignes_max": 10,
  "inclinaison_cockpit": false,
  "angle_cockpit_degres": 3.5,
  "perspective_cockpit": 0.07,
  "positions_par_vue": {
    "cockpit": [80, 120],
    "carte_systeme": [80, 120],
    "carte_galactique": [80, 120],
    "a_pied": [80, 120]
  }
}
```

* Adaptez librement les couleurs hexadécimales (`#FF7100` par défaut) à votre thème **EDHM UI**.
* `inclinaison_cockpit: true` ajoute un léger effet perspective 3D en cockpit.
* Vos déplacements à la souris sont enregistrés automatiquement dans `data/hud_positions.json`.
* Ne mettez pas le mot `ath` dans `commandes_afficher` / `commandes_masquer` (réservé à l'ATH du jeu).

## 3.4 Configurer la Vision & le Mode Photo (`"vision"`)

Voici le bloc `"vision"` complet présent dans `config_oscar.json` :

```json
"vision": {
  "actif": true,
  "photo_active": true,
  "moteur": "openai",
  "modele_openai": "gpt-4o-mini",
  "detail_openai": "high",
  "ollama_url": "http://127.0.0.1:11434",
  "modele": "qwen2.5vl:7b",
  "keep_alive": 0,
  "num_ctx": 6144,
  "timeout_secondes": 60,
  "largeur_max_analyse": 1600,
  "qualite_jpeg_analyse": 85,
  "zoom_ath_ultrawide": true,
  "codex_maj_auto_jours": 30,
  "dossier_photos": "%USERPROFILE%\\Pictures\\Frontier Developments\\Elite Dangerous",
  "prefixe_nom_photo": "Oscar",
  "verifier_ath_photo": true,
  "commande_va_masquer_ath": "Désactiver ATH",
  "delai_apres_masquage_ath": 3.5,
  "reactiver_ath_apres_photo": true,
  "delai_masquage_hud_oscar": 0.15,
  "phrase_attente_analyse": "Je regarde.",
  "prefixes_analyse": ["regarde", "regardes", "regardez", "analyse mon ecran", "analyse l ecran"],
  "commandes_photo": ["prendre une photo", "prends une photo", "photo", "une photo", "capture d ecran"]
}
```

| Clé | Rôle principal |
| :--- | :--- |
| `actif` / `photo_active` | Active ou désactive indépendamment la Vision IA et le Mode Photo. |
| `moteur` | `"openai"` *(recommandé : rapide, précis, 0 VRAM)* ou `"ollama"` *(local, moins précis)*. |
| `modele_openai` / `detail_openai` | Modèle et niveau de précision en mode OpenAI (`"high"` recommandé). |
| `modele` / `keep_alive` | Modèle Ollama (`qwen2.5vl:7b` ou `3b`) ; `0` libère immédiatement la VRAM après chaque analyse. |
| `zoom_ath_ultrawide` | Sur écran 21:9 ou 32:9, recadre la zone centrale 16:9 lors des questions sur les instruments cockpit. |
| `codex_maj_auto_jours` | Fréquence (en jours) de mise à jour automatique des nébuleuses et POIs depuis EDAstro/EDSM. |
| `dossier_photos` / `prefixe_nom_photo` | Emplacement et préfixe des captures PNG (`Oscar_AAAAMMJJ_HHMMSS.png`). |
| `verifier_ath_photo` / `delai_apres_masquage_ath` / `reactiver_ath_apres_photo` | Détecte l'ATH Caméra Libre, attend le fondu (`3.5` s), capture l'image propre, puis rétablit l'ATH. |
| `prefixes_analyse` / `commandes_photo` | Mots déclencheurs reconnus pour la Vision et le Mode Photo. |

## 3.5 Configurer la Navigation proactive (`"navigation_proactive"`)

```json
"navigation_proactive": {
  "actif": true,
  "systeme_maison": "auto",
  "annoncer_arrivee_systeme": true,
  "annoncer_honk": true
}
```

* En mode `"auto"`, Oscar déduit automatiquement votre système maison à partir de l'endroit où sont garés la majorité de vos vaisseaux. Vous pouvez aussi saisir directement un nom exact (ex. `"Popocassa"`).

## 3.6 Personnaliser les synonymes de verbes, d'objets et les modes texte

```json
"synonymes_verbes": {
  "ouvrir_activer": ["activer", "afficher", "ouvrir", "lancer", "éjecter", "mettre", "passer", "allumer", "démarrer", "montrer", "rétablir", "remettre"],
  "fermer_desactiver": ["désactiver", "fermer", "enlever", "masquer", "cacher", "supprimer", "effacer", "couper", "éteindre", "quitter", "retirer", "arrêter"],
  "sortir_prendre": ["sortir", "prendre", "équiper", "déployer", "dégainer"],
  "ranger_rentrer": ["ranger", "rengainer", "rentrer", "rétracter", "cacher"],
  "changer_suivant": ["changer", "basculer", "alterner", "inverser"],
  "charger_utiliser": ["utiliser", "charger", "recharger"]
},
"synonymes_objets": {
  "roue insight": "menu insight",
  "fss": "acs",
  "torche": "phares"
}
```

* Ajoutez vos verbes préférés à l'infinitif dans `"synonymes_verbes"` : les conjugaisons courantes (*Active*, *Ferme*, *Sors*, *Éteins*…) sont automatiquement comprises.
* Dans `"commandes_modes"`, vous pouvez aussi ajouter vos propres mots-clés de dictée (`validation_dictee`, `correction_dictee`, `paragraphe_dictee`, `commandes_sortie`) et vos prénoms dans `alphabet_phonetique`.

## 3.7 Ajouter un nouveau vaisseau d'Elite Dangerous

### Pourquoi est-ce parfois nécessaire ?
Lorsque Frontier ajoute un nouveau vaisseau (ex. *Python Mk II*, *Cobra Mk V*, *Caspian Explorer*), le jeu écrit parfois un **code interne technique** dans ses fichiers (comme `python_nx`, `cobramkv` ou `explorer_nx`) au lieu du vrai nom commercial. Le dictionnaire `"noms_vaisseaux"` de `config_oscar.json` traduit ce code pour qu'Oscar prononce et affiche le bon nom :

```json
"noms_vaisseaux": {
  "mandalay": "Mandalay",
  "python_nx": "Python Mk II",
  "explorer_nx": "Caspian Explorer",
  "cobramkv": "Cobra Mk V",
  "nouveau_code_en_minuscules": "Nom Officiel du Vaisseau"
}
```

### Où trouver le code interne d'un nouveau vaisseau (3 méthodes simples) ?
1. **En ligne (sans ouvrir vos journaux) :** consultez la table communautaire des identifiants vaisseaux sur la documentation **EDCD / Elite Dangerous Journal Docs** (ou dans les exports JSON de **EDSY** / **Coriolis**).
2. **Directement via Oscar :** montez une fois à bord du nouveau vaisseau, puis ouvrez **`data/flotte_cmdr.json`** (fichier léger et lisible) — le code brut du vaisseau y apparaît clairement.
3. **Dans le journal du jeu :** en dernier recours, cherchez `"Ship":` dans votre dernier `Journal.*.log`.

Ajoutez ensuite simplement la paire `"code": "Nom officiel"` en minuscules dans `"noms_vaisseaux"` de `config_oscar.json`.

## 3.8 Ajouter ou modifier des commandes VoiceAttack

> 🚨 **Règle d'or :** Le nom inscrit dans **`data/commandes_vaisseau.txt`** doit être **strictement identique** (majuscules, accents, espaces) au nom de la macro dans **VoiceAttack**, car Oscar exécute `VoiceAttack.exe -command "Nom Exact"`.

* **Ajouter une nouvelle commande :**
  1. Créez la macro dans **VoiceAttack** avec son raccourci clavier.
  2. Assignez ce même raccourci dans la colonne **Secondaire (`<Secondary>`)** dans Elite Dangerous (ou relancez `py sync_binds.py` après export `.vap`).
  3. Ajoutez une ligne contenant le nom exact de la macro dans **`data/commandes_vaisseau.txt`**, puis relancez Oscar.
* **Modifier le raccourci d'une commande existante :** modifiez la touche dans VoiceAttack et dans la colonne `<Secondary>` du jeu — inutile de toucher à `commandes_vaisseau.txt`.
* **Renommer une commande existante :** reportez le même nouveau nom dans VoiceAttack et dans `data/commandes_vaisseau.txt`.

## 3.9 Codex local & mise à jour galactique

* **`data/codex_ed.json`** embarque les 15 genres (~75 espèces) d'exobiologie Odyssey, la géologie et **979 nébuleuses / POIs** mis à jour automatiquement tous les 30 jours depuis EDAstro/EDSM.
* **`data/codex_cmdr.json`** mémorise localement votre historique de découvertes (systèmes visités, espèces scannées, entrées Codex) en lisant vos journaux en lecture seule. Vous pouvez déclencher un rafraîchissement ou diagnostic manuel avec `py -m modules.codex_ed`.

---

# Annexe — Tableau Récapitulatif Complet des Commandes

Toutes les commandes physiques sont injectées dans la colonne **Secondaire (`<Secondary>`)** d'Elite Dangerous : vos commandes principales (HOTAS / manette) restent intactes.

## A.1 Commandes intelligentes & locales gérées directement par Oscar

| Type | Exemples d'ordres vocaux | Fonctionnement |
| :--- | :--- | :--- |
| **HUD Overlay (0 jeton)** | *« Affiche / Active le HUD »*, *« Enlève / Ferme le HUD »* | Pilote la fenêtre overlay d'Oscar sans toucher à l'ATH du jeu. |
| **Mode Photo (0 jeton)** | *« Prends une photo »*, *« Capture d'écran »* | PNG natif + masquage auto HUD Oscar & ATH caméra + rétablissement auto. |
| **Vision Hybride** | *« Regarde ! … »*, *« Analyse mon écran… »* | Analyse visuelle croisée avec les journaux ED, le Codex et la couleur des nébuleuses. |
| **Cycle Outils sécurisé** | *« Prends l'outil suivant »*, *« Prends l'autre outil »* | Cycle entre `Prend Outil Combinaison` → `Active énergiseur` → `Active Analyseur Profil` (jamais d'arme). |
| **Anti-toggle à pied** | Répétition d'un outil déjà en main ou `Range l'outil / l'arme` mains vides | Vérifie votre équipement actif et évite d'envoyer une bascule involontaire. |
| **Cellule d'énergie adaptative** | *« Utilise / Charge une cellule d'énergie »* | `Utilise Cellule Energie` à pied ↔ `Charger Cellule énergie` en vaisseau. |
| **Bascule 3 roues radiales** | *« Affiche la roue d'inventaire / d'émoticônes / Insight »* | Ferme automatiquement la roue active avant d'ouvrir la nouvelle (0 superposition). |
| **Rattrapage itinéraire** | *« Sélectionne la prochaine destination de l'itinéraire »* | Si Odyssey a oublié la route en RAM, aller-retour éclair Carte Galactique automatique. |
| **Modes Texte (0 jeton)** | *« Mode dictée »*, *« Mode épellation »* | Saisie directe chat / Carte Galactique. |

## A.2 Grand tableau des 110 actions (Vaisseau, VRS, À pied & Général)

| Commande VoiceAttack / IA | Touche VoiceAttack | Mode ED | Action dans Elite Dangerous (`<Balise XML>`) | Touche `.binds` (QWERTY/XML) |
| :--- | :--- | :---: | :--- | :--- |
| Activer Assistance Vol / Désactiver Assistance Vol | `1` | **Vaisseau** | Activer / Couper l'assistance de vol (`<ToggleFlightAssist>`) | `Key_Ampersand` |
| Activer Correction Rotationnelle / Désactiver Correction Rotationnelle | `2` | **Vaisseau** | Activer / Couper la correction rotationnelle (`<DisableRotationCorrectToggle>`) | `Key_é` |
| Afficher Orbite / Supprimer Orbite | `3` | **Vaisseau** | Afficher / Masquer les lignes d'orbite (`<OrbitLinesToggle>`) | `Key_DoubleQuote` |
| Cible devant | `4` | **Vaisseau** | Verrouiller la cible devant soi (`<SelectTarget>`) | `Key_Apostrophe` |
| Cible Suivante | `5` | **Vaisseau** | Cibler le vaisseau suivant (`<CycleNextTarget>`) | `Key_LeftParenthesis` |
| Vaisseau précédent | `6` | **Vaisseau** | Cibler le vaisseau précédent (`<CyclePreviousTarget>`) | `Key_Minus` |
| Menace principale | `7` | **Vaisseau** | Cibler la menace principale (`<SelectHighestThreat>`) | `Key_è` |
| Cible Hostile Suivante | `8` | **Vaisseau** | Cibler le vaisseau hostile suivant (`<CycleNextHostileTarget>`) | `Key_Underline` |
| Vaisseau Ennemi Précédent | `9` | **Vaisseau** | Cibler le vaisseau hostile précédent (`<CyclePreviousHostileTarget>`) | `Key_ç` |
| Coéquipier 1 | `A` | **Général** | Cibler le coéquipier 1 (`<TargetWingman0>`) | `Key_A` |
| Coéquipier 2 | `Z` | **Général** | Cibler le coéquipier 2 (`<TargetWingman1>`) | `Key_Z` |
| Coéquipier 3 | `E` | **Général** | Cibler le coéquipier 3 (`<TargetWingman2>`) | `Key_E` |
| Cible du coéquipier | `R` | **Général** | Cibler la cible du coéquipier (`<SelectTargetsTarget>`) | `Key_R` |
| Suivre le coéquipier | `T` | **Général** | Verrouillage navigationnel d'escadrille (`<WingNavLock>`) | `Key_T` |
| Sous-système suivant | `Y` | **Vaisseau** | Cibler le sous-système suivant (`<CycleNextSubsystem>`) | `Key_Y` |
| Sous-système précédent | `U` | **Vaisseau** | Cibler le sous-système précédent (`<CyclePreviousSubsystem>`) | `Key_U` |
| Cibler prochain système de l'itinéraire | `I` | **Vaisseau** | Cibler le prochain système de l'itinéraire (`<TargetNextRouteSystem>`) | `Key_I` |
| Armes Suivantes | `O` | **Vaisseau** | Groupe d'armes suivant (`<CycleFireGroupNext>`) | `Key_O` |
| Armes Précédentes | `Q` | **Vaisseau** | Groupe d'armes précédent (`<CycleFireGroupPrevious>`) | `Key_Q` |
| Déployer Points d'emport / Rentrer Points d'emport | `S` | **Vaisseau** | Déployer / Rentrer les points d'emport (`<DeployHardpointToggle>`) | `Key_S` |
| Passer Mode Furtif *(Verrou sécurité)* | `D` | **Vaisseau** | Activer / Désactiver le mode furtif (`<ToggleButtonUpInput>`) | `Key_D` |
| Ejecter Dissipateur Thermique | `F` | **Vaisseau** | Éjecter un dissipateur thermique (`<DeployHeatSink>`) | `Key_F` |
| Allumer Phares / Eteindre Phares | `F12` | **Vaisseau** | Allumer / Éteindre les phares du vaisseau (`<ShipSpotLightToggle>`) | `Key_F12` |
| Equilibrer Puissance | `G` | **Vaisseau** | Équilibrer la répartition d'énergie (`<ResetPowerDistribution>`) | `Key_G` |
| Réinitialisation Visiocasque | `H` | **Général** | Réinitialisation VR / Suivi de tête (`<HMDReset>`) | `Key_H` |
| Ouvrir Récupérateur Cargaison / Fermer Récupérateur Cargaison | `J` | **Vaisseau** | Ouvrir / Fermer le récupérateur de cargaison (`<ToggleCargoScoop>`) | `Key_J` |
| Larguer Cargaison *(Verrou sécurité)* | `K` | **Vaisseau** | Larguer toute la cargaison (`<EjectAllCargo>`) | `Key_K` |
| Sortir Train Atterrissage / Rentrer Train Atterrissage | `L` | **Vaisseau** | Sortir / Rentrer le train d'atterrissage (`<LandingGearToggle>`) | `Key_L` |
| Charger Cellule énergie | `M` | **Vaisseau** | Déclencher une cellule d'énergie de bouclier (`<UseShieldCell>`) | `Key_M` |
| Lancer Paillettes / Ejecter Paillettes | `ù` | **Vaisseau** | Lancer des paillettes de brouillage (`<FireChaffLauncher>`) | `Key_Apostrophe (XML : Key_ù)` |
| Champ incapacitant | `W` | **Vaisseau** | Neutralisateur de champ Thargoid (`<TriggerFieldNeutraliser>`) | `Key_W` |
| Charger CME | `X` | **Vaisseau** | Contre-mesures électroniques (`<ChargeECM>`) | `Key_X` |
| Activer Vision Nocturne / Désactiver Vision Nocturne | `C` | **Vaisseau** | Activer / Désactiver la vision nocturne (`<NightVisionToggle>`) | `Key_C` |
| Colonisation Système | `V` | **Vaisseau** | Module / balise de colonisation (`<TriggerColonisationModule>`) | `Key_V` |
| Ouvrir Carte Galactique | `B` | **Vaisseau** | Ouvrir la carte galactique (`<GalaxyMapOpen>`) | `Key_B` |
| Ouvrir Carte Système | `N` | **Vaisseau** | Ouvrir la carte du système (`<SystemMapOpen>`) | `Key_N` |
| Activer Mode Combat / Activer Mode Analyse | `,` | **Vaisseau** | Basculer mode ATH Combat / Analyse (`<PlayerHUDModeToggle>`) | `Key_Comma` |
| Activer Mode ACS | `;` | **Vaisseau** | Activer le scanner complet ACS/FSS (`<ExplorationFSSEnter>`) | `Key_SemiColon` |
| Centre Système Actuel | `1` | **Général** | Centrer la carte galactique sur le système actuel (`<GalaxyMapHome>`) | `Key_Ampersand` |
| Activer Frein Stationnement / Enlever Frein Stationnement | `Shift G + F` | **VRS** | Frein de stationnement VRS (`<AutoBreakBuggyButton>`) | `Key_LeftShift + Key_F` |
| Allumer Phares / Eteindre Phares | `F12` | **VRS** | Phares du VRS (`<HeadlightsBuggyButton>`) | `Key_F12` |
| Passer Tourelle / Activer Tourelle / Retour Cockpit / Désactiver Tourelle | `Shift G + T` | **VRS** | Tourelle VRS / Retour cockpit (`<ToggleBuggyTurretButton>`) | `Key_LeftShift + Key_T` |
| Armes Suivantes | `O` | **VRS** | Groupe d'armes suivant en VRS (`<BuggyCycleFireGroupNext>`) | `Key_O` |
| Armes Précédentes | `Q` | **VRS** | Groupe d'armes précédent en VRS (`<BuggyCycleFireGroupPrevious>`) | `Key_Q` |
| Cible devant | `4` | **VRS** | Cibler devant soi en VRS (`<SelectTarget_Buggy>`) | `Key_Apostrophe` |
| Equilibrer Puissance | `G` | **VRS** | Équilibrer l'énergie en VRS (`<ResetPowerDistribution_Buggy>`) | `Key_G` |
| Ouvrir Récupérateur Cargaison / Fermer Récupérateur Cargaison | `J` | **VRS** | Récupérateur de cargaison VRS (`<ToggleCargoScoop_Buggy>`) | `Key_J` |
| Larguer Cargaison *(Verrou sécurité)* | `K` | **VRS** | Larguer la cargaison du VRS (`<EjectAllCargo_Buggy>`) | `Key_K` |
| Rappeler Vaisseau / Renvoyer Vaisseau | `Shift G + R` | **VRS** | Rappeler / Renvoyer le vaisseau (`<RecallDismissShip>`) | `Key_LeftShift + Key_R` |
| Ouvrir Carte Galactique | `B` | **VRS** | Ouvrir la carte galactique en VRS (`<GalaxyMapOpen_Buggy>`) | `Key_B` |
| Ouvrir Carte Système | `N` | **VRS** | Ouvrir la carte système en VRS (`<SystemMapOpen_Buggy>`) | `Key_N` |
| Activer Mode Combat / Activer Mode Analyse | `,` | **VRS** | Mode ATH Combat / Analyse en VRS (`<PlayerHUDModeToggle_Buggy>`) | `Key_Comma` |
| Rappeler Chasseur | `Pavé num 1` | **Vaisseau** | Chasseur : Demander l'arrimage (`<OrderRequestDock>`) | `Key_Numpad_1` |
| Chasseur Défendre | `Pavé num 2` | **Vaisseau** | Chasseur : Posture défensive (`<OrderDefensiveBehaviour>`) | `Key_Numpad_2` |
| Chasseur Feu à volonté | `Pavé num 3` | **Vaisseau** | Chasseur : Feu à volonté (`<OrderAggressiveBehaviour>`) | `Key_Numpad_3` |
| Chasseur Attaquer Cible | `Pavé num 4` | **Vaisseau** | Chasseur : Attaquer ma cible (`<OrderFocusTarget>`) | `Key_Numpad_4` |
| Chasseur Maintenir Formation | `Pavé num 5` | **Vaisseau** | Chasseur : Maintenir la formation (`<OrderHoldFire>`) | `Key_Numpad_5` |
| Chasseur Maintenir Position | `Pavé num 6` | **Vaisseau** | Chasseur : Maintenir la position (`<OrderHoldPosition>`) | `Key_Numpad_6` |
| Chasseur Me Suivre | `Pavé num 7` | **Vaisseau** | Chasseur : Me suivre (`<OrderFollow>`) | `Key_Numpad_7` |
| Chasseur Ouvrir Ordres | `Pavé num 8` | **Vaisseau** | Ouvrir les ordres du chasseur (`<OpenOrders>`) | `Key_Numpad_8` |
| Désactiver ATH / Activer ATH | `1` | **Général** | Masquer / Rétablir l'ATH Caméra Libre (`<FreeCamToggleHUD>`) | `Key_Ampersand` |
| Lecture Pause News | `2` | **Général** | Galnet Audio : Lecture / Pause (`<GalnetAudio_Play_Pause>`) | `Key_é` |
| News Suivante | `3` | **Général** | Galnet Audio : Article suivant (`<GalnetAudio_SkipForward>`) | `Key_DoubleQuote` |
| News Précédente | `4` | **Général** | Galnet Audio : Article précédent (`<GalnetAudio_SkipBackward>`) | `Key_Apostrophe` |
| Effacer Liste Lecture | `5` | **Général** | Galnet Audio : Vider la liste (`<GalnetAudio_ClearQueue>`) | `Key_LeftParenthesis` |
| Quitter ACS | `Q` | **Vaisseau** | Quitter le scanner ACS/FSS (`<ExplorationFSSQuit>`) | `Key_Q` |
| Vue arrière ou avant planète | `F1` | **Vaisseau** | DSS : Inverser la vue avant / arrière (`<ExplorationSAAChangeScannedAreaViewToggle>`) | `Key_F1` |
| Quitter DSS | `F2` | **Vaisseau** | Quitter le scanner de surface DSS (`<ExplorationSAAExitThirdPerson>`) | `Key_F2` |
| Affiche Roue d'inventaire / Enlève Roue d'inventaire | `Ctrl G + A` | **À pied** | Ouvrir / Fermer la roue d'inventaire (`<HumanoidItemWheelButton>`) | `Key_LeftControl + Key_A` |
| Affiche Roue d'émoticomes / Enlève Roue d'émoticomes | `Ctrl G + Z` | **À pied** | Ouvrir / Fermer la roue d'émoticônes (`<HumanoidEmoteWheelButton>`) | `Key_LeftControl + Key_Z` |
| Lance une grenade | `Ctrl G + E` | **À pied** | Lancer une grenade (`<HumanoidThrowGrenadeButton>`) | `Key_LeftControl + Key_E` |
| Recharge Arme | `Ctrl G + R` | **À pied** | Recharger l'arme active (`<HumanoidReloadButton>`) | `Key_LeftControl + Key_R` |
| Change Arme | `Ctrl G + T` | **À pied** | Alterner les armes (`<HumanoidSwitchWeapon>`) | `Key_LeftControl + Key_T` |
| Arme principale | `Ctrl G + Y` | **À pied** | Sélectionner l'arme principale (`<HumanoidSelectPrimaryWeaponButton>`) | `Key_LeftControl + Key_Y` |
| Arme secondaire | `Ctrl G + U` | **À pied** | Sélectionner l'arme secondaire (`<HumanoidSelectSecondaryWeaponButton>`) | `Key_LeftControl + Key_U` |
| *(Emplacement utilitaire — masqué au LLM par sécurité)* | `Ctrl G + I` | **À pied** | Sélectionner l'arme/outil utilitaire (`<HumanoidSelectUtilityWeaponButton>`) | `Key_LeftControl + Key_I` |
| Arme suivante | `Ctrl G + O` | **À pied** | Sélectionner l'arme suivante (`<HumanoidSelectNextWeaponButton>`) | `Key_LeftControl + Key_O` |
| Arme précédente | `Ctrl G + P` | **À pied** | Sélectionner l'arme précédente (`<HumanoidSelectPreviousWeaponButton>`) | `Key_LeftControl + Key_P` |
| Ranger Arme / Ranger Outil | `Ctrl G + ^` | **À pied** | Rengainer / Mains vides (`<HumanoidHideWeaponButton>`) | `Key_LeftControl + Key_LeftBracket (XML : Key_Circumflex)` |
| Grenade suivante | `Ctrl G + $` | **À pied** | Type de grenade suivant (`<HumanoidSelectNextGrenadeTypeButton>`) | `Key_LeftControl + Key_RightBracket (XML : Key_Dollar)` |
| Grenade précédente | `Ctrl G + Q` | **À pied** | Type de grenade précédent (`<HumanoidSelectPreviousGrenadeTypeButton>`) | `Key_LeftControl + Key_Q` |
| Allumer Phares / Eteindre Phares *(Torche)* | `F12` | **À pied** | Lampe torche de combinaison (`<HumanoidToggleFlashlightButton>`) | `Key_F12` |
| Activer Vision Nocturne / Désactiver Vision Nocturne | `C` | **À pied** | Vision nocturne de combinaison (`<HumanoidToggleNightVisionButton>`) | `Key_C` |
| Activer Bouclier / Désactiver Bouclier | `Ctrl G + S` | **À pied** | Bouclier personnel de combinaison (`<HumanoidToggleShieldsButton>`) | `Key_LeftControl + Key_S` |
| Supprime Accréditation | `D` | **À pied** | Effacer le profil d'accréditation volé (`<HumanoidClearAuthorityLevel>`) | `Key_LeftControl + Key_D` |
| Soigne moi / Kit de santé | `Ctrl G + 9` | **À pied** | Utiliser un Medkit (`<HumanoidHealthPack>`) | `Key_RightControl + Key_F` |
| Utilise Cellule Energie | `Ctrl G + G` | **À pied** | Utiliser une batterie de combinaison (`<HumanoidBattery>`) | `Key_LeftControl + Key_G` |
| Grenade Fragmentation | `Ctrl G + H` | **À pied** | Grenade à fragmentation (`<HumanoidSelectFragGrenade>`) | `Key_LeftControl + Key_H` |
| Grenade IEM | `J` | **À pied** | Grenade IEM (`<HumanoidSelectEMPGrenade>`) | `Key_LeftControl + Key_J` |
| Grenade Bouclier | `Ctrl G + K` | **À pied** | Grenade à bouclier (`<HumanoidSelectShieldGrenade>`) | `Key_LeftControl + Key_K` |
| Active énergiseur | `Ctrl G + L` | **À pied** | Équiper l'énergiseur (`<HumanoidSwitchToRechargeTool>`) | `Key_LeftControl + Key_L` |
| Active Analyseur Profil | `Ctrl G + M` | **À pied** | Équiper l'analyseur de profil (`<HumanoidSwitchToCompAnalyser>`) | `Key_LeftControl + Key_M` |
| Prend Outil Combinaison | `Ctrl G + ù` | **À pied** | Équiper l'outil de combinaison (`<HumanoidSwitchToSuitTool>`) | `Key_LeftControl + Key_Apostrophe (XML : Key_ù)` |
| Change Mode Outil | `Ctrl G + *` | **À pied** | Changer le mode de l'outil actif (`<HumanoidToggleToolModeButton>`) | `Key_LeftControl + Key_BackSlash (XML : Key_Asterisk)` |
| Affiche l'aide / Masque l'aide | `Ctrl G + W` | **À pied** | Aide de mission à pied (`<HumanoidToggleMissionHelpPanelButton>`) | `Key_LeftControl + Key_W` |
| Ouvrir Carte Galactique | `B` | **À pied** | Carte galactique à pied (`<GalaxyMapOpen_Humanoid>`) | `Key_B` |
| Ouvrir Carte Système | `N` | **À pied** | Carte système à pied (`<SystemMapOpen_Humanoid>`) | `Key_N` |
| Affiche Panneau Communication / Masque Panneau Communication | `Ctrl G + X` | **À pied** | Panneau de communication à pied (`<FocusCommsPanel_Humanoid>`) | `Key_LeftControl + Key_X` |
| Affiche Panneau Com Rapide / Masque Panneau Com Rapide | `Ctrl G + C` | **À pied** | Panneau Com rapide à pied (`<QuickCommsPanel_Humanoid>`) | `Key_LeftControl + Key_C` |
| Ouvre Menu Insight / Ferme Menu Insight | `Ctrl G + !` | **À pied** | Roue / Menu d'accès Insight (`<HumanoidOpenAccessPanelButton>`) | `Key_LeftControl + Key_Slash (XML : Key_ExclamationPoint)` |
| Affiche Statistique Combat / Masque Statistique Combat | `Ctrl G + B` | **À pied** | Statistiques de zone de conflit (`<HumanoidConflictContextualUIButton>`) | `Key_LeftControl + Key_B` |
| Pointe le doigt | `Ctrl G + 1` | **À pied** | Émoticône 1 (`<HumanoidEmoteSlot1>`) | `Key_LeftControl + Key_Ampersand` |
| Fais un coucou | `Ctrl G + 2` | **À pied** | Émoticône 2 (`<HumanoidEmoteSlot2>`) | `Key_LeftControl + Key_é` |
| Fais un geste d'accord | `Ctrl G + 3` | **À pied** | Émoticône 3 (`<HumanoidEmoteSlot3>`) | `Key_LeftControl + Key_DoubleQuote` |
| Fais un non | `Ctrl G + 4` | **À pied** | Émoticône 4 (`<HumanoidEmoteSlot4>`) | `Key_LeftControl + Key_Apostrophe` |
| Fais un en avant | `Ctrl G + 5` | **À pied** | Émoticône 5 (`<HumanoidEmoteSlot5>`) | `Key_LeftControl + Key_LeftParenthesis` |
| Fais un Stop | `Ctrl G + 6` | **À pied** | Émoticône 6 (`<HumanoidEmoteSlot6>`) | `Key_LeftControl + Key_Minus` |
| Fais un applaudissement | `Ctrl G + 7` | **À pied** | Émoticône 7 (`<HumanoidEmoteSlot7>`) | `Key_LeftControl + Key_è` |
| Fais un salut | `Ctrl G + 8` | **À pied** | Émoticône 8 (`<HumanoidEmoteSlot8>`) | `Key_LeftControl + Key_Underline` |

## A.3 Les 4 commandes système VoiceAttack

| Commande | Déclencheur | Action clavier simulée | Rôle |
| :--- | :--- | :--- | :--- |
| **`COM_IA_ON`** | Bouton HOTAS enfoncé | `Key Down` `Ctrl + Shift + F9` | Interrompt la parole en cours (*Barge-in*) et ouvre l'enregistrement micro Whisper. |
| **`COM_IA_OFF`** | Bouton HOTAS relâché | `Key Up` `Ctrl + Shift + F9` | Ferme l'écoute (+180 ms de marge), transcrit sur GPU et déclenche Oscar. |
| **`Oscar`** | Vocal (*« Oscar »*) | Accusé vocal + `Key Down` `Ctrl + Shift + F9` | Ouvre l'écoute en mode Mains Libres. |
| **`Terminé`** | Vocal (*« Terminé »*) | `Key Up` `Ctrl + Shift + F9` | Clôture et soumet la phrase dictée en mode Mains Libres. |

---

*Projet open-source partagé pour la communauté des pilotes d'Elite Dangerous. Elite Dangerous est une marque déposée de Frontier Developments plc. VoiceAttack est édité par VoiceAttack LLC.*
