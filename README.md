# Lab Instrumentation — Python DAQ & Control
### Year 2 Physics Laboratory — University of Nottingham (2022–2023)

> **Python-based data acquisition, hardware control, and feedback systems for three experimental physics investigations.**
> All experiments interfaced directly with physical hardware via a National Instruments DAQ card using a university-developed `y2daq` library.

---

## Overview

This repository contains the Python code written for three second-year physics experiments at the University of Nottingham. Each experiment required writing acquisition software from scratch — reading analogue signals from sensors, controlling hardware outputs, and implementing real-time data analysis and plotting.

The common theme across all three: **write code that talks to real hardware, processes noisy physical signals, and produces quantitative results with proper uncertainty analysis.**

---

## Hardware Stack

All experiments used:
- **National Instruments DAQ card** — analogue inputs (AI0–AI3), analogue output (AO0), digital I/O
- **`y2daq` library** — university Python wrapper for NI-DAQmx
- **Windows PC** — experiments run in Spyder/Anaconda environment

> ⚠️ Note: `y2daq` is a university-internal library and is not pip-installable. The code in this repository is preserved for reference — the logic, control algorithms, and signal processing are fully portable to standard Python DAQ libraries (e.g. `nidaqmx`, `pyserial`, or any hardware abstraction layer).

---

## Experiments

| Folder | Experiment | Key Skills |
|---|---|---|
| [`peltier-heat-pump/`](./peltier-heat-pump/) | Peltier thermoelectric device — characterisation + closed-loop control | PID control, real-time acquisition, feedback systems |
| [`thermal-diffusivity/`](./thermal-diffusivity/) | Thermal diffusivity of stainless steel — Parker flash method | Hardware-triggered acquisition, curve fitting, heat equation |
| [`semiconductor-optical-absorption/`](./semiconductor-optical-absorption/) | Optical absorption in GaAs — bandgap and Urbach energy extraction | Stepper motor control, lock-in amplifier, spectroscopy automation |

---

## Why This Is Relevant to Automation Engineering

These experiments were, in essence, small embedded control systems:

- **Peltier PI controller** — identical in structure to industrial temperature PID loops used in process control. On/Off → Proportional → Proportional-Integral, tuned by hand against a real physical system.
- **Hardware-triggered acquisition** — the thermal diffusivity code triggers data capture off a hardware event (light flash detected by phototransistor), which is the same principle as interrupt-driven I/O in PLC and embedded systems.
- **Stepper motor automation** — the semiconductor code drives a stepper motor via digital outputs to sweep a monochromator, exactly analogous to commanding a stepper actuator in embedded/industrial firmware.

---

## Authors

Miguel PJ Arias — University of Nottingham, School of Physics & Astronomy, 2022–2023
