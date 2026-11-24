#include "net.h"
#include <WiFiManager.h>          // tzapu/WiFiManager
#include <PubSubClient.h>
#include <ArduinoJson.h>

static WiFiClient espClient;
static PubSubClient mqtt(espClient);
static WiFiManager wm;

void net_init(NodeConfig &cfg) {
  wm.setConfigPortalTimeout(180);
  if (!wm.autoConnect("VibraSense-Setup")) ESP.restart();
  mqtt.setServer(cfg.broker, cfg.broker_port);
}

void net_connect_mqtt(NodeConfig &cfg) {
  while (!mqtt.connected()) {
    String cid = String(cfg.node_id);
    if (mqtt.connect(cid.c_str(), (String("vs/") + cfg.node_id + "/status").c_str(),
                     1, true, "offline"))
      mqtt.publish((String("vs/") + cfg.node_id + "/status").c_str(), "online", true);
    else delay(2000);
  }
}

bool net_publish_telemetry(const NodeConfig &cfg, const Telemetry *t) {
  StaticJsonDocument<256> doc;
  doc["rms_vel"] = t->rms_vel; doc["peak"] = t->peak; doc["crest"] = t->crest;
  doc["kurt"] = t->kurt; doc["cur_rms"] = t->cur_rms; doc["temp"] = t->temp_c;
  doc["flags"] = t->flags;
  char buf[256]; size_t n = serializeJson(doc, buf);
  return mqtt.publish((String("vs/") + cfg.node_id + "/telemetry").c_str(), buf, n, MQTT_QOS);
}

void net_publish_hello(const NodeConfig &cfg, bool selftest_ok) {
  StaticJsonDocument<192> doc;
  doc["fw"] = FW_VERSION; doc["selftest"] = selftest_ok; doc["caps"] = "vib,cur,temp,fft";
  char buf[192]; size_t n = serializeJson(doc, buf);
  mqtt.publish("vs/hello", buf, n, true);
}

void net_publish_bands(const NodeConfig &cfg, const BandEnergies *b) {
  StaticJsonDocument<128> doc;
  doc["b1"] = b->b1; doc["b2"] = b->b2; doc["b3"] = b->b3;
  char buf[128]; size_t n = serializeJson(doc, buf);
  mqtt.publish((String("vs/") + cfg.node_id + "/bands").c_str(), buf, n, MQTT_QOS);
}

void net_loop() { if (!mqtt.connected()) { /* reconnect in-place */ } mqtt.loop(); }
