# FC_01 — revue schéma, PCB, empreintes et placement (28/09/2026)

État du PCB : **pré-routage, non libéré pour fabrication**. Les deux faces F.Cu/B.Cu et les trous traversants ont été examinés. Les 22 références figées (connecteurs, fixations, U8, U14, USB1) restent à leur emplacement initial.

## Corrections de cette passe

| Cellule | Changement | Résultat géométrique |
|---|---|---|
| U6, C30, C32 | U6 orienté 270°; condensateurs entrée/sortie remis du côté de leurs broches respectives | U6.8→C30.1 : **5,02 → 2,14 mm**; U6.1→C32.1 : **1,61 → 1,93 mm**. Trous USB1 libres. |
| U5, C29, C31 | U5 et ses deux condensateurs retournés sur place, pads alimentation vers le LDO | U5.8→C29.1 : **3,51 → 1,96 mm**; U5.1→C31.1 : **3,66 → 2,23 mm**. |
| U3, L1 | L1 retournée sans déplacer son corps | Broche SW U3.5→L1.1 : **3,87 → environ 3,43 mm**. |
| U9 BMI088 | Ouverture de pâte des 16 pads périphériques diminuée de 0,025 mm par côté sur le PCB et l'empreinte locale | Ouverture 0,20 × 0,625 mm pour pad 0,25 × 0,675 mm : **74,1 % de l'aire cuivre**. |

Les distances sont entre centres de pads, en projection 2D : elles aident à comparer les implantations mais ne mesurent ni longueur routée ni aire de boucle. Aucun composant figé n'a bougé.

## Rapprochement statique

| Contrôle | Résultat |
|---|---|
| Schéma ↔ PCB | **156/156 références**, **562/562 couples broche/pad**; empreintes PCB ↔ bibliothèques locales cohérentes; zéro erreur dans `verify_design.py`. |
| Réseaux | 456 broches avec noms de nets comparées indépendamment; zéro discordance. Aucune fusion ou séparation inattendue des groupes. Les quatre couples MCU↔résistance MOTOR1–4 sont comparés explicitement; développement complet des bus à contrôler dans KiCad. |
| Courtyards F.Cu/B.Cu | Aucun recouvrement entre composants d'une même face détecté par `audit_placement.py`. |
| Face opposée / traversants | Aucun contact trou traversant ↔ pad SMD ou courtyard opposé détecté par `audit_through_holes.py`; la projection seule des composants sur deux faces n'est pas une collision physique. |
| Oscillateur et références figées | Y1 du même côté F.Cu que U2; keepout opposé libre; 22 références figées sans déplacement. |
| Routage | **0 piste, 0 via, 2 zones**. Les deux zones ne remplacent pas un remplissage et un DRC natif. |

## Comparaison aux fiches constructeur archivées

| Bloc | Prescription vérifiée | Constat / point restant |
|---|---|---|
| U5/U6 AP7361C | Au moins 1 µF à l'entrée, 2,2 µF à la sortie, céramiques proches de IN/OUT et GND ([fiche](../composants/pdf/AP7361C.pdf)). | C29–C32 : 4,7 µF nominaux; les pads d'alimentation sont à 1,93–2,23 mm des broches utiles. Capacité effective sous polarisation et retour GND à confirmer. |
| U3 LMR43620 | CIN, VCC, BOOT proches; nœud SW court; FB à l'écart du SW ([fiche](../composants/pdf/U3_datasheet.pdf), §9.5.1). | U3→C16 1,88 mm; →C20 1,60 mm; →C21 2,74 mm; SW→L1 ~3,43 mm. Boucles et masse à mesurer après routage. |
| U4 LMR60430-Q1 | Même discipline CIN/BOOT/SW/FB et cuivre thermique ([fiche](../composants/pdf/U4_datasheet.pdf), §8.4.1). | U4→C19 1,61 mm; →C22 2,55 mm; FB→R10 1,22 mm; SW→L2 4,03 mm. Chemin SW, dissipation, épaisseur de cuivre et masse restent à valider. |
| U2 STM32H743, Y1 | Découplage et VCAP près des broches; résonateur HSE proche des entrées ([fiche](../composants/pdf/U2_datasheet.pdf)). | U2→C7 1,88 mm, →C10 1,94 mm; Y1 sur F.Cu, à 4,13/3,19 mm des broches HSE. VCAP 2,2 µF nominal; ESR et capacité effective à confirmer. |
| U9 BMI088 | Stencil signal 70–90 % de la surface pad, épaisseur 80–150 µm ([fiche](../composants/pdf/U9_datasheet.pdf), §8.5). | 74,1 % après correction; épaisseur de stencil à spécifier à l'assembleur. U9 est sous la projection du MCU sur l'autre face : vérifier mécanique/thermique. |
| U12 BMP581 | Pad allongé de 25 µm, séparation ≥200 µm, ni piste ni via sous le capteur; contraintes de masque ([fiche](../composants/pdf/U12_datasheet.pdf), §8.2). | Keepout local B.Cu et pads 0,300 × 0,325 mm présents. Les couches internes et la fenêtre de masque sous le corps restent à confirmer dans KiCad et auprès de l'assembleur. |
| USB1 | Validation du connecteur JAE et des ancrages. | Trous et pads dégagés sur les deux faces. Le PDF JAE archivé n'est pas un plan coté complet : validation mécanique fabricant encore ouverte. |

## Avant libération

Ouvrir le projet dans KiCad, mettre à jour le PCB depuis le schéma en examinant le diff, exécuter ERC puis DRC natifs, remplir les zones et router. Contrôler alors impédance USB selon l'empilage réel, retours de courant, boucles SW, chemins de protection ESD et dégagements 3D. Examiner les points ouverts U12, USB1, VCAP et stencil avec les fiches et l'assembleur. **Aucun ERC/DRC natif n'a été exécuté dans cet environnement**, où `kicad-cli`/`pcbnew` ne sont pas installés; ce rapport ne certifie pas le fonctionnement électrique ou la fabricabilité.
