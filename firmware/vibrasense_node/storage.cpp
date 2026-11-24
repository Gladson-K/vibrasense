#include "storage.h"
#include <SPIFFS.h>
#include <ArduinoJson.h>

static File ring; static uint32_t head = 0, count = 0;
void storage_init() {
  SPIFFS.begin(true);
  ring = SPIFFS.open(SPIFFS_RING_FILE, FILE_APPEND);
}
bool storage_push(const Telemetry *t) {
  StaticJsonDocument<192> doc;
  doc["rms_vel"]=t->rms_vel; doc["peak"]=t->peak; doc["crest"]=t->crest;
  doc["kurt"]=t->kurt; doc["cur_rms"]=t->cur_rms; doc["temp"]=t->temp_c; doc["flags"]=t->flags;
  char buf[192]; size_t n = serializeJson(doc, buf);
  if (count >= RING_MAX_RECORDS) { ring.close(); SPIFFS.remove(SPIFFS_RING_FILE); ring = SPIFFS.open(SPIFFS_RING_FILE, FILE_APPEND); count = 0; }
  ring.write((uint8_t*)buf, n); ring.write('\n');
  count++; head = ring.position();
  return true;
}
bool storage_flush_to_mqtt(const NodeConfig &cfg, PublishFn fn) { /* read lines, publish, truncate */ return true; }
