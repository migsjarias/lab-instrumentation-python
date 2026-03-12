"""
data_acquisition.py
===================
Real-time data acquisition for the Peltier heat pump experiment.

Reads four analogue channels simultaneously via NI DAQ:
    AI0  — Cold junction temperature T₁  (10 mV/°C)
    AI1  — Hot junction temperature T₀   (10 mV/°C)
    AI2  — Device voltage V              (V)
    AI3  — Device current I              (100 mV/A)

Plots temperature difference ΔT, voltage, and current live.
After acquisition is stopped, fits ln(ΔT) vs t to extract thermal
conductivity κ, and fits V vs ΔT to extract the Seebeck coefficient α.

Hardware: Peltier device (bismuth telluride, 127 n-p elements) interfaced
          via NI DAQ card and y2daq library.

Authors: Miguel PJ Arias — University of Nottingham, Nov 2022
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import time
import sys
sys.path.insert(1, "C:\\python")
import y2daq

# ---------------------------------------------------------------------------
# DEVICE CONSTANTS
# ---------------------------------------------------------------------------

N_ELEMENTS = 127        # Number of n-p coupled elements in the Peltier device
G_FACTOR = 0.00078      # Geometric factor (m) — G = 0.078 cm converted to m

# Brass block properties (used to calculate heat capacity)
BRASS_HEAT_CAPACITY = 0.387   # J / (g·K)
BRASS_DENSITY = 8.4           # g/cm³
BRASS_VOLUME = 30 * 30 * 9   # mm³ — block is 30×30×9 mm

# Convert brass volume to cm³ and compute heat capacity C = c × ρ × V
BRASS_VOLUME_CM3 = BRASS_VOLUME / 1000
BRASS_MASS_G = BRASS_DENSITY * BRASS_VOLUME_CM3
C_BRASS = BRASS_HEAT_CAPACITY * BRASS_MASS_G   # Total heat capacity in J/K

# ---------------------------------------------------------------------------
# DAQ CONFIGURATION
# ---------------------------------------------------------------------------

daq = y2daq.analog()
daq.addInput(0)     # T₁ — cold junction temperature
daq.addInput(1)     # T₀ — hot junction temperature
daq.addInput(2)     # V  — device voltage
daq.addInput(3)     # I  — device current
daq.Nscans = 100    # Points per acquisition burst
daq.Rate = 5000     # Sampling rate (points/second)

# ---------------------------------------------------------------------------
# DATA ARRAYS
# ---------------------------------------------------------------------------

voltage = np.array([])
current = np.array([])
delta_T = np.array([])
err_voltage = np.array([])   # Standard error in voltage
err_delta_T = np.array([])   # Standard error in ΔT
time_s = np.array([])

# ---------------------------------------------------------------------------
# LIVE PLOT SETUP
# ---------------------------------------------------------------------------

fig = plt.figure(figsize=(7, 5))

# Stop button
off_ax = plt.axes([0.8, 0.75, 0.1, 0.1])
off_btn = widgets.Button(off_ax, "Stop")

# Main plot area
plt.axes([0.15, 0.25, 0.6, 0.7])
plt.xlabel("Time (s)")
plt.ylabel("Signal")
plt.grid(alpha=0.4)

# State flag for acquisition loop
acquisition_running = True

def stop_callback(event):
    global acquisition_running
    acquisition_running = False
    print("Acquisition stopped.")

off_btn.on_clicked(stop_callback)

# ---------------------------------------------------------------------------
# REAL-TIME ACQUISITION LOOP
# ---------------------------------------------------------------------------

t0 = time.time()

while acquisition_running:
    t_read = time.time()
    data, timestamps = daq.read()

    t_now = t_read - t0 + np.mean(timestamps)

    # Extract mean values from the burst
    v_now = np.mean(data[2, :])                   # Voltage (V)
    i_now = np.mean(data[3, :])                   # Current (A, via 100mV/A calibration)
    raw_dT = data[0, :] - data[1, :]              # ΔT per sample in the burst
    dT_now = np.mean(raw_dT)                       # Mean ΔT (in units of 10mV/°C)

    # Standard errors (uncertainty across the Nscans burst)
    err_v = np.std(data[2, :]) / np.sqrt(daq.Nscans)
    err_dT = np.std(raw_dT) / np.sqrt(daq.Nscans)

    # Live plot — ΔT (green), V (red), I (blue)
    plt.errorbar(t_now, v_now,   yerr=err_v,  fmt="r*", capsize=3, ecolor="k")
    plt.errorbar(t_now, dT_now,  yerr=err_dT, fmt="g.", capsize=3, ecolor="k")
    plt.plot(t_now, i_now, "b.")

    plt.pause(0.01)

    # Append to arrays
    time_s     = np.append(time_s,     t_now)
    voltage    = np.append(voltage,    v_now)
    current    = np.append(current,    i_now)
    delta_T    = np.append(delta_T,    dT_now)
    err_voltage = np.append(err_voltage, err_v)
    err_delta_T = np.append(err_delta_T, err_dT)

# ---------------------------------------------------------------------------
# ANALYSIS — EXTRACT κ FROM ln(ΔT) VS TIME
# ---------------------------------------------------------------------------

fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
plt.subplots_adjust(hspace=0.4)

ln_dT = np.log(delta_T)                 # Natural log of temperature difference
err_ln_dT = err_delta_T / delta_T       # Error propagation: δ(ln x) = δx / x
mean_err_ln_dT = np.mean(err_ln_dT)

# Least-squares best-fit line for ln(ΔT) vs t
t_mean = np.mean(time_s)
lnT_mean = np.mean(ln_dT)
m_best = np.sum((time_s - t_mean) * ln_dT) / np.sum((time_s - t_mean)**2)
c_best = lnT_mean - m_best * t_mean

# Worst-fit line for uncertainty estimate
k_last = len(ln_dT) - 1
m_worst = ((ln_dT[k_last] - mean_err_ln_dT / 2) - (ln_dT[0] + mean_err_ln_dT / 2)) / (time_s[k_last] - time_s[0])
c_worst = ln_dT[0] - m_worst * time_s[0]
delta_m = m_best - m_worst

# Thermal conductivity κ from time constant:
# τ = -C / (2N·κ·G)  →  κ = -C·m / (2N·G)
kappa = -(C_BRASS * m_best) / (2 * N_ELEMENTS * G_FACTOR)
delta_kappa = (C_BRASS / (2 * N_ELEMENTS * G_FACTOR)) * delta_m

ax1.plot(time_s, m_best * time_s + c_best, "b-", label="Best fit")
ax1.plot(time_s, m_worst * time_s + c_worst, "r--", label="Worst fit")
ax1.set_xlabel("Time, $t$ (s)")
ax1.set_ylabel("ln(ΔT)")
ax1.legend()
ax1.grid(alpha=0.4)

print(f"\n── Thermal Conductivity Analysis ──")
print(f"  Gradient (best fit):   {m_best:.5f}")
print(f"  Gradient (worst fit):  {m_worst:.5f}")
print(f"  Uncertainty in m:      {delta_m:.5f}")
print(f"  κ = {kappa:.4f} ± {delta_kappa:.4f}  (W/K)")

# ---------------------------------------------------------------------------
# ANALYSIS — EXTRACT α (SEEBECK COEFFICIENT) FROM V VS ΔT
# ---------------------------------------------------------------------------

mean_err_v = np.mean(err_voltage)
dT_mean = np.mean(delta_T)
v_mean = np.mean(voltage)

m_v = np.sum((delta_T - dT_mean) * voltage) / np.sum((delta_T - dT_mean)**2)
c_v = v_mean - m_v * dT_mean

k_last = len(voltage) - 1
m_v_worst = ((voltage[k_last] - mean_err_v / 2) - (voltage[0] + mean_err_v / 2)) / (delta_T[k_last] - delta_T[0])
delta_m_v = m_v - m_v_worst

# Seebeck coefficient: V = 2N·α·ΔT  →  α = m / (2N)
alpha = m_v / (2 * N_ELEMENTS)
delta_alpha = delta_m_v / (2 * N_ELEMENTS)

ax2.plot(delta_T, m_v * delta_T + c_v, "c-", label="Best fit")
ax2.plot(delta_T, m_v_worst * delta_T + (voltage[0] - m_v_worst * delta_T[0]), "m--", label="Worst fit")
ax2.set_xlabel("Temperature Difference, ΔT (×10mV/°C)")
ax2.set_ylabel("Voltage, V (V)")
ax2.legend()
ax2.grid(alpha=0.4)

print(f"\n── Seebeck Coefficient Analysis ──")
print(f"  Gradient (best fit):   {m_v:.5f}")
print(f"  Gradient (worst fit):  {m_v_worst:.5f}")
print(f"  Uncertainty in m:      {delta_m_v:.5f}")
print(f"  α = {alpha:.6f} ± {delta_alpha:.6f}  (V/K)")

plt.show()
