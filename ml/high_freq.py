import numpy as np

DEFAULT_FS = 32000.0
EXTENDED_BANDS = ((10.0, 100.0), (100.0, 1000.0), (1000.0, 5000.0), (5000.0, 10000.0))


def analytic_signal(samples):
    x = np.asarray(samples, dtype=float)
    n = x.size
    if n == 0:
        return x
    spectrum = np.fft.rfft(x)
    h = np.zeros(spectrum.shape, dtype=float)
    h[0] = 1.0
    if n % 2 == 0:
        if n // 2 < h.size:
            h[1:n // 2] = 2.0
            h[n // 2] = 1.0
    else:
        h[1:] = 2.0
    return np.fft.irfft(spectrum * h, n)


def envelope(samples):
    return np.abs(analytic_signal(samples))


def extended_band_energies(samples, fs=DEFAULT_FS, bands=EXTENDED_BANDS):
    x = np.asarray(samples, dtype=float)
    if x.size == 0:
        return {}
    centered = x - np.mean(x)
    spectrum = np.fft.rfft(centered)
    freqs = np.fft.rfftfreq(x.size, 1.0 / fs)
    power = np.abs(spectrum) ** 2 / (x.size * x.size)
    return {
        "%g-%g" % (low, high): float(np.sum(power[(freqs >= low) & (freqs < high)]))
        for low, high in bands
    }


def bearing_frequencies(rpm, ball_dia_mm, pitch_dia_mm, balls, contact_angle_deg=0.0):
    if rpm <= 0 or ball_dia_mm <= 0 or pitch_dia_mm <= 0 or balls <= 0:
        raise ValueError("bearing inputs must be positive")
    if ball_dia_mm > pitch_dia_mm:
        raise ValueError("ball diameter cannot exceed pitch diameter")
    angle = np.deg2rad(contact_angle_deg)
    ratio = (ball_dia_mm / pitch_dia_mm) * np.cos(angle)
    if ratio >= 1:
        raise ValueError("invalid bearing geometry")
    shaft_hz = rpm / 60.0
    return {
        "bpfo": round(shaft_hz * balls * (1.0 - ratio) / 2.0, 4),
        "bpfi": round(shaft_hz * balls * (1.0 + ratio) / 2.0, 4),
        "bsf": round(shaft_hz * pitch_dia_mm * (1.0 - ratio ** 2) / (2.0 * ball_dia_mm), 4),
        "ftf": round(shaft_hz * (1.0 - ratio) / 2.0, 4),
    }


def envelope_peaks(env_samples, fs=DEFAULT_FS, min_hz=10.0, max_hz=1000.0, top_n=10):
    y = np.asarray(env_samples, dtype=float)
    if y.size == 0:
        return []
    centered = y - np.mean(y)
    window = np.hanning(y.size)
    spectrum = np.fft.rfft(centered * window)
    freqs = np.fft.rfftfreq(y.size, 1.0 / fs)
    power = np.abs(spectrum) ** 2 / (y.size * y.size)
    candidates = np.argsort(power)[::-1]
    peaks = []
    for index in candidates:
        hz = float(freqs[index])
        if hz < min_hz or hz >= max_hz:
            continue
        if any(abs(hz - item["hz"]) < 3.0 for item in peaks):
            continue
        peaks.append({"hz": round(hz, 3), "magnitude": float(power[index])})
        if len(peaks) >= top_n:
            break
    return peaks


def detect_defect_frequency(env_samples, fs=DEFAULT_FS, targets=(), tolerance_hz=2.0):
    peaks = envelope_peaks(env_samples, fs=fs, top_n=25)
    matches = []
    for target in targets:
        for peak in peaks:
            if abs(peak["hz"] - target) <= tolerance_hz:
                matches.append({"target_hz": target, "peak": peak})
                break
    return matches
