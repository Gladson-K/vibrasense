// VibraSense Node v1.0.0 — main orchestration
#include "config.h"
#include "sensors.h"
#include "dsp.h"
#include "net.h"
#include "storage.h"
#include "selftest.h"
#include "led.h"

static NodeConfig cfg;
static FeatureWindow win;
static uint32_t last_telemetry = 0, last_fft = 0, last_temp = 0;

void setup() {
  Serial.begin(115200);
  Serial.printf("VibraSense %s boot\n", FW_VERSION);
  led_init();
  sensors_init();
  storage_init();
  bool ok = run_selftest();
  net_init(cfg);           // WiFiManager captive portal if unprovisioned
  net_connect_mqtt(cfg);
  net_publish_hello(cfg, ok);
}

void loop() {
  sensors_sample_isr_driven(&win);          // 1 kHz accel + current, Welford stats
  net_loop();

  uint32_t now = millis();
  if (now - last_telemetry >= WINDOW_SEC * 1000UL) {
    last_telemetry = now;
    Telemetry t = finalize_window(&win);
    sensors_read_temp(&t.temp_c);
    t.flags = 0;
    if (!net_publish_telemetry(cfg, &t))   // QoS1; on failure:
      storage_push(&t);                    // buffer locally
    led_heartbeat(ok_recently());
    win_reset(&win);
  }
  if (now - last_fft >= 60000UL) {          // 60 s FFT pass
    last_fft = now;
    BandEnergies b = compute_bands(FFT_SIZE);
    net_publish_bands(cfg, &b);
  }
  if (now - last_temp >= TEMP_PERIOD_SEC * 1000UL) { last_temp = now; /* temp read in telemetry */ }
}
