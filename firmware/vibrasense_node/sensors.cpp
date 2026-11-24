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
static portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;

// Timer ISR @1 kHz: burst-read accel, sample ADC (current)
static void IRAM_ATTR on_sample() {
  portENTER_CRITICAL_ISR(&mux);
  mpu.getAcceleration(&ax, &ay, &az);            // I2C burst (~250 µs)
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
  sampler = timerBegin(0, 80, true);             // 80 MHz / 80 = 1 MHz tick
  timerAttachInterrupt(sampler, &on_sample, true);
  timerAlarmWrite(sampler, 1000, true);          // 1000 ticks = 1 kHz
  timerAlarmEnable(sampler);
}

void sensors_sample_isr_driven(FeatureWindow *w) {
  static int16_t pax, pay, paz, pcur; static bool have = false;
  int16_t cx, cy, cz, cc;
  portENTER_CRITICAL(&mux);
  cx = ax; cy = ay; cz = az; cc = adc_cur;
  portEXIT_CRITICAL(&mux);
  if (have) {
    float mag = sqrtf(cx*cx + cy*cy + cz*cz) / 2048.0f;      // LSB->g (±16g, 2048 LSB/g)
    float amps = (cc - 2048) * (3.3f / 4095.0f) / 1.0f;      // volts across burden ~ calibrated
    welford_push(&w->vib, mag);
    welford_push(&w->cur, amps);
    (void)pax;(void)pay;(void)paz;(void)pcur;
  }
  pax = cx; pay = cy; paz = cz; pcur = cc; have = true;
}

void sensors_read_temp(float *out) {
  temps.requestTemperatures();
  *out = temps.getTempCByIndex(0);
}
