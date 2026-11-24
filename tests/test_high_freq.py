import numpy as np
import pytest
from high_freq import (
    bearing_frequencies,
    detect_defect_frequency,
    envelope,
    envelope_peaks,
    extended_band_energies,
)


def test_bearing_frequencies_known_geometry():
    values = bearing_frequencies(1200, 8, 40, 9, 0)
    assert values == pytest.approx({"bpfo": 72.0, "bpfi": 108.0, "bsf": 48.0, "ftf": 8.0})


def test_bearing_frequency_validation():
    with pytest.raises(ValueError):
        bearing_frequencies(0, 8, 40, 9)


def test_envelope_detects_amplitude_modulation():
    fs = 32000
    t = np.arange(fs) / fs
    carrier_hz = 2000.0
    defect_hz = 90.0
    samples = (1.0 + 0.6 * np.sin(2 * np.pi * defect_hz * t)) * np.sin(2 * np.pi * carrier_hz * t)
    peaks = envelope_peaks(envelope(samples), fs=fs, min_hz=20.0, max_hz=300.0, top_n=8)
    assert any(abs(item["hz"] - defect_hz) < 3.0 for item in peaks)
    matches = detect_defect_frequency(envelope(samples), fs=fs, targets=[defect_hz], tolerance_hz=3.0)
    assert matches


def test_extended_bands_locates_tone():
    fs = 32000
    t = np.arange(fs) / fs
    samples = 0.5 * np.sin(2 * np.pi * 3000.0 * t)
    bands = extended_band_energies(samples, fs=fs)
    assert bands["1000-5000"] > bands["10-100"]
    assert bands["1000-5000"] > bands["5000-10000"]
