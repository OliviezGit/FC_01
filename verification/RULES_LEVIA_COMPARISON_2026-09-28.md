# FC_01 — règles inspirées de LEVIA-H7 (28/09/2026)

Référence examinée : `piecol/LEVIA-H7`, branche `main`, projet `LEVIA_H7.kicad_pro` et `LEVIA_H7.kicad_dru`. Les minima et tailles proposés de LEVIA sont copiés dans `H743_Ardupilot.kicad_pro`; les affectations sont adaptées aux noms des nets FC_01.

| Paramètre | Ancien FC_01 | Nouveau FC_01 / LEVIA |
|---|---:|---:|
| Minimum cuivre/cuivre | 0 mm au niveau carte; 0,20 mm classe Default | 0,127 mm; Default 0,127 mm |
| Minimum cuivre/bord | 0,50 mm | 0,20 mm |
| Minimum largeur de piste | 0,20 mm | 0,127 mm |
| Via minimum / couronne minimum | 0,50 / 0,10 mm | 0,40 / 0,075 mm |
| Trous/pads traversants, écart trou/trou | 0,30 / 0,25 mm | 0,25 / 0,20 mm |
| Dégagement cuivre/trou | 0,25 mm | 0,20 mm |
| Zone par défaut, dégagement / largeur minimale | 0,50 / 0,25 mm | 0,152 / 0,20 mm |
| Zone par défaut, thermique gap / pont | 0,50 / 0,50 mm | 0,20 / 0,45 mm |

Les tailles prédéfinies de piste/via et les valeurs de la classe Default proviennent également du projet LEVIA. Les classes fonctionnelles FC_01 sont conservées et effectivement affectées par motifs : USB, I²C, SPI, SDIO, moteurs, CAN, rails d'alimentation, VCAP et HSE. Les classes `POWER`, `SENSITIVE` et `CAN` ont un dégagement de 0,127 mm afin que leurs pads de circuits fins ne soient pas contredits par l'ancien 0,25 mm; leurs largeurs de routage restent spécifiques. `USB_90R` prend la largeur 0,2037 mm, l'écart 0,2451 mm et le dégagement 0,148 mm de la classe USB LEVIA.

## Exceptions à la copie littérale

- **Pas de copie de `LEVIA_H7.kicad_dru`** : il diminue à 0,05 mm le dégagement des pads au bord et l'autorise à −1 mm pour H1–H4. Ces exceptions ne conviennent pas automatiquement aux trous métallisés Ø5,7 mm et au contour FC_01; leurs erreurs de bord restent visibles.
- **Pas de via USB Ø0,01016 mm / perçage 0,00635 mm** du champ de netclass LEVIA : valeurs inférieures à son propre minimum global. FC_01 utilise provisoirement Ø0,40 mm / perçage 0,25 mm pour cette classe; ce choix est à confirmer avec le fabricant.
- L'empilage physique détaillé de LEVIA n'est pas transposé : FC_01 n'a encore que six couches nommées et une épaisseur totale 1,6 mm. La géométrie USB nominale ne garantit donc pas 90 Ω sur l'empilage du fabricant.
- Les deux zones GND **existantes** gardent leurs propres paramètres (dégagement 0,20 mm, largeur mini 0,20 mm, thermique 0,30 mm); les nouveaux paramètres de zone s'appliquent aux zones créées ultérieurement. Les deux zones doivent être remplies et revues après routage.

## DRC KiCad 10.0.6, avant/après changement de règles

| Type d'erreur | Avant | Après |
|---|---:|---:|
| Dégagement cuivre | 32 | 1 (U4, 0,125 mm réel contre 0,127 mm) |
| Cuivre/bord | 9 | 4 |
| Ponts de masque U12 | 39 | 39 |
| Contour auto-intersecté | 2 | 2 |
| **Total erreurs DRC** | **82** | **46** |
| Connexions non routées | 353 | 353 |

La diminution du nombre d'erreurs provient de règles différentes, **pas d'une modification de cuivre ni d'une preuve de fabricabilité**. Les exigences du fabricant PCB, le plan de l'empreinte U4, l'empilage/impédance USB, le masque du BMP581 et le contour mécanique restent à qualifier avant fabrication.
