# Correction des collisions de placement — KiCad 10.0.6 (28/09/2026)

## Changements

- **D3** déplacée de `(105,90 ; 92,10)` à `(103,50 ; 104,00)` sur F.Cu, orientation 90° conservée. Le trou de fixation H1 reste à sa place. Cette zone dégage les courtyards, pads, trous traversants et connecteurs sur les deux faces. Ce déplacement allonge potentiellement la liaison de protection/alimentation `+5V` ↔ `+5V_SYS` : son trajet, sa largeur et la chute de tension doivent être vérifiés pendant le routage.
- **U12 BMP581** : les 20 segments de courtyard, dont plusieurs de longueur nulle et qui se croisaient, sont remplacés par un rectangle fermé `2,6162 × 2,6162 mm`. Correction dans le PCB et dans l'empreinte locale.
- Les **22 positions figées** restent inchangées. Aucune piste ni via n'a été ajoutée.

## Comparaison des contrôles natifs

| KiCad 10.0.6 | Avant | Après |
|---|---:|---:|
| DRC, violations | 519 | **496** |
| DRC, erreurs | 104 | **82** |
| Courts-circuits détectés | 1 (D3/H1, +5V/GND) | **0** |
| Chevauchements de courtyards | 1 (D3/H1) | **0** |
| Courtyard malformé | 19 (U12) | **0** |
| Connexions non routées | 353 | **353** |
| ERC, violations | 341 (23 erreurs, 318 avertissements) | **341** (schéma non modifié) |

Les scripts `verify_design.py` (156 empreintes, 562 couples broche/pad), `check_connectivity.py`, `audit_placement.py` et `audit_through_holes.py` ne signalent pas de nouvelle discordance/collision dans leur périmètre. Le DRC natif fait foi pour les défauts de cuivre et mécanique.

## Défauts encore ouverts

- **32 erreurs de dégagement cuivre** : toutes entre pads d'une même empreinte (U1, U4, U10, U11). Leur correction requiert l'examen des land patterns constructeur ou une règle locale documentée; déplacer ces composants ne peut pas supprimer leurs erreurs internes.
- **39 ponts de masque**, tous liés à la fenêtre B.Mask sous U12. L'ouverture suit la recommandation Bosch de ne pas mettre de masque sous le capteur, mais les ponts entre pads exigent une décision avec l'assembleur et une vérification de production.
- **Deux erreurs de contour Edge.Cuts** (auto-intersections) et **neuf dégagements cuivre/bord**, dont les trous de fixation/connecteurs figés. Le contour mécanique doit être validé avec les dimensions du châssis avant modification.
- La sérigraphie et trois différences entre empreinte embarquée et bibliothèque locale sont encore signalées par KiCad. Le déplacement D3 peut produire des avertissements de sérigraphie près de U2/R31.
- Le PCB reste **non routé**. ERC, DRC et fabricant doivent être revus après corrections et routage. Cette passe ne libère pas la fabrication.
