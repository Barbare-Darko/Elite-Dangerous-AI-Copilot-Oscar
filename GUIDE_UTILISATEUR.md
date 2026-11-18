# 📖 Guide d'Utilisation Complet — Copilote Oscar

Bienvenue à bord, Commandant. Ce guide détaille l'ensemble des fonctionnalités, commandes vocales et modes de saisie disponibles avec votre copilote IA **Oscar** pour **Elite Dangerous**.

---

## 🧭 Sommaire

1. [Principes de Fonctionnement & Activation Vocale](#1-principes-de-fonctionnement--activation-vocale)
2. [Mode Dictée (Chat & Rédaction)](#2-mode-dictée-chat--rédaction)
3. [Mode Épellation (Carte Galactique & Recherche)](#3-mode-épellation-carte-galactique--recherche)
4. [Télémétrie & Surveillance en Temps Réel](#4-télémétrie--surveillance-en-temps-réel)
5. [Alertes Proactives Autonomes](#5-alertes-proactives-autonomes)
6. [Commerce, Équipement & Navigation (Spansh & EDSM)](#6-commerce-équipement--navigation-spansh--edsm)
7. [Gestion de la Flotte & Configurations](#7-gestion-de-la-flotte--configurations)
8. [Mémoire & Journal de Bord Persistant](#8-mémoire--journal-de-bord-persistant)
9. [Catalogue des Commandes Physiques de Bord (VoiceAttack)](#9-catalogue-des-commandes-physiques-de-bord-voiceattack)
10. [Mode Discussion Libre (Culture Générale & Conversation)](#10-mode-discussion-libre-culture-générale--conversation)

---

## 1. Principes de Fonctionnement & Activation Vocale

### Deux méthodes d'activation vocale

Oscar propose deux méthodes complémentaires pour communiquer, selon vos préférences de pilotage :

1. **Méthode 1 : Le Push-To-Talk HOTAS / Clavier (Recommandé pour un contrôle absolu)**
   - **Maintenez enfoncée** la touche PTT configurée sur un bouton de votre manette des gaz, votre joystick ou votre clavier au moment de l'installation.
   - **Parlez** dans votre microphone.
   - **Relâchez le bouton** dès que vous avez terminé votre phrase.

2. **Méthode 2 : L'activation Mains Libres vocale (100 % sans les mains, gérée par VoiceAttack)**
   - Prononcez distinctement le mot de réveil : **« Oscar »** (ou tout autre mot-clé que vous auriez modifié à l'installation).
   - VoiceAttack intercepte l'appel, confirme vocalement sa disponibilité (*« Oui Barbare »* / *« Oui Commandant »*) et **maintient automatiquement le canal d'écoute ouvert**.
   - Énoncez votre ordre, votre question ou votre phrase dictée.
   - Terminez en disant : **« Terminé »**. VoiceAttack relâche instantanément le canal, déclenchant l'analyse audio de Faster-Whisper.

---

### Architecture et Flux d'Interprétation

Chaque échange vocal suit un cycle rigoureux en trois étapes :

~~~text
       [ Pilote (Voix) ]
              │
              ▼  (Bouton HOTAS relâché ou « Terminé »)
   [ 1. Faster-Whisper GPU CUDA ]
              │  Transcription locale ultra-rapide (0.2s)
              ▼
   [ 2. Cerveau OpenAI GPT-4o-mini ]
      ├── Personnalité sarcastique (config_oscar.json)
      ├── Télémétrie en direct (Status.json, Cargo.json, ModulesInfo)
      ├── Mémoire du pilote (journal_de_bord.txt)
      └── Catalogue des 121 macros de bord (commandes_vaisseau.txt)
              │
       ┌──────┴────────────────────────────────┐
       ▼                                       ▼
[ Cas A : Interrogation ]           [ Cas B : Action Physique ]
  • Function Calling Python           • GPT formule une courte réplique
  • Lecture télémétrie locale         • GPT appose [EXECUTE:Nom_Commande]
    ou requêtes EDSM/Spansh           • Python intercepte et appelle VoiceAttack
  • Retour données brutes à GPT       • VoiceAttack simule le raccourci clavier
  • Réponse vocale naturelle Edge-TTS • Elite Dangerous exécute (.binds)
~~~

1. **Reconnaissance vocale locale (Faster-Whisper sur GPU) :**  
   Le signal audio capturé par `sounddevice` est transcrit directement sur votre carte graphique NVIDIA sans aucun envoi vers le cloud.
2. **Analyse sémantique contextuelle (GPT-4o-mini) :**  
   Le texte transcrit est transmis à GPT-4o-mini accompagné des contextes dynamiques du cockpit : télémétrie instantanée, mémoires de vol et liste exhaustive des actions autorisées.
3. **Trois voies d'exécution distinctes :**
   - **Interrogation de données (Télémétrie, Spansh, EDSM, Flotte) :**  
     GPT-4o-mini déclenche automatiquement un outil Python (*Function Calling*). Le script interroge vos fichiers locaux (`Status.json`, `Cargo.json`, `ModulesInfo.json`, `flotte_cmdr.json`) ou contacte les APIs externes (recherche de station avec PAD compatible sur Spansh, calcul de distance 3D sur EDSM). Les données chiffrées sont réinjectées à GPT, qui rédige alors une réponse fluide, expressive et teintée de son humour habituel.
   - **Action physique de bord (Vaisseau, VRS, À pied) :**  
     Pour toute manœuvre (phares, trains, FSD, armes, etc.), GPT produit une courte réplique et insère à la fin la balise `[EXECUTE:Nom_Exact_De_La_Commande]`. Le script Python intercepte cette balise et transmet l'ordre à **VoiceAttack**, qui simule alors le raccourci clavier configuré dans votre profil `.binds` *(un tableau complet des 121 commandes possibles est fourni dans la documentation)*.
   - **Bascule vers les modes de saisie directe :**  
     Si vous demandez à écrire ou épeler, GPT émet la balise `[MODE_DICTEE]` ou `[MODE_EPELLATION]`. Oscar confirme la bascule (*« Mode dictée activé. »*), puis se met en retrait complet : chaque nouvel appui micro injecte directement votre texte à l'écran, **sans consommer le moindre jeton OpenAI**.

---

### 🛡️ Bonnes Pratiques & Précautions d'Usage

> ⚠️ **1. Ne prononcez jamais « Oscar » en Mode Dictée ou Épellation (ou votre mot-clé d'activation défini à l'installation) :**  
> VoiceAttack écoute en continu ce mot de réveil. Si vous le prononcez pendant que vous dictez ou épelez, VoiceAttack interceptera votre voix et ouvrira un canal concurrent.  
> 👉 Pour taper la lettre **O** dans la carte galactique, utilisez **exclusivement le prénom « Olivier »** (ou « Lettre O »).

> 💡 **2. Épelez par groupes naturels de 3 à 5 caractères (et le tiret isolément) :**  
> Pour une transcription parfaite par Whisper, découpez les longs identifiants stellaires en segments PTT naturels, en gardant toujours le mot **« tiret »** sur un appui seul :  
> - Appui 1 : *« S, Y, N »* → `SYN`  
> - Appui 2 : *« U, E, F, E »* → `UEFE`  
> - Appui 3 : *« Espace »* → ` `  
> - Appui 4 : *« B »* → `B`  
> - Appui 5 (seul) : *« Tiret »* → `-`  
> - Appui 6 : *« 0, 2, 5 »* → `025`
---

## 2. Mode Dictée (Chat & Rédaction)

Le **Mode Dictée** permet d'écrire vocalement des messages dans le chat d'Elite Dangerous (ou dans toute application active comme Discord ou le Bloc-notes), avec gestion automatique des espaces et de la ponctuation.

### Activation & Sortie
- **Entrer en Mode Dictée :** Dites naturellement au copilote :  
  *« Oscar, active la dictée »*, *« Passe en mode dictée »* ou *« Je voudrais dicter un message »*.  
  Oscar prononce sa réplique sarcastique et confirme à haute voix : **« Mode dictée activé. »**.
- **Quitter le Mode Dictée :** Dites *« Stop »*, *« Annuler »*, *« Quitter »* ou *« Terminer »*.  
  Oscar confirme à haute voix : **« Retour au mode commande. »**.

### Commandes vocales de contrôle en Mode Dictée

| Commande Vocale | Action effectuée |
| :--- | :--- |
| **`Envoi`** / **`Envoyer le message`** / **`Poster le message`** / **`Valider le message`** / **`Expédier`** | Simule la touche `Entrée` matérielle pour envoyer le message dans le chat, puis quitte le mode dictée (*« Retour au mode commande. »*). |
| **`Corriger`** / **`Annuler dernier bloc`** | Efface exactement le dernier bloc de texte injecté lors du précédent appui micro. |
| **`Effacer`** / **`Tout effacer`** / **`Effacer tout`** | Sélectionne tout le texte (`Ctrl + A`) et le supprime (`Suppr`). |
| **`Paragraphe suivant`** / **`À la ligne`** / **`Nouvelle ligne`** | Simule la touche `Entrée` pour sauter une ligne (à prononcer sur un appui PTT distinct après votre phrase pour un saut de ligne garanti). |
| **`Stop`** / **`Annuler`** / **`Quitter`** / **`Terminer`** | Quitte immédiatement la dictée sans toucher au texte déjà saisi (*« Retour au mode commande. »*). |

### Ponctuation vocale automatique
Prononcez simplement la ponctuation souhaitée :
- *« point »* $\rightarrow$ `.`
- *« virgule »* $\rightarrow$ `,`
- *« point d'interrogation »* $\rightarrow$ `?`
- *« point d'exclamation »* $\rightarrow$ `!`
- *« deux points »* $\rightarrow$ `:`
- *« point virgule »* $\rightarrow$ `;`
- *« points de suspension »* $\rightarrow$ `...`
- *« tiret »* $\rightarrow$ `-`
- *« dièse »* $\rightarrow$ `#`
- *« underscore »* / *« tiret du bas »* $\rightarrow$ `_`

---

## 3. Mode Épellation (Carte Galactique & Recherche)

Le **Mode Épellation** est spécialement conçu pour saisir lettre par lettre les noms complexes de systèmes stellaires dans le champ de recherche de la carte galactique d'Elite Dangerous (ex: `SYNUEFE B-025 C23.SA`).

### Activation & Sortie
- **Entrer en Mode Épellation :** Dites à Oscar :  
  *« Oscar, mode épellation »*, *« Je veux épeler un système »* ou *« Passe en mode lettre à lettre »*.  
  Oscar confirme à haute voix : **« Mode épellation activé. »**.
- **Quitter le Mode Épellation :** Dites *« Stop »*, *« Quitter »* ou validez par *« Envoi »* / *« Valider »*.  
  Oscar confirme à haute voix : **« Retour au mode commande. »**.

### Table de correspondance alphabétique (OTAN + Français)
Vous pouvez mélanger librement l'alphabet international (OTAN) et l'alphabet téléphonique français :

| Lettre | Mots reconnus |
| :---: | :--- |
| **A** | Alpha, Alfa, Antoine, Anatole |
| **B** | Bravo, Bernard, Berthe, Bé, Bo |
| **C** | Charlie, Charles, Célestine, Cé |
| **D** | Delta, Denis, Désiré, Dé |
| **E** | Echo, Écho, Émile, Eugène |
| **F** | Foxtrot, François, Fernand |
| **G** | Golf, Gaston, Georges, Gé |
| **H** | Hotel, Hôtel, Henri, Henry, Hache |
| **I** | India, Irma, Isidore |
| **J** | Juliett, Juliet, Juliette, Jules, Joseph, Ji |
| **K** | Kilo, Kléber, Ka |
| **L** | Lima, Louis, Lucien, Elle |
| **M** | Mike, Marcel, Maurice, Emme |
| **N** | November, Nicolas, Noémie, Enne |
| **O** | **Olivier**, Octave, Odile *(Règle : "Oscar" est réservé et ne tape rien pour protéger VoiceAttack)* |
| **P** | Papa, Paul, Pierre, Pé |
| **Q** | Quebec, Québec, Quentin |
| **R** | Romeo, Roméo, Robert, René, Erre |
| **S** | Sierra, Suzanne, Simon, Esse |
| **T** | Tango, Thérèse, Thomas, Té |
| **U** | Uniform, Ursule, Urbain |
| **V** | Victor, Vincent, Vé |
| **W** | Whiskey, Whisky, William, Double Vé |
| **X** | X-ray, Xray, Xavier, Ixe |
| **Y** | Yankee, Yvonne, Yves, I grec |
| **Z** | Zulu, Zoulou, Zoé, Zède |

### Règle déterministe des symboles en Épellation
1. **Le Tiret (`-`) :**  
   - Pour insérer un vrai tiret, prononcez-le **impérativement seul sur un appui micro** : *« tiret »*, *« tirer »*, *« tirez »*, *« trait d'union »* ou *« moins »*.
   - Si vous épelez une suite de lettres rapides (ex: Whisper comprendra *« S-Y-N-U-E-F-E »*), tous les tirets automatiques de liaison sont purgés pour produire fidèlement **`SYNUEFE`**.
2. **Le Point (`.`) :**  
   - Pour insérer un point isolé, dites simplement : *« point »*.
   - Si un point se trouve naturellement entre deux lettres ou chiffres (ex: `C012.3` ou `C23.SA`), Oscar le conserve intact.
3. **L'Espace :** Prononcez *« espace »* sur un appui PTT pour ajouter un espace.
4. **La tournure "Lettre X" :** Vous pouvez dire *« Lettre P »*, *« Lettre B »*, *« Lettre O »* pour injecter immédiatement la lettre majuscule désirée.

### Corrections rapides en Épellation
- **`Corriger`** : Efface le tout dernier caractère saisi (1 appui sur Retour arrière).
- **`Corriger X`** / **`Effacer X lettres`** (ex: *« Corriger 3 »*, *« Effacer 4 lettres »*) : Efface d'un seul coup X caractères consécutifs.
- **`Corriger mot`** / **`Effacer mot`** : Envoie `Ctrl + Retour arrière` pour effacer le mot entier jusqu'au dernier espace.
- **`Tout effacer`** : Envoie `Ctrl + A` puis `Suppr` pour vider complètement le champ de recherche.

---

## 4. Télémétrie & Surveillance en Temps Réel

Interrogez Oscar à tout moment sur la situation de votre vaisseau, de votre soute ou de votre position.

### Subtilités importantes sur les modules :
- **Lecture des modules (`ModulesInfo.json`) :** Elite Dangerous n'écrit l'état détaillé de vos équipements que lorsque vous consultez le panneau de droite du vaisseau. La connaissance de vos modules n'est donc possible **que si vous avez ouvert au moins une fois l'onglet Modules** durant votre session de vol.
- **Interrogation ciblée :** Oscar peut vérifier et vous indiquer si **un module précis** est actuellement actif ou désactivé (ex: *« Est-ce que mon récupérateur de carburant est actif ? »*), mais il ne peut pas dresser d'un coup une liste globale de tous les modules actifs/inactifs.

### Exemples de questions reconnues :
- *« Oscar, quel est l'état du vaisseau ? »*
- *« Combien de tonnes de carburant nous reste-t-il ? »*
- *« Combien de place avons-nous en soute ? »*
- *« Quel est le contenu de notre soute ? »*
- *« Quels sont nos rangs actuels et notre progression ? »*
- *« Quel est notre solde de crédits ? »*
- *« Est-ce que mon détecteur d'ondes de choc est actif ? »* / *« Y a-t-il des modules endommagés ? »*
- *« Combien de Fer et d'Arsenic avons-nous en stock ? »*

---

## 5. Alertes Proactives Autonomes

Même si vous ne posez aucune question, un thread d'arrière-plan haute réactivité (0,4 seconde) analyse les capteurs du vaisseau et avertit de vive voix le commandant en cas de danger critique :
- **🛡️ Boucliers :** Annonce instantanée dès que le bouclier tombe sous le feu ennemi.
- **🔥 Surchauffe thermique :** Alerte dès que la température dépasse le seuil critique (proximité d'étoile ou tir d'arme thermique).
- **⛽ Carburant bas :** Avertissement dès que la réserve principale atteint le seuil d'alerte.
- **🚨 Interdiction en cours :** Détection immédiate d'une tentative d'interdiction en hyper-espace.
- **💥 Intégrité de la coque :** Avertissement sur les dégâts majeurs subis par la structure.
- **⚠️ Santé des modules (< 50%) :** Détection des modules critiques endommagés ou en dysfonctionnement.

---

## 6. Commerce, Équipement & Navigation (Spansh & EDSM)

Oscar est connecté en temps réel aux APIs de **Spansh** et d'**EDSM** pour vous orienter à travers la galaxie.

### Recherche commerciale avec vérification de PAD
Oscar identifie le modèle de votre vaisseau actif : s'il s'agit d'un vaisseau lourd (Cutter, Corvette, Anaconda, Type-7, Type-9, Type-10, Beluga, Caspian...), il filtre **exclusivement** les stations équipées d'un **PAD Large**.
- *« Oscar, où puis-je vendre mon Platine au meilleur prix à moins de 3 sauts ? »*
- *« Où acheter du Tritium le plus près d'ici ? »*
- *« Trouve une station qui achète de l'Or dans un rayon de 80 années-lumière. »*

> 📋 **Copie presse-papiers automatique :** Dès qu'Oscar trouve la meilleure station, il copie automatiquement le nom du système stellaire dans votre presse-papiers Windows. Il vous suffit de faire `Ctrl + V` dans la carte galactique pour tracer la route !

### Recherche d'équipements & modules
- *« Où trouver un Réacteur FSD 5A dans les environs ? »*
- *« Trouve-moi un Générateur de bouclier 6A proche. »*

### Calcul de distances 3D
- *« À quelle distance se trouve Sol ? »*
- *« Quelle est la distance entre Popocassa et Shinrarta Dezhra ? »*

---

## 7. Gestion de la Flotte & Configurations

Oscar maintient un cache local (`data/flotte_cmdr.json`) de tous vos vaisseaux stockés à travers la galaxie.

> ℹ️ **Condition de mise à jour de la flotte :** Elite Dangerous n'enregistre l'inventaire complet de vos vaisseaux dans les journaux de vol que lors de la consultation des services en station. Votre flotte ne pourra donc être connue par Oscar **qu'après avoir ouvert au moins une fois le « Chantier naval » en station** depuis l'installation d'`IA_Elite`.

### Exemples de questions :
- *« Où est garé mon Anaconda ? »*
- *« Donne-moi la liste complète de ma flotte. »*
- *« Quelle est la portée de saut de mon Mandalay ? »*
- *« Quelle est la capacité de soute de mon Type-7 ? »*
- *« Quels sont les modules ingénieurs installés sur mon Krait Phantom ? »*

---

## 8. Mémoire & Journal de Bord Persistant

Oscar se souvient de vos aventures ! À la fin de chaque échange pertinent, un résumé asynchrone est consolidé dans `data/journal_de_bord.txt`.
- À chaque démarrage, Oscar formule un accueil personnalisé et sarcastique tenant compte de vos dernières actions et de votre position actuelle.
- Vos préférences (vaisseau favori, type de mission préféré, habitudes de minage) sont retenues d'une session à l'autre.

---

## 9. Catalogue des Commandes Physiques de Bord (VoiceAttack)

Oscar peut déclencher directement toutes les macros physiques de bord configurées dans VoiceAttack *(le tableau complet des 121 commandes possibles est disponible dans le projet)*. Voici les principales formulations reconnues :

### Navigation & Pilotage
- *« Sors le train d'atterrissage »* / *« Rentre le train »*
- *« Allume les phares »* / *« Éteins les phares »*
- *« Ouvre la carte galactique »* / *« Ouvre la carte système »*
- *« Active l'assistance de vol »* / *« Coupe l'assistance de vol »*
- *« Active la vision nocturne »* / *« Désactive la vision nocturne »*
- *« Passe en mode combat »* / *« Passe en mode analyse »*

### Combat & Ciblage
- *« Déploie les points d'emport »* / *« Rentre les armes »*
- *« Cible devant »* / *« Cible suivante »* / *« Menace principale »*
- *« Sous-système suivant (viser le générateur) »*
- *« Cible le coéquipier 1 »* / *« Suivre le coéquipier »*
- *« Éjecte un dissipateur thermique »*
- *« Lance des paillettes »*
- *« Charge une cellule d'énergie »*
- *« Équilibre la puissance »*

### Véhicule Terrestre (VRS) & À pied (Odyssey)
- *« Allume les phares du buggy »*
- *« Active le frein à main »*
- *« Déploie la tourelle du VRS »*
- *« Rappelle le vaisseau »* / *« Renvoyer le vaisseau »*
- *« Allume la torche »* (à pied)
- *« Sors l'arme »* / *« Rengaine l'arme »*
- *« Ouvre la roue d'équipement »* / *« Utilise un medkit »* / *« Recharge la batterie »*

---

## 10. Mode Discussion Libre (Culture Générale & Conversation)

En dehors des manœuvres de vol et des données du jeu, Oscar reste un compagnon de voyage doté de toute la culture générale de **GPT-4o-mini** :
- **Parlez de tout et de rien :** Vous pouvez discuter avec lui de la pluie et du beau temps durant les longs trajets en super-navigation, ou lui poser n'importe quelle question de culture générale, d'histoire, de science ou d'actualité (par exemple : *« Oscar, quel est l'âge du pape ? »* ou *« Explique-moi comment fonctionne un trou noir »*).
- **Réponse naturelle sans action en jeu :** Lorsqu'aucune action de bord n'est demandée, Oscar vous répond librement avec sa personnalité sarcastique habituelle, sans jamais déclencher de touche ni modifier l'état de votre vaisseau.

---
---

# 📖 Complete User Guide — Oscar AI Copilot

Welcome aboard, Commander. This guide details all the features, voice commands, and text input modes available with your **Oscar** AI copilot for **Elite Dangerous**.

---

## 🧭 Table of Contents

1. [Operating Principles & Voice Activation](#1-operating-principles--voice-activation)
2. [Dictation Mode (Chat & Writing)](#2-dictation-mode-chat--writing)
3. [Spelling Mode (Galaxy Map & Search)](#3-spelling-mode-galaxy-map--search)
4. [Real-Time Telemetry & Monitoring](#4-real-time-telemetry--monitoring)
5. [Autonomous Proactive Alerts](#5-autonomous-proactive-alerts)
6. [Trading, Outfitting & Navigation (Spansh & EDSM)](#6-trading-outfitting--navigation-spansh--edsm)
7. [Fleet & Loadout Management](#7-fleet--loadout-management)
8. [Persistent Flight Memory & Logbook](#8-persistent-flight-memory--logbook)
9. [Onboard Physical Command Catalog (VoiceAttack)](#9-onboard-physical-command-catalog-voiceattack)
10. [Free Chat Mode (General Knowledge & Conversation)](#10-free-chat-mode-general-knowledge--conversation)

---

## 1. Operating Principles & Voice Activation

### Two Voice Activation Methods

Oscar provides two complementary ways to communicate, depending on your flying preferences:

1. **Method 1: HOTAS / Keyboard Push-To-Talk (Recommended for absolute control)**
   - **Press and hold** the PTT button configured on your throttle, joystick, or keyboard during installation.
   - **Speak** into your microphone.
   - **Release the button** as soon as you finish your sentence.

2. **Method 2: Hands-Free Voice Activation (100% voice-operated via VoiceAttack)**
   - Clearly pronounce the wake word: **"Oscar"** (or whatever custom wake word you configured during setup).
   - VoiceAttack intercepts the call, confirms aloud that it is listening (*"Oui Barbare"* / *"Oui Commandant"*), and **automatically holds the listening channel open**.
   - Speak your order, question, or dictated sentence.
   - Finish by saying: **"Terminé"**. VoiceAttack immediately releases the channel, triggering Faster-Whisper audio processing.

---

### Architecture and Interpretation Pipeline

Every voice exchange follows a strict, deterministic three-step cycle:
~~~text
       [ Pilot (Voice) ]
              │
              ▼  (HOTAS button released or "Terminé")
   [ 1. Faster-Whisper GPU CUDA ]
              │  Ultra-fast local transcription (0.2s)
              ▼
   [ 2. OpenAI GPT-4o-mini Brain ]
      ├── Sarcastic personality (config_oscar.json)
      ├── Live telemetry (Status.json, Cargo.json, ModulesInfo)
      ├── Pilot memory (journal_de_bord.txt)
      └── Catalog of 121 onboard macros (commandes_vaisseau.txt)
              │
       ┌──────┴────────────────────────────────┐
       ▼                                       ▼
[ Case A: Data Query ]              [ Case B: Physical Action ]
  • Python Function Calling           • GPT generates a short reply
  • Reads local telemetry             • GPT appends [EXECUTE:Command_Name]
    or queries EDSM/Spansh            • Python intercepts and calls VoiceAttack
  • Returns raw data to GPT           • VoiceAttack simulates the keybind
  • Natural Edge-TTS voice reply      • Elite Dangerous executes (.binds)
~~~
1. **Local Speech Recognition (Faster-Whisper on GPU):**  
   Audio captured by `sounddevice` is transcribed directly on your NVIDIA graphics card with zero cloud audio upload.
2. **Contextual Semantic Analysis (GPT-4o-mini):**  
   The transcribed text is sent to GPT-4o-mini alongside dynamic cockpit context: live telemetry, flight memories, and the complete list of authorized actions.
3. **Three Distinct Execution Paths:**
   - **Data Queries (Telemetry, Spansh, EDSM, Fleet):**  
     GPT-4o-mini automatically triggers a Python tool (*Function Calling*). The script reads your local files (`Status.json`, `Cargo.json`, `ModulesInfo.json`, `flotte_cmdr.json`) or queries external APIs (pad-compatible station search on Spansh, 3D distance calculation on EDSM). Raw figures are returned to GPT, which crafts a fluid, expressive reply flavored with its signature sarcasm.
   - **Physical Onboard Actions (Ship, SRV, On-Foot):**  
     For any ship maneuver (lights, landing gear, FSD, weapons, etc.), GPT produces a short reply and appends the tag `[EXECUTE:Exact_Command_Name]`. Python intercepts this tag and forwards the command to **VoiceAttack**, which simulates the keyboard shortcut mapped in your `.binds` profile *(a complete table of all 121 available commands is included in the documentation)*.
   - **Switching to Direct Input Modes:**  
     If you ask to write or spell, GPT emits `[MODE_DICTEE]` or `[MODE_EPELLATION]`. Oscar confirms the switch aloud (*"Mode dictée activé."*), then steps back completely: every subsequent PTT press injects text straight onto your screen, **consuming zero OpenAI tokens**.

---

### 🛡️ Best Practices & Usage Precautions

> ⚠️ **1. Never say "Oscar" while in Dictation or Spelling Mode (or your custom wake word set during setup):**  
> VoiceAttack continuously listens for this wake word. If you say it while dictating or spelling, VoiceAttack will intercept your voice and open a competing listening channel.  
> 👉 To type the letter **O** in the Galaxy Map, **exclusively use the name "Olivier"** (or "Lettre O").

> 💡 **2. Spell in natural groups of 3 to 5 characters (and speak hyphens alone):**  
> For flawless Whisper transcription, break long star system identifiers into natural PTT chunks, always speaking **"tiret"** (hyphen) on a separate press:  
> - Press 1: *"S, Y, N"* → `SYN`  
> - Press 2: *"U, E, F, E"* → `UEFE`  
> - Press 3: *"Espace"* → ` `  
> - Press 4: *"B"* → `B`  
> - Press 5 (alone): *"Tiret"* → `-`  
> - Press 6: *"0, 2, 5"* → `025`

## 2. Dictation Mode (Chat & Writing)

**Dictation Mode** lets you speak messages directly into the Elite Dangerous chat box (or any active window such as Discord or Notepad), with automatic spacing and punctuation.

### Entering & Exiting
- **Enter Dictation Mode:** Naturally tell your copilot:  
  *"Oscar, active la dictée"*, *"Passe en mode dictée"*, or *"Je voudrais dicter un message"*.  
  Oscar delivers a sarcastic quip and confirms aloud: **"Mode dictée activé."**.
- **Exit Dictation Mode:** Say *"Stop"*, *"Annuler"*, *"Quitter"*, or *"Terminer"*.  
  Oscar confirms aloud: **"Retour au mode commande."**.

### Voice Control Commands in Dictation Mode

| Voice Command | Action Performed |
| :--- | :--- |
| **`Envoi`** / **`Envoyer le message`** / **`Poster le message`** / **`Valider le message`** / **`Expédier`** | Simulates the physical `Enter` key to send the message in chat, then exits Dictation Mode (*"Retour au mode commande."*). |
| **`Corriger`** / **`Annuler dernier bloc`** | Deletes only the last block of text injected during the previous microphone press. |
| **`Effacer`** / **`Tout effacer`** / **`Effacer tout`** | Selects all text (`Ctrl + A`) and deletes it (`Delete`). |
| **`Paragraphe suivant`** / **`À la ligne`** / **`Nouvelle ligne`** | Simulates the `Enter` key for a line break (speak on a separate PTT press after your sentence for a reliable newline). |
| **`Stop`** / **`Annuler`** / **`Quitter`** / **`Terminer`** | Immediately exits dictation without altering already typed text (*"Retour au mode commande."*). |

### Automatic Spoken Punctuation
Simply speak the desired punctuation mark (in French):
- *"point"* → `.`
- *"virgule"* → `,`
- *"point d'interrogation"* → `?`
- *"point d'exclamation"* → `!`
- *"deux points"* → `:`
- *"point virgule"* → `;`
- *"points de suspension"* → `...`
- *"tiret"* → `-`
- *"dièse"* → `#`
- *"underscore"* / *"tiret du bas"* → `_`

---

## 3. Spelling Mode (Galaxy Map & Search)

**Spelling Mode** is specifically designed to enter complex star system names character by character into the Elite Dangerous Galaxy Map search bar (e.g., `SYNUEFE B-025 C23.SA`).

### Entering & Exiting
- **Enter Spelling Mode:** Tell Oscar:  
  *"Oscar, mode épellation"*, *"Je veux épeler un système"*, or *"Passe en mode lettre à lettre"*.  
  Oscar confirms aloud: **"Mode épellation activé."**.
- **Exit Spelling Mode:** Say *"Stop"*, *"Quitter"*, or confirm with *"Envoi"* / *"Valider"*.  
  Oscar confirms aloud: **"Retour au mode commande."**.

### Phonetic Alphabet Lookup Table (NATO + French)
You may freely mix the international NATO phonetic alphabet and the French telephone alphabet:

| Letter | Recognized Words |
| :---: | :--- |
| **A** | Alpha, Alfa, Antoine, Anatole |
| **B** | Bravo, Bernard, Berthe, Bé, Bo |
| **C** | Charlie, Charles, Célestine, Cé |
| **D** | Delta, Denis, Désiré, Dé |
| **E** | Echo, Écho, Émile, Eugène |
| **F** | Foxtrot, François, Fernand |
| **G** | Golf, Gaston, Georges, Gé |
| **H** | Hotel, Hôtel, Henri, Henry, Hache |
| **I** | India, Irma, Isidore |
| **J** | Juliett, Juliet, Juliette, Jules, Joseph, Ji |
| **K** | Kilo, Kléber, Ka |
| **L** | Lima, Louis, Lucien, Elle |
| **M** | Mike, Marcel, Maurice, Emme |
| **N** | November, Nicolas, Noémie, Enne |
| **O** | **Olivier**, Octave, Odile *(Rule: "Oscar" is reserved and types nothing to prevent triggering VoiceAttack)* |
| **P** | Papa, Paul, Pierre, Pé |
| **Q** | Quebec, Québec, Quentin |
| **R** | Romeo, Roméo, Robert, René, Erre |
| **S** | Sierra, Suzanne, Simon, Esse |
| **T** | Tango, Thérèse, Thomas, Té |
| **U** | Uniform, Ursule, Urbain |
| **V** | Victor, Vincent, Vé |
| **W** | Whiskey, Whisky, William, Double Vé |
| **X** | X-ray, Xray, Xavier, Ixe |
| **Y** | Yankee, Yvonne, Yves, I grec |
| **Z** | Zulu, Zoulou, Zoé, Zède |

### Deterministic Symbol Rules in Spelling Mode
1. **Hyphen (`-`):**  
   - To insert a real hyphen, speak it **strictly alone on a single PTT press**: *"tiret"*, *"tirer"*, *"tirez"*, *"trait d'union"*, or *"moins"*.
   - When spelling rapid letter sequences (e.g., Whisper transcribes *"S-Y-N-U-E-F-E"*), all automatic linking hyphens are stripped to cleanly output **`SYNUEFE`**.
2. **Period / Dot (`.`):**  
   - To insert a standalone dot, simply say: *"point"*.
   - When a dot appears naturally between letters or numbers (e.g., `C012.3` or `C23.SA`), Oscar preserves it intact.
3. **Space:** Speak *"espace"* on a PTT press to insert a space.
4. **"Lettre X" phrasing:** You can say *"Lettre P"*, *"Lettre B"*, or *"Lettre O"* to inject the corresponding uppercase letter immediately.

### Quick Corrections in Spelling Mode
- **`Corriger`**: Deletes the last typed character (1 Backspace press).
- **`Corriger X`** / **`Effacer X lettres`** (e.g., *"Corriger 3"*, *"Effacer 4 lettres"*): Deletes X consecutive characters at once.
- **`Corriger mot`** / **`Effacer mot`**: Sends `Ctrl + Backspace` to erase the entire word back to the last space.
- **`Tout effacer`**: Sends `Ctrl + A` followed by `Delete` to completely clear the search field.

---

> 🌐 **Language Note for English-Speaking Commanders:**  
> By default, the provided VoiceAttack profile (`Barbare Darko-Profile.vap`), the onboard command list (`data/commandes_vaisseau.txt`), the Whisper speech recognition setting (`language="fr"`), and the neural voice (`fr-FR-HenriNeural`) are configured for **French**. That is why the sample voice commands below are shown in French—they work out of the box with the included profile.  
> 👉 If you wish to operate Oscar **entirely in English** (speaking English commands and receiving English replies), see the **[Customization Guide (PERSONNALISATION.md)](PERSONNALISATION.md)** to switch the voice/personality to English and adapt the command names in VoiceAttack and `commandes_vaisseau.txt`.

## 4. Real-Time Telemetry & Monitoring

Ask Oscar at any time about your ship's status, cargo hold, or current situation.

### Important Subtleties Regarding Ship Modules:
- **Module reading (`ModulesInfo.json`):** Elite Dangerous only writes detailed equipment status to disk when you open the right-hand ship panel. Module awareness is therefore available **only after you have opened the Modules tab at least once** during your current flight session.
- **Targeted queries:** Oscar can check and tell you whether **a specific module** is currently powered on or off (e.g., *"Est-ce que mon récupérateur de carburant est actif ?"*), but cannot list all active/inactive modules at once.

### Sample Recognized Questions:
- *"Oscar, quel est l'état du vaisseau ?"*
- *"Combien de tonnes de carburant nous reste-t-il ?"*
- *"Combien de place avons-nous en soute ?"*
- *"Quel est le contenu de notre soute ?"*
- *"Quels sont nos rangs actuels et notre progression ?"*
- *"Quel est notre solde de crédits ?"*
- *"Est-ce que mon détecteur d'ondes de choc est actif ?"* / *"Y a-t-il des modules endommagés ?"*
- *"Combien de Fer et d'Arsenic avons-nous en stock ?"*

---

## 5. Autonomous Proactive Alerts

Even when you ask nothing, a high-frequency background thread (0.4s) monitors your ship's sensors and warns you aloud upon critical events:
- **🛡️ Shields:** Instant alert when shields drop under enemy fire.
- **🔥 Thermal Overheating:** Warning when heat exceeds critical thresholds (star proximity or thermal weapons).
- **⛽ Low Fuel:** Alert when main fuel reserves reach warning levels.
- **🚨 Interdiction in Progress:** Immediate detection of a hyperspace/supercruise interdiction attempt.
- **💥 Hull Integrity:** Warning upon major structural hull damage.
- **⚠️ Module Health (< 50%):** Detection of damaged or malfunctioning critical modules.

---

## 6. Trading, Outfitting & Navigation (Spansh & EDSM)

Oscar connects in real time to the **Spansh** and **EDSM** APIs to guide you across the galaxy.

### Commodity Search with Landing Pad Verification
Oscar detects your active ship model: if you are flying a large hull (Cutter, Corvette, Anaconda, Type-7, Type-9, Type-10, Beluga, Caspian, etc.), it **exclusively** filters stations equipped with a **Large Landing Pad**.
- *"Oscar, où puis-je vendre mon Platine au meilleur prix à moins de 3 sauts ?"*
- *"Où acheter du Tritium le plus près d'ici ?"*
- *"Trouve une station qui achète de l'Or dans un rayon de 80 années-lumière."*

> 📋 **Automatic Clipboard Copy:** As soon as Oscar finds the best station, it automatically copies the star system name to your Windows clipboard. Simply press `Ctrl + V` in the Galaxy Map to plot your route!

### Outfitting & Module Search
- *"Où trouver un Réacteur FSD 5A dans les environs ?"*
- *"Trouve-moi un Générateur de bouclier 6A proche."*

### 3D Distance Calculations
- *"À quelle distance se trouve Sol ?"*
- *"Quelle est la distance entre Popocassa et Shinrarta Dezhra ?"*

---

## 7. Fleet & Loadout Management

Oscar maintains a local cache (`data/flotte_cmdr.json`) of all your stored ships across the galaxy.

> ℹ️ **Fleet Update Requirement:** Elite Dangerous only writes your complete ship inventory to the player journal when you access station shipyard services. Your fleet becomes known to Oscar **only after you have opened the "Shipyard" (Chantier naval) at a station at least once** since installing `IA_Elite`.

### Sample Questions:
- *"Où est garé mon Anaconda ?"*
- *"Donne-moi la liste complète de ma flotte."*
- *"Quelle est la portée de saut de mon Mandalay ?"*
- *"Quelle est la capacité de soute de mon Type-7 ?"*
- *"Quels sont les modules ingénieurs installés sur mon Krait Phantom ?"*

---

## 8. Persistent Flight Memory & Logbook

Oscar remembers your adventures! At the end of every meaningful exchange, an asynchronous summary is saved to `data/journal_de_bord.txt`.
- At startup, Oscar delivers a personalized, sarcastic greeting based on your recent actions and current location.
- Your preferences (favorite ship, preferred mission types, mining habits) are remembered from session to session.

---

## 9. Onboard Physical Command Catalog (VoiceAttack)

Oscar can directly trigger any onboard physical macro configured in VoiceAttack *(the complete table of all 121 available commands is provided in the project documentation)*. Here are the main recognized commands:

### Navigation & Piloting
- *"Sors le train d'atterrissage"* / *"Rentre le train"*
- *"Allume les phares"* / *"Éteins les phares"*
- *"Ouvre la carte galactique"* / *"Ouvre la carte système"*
- *"Active l'assistance de vol"* / *"Coupe l'assistance de vol"*
- *"Active la vision nocturne"* / *"Désactive la vision nocturne"*
- *"Passe en mode combat"* / *"Passe en mode analyse"*

### Combat & Targeting
- *"Déploie les points d'emport"* / *"Rentre les armes"*
- *"Cible devant"* / *"Cible suivante"* / *"Menace principale"*
- *"Sous-système suivant (viser le générateur)"*
- *"Cible le coéquipier 1"* / *"Suivre le coéquipier"*
- *"Éjecte un dissipateur thermique"*
- *"Lance des paillettes"*
- *"Charge une cellule d'énergie"*
- *"Équilibre la puissance"*

### Surface Recon Vehicle (SRV) & On-Foot (Odyssey)
- *"Allume les phares du buggy"*
- *"Active le frein à main"*
- *"Déploie la tourelle du VRS"*
- *"Rappelle le vaisseau"* / *"Renvoyer le vaisseau"*
- *"Allume la torche"* (on foot)
- *"Sors l'arme"* / *"Rengaine l'arme"*
- *"Ouvre la roue d'équipement"* / *"Utilise un medkit"* / *"Recharge la batterie"*

---

## 10. Free Chat Mode (General Knowledge & Conversation)

Outside of flight maneuvers and game telemetry, Oscar remains a conversational companion powered by **GPT-4o-mini**'s general knowledge:
- **Chat about anything:** Talk with Oscar during long supercruise trips or ask any question about history, science, general trivia, or current events (e.g., *"Oscar, quel est l'âge du pape ?"* or *"Explique-moi comment fonctionne un trou noir"*).
- **Natural reply with zero in-game action:** Whenever no ship maneuver is requested, Oscar replies freely in its signature sarcastic persona without pressing any key or altering your ship's state.
