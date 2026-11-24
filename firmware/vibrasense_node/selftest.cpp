#include "selftest.h"
#include "sensors.h"
bool run_selftest() {
  // gravity vector check: |mag| ≈ 1g after 1s settle
  delay(1000);
  int16_t x, y, z; sensors_raw_accel(&x, &y, &z);
  float mag = sqrtf(x*x + y*y + z*z) / 2048.0f;
  return fabsf(mag - 1.0f) < 0.05f;   // ±5%
}
