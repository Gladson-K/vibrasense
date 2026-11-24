#pragma once
#include "config.h"
#include "dsp.h"

void net_init(NodeConfig&);
bool net_connect_mqtt(NodeConfig&);
bool net_publish_telemetry(const NodeConfig&, const Telemetry*);
void net_publish_hello(const NodeConfig&, bool selftest_ok);
void net_publish_bands(const NodeConfig&, const BandEnergies*);
bool net_publish_raw(const char* topic, const char* payload);
void net_loop(NodeConfig&);
