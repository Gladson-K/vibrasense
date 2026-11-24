#include "config.h"
#include "sensors.h"
#include "dsp.h"
#include "net.h"
#include "storage.h"
#include "selftest.h"
#include "led.h"

static NodeConfig cfg;
static FeatureWindow win;
static uint32_t last_telemetry = 0;
static uint32_t last_fft = 0;
static uint32_t last_temp = 0;
static uint32_t last_selftest_ok = 0;
static float current_temp_c = 0.0f;

static bool publish_buffered(const char* topic, const char* payload) {
  return net_publish_raw(topic, payload);
}

void setup() {
  Serial.begin(115200);
  Serial.printf("VibraSense %s boot\n", FW_VERSION);
  led_init();
  sensors_init();
  storage_init();
  bool ok = run_selftest();
  if (ok) last_selftest_ok = millis();
  net_init(cfg);
  net_connect_mqtt(cfg);
  net_publish_hello(cfg, ok);
}

void loop() {
  net_loop(cfg);
  sensors_sample_isr_driven(&win);
  uint32_t now = millis();
  if (now - last_temp >= TEMP_PERIOD_SEC * 1000UL) {
    last_temp = now;
    sensors_read_temp(&current_temp_c);
  }
  if (now - last_telemetry >= WINDOW_SEC * 1000UL) {
    last_telemetry = now;
    Telemetry t = finalize_window(&win);
    t.temp_c = current_temp_c;
    t.flags = (now - last_selftest_ok <= SELFTEST_OK_WINDOW_MS) ? 0 : 1;
    if (!net_publish_telemetry(cfg, &t)) storage_push(&t);
    led_heartbeat(now - last_selftest_ok <= SELFTEST_OK_WINDOW_MS);
    win_reset(&win);
    storage_flush_to_mqtt(cfg, publish_buffered);
  }
  if (now - last_fft >= 60000UL) {
    last_fft = now;
    BandEnergies b = compute_bands(FFT_SIZE);
    net_publish_bands(cfg, &b);
  }
}
