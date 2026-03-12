"""
analysis.py
===========
Calculates the thermal diffusivity of stainless steel from Parker flash method data.

Half-times t½ are measured for steel plates of different thickness L.
The thermal diffusivity α is extracted from the slope of t½ vs L²:

    t½ = (0.1388 / α) × L²

So:  α = 0.1388 / slope

Uses least-squares linear regression with a best-fit and worst-fit line
to estimate uncertainty in α.

Data collected from five plate thicknesses at the University of Nottingham lab.

Authors: Miguel PJ Arias — University of Nottingham, Dec 2022
"""

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# EXPERIMENTAL DATA
# Plate thickness L (mm) and measured half-time t½ (s)
# ---------------------------------------------------------------------------

# L² values (mm²) — derived from measured plate thicknesses
L_squared = np.array([0.27, 0.50, 0.96, 1.42, 2.16])   # mm²

# Measured half-times (s) — one per plate thickness
t_half = np.array([0.04835, 0.05754, 0.07615, 0.09500, 0.11809])  # s

# Uncertainties
err_t_half = 0.00004                                    # Constant vertical error (s)
err_L_sq   = np.array([0.01, 0.01, 0.02, 0.02, 0.03])  # Horizontal error in L² (mm²)

# ---------------------------------------------------------------------------
# LEAST-SQUARES LINEAR FIT — t½ vs L²
# ---------------------------------------------------------------------------

L_sq_mean = np.mean(L_squared)
t_mean     = np.mean(t_half)

numerator   = np.sum((L_squared - L_sq_mean) * t_half)
denominator = np.sum((L_squared - L_sq_mean)**2)

slope_best = numerator / denominator                    # Best-fit gradient
intercept  = t_mean - slope_best * L_sq_mean

# ---------------------------------------------------------------------------
# WORST-FIT LINE — for uncertainty estimation
# Upper-left to lower-right extreme through the error bars
# ---------------------------------------------------------------------------

slope_worst = (t_half[-2] - t_half[0]) / (L_squared[-2] - L_squared[0])
intercept_worst = t_half[0] - slope_worst * L_squared[0] + err_t_half

delta_slope = np.abs(slope_best - slope_worst)

# ---------------------------------------------------------------------------
# THERMAL DIFFUSIVITY — from Parker formula
# α = 0.1388 × L² / t½  →  α = 0.1388 / slope  (when L in m, t in s)
# Factor of 0.1388 comes from the analytical solution at T/Tmax = 0.5
# ---------------------------------------------------------------------------

PARKER_FACTOR = 0.1388   # Dimensionless — from analytical solution

# Convert L² from mm² to m² for SI units
alpha = PARKER_FACTOR / (slope_best * 1e-6)      # m²/s
delta_alpha = (PARKER_FACTOR * delta_slope) / (slope_best**2 * 1e-6)

# ---------------------------------------------------------------------------
# PLOT
# ---------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5))

ax.errorbar(
    L_squared, t_half,
    xerr=err_L_sq, yerr=err_t_half,
    fmt="m*", capsize=4, ecolor="k",
    label="Measured data", zorder=3
)
ax.plot(L_squared, slope_best  * L_squared + intercept,       "b-",  label="Best fit")
ax.plot(L_squared, slope_worst * L_squared + intercept_worst, "r--", label="Worst fit")

ax.set_xlabel(r"$L^2 \; (\mathrm{mm}^2)$", fontsize=13)
ax.set_ylabel(r"$t_{1/2} \; (\mathrm{s})$", fontsize=13)
ax.set_title("Parker Flash Method — Half-Time vs Plate Thickness²", fontsize=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.4)

plt.tight_layout()
plt.savefig("thermal_diffusivity_fit.png", dpi=150, bbox_inches="tight")
plt.show()

# ---------------------------------------------------------------------------
# RESULTS OUTPUT
# ---------------------------------------------------------------------------

print("\n── Thermal Diffusivity Results ──")
print(f"  Best-fit slope:                  {slope_best:.6f}  s/mm²")
print(f"  Worst-fit slope:                 {slope_worst:.6f}  s/mm²")
print(f"  Uncertainty in slope:            {delta_slope:.6f}  s/mm²")
print(f"")
print(f"  Thermal Diffusivity α:           {alpha:.3e}  m²/s")
print(f"  Uncertainty in α:                {delta_alpha:.3e}  m²/s")
print(f"")
print(f"  Literature value (stainless):    ~4.0 × 10⁻⁶  m²/s")
