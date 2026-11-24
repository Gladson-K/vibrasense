#include "storage.h"
#include <SPIFFS.h>
#include <ArduinoJson.h>

static File ring;
static uint32_t head = 0;
static uint32_t count = 0;

void storage_init() {
  SPIFFS.begin(true);
  ring = SPIFFS.open(SPIFFS_RING_FILE, FILE_APPEND);
}

bool storage_push(const Telemetry *t) {
  StaticJsonDocument<192> doc;
  doc["rms_vel"] = t->rms_vel;
  doc["peak"] = t->peak;
  doc["crest"] = t->crest;
  doc["kurt"] = t->kurt;
  doc["cur_rms"] = t->cur_rms;
  doc["temp"] = t->temp_c;
  doc["flags"] = t->flags;
  char buf[192];
  size_t n = serializeJson(doc, buf);
  if (count >= RING_MAX_RECORDS) {
    ring.close();
    SPIFFS.remove(SPIFFS_RING_FILE);
    ring = SPIFFS.open(SPIFFS_RING_FILE, FILE_APPEND);
    count = 0;
    head = 0;
  }
  ring.write((uint8_t*)buf, n);
  ring.write('\n');
  count++;
  head = ring.position();
  return true;
}

bool storage_flush_to_mqtt(const NodeConfig &cfg, PublishFn fn) {
  File input = SPIFFS.open(SPIFFS_RING_FILE, FILE_READ);
  if (!input || input.size() == 0) {
    if (input) input.close();
    return true;
  }
  String remaining;
  uint32_t failed = 0;
  String topic = String("vs/") + cfg.node_id + "/telemetry";
  while (input.available()) {
    String line = input.readStringUntil('\n');
    line.trim();
    if (!line.length()) continue;
    if (!fn(topic.c_str(), line.c_str())) {
      remaining += line + "\n";
      failed++;
    }
  }
  input.close();
  if (failed == 0) {
    SPIFFS.remove(SPIFFS_RING_FILE);
    ring = SPIFFS.open(SPIFFS_RING_FILE, FILE_APPEND);
    count = 0;
    head = ring.position();
    return true;
  }
  File output = SPIFFS.open(SPIFFS_RING_FILE, FILE_WRITE);
  output.print(remaining);
  output.close();
  ring = SPIFFS.open(SPIFFS_RING_FILE, FILE_APPEND);
  count = failed;
  head = ring.position();
  return false;
}
