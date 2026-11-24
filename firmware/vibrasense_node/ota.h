#pragma once
#include <stddef.h>

bool ota_choose_boot_slot(bool slot_a_ok, bool slot_b_ok, char *out, size_t out_len);
