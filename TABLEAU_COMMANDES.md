# 🗺️ Tableau Récapitulatif Complet des Commandes — Copilote Oscar & Elite Dangerous

Ce document détaille la matrice intégrale de correspondance entre les ordres vocaux interceptés par **Oscar**, les macros exécutées dans **VoiceAttack**, et les actions matérielles reçues par le moteur d'**Elite Dangerous** via votre fichier de configuration de touches (`.binds`).

Le copilote Oscar s'appuie sur une architecture non intrusive : toutes les commandes simulées sont injectées dans la colonne **Secondaire** (`<Secondary>`) d'Elite Dangerous, ce qui garantit que vos raccourcis principaux (HOTAS, manette ou clavier principal) ne sont **jamais altérés ni écrasés**.

---

## 🧭 Structure des 5 colonnes du tableau

1. **Commande VoiceAttack / IA :** Nom textuel exact de l'ordre figurant dans `data/commandes_vaisseau.txt` et dans le profil VoiceAttack (`data/Barbare Darko-Profile.vap`). Lorsqu'une commande comporte des variantes ou des bascules (toggle), les alias vocaux sont indiqués entre parenthèses.

2. **Touche dans VoiceAttack :** Séquence de touches physique simulée par VoiceAttack sur le clavier AZERTY français (ex: `Ctrl gauche + ^`, `Shift gauche + F`, `F12`, `1`).

3. **Mode Elite Dangerous :** Contexte opérationnel du jeu dans lequel s'applique la commande (`Général`, `Vaisseau`, `VRS` ou `À pied`).

4. **Action dans Elite Dangerous :** Libellé officiel de la fonction en français dans les menus du jeu, accompagné de la balise XML exacte correspondante dans le fichier `.binds`.

5. **Touche dans le fichier `.binds` (QWERTY/XML) :** Touche matérielle DirectInput reconnue par le moteur d'Elite Dangerous (ex: `Key_LeftControl + Key_LeftBracket`), avec la mention de la clé XML brute si elle diffère.

---

## 📊 Grand Tableau des 110 Actions de Pilotage (Vaisseau, VRS, À pied & Général)

> 💡 **Prise en charge multi-modes :** Lorsqu'une même commande vocale agit sur plusieurs contextes du jeu (par exemple les *Phares / Torche*, la *Vision nocturne*, les *Cartes Galactique/Système* ou le *Mode ATH*), une ligne distincte est créée pour chaque mode afin de refléter la balise XML spécifique correspondante dans Elite Dangerous.


| Commande VoiceAttack / IA | Touche dans VoiceAttack | Mode Elite Dangerous | Action dans Elite Dangerous | Touche dans le fichier `.binds` (QWERTY/XML) |
| :--- | :--- | :---: | :--- | :--- |
| Activer Assistance Vol / Désactiver Assistance Vol (`Activer Assistance Vol;Désactiver Assistance Vol`) | `1` | **Vaisseau** | Activer / Couper l'assistance de vol (`<ToggleFlightAssist>`) | `Key_Ampersand` |
| Activer Correction Rotationnelle / Désactiver Correction Rotationnelle (`Activer Correction Rotationnelle;Désactiver Correction Rotationnelle`) | `2` | **Vaisseau** | Activer / Couper la correction rotationnelle (`<DisableRotationCorrectToggle>`) | `Key_é` |
| Afficher Orbite / Supprimer Orbite (`Afficher Orbite;Supprimer Orbite`) | `3` | **Vaisseau** | Afficher / Masquer les lignes d'orbite (`<OrbitLinesToggle>`) | `Key_DoubleQuote` |
| Cible devant | `4` | **Vaisseau** | Verrouiller la cible devant soi (`<SelectTarget>`) | `Key_Apostrophe` |
| Cible Suivante | `5` | **Vaisseau** | Cibler le vaisseau suivant (`<CycleNextTarget>`) | `Key_LeftParenthesis` |
| Vaisseau précédent | `6` | **Vaisseau** | Cibler le vaisseau précédent (`<CyclePreviousTarget>`) | `Key_Minus` |
| Menace principale | `7` | **Vaisseau** | Cibler la menace principale (plus grand danger) (`<SelectHighestThreat>`) | `Key_è` |
| Cible Hostile Suivante | `8` | **Vaisseau** | Cibler le vaisseau hostile suivant (`<CycleNextHostileTarget>`) | `Key_Underline` |
| Vaisseau Ennemi Précédent | `9` | **Vaisseau** | Cibler le vaisseau hostile précédent (`<CyclePreviousHostileTarget>`) | `Key_ç` |
| Coéquipier 1 | `A` | **Général** | Cibler le coéquipier 1 (`<TargetWingman0>`) | `Key_A` |
| Coéquipier 2 | `Z` | **Général** | Cibler le coéquipier 2 (`<TargetWingman1>`) | `Key_Z` |
| Coéquipier 3 | `E` | **Général** | Cibler le coéquipier 3 (`<TargetWingman2>`) | `Key_E` |
| Cible du coéquipier | `R` | **Général** | Cibler la cible du coéquipier (`<SelectTargetsTarget>`) | `Key_R` |
| Suivre le coéquipier | `T` | **Général** | Verrouillage navigationnel d'escadrille (suivre le coéquipier) (`<WingNavLock>`) | `Key_T` |
| Sous-système suivant | `Y` | **Vaisseau** | Cibler le sous-système suivant (ex: Générateur) (`<CycleNextSubsystem>`) | `Key_Y` |
| Sous-système précédent | `U` | **Vaisseau** | Cibler le sous-système précédent (`<CyclePreviousSubsystem>`) | `Key_U` |
| Cibler prochain système de l'itinéraire | `I` | **Vaisseau** | Cibler le prochain système de l'itinéraire (`<TargetNextRouteSystem>`) | `Key_I` |
| Armes Suivantes | `O` | **Vaisseau** | Groupe d'armes suivant (`<CycleFireGroupNext>`) | `Key_O` |
| Armes Précédentes | `Q` | **Vaisseau** | Groupe d'armes précédent (`<CycleFireGroupPrevious>`) | `Key_Q` |
| Déployer Points d'emport / Rentrer Points d'emport (`Déployer Points d'emport;Rentrer Points d'emport`) | `S` | **Vaisseau** | Déployer / Rentrer les points d'emport (armes) (`<DeployHardpointToggle>`) | `Key_S` |
| Passer Mode Furtif | `D` | **Vaisseau** | Activer / Désactiver le mode furtif (Silent Running) (`<ToggleButtonUpInput>`) | `Key_D` |
| Ejecter Dissipateur Thermique | `F` | **Vaisseau** | Éjecter un dissipateur thermique (`<DeployHeatSink>`) | `Key_F` |
| Allumer Phares / Eteindre Phares (`Allumer Phares;Eteindre Phares;Allumer Torche;Eteindre Torche`) | `F12` | **Vaisseau** | Allumer / Éteindre les phares du vaisseau (`<ShipSpotLightToggle>`) | `Key_F12` |
| Equilibrer Puissance | `G` | **Vaisseau** | Équilibrer la répartition d'énergie (Systèmes / Moteurs / Armes) (`<ResetPowerDistribution>`) | `Key_G` |
| Réinitialisation Visiocasque | `H` | **Général** | Réinitialisation du visiocasque VR / Suivi de tête (TrackIR) (`<HMDReset>`) | `Key_H` |
| Ouvrir Récupérateur Cargaison / Fermer Récupérateur Cargaison (`Ouvrir Récupérateur Cargaison;Fermer Récupérateur Cargaison`) | `J` | **Vaisseau** | Ouvrir / Fermer le récupérateur de cargaison (écope) (`<ToggleCargoScoop>`) | `Key_J` |
| Larguer Cargaison | `K` | **Vaisseau** | Larguer toute la cargaison (`<EjectAllCargo>`) | `Key_K` |
| Sortir Train Atterrissage / Rentrer Train Atterrissage (`Sortir Train Atterrissage;Rentrer Train Atterrissage`) | `L` | **Vaisseau** | Sortir / Rentrer le train d'atterrissage (`<LandingGearToggle>`) | `Key_L` |
| Charger Cellule énergie | `M` | **Vaisseau** | Charger / Déclencher une cellule d'énergie de bouclier (`<UseShieldCell>`) | `Key_M` |
| Lancer Paillettes / Ejecter Paillettes (`Lancer Paillettes;Ejecter Paillettes`) | `ù` | **Vaisseau** | Lancer / Éjecter des paillettes de brouillage (Chaff) (`<FireChaffLauncher>`) | `Key_Apostrophe (XML : Key_ù)` |
| Champ incapacitant | `W` | **Vaisseau** | Activer le neutralisateur de champ Thargoid (`<TriggerFieldNeutraliser>`) | `Key_W` |
| Charger CME | `X` | **Vaisseau** | Déclencher les contre-mesures électroniques (CME) (`<ChargeECM>`) | `Key_X` |
| Activer Vision Nocturne / Désactiver Vision Nocturne (`Activer Vision Nocturne;Désactiver Vision Nocturne`) | `C` | **Vaisseau** | Activer / Désactiver la vision nocturne du cockpit (`<NightVisionToggle>`) | `Key_C` |
| Colonisation Système | `V` | **Vaisseau** | Activer module de colonisation / balise de colonisation (`<TriggerColonisationModule>`) | `Key_V` |
| Ouvrir Carte Galactique | `B` | **Vaisseau** | Ouvrir la carte galactique (`<GalaxyMapOpen>`) | `Key_B` |
| Ouvrir Carte Système | `N` | **Vaisseau** | Ouvrir la carte du système (`<SystemMapOpen>`) | `Key_N` |
| Activer Mode Combat / Activer Mode Analyse (`Activer Mode Combat;Activer Mode Analyse`) | `,` | **Vaisseau** | Basculer mode ATH (Combat / Analyse) (`<PlayerHUDModeToggle>`) | `Key_Comma` |
| Activer Mode ACS | `;` | **Vaisseau** | Activer le mode ACS (Scanner de détection complet FSS) (`<ExplorationFSSEnter>`) | `Key_SemiColon` |
| Centre Système Actuel | `1` | **Général** | Centrer la carte galactique sur le système actuel (`<GalaxyMapHome>`) | `Key_Ampersand` |
| Activer Frein Stationnement / Enlever Frein Stationnement (`Mettre Frein Stationnement;Enlever Frein Stationnement`) | `Shift gauche + F` | **VRS** | Activer / Enlever le frein de stationnement du VRS (`<AutoBreakBuggyButton>`) | `Key_LeftShift + Key_F` |
| Allumer Phares / Eteindre Phares (`Allumer Phares;Eteindre Phares;Allumer Torche;Eteindre Torche`) | `F12` | **VRS** | Allumer / Éteindre les phares du VRS (`<HeadlightsBuggyButton>`) | `Key_F12` |
| Passer Tourelle / Activer Tourelle / Retour Cockpit / Désactiver Tourelle (`Passer Tourelle;Activer Tourelle;Retour Cockpit;Désactiver Tourelle`) | `Shift gauche + T` | **VRS** | Activer tourelle VRS / Retour poste de pilotage (`<ToggleBuggyTurretButton>`) | `Key_LeftShift + Key_T` |
| Armes Suivantes | `O` | **VRS** | Groupe d'armes suivant en VRS (`<BuggyCycleFireGroupNext>`) | `Key_O` |
| Armes Précédentes | `Q` | **VRS** | Groupe d'armes précédent en VRS (`<BuggyCycleFireGroupPrevious>`) | `Key_Q` |
| Cible devant | `4` | **VRS** | Cibler devant soi en VRS (`<SelectTarget_Buggy>`) | `Key_Apostrophe` |
| Equilibrer Puissance | `G` | **VRS** | Équilibrer la répartition d'énergie en VRS (`<ResetPowerDistribution_Buggy>`) | `Key_G` |
| Ouvrir Récupérateur Cargaison / Fermer Récupérateur Cargaison (`Ouvrir Récupérateur Cargaison;Fermer Récupérateur Cargaison`) | `J` | **VRS** | Ouvrir / Fermer le récupérateur de cargaison du VRS (`<ToggleCargoScoop_Buggy>`) | `Key_J` |
| Larguer Cargaison | `K` | **VRS** | Larguer toute la cargaison du VRS (`<EjectAllCargo_Buggy>`) | `Key_K` |
| Rappeler Vaisseau / Renvoyer Vaisseau | `Shift gauche + R` | **VRS** | Rappeler / Renvoyer le vaisseau en orbite (`<RecallDismissShip>`) | `Key_LeftShift + Key_R` |
| Ouvrir Carte Galactique | `B` | **VRS** | Ouvrir la carte galactique depuis le VRS (`<GalaxyMapOpen_Buggy>`) | `Key_B` |
| Ouvrir Carte Système | `N` | **VRS** | Ouvrir la carte du système depuis le VRS (`<SystemMapOpen_Buggy>`) | `Key_N` |
| Activer Mode Combat / Activer Mode Analyse (`Activer Mode Combat;Activer Mode Analyse`) | `,` | **VRS** | Basculer mode ATH (Combat / Analyse) en VRS (`<PlayerHUDModeToggle_Buggy>`) | `Key_Comma` |
| Rappeler Chasseur | `Pavé num 1` | **Vaisseau** | Ordre chasseur : Demander l'arrimage au vaisseau mère (`<OrderRequestDock>`) | `Key_Numpad_1` |
| Chasseur Défendre | `Pavé num 2` | **Vaisseau** | Ordre chasseur : Posture défensive (`<OrderDefensiveBehaviour>`) | `Key_Numpad_2` |
| Chasseur Feu à volonté | `Pavé num 3` | **Vaisseau** | Ordre chasseur : Feu à volonté (`<OrderAggressiveBehaviour>`) | `Key_Numpad_3` |
| Chasseur Attaquer Cible | `Pavé num 4` | **Vaisseau** | Ordre chasseur : Attaquer ma cible (`<OrderFocusTarget>`) | `Key_Numpad_4` |
| Chasseur Maintenir Formation | `Pavé num 5` | **Vaisseau** | Ordre chasseur : Cessez-le-feu / Maintenir la formation (`<OrderHoldFire>`) | `Key_Numpad_5` |
| Chasseur Maintenir Position | `Pavé num 6` | **Vaisseau** | Ordre chasseur : Maintenir la position (`<OrderHoldPosition>`) | `Key_Numpad_6` |
| Chasseur Me Suivre | `Pavé num 7` | **Vaisseau** | Ordre chasseur : Me suivre (`<OrderFollow>`) | `Key_Numpad_7` |
| Chasseur Ouvrir Ordres | `Pavé num 8` | **Vaisseau** | Ouvrir le panneau des ordres du chasseur (`<OpenOrders>`) | `Key_Numpad_8` |
| Désactiver ATH / Activer ATH (`Désactiver ATH;Activer ATH`) | `1` | **Général** | Activer / Désactiver l'ATH (Caméra libre / Cockpit) (`<FreeCamToggleHUD>`) | `Key_Ampersand` |
| Lecture Pause News | `2` | **Général** | Galnet Audio : Lecture / Pause (`<GalnetAudio_Play_Pause>`) | `Key_é` |
| News Suivante | `3` | **Général** | Galnet Audio : Article suivant (`<GalnetAudio_SkipForward>`) | `Key_DoubleQuote` |
| News Précédente | `4` | **Général** | Galnet Audio : Article précédent (`<GalnetAudio_SkipBackward>`) | `Key_Apostrophe` |
| Effacer Liste Lecture | `5` | **Général** | Galnet Audio : Vider la liste de lecture (`<GalnetAudio_ClearQueue>`) | `Key_LeftParenthesis` |
| Quitter ACS | `Q` | **Vaisseau** | Quitter le mode ACS (Scanner de détection complet FSS) (`<ExplorationFSSQuit>`) | `Key_Q` |
| Vue arrière ou avant planète | `F1` | **Vaisseau** | Sondage planétaire DSS : Inverser la vue avant / arrière (`<ExplorationSAAChangeScannedAreaViewToggle>`) | `Key_F1` |
| Quitter DSS | `F2` | **Vaisseau** | Quitter le scanner de surface détaillée (DSS) (`<ExplorationSAAExitThirdPerson>`) | `Key_F2` |
| Affiche Roue d'inventaire / Enlève Roue d'inventaire (`Affiche Roue d'inventaire;Enlève Roue d'inventaire`) | `Ctrl gauche + A` | **À pied** | Afficher / Masquer la roue d'inventaire (`<HumanoidItemWheelButton>`) | `Key_LeftControl + Key_A` |
| Affiche Roue d'émoticomes / Enlève Roue d'émoticomes (`Affiche Roue d'émoticomes;Enlève Roue d'émoticomes`) | `Ctrl gauche + Z` | **À pied** | Afficher / Masquer la roue des émoticônes (`<HumanoidEmoteWheelButton>`) | `Key_LeftControl + Key_Z` |
| Lance une grenade | `Ctrl gauche + E` | **À pied** | Lancer une grenade (`<HumanoidThrowGrenadeButton>`) | `Key_LeftControl + Key_E` |
| Recharge Arme | `Ctrl gauche + R` | **À pied** | Recharger l'arme active (`<HumanoidReloadButton>`) | `Key_LeftControl + Key_R` |
| Change Arme | `Ctrl gauche + T` | **À pied** | Changer d'arme / Alterner les armes (`<HumanoidSwitchWeapon>`) | `Key_LeftControl + Key_T` |
| Arme principale | `Ctrl gauche + Y` | **À pied** | Sélectionner l'arme principale (Emplacement 1) (`<HumanoidSelectPrimaryWeaponButton>`) | `Key_LeftControl + Key_Y` |
| Arme secondaire | `Ctrl gauche + U` | **À pied** | Sélectionner l'arme secondaire (Emplacement 2) (`<HumanoidSelectSecondaryWeaponButton>`) | `Key_LeftControl + Key_U` |
| Range Outil | `Ctrl gauche + I` | **À pied** | Sélectionner l'outil lourd / arme utilitaire (Emplacement 3) (`<HumanoidSelectUtilityWeaponButton>`) | `Key_LeftControl + Key_I` |
| Arme suivante | `Ctrl gauche + O` | **À pied** | Sélectionner l'arme suivante (`<HumanoidSelectNextWeaponButton>`) | `Key_LeftControl + Key_O` |
| Arme précédente | `Ctrl gauche + P` | **À pied** | Sélectionner l'arme précédente (`<HumanoidSelectPreviousWeaponButton>`) | `Key_LeftControl + Key_P` |
| Ranger Arme / Ranger Outil (`Ranger Arme;Ranger Outil`) | `Ctrl gauche + ^` | **À pied** | Ranger l'arme / Rengainer (`<HumanoidHideWeaponButton>`) | `Key_LeftControl + Key_LeftBracket (XML : Key_Circumflex)` |
| Grenade suivante | `Ctrl gauche + $` | **À pied** | Type de grenade suivant (`<HumanoidSelectNextGrenadeTypeButton>`) | `Key_LeftControl + Key_RightBracket (XML : Key_Dollar)` |
| Grenade précédente | `Ctrl gauche + Q` | **À pied** | Type de grenade précédent (`<HumanoidSelectPreviousGrenadeTypeButton>`) | `Key_LeftControl + Key_Q` |
| Allumer Phares / Eteindre Phares (`Allumer Phares;Eteindre Phares;Allumer Torche;Eteindre Torche`) | `F12` | **À pied** | Allumer / Éteindre la lampe torche de la combinaison (`<HumanoidToggleFlashlightButton>`) | `Key_F12` |
| Activer Vision Nocturne / Désactiver Vision Nocturne (`Activer Vision Nocturne;Désactiver Vision Nocturne`) | `C` | **À pied** | Activer / Désactiver la vision nocturne de la combinaison (`<HumanoidToggleNightVisionButton>`) | `Key_C` |
| Activer Bouclier / Désactiver Bouclier (`Activer Bouclier;Désactiver Bouclier`) | `Ctrl gauche + S` | **À pied** | Activer / Désactiver le bouclier personnel de la combinaison (`<HumanoidToggleShieldsButton>`) | `Key_LeftControl + Key_S` |
| Supprime Accréditation | `D` | **À pied** | Supprimer le profil d'accréditation volé (effacer identité) (`<HumanoidClearAuthorityLevel>`) | `Key_LeftControl + Key_D` |
| Soigne moi / Kit de santé (`Soigne moi;Kit de santé`) | `Ctrl gauche + 9` | **À pied** | Utiliser une trousse de soins (Medkit) (`<HumanoidHealthPack>`) | `Key_RightControl + Key_F` |
| Utilise Cellule Energie | `Ctrl gauche + G` | **À pied** | Utiliser une cellule d'énergie / batterie de recharge (`<HumanoidBattery>`) | `Key_LeftControl + Key_G` |
| Grenade Fragmentation | `Ctrl gauche + H` | **À pied** | Sélectionner la grenade à fragmentation (`<HumanoidSelectFragGrenade>`) | `Key_LeftControl + Key_H` |
| Grenade IEM | `J` | **À pied** | Sélectionner la grenade IEM (impulsion électromagnétique) (`<HumanoidSelectEMPGrenade>`) | `Key_LeftControl + Key_J` |
| Grenade Bouclier | `Ctrl gauche + K` | **À pied** | Sélectionner la grenade à bouclier (`<HumanoidSelectShieldGrenade>`) | `Key_LeftControl + Key_K` |
| Active énergiseur | `Ctrl gauche + L` | **À pied** | Équiper l'outil de liaison énergétique (Énergiseur) (`<HumanoidSwitchToRechargeTool>`) | `Key_LeftControl + Key_L` |
| Active Analyseur Profil | `Ctrl gauche + M` | **À pied** | Équiper l'analyseur génétique / profil de composition (`<HumanoidSwitchToCompAnalyser>`) | `Key_LeftControl + Key_M` |
| Prend Outil / Prend Outil Combinaison (`Prend Outil Combinaison` / `Prend Outil;Range Outil`) | `Ctrl gauche + ù` | **À pied** | Équiper l'outil de combinaison polyvalent (`<HumanoidSwitchToSuitTool>`) | `Key_LeftControl + Key_Apostrophe (XML : Key_ù)` |
| Change Mode Outil | `Ctrl gauche + *` | **À pied** | Changer le mode de l'outil actif (`<HumanoidToggleToolModeButton>`) | `Key_LeftControl + Key_BackSlash (XML : Key_Asterisk)` |
| Affiche l'aide / Masque l'aide (`Affiche l'aide;Masque l'aide`) | `Ctrl gauche + W` | **À pied** | Afficher / Masquer l'aide de mission (`<HumanoidToggleMissionHelpPanelButton>`) | `Key_LeftControl + Key_W` |
| Ouvrir Carte Galactique | `B` | **À pied** | Ouvrir la carte galactique à pied (`<GalaxyMapOpen_Humanoid>`) | `Key_B` |
| Ouvrir Carte Système | `N` | **À pied** | Ouvrir la carte du système à pied (`<SystemMapOpen_Humanoid>`) | `Key_N` |
| Affiche Panneau Communication / Masque Panneau Communication (`Affiche Panneau Communication;Masque Panneau Communication`) | `Ctrl gauche + X` | **À pied** | Afficher / Masquer le panneau de communication (`<FocusCommsPanel_Humanoid>`) | `Key_LeftControl + Key_X` |
| Affiche Panneau Com Rapide / Masque Panneau Com Rapide (`Affiche Panneau Com Rapide;Masque Panneau Com Rapide`) | `Ctrl gauche + C` | **À pied** | Afficher / Masquer le panneau de communication rapide (`<QuickCommsPanel_Humanoid>`) | `Key_LeftControl + Key_C` |
| Ouvre Menu Insight / Ferme Menu Insight (`Ouvre Menu Insight;Ferme Menu Insight`) | `Ctrl gauche + !` | **À pied** | Ouvrir / Fermer le menu d'accès Insight (`<HumanoidOpenAccessPanelButton>`) | `Key_LeftControl + Key_Slash (XML : Key_ExclamationPoint)` |
| Affiche Statistique Combat / Masque Statistique Combat (`Affiche Statistique Combat;Masque Statistique Combat`) | `Ctrl gauche + B` | **À pied** | Afficher / Masquer les statistiques de zone de conflit (`<HumanoidConflictContextualUIButton>`) | `Key_LeftControl + Key_B` |
| *(Commande directe clavier / non vocale)* | — | **Général** | Ouvrir / Fermer la boutique cosmétique Frontier Store (`<StoreToggle>`) | `Key_Tab` |
| Pointe le doigt | `Ctrl gauche + 1` | **À pied** | Émoticône 1 : Pointer du doigt (`<HumanoidEmoteSlot1>`) | `Key_LeftControl + Key_Ampersand` |
| Fais un coucou | `Ctrl gauche + 2` | **À pied** | Émoticône 2 : Saluer de la main (Coucou) (`<HumanoidEmoteSlot2>`) | `Key_LeftControl + Key_é` |
| Fais un geste d'accord | `Ctrl gauche + 3` | **À pied** | Émoticône 3 : Geste d'accord / Approbation (`<HumanoidEmoteSlot3>`) | `Key_LeftControl + Key_DoubleQuote` |
| Fais un non | `Ctrl gauche + 4` | **À pied** | Émoticône 4 : Geste de désaccord / Refus (Non) (`<HumanoidEmoteSlot4>`) | `Key_LeftControl + Key_Apostrophe` |
| Fais un en avant | `Ctrl gauche + 5` | **À pied** | Émoticône 5 : Signe « En avant » (Avancer) (`<HumanoidEmoteSlot5>`) | `Key_LeftControl + Key_LeftParenthesis` |
| Fais un Stop | `Ctrl gauche + 6` | **À pied** | Émoticône 6 : Signe « Stop » (Arrêt) (`<HumanoidEmoteSlot6>`) | `Key_LeftControl + Key_Minus` |
| Fais un applaudissement | `Ctrl gauche + 7` | **À pied** | Émoticône 7 : Applaudissements (`<HumanoidEmoteSlot7>`) | `Key_LeftControl + Key_è` |
| Fais un salut | `Ctrl gauche + 8` | **À pied** | Émoticône 8 : Salut militaire (`<HumanoidEmoteSlot8>`) | `Key_LeftControl + Key_Underline` |

---

## ⚙️ Section Spéciale — Les 4 Commandes Système de VoiceAttack

Ces 4 commandes fondamentales ne pilotent pas directement le vaisseau en jeu. Elles constituent **l'ossature de communication** entre vos périphériques physiques, l'interface VoiceAttack et le moteur de reconnaissance vocale et d'intelligence artificielle d'Oscar.


| Commande Système | Type & Déclencheur | Séquence dans VoiceAttack | Rôle technique dans l'architecture Oscar |
| :--- | :--- | :--- | :--- |
| **`COM_IA_ON`** | **Matériel (HOTAS)**<br>Enfoncement continu du bouton Push-To-Talk assigné | `Key Down` (Enfoncement)<br>`Ctrl gauche + Shift gauche + F9` | **Ouverture de l'enregistrement micro PTT :** Enclenche la capture audio en continu via `sounddevice` tant que le bouton physique reste enfoncé. |
| **`COM_IA_OFF`** | **Matériel (HOTAS)**<br>Relâchement du bouton Push-To-Talk assigné | `Key Up` (Relâchement)<br>`Ctrl gauche + Shift gauche + F9` | **Clôture & Déclenchement de l'IA :** Coupe la capture micro, transmet le fichier audio à `Faster-Whisper` (sur GPU NVIDIA) pour transcription locale ultra-rapide (0.2s), puis soumet la requête à `GPT-4o-mini` pour réponse vocale immédiate via Edge-TTS ou déclenchement d'une macro `[EXECUTE:...]`. |
| **`Oscar`** | **Vocal (Mains Libres)**<br>Énonciation du mot-clé de réveil : *« Oscar »* | 1. Réponse sonore vocale aléatoire *(Paul)*<br>2. `Key Down` de `Ctrl gauche + Shift gauche + F9` | **Activation Mains Libres (Wake Word) :** Détecte l'appel vocal sans toucher au HOTAS, accuse réception vocalement (*« Oui commandant ? »*, *« À tes ordres ! »*...) et maintient le canal d'enregistrement micro grand ouvert. |
| **`Terminé`**<br>(`*Terminé`) | **Vocal (Mains Libres)**<br>Énonciation du mot-clé de fin : *« Terminé »* | `Key Up` (Relâchement)<br>`Ctrl gauche + Shift gauche + F9` | **Validation de l'ordre Mains Libres :** Relâche la touche virtuelle PTT, fermant le canal d'enregistrement et lançant l'analyse Whisper / GPT-4o-mini de la commande dictée. |

### 💡 Précisions importantes sur le Push-To-Talk et la personnalisation :
1. **Combinaison interne par défaut (`Ctrl + Shift + F9`) :** Cette combinaison a été spécialement retenue car elle ne comporte pas la touche `Alt` (évitant ainsi tout déclenchement indésirable des barres de menus Windows pendant les sessions de jeu ou de dictée).
2. **Modification du raccourci :** Si cette combinaison entre en conflit avec un logiciel tiers (ex: GeForce Experience, Discord, OBS), vous pouvez la modifier à la fois dans `config_oscar.json` (clé `"raccourci_ptt"`) et dans VoiceAttack au sein des 4 commandes ci-dessus.
3. **Mode Dictée & Mode Épellation :** En mode Dictée et en mode Épellation, le mot-clé « Oscar » ne doit pas être prononcé pour éviter que VoiceAttack n'intercepte l'appel. Pour taper la lettre **O** dans la carte galactique, utilisez toujours le prénom **« Olivier »**.

---

## 📈 Statistiques et Couverture du Profil

- **Total des balises secondaires clavier cartographiées :** 110 actions.
- **Répartition par mode Elite Dangerous :**
  - 🛸 **Mode Vaisseau :** 47 actions (Pilotage, Ciblage, Systèmes de bord, Armement, Chasseurs embarqués, Exploration/Scanners).
  - 🚗 **Mode VRS (Surface Recon Vehicle) :** 13 actions (Conduite, Tourelle, Phares, Cargaison, Rappel vaisseau).
  - 🥾 **Mode À pied (Odyssey) :** 42 actions (Armes, Outils énergétiques/analyseurs, Medkit, Batteries, Grenades, Émoticônes).
  - 🌐 **Mode Général :** 8 actions (Navigation escadrille, Carte galactique, Galnet Audio, Caméra libre, Visiocasque).
- **Commandes système de communication :** 4 commandes (`COM_IA_ON`, `COM_IA_OFF`, `Oscar`, `Terminé`).
- **Total des ordres vocaux et variantes reconnus dans `commandes_vaisseau.txt` :** 121 macros opérationnelles.

---
---

# 🗺️ Complete Command Reference Table — Oscar Copilot & Elite Dangerous

This document details the full mapping matrix between voice commands intercepted by **Oscar**, macros executed inside **VoiceAttack**, and hardware keystrokes received by **Elite Dangerous** via your keybindings file (`.binds`).

Oscar relies on a non-intrusive architecture: all simulated commands are injected into Elite Dangerous's **Secondary** column (`<Secondary>`), ensuring that your primary controls (HOTAS, controller, or main keyboard binds) are **never altered or overwritten**.

---

## 🧭 Structure of the 5 Table Columns

1. **VoiceAttack / AI Command:** Exact text name of the order listed in `data/commandes_vaisseau.txt` and in the VoiceAttack profile (`data/Barbare Darko-Profile.vap`). When a command includes variants or toggles, voice aliases are shown in parentheses.
2. **VoiceAttack Keystroke:** Physical key sequence simulated by VoiceAttack on a French AZERTY keyboard (e.g., `Ctrl gauche + ^`, `Shift gauche + F`, `F12`, `1`).
3. **Elite Dangerous Mode:** Operational game context in which the command applies (`General`, `Ship`, `SRV`, or `On-Foot`).
4. **Elite Dangerous Action:** In-game function description accompanied by its exact XML tag in the `.binds` file.
5. **`.binds` Key (QWERTY/XML):** DirectInput hardware key name recognized by Elite Dangerous's engine (e.g., `Key_LeftControl + Key_LeftBracket`), noting the raw XML key when applicable.

---

## 📊 Master Table of 110 Piloting Actions (Ship, SRV, On-Foot & General)

> 💡 **Multi-Mode Support:** When a single voice command operates across multiple game contexts (such as *Lights / Flashlight*, *Night Vision*, *Galaxy / System Maps*, or *HUD Mode*), a separate row is listed for each mode to reflect its specific XML tag in Elite Dangerous.

| VoiceAttack / AI Command | VoiceAttack Keystroke | Elite Dangerous Mode | Elite Dangerous Action | `.binds` Key (QWERTY/XML) |
| :--- | :--- | :---: | :--- | :--- |
| Activer Assistance Vol / Désactiver Assistance Vol (`Activer Assistance Vol;Désactiver Assistance Vol`) | `1` | **Ship** | Toggle Flight Assist (`<ToggleFlightAssist>`) | `Key_Ampersand` |
| Activer Correction Rotationnelle / Désactiver Correction Rotationnelle (`Activer Correction Rotationnelle;Désactiver Correction Rotationnelle`) | `2` | **Ship** | Toggle Rotational Correction (`<DisableRotationCorrectToggle>`) | `Key_é` |
| Afficher Orbite / Supprimer Orbite (`Afficher Orbite;Supprimer Orbite`) | `3` | **Ship** | Toggle Orbit Lines (`<OrbitLinesToggle>`) | `Key_DoubleQuote` |
| Cible devant | `4` | **Ship** | Select Target Ahead (`<SelectTarget>`) | `Key_Apostrophe` |
| Cible Suivante | `5` | **Ship** | Cycle Next Target (`<CycleNextTarget>`) | `Key_LeftParenthesis` |
| Vaisseau précédent | `6` | **Ship** | Cycle Previous Target (`<CyclePreviousTarget>`) | `Key_Minus` |
| Menace principale | `7` | **Ship** | Select Highest Threat (`<SelectHighestThreat>`) | `Key_è` |
| Cible Hostile Suivante | `8` | **Ship** | Cycle Next Hostile Target (`<CycleNextHostileTarget>`) | `Key_Underline` |
| Vaisseau Ennemi Précédent | `9` | **Ship** | Cycle Previous Hostile Target (`<CyclePreviousHostileTarget>`) | `Key_ç` |
| Coéquipier 1 | `A` | **General** | Select Wingman 1 (`<TargetWingman0>`) | `Key_A` |
| Coéquipier 2 | `Z` | **General** | Select Wingman 2 (`<TargetWingman1>`) | `Key_Z` |
| Coéquipier 3 | `E` | **General** | Select Wingman 3 (`<TargetWingman2>`) | `Key_E` |
| Cible du coéquipier | `R` | **General** | Select Wingman's Target (`<SelectTargetsTarget>`) | `Key_R` |
| Suivre le coéquipier | `T` | **General** | Wingman Nav-Lock (`<WingNavLock>`) | `Key_T` |
| Sous-système suivant | `Y` | **Ship** | Cycle Next Subsystem (e.g., Power Plant) (`<CycleNextSubsystem>`) | `Key_Y` |
| Sous-système précédent | `U` | **Ship** | Cycle Previous Subsystem (`<CyclePreviousSubsystem>`) | `Key_U` |
| Cibler prochain système de l'itinéraire | `I` | **Ship** | Target Next System in Route (`<TargetNextRouteSystem>`) | `Key_I` |
| Armes Suivantes | `O` | **Ship** | Cycle Next Fire Group (`<CycleFireGroupNext>`) | `Key_O` |
| Armes Précédentes | `Q` | **Ship** | Cycle Previous Fire Group (`<CycleFireGroupPrevious>`) | `Key_Q` |
| Déployer Points d'emport / Rentrer Points d'emport (`Déployer Points d'emport;Rentrer Points d'emport`) | `S` | **Ship** | Deploy / Retract Hardpoints (`<DeployHardpointToggle>`) | `Key_S` |
| Passer Mode Furtif | `D` | **Ship** | Toggle Silent Running (`<ToggleButtonUpInput>`) | `Key_D` |
| Ejecter Dissipateur Thermique | `F` | **Ship** | Deploy Heat Sink (`<DeployHeatSink>`) | `Key_F` |
| Allumer Phares / Eteindre Phares (`Allumer Phares;Eteindre Phares;Allumer Torche;Eteindre Torche`) | `F12` | **Ship** | Toggle Ship Lights (`<ShipSpotLightToggle>`) | `Key_F12` |
| Equilibrer Puissance | `G` | **Ship** | Reset Power Distribution (`<ResetPowerDistribution>`) | `Key_G` |
| Réinitialisation Visiocasque | `H` | **General** | Reset HMD / Headlook Orientation (`<HMDReset>`) | `Key_H` |
| Ouvrir Récupérateur Cargaison / Fermer Récupérateur Cargaison (`Ouvrir Récupérateur Cargaison;Fermer Récupérateur Cargaison`) | `J` | **Ship** | Toggle Cargo Scoop (`<ToggleCargoScoop>`) | `Key_J` |
| Larguer Cargaison | `K` | **Ship** | Jettison All Cargo (`<EjectAllCargo>`) | `Key_K` |
| Sortir Train Atterrissage / Rentrer Train Atterrissage (`Sortir Train Atterrissage;Rentrer Train Atterrissage`) | `L` | **Ship** | Toggle Landing Gear (`<LandingGearToggle>`) | `Key_L` |
| Charger Cellule énergie | `M` | **Ship** | Use Shield Cell Bank (`<UseShieldCell>`) | `Key_M` |
| Lancer Paillettes / Ejecter Paillettes (`Lancer Paillettes;Ejecter Paillettes`) | `ù` | **Ship** | Fire Chaff Launcher (`<FireChaffLauncher>`) | `Key_Apostrophe (XML: Key_ù)` |
| Champ incapacitant | `W` | **Ship** | Trigger Shutdown Field Neutraliser (`<TriggerFieldNeutraliser>`) | `Key_W` |
| Charger CME | `X` | **Ship** | Charge Electronic Countermeasure (ECM) (`<ChargeECM>`) | `Key_X` |
| Activer Vision Nocturne / Désactiver Vision Nocturne (`Activer Vision Nocturne;Désactiver Vision Nocturne`) | `C` | **Ship** | Toggle Night Vision (`<NightVisionToggle>`) | `Key_C` |
| Colonisation Système | `V` | **Ship** | Trigger Colonisation Module / Beacon (`<TriggerColonisationModule>`) | `Key_V` |
| Ouvrir Carte Galactique | `B` | **Ship** | Open Galaxy Map (`<GalaxyMapOpen>`) | `Key_B` |
| Ouvrir Carte Système | `N` | **Ship** | Open System Map (`<SystemMapOpen>`) | `Key_N` |
| Activer Mode Combat / Activer Mode Analyse (`Activer Mode Combat;Activer Mode Analyse`) | `,` | **Ship** | Switch HUD Mode (Combat / Analysis) (`<PlayerHUDModeToggle>`) | `Key_Comma` |
| Activer Mode ACS | `;` | **Ship** | Enter Full Spectrum System Scanner (FSS) (`<ExplorationFSSEnter>`) | `Key_SemiColon` |
| Centre Système Actuel | `1` | **General** | Center Galaxy Map on Current System (`<GalaxyMapHome>`) | `Key_Ampersand` |
| Activer Frein Stationnement / Enlever Frein Stationnement (`Mettre Frein Stationnement;Enlever Frein Stationnement`) | `Shift gauche + F` | **SRV** | Toggle SRV Handbrake (`<AutoBreakBuggyButton>`) | `Key_LeftShift + Key_F` |
| Allumer Phares / Eteindre Phares (`Allumer Phares;Eteindre Phares;Allumer Torche;Eteindre Torche`) | `F12` | **SRV** | Toggle SRV Headlights (`<HeadlightsBuggyButton>`) | `Key_F12` |
| Passer Tourelle / Activer Tourelle / Retour Cockpit / Désactiver Tourelle (`Passer Tourelle;Activer Tourelle;Retour Cockpit;Désactiver Tourelle`) | `Shift gauche + T` | **SRV** | Toggle SRV Turret View (`<ToggleBuggyTurretButton>`) | `Key_LeftShift + Key_T` |
| Armes Suivantes | `O` | **SRV** | SRV Cycle Next Fire Group (`<BuggyCycleFireGroupNext>`) | `Key_O` |
| Armes Précédentes | `Q` | **SRV** | SRV Cycle Previous Fire Group (`<BuggyCycleFireGroupPrevious>`) | `Key_Q` |
| Cible devant | `4` | **SRV** | SRV Select Target Ahead (`<SelectTarget_Buggy>`) | `Key_Apostrophe` |
| Equilibrer Puissance | `G` | **SRV** | SRV Reset Power Distribution (`<ResetPowerDistribution_Buggy>`) | `Key_G` |
| Ouvrir Récupérateur Cargaison / Fermer Récupérateur Cargaison (`Ouvrir Récupérateur Cargaison;Fermer Récupérateur Cargaison`) | `J` | **SRV** | SRV Toggle Cargo Scoop (`<ToggleCargoScoop_Buggy>`) | `Key_J` |
| Larguer Cargaison | `K` | **SRV** | SRV Jettison All Cargo (`<EjectAllCargo_Buggy>`) | `Key_K` |
| Rappeler Vaisseau / Renvoyer Vaisseau | `Shift gauche + R` | **SRV** | Recall / Dismiss Ship (`<RecallDismissShip>`) | `Key_LeftShift + Key_R` |
| Ouvrir Carte Galactique | `B` | **SRV** | Open Galaxy Map from SRV (`<GalaxyMapOpen_Buggy>`) | `Key_B` |
| Ouvrir Carte Système | `N` | **SRV** | Open System Map from SRV (`<SystemMapOpen_Buggy>`) | `Key_N` |
| Activer Mode Combat / Activer Mode Analyse (`Activer Mode Combat;Activer Mode Analyse`) | `,` | **SRV** | SRV Switch HUD Mode (Combat / Analysis) (`<PlayerHUDModeToggle_Buggy>`) | `Key_Comma` |
| Rappeler Chasseur | `Pavé num 1` | **Ship** | Fighter Order: Request Dock (`<OrderRequestDock>`) | `Key_Numpad_1` |
| Chasseur Défendre | `Pavé num 2` | **Ship** | Fighter Order: Defensive Behaviour (`<OrderDefensiveBehaviour>`) | `Key_Numpad_2` |
| Chasseur Feu à volonté | `Pavé num 3` | **Ship** | Fighter Order: Aggressive / Fire at Will (`<OrderAggressiveBehaviour>`) | `Key_Numpad_3` |
| Chasseur Attaquer Cible | `Pavé num 4` | **Ship** | Fighter Order: Attack My Target (`<OrderFocusTarget>`) | `Key_Numpad_4` |
| Chasseur Maintenir Formation | `Pavé num 5` | **Ship** | Fighter Order: Hold Fire / Maintain Formation (`<OrderHoldFire>`) | `Key_Numpad_5` |
| Chasseur Maintenir Position | `Pavé num 6` | **Ship** | Fighter Order: Hold Position (`<OrderHoldPosition>`) | `Key_Numpad_6` |
| Chasseur Me Suivre | `Pavé num 7` | **Ship** | Fighter Order: Follow Me (`<OrderFollow>`) | `Key_Numpad_7` |
| Chasseur Ouvrir Ordres | `Pavé num 8` | **Ship** | Open Fighter Orders Panel (`<OpenOrders>`) | `Key_Numpad_8` |
| Désactiver ATH / Activer ATH (`Désactiver ATH;Activer ATH`) | `1` | **General** | Toggle HUD (Free Camera / Cockpit) (`<FreeCamToggleHUD>`) | `Key_Ampersand` |
| Lecture Pause News | `2` | **General** | Galnet Audio: Play / Pause (`<GalnetAudio_Play_Pause>`) | `Key_é` |
| News Suivante | `3` | **General** | Galnet Audio: Next Track (`<GalnetAudio_SkipForward>`) | `Key_DoubleQuote` |
| News Précédente | `4` | **General** | Galnet Audio: Previous Track (`<GalnetAudio_SkipBackward>`) | `Key_Apostrophe` |
| Effacer Liste Lecture | `5` | **General** | Galnet Audio: Clear Queue (`<GalnetAudio_ClearQueue>`) | `Key_LeftParenthesis` |
| Quitter ACS | `Q` | **Ship** | Exit Full Spectrum System Scanner (FSS) (`<ExplorationFSSQuit>`) | `Key_Q` |
| Vue arrière ou avant planète | `F1` | **Ship** | DSS Planetary Probe: Toggle Front / Back View (`<ExplorationSAAChangeScannedAreaViewToggle>`) | `Key_F1` |
| Quitter DSS | `F2` | **Ship** | Exit Detailed Surface Scanner (DSS) (`<ExplorationSAAExitThirdPerson>`) | `Key_F2` |
| Affiche Roue d'inventaire / Enlève Roue d'inventaire (`Affiche Roue d'inventaire;Enlève Roue d'inventaire`) | `Ctrl gauche + A` | **On-Foot** | Open / Close Item Wheel (`<HumanoidItemWheelButton>`) | `Key_LeftControl + Key_A` |
| Affiche Roue d'émoticomes / Enlève Roue d'émoticomes (`Affiche Roue d'émoticomes;Enlève Roue d'émoticomes`) | `Ctrl gauche + Z` | **On-Foot** | Open / Close Emote Wheel (`<HumanoidEmoteWheelButton>`) | `Key_LeftControl + Key_Z` |
| Lance une grenade | `Ctrl gauche + E` | **On-Foot** | Throw Grenade (`<HumanoidThrowGrenadeButton>`) | `Key_LeftControl + Key_E` |
| Recharge Arme | `Ctrl gauche + R` | **On-Foot** | Reload Active Weapon (`<HumanoidReloadButton>`) | `Key_LeftControl + Key_R` |
| Change Arme | `Ctrl gauche + T` | **On-Foot** | Switch Weapon (`<HumanoidSwitchWeapon>`) | `Key_LeftControl + Key_T` |
| Arme principale | `Ctrl gauche + Y` | **On-Foot** | Select Primary Weapon (Slot 1) (`<HumanoidSelectPrimaryWeaponButton>`) | `Key_LeftControl + Key_Y` |
| Arme secondaire | `Ctrl gauche + U` | **On-Foot** | Select Secondary Weapon (Slot 2) (`<HumanoidSelectSecondaryWeaponButton>`) | `Key_LeftControl + Key_U` |
| Range Outil | `Ctrl gauche + I` | **On-Foot** | Select Heavy / Utility Weapon (Slot 3) (`<HumanoidSelectUtilityWeaponButton>`) | `Key_LeftControl + Key_I` |
| Arme suivante | `Ctrl gauche + O` | **On-Foot** | Select Next Weapon (`<HumanoidSelectNextWeaponButton>`) | `Key_LeftControl + Key_O` |
| Arme précédente | `Ctrl gauche + P` | **On-Foot** | Select Previous Weapon (`<HumanoidSelectPreviousWeaponButton>`) | `Key_LeftControl + Key_P` |
| Ranger Arme / Ranger Outil (`Ranger Arme;Ranger Outil`) | `Ctrl gauche + ^` | **On-Foot** | Holster Weapon (`<HumanoidHideWeaponButton>`) | `Key_LeftControl + Key_LeftBracket (XML: Key_Circumflex)` |
| Grenade suivante | `Ctrl gauche + $` | **On-Foot** | Select Next Grenade Type (`<HumanoidSelectNextGrenadeTypeButton>`) | `Key_LeftControl + Key_RightBracket (XML: Key_Dollar)` |
| Grenade précédente | `Ctrl gauche + Q` | **On-Foot** | Select Previous Grenade Type (`<HumanoidSelectPreviousGrenadeTypeButton>`) | `Key_LeftControl + Key_Q` |
| Allumer Phares / Eteindre Phares (`Allumer Phares;Eteindre Phares;Allumer Torche;Eteindre Torche`) | `F12` | **On-Foot** | Toggle Suit Flashlight (`<HumanoidToggleFlashlightButton>`) | `Key_F12` |
| Activer Vision Nocturne / Désactiver Vision Nocturne (`Activer Vision Nocturne;Désactiver Vision Nocturne`) | `C` | **On-Foot** | Toggle Suit Night Vision (`<HumanoidToggleNightVisionButton>`) | `Key_C` |
| Activer Bouclier / Désactiver Bouclier (`Activer Bouclier;Désactiver Bouclier`) | `Ctrl gauche + S` | **On-Foot** | Toggle Personal Suit Shields (`<HumanoidToggleShieldsButton>`) | `Key_LeftControl + Key_S` |
| Supprime Accréditation | `D` | **On-Foot** | Clear Stolen Security Profile (`<HumanoidClearAuthorityLevel>`) | `Key_LeftControl + Key_D` |
| Soigne moi / Kit de santé (`Soigne moi;Kit de santé`) | `Ctrl gauche + 9` | **On-Foot** | Use Medkit (`<HumanoidHealthPack>`) | `Key_RightControl + Key_F` |
| Utilise Cellule Energie | `Ctrl gauche + G` | **On-Foot** | Use Energy Cell (`<HumanoidBattery>`) | `Key_LeftControl + Key_G` |
| Grenade Fragmentation | `Ctrl gauche + H` | **On-Foot** | Select Frag Grenade (`<HumanoidSelectFragGrenade>`) | `Key_LeftControl + Key_H` |
| Grenade IEM | `J` | **On-Foot** | Select EMP Grenade (`<HumanoidSelectEMPGrenade>`) | `Key_LeftControl + Key_J` |
| Grenade Bouclier | `Ctrl gauche + K` | **On-Foot** | Select Shield Projector Grenade (`<HumanoidSelectShieldGrenade>`) | `Key_LeftControl + Key_K` |
| Active énergiseur | `Ctrl gauche + L` | **On-Foot** | Equip Energylink Tool (`<HumanoidSwitchToRechargeTool>`) | `Key_LeftControl + Key_L` |
| Active Analyseur Profil | `Ctrl gauche + M` | **On-Foot** | Equip Profile Analyser (`<HumanoidSwitchToCompAnalyser>`) | `Key_LeftControl + Key_M` |
| Prend Outil / Prend Outil Combinaison (`Prend Outil Combinaison` / `Prend Outil;Range Outil`) | `Ctrl gauche + ù` | **On-Foot** | Equip Suit Multi-Tool (`<HumanoidSwitchToSuitTool>`) | `Key_LeftControl + Key_Apostrophe (XML: Key_ù)` |
| Change Mode Outil | `Ctrl gauche + *` | **On-Foot** | Toggle Tool Mode (`<HumanoidToggleToolModeButton>`) | `Key_LeftControl + Key_BackSlash (XML: Key_Asterisk)` |
| Affiche l'aide / Masque l'aide (`Affiche l'aide;Masque l'aide`) | `Ctrl gauche + W` | **On-Foot** | Toggle Mission Help Panel (`<HumanoidToggleMissionHelpPanelButton>`) | `Key_LeftControl + Key_W` |
| Ouvrir Carte Galactique | `B` | **On-Foot** | Open Galaxy Map On-Foot (`<GalaxyMapOpen_Humanoid>`) | `Key_B` |
| Ouvrir Carte Système | `N` | **On-Foot** | Open System Map On-Foot (`<SystemMapOpen_Humanoid>`) | `Key_N` |
| Affiche Panneau Communication / Masque Panneau Communication (`Affiche Panneau Communication;Masque Panneau Communication`) | `Ctrl gauche + X` | **On-Foot** | Focus Comms Panel On-Foot (`<FocusCommsPanel_Humanoid>`) | `Key_LeftControl + Key_X` |
| Affiche Panneau Com Rapide / Masque Panneau Com Rapide (`Affiche Panneau Com Rapide;Masque Panneau Com Rapide`) | `Ctrl gauche + C` | **On-Foot** | Quick Comms Panel On-Foot (`<QuickCommsPanel_Humanoid>`) | `Key_LeftControl + Key_C` |
| Ouvre Menu Insight / Ferme Menu Insight (`Ouvre Menu Insight;Ferme Menu Insight`) | `Ctrl gauche + !` | **On-Foot** | Open / Close Insight Access Hub (`<HumanoidOpenAccessPanelButton>`) | `Key_LeftControl + Key_Slash (XML: Key_ExclamationPoint)` |
| Affiche Statistique Combat / Masque Statistique Combat (`Affiche Statistique Combat;Masque Statistique Combat`) | `Ctrl gauche + B` | **On-Foot** | Toggle Conflict Zone Contextual UI (`<HumanoidConflictContextualUIButton>`) | `Key_LeftControl + Key_B` |
| *(Direct keyboard bind / non-voice)* | — | **General** | Open / Close Frontier Store (`<StoreToggle>`) | `Key_Tab` |
| Pointe le doigt | `Ctrl gauche + 1` | **On-Foot** | Emote 1: Point (`<HumanoidEmoteSlot1>`) | `Key_LeftControl + Key_Ampersand` |
| Fais un coucou | `Ctrl gauche + 2` | **On-Foot** | Emote 2: Wave (`<HumanoidEmoteSlot2>`) | `Key_LeftControl + Key_é` |
| Fais un geste d'accord | `Ctrl gauche + 3` | **On-Foot** | Emote 3: Agree / Thumbs Up (`<HumanoidEmoteSlot3>`) | `Key_LeftControl + Key_DoubleQuote` |
| Fais un non | `Ctrl gauche + 4` | **On-Foot** | Emote 4: Disagree / No (`<HumanoidEmoteSlot4>`) | `Key_LeftControl + Key_Apostrophe` |
| Fais un en avant | `Ctrl gauche + 5` | **On-Foot** | Emote 5: Go Forward (`<HumanoidEmoteSlot5>`) | `Key_LeftControl + Key_LeftParenthesis` |
| Fais un Stop | `Ctrl gauche + 6` | **On-Foot** | Emote 6: Stop (`<HumanoidEmoteSlot6>`) | `Key_LeftControl + Key_Minus` |
| Fais un applaudissement | `Ctrl gauche + 7` | **On-Foot** | Emote 7: Applaud (`<HumanoidEmoteSlot7>`) | `Key_LeftControl + Key_è` |
| Fais un salut | `Ctrl gauche + 8` | **On-Foot** | Emote 8: Salute (`<HumanoidEmoteSlot8>`) | `Key_LeftControl + Key_Underline` |

---

## ⚙️ Special Section — The 4 VoiceAttack System Commands

These 4 core commands do not directly control your ship in-game. Instead, they form the **communication backbone** between your physical controllers, VoiceAttack, and Oscar's speech recognition and AI engine.

| System Command | Type & Trigger | VoiceAttack Sequence | Technical Role in Oscar's Architecture |
| :--- | :--- | :--- | :--- |
| **`COM_IA_ON`** | **Hardware (HOTAS)**<br>Continuous press of assigned Push-To-Talk button | `Key Down` (Press)<br>`Ctrl gauche + Shift gauche + F9` | **Opens PTT Microphone Recording:** Starts continuous audio capture via `sounddevice` for as long as the physical button is held down. |
| **`COM_IA_OFF`** | **Hardware (HOTAS)**<br>Release of assigned Push-To-Talk button | `Key Up` (Release)<br>`Ctrl gauche + Shift gauche + F9` | **Closes & Triggers AI Processing:** Stops mic capture, sends the audio buffer to `Faster-Whisper` (on NVIDIA GPU) for ultra-fast local transcription (0.2s), and submits the query to `GPT-4o-mini` for immediate Edge-TTS voice reply or macro execution (`[EXECUTE:...]`). |
| **`Oscar`** | **Voice (Hands-Free)**<br>Spoken wake word: *"Oscar"* | 1. Random spoken confirmation *(Paul)*<br>2. `Key Down` of `Ctrl gauche + Shift gauche + F9` | **Hands-Free Activation (Wake Word):** Detects the spoken call without touching your HOTAS, acknowledges aloud (*"Oui commandant ?"*, *"À tes ordres !"*...), and holds the recording channel open. |
| **`Terminé`**<br>(`*Terminé`) | **Voice (Hands-Free)**<br>Spoken end keyword: *"Terminé"* | `Key Up` (Release)<br>`Ctrl gauche + Shift gauche + F9` | **Validates Hands-Free Order:** Releases the virtual PTT key, closing the recording channel and triggering Whisper / GPT-4o-mini processing of your spoken request. |

### 💡 Important Notes on Push-To-Talk & Customization:
1. **Default Internal Shortcut (`Ctrl + Shift + F9`):** This combination was specifically chosen because it omits the `Alt` key (preventing unwanted activation of Windows menu bars during gameplay or text dictation).
2. **Changing the Shortcut:** If this keystroke conflicts with third-party software (e.g., GeForce Experience, Discord, OBS), you can update it both inside `config_oscar.json` (`"raccourci_ptt"` key) and inside VoiceAttack across the 4 commands above.
3. **Dictation & Spelling Modes:** While inside Dictation or Spelling mode, avoid saying the wake word "Oscar" so VoiceAttack does not intercept your speech. To type the letter **O** in the Galaxy Map, always use **"Olivier"**.

---

## 📈 Profile Statistics & Coverage

- **Total mapped secondary keyboard actions:** 110 actions.
- **Breakdown by Elite Dangerous mode:**
  - 🛸 **Ship Mode:** 47 actions (Piloting, Targeting, Ship Systems, Hardpoints, Ship-Launched Fighters, Exploration/Scanners).
  - 🚗 **SRV Mode (Surface Recon Vehicle):** 13 actions (Driving, Turret, Lights, Cargo Scoop, Recall/Dismiss Ship).
  - 🥾 **On-Foot Mode (Odyssey):** 42 actions (Weapons, Energylink/Profile Analyser, Medkit, Energy Cells, Grenades, Emotes).
  - 🌐 **General Mode:** 8 actions (Wingman Navigation, Galaxy Map, Galnet Audio, Free Camera, HMD Reset).
- **Communication system commands:** 4 commands (`COM_IA_ON`, `COM_IA_OFF`, `Oscar`, `Terminé`).
- **Total voice orders and variants in `commandes_vaisseau.txt`:** 121 active macros.


