"""
data_acquisition.py
===================
Automated optical absorption measurement for the GaAs spectroscopy experiment.

Controls a stepper motor (via digital outputs) to sweep the monochromator
grating through wavelengths, while simultaneously reading the lock-in amplifier
output (via analogue input) to measure transmitted light intensity.

The lock-in amplifier rejects background noise by demodulating the signal at
the chopper frequency — only light at the modulation frequency is recorded.

Stepper motor: 4-phase, driven via y2daq digital output channels.
Step sequence: [51, 102, 204, 153] (uint8 big-endian, standard 4-phase half-step)

Wavelength calibration: 0.412 nm per 4 motor steps.

Authors: Miguel PJ Arias — University of Nottingham, Feb 2023
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import time
import sys
sys.path.insert(1, "C:\\python")
import y2daq

# ---------------------------------------------------------------------------
# STEPPER MOTOR STEP SEQUENCES
# 4-phase half-step patterns — uint8 values written to digital output channels
# ---------------------------------------------------------------------------

STEPS_INCREASE = np.array([51, 102, 204, 153], dtype=np.uint8)   # Increase wavelength
STEPS_DECREASE = np.array([153, 204, 102, 51], dtype=np.uint8)   # Decrease wavelength

STEP_DELAY = 0.3          # Seconds per motor step — limits sweep speed to avoid overshoot
NM_PER_STEP_SET = 0.412   # Wavelength advance per 4-step set (nm) — calibration constant

# ---------------------------------------------------------------------------
# GLOBALS
# ---------------------------------------------------------------------------

start_wavelength = int(input("Enter initial wavelength on monochromator (nm): "))
start_rotation = False
wavelengths = np.array([])
intensities = np.array([])
acquisition_running = True

# ---------------------------------------------------------------------------
# CALLBACKS
# ---------------------------------------------------------------------------

def start_callback(event):
    """Begin monochromator sweep and data acquisition."""
    global start_rotation, wavelengths, intensities
    start_rotation = True
    wavelengths, intensities = run_sweep(start_wavelength)

def stop_callback(event):
    """Pause the wavelength sweep (keeps acquisition live)."""
    global start_rotation
    start_rotation = False

def close_callback(event):
    """Release digital I/O and close all windows."""
    dio.clear()
    dio.__end__()
    plt.close("all")

def acq_stop_callback(event):
    """Stop data acquisition loop."""
    global acquisition_running
    acquisition_running = False
    print("Acquisition stopped.")

# ---------------------------------------------------------------------------
# SWEEP FUNCTION
# ---------------------------------------------------------------------------

def run_sweep(start_nm: int) -> tuple:
    """
    Executes the automated monochromator sweep.

    For each 4-step motor advance:
    1. Write the step sequence to digital outputs (moves grating)
    2. Read the lock-in amplifier output via analogue input
    3. Calculate current wavelength from start + elapsed steps × calibration
    4. Append (wavelength, intensity) to arrays and plot live

    Parameters
    ----------
    start_nm : int
        Starting wavelength on the monochromator dial (nm).

    Returns
    -------
    tuple : (wavelengths_nm, intensities_V)
        Recorded wavelengths and corresponding lock-in amplifier readings.
    """
    global acquisition_running

    # Set up analogue input for lock-in amplifier
    daq = y2daq.analog()
    daq.addInput(0)     # Lock-in amplifier output
    daq.Nscans = 100
    daq.Rate = 5000

    # Stop button within the sweep
    off_ax = plt.axes([0.1, 0.05, 0.2, 0.1])
    off_btn = widgets.Button(off_ax, "End Acquisition")
    off_btn.on_clicked(acq_stop_callback)

    ax = plt.axes([0.1, 0.25, 0.6, 0.7])
    plt.xlabel(r"Wavelength $\lambda$ (nm)")
    plt.ylabel(r"Lock-in Output $I$ (V)")

    wavelengths_arr = np.array([])
    intensities_arr = np.array([])

    t0 = time.time()
    acquisition_running = True

    while start_rotation:
        # Select step direction from radio button
        direction = radio_btn.value_selected
        steps = STEPS_INCREASE if direction == "increase" else STEPS_DECREASE

        # Advance motor by one 4-step set
        for step in steps:
            dio.write(np.unpackbits(step))
            plt.pause(STEP_DELAY)

        if acquisition_running:
            t_now = time.time()

            # Read lock-in amplifier
            data, timestamps = daq.read()
            intensity = np.mean(data)

            # Calculate wavelength from elapsed time and calibration
            elapsed_time = t_now - t0 + np.mean(timestamps)
            if direction == "increase":
                wavelength = start_nm + elapsed_time * NM_PER_STEP_SET
            else:
                wavelength = start_nm - elapsed_time * NM_PER_STEP_SET

            # Plot and record
            ax.plot(wavelength, intensity, "m.")
            plt.pause(0.1)

            wavelengths_arr = np.append(wavelengths_arr, wavelength)
            intensities_arr = np.append(intensities_arr, intensity)

    return wavelengths_arr, intensities_arr

# ---------------------------------------------------------------------------
# GUI SETUP
# ---------------------------------------------------------------------------

fig = plt.figure(figsize=(9, 5))

# Direction radio buttons
radio_ax = plt.axes([0.7, 0.3, 0.3, 0.3])
radio_btn = widgets.RadioButtons(radio_ax, ("increase", "decrease"), active=0)

# Start / Stop wavelength sweep buttons
start_ax = plt.axes([0.70, 0.20, 0.08, 0.08])
start_btn = widgets.Button(start_ax, "Start")
start_btn.on_clicked(start_callback)

stop_ax = plt.axes([0.92, 0.20, 0.08, 0.08])
stop_btn = widgets.Button(stop_ax, "Stop")
stop_btn.on_clicked(stop_callback)

# Exit button
exit_ax = plt.axes([0.85, 0.85, 0.1, 0.1])
exit_btn = widgets.Button(exit_ax, "Exit")
exit_btn.on_clicked(close_callback)

# ---------------------------------------------------------------------------
# DIGITAL I/O — stepper motor
# ---------------------------------------------------------------------------

dio = y2daq.digital()

plt.show()
