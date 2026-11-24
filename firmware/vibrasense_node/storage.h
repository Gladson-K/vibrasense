#pragma once
#include "config.h"
#include "dsp.h"
typedef bool (*PublishFn)(const char* topic, const char* payload);
void storage_init();
bool storage_push(const Telemetry*);
bool storage_flush_to_mqtt(const NodeConfig&, PublishFn);
