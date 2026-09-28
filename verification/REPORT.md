# FC_01 — revue composants et bibliothèques

**Mise à jour du 28/09/2026 :** voir [FULL_DESIGN_REVIEW_2026-09-28.md](FULL_DESIGN_REVIEW_2026-09-28.md) pour l'état courant. [USB_POWER_REWORK_2026-09-28.md](USB_POWER_REWORK_2026-09-28.md) et les sections ci-dessous décrivent des révisions précédentes; leurs coordonnées et résultats ne doivent pas être utilisés pour le PCB courant.

Date : 2026-09-27. Base initiale : `8023e116a3f5c59ac772a055e0b58ddf85dce90a`. Fusion avec main : `8d4ebe12d84cf1e334181edc0c4434b1bac12989`.

**État : corrections intégrées, revue statique terminée ; fabrication non libérée.**
Le projet contient 155 références physiques, 44 MPN distincts et 560 broches/pads numérotés. Les 155 références disposent désormais d'un symbole et d'une empreinte résolus dans le dépôt. Le contrôle statique ne remplace pas KiCad ERC/DRC, une vérification électrique du circuit, ni une qualification d'assemblage.

## Revue implantation / CEM — mise à jour du 27/09/2026

Le PCB courant est désormais configuré en **6 couches cuivre** : F.Cu, In1.Cu, In2.Cu, In3.Cu, In4.Cu et B.Cu. Le routage n'a pas commencé : **0 segment, 0 via et 0 zone cuivre**. Le preset différentiel Huaqiu 90 ohms est enregistré dans le projet à **0,2037 mm de largeur / 0,2451 mm d'espacement**.

Les remarques CEM/implantation ont été rapprochées du fichier PCB courant :
- **USB1/U1/R1/R2** : le chevauchement courtyard a été supprimé. La marge courtyard USB1→U1 est d'environ **0,22 mm** ; la validation mécanique finale reste ouverte tant que le plan primaire coté JAE n'est pas archivé.
- **J12 microSD** : l'empreinte Amphenol 10067099-200LF Rev.H est intégrée ; la validation mécanique finale reste requise.
- **VCAP C7/C10** : corrigés sur **F.Cu**, au même côté que le STM32H743. C7 est maintenant à **(87,50 ; 94,05), 90°** et C10 à **(102,50 ; 98,40), 0°**, afin de réduire les boucles VCAP.
- **Y1 8 MHz** : reste actuellement sur **B.Cu**. Il ne doit pas être déplacé sur F.Cu sans réorganisation du bloc 9 V, car **L2 occupe actuellement la zone immédiatement sous OSC_IN/OSC_OUT**. Ce point reste bloquant avant routage.
- **U4/L2 9 V** : la cellule doit encore être repackée ; le feedback R10/R11 et la position de L2 sont à optimiser en même temps que le déplacement de Y1, avec nœud SW minimal et feedback éloigné de SW.
- **D5 / U8 CAN** : D5 est déjà placée au bord du connecteur U8 ; les courtyards sont séparés d'environ **0,47 mm**. Le routage devra conserver connecteur → protection ESD → transceiver sans stub.
- **BMI088 / BMP581** : les keepouts de routage/vias/métal constructeur restent à matérialiser dans KiCad avant routage.
- **Plans internes** : les 6 couches sont créées, mais les plans GND/POWER ne sont pas encore matérialisés par des zones ; la CEM finale ne pourra être validée qu'après routage, stitching et DRC.

## Modifications

| Référence | Correction appliquée |
|---|---|
| U14 | Empreinte JST SH 9 contacts remplacée par la variante SM08B à 8 contacts correspondant au MPN ; pattes 9/10 reliées GND. |
| U5, U6 | Empreinte dédiée Diodes U-DFN3030-8 Type E ; EP 1.60 × 2.35 mm et pads périphériques conformes au plan. Fenêtres de pâte EP à qualifier avec l'assembleur. |
| D2 | Empreinte Diodes SMA avec pads 2.50 × 1.70 mm, centres espacés de 4.00 mm. Ancien modèle Littelfuse conservé dans ses fichiers historiques, mais plus affecté à D2. |
| U12 | Dimensions des six pads haut/bas BMP581 corrigées à 0.300 × 0.325 mm ; ouverture masque sous corps ajoutée selon Bosch. |
| D1 | Noms de broches corrigés : 1 BK, 2 RK, 3 GK, 4 BA, 5 RA, 6 GA ; numéros et fils conservés. Empreinte Everlight dédiée ajoutée. |
| U11 | Empreinte LGA14 ajoutée ; cinq marqueurs NC déplacés sur les extrémités des broches. **GND reste en 6 et VDD en 8**, comme indiqué par TDK. |
| U13, Y1 | Empreintes locales DPS368 et résonateur Murata ajoutées. |
| R34, R35, R36 | Affectations des nets aux pads 1/2 du PCB remises en accord avec le schéma. |
| D4, D5, U8 | Liens datasheet, noms de pins D5 et métadonnée de boîtier GH corrigés. |

Y1, D1, U11 et U13 sont désormais intégrés au PCB courant ; l'ancienne zone d'attente à x=230 mm n'est plus l'état de référence. Le placement actuel du PCB fait foi. Y1 reste néanmoins à reprendre côté F.Cu après réorganisation du bloc 9 V, comme indiqué dans la revue implantation/CEM ci-dessus. C13, supprimé du schéma dans main, est retiré du PCB et des nomenclatures (151 empreintes héritées conservées). La correction ADC_VBAT2 du schéma est reportée sur C35.1, R19.1 et R18.2; aucun segment routé ne portait cet ancien net. Les nets internes hérités de noms de pins D1 peuvent conserver leur ancien libellé ; les connexions numériques sont inchangées.

Les symboles utilisés sont figés dans `composants/kicad/FC01_Project.kicad_sym`, avec un nom distinct par feuille/variante pour préserver les personnalisations. Les empreintes standard utilisées sont copiées depuis le PCB dans `composants/kicad/vendor/` et référencées par `fp-lib-table`. Il s'agit d'instantanés de ce projet, pas d'une mise à jour vers la dernière bibliothèque KiCad. Les 133 composants achetés disposent de modèles STEP locaux. Neuf MPN utilisent une enveloppe reconstruite, sans contacts détaillés; voir `../composants/3d/BINDINGS.json`. Les fichiers `extralib/` historiques restent conservés, mais les tables pointent désormais sur `composants/kicad/`.

La nomenclature actuelle est `../composants/BOM_FR.csv`. Prix et stocks ont été recherchés sur les sites France le 27/09/2026. Quatre MPN restent sans offre France confirmée. Le tarif Farnell C1005X5R1C225M050BC est à partir de 10 pièces et sa source indexée est ancienne. `BOM_DigiKey.csv` est synchronisé avec ces données.

## Preuves et portée

- [COMPONENTS.csv](COMPONENTS.csv) : une ligne par référence, MPN, boîtier, symbole, empreinte, statut et source.
- [PINS.csv](PINS.csv) : une ligne par pin avec nom, net PCB, NC et dimensions/positions de pad. Pour les pads `custom`, `size` est la taille de l'ancre ; le polygone complet fait foi.
- [EVIDENCE.json](EVIDENCE.json) : constat par MPN, détails dimensionnels et réserves.
- [SOURCE_HASHES.json](SOURCE_HASHES.json) : empreintes SHA-256 des PDF effectivement téléchargés et examinés. Les 35 PDF techniques sont désormais archivés dans `../composants/pdf/`; le manifeste courant est `../composants/pdf/SOURCES.json`.
- [CHECKS.json](CHECKS.json) : résultats du contrôle reproductible.
- [SCHEMA_FIELDS.csv](SCHEMA_FIELDS.csv) : propriétés effectivement enregistrées sur les 155 instances de composants des schémas, avec liens locaux, données d'achat et réserves.
- [SCHEMA_SYMBOLS.csv](SCHEMA_SYMBOLS.csv) : les 282 instances de symboles, y compris les 127 symboles d'alimentation/réseau sans composant physique.

Les statuts `MANUFACTURER_LAND_*` concernent les dimensions citées, pas une certification de fabricabilité. `PACKAGE_REVIEWED_STANDARD_LAND` et `FAMILY_PACKAGE_REVIEWED` indiquent un boîtier/famille reconnu avec empreinte standard conservée ; ils ne prétendent pas reproduire un land pattern constructeur spécifique. Les listes de pins exportées constituent une preuve de cohérence des fichiers, pas à elles seules une validation indépendante de toutes les fonctions électriques.

## Contrôles exécutés

Depuis la racine du dépôt :

```sh
python3 tools/verify_design.py
python3 tools/check_connectivity.py
```

Le validateur vérifie : ensembles de références, résolution des bibliothèques locales, égalité symbole embarqué/bibliothèque, ensembles de numéros de pins/pads, géométrie des pads PCB/bibliothèque après normalisation de face/orientation, rattachement UUID et cohérence des groupes de nets. Il ne modifie aucun fichier sans `--write`.

Il contrôle également les propriétés de chaque composant du schéma contre le catalogue, l'existence de ses fichiers locaux et la cohérence des anciens champs commerciaux avec le fournisseur France retenu. Les prix non confirmés sont vides. Les anciens champs USB1 (tarif de bobine et URL erronée), C7/C10 (ancienne offre DigiKey) et les autres valeurs périmées ont été corrigés; les 3D simplifiées restent explicitement identifiées.

Résultat : **155/155 références, 560 pins/pads, zéro erreur dans le périmètre analysé**. La géométrie des nouveaux pads a également été examinée sur un rendu technique indépendant. Les quatre nets `/MCU/MOTOR1` à `/MCU/MOTOR4` traversent un bus vectoriel que le script ne développe pas : ils sont explicitement exclus du rapprochement entre groupes et restent à vérifier nativement. Les alias de bus et les croisements complexes requièrent aussi le contrôle natif.

## Points ouverts avant fabrication

1. **KiCad 10** : ouvrir le projet, mettre à jour le PCB depuis le schéma (F8), comparer les changements proposés, exécuter ERC puis DRC après placement/routage. `kicad-cli` n'est pas disponible ici ; aucun résultat ERC/DRC natif n'est annoncé.
2. **USB1/JAE** : obtenir le plan coté complet et valider les ancrages/courtyard avant fabrication. Le STEP fourni a été orienté et ses contacts rapprochés des pads. **J12/Amphenol** : plan Rev.H maintenant archivé et relu, STEP orienté, corps et contacts cohérents avec le plan; validation d’assemblage reste requise.
3. **L1/L2 Coilcraft** : le plan mécanique document 1575-4 du 19/12/2022 est maintenant archivé et confirme les pads 0.98 × 3.40 mm, entraxe 2.37 mm. L’offre commerciale France reste non confirmée. Le modèle local est une enveloppe nominale.
4. **U1/U10/U11** : confirmer avec l'assembleur les pads alternatifs conservés/créés. Pour U1, l'empreinte fournisseur SOT-666 est conservée ; elle diffère du dessin conseillé par ST. Pour U11, les dimensions du boîtier et le brochage sont confirmés, mais les extensions de pads sont un choix IPC de projet.
5. **U13 et U5/U6** : approuver respectivement le recouvrement masque SMD choisi (cuivre 0.45, ouverture 0.35 mm) et les quatre fenêtres de pâte thermique. Contrôler les contraintes de montage/nettoyage des capteurs de pression.
6. Réaliser le placement, les dégagements mécaniques, le routage, les contrôles d'alimentation/intégrité des signaux et les sorties de fabrication. Cette revue ne certifie pas le fonctionnement du contrôleur de vol.

Les anciens rapports d'audit du dépôt décrivent des états antérieurs. Pour les modifications de cette révision, ce dossier et les fichiers de conception courants font foi.

## Complément documentaire et approvisionnement

Voir [composants/README.md](../composants/README.md) et le [contrôle PDF complet](../composants/controle/CONTROLE_COMPLET.pdf). Les tests vérifient désormais aussi présence locale et égalité des associations 3D PCB/bibliothèque. Les modèles d’enveloppe ne sont pas des modèles détaillés certifiés fabricant.

## Corrections CEM / pré-routage — 27/09/2026 soir

- Netclasses KiCad créées : `POWER`, `USB_90R`, `CAN`, `SENSITIVE`; affectations initiales enregistrées dans le projet. La géométrie USB reste à recalculer/valider contre le stack-up fabricant réel avant routage.
- Cellule 9 V : R10/R11 rapprochées de U4/FB, L2 éloignée de la zone oscillateur; C19 rapprochée de U4. Le routage SW/PGND/FB reste à réaliser selon la boucle minimale du constructeur.
- Buck 5 V : C17 rapprochée de U3 VIN/GND.
- U7 : TJA1051TK/3,118 EOL remplacé au schéma par TJA1057GTK/3Z, brochage /3 et boîtier HVSON8/SOT782 compatibles à conserver lors de la synchronisation PCB.
- D2 : SMAJ30CA non validée pour protection des buck 42 V (clamp max trop élevé). SMAJ24CA identifiée comme piste de correction, mais non imposée car VRWM=24 V est inférieur au 25,2 V d'un pack 6S plein; choix final de protection transitoire encore ouvert.
- Y1 : déplacement final et zone oscillateur dédiée encore ouverts; aucune implantation arbitraire n'a été imposée.
- BMI088/BMP581 : keepouts constructeur cuivre/vias encore à matérialiser précisément dans le PCB.
- SDIO_CLK : résistance série optionnelle encore à intégrer proprement au schéma + PCB; ne pas modifier seulement le PCB.

## Pré-routage CEM — application 27/09/2026

- Y1: zone oscillateur matérialisée; résonateur rapproché du MCU, keepout cuivre/vias local B.Cu et keepout opposé F.Cu pour interdire un convertisseur directement en vis-à-vis.
- BMI088 U9: keepout footprint corrigé pour être local au composant et couvrir la zone sous boîtier; pistes/vias/copper pour interdits dans la zone définie.
- BMP581 U12: keepout sous boîtier ajouté, avec pistes/vias/copper pour interdits; pads autorisés.
- SDIO_CLK: R47 22 ohms ajoutée en série côté source dans MICRO_SD, 0402; option 0 ohm après validation SI. Empreinte synchronisée sur PCB et net carte séparé.
- D2 / architecture VBAT: décision gelée — conserver SMAJ30CA, U3 LMR43620 et U4 LMR60430-Q1. Pas d'eFuse/clamp actif et pas de passage à des buck 60–100 V. Le système est conçu pour VBAT 6S (25,2 V max normal); la SMAJ30CA est une protection transitoire, pas une garantie de clamp <42 V dans toutes les conditions.
- Plans GND In1/In4 ajoutés, ainsi qu'une première couronne de vias de stitching GND périphériques.
- Routage signal complet NON réalisé: le PCB était encore à 0 segment avant cette passe et un routage automatique non revu serait contraire à l'objectif CEM. Les boucles buck, USB 90 ohms, CAN et retours capteurs doivent être routés/revus explicitement.
- ERC/DRC KiCad 10 NON exécuté dans cet environnement: kicad-cli n'est pas disponible. Ne pas considérer la carte libérable avant ouverture/sauvegarde KiCad 10 puis ERC/DRC natifs.

## Décision architecture VBAT / D2 / buck — 27/09/2026

Décision finale pour cette révision: conserver l'architecture simple existante.

- Entrée: VBAT 6S, 25,2 V maximum en fonctionnement normal.
- D2: SMAJ30CA conservée.
- U3: LMR43620 conservé.
- U4: LMR60430-Q1 conservé.
- Aucun eFuse/clamp actif ajouté.
- Aucun remplacement des buck par des versions 60/80/100 V.
- D2 doit rester implantée au plus près de l'entrée VBAT/GND avec boucle de décharge courte et large.
- Les condensateurs d'entrée de chaque buck doivent rester directement associés aux broches VIN/PGND; minimiser les boucles chaudes VIN-SW-PGND.
- Limite documentée: la valeur Vc maximale de la SMAJ30CA à son courant d'essai peut dépasser 42 V; D2 réduit les surtensions mais n'est pas spécifiée comme écrêteur garanti sous l'absolute maximum des buck pour toute impulsion possible.
- Cette limitation est acceptée pour la révision 6S actuelle; elle devra être réévaluée si l'entrée batterie, le câblage, l'ESC, la capacité bulk ou la tension maximale changent.

## Revue placement / corrections — 27/09/2026

- Collision de référence corrigée: la résistance série SDIO_CLK est désormais R51 (22 ohms, option 0 ohm après validation SI). R47 reste exclusivement la résistance MOTOR1 200 ohms.
- PCB synchronisé manuellement pour R51; net SDIO_CLK -> R51 -> J12 CLK conservé.
- L2 déplacée légèrement à (91.6,117.6) pour augmenter l'écart à Y1 sans allonger excessivement la boucle SW U4-L2. Le routage SW_9V devra rester compact et orienté à l'opposé de Y1.
- Découplages H743 rapprochés de la périphérie MCU: C6, C8, C11, C12. Les couloirs d'évasion du LQFP100 sont conservés; aucune piste n'est encore routée.
- Découplages capteurs resserrés: C44/C47 autour de U11, C46/C49/C52 autour de U9, C53 autour de BMP581. U10 était déjà correctement découplé localement.
- Connectique contrôlée: CAN J13/J14/U8 reste sur la périphérie; I2C J8/J9 en bord inférieur; ESC U14 en bord gauche; USB1 en bord supérieur. Cette organisation est conservée pour éviter des traversées inutiles de la zone MEMS.
- Séparation puissance/capteurs: L1/U3 restent côté gauche; U9/U10/U11/U12/U13 côté droit. Les nets SW_5V et SW_9V ne devront pas être routés sous la zone MEMS ni sous Y1.
- Statut: placement nettement plus proche du gel, mais validation DRC et inspection visuelle KiCad 10 requises avant freeze définitif.
