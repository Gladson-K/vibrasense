# v3 LoRaWAN variant

## Scope

Private-gateway LoRaWAN path for plants without Wi-Fi coverage.

## Packet contract

| Field | Type | Notes |
| --- | --- | --- |
| `node_id` | string | Same validation as MQTT node IDs |
| `fw` | string | Firmware version |
| `seq` | integer | Monotonic counter |
| `rms_vel` | float | Vibration RMS |
| `peak` | float | Peak acceleration in g |
| `cur_rms` | float | Current RMS |
| `temp` | float | Temperature in Celsius |
| `b1`–`b4` | float | Extended band energies |
| `flags` | integer | Self-test and quality flags |

## Controls

- No raw waveform is transmitted.
- Payload size stays within the selected LoRaWAN data rate limit.
- Gateway forwards packets to the same ingest schema as MQTT telemetry.
- Keys are provisioned locally and never committed.
- Range and coverage evidence must come from a plant survey.

## Status

Packet schema is documented here. Radio hardware, antenna tuning, and 500 m plant-range evidence remain release blockers.
