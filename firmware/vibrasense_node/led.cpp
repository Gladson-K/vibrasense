#include "led.h"
#include <Arduino.h>
void led_init() { pinMode(PIN_LED, OUTPUT); }
void led_heartbeat(bool ok) { digitalWrite(PIN_LED, ok ? HIGH : LOW); }
