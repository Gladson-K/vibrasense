import os, sys, math
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml"))
from features import window_features, band_energies

def test_rms_of_sine():
    t = np.arange(1000) / 1000.0
    mag = 1.0 * np.sin(2*np.pi*5*t) + 1.0   # 5 Hz sine, 1 g offset, amplitude 1 g
    f = window_features(mag, np.zeros(1000), 40.0)
    assert abs(f["peak"] - 2.0) < 0.05
    assert abs(f["rms_vel"]) > 0
    assert 0.9 < f["crest"] < 1.7   # sine+DC crest is moderate

def test_kurtosis_gaussian_noise():
    rng = np.random.default_rng(7)
    mag = 1.0 + 0.1*rng.standard_normal(4000)
    f = window_features(mag, np.zeros(4000), 40.0)
    assert abs(f["kurt"] - 3.0) < 0.6   # Gaussian excess->kurtosis ~3

def test_kurtosis_spikes():
    rng = np.random.default_rng(7)
    mag = 1.0 + 0.1*rng.standard_normal(4000)
    mag[::200] += 3.0                   # impulse spikes -> high kurtosis
    f = window_features(mag, np.zeros(4000), 40.0)
    assert f["kurt"] > 8.0
