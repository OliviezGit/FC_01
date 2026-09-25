# H743_Ardupilot — BOM / EDA audit

Audit date: 2026-09-25

## Scope

Active hierarchical schematic sheets:
- MCU.kicad_sch
- ANALOG_SENS.kicad_sch
- CAN.kicad_sch
- BUZZER.kicad_sch
- MOTORS[1-4].kicad_sch
- UART_I2C.kicad_sch
- POWER.kicad_sch
- SENSORS.kicad_sch
- MICRO_SD.kicad_sch

145 placed components were reviewed.

## Metadata added

Each purchasable component now carries, when applicable:
- Manufacturer
- MPN
- Package
- Datasheet
- DigiKey Part Number
- DigiKey URL
- DigiKey Specs
- DigiKey Unit Price EUR
- DigiKey Price Qty
- Price Checked
- DigiKey Status
- Footprint Audit
- Library Audit

## Main corrections

- Incorrect resistor MPN/value mappings were replaced by value-correct YAGEO RC0402-family parts.
- Logic-domain 100 nF capacitors were normalized to 16 V X7R parts.
- POWER-sheet 100 nF capacitors were normalized to 50 V X7R parts.
- 22 µF / 0805 power capacitors were normalized to active 25 V X5R metadata.
- CAN U3 metadata now matches the actual NXP TJA1051TK/3,118 device and records DigiKey Last-Time-Buy status.
- D5 metadata remains normalized to active 1N5819HW-7-F, 40 V / 1 A / SOD-123. D4 was subsequently upgraded to PMEG4030ER,115 (40 V / 3 A / SOD-123W).
- BMP581 uses project-local footprint alias H743_Custom:QFN10_BMP581_BOS.
- A project fp-lib-table was added for extralib/footprints.pretty.
- BMP581 symbol-library datasheet and footprint fields were corrected.
- BOM_DigiKey.csv was added to the repository.

## Remaining footprint / mechanical checks

### Blocking
- ANALOG_SENS J1: generic connector, no footprint.
- UART_I2C J2-J7: generic connectors, no footprints.
- SENSORS J8/J9: generic connectors, no footprints.

### Needs final land-pattern verification
- POWER U12 LMR43620R5RPER: current EasyEDA footprint name is 2.1 x 2.1 mm; compare pad geometry to TI RPE land pattern.
- MICRO_SD J10 TF-028-H265: compare EasyEDA footprint with HANBO mechanical drawing.
- BUZZER U10 ZX-SH1.0-3PWT: compare supplier drawing with EasyEDA footprint.
- MCU D1 RGB LED: compare supplier drawing with EasyEDA footprint.
- MCU JP1: footprint library `_pico` is not stored in this repository.
- Top-level H1-H4 mounting-hole footprints also reference the unresolved `_pico` library.
- MCU TP1-TP4 still have no PCB footprint assigned.
- MCU TP1-TP4: test-point symbols currently have no schematic footprint assigned.

## Price coverage

The unit-price field exists for all rows. Exact qty-1 prices were populated where they could be verified from DigiKey during this audit.

24 rows intentionally remain without a numeric price because an exact current DigiKey qty-1 price could not be independently verified:
- 3 x 220 ohm resistors RC0402FR-07220RL
- 18 x 200 ohm resistors RC0402FR-07200RL
- 1 x 12.4 kohm resistor RC0402FR-0712K4L
- 2 x Coilcraft XGL4020-222MEC inductors

No price was invented for these rows.

## Tool limitation

A full KiCad ERC/DRC was not run because kicad-cli is not installed in the execution environment.

## XGL4020 footprint correction

- L1 and L2 now use `H743_Custom:L_Coilcraft_XGL4020` (exact project-local XGL4020 land pattern).
- Land pattern follows Coilcraft XGL4020 Document 1529-3 (rev. 2026-02-19): pad size 0.98 x 3.40 mm, pad centers at +/-1.185 mm.
- Pad 1 is the marked/start terminal; in the current POWER schematic, L1.1 = SW_5V and L2.1 = SW_9V, which follows Coilcraft's recommendation to connect the high-dv/dt node to the start/short lead for lowest EMI.

## D4 5 V OR-ing diode update

- D4 changed from 1N5819HW-7-F (1 A) to **Nexperia PMEG4030ER,115**.
- Rating: 40 V, 3 A average forward current, Vf max 0.54 V @ 3 A.
- Package: **CFP3 / SOD-123W**; schematic footprint: `Diode_SMD:Nexperia_CFP3_SOD-123W`. This is not the same land pattern as SOD-123. The schematic is corrected; the current legacy PCB file still contains the old D4 SOD-123 footprint and must be synchronized before routing.
- DigiKey P/N: `1727-5313-1-ND`; qty-1 price recorded at 0.51 EUR on 2026-09-25.
- DigiKey CT reference for D4: **1727-5313-1-ND**; verified product page: PMEG4030ER,115 / 40 V / 3 A / SOD-123W.
- D5 remains 1N5819HW-7-F on the USB branch.
