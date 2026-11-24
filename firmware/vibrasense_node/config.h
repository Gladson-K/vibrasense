// VibraSense Node v1 — configuration
#pragma once
#define FW_VERSION "1.0.0"
#define NODE_NAME_MAX 32

// Pins
#define PIN_SDA 21
#define PIN_SCL 22
#define PIN_ONEWIRE 4
#define PIN_ADC_CURRENT 36
#define PIN_LED 2

// Sampling
#define SAMPLE_RATE_HZ 1000
#define WINDOW_SEC 10
#define FFT_SIZE 256
#define TEMP_PERIOD_SEC 30

// MQTT / net
#define MQTT_PORT 1883
#define MQTT_QOS 1
#define TELEMETRY_TOPIC "vs/%s/telemetry"
#define STATUS_TOPIC "vs/%s/status"
#define CONFIG_TOPIC "vs/%s/config"

// Storage
#define SPIFFS_RING_FILE "/ring.bin"
#define RING_MAX_RECORDS 9000   // ~24h @10s

// Alarms (defaults; per-node configurable via MQTT config)
#define Z_ALERT 4.0
#define Z_WATCH 2.5
#define ALARM_CONSEC_WINDOWS 3
#define MULTI_FEATURE_VOTE 3

struct NodeConfig {
  char node_id[NODE_NAME_MAX] = "vs-node-0001";
  char broker[64] = "";
  uint16_t broker_port = MQTT_PORT;
  float current_cal = 30.0;    // SCT-013-030: full-scale amps at 1.0 Vrms
  float z_alert = Z_ALERT;
  float z_watch = Z_WATCH;
};
