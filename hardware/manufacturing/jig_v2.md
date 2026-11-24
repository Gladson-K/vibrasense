# v2 manufacturing test jig

## Purpose

Automated per-unit test for the first 100-unit pilot batch.

## Fixture

- Pogo-pin bed for 5 V, GND, UART, boot, reset, I2C, 1-Wire, and ADC test points.
- Isolated programmable load for current-channel injection.
- Signal generator for vibration-equivalent ADC stimulus.
- Temperature simulator or fixed resistor substitution.
- USB serial capture for boot time and self-test logs.

## Test sequence

1. Apply 5 V SELV power and verify current below limit.
2. Read firmware version and node ID.
3. Verify watchdog reset path.
4. Inject known ADC waveform and verify `cur_rms` within ±3%.
5. Inject I2C self-test response and verify LED/status output.
6. Verify DS18B20 channel with simulator.
7. Force MQTT publish failure and verify SPIFFS buffering.
8. Force OTA manifest verification failure and verify rollback selection.
9. Measure boot time and record result.
10. Write per-unit log to the manufacturing database with serial, date, operator, and pass/fail.

## Acceptance

- Boot time below 3 s.
- No false self-test failures.
- Current accuracy within ±3%.
- Fewer than 2% dead-on-arrival units in the 100-unit pilot.
- No test logs containing personal data or plant telemetry.
