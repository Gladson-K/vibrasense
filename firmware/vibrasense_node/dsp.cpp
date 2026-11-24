#include "dsp.h"
#include "sensors.h"
#include <Arduino.h>
#include <math.h>

void welford_push(Welford *w, float x) {
  w->n++;
  float d = x - w->mean;
  w->mean += d / w->n;
  w->M2 += d * (x - w->mean);
  float d3 = x - w->mean;
  w->M3 += d * d * d3;
  w->M4 += d * d * d3 * d3;
  if (x > w->peak) w->peak = x;
  w->sum_sq += x * x;
}

void welford_reset(Welford *w) { *w = Welford{}; }

void win_reset(FeatureWindow *w) { welford_reset(&w->vib); welford_reset(&w->cur); }

static float rms_from(const Welford *w) {
  return w->n ? sqrtf(w->sum_sq / w->n) : 0.0f;
}

Telemetry finalize_window(FeatureWindow *w) {
  Telemetry t{};
  float rms = rms_from(&w->vib);
  t.rms_vel = rms * 9810.0f / (2 * M_PI * 60.0f);
  t.peak = w->vib.peak;
  t.crest = rms > 0 ? t.peak / rms : 0;
  float var = w->vib.n > 1 ? w->vib.M2 / (w->vib.n - 1) : 0;
  t.kurt = var > 0 ? (w->vib.n * w->vib.M4 / (w->vib.M2 * w->vib.M2)) : 0;
  t.cur_rms = rms_from(&w->cur);
  return t;
}

BandEnergies compute_bands(int n) {
  BandEnergies b{0,0,0};
  static float buf[FFT_SIZE];
  accel_ring_copy(buf, n);
  for (int k = 1; k < n/2; k++) {
    float re = 0, im = 0, hz = (float)k * SAMPLE_RATE_HZ / n;
    for (int i = 0; i < n; i++) {
      float a = -2 * M_PI * k * i / n;
      re += buf[i] * cosf(a);
      im += buf[i] * sinf(a);
    }
    float p = (re*re + im*im) / (n*n);
    if (hz >= 10 && hz < 100) b.b1 += p;
    else if (hz < 300) b.b2 += p;
    else if (hz < 500) b.b3 += p;
  }
  return b;
}
