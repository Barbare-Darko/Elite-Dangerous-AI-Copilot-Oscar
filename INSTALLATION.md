# 🛠️ Guide d'Installation Complet — Copilote Vocal Oscar

Ce guide vous accompagne pas-à-pas pour installer, configurer et lancer **Oscar** sur votre PC en toute sécurité, **sans aucun droit Administrateur requis**, tout en préservant intacte votre configuration matérielle existante (HOTAS, clavier, souris).

---

## 🧭 Sommaire

1. [Prérequis Système & Logiciels](#1-prérequis-système--logiciels)
2. [Étape 1 — Installation des fichiers & Dépendances Python](#étape-1--installation-des-fichiers--dépendances-python)
3. [Étape 2 — Configuration des clés et chemins (secrets.json)](#étape-2--configuration-des-clés-et-chemins-secretsjson)
4. [Étape 3 — Configuration de VoiceAttack (Règle Non-Admin)](#étape-3--configuration-de-voiceattack-règle-non-admin)
5. [Étape 4 — Synchronisation automatique des commandes Elite Dangerous (sync_binds.py)](#étape-4--synchronisation-automatique-des-commandes-elite-dangerous-sync_bindspy)
6. [Étape 5 — Premier Démarrage & Vérification](#étape-5--premier-démarrage--vérification)
7. [Résolution des Problèmes Fréquents (Dépannage)](#résolution-des-problèmes-fréquents-dépannage)

---

## 1. Prérequis Système & Logiciels

Avant de commencer, assurez-vous de disposer des éléments suivants :

| Élément | Version minimale | Remarques |
| :--- | :--- | :--- |
| **Système d'Exploitation** | Windows 10 ou 11 (64-bit) | Tourne en **mode utilisateur standard** (aucun droit Admin requis). |
| **Python** | Python 3.10 ou supérieur | Téléchargeable sur [python.org](https://www.python.org/downloads/). Veillez à **cocher la case `Add Python to PATH`** lors de l'installation. |
| **Carte Graphique (GPU)** | NVIDIA GTX 1060 / RTX recommandée | Pilotes NVIDIA récents avec support **CUDA** pour une transcription vocale ultra-rapide (< 0.2s) via Faster-Whisper. *(Fonctionne aussi sur CPU avec un léger délai).* |
| **VoiceAttack** | Version 1.8+ (Steam ou Standalone) | Version enregistrée recommandée pour bénéficier du profil complet de 121 macros sans limitation. |
| **Clé API OpenAI** | Compte actif sur [platform.openai.com](https://platform.openai.com/) | Utilise le modèle économique et performant **`gpt-4o-mini`** (quelques centimes d'euro par session de jeu). |
| **Clé API EDSM (Optionnelle)** | Gratuite sur [edsm.net](https://www.edsm.net/) | Permet au copilote de vérifier vos coordonnées 3D et votre position si les journaux locaux sont muets. |

---

## Étape 1 — Installation des fichiers & Dépendances Python

### 1.1 Choisir l'emplacement du projet (Règle d'or)
Placez le dossier du projet dans votre espace personnel utilisateur Windows, par exemple :
```text
C:\Users\<VotreNom>\Documents\IA Elite
```
> ⚠️ **À ÉVITER IMPÉRATIVEMENT :** Ne placez jamais ce dossier dans `C:\Program Files` ou `C:\Program Files (x86)`. Windows protège ces dossiers système en écriture, ce qui forcerait l'élévation en mode Administrateur et créerait des conflits de communication entre Python, VoiceAttack et Elite Dangerous.

### 1.2 Installer les dépendances Python
1. Ouvrez une invite de commandes Windows (`cmd`) ou PowerShell.
2. Déplacez-vous dans le dossier du projet :
   ```cmd
   cd /d "C:\Users\<VotreNom>\Documents\IA Elite"
   ```
3. Installez toutes les bibliothèques requises en une seule ligne :
   ```cmd
   pip install -r requirements.txt
   ```
*Le fichier `requirements.txt` installe automatiquement : `faster-whisper`, `sounddevice`, `numpy`, `keyboard`, `openai`, `edge-tts`, `pywin32` et `requests`.*

---

## Étape 2 — Configuration des clés et chemins (`secrets.json`)

Pour protéger vos clés privées et permettre la publication sur GitHub, tous les secrets sont isolés dans `secrets.json` (qui est strictement ignoré par Git).

1. Dans le dossier du projet, faites une copie du fichier `secrets.example.json` et renommez-le en **`secrets.json`** :
   ```cmd
   copy secrets.example.json secrets.json
   ```
2. Ouvrez `secrets.json` avec le Bloc-notes ou votre éditeur favori :
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
3. Renseignez :
   - `"openai_api_key"` : Votre clé secrète OpenAI commençant par `sk-...`.
   - `"cmdr_name"` : Votre nom de pilote en jeu (ex: *« Barbare Darko »*).
   - `"dossier_journaux_ed"` : Laissez la valeur par défaut `%USERPROFILE%\Saved Games\...` (emplacement officiel des journaux de vol d'Elite Dangerous).
   - `"chemin_voiceattack"` : Vérifiez le chemin menant à votre exécutable `VoiceAttack.exe` (Steam ou Standalone).

---

## Étape 3 — Configuration de VoiceAttack (Règle Non-Admin)

### 3.1 Décocher impérativement le mode Administrateur de VoiceAttack
Pour que Python puisse communiquer avec VoiceAttack et pour que VoiceAttack puisse envoyer des frappes matérielles à Elite Dangerous sans blocage de sécurité Windows (UIPI) :
1. Lancez **VoiceAttack**.
2. Cliquez sur l'icône **Clé à molette** (Options).
3. Rendez-vous dans l'onglet **System / Advanced**.
4. Vérifiez que la case **« Run VoiceAttack as an Administrator » est bien DÉCOCHÉE**.
5. Cliquez sur **OK** et redémarrez VoiceAttack si nécessaire.

### 3.2 Importer le profil VoiceAttack
1. Dans VoiceAttack, cliquez sur l'icône **Dossier de profils** $\rightarrow$ **Importer un profil**.
2. Naviguez vers le dossier de votre projet et sélectionnez le fichier :  
   `data/Profil IA ELite Dangerous-Profile.vap` (ou présent à la racine).
3. Cliquez sur **Importer**. Le profil contient l'ensemble des 121 macros de commandes de bord et la gestion du Push-To-Talk.

### 3.3 Configurer votre Push-To-Talk (PTT)
- Le raccourci d'écoute micro est configuré sur **`Ctrl + Shift + F9`** (sans Alt pour éviter tout conflit avec les menus Windows).
- **Sur votre HOTAS / Joystick :** Dans le logiciel de votre périphérique (ex: TARGET, Logitech G Hub, VKB Device Config) ou dans VoiceAttack, assignez votre bouton micro favori pour enfoncer la combinaison `Ctrl + Shift + F9` tant que vous maintenez le bouton appuyé.
- **En mode Mains Libres (sans bouton) :** Vous pouvez aussi simplement dire à la voix *« Oscar »* pour ouvrir l'écoute, puis *« Terminé »* pour clore votre phrase.

---

## Étape 4 — Synchronisation automatique des commandes Elite Dangerous (`sync_binds.py`)

Cette étape est fondamentale pour permettre à Oscar d'exécuter des actions physiques (sortir le train, allumer les phares, ouvrir la soute, cibler, etc.) **sans modifier vos commandes HOTAS principales**.

1. Ouvrez votre terminal dans le dossier du projet :
   ```cmd
   py sync_binds.py
   ```
2. **Ce que fait le script :**
   - Il inspecte votre profil de commandes actif d'Elite Dangerous (ex: `HOTAS TOUS MODES`, `Custom`, etc.).
   - Il crée une **nouvelle copie dédiée et sécurisée** (ex: `Custom_Oscar.4.2.binds`).
   - Il injecte les 110 raccourcis clavier requis **uniquement dans la colonne secondaire (`<Secondary>`)**, laissant votre colonne principale (`<Primary>`) 100 % intacte.
   - Il utilise les codes matériels DirectInput reconnus par le moteur du jeu (résolvant tout problème avec les touches AZERTY spéciales).
   - *(Pour consulter la correspondance exacte de chacune des 110 balises, touches et modes de jeu, reportez-vous au **[Tableau Récapitulatif Complet des Commandes (TABLEAU_COMMANDES.md)](TABLEAU_COMMANDES.md)**).*
3. **Activation en jeu :**
   - Lancez **Elite Dangerous**.
   - Allez dans **Options $\rightarrow$ Commandes**.
   - En haut à droite, dans la liste déroulante des profils, sélectionnez votre nouveau profil :  
     **`..._Oscar`** (ex: *HOTAS TOUS MODES_Oscar* ou *Custom_Oscar*).
   - Cliquez sur **Appliquer**.

---

## Étape 5 — Premier Démarrage & Vérification

1. Double-cliquez sur :
   ```text
   IA_Elite.bat
   ```
   *(Ou lancez en ligne de commande : `py IA_Elite.py`)*
2. Le lanceur ouvre automatiquement VoiceAttack, initialise le modèle Whisper sur votre GPU et charge vos mémoires de bord.
3. Dès qu'Oscar est prêt, il vous salue de vive voix à travers vos écouteurs avec sa réplique d'accueil.
4. **Test en vol :**
   - Maintenez votre bouton Push-To-Talk (`Ctrl + Shift + F9`).
   - Dites distinctement : *« Oscar, sors le train d'atterrissage »*.
   - Relâchez le bouton : Oscar répond brièvement de vive voix et votre train d'atterrissage se déploie instantanément en jeu !

---

## 🔍 Résolution des Problèmes Fréquents (Dépannage)

### 1. Oscar parle mais aucune commande physique ne s'exécute en jeu
- **Cause 1 :** VoiceAttack tourne en mode Administrateur alors qu'Elite Dangerous ou Python tourne en mode utilisateur standard (Windows bloque l'envoi de signaux clavier entre différents niveaux de privilèges).  
  👉 *Solution :* Vérifiez dans les options de VoiceAttack (*System / Advanced*) que *« Run VoiceAttack as an Administrator »* est bien décoché.
- **Cause 2 :** Vous n'avez pas sélectionné le profil de commandes `..._Oscar` dans les options du jeu.  
  👉 *Solution :* Allez dans *Options > Commandes* en jeu et sélectionnez le profil généré par `sync_binds.py`.

### 2. Whisper transcrit lentement (> 2 secondes) ou charge le CPU
- **Cause :** Faster-Whisper n'a pas détecté CUDA ou les bibliothèques NVIDIA nécessaires, et s'exécute sur le processeur (CPU).  
  👉 *Solution :* Vérifiez que vous avez une carte graphique NVIDIA avec des pilotes récents installés. `IA_Elite.py` intègre un injecteur automatique des DLLs CUDA `cublas` présentes dans votre environnement Python.

### 3. La dictée n'écrit pas dans le chat en jeu
- **Cause :** La fenêtre du chat n'était pas active ou le curseur n'était pas dans le champ de saisie texte.  
  👉 *Solution :* Ouvrez d'abord le chat en jeu (touche par défaut du jeu pour ouvrir la boîte de communication), puis maintenez votre touche PTT pour dicter votre message.

### 4. Le mot-clé « Oscar » n'ouvre pas le canal d'écoute
- **Cause :** Le périphérique microphone de VoiceAttack n'est pas configuré sur le bon micro physique.  
  👉 *Solution :* Dans VoiceAttack, cliquez sur l'icône Clé à molette $\rightarrow$ onglet *Audio* $\rightarrow$ vérifiez que le *Recording device* cible bien votre microphone actif Windows.
