#include "net.h"
#include <WiFiManager.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <cstring>

static WiFiClient espClient;
static PubSubClient mqtt(espClient);
static WiFiManager wm;
static NodeConfig* active_cfg = nullptr;

static bool valid_cfg_node(const char* value) {
  if (!value || !*value) return false;
  size_t n = strlen(value);
  if (n > NODE_NAME_MAX - 1) return false;
  for (size_t i = 0; i < n; i++) {
    char c = value[i];
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
          (c >= '0' && c <= '9') || c == '.' || c == '_' || c == '-')) return false;
  }
  return true;
}

static void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  if (!active_cfg) return;
  char buf[192];
  size_t n = length < sizeof(buf) - 1 ? length : sizeof(buf) - 1;
  memcpy(buf, payload, n);
  buf[n] = 0;
  StaticJsonDocument<192> doc;
  if (deserializeJson(doc, buf, n)) return;
  String expected = String("vs/") + active_cfg->node_id + "/config";
  if (strcmp(topic, expected.c_str()) != 0) return;
  if (doc.containsKey("node_id")) {
    const char* value = doc["node_id"];
    if (valid_cfg_node(value)) strlcpy(active_cfg->node_id, value, NODE_NAME_MAX);
  }
  if (doc.containsKey("current_cal")) active_cfg->current_cal = doc["current_cal"] | active_cfg->current_cal;
  if (doc.containsKey("z_alert")) active_cfg->z_alert = doc["z_alert"] | active_cfg->z_alert;
  if (doc.containsKey("z_watch")) active_cfg->z_watch = doc["z_watch"] | active_cfg->z_watch;
}

void net_init(NodeConfig &cfg) {
  active_cfg = &cfg;
  wm.setConfigPortalTimeout(180);
  if (!wm.autoConnect("VibraSense-Setup")) ESP.restart();
  mqtt.setServer(cfg.broker, cfg.broker_port);
  mqtt.setCallback(mqtt_callback);
}

bool net_connect_mqtt(NodeConfig &cfg) {
  active_cfg = &cfg;
  if (mqtt.connected()) return true;
  String cid = String(cfg.node_id);
  String status = String("vs/") + cfg.node_id + "/status";
  for (int attempt = 0; attempt < MAX_CONNECT_ATTEMPTS; attempt++) {
    if (mqtt.connect(cid.c_str(), nullptr, nullptr, status.c_str(), 1, true, "offline")) {
      mqtt.publish(status.c_str(), "online", true);
      mqtt.subscribe((String("vs/") + cfg.node_id + "/config").c_str(), 1);
      return true;
    }
    delay(MQTT_RETRY_MS);
  }
  return false;
}

bool net_publish_telemetry(const NodeConfig &cfg, const Telemetry *t) {
  StaticJsonDocument<256> doc;
  doc["rms_vel"] = t->rms_vel;
  doc["peak"] = t->peak;
  doc["crest"] = t->crest;
  doc["kurt"] = t->kurt;
  doc["cur_rms"] = t->cur_rms;
  doc["temp"] = t->temp_c;
  doc["flags"] = t->flags;
  char buf[256];
  size_t n = serializeJson(doc, buf);
  return mqtt.publish((String("vs/") + cfg.node_id + "/telemetry").c_str(), buf, n, MQTT_QOS);
}

void net_publish_hello(const NodeConfig &cfg, bool selftest_ok) {
  StaticJsonDocument<192> doc;
  doc["fw"] = FW_VERSION;
  doc["selftest"] = selftest_ok;
  doc["caps"] = "vib,cur,temp,fft";
  char buf[192];
  size_t n = serializeJson(doc, buf);
  mqtt.publish("vs/hello", buf, n, true);
}

void net_publish_bands(const NodeConfig &cfg, const BandEnergies *b) {
  StaticJsonDocument<128> doc;
  doc["b1"] = b->b1;
  doc["b2"] = b->b2;
  doc["b3"] = b->b3;
  char buf[128];
  size_t n = serializeJson(doc, buf);
  mqtt.publish((String("vs/") + cfg.node_id + "/bands").c_str(), buf, n, MQTT_QOS);
}

bool net_publish_raw(const char* topic, const char* payload) {
  return mqtt.publish(topic, payload, MQTT_QOS);
}

void net_loop(NodeConfig &cfg) {
  if (!mqtt.connected()) net_connect_mqtt(cfg);
  mqtt.loop();
}
