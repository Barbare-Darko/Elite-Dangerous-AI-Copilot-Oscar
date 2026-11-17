# 📖 Guide d'Utilisation Complet — Copilote Oscar

Bienvenue à bord, Commandant. Ce guide détaille l'ensemble des fonctionnalités, commandes vocales et modes de saisie disponibles avec votre copilote IA **Oscar** pour **Elite Dangerous**.

---

## 🧭 Sommaire

1. [Principes de Fonctionnement & Raccourci PTT](#1-principes-de-fonctionnement--raccourci-ptt)
2. [Mode Dictée (Chat & Rédaction)](#2-mode-dictée-chat--rédaction)
3. [Mode Épellation (Carte Galactique & Recherche)](#3-mode-épellation-carte-galactique--recherche)
4. [Télémétrie & Surveillance en Temps Réel](#4-télémétrie--surveillance-en-temps-réel)
5. [Alertes Proactives Autonomes](#5-alertes-proactives-autonomes)
6. [Commerce, Équipement & Navigation (Spansh & EDSM)](#6-commerce-équipement--navigation-spansh--edsm)
7. [Gestion de la Flotte & Configurations](#7-gestion-de-la-flotte--configurations)
8. [Mémoire & Journal de Bord Persistant](#8-mémoire--journal-de-bord-persistant)
9. [Catalogue des Commandes Physiques de Bord (VoiceAttack)](#9-catalogue-des-commandes-physiques-de-bord-voiceattack)

---

## 1. Principes de Fonctionnement & Raccourci PTT

### Deux méthodes d'activation vocale

Oscar propose deux méthodes complémentaires pour communiquer, selon vos préférences de pilotage :

1. **Méthode 1 : Le Push-To-Talk HOTAS / Clavier (Recommandé pour un contrôle absolu)**
   - **Maintenez enfoncée** la combinaison PTT (par défaut : **`Ctrl + Shift + F9`** configurée sur un bouton de votre manette des gaz ou joystick).
   - **Parlez** dans votre microphone.
   - **Relâchez le bouton** dès que vous avez terminé votre phrase.

2. **Méthode 2 : L'activation Mains Libres vocale (100 % sans les mains, géré par VoiceAttack)**
   - Prononcez distinctement le mot de réveil : **« Oscar »**.
   - VoiceAttack intercepte l'appel, confirme sa disponibilité vocale (*« Oui Commandant »* ou bip sonore) et **maintient automatiquement le canal d'écoute ouvert** (`Ctrl + Shift + F9`).
   - Énoncez votre ordre, votre question ou votre phrase dictée.
   - Terminez en disant : **« Terminé »**. VoiceAttack relâche instantanément le canal, déclenchant l'analyse audio de Faster-Whisper.

---

### Architecture et Flux d'Interprétation

Chaque échange vocal suit un cycle rigoureux et déterministe en trois étapes :

```text
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
```

1. **Reconnaissance vocale locale (Faster-Whisper sur GPU) :**  
   Le signal audio capturé par `sounddevice` est transcrit directement sur votre carte graphique NVIDIA sans aucun envoi vers le cloud, avec une latence quasi-nulle.
2. **Analyse sémantique contextuelle (GPT-4o-mini) :**  
   Le texte transcrit est transmis à GPT-4o-mini accompagné des contextes dynamiques du cockpit : télémétrie instantanée, mémoires de vol et liste exhaustive des actions autorisées.
3. **Deux voies d'exécution distinctes :**
   - **Interrogation de données (Télémétrie, Spansh, EDSM, Flotte) :**  
     GPT-4o-mini déclenche automatiquement un outil Python (*Function Calling*). Le script interroge vos fichiers locaux (`Status.json`, `Cargo.json`, `ModulesInfo.json`, `flotte_cmdr.json`) ou contacte les APIs externes (recherche de station avec PAD compatible sur Spansh, calcul de distance 3D sur EDSM). Les données chiffrées sont réinjectées à GPT, qui rédige alors une réponse fluide, expressive et teintée de son humour habituel.
   - **Action physique de bord (Vaisseau, VRS, À pied) :**  
     Pour toute manœuvre (phares, trains, FSD, régulateur, armes, etc.), GPT produit une courte réplique (5-6 mots max) et insère à la fin la balise `[EXECUTE:Nom_Exact_De_La_Commande]`. Le script Python intercepte cette balise, la masque pour la synthèse vocale, et transmet l'ordre en ligne de commande à **VoiceAttack** (`VoiceAttack.exe -command "..."`). VoiceAttack injecte alors le raccourci clavier matériel configuré dans la colonne `<Secondary>` de votre profil `.binds`.
   - **Bascule vers les modes de saisie directe :**  
     Si vous demandez à écrire ou épeler, GPT émet la balise `[MODE_DICTEE]` ou `[MODE_EPELLATION]`. Oscar confirme la bascule (*« Mode dictée activé. »*), puis se met en retrait complet : chaque nouvel appui micro injecte directement votre texte à l'écran, **sans consommer le moindre jeton OpenAI**.

---

### 🛡️ Bonnes Pratiques & Précautions d'Usage

> ⚠️ **1. Ne prononcez jamais « Oscar » en Mode Dictée ou Épellation :**  
> VoiceAttack écoute en continu le mot de réveil « Oscar ». Si vous le prononcez pendant que vous dictez ou épelez, VoiceAttack interceptera votre voix et ouvrira un canal concurrent.  
> 👉 Pour taper la lettre **O** dans la carte galactique, utilisez **exclusivement le prénom « Olivier »** (ou « Lettre O »).

> 💡 **2. Épelez par groupes naturels de 3 à 5 caractères :**  
> Pour une transcription parfaite et sans hésitation par Whisper, découpez les longs identifiants stellaires en 2 ou 3 segments PTT naturels (ex: Premier appui : *« S, Y, N »* $\rightarrow$ Deuxième appui : *« U, E, F, E »* $\rightarrow$ Troisième appui : *« B tiret 025 »*).

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
| **`Tout effacer`** / **`Effacer tout`** | Sélectionne tout le texte (`Ctrl + A`) et le supprime (`Suppr`). |
| **`Paragraphe suivant`** / **`À la ligne`** / **`Nouvelle ligne`** | Simule la touche `Entrée` pour sauter une ligne. |
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

> 💡 **Enchaînement fluide :** Vous pouvez prononcer un saut de ligne directement à la fin d'une phrase dictée (ex: *« Tout est prêt pour le décollage point, paragraphe suivant »*). Oscar tapera la phrase ponctuée puis fera immédiatement le saut de ligne.

---

## 3. Mode Épellation (Carte Galactique & Recherche)

Le **Mode Épellation** est spécialement conçu pour saisir lettre par lettre les noms complexes de systèmes stellaires dans le champ de recherche de la carte galactique d'Elite Dangerous (ex: `SYNUEFE B0-Y C23.SA`).

### Activation & Sortie
- **Entrer en Mode Épellation :** Dites à Oscar :  
  *« Oscar, mode épellation »*, *« Je veux épeler un système »* ou *« Passe en mode lettre par lettre »*.  
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
   - Pour insérer un vrai tiret, prononcez-le de manière isolée sur un appui micro : *« tiret »*, *« tirer »*, *« tirez »*, *« trait d'union »* ou *« moins »*.
   - Si vous épelez une suite de lettres rapides (ex: Whisper entendant *« S-Y-N-U-E-F-E »*), tous les tirets automatiques de liaison sont purgés pour produire fidèlement **`SYNUEFE`**.
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

### Exemples de questions reconnues :
- *« Oscar, quel est l'état du vaisseau ? »*
- *« Combien de tonnes de carburant nous reste-t-il ? »*
- *« Combien de place avons-nous en soute ? »*
- *« Quel est le contenu de notre soute ? »*
- *« Quels sont nos rangs actuels et notre progression ? »*
- *« Quel est notre solde de crédits ? »*
- *« Quelle est notre destination verrouillée ? »*
- *« Y a-t-il des modules endommagés ou inactifs ? »*
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
- *« Quels sont les systèmes stellaires voisins dans un rayon de 30 années-lumière ? »*

---

## 7. Gestion de la Flotte & Configurations

Oscar maintient un cache local (`data/flotte_cmdr.json`) de tous vos vaisseaux stockés à travers la galaxie :
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

Oscar peut déclencher directement toutes les macros physiques de bord configurées dans VoiceAttack. Voici les principales formulations reconnues :

### Navigation & Pilotage
- *« Sors le train d'atterrissage »* / *« Rentre le train »*
- *« Allume les phares »* / *« Éteins les phares »*
- *« Ouvre la carte galactique »* / *« Ouvre la carte système »*
- *« Active l'assistance de vol »* / *« Coupe l'assistance de vol »*
- *« Active la vision nocturne »* / *« Désactive la vision nocturne »*
- *« Passe en mode combat »* / *« Passe en mode analyse »*
- *« Active le régulateur de vitesse »* / *« Vitesse à 75 % »* / *« Vitesse à 100 % »* / *« Arrêt complet »*

### Combat & Ciblage
- *« Déploie les points d'emport »* / *« Rentre les armes »*
- *« Cible devant »* / *« Cible suivante »* / *« Menace principale »*
- *« Sous-système suivant (viser le générateur) »*
- *« Cible le coéquipier 1 »* / *« Suivre le coéquipier »*
- *« Éjecte un dissipateur thermique »*
- *« Lance des paillettes »*
- *« Charge une cellule d'énergie »*
- *« Répartis l'énergie sur les armes »* / *« Puissance sur les moteurs »* / *« Équilibre la puissance »*

### Véhicule Terrestre (VRS) & À pied (Odyssey)
- *« Allume les phares du buggy »*
- *« Active le frein à main »*
- *« Déploie la tourelle du VRS »*
- *« Rappelle le vaisseau »* / *« Renvoyer le vaisseau »*
- *« Allume la torche »* (à pied)
- *« Sors l'arme »* / *« Rengaine l'arme »*
- *« Ouvre la roue d'équipement »* / *« Utilise un medkit »* / *« Recharge la batterie »*
