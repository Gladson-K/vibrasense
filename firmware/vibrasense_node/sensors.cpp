#include "sensors.h"
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <OneWire.h>
#include <DallasTemperature.h>

static Adafruit_MPU6050 mpu;
static OneWire oneWire(PIN_ONEWIRE);
static DallasTemperature temps(&oneWire);
static hw_timer_t *sampler = nullptr;
static volatile int16_t ax, ay, az, adc_cur;
static volatile float accel_ring[FFT_SIZE];
static volatile uint16_t accel_head = 0;
static portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;

static void IRAM_ATTR on_sample() {
  portENTER_CRITICAL_ISR(&mux);
  mpu.getAcceleration(&ax, &ay, &az);
  adc_cur = analogRead(PIN_ADC_CURRENT);
  portEXIT_CRITICAL_ISR(&mux);
}

void sensors_init() {
  Wire.begin(PIN_SDA, PIN_SCL, 400000);
  mpu.begin(0x68, &Wire);
  mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
  mpu.setFilterBandwidth(MPU6050_BAND_260_HZ);
  oneWire.begin(PIN_ONEWIRE);
  temps.begin();
  analogSetAttenuation(ADC_11db);
  sampler = timerBegin(0, 80, true);
  timerAttachInterrupt(sampler, &on_sample, true);
  timerAlarmWrite(sampler, 1000000UL / SAMPLE_RATE_HZ, true);
  timerAlarmEnable(sampler);
}

void sensors_sample_isr_driven(FeatureWindow *w) {
  int16_t cx, cy, cz, cc;
  portENTER_CRITICAL(&mux);
  cx = ax; cy = ay; cz = az; cc = adc_cur;
  portEXIT_CRITICAL(&mux);
  float mag = sqrtf(cx*cx + cy*cy + cz*cz) / 2048.0f;
  float amps = (cc - 2048) * (3.3f / 4095.0f);
  welford_push(&w->vib, mag);
  welford_push(&w->cur, amps);
  portENTER_CRITICAL(&mux);
  accel_ring[accel_head] = mag;
  accel_head = (accel_head + 1) % FFT_SIZE;
  portEXIT_CRITICAL(&mux);
}

void sensors_read_temp(float *out) {
  temps.requestTemperatures();
  *out = temps.getTempCByIndex(0);
}

void sensors_raw_accel(int16_t *x, int16_t *y, int16_t *z) {
  portENTER_CRITICAL(&mux);
  *x = ax; *y = ay; *z = az;
  portEXIT_CRITICAL(&mux);
}

void accel_ring_copy(float *out, int n) {
  int count = n < FFT_SIZE ? n : FFT_SIZE;
  portENTER_CRITICAL(&mux);
  for (int i = 0; i < count; i++) {
    uint16_t idx = (accel_head - count + i + FFT_SIZE) % FFT_SIZE;
    out[i] = accel_ring[idx];
  }
  portEXIT_CRITICAL(&mux);
  for (int i = count; i < n; i++) out[i] = 0.0f;
}
