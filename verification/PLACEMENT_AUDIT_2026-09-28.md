# FC_01 — contrôle schéma, empreintes et implantation (28/09/2026)

Base : `b4cfb44959cea596d19cdc92941de7909c9316be` (`main`). Les positions des 22 références figées par Olivier ont été comparées au PCB de cette base.

**Correction ultérieure :** voir [USB_POWER_REWORK_2026-09-28.md](USB_POWER_REWORK_2026-09-28.md). Le contrôle ci-dessous ignorait les trous traversants de USB1 en face des composants F.Cu; les positions U6/D4/C30/R12 décrites ici sont périmées.

[Aperçu corrigé UP/DOWN des courtyards](PLACEMENT_PREVIEW_2026-09-28.png) : gris = position figée, orange = correction après revue graphique. Cette image ne représente ni les pistes ni les couches internes.

## Revue graphique corrective du 28/09

La première version avait laissé **Y1 au dos**, dans l'espace étroit entre USB1 et J12. Cette implantation était mal choisie. Y1 est désormais sur **F.Cu à (94,80 ; 93,00 mm), angle 180°**, du même côté que U2 et dans l'ordre des broches OSC_IN/OSC_OUT. Les distances directes pad à pad sont de 4,13 mm vers U2.12 et 3,19 mm vers U2.13. Le CSTNE8M00GH5C000R0 intègre ses capacités de charge : il n'y a pas de condensateurs externes à ajouter autour de Y1.

Le keepout de cuivre local suit Y1 sur F.Cu; son keepout opposé est désormais sur B.Cu. **C34** a été déplacé à (97,73 ; 90,87 mm) et **R18** à (93,55 ; 91,03 mm) pour libérer ce keepout. C32, R13, C17, C19 et C46 ont été légèrement espacés de leurs voisins. Le contrôle de courtyards ne trouve aucun recouvrement sur une même face et aucun composant B.Cu dans le keepout opposé de Y1. Les 22 composants figés restent inchangés.

La vue reste une vérification de placement 2D : les textes de sérigraphie, l'accès de soudage, les boîtiers réels et les dégagements cuivre ne sont pas validés par ce contrôle. Le routage et un DRC KiCad restent indispensables.

## Résultat reproductible

| Contrôle | Résultat | Limite |
|---|---:|---|
| Références schéma / PCB | 156 / 156 | Contrôle structurel, pas ERC natif |
| Broches numérotées comparées | 562 | Les quatre nets de bus MOTOR1–4 exigent F8/ERC natifs |
| Symbole local et cache schéma | 156 cohérents | Bibliothèque projet `FC01_Project` |
| Pads PCB / empreintes locales | Aucun écart | Numéros, positions, dimensions, forme, orientation, couches et modèles 3D |
| Groupes de nets schéma / PCB | Aucun conflit ni fusion | Bus MOTOR1–4 exclus du parseur statique |
| Courtyards sur la même face | Aucun recouvrement détecté | Test de rectangles englobants, à confirmer par DRC KiCad |
| Keepout opposé Y1 sur B.Cu | Aucun composant dedans | Zone opposée déplacée avec Y1 |
| Positions figées | 22 inchangées | Coordonnées, angles et faces comparés à `main` |
| Segments routés / vias / zones cuivre | 0 / 26 / 2 à la date de cet audit | Les 26 vias ont ensuite été supprimés; voir correction ultérieure |

Commandes : `python tools/verify_design.py`, `python tools/check_connectivity.py` et `python tools/audit_placement.py --baseline <PCB de b4cfb44>`.

## Références figées

`J3 J13 J14 JP1 J8 J9 J11 J10 J7 J6 J4 J5 J1 J2 H1 H2 H3 H4 USB1 U8 U14 J12`.

## Corrections électriques et bibliothèques

- Les nets des deux pads de **R34, R35 et R36** ont été inversés sur le PCB pour refléter le schéma. Les résistances série séparent désormais les nets MCU et IMU.
- Le symbole local **U7 TJA1057GTK/3Z** est synchronisé avec son cache du schéma. L'ancien PDF TJA1051 enregistré comme `U7_datasheet.pdf` a été remplacé par le PDF NXP TJA1057 Rev. 8.1 (02/03/2026). Les prix et stocks hérités du TJA1051 sont supprimés.
- La référence **R51** est `RC0402FR-0722RL` (22 Ω), vérifiée dans sa fiche Yageo archivée sous `R51_datasheet.pdf`. `RC0402FR-07220RL` désigne 220 Ω et ne doit pas être utilisé pour R51. Son offre France reste non confirmée.
- Les orientations des pads PCB ont été resynchronisées depuis les empreintes locales et les associations 3D U10/U11 ont été remises en accord. Les coordonnées des composants figés n'ont pas changé.

## Contrôle croisé des boîtiers critiques

| Références | Fiche archivée / constat dans l'empreinte | Réserve |
|---|---|---|
| U2 | ST STM32H743VIT6, LQFP100 14 × 14 mm, pas 0,5 mm; 100 pads présents | Routage et découplage à vérifier dans KiCad |
| U3 | TI LMR43620, RPE0009B VQFN-HR 2 × 2 mm; neuf pads avec polygones cuivre propres au boîtier | Stencil et vias thermiques à contrôler à l'assemblage |
| U4 | TI LMR60430-Q1, RAK0009A WQFN-HR 2,5 × 2,0 mm; neuf pads propres au boîtier | Boucle SW/PGND et FB à contrôler après routage |
| U5/U6 | Diodes AP7361C-33FGE-7, U-DFN3030-8 Type E; huit pads au pas 0,65 mm et pad 9 de 1,60 × 2,35 mm | Quatre fenêtres de pâte du pad thermique à qualifier |
| L1/L2 | Coilcraft XGL4030, deux pads de 0,98 × 3,40 mm, centres séparés de 2,37 mm | Validation d'assemblage et disponibilité à confirmer |
| U7 | NXP TJA1057GTK/3Z, HVSON8 SOT782-1; pin 5 VIO, pin 9/EP GND | Offre France à reconfirmer; modèle 3D = enveloppe |

Les autres 39 MPN utilisent les preuves classées dans `EVIDENCE.json`, les 36 PDF hachés dans `SOURCE_HASHES.json`, et les dimensions/pins contrôlés par `verify_design.py`. Ce rapprochement ne constitue pas une validation indépendante de chaque spécification électrique ou de chaque tolérance mécanique constructeur. **USB1** reste marqué « plan primaire coté en attente »; les alternatives de pads U1/U10/U11 et le stencil U5/U6 nécessitent une revue de fabrication.

## Déplacements et distances pad à pad

| Liaison | Avant (mm) | Après (mm) |
|---|---:|---:|
| C7.1 → U2.48 VCAP | 1,60 | 1,88 |
| C10.1 → U2.73 VCAP | 2,58 | 1,94 |
| C3.1 → U2.20 VDDA | 21,95 | 1,75 |
| C9.1 → U2.14 NRST | 23,63 | 1,95 |
| C14.1 → U2.21 VDDA | 19,69 | 2,38 |
| C15.1 → U2.20 VDDA | 20,40 | 2,56 |
| Y1.1 → U2.12 OSC_IN | 17,03 | 4,13 |
| Y1.3 → U2.13 OSC_OUT | 17,09 | 3,19 |
| C19.1 → U4.1 VBAT | 3,53 | 1,75 |
| R10.1 → U4.6 FB | 4,05 | 1,22 |

C7 a été reculé de 0,35 mm pour libérer le courtyard du MCU; sa distance électrique augmente de 0,28 mm. Y1 est maintenant côté F.Cu et son keepout opposé est sur B.Cu. Le filtre ADC_AIRSPEED, dont R18 et C34 ont été déplacés, doit être revu au routage. Le nœud SW U4→L2 reste d'environ 4 mm à vol d'oiseau; le réduire davantage demande de réorganiser toute la cellule 9 V et son routage.

## Blocages avant fabrication

KiCad 10 et `kicad-cli` ne sont pas disponibles dans cet environnement : **ERC, F8 et DRC natifs non exécutés**. Le PCB n'a aucun segment routé; les distances ci-dessus ne sont pas des longueurs de piste. Il faut vérifier dans KiCad les keepouts capteurs U9/U12, les dégagements des trous/connecteurs et les plans GND après remplissage, puis router et exécuter DRC. Ne pas lancer de fabrication sur ce seul audit statique.
