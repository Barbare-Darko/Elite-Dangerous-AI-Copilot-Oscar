# ⚙️ Guide de Personnalisation — Copilote Oscar

Toutes les options de personnalisation d'Oscar sont externalisées dans le fichier **`config_oscar.json`** situé à la racine du projet. Vous pouvez ainsi modifier le nom, la personnalité, la voix et les paramètres de simulation sans jamais modifier une seule ligne de code Python.

---

## 🧭 Sommaire

1. [Changer le nom du Copilote](#1-changer-le-nom-du-copilote)
2. [Modifier la personnalité et le prompt système](#2-modifier-la-personnalité-et-le-prompt-système)
3. [Changer la voix de synthèse (Edge-TTS) et la vitesse](#3-changer-la-voix-de-synthèse-edge-tts-et-la-vitesse)
4. [Ajouter de nouveaux vaisseaux d'Elite Dangerous](#4-ajouter-de-nouveaux-vaisseaux-delite-dangerous)
5. [Ajuster les délais de simulation clavier DirectX](#5-ajuster-les-délais-de-simulation-clavier-directx)
6. [Personnaliser le vocabulaire des commandes vocales](#6-personnaliser-le-vocabulaire-des-commandes-vocales)

---

## 1. Changer le nom du Copilote

Par défaut, votre copilote s'appelle **Oscar**. Vous pouvez le renommer librement (par exemple *Sophie*, *Astra*, *Jarvis*, *Cortex*).

Dans `config_oscar.json`, modifiez la clé `"nom_ia"` :
```json
{
  "nom_ia": "Sophie"
}
```
> 💡 **Effet immédiat :** Whisper filtrera automatiquement le nouveau nom quand vous l'interpellez (ex: *« Sophie, quel est l'état du vaisseau ? »*), et l'IA répondra sous cette nouvelle identité.

### ⚠️ Avertissements indispensables en cas de renommage :
1. **Renommer le mot-clé dans VoiceAttack :**  
   Si vous utilisez le mode d'activation Mains Libres, ouvrez votre profil dans **VoiceAttack** et modifiez la commande de réveil qui écoute actuellement *« Oscar »* pour la remplacer par votre nouveau nom (ex: *« Sophie »*).
2. **Éviter les collisions avec le Mode Épellation :**  
   Si votre nouveau nom correspond à un prénom présent dans l'alphabet phonétique de `config_oscar.json` (par exemple *« Sophie »* $\rightarrow$ S ou *« Victor »* $\rightarrow$ V), **retirez impérativement ce prénom de la section `"alphabet_phonetique"`** pour éviter que VoiceAttack n'intercepte l'appel pendant que vous épelez un système stellaire.

---

## 2. Modifier la personnalité et le prompt système

La personnalité d'Oscar est régie par la clé `"personnalite_ia"`. Vous pouvez la réécrire selon l'ambiance souhaitée pour votre cockpit.

### Exemples de styles :

#### Style Actuel : Sarcastique & Pince-sans-rire (Oscar par défaut)
```text
"Tu es Oscar, l'ordinateur de bord et co-pilote IA d'un vaisseau spatial. Tu as un humour noir, cynique, pince-sans-rire et très sarcastique. Tu adores taquiner le Commandant sur ses talents de pilotage, sa passion obsessionnelle pour les cailloux (le minage), l'exploration ou ses dépenses inutiles, tout en restant ultra-concis (1 à 2 phrases maximum). Ne donne jamais de conseils de sécurité ennuyeux."
```

#### Variante : Ordinateur de bord militaire strict
```text
"Tu es l'ordinateur de bord tactique d'un croiseur spatial de la Fédération. Tu es extrêmement formel, froid, précis et efficace. Tu réponds de manière concise (1 phrase) sans fioritures et avec le jargon militaire adapté."
```

#### Variante : Copilote chaleureuse et bienveillante
```text
"Tu es Sophie, une copilote attentive, enthousiaste et protectrice. Tu veilles sur la sécurité du Commandant avec chaleur et professionnalisme, tout en restant concise (1 à 2 phrases maximum)."
```

> ⚠️ **Consigne impérative à préserver :** Pour conserver le bon fonctionnement des modes Dictée et Épellation, veillez à toujours conserver la consigne des balises à la fin de votre prompt :
> `... Si le Commandant demande à écrire, dicter du texte ou passer en mode dictée, formule une courte réplique et termine impérativement par [MODE_DICTEE]. S'il demande à épeler ou passer en mode lettre à lettre, termine impérativement par [MODE_EPELLATION]. N'UTILISE JAMAIS de gras (**), de listes à puces ni de numérotation.`

---

## 3. Changer la voix de synthèse (Edge-TTS) et la vitesse

Oscar utilise les voix neurales haute définition de **Microsoft Edge-TTS**. Vous pouvez sélectionner n'importe quelle voix française disponible et régler le débit d'élocution.

Dans `config_oscar.json` :
```json
"tts": {
  "voix": "fr-FR-HenriNeural",
  "vitesse": "+8%"
}
```

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

## 4. Ajouter de nouveaux vaisseaux d'Elite Dangerous

Frontier Developments ajoute régulièrement de nouveaux vaisseaux (ex: *Python Mk II*, *Mandalay*, *Caspian Explorer*, *Cobra Mk V*...).

Le dictionnaire `"noms_vaisseaux"` fait correspondre le code technique interne renvoyé par les journaux du jeu avec son appellation officielle lisible :

```json
"noms_vaisseaux": {
  "mandalay": "Mandalay",
  "python_nx": "Python Mk II",
  "explorer_nx": "Caspian Explorer",
  "cobramkv": "Cobra Mk V",
  "votre_nouveau_code": "Nom Officiel du Vaisseau"
}
```

### Comment trouver le code interne d'un nouveau vaisseau ?
1. Montez à bord du nouveau vaisseau en jeu.
2. Ouvrez le dernier fichier `Journal.*.log` situé dans `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous`.
3. Recherchez l'événement `"event":"Loadout"` ou `"event":"LoadGame"`.
4. Repérez la valeur du champ `"Ship"` (ex: `"Ship":"explorer_nx"`).
5. Ajoutez simplement la ligne correspondante dans `config_oscar.json` en minuscules :
   `"explorer_nx": "Caspian Explorer"`

---

## 5. Ajuster les délais de simulation clavier DirectX

Si vous jouez sur une configuration avec une fréquence d'images (FPS) variable ou sur un écran avec V-Sync élevé, vous pouvez ajuster les temporisations matérielles dans la section `"delais_clavier"` :

```json
"delais_clavier": {
  "delai_apres_ptt_relachement": 0.06,
  "delai_frappe_down": 0.025,
  "delai_frappe_up": 0.015,
  "delai_ctrl_combinaison": 0.035,
  "delai_clipboard_injection": 0.04
}
```

- **`delai_apres_ptt_relachement` (0.06s) :** Délai d'attente après le relâchement physique du bouton Push-To-Talk avant d'injecter du texte (laisse à Windows le temps de libérer Ctrl/Shift).
- **`delai_frappe_down` (0.025s) / `delai_frappe_up` (0.015s) :** Durée d'enfoncement et de relâchement des touches matérielles (Backspace, Entrée, etc.). Une valeur trop courte (< 0.01s) pourrait être manquée par le moteur DirectX du jeu.
- **`delai_clipboard_injection` (0.04s) :** Temps de stabilisation de la mémoire tampon Windows lors d'un collage `Ctrl + V`.

---

## 6. Personnaliser le vocabulaire des commandes vocales

Dans la section `"commandes_modes"`, vous pouvez ajouter vos propres synonymes préférés pour piloter les modes :

- **`validation_dictee` :** Mots-clés pour envoyer et quitter le mode dictée (ex: ajoutez `"transmission"`, `"publier"`).
- **`correction_dictee` :** Mots-clés pour corriger le dernier bloc (ex: `"oups"`, `"gommer"`).
- **`paragraphe_dictee` :** Mots-clés pour sauter une ligne (ex: `"retour chariot"`, `"saut"`).
- **`commandes_sortie` :** Mots-clés d'annulation universelle (ex: `"rompez"`, `"stop là"`).
- **`alphabet_phonetique` :** Vous pouvez y ajouter des prénoms ou termes personnalisés pour l'épellation (ex: `"darko": "D"`, `"barbare": "B"`).

---

## 7. Ajouter de nouvelles commandes physiques (VoiceAttack)

Vous pouvez enrichir à volonté le catalogue des commandes physiques du vaisseau (par exemple pour gérer de nouvelles fonctionnalités d'Elite Dangerous ou des macros personnalisées).

### 🚨 La Règle d'Or : Identité Syntaxique Absolue
Le nom de la commande ajouté dans **`data/commandes_vaisseau.txt`** doit être **STRICTEMENT IDENTIQUE** (au caractère près : majuscules, accents, espaces, tirets) au nom de la macro correspondante créée dans votre profil **VoiceAttack**.

**Pourquoi ?**
Lorsqu'un ordre est reconnu, GPT-4o-mini pioche le nom exact dans `commandes_vaisseau.txt` et produit la balise `[EXECUTE:Nom_De_La_Commande]`. Le script Python transmet ensuite cet ordre directement à VoiceAttack via la ligne de commande :
```cmd
VoiceAttack.exe -command "Nom_De_La_Commande"
```
Si le moindre accent, majuscule ou espace diffère entre `commandes_vaisseau.txt` et VoiceAttack, VoiceAttack ignorera l'ordre !

### Procédure pas-à-pas pour ajouter une commande :
1. **Dans VoiceAttack :**  
   Créez votre nouvelle macro (ex: `Lancer Sonde Reconnaissance`) et associez-lui un raccourci clavier (ex: `Ctrl + Alt + K`).
2. **Dans Elite Dangerous (Bindings) :**  
   Dans les options de commandes du jeu, assignez ce même raccourci (`Ctrl + Alt + K`) dans la colonne **Secondaire** (`<Secondary>`) de l'action souhaitée.
3. **Dans `data/commandes_vaisseau.txt` :**  
   Ajoutez simplement une nouvelle ligne contenant le nom exact de la commande :
   ```text
   Lancer Sonde Reconnaissance
   ```
4. **Relancez Oscar (`IA_Elite.bat`) :**  
   Au démarrage, Oscar charge automatiquement la liste actualisée. Vous pouvez désormais lui demander à la voix : *« Oscar, balance une sonde »* ou *« Lance la reconnaissance »*, et il déclenchera fidèlement votre macro !

