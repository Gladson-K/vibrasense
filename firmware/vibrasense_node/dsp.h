#pragma once
#include "config.h"
struct Welford { uint32_t n = 0; float mean = 0, M2 = 0, M3 = 0, M4 = 0, peak = 0, sum_sq = 0; };
struct FeatureWindow { Welford vib, cur; };
struct Telemetry { float rms_vel, peak, crest, kurt, cur_rms, temp_c; uint8_t flags; };
struct BandEnergies { float b1, b2, b3; };
void welford_push(Welford*, float); void welford_reset(Welford*);
void win_reset(FeatureWindow*);
Telemetry finalize_window(FeatureWindow*);
BandEnergies compute_bands(int n);
void accel_ring_copy(float*, int n);   // provided by sensors.cpp (ring of last 256 magnitudes)
