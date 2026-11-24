# VibraSense Kit — Assembly & Deployment Quickstart (v1)

## Assembly (~20 min, soldering iron + multimeter required)

1. Solder ESP32 module to perfboard; add 100 nF + 10 µF decoupling near 3V3 pin.
2. Wire I2C: GPIO21→SDA, GPIO22→SCL to GY-521 (add 2.2k pull-ups if module lacks them).
3. Wire 1-Wire: GPIO4→DS18B20 data, 4.7k pull-up to 3V3.
4. Build analog front end: SCT-013 → 33 Ω burden → 1.6k/100nF RC → bias 1.65 V (100k/100k) → GPIO36.
5. Fit in enclosure; mount magnet plate with Sorbothane pad; route glands; label with node ID.
6. Power on: LED blinks 3× then steady = self-test pass.

## Calibration

- Current: clamp one conductor of a known load (e.g., 500 W heater ≈ 2.17 A @ 230 V); update `current_cal` via MQTT config message; verify `cur_rms` within ±3%.
- Vibration: at rest, `peak` should be ≈ 1.0–1.2 g (gravity + noise).

## Deployment

1. Node boots into AP "VibraSense-Setup" → phone portal → enter plant Wi-Fi + broker IP.
2. Mount node on machine housing (magnet base on clean flat surface, near bearing).
3. Clamp CT on one motor phase inside panel (qualified personnel).
4. Attach DS18B20 probe on bearing housing with thermal paste + hose clamp.
5. Dashboard at `http://127.0.0.1:5000` when run locally — node appears within seconds; status "learning" for first ~20 min, then WATCH/ALARM logic is active.
6. After 3+ days of healthy running: POST `/api/models/retrain` to enable the autoencoder.

## Safety

- Mains work only by qualified personnel; CT is non-invasive but panel rules apply.
- 5 V SELV only inside node enclosure.
- Alarms are advisory decision support, not certified safety functions.
- See `SECURITY.md` and `AI-USE.md` for controls and claim boundaries.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| No Wi-Fi AP | Flash firmware; check 3V3 rail |
| selftest fail | MPU6050 wiring/I2C address (0x68) |
| cur_rms stuck at 0 | clamp on BOTH conductors cancels → clamp ONE conductor only |
| Alarms immediately | Mounting loose / learning period too short — wait 20 min, check magnet seating |
