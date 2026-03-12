# Thermal Diffusivity of Stainless Steel — Parker Flash Method
### Year 2 Physics Laboratory — University of Nottingham (Dec 2022)

---

## Experiment Summary

Determines the **thermal diffusivity** α of a stainless steel plate using the Parker flash method:

1. A flash gun fires a brief, intense light pulse at the front face of a thin steel plate
2. A thermopile on the rear face records the temperature rise over time
3. The time taken to reach half the maximum temperature rise (the **half-time** t½) is extracted
4. Thermal diffusivity is calculated from: `α = 0.1388 × L² / t½`

The experiment is repeated for steel plates of different thickness L, and α is found from the slope of t½ vs L².

---

## Key Physics

Heat flow in an isotropic medium:

```
∂T/∂t = α · ∂²T/∂x²
```

The analytical solution for temperature at the rear surface (x = L) after a flash at t = 0 gives:

```
T(L,t) / T_max = 1 − 2·Σ (−1)ⁿ · exp(−n²π²αt / L²)
```

At `T / T_max = 0.5` this yields: `t½ = 0.1388 · L² / α`

---

## Hardware-Triggered Acquisition

A key aspect of this experiment is that data acquisition is **triggered by the flash event itself**:

- A phototransistor detects the light pulse
- The DAQ card monitors this channel continuously with a pre-trigger buffer (200 samples)
- When the signal crosses a threshold, acquisition is automatically triggered
- The code captures the thermal response curve starting from the moment of the flash

This is directly analogous to **interrupt-driven I/O** in embedded and PLC systems — a hardware event triggers a software response.

---

## Files

| File | Description |
|---|---|
| `acquisition.py` | Hardware-triggered data acquisition — detects flash, captures thermopile signal, extracts t½ |
| `analysis.py` | Plots t½ vs L², fits best/worst lines, calculates α with uncertainty |

---

## Results

From the slope of t½ vs L² across multiple plate thicknesses:

```
α = 0.193 / slope    (m²/s)
```

Literature value for stainless steel: α ≈ 4.0 × 10⁻⁶ m²/s
