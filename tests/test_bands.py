import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml"))
from features import band_energies

def test_tone_in_band2():
    t = np.arange(1000) / 1000.0
    mag = 0.05*np.sin(2*np.pi*150*t) + 1.0   # 150 Hz tone -> band 2 (100-300 Hz)
    b = band_energies(mag)
    assert b[1] > b[0] and b[1] > b[2]

def test_tone_in_band1():
    t = np.arange(1000) / 1000.0
    mag = 0.05*np.sin(2*np.pi*50*t) + 1.0    # 50 Hz -> band 1
    b = band_energies(mag)
    assert b[0] > b[1] and b[0] > b[2]
