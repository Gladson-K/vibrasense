import numpy as np

FEATURES = ["rms_vel", "peak", "crest", "kurt", "cur_rms", "temp", "b1", "b2", "b3"]

def window_features(mag_g, amps, temp):
    # Compute the 9 core features from raw window arrays (mirrors on-node DSP).
    rms_a = float(np.sqrt(np.mean(mag_g**2)))
    peak = float(np.max(mag_g))
    crest = peak / rms_a if rms_a > 0 else 0.0
    kurt = float(np.mean((mag_g - mag_g.mean())**4) / (mag_g.std()**4 + 1e-12))
    rms_c = float(np.sqrt(np.mean(amps**2)))
    return {"rms_vel": rms_a * 9810 / (2*np.pi*60), "peak": peak, "crest": crest,
            "kurt": kurt, "cur_rms": rms_c, "temp": float(temp),
            "b1": 0.0, "b2": 0.0, "b3": 0.0}   # bands filled by FFT stage

def band_energies(mag_g, fs=1000.0, n=256):
    # Simple DFT band energies for bands 10-100, 100-300, 300-500 Hz.
    seg = mag_g[:n] - mag_g[:n].mean()
    b = [0.0, 0.0, 0.0]
    for k in range(1, n//2):
        re = np.sum(seg * np.cos(-2*np.pi*k*np.arange(n)/n))
        im = np.sum(seg * np.sin(-2*np.pi*k*np.arange(n)/n))
        p = (re*re + im*im) / (n*n)
        hz = k * fs / n
        if 10 <= hz < 100: b[0] += p
        elif hz < 300: b[1] += p
        elif hz < 500: b[2] += p
    return b
