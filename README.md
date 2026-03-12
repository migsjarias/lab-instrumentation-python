# Peltier Heat Pump — Thermoelectric Device Characterisation & PID Control
### Year 2 Physics Laboratory — University of Nottingham (Nov 2022)

---

## Experiment Summary

A Peltier (thermoelectric) device uses the Seebeck effect to maintain a temperature difference between two surfaces when current is applied. This experiment:

1. **Characterised** the device — measuring its Seebeck coefficient α and thermal conductivity κ from real acquired data
2. **Implemented three feedback controllers** (On/Off, Proportional, Proportional-Integral) in Python to maintain a stable temperature setpoint

The device used: bismuth telluride n-p junction array (127 coupled elements), interfaced via NI DAQ card.

---

## Physics Background

The heat flow at the cold junction is governed by:

```
dQ/dt = α·I·T₁ - κ·(T₁ - T₀) - I²·ρ/(2G)
```

Where:
- `α` = Seebeck coefficient (V/K)
- `κ` = thermal conductivity (W/K)  
- `T₁`, `T₀` = cold and hot junction temperatures (K)
- `ρ` = electrical resistivity, `G` = geometric factor (0.078 cm)

Under zero-current conditions the temperature decay is exponential:

```
ΔT(t) = A · exp(-t/τ)
```

The time constant τ is directly related to κ — extracted from the slope of ln(ΔT) vs t.

The Seebeck coefficient α is extracted from the slope of V vs ΔT under zero-current conditions (from V = 2N·α·ΔT where N = 127 elements).

---

## Files

| File | Description |
|---|---|
| `data_acquisition.py` | Reads 4 analogue channels (T₁, T₀, V, I) simultaneously, plots live, extracts α and κ |
| `control_onoff.py` | On/Off controller — switches current direction based on setpoint comparison |
| `control_proportional.py` | Proportional controller — output current = Kp × (setpoint − measured) |
| `control_pi.py` | Proportional-Integral controller — adds accumulated error term to eliminate steady-state offset |

---

## Controller Summary

### On/Off Control
```python
if dT_measured > setpoint:
    a.write(+3)   # cool
else:
    a.write(-3)   # heat
```
Simple but produces sustained oscillation around the setpoint. Never reaches true steady state.

### Proportional (P) Control
```python
I_output = Kp * (setpoint - dT_measured)
```
Reduces oscillation. Has a steady-state error (offset) because when the error is zero, there is no drive current.

### Proportional-Integral (PI) Control
```python
I_output = Kp * error_now + Ki * sum(all_past_errors)
```
The integral term accumulates past error and eliminates steady-state offset. This is the industry-standard approach — the same structure used in industrial temperature controllers, motor drives, and pressure regulators.

**Tuned values:** Kp = −0.5, Ki = 0.01 × Kp

---

## Key Results

- **Thermal conductivity:** κ = extracted from exponential decay fit of ΔT vs t under zero current
- **Seebeck coefficient:** α = extracted from slope of V vs ΔT
- PI control achieved stable temperature lock within ~60 seconds of setpoint change, with <0.2°C residual error
