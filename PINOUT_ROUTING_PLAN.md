# H743_Ardupilot — Pinout lock and PCB routing plan

Validated: 2026-09-25

## Reference sources

1. ArduPilot Copter 4.7.1:
   `libraries/AP_HAL_ChibiOS/hwdef/MatekH743/hwdef.dat`
   tag: `Copter-4.7.1`
2. Matek H743-SLIM V4 official hardware page.
3. STM32H743VIT6 alternate-function mapping.

Goal: keep the custom FC as close as practical to the official `MatekH743` target while reserving only deliberate custom additions for the new IMUs.

## Locked MCU mapping

| Function | STM32H743 pin | Status | Routing intent |
|---|---|---|---|
| SPI1 SCK | PA5 | LOCKED | ICM-45686 |
| SPI1 MISO | PA6 | LOCKED | ICM-45686 |
| SPI1 MOSI | PD7 | LOCKED | ICM-45686; PA7 must NOT share this net |
| SPI1 CS | PC15 | LOCKED | ICM-45686 |
| SPI4 CS | PE11 | LOCKED | LSM6DSV16X |
| SPI4 SCK | PE12 | LOCKED | LSM6DSV16X |
| SPI4 MISO | PE13 | LOCKED | LSM6DSV16X |
| SPI4 MOSI | PE14 | LOCKED | LSM6DSV16X |
| SPI3 SCK | PB3 | LOCKED | BMI088 |
| SPI3 MISO | PB4 | LOCKED | BMI088 |
| SPI3 MOSI | PB5 | LOCKED | BMI088 |
| BMI088 accel CS | PD4 | LOCKED | custom use, also matches Matek EXT_CS1 resource |
| BMI088 gyro CS | PE2 | LOCKED | custom use, also matches Matek EXT_CS2 resource |
| SPI2 CS | PB12 | LOCKED | BMP581 |
| SPI2 SCK | PB13 | LOCKED | BMP581 |
| SPI2 MISO | PB14 | LOCKED | BMP581 |
| SPI2 MOSI | PB15 | LOCKED | BMP581 |
| I2C1 SCL | PB6 | LOCKED | external I2C |
| I2C1 SDA | PB7 | LOCKED | external I2C |
| I2C2 SCL | PB10 | LOCKED | barometer / second I2C |
| I2C2 SDA | PB11 | LOCKED | barometer / second I2C |
| CAN1 RX | PD0 | LOCKED | TJA1051 |
| CAN1 TX | PD1 | LOCKED | TJA1051 |
| CAN silent | PD3 | LOCKED | TJA1051 S |
| USB FS DM | PA11 | LOCKED | USB-C right side |
| USB FS DP | PA12 | LOCKED | USB-C right side |
| SD D0 | PC8 | LOCKED | microSD |
| SD D1 | PC9 | LOCKED | microSD |
| SD D2 | PC10 | LOCKED | microSD |
| SD D3 | PC11 | LOCKED | microSD |
| SD CLK | PC12 | LOCKED | microSD |
| SD CMD | PD2 | LOCKED | microSD |
| MOTOR1 | PB0 | LOCKED | ESC |
| MOTOR2 | PB1 | LOCKED | ESC |
| MOTOR3 | PA0 | LOCKED | ESC |
| MOTOR4 | PA1 | LOCKED | ESC |
| Buzzer | PA15 | LOCKED | buzzer transistor |
| LED0 | PE3 | LOCKED | status LED |
| LED1 | PE4 | LOCKED | status LED |
| LED strip | PA8 | LOCKED | WS2812 / output |
| ADC VBAT1 | PC0 | LOCKED | battery voltage |
| ADC CURR1 | PC1 | LOCKED | battery current |
| ADC VBAT2 | PA4 | LOCKED | second voltage |
| ADC Airspeed | PC4 | LOCKED | analog airspeed |
| ADC CURR2 | PA7 | RESERVED | Matek-compatible second current input; intentionally free in current schematic |
| ADC RSSI | PC5 | RESERVED | Matek-compatible analog RSSI; intentionally free in current schematic |
| IMU1 CLKIN | PD14 | CUSTOM LOCKED | ICM-45686 clock input |
| IMU1 DRDY | PE15 | CUSTOM LOCKED | ICM-45686 interrupt/data-ready |
| IMU2 DRDY | PB2 | CUSTOM LOCKED | reserved for second IMU DRDY |

`IMU2_CLKIN` is intentionally removed. PD15 is therefore free again.

## Routing / placement zones

### MCU center

Place STM32H743 near the geometric center of the board. Keep the crystal, VCAP capacitors, VREF/VDDA filtering and MCU decoupling immediately around it.

### Left-of-MCU sensor zone

Place the LSM6DSV16X close to PE11/PE12/PE13/PE14. Those four SPI4 signals are contiguous on the MCU package and are the cleanest sensor bus for direct short routing.

Keep the IMU away from:
- 5 V and 9 V buck inductors;
- switch nodes;
- USB connector mechanical stress;
- mounting-hole load paths.

### Right/lower MCU sensor zone

SPI2 PB12/PB13/PB14/PB15 is contiguous. Prefer BMP581 near that MCU side, but keep the pressure port away from propwash paths, board-edge turbulence and hot regulators.

I2C1 PB6/PB7 and I2C2 PB10/PB11 are also grouped on the same MCU side. Route both buses as short parallel pairs without unnecessary vias. Keep the DPS368 / barometer branch short.

### ICM-45686

SPI1 follows the Matek mapping and is less geometrically compact because MOSI is PD7 while SCK/MISO are PA5/PA6 and CS is PC15. Do not change the pin assignment merely for PCB convenience: preserve ArduPilot/Matek compatibility.

Use direct routing with as few vias as practical and keep all four SPI1 traces away from buck SW nodes.

### BMI088

Keep accel and gyro CS independent. Route PB3/PB4/PB5 as a compact SPI3 group. Avoid routing high-current or switching-power traces beneath the sensor.

### USB-C

USB is required on the right side. PA11/PA12 are already well suited. Route D+/D- as a short differential pair, avoid stubs after the ESD protector and keep a continuous ground reference underneath.

### microSD

Keep SDMMC CLK especially short and isolated from IMU clock/data lines. CMD and D0-D3 should run as a compact bus. Final series damping on CLK can be decided after placement/length review.

### CAN

PD0/PD1/PD3 are grouped. Place the transceiver close to the external CAN connector. CANH/CANL should leave the transceiver as a differential pair and reach the TVS before the connector with minimal stub length.

### Power zoning

Keep the 5 V and 9 V switch-mode power section together on one board edge and physically separated from the IMU/barometer zone.

Priority:
1. minimize VIN/SW/inductor/output-cap high-di/dt loops;
2. keep SW copper compact;
3. keep an uninterrupted ground reference under digital buses;
4. do not route SPI/clock lines through the buck power zone;
5. place 3V3_MCU and 3V3_SENS LDOs near the loads they serve, downstream of the noisy buck section.

## Changes applied on 2026-09-25

- removed the incorrect PA7 -> SPI1.MOSI connection;
- SPI1 MOSI now remains only on PD7;
- connected SPI4 to PE11/PE12/PE13/PE14;
- connected I2C1 to PB6/PB7;
- connected I2C2 to PB10/PB11;
- removed obsolete IMU2_CLKIN / PD15 assignment;
- corrected top-level hierarchy so SENSORS.IMU1_DRDY reaches MCU.IMU1_DRDY and SENSORS.IMU1_CLKIN reaches MCU.IMU1_CLKIN;
- corrected SPI/I2C hierarchy directions to bidirectional.

## Do not change without re-validating hwdef

The entries marked **LOCKED** should not be reassigned only to simplify PCB routing. Any change requires simultaneous update and validation of the ArduPilot `hwdef.dat`.
