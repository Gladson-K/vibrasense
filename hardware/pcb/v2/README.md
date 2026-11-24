# v2 PCB design package status

The v2 hardware target is a two-layer ESP32 board with analog front end, power input, ESD protection, watchdog, and dual-bank firmware layout. This directory contains the reviewable design contract and acceptance inputs.

## Required design files before kit sales

- KiCad project with schematic and PCB.
- Netlist and bill of materials exported from the schematic.
- Gerber and drill files for rev A.
- Assembly drawings and test-point map.
- Per-unit manufacturing log export.

## Electrical contract

| Item | Requirement |
| --- | --- |
| MCU | ESP32-WROOM-32 module with exposed boot/reset |
| Vibration | MPU6050 I2C at 0x68 with 2.2 kΩ pull-up option |
| Temperature | DS18B20 1-Wire with 4.7 kΩ pull-up |
| Current input | SCT-013 burden, RC filter, 1.65 V bias, ADC GPIO36 |
| Power | 5 V SELV input, reverse polarity and ESD protection |
| Watchdog | TPS3823 supervisor with reset to ESP32 enable |
| Boot time | Less than 3 s from power good to telemetry loop |
| Brownout | No corrupt configuration on supply dip |

## OTA layout

- Two application slots: A and B.
- Manifest contains slot, version, image size, SHA-256, and signature.
- Bootloader selects the verified inactive slot after success.
- A failed verification or interrupted update rolls back to the known-good slot.
- Signing keys stay outside the repository and are supplied by environment variable.
- HMAC-SHA256 in the test harness is not a production field signing scheme; replace with asymmetric signatures before field OTA.

## Status

PCB geometry, Gerbers, and EMC pre-scan evidence are not present in this repository. Treat them as release blockers until a named hardware owner supplies and reviews the files.
