# FC_01 — revue composants et bibliothèques

Date : 2026-09-27. Base initiale : `8023e116a3f5c59ac772a055e0b58ddf85dce90a`. Fusion avec main : `8d4ebe12d84cf1e334181edc0c4434b1bac12989`.

**État : corrections intégrées, revue statique terminée ; fabrication non libérée.**
Le projet contient 155 références physiques, 44 MPN distincts et 560 broches/pads numérotés. Les 155 références disposent désormais d'un symbole et d'une empreinte résolus dans le dépôt. Le contrôle statique ne remplace pas KiCad ERC/DRC, une vérification électrique du circuit, ni une qualification d'assemblage.

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

Y1, D1, U11 et U13 étaient absents du PCB : ils sont ajoutés dans une zone d'attente à x=230 mm, y=100/110/120/130 mm, face avant. **Leur placement et le routage restent à effectuer.** Positions, orientations, faces et UUID courants de main sont conservés. C13, supprimé du schéma dans main, est retiré du PCB et des nomenclatures (151 empreintes héritées conservées). La correction ADC_VBAT2 du schéma est reportée sur C35.1, R19.1 et R18.2; aucun segment routé ne portait cet ancien net. Les nets internes hérités de noms de pins D1 peuvent conserver leur ancien libellé ; les connexions numériques sont inchangées.

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
