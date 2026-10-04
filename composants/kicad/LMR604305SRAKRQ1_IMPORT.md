# LMR604305SRAKRQ1 — bibliothèque FC_01

Mise à jour du 04/10/2026 à partir de l'archive `LMR604305SRAKRQ1.zip` fournie par l'utilisateur et de la fiche TI LMR60430-Q1, SNAS875E, révision E.

## Utilisation dans KiCad

- Symbole : `H743_Ardupilot:LMR604305SRAKRQ1`.
- Empreinte : `H743_Custom:TI_RAK0009A_WQFN-HR-9_2.5x2.0mm_LMR604305`.
- STEP : `${KIPRJMOD}/composants/3d/LMR604305SRAKRQ1_RAK0009A.step`.
- Les tables de bibliothèques du projet enregistrent déjà `H743_Ardupilot` et `H743_Custom`; aucune configuration supplémentaire n'est nécessaire.

Le composant est disponible pour insertion. Cette mise à jour des bibliothèques ne remplace aucun composant dans les schémas ou dans le PCB.

## Comparaison et corrections

Le symbole du ZIP comporte le brochage exact de la référence 5 V. Ses types électriques SW `power_in` et FB/MODE/RT `unspecified` ne sont pas repris tels quels. Le symbole ajouté utilise la présentation compacte existante du projet, les types ci-dessous et la référence fabricant exacte. Aucun code fournisseur de la référence 3,3 V n'est recopié.

| Broche | Fonction | Type KiCad |
|---|---|---|
| 1 | VIN | power_in |
| 2 | PGND | power_in |
| 3 | SW | power_out |
| 4 | BOOT | passive |
| 5 | PG | open_collector |
| 6 | FB | input |
| 7 | MODE/SYNC | input |
| 8 | RT | passive |
| 9 | EN | input |

BOOT est passif pour représenter le raccordement bootstrap par condensateur sans demander une source d'alimentation externe sur ce nœud. RT est passif pour représenter sa résistance de programmation; PG est une sortie à drain ouvert représentée par le type KiCad `open_collector`.

L'empreinte brute du ZIP dessine plusieurs plages de cuivre comme graphiques `F.Cu`, séparées des pastilles circulaires, et numérote les trois trous thermiques 10, 11 et 12. Ces numéros ne sont pas des broches du composant RAK à neuf broches. L'empreinte intégrée reprend les pastilles personnalisées électriquement connectées de FC_01, ses ouvertures de masque et de pâte, son repère de broche 1 et sa cour intérieure, avec le STEP fourni. Elle ne contient ni cuivre graphique flottant ni pastille 10–12. Les vias thermiques éventuels doivent être posés sur le réseau PGND pendant le routage; les recommandations TI de remplissage, bouchage ou tenting doivent être prises en compte selon le procédé de fabrication.

La géométrie cuivre/masque/pâte est conservée à l'identique de l'empreinte locale existante. Une variante dédiée à la référence 5 V évite de changer les associations historiques et les empreintes déjà placées.

## Contrôles exécutés

- Lecture structurée des fichiers KiCad et absence de noms de symboles dupliqués.
- Les sept symboles précédents de la bibliothèque sont conservés à l'identique; un huitième symbole est ajouté.
- Brochage 1–9 comparé au symbole fourni et à la table TI, page 4.
- Contrôle des neuf pastilles électriques, du lien symbole/empreinte et des chemins de bibliothèques actifs.
- Comparaison de la géométrie au fichier local précédent et revue du plan TI RAK0009A, pages 43–45.
- STEP fourni lu par OpenCascade : dix solides, neuf contacts alignés sur les neuf pastilles; encombrement 2,0 × 2,5 × 0,8 mm et origine de montage Z = 0.
- Le STEP est copié sans modification. SHA-256 : `45047d72ab90321aa5fd37295c414bddf8963955413e9c0bb3c3ade36f1926e9`.

KiCad natif n'est pas installé dans cet environnement : ces contrôles ne constituent pas un ERC/DRC natif ni une validation de fabrication. La validation électrique du convertisseur, son implantation, ses vias thermiques et son intégration au schéma restent distinctes de cette mise à jour de bibliothèque.

Source TI : https://www.ti.com/lit/gpn/LMR60430-Q1
