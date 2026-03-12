"""
control_pi.py
=============
Proportional-Integral (PI) temperature controller for the Peltier device.

The output current on iteration n is given by:

    I_n = Kp × (setpoint − ΔT_n) + Ki × Σ(setpoint_i − ΔT_i)  for i = 0..n-1

Where:
    Kp  — proportional gain (immediate response to current error)
    Ki  — integral gain (accumulated response to eliminate steady-state offset)

The integral term sums up all past errors. This eliminates the steady-state
offset that the pure proportional controller leaves behind — when the system
is at setpoint, the integrator holds the current needed to maintain it.

Tuned values: Kp = -0.5, Ki = 0.01 × Kp
The setpoint is adjusted live using a slider widget.

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
# CONTROLLER GAINS — tuned by trial and error against the physical device
# ---------------------------------------------------------------------------

Kp = -0.5          # Proportional gain — negative because increasing current cools the cold side
Ki = 0.01 * Kp     # Integral gain — start much smaller than Kp, increase if slow to settle

# ---------------------------------------------------------------------------
# DAQ CONFIGURATION
# ---------------------------------------------------------------------------

daq = y2daq.analog()
daq.addInput(0)     # T₁ — cold junction temperature
daq.addInput(1)     # T₀ — hot junction temperature
daq.addInput(2)     # V  — device voltage
daq.addInput(3)     # I  — device current
daq.addOutput(0)    # AO0 — output voltage to current amplifier (0.5 A/V calibration)
daq.Nscans = 100
daq.Rate = 5000

# ---------------------------------------------------------------------------
# DATA ARRAYS
# ---------------------------------------------------------------------------

voltage    = np.array([])
current    = np.array([])
delta_T    = np.array([])
err_voltage = np.array([])
err_delta_T = np.array([])
time_s      = np.array([])
setpoints   = np.array([])   # Log of setpoint values for integral calculation

# ---------------------------------------------------------------------------
# LIVE PLOT & WIDGETS
# ---------------------------------------------------------------------------

fig = plt.figure(figsize=(7, 5))

# Stop button
off_ax = plt.axes([0.8, 0.75, 0.1, 0.1])
off_btn = widgets.Button(off_ax, "Stop")

# Setpoint slider: range ±4 °C, initial value 0
slider_ax = plt.axes([0.1, 0.05, 0.6, 0.03])
setpoint_slider = widgets.Slider(slider_ax, r"$\Delta T_{set}$ (°C)", -4, 4, valinit=0.0)

# Main plot axes
plt.axes([0.15, 0.25, 0.6, 0.7])
plt.xlabel("Time (s)")
plt.ylabel("Temperature Difference ΔT (°C)")
plt.grid(alpha=0.4)

acquisition_running = True

def stop_callback(event):
    global acquisition_running
    acquisition_running = False
    print("Acquisition stopped.")

def slider_callback(val):
    print(f"New setpoint: {val:.2f} °C")
    plt.draw()

off_btn.on_clicked(stop_callback)
setpoint_slider.on_changed(slider_callback)

# ---------------------------------------------------------------------------
# PI CONTROL LOOP
# ---------------------------------------------------------------------------

t0 = time.time()

while acquisition_running:
    t_read = time.time()
    data, timestamps = daq.read()

    t_now = t_read - t0 + np.mean(timestamps)

    # Read sensor values
    v_now  = np.mean(data[2, :])
    i_now  = np.mean(data[3, :])
    raw_dT = data[0, :] - data[1, :]
    dT_now = np.mean(raw_dT)

    err_v  = np.std(data[2, :]) / np.sqrt(daq.Nscans)
    err_dT = np.std(raw_dT)    / np.sqrt(daq.Nscans)

    # Current setpoint from slider
    setpoint = setpoint_slider.val

    # Append to history before computing integral
    time_s    = np.append(time_s,    t_now)
    delta_T   = np.append(delta_T,   dT_now)
    setpoints = np.append(setpoints, setpoint)

    # PI control law:
    # Proportional term: respond to current error
    # Integral term: sum of all past errors (accumulated over all iterations so far)
    proportional_term = Kp * (setpoint - dT_now)
    integral_term     = Ki * np.sum(setpoints[:-1] - delta_T[:-1])
    I_output = proportional_term + integral_term

    # Write output current (voltage in V → current via 0.5 A/V amplifier calibration)
    daq.write(I_output)

    # Live plot — measured ΔT (green dots with error bars)
    plt.errorbar(t_now, dT_now, yerr=err_dT, fmt="g.", capsize=3, ecolor="k")
    plt.axhline(setpoint, color="orange", linewidth=0.8, linestyle="--")

    plt.pause(0.01)

    # Append remaining arrays
    voltage     = np.append(voltage,     v_now)
    current     = np.append(current,     i_now)
    err_voltage = np.append(err_voltage, err_v)
    err_delta_T = np.append(err_delta_T, err_dT)

print(f"\nFinal controller state:")
print(f"  Setpoint:          {setpoints[-1]:.2f} °C")
print(f"  Measured ΔT:       {delta_T[-1]:.2f} °C")
print(f"  Residual error:    {setpoints[-1] - delta_T[-1]:.3f} °C")
