# Optical Absorption in GaAs — Bandgap & Urbach Energy
### Year 2 Physics Laboratory — University of Nottingham (Feb–Apr 2023)
### Pair Project

---

## Experiment Summary

Investigates light absorption in **GaAs** (gallium arsenide), a direct bandgap III-V semiconductor used in LEDs, laser diodes, and photodiodes. The optical absorption coefficient α is measured as a function of photon energy to extract:

1. **Band gap energy Eg** — the minimum photon energy needed to excite an electron across the gap
2. **Urbach energy EU** — characterises the width of the exponential absorption tail below the band edge (related to disorder and thermal broadening)

---

## Experimental Setup

The experiment uses a **monochromator** to sweep through wavelengths (~880–911 nm, near the GaAs absorption edge), with a **stepper motor** controlling the grating angle. Light transmitted through the GaAs wafer is detected by an **avalanche photodiode**, measured by a **lock-in amplifier** to reject background noise and 50 Hz pickup.

**The key automation challenge:** the Python code must simultaneously:
- Drive a stepper motor (4-phase, via digital outputs) to advance the monochromator
- Read the lock-in amplifier output (via analogue input)
- Record wavelength vs intensity data in real-time

This is exactly the kind of multi-channel real-time control that embedded and PLC systems perform.

---

## Physics

For a **direct bandgap** semiconductor (GaAs), above the band edge:

```
α² ∝ (E − Eg)    →    Eg extracted from x-intercept of α² vs E linear fit
```

Below the band edge (Urbach tail):

```
ln(α) ∝ E / EU    →    EU = 1 / slope of ln(α) vs E
```

The absorption coefficient α is calculated from the transmission ratio T = I / I₀:

```
α = −(1/x) · ln( [ √((1−R)⁴ + 4T²R²) − (1−R)² ] / (2TR²) )
```

Where x = wafer thickness (0.0417 cm), R = reflection coefficient, T = I/I₀.

---

## Files

| File | Description |
|---|---|
| `data_acquisition.py` | Automated monochromator sweep — stepper motor control + lock-in amplifier readout |
| `bandgap_analysis.py` | Calculates α², plots vs photon energy E, extracts Eg via linear fit |
| `urbach_analysis.py` | Calculates ln(α), plots vs photon energy E, extracts Urbach energy EU |

---

## Results (GaAs)

| Parameter | Measured | Literature |
|---|---|---|
| Band gap energy Eg | ~1.39 eV | 1.42 eV |
| Urbach energy EU | ~7 meV | ~7–10 meV |

---

## Notes

- `y2daq` is a university-internal library not available via pip — see parent repo README
- The stepper motor step sequence `[51, 102, 204, 153]` (big-endian uint8) is standard 4-phase half-stepping
- Wavelength calibration factor: 0.412 nm per motor step
