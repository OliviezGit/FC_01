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
- D4/D5 metadata was normalized to active 1N5819HW-7-F, 40 V / 1 A / SOD-123.
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
- POWER L1/L2 XGL4020-222MEC: schematic currently references an XAL4030-family KiCad footprint; exact XGL4020 land-pattern overlay is required.
- MICRO_SD J10 TF-028-H265: compare EasyEDA footprint with HANBO mechanical drawing.
- BUZZER U10 ZX-SH1.0-3PWT: compare supplier drawing with EasyEDA footprint.
- MCU D1 RGB LED: compare supplier drawing with EasyEDA footprint.
- MCU JP1: footprint library _pico is not stored in this repository.
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
