"""
acquisition.py
==============
Hardware-triggered data acquisition for the Parker flash method experiment.

A flash gun fires a light pulse at the front face of a stainless steel plate.
A phototransistor detects the flash and triggers data acquisition automatically.
The thermopile signal on the rear face is captured and the half-time t½ is
extracted — the time at which the temperature reaches 50% of its maximum rise.

Acquisition is pre-triggered: 200 samples are buffered before the trigger
event so the full rising edge of the thermopile signal is captured.

Authors: Miguel PJ Arias — University of Nottingham, Dec 2022
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.insert(1, "C:\\python")
import y2daq

# ---------------------------------------------------------------------------
# ACQUISITION PARAMETERS
# ---------------------------------------------------------------------------

SAMPLE_RATE = 10_000        # Hz — 10 kHz gives 0.1 ms time resolution
N_SAMPLES = 4000            # Total samples to capture after trigger
PRE_TRIGGER = 200           # Samples to buffer before the trigger event
TRIM_OFFSET = 100           # Extra samples to skip after trigger (removes photodiode spike)

# Smoothing window — N=1 means no smoothing; increase for noisy data
SMOOTHING_N = 1

# ---------------------------------------------------------------------------
# DAQ CONFIGURATION — single analogue input channel
# ---------------------------------------------------------------------------

daq = y2daq.analog()
daq.reset()
daq.addInput(0)             # AI0 — thermopile output (mV)
daq.Rate = SAMPLE_RATE
daq.Nscans = N_SAMPLES

# Set hardware trigger — acquisition waits for threshold crossing on the
# phototransistor channel. PRE_TRIGGER samples are buffered before the event.
daq.addTrigger(pretriggersamples=PRE_TRIGGER)

print("Ready. Fire the flash gun when prompted...")
print("go")  # Operator cue — fires flash gun now

# ---------------------------------------------------------------------------
# ACQUIRE DATA
# ---------------------------------------------------------------------------

data, timestamps = daq.read()

# Slice out the post-trigger signal, skipping the initial photodiode spike
start_idx = PRE_TRIGGER + TRIM_OFFSET
signal = data[start_idx : N_SAMPLES - 1]
time_axis = timestamps[start_idx : N_SAMPLES - 1]

# ---------------------------------------------------------------------------
# SMOOTHING — moving average (convolve with a uniform kernel of width N)
# ---------------------------------------------------------------------------

smoothed = np.convolve(signal, np.ones(SMOOTHING_N) / SMOOTHING_N, mode="same")

# ---------------------------------------------------------------------------
# EXTRACT HALF-TIME t½
# ---------------------------------------------------------------------------

V_max = np.amax(smoothed)
V_min = np.amin(smoothed)
V_half = (V_max - V_min) * 0.5 + V_min    # Midpoint between max and min

# Find the first index where the smoothed signal exceeds V_half
indices_above_half = np.argwhere(smoothed >= V_half)

if len(indices_above_half) == 0:
    print("WARNING: signal never reached half-maximum. Check flash gun and connection.")
    half_time = None
else:
    idx_half = indices_above_half[0][0]
    half_time = time_axis[idx_half]
    print(f"\nHalf-time index: {idx_half}")
    print(f"Half-time t½:    {half_time:.5f} s")
    print(f"V_max = {V_max:.4f} V,  V_half = {V_half:.4f} V")

# ---------------------------------------------------------------------------
# PLOT — raw signal and smoothed curve
# ---------------------------------------------------------------------------

plt.figure(figsize=(9, 5))
plt.plot(timestamps, data, "r-", alpha=0.4, linewidth=0.8, label="Raw signal (full)")
plt.plot(time_axis, smoothed, "b-", linewidth=1.2, label="Post-trigger (smoothed)")

if half_time is not None:
    plt.axhline(V_half, color="gray", linestyle="--", linewidth=0.8, label=f"V½ = {V_half:.4f} V")
    plt.axvline(half_time, color="orange", linestyle="--", linewidth=0.8, label=f"t½ = {half_time:.4f} s")

plt.xlabel("Time (s)")
plt.ylabel("Thermopile Signal (V)")
plt.title("Parker Flash Method — Thermal Response Curve")
plt.legend(fontsize=9)
plt.grid(alpha=0.4)
plt.tight_layout()
plt.show()

# ---------------------------------------------------------------------------
# RESET DAQ
# ---------------------------------------------------------------------------

daq.reset()
