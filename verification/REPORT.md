# FC_01 — revue composants et bibliothèques

Date : 2026-09-27. Base : `8023e116a3f5c59ac772a055e0b58ddf85dce90a`.

**État : corrections intégrées, revue statique terminée ; fabrication non libérée.**
Le projet contient 156 références physiques, 44 MPN distincts et 562 broches/pads numérotés. Les 156 références disposent désormais d'un symbole et d'une empreinte résolus dans le dépôt. Le contrôle statique ne remplace pas KiCad ERC/DRC, une vérification électrique du circuit, ni une qualification d'assemblage.

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

Y1, D1, U11 et U13 étaient absents du PCB : ils sont ajoutés dans une zone d'attente à x=230 mm, y=100/110/120/130 mm, face avant. **Leur placement et le routage restent à effectuer.** Positions, orientations, faces et UUID des 152 empreintes déjà présentes sont conservés. Les nets internes hérités de noms de pins D1 peuvent conserver leur ancien libellé ; les connexions numériques sont inchangées.

Les symboles utilisés sont figés dans `extralib/FC01_Project.kicad_sym`, avec un nom distinct par feuille/variante pour préserver les personnalisations. Les empreintes standard utilisées sont copiées depuis le PCB dans `extralib/vendor/` et référencées par `fp-lib-table`. Il s'agit d'instantanés de ce projet, pas d'une mise à jour vers la dernière bibliothèque KiCad. Les modèles 3D externes ne sont pas couverts par cette autonomie.

`BOM_DigiKey.csv` est régénéré depuis les références actuelles. Prix, dates de prix et statuts commerciaux sont les données préexistantes ; ils n'ont pas été revérifiés aujourd'hui.

## Preuves et portée

- [COMPONENTS.csv](COMPONENTS.csv) : une ligne par référence, MPN, boîtier, symbole, empreinte, statut et source.
- [PINS.csv](PINS.csv) : une ligne par pin avec nom, net PCB, NC et dimensions/positions de pad. Pour les pads `custom`, `size` est la taille de l'ancre ; le polygone complet fait foi.
- [EVIDENCE.json](EVIDENCE.json) : constat par MPN, détails dimensionnels et réserves.
- [SOURCE_HASHES.json](SOURCE_HASHES.json) : empreintes SHA-256 des PDF effectivement téléchargés et examinés. Les PDF ne sont pas redistribués.
- [CHECKS.json](CHECKS.json) : résultats du contrôle reproductible.

Les statuts `MANUFACTURER_LAND_*` concernent les dimensions citées, pas une certification de fabricabilité. `PACKAGE_REVIEWED_STANDARD_LAND` et `FAMILY_PACKAGE_REVIEWED` indiquent un boîtier/famille reconnu avec empreinte standard conservée ; ils ne prétendent pas reproduire un land pattern constructeur spécifique. Les listes de pins exportées constituent une preuve de cohérence des fichiers, pas à elles seules une validation indépendante de toutes les fonctions électriques.

## Contrôles exécutés

Depuis la racine du dépôt :

```sh
python3 tools/verify_design.py
python3 tools/check_connectivity.py
```

Le validateur vérifie : ensembles de références, résolution des bibliothèques locales, égalité symbole embarqué/bibliothèque, ensembles de numéros de pins/pads, géométrie des pads PCB/bibliothèque après normalisation de face/orientation, rattachement UUID et cohérence des groupes de nets. Il ne modifie aucun fichier sans `--write`.

Résultat : **156/156 références, 562 pins/pads, zéro erreur dans le périmètre analysé**. La géométrie des nouveaux pads a également été examinée sur un rendu technique indépendant. Les quatre nets `/MCU/MOTOR1` à `/MCU/MOTOR4` traversent un bus vectoriel que le script ne développe pas : ils sont explicitement exclus du rapprochement entre groupes et restent à vérifier nativement. Les alias de bus et les croisements complexes requièrent aussi le contrôle natif.

## Points ouverts avant fabrication

1. **KiCad 10** : ouvrir le projet, mettre à jour le PCB depuis le schéma (F8), comparer les changements proposés, exécuter ERC puis DRC après placement/routage. `kicad-cli` n'est pas disponible ici ; aucun résultat ERC/DRC natif n'est annoncé.
2. **USB1/JAE et J12/Amphenol** : obtenir/relire les plans cotés complets et valider trous, ancrages, courtyards et sens d'insertion. Les modèles fournisseurs et les références ont été retrouvés ; la validation dimensionnelle complète reste ouverte.
3. **L1/L2 Coilcraft** : confirmer le land pattern mécanique officiel ; les pads existants 0.98 × 3.40 mm aux centres ±1.185 mm sont conservés sans approbation dimensionnelle finale.
4. **U1/U10/U11** : confirmer avec l'assembleur les pads alternatifs conservés/créés. Pour U1, l'empreinte fournisseur SOT-666 est conservée ; elle diffère du dessin conseillé par ST. Pour U11, les dimensions du boîtier et le brochage sont confirmés, mais les extensions de pads sont un choix IPC de projet.
5. **U13 et U5/U6** : approuver respectivement le recouvrement masque SMD choisi (cuivre 0.45, ouverture 0.35 mm) et les quatre fenêtres de pâte thermique. Contrôler les contraintes de montage/nettoyage des capteurs de pression.
6. Réaliser le placement, les dégagements mécaniques, le routage, les contrôles d'alimentation/intégrité des signaux et les sorties de fabrication. Cette revue ne certifie pas le fonctionnement du contrôleur de vol.

Les anciens rapports d'audit du dépôt décrivent des états antérieurs. Pour les modifications de cette révision, ce dossier et les fichiers de conception courants font foi.
