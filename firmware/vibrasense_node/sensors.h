#pragma once
#include <stdint.h>
#include "config.h"
#include "dsp.h"

void sensors_init();
void sensors_sample_isr_driven(FeatureWindow *w);
void sensors_read_temp(float *out);
void sensors_raw_accel(int16_t *x, int16_t *y, int16_t *z);
void accel_ring_copy(float *out, int n);
