#include "ota.h"
#include <cstring>

bool ota_choose_boot_slot(bool slot_a_ok, bool slot_b_ok, char *out, size_t out_len) {
  if (!out || out_len < 2) return false;
  if (slot_b_ok && !slot_a_ok) {
    strlcpy(out, "B", out_len);
    return true;
  }
  if (slot_a_ok) {
    strlcpy(out, "A", out_len);
    return true;
  }
  out[0] = 0;
  return false;
}
