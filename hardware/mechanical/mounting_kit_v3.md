# v3 high-frequency sensing artefacts

## Implemented analysis path

- `ml/high_freq.py` provides Hilbert envelope analysis via FFT, extended band energies to 10 kHz, bearing-frequency calculators, and envelope peak matching.
- The dashboard exposes bearing-frequency calculation through `/api/bearing-frequencies`.
- v1 1 kHz sensing remains the compatibility path.

## Sensor variant

| Item | Requirement |
| --- | --- |
| Accelerometer | IIM-42652 or equivalent industrial MEMS on SPI |
| Sample rate | 8–32 kHz configurable |
| Analysis band | Up to 10 kHz |
| Mounting | Stud mount preferred; adhesive mount qualified; magnet correction profile required |
| Gateway variant | LoRaWAN node with private gateway and packet schema |

## Firmware constants

`HF_SAMPLE_RATE_HZ`, `HF_FFT_SIZE`, and `HF_MAX_HZ` are reserved in `config.h`. The high-rate acquisition driver and on-device envelope implementation remain hardware-dependent and must be reviewed before field use.

## Physical evidence still required

- Inner-race fault detected at least 2× earlier than v1 on the rig.
- LoRa range at least 500 m in the target plant.
- Mounting resonance correction validated for magnet and adhesive mounts.
