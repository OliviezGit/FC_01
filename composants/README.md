# Dossier composants FC_01

Contrôle du 27 septembre 2026. **Le dossier est complet pour la présence des fichiers, mais la fabrication et l'approvisionnement ne sont pas entièrement validés.**

- [Rapport PDF complet](controle/CONTROLE_COMPLET.pdf) : 114 pages, empreintes, vues 3D, variantes de symboles et éléments PCB.
- [Nomenclature France](BOM_FR.csv) : 44 références fabricant, 133 composants achetés, prix EUR HT, minimum tarifaire, stock relevé, référence à commander et liens.
- [Inventaire machine](catalogue.json) : associations exactes repères / symbole / empreinte / STEP / PDF / fournisseur.
- [PDF techniques](pdf/) : 35 documents fabricant, dont certains couvrent plusieurs références. [Sources et SHA-256](pdf/SOURCES.json).
- [Bibliothèques KiCad actives](kicad/) : utilisées par les tables du projet. Les anciens fichiers `extralib/` restent des instantanés historiques.
- [Modèles 3D](3d/) : fichiers STEP locaux et [associations/transformations](3d/BINDINGS.json).
- [Éléments PCB](ELEMENTS_PCB.csv) : 22 repères constitués de cuivre ou de trous; symbole et empreinte présents, aucun achat ni composant 3D séparé applicable.

## Résultat

Les 155 repères possèdent un symbole et une empreinte locaux. Les 133 composants achetés possèdent un fichier STEP associé dans la bibliothèque et dans le PCB. Le contrôle indépendant vérifie 560 correspondances broche/pastille, sans écart dans le périmètre analysé. La fusion avec main au commit 8d4ebe12 préserve les positions, orientations et faces courantes. C13, supprimé du schéma dans main, a été retiré du PCB et des nomenclatures. Les pads C35.1, R19.1 et R18.2 suivent désormais la correction ADC_VBAT2 du schéma.

## Propriétés dans les schémas KiCad

Les champs sont renseignés sur **chaque instance de composant** dans les fichiers `.kicad_sch`, et contrôlés contre le catalogue. Les anciens champs DigiKey avec espaces sont synchronisés; les anciens tarifs et références d'autres offres non vérifiées sont effacés pour éviter les contradictions.

| Champ de la propriété du symbole | Contenu |
|---|---|
| `Footprint` / `Footprint_File` | Identifiant KiCad et fichier d'empreinte local. |
| `Symbol_ID` / `Symbol_Library_File` | Variante de symbole utilisée et bibliothèque locale. |
| `Model_3D` / `Model_3D_Type` | Fichier STEP local et nature du modèle, y compris les enveloppes simplifiées. L'association 3D active se trouve dans l'empreinte et dans le PCB. |
| `Datasheet` / `Datasheet_URL` | PDF technique local et URL de sa source. |
| `Component_PDF` | PDF de contrôle avec symbole, empreinte et vue du modèle 3D. |
| `Supplier` / `Supplier_Order_Code` / `Supplier_URL` | Fournisseur France retenu, référence exacte à commander et lien. |
| `Unit_Price_EUR` / `Price_Basis` / `Price_Qty` | Prix par pièce en EUR HT et quantité minimale correspondant au tarif. |
| `Stock_Units` / `Supplier_Status` | Stock relevé et statut, avec distinction entre rupture et offre non confirmée. |
| `Price_Checked` / `Stock_Checked` / `Supplier_Notes` | Date de consultation et réserves sur le relevé. |

Les champs non confirmés restent vides et sont accompagnés du statut explicite. Les 22 éléments fabriqués dans le PCB (pastilles, trous, cavaliers cuivre) portent une mention « non applicable » pour l'achat et le modèle 3D séparé, et un lien vers leur PDF de contrôle. Les 127 symboles d'alimentation/réseau sont aussi vérifiés contre la bibliothèque locale; ils n'ont pas de composant physique à commander. Au total : **282 instances de symboles examinées**, dont 155 repères PCB.

Exports de contrôle : [champs par composant](../verification/SCHEMA_FIELDS.csv) et [toutes les instances de symboles](../verification/SCHEMA_SYMBOLS.csv).

Neuf MPN utilisent une **enveloppe reconstruite**, clairement indiquée dans chaque fiche : LMR43620R5RPER, LMR604303SRAKRQ1, TJA1051TK/3,118, BMP581, DPS368XTSA1, Everlight 19-337/R6GHBHC-M01/2T, CSTNE8M00GH5C000R0, XGL4030-332MEC et DX07S016JA1R1500. Une enveloppe représente l'encombrement renseigné, pas les contacts ni une validation des tolérances. Les autres modèles sont génériques KiCad ou issus du STEP Amphenol fourni. Les modèles LSM6DSV16X et ICM-45686 ont une hauteur adaptée respectivement à 0.83 et 0.81 mm.

Les archives SnapMagic USBLC6 et JAE fournies ont servi de comparaison. Leur licence interdit la redistribution isolée : leurs STEP originaux et leurs versions transformées ne sont pas ajoutés ici. U1 utilise le SOT-666 KiCad; USB1 utilise une enveloppe indépendante. Les symboles et empreintes spécifiques au projet restent intégrés au circuit; ce dossier n'est pas une bibliothèque fournisseur destinée à une redistribution séparée.

## Achats à résoudre

| Repères | MPN exact | Résultat |
|---|---|---|
| R1, R2 | 0402WGF5101TCE | Offre exacte non retrouvée chez Farnell, RS et DigiKey France; prix, stock et code de commande non confirmés. |
| D1 | 19-337/R6GHBHC-M01/2T | Même réserve. |
| R9 | RC0402FR-0716K5L | Référence trouvée à l'international, offre France non confirmée. |
| L1, L2 | XGL4030-332MEC | Fiche DigiKey Marketplace à l'international; disponibilité et tarif France non confirmés. |

Aucune substitution n'a été appliquée. Les données absentes sont laissées vides, jamais remplacées par zéro. Un stock nul indique une rupture sur la page consultée; un stock vide signifie non confirmé. Les disponibilités sont des relevés web, pas des réservations. Les pages peuvent être indexées avec retard.

Pour C1005X5R1C225M050BC, Farnell France 2525017 affiche 0.104 EUR HT par pièce **à partir de 10**, minimum et multiple de 10. La page indexée est ancienne et annonce une vente jusqu'à épuisement : prix et stock à reconfirmer. Le TJA1051TK/3,118 annonce une dernière date d'achat au 26/12/2026 sur DigiKey : cycle de vie à revoir avant approvisionnement.

## Contrôles restant ouverts

Voir [verification/REPORT.md](../verification/REPORT.md). ERC/DRC natifs KiCad non exécutés; le contrôleur indépendant ne développe pas les quatre nets du bus MOTOR. Les pads alternatifs U1/U10/U11, le masque U13, la pâte U5/U6 et le plan complet USB1 requièrent encore validation. Les quatre composants ajoutés dans la revue précédente restent en zone provisoire et leur placement/routage n'est pas terminé.

```sh
python3 tools/verify_design.py
python3 tools/check_connectivity.py
```

Les PDF de contrôle sont des rendus indépendants des fichiers KiCad, pas une sortie native de KiCad. Les numéros et connexions complets se trouvent dans [PINS.csv](../verification/PINS.csv). Les fiches techniques restent la référence pour les spécifications électriques complètes.

## Provenance

Les PDF fabricant et modèles tiers conservent leurs droits d'origine. Les commentaires de licence et noms d’auteur des STEP KiCad sont conservés. Une adresse personnelle présente dans un en-tête a été retirée; la section géométrique STEP est inchangée, et cette modification est tracée dans 3d/SOURCES.json. Les enveloppes paramétriques sont générées par `tools/localize_component_assets.py`; `tools/build_component_catalog.py` et `tools/render_component_catalog.py` régénèrent le catalogue. Dépendances : Python, CadQuery, NumPy, Matplotlib, PyMuPDF, ReportLab et polices DejaVu.
