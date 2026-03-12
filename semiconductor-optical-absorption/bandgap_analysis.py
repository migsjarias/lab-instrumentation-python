"""
bandgap_analysis.py
===================
Extracts the band gap energy Eg of GaAs from optical transmission data.

For a direct bandgap semiconductor, above the band edge the absorption
coefficient satisfies:

    α² ∝ (hν − Eg)

A linear fit of α² vs photon energy E gives Eg as the x-intercept (where α² = 0).

The absorption coefficient α is computed from measured transmission I/I₀
using the full reflection-corrected formula:

    α = −(1/x) · ln( [ √((1−R)⁴ + 4T²R²) − (1−R)² ] / (2TR²) )

Where:
    T = I / I₀    (transmission coefficient)
    R = (T−1)/(T+1)  (approximate reflection coefficient from Fresnel equations)
    x = wafer thickness (cm)

Data: GaAs wafer, measured at near-infrared wavelengths (880–911 nm)
at the University of Nottingham optical absorption lab.

Authors: Miguel PJ Arias — University of Nottingham, Apr 2023
"""

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# PHYSICAL CONSTANTS
# ---------------------------------------------------------------------------

h = 6.6263e-34    # Planck's constant (J·s)
c = 3.0e8         # Speed of light (m/s)
e = 1.6e-19       # Electron charge (C)
x = 0.0417        # GaAs wafer thickness (cm)

# ---------------------------------------------------------------------------
# MEASURED DATA
# Wavelength (nm) and corresponding transmitted / reference intensities (V)
# ---------------------------------------------------------------------------

wavelength_nm = np.array([
    880.5,  881.056, 881.604, 882.155, 882.705, 883.255, 883.805, 884.354,
    884.904, 885.454, 886.006, 886.554, 887.104, 887.653, 888.204, 888.755,
    889.305, 889.854, 890.404, 890.954, 891.503, 892.053, 892.603, 893.154,
    893.706, 894.256, 894.804, 895.355, 895.906, 896.454, 897.004, 897.555,
    898.106, 898.655, 899.207, 899.758, 900.309, 900.862, 901.414, 901.965,
    902.516, 903.064, 903.615, 904.164, 904.714, 905.264, 905.814, 906.364,
    906.914, 907.464, 908.012, 908.561, 909.112, 909.663, 910.212, 910.763
])

# I  — transmitted intensity through GaAs wafer (lock-in amplifier output, V)
I = np.array([
    0.00804739, 0.0080636, 0.0075871, 0.00834237, 0.00870217, 0.00753524,
    0.00628402, 0.00726295, 0.00803443, 0.00846555, 0.00895177, 0.00924674,
    0.00956765, 0.0103132,  0.0115028,  0.0131689,  0.0154542,  0.018271,
    0.0226017,  0.0273472,  0.0346665,  0.0452791,  0.0569841,  0.0742742,
    0.0927896,  0.112407,   0.138501,   0.165292,   0.191684,   0.215648,
    0.243943,   0.270705,   0.297204,   0.323895,   0.351337,   0.378997,
    0.397493,   0.413933,   0.429058,   0.442232,   0.453609,   0.464617,
    0.47407,    0.479684,   0.485058,   0.49075,    0.494909,   0.500258,
    0.502802,   0.506462,   0.507797,   0.511078,   0.512449,   0.487117,
    0.460893,   0.458241
])

# I₀ — reference intensity (no sample in beam)
I0 = np.array([
    1.07057, 1.07386, 1.07224, 1.07105, 1.07335, 1.07563, 1.07522, 1.07098,
    1.06481, 1.07867, 1.08102, 1.08158, 1.08047, 1.07901, 1.08194, 1.08407,
    1.08445, 1.08402, 1.08500, 1.08392, 1.08413, 1.08476, 1.08541, 1.08580,
    1.08872, 1.08996, 1.09152, 1.09188, 1.09156, 1.08977, 1.09108, 1.09090,
    1.10954, 1.08667, 1.09102, 1.09070, 1.09100, 1.09341, 1.09598, 1.09586,
    1.09852, 1.09862, 1.10178, 1.10429, 1.10428, 1.10536, 1.10549, 1.10306,
    1.10802, 1.10614, 1.11254, 1.10482, 1.10467, 1.10861, 1.10415, 1.09871
])

# ---------------------------------------------------------------------------
# COMPUTE ABSORPTION COEFFICIENT α
# ---------------------------------------------------------------------------

T = I / I0                       # Transmission coefficient
R = (T - 1) / (1 + T)           # Reflection coefficient (Fresnel approximation)

# Photon energy E = hc / λ  (eV)
E_eV = (h * c) / (wavelength_nm * 1e-9 * e)

# Absorption coefficient — full reflection-corrected expression
term_A = (1 - R)**4
term_B = 4 * (T**2) * (R**2)
alpha = (-1 / x) * np.log(
    (np.sqrt(term_A + term_B) - (1 - R)**2) / (2 * T * (R**2))
)

alpha_sq = alpha**2

# ---------------------------------------------------------------------------
# ERROR PROPAGATION
# ---------------------------------------------------------------------------

dI  = np.std(I[:10])    # Noise estimate from low-intensity (opaque) region
dI0 = np.std(I0[:10])
dx  = 0.0001            # Uncertainty in wafer thickness (cm)

dT = T  * np.sqrt((dI / I)**2 + (dI0 / I0)**2)
dR = R  * np.sqrt((dT / (1 - T))**2 + (dT / (1 + T))**2)

A  = 1 - R
dA = dR
C  = (T**2) * (R**2)
dC = C  * np.sqrt(2 * (dT / T) + 2 * (dR / R))
B  = A**4 + 4 * C
dB = B  * np.sqrt((4 * A**3 * dA)**2 + dC**2)
D  = B**0.5 - A**2
dD = D  * np.sqrt((0.5 * dB * B**(-0.5))**2 + (2 * dA * A)**2)
J  = D / (2 * T * R**2)
dJ = J  * np.sqrt((dD / D)**2 + (dT / T)**2 + (2 * dR / R)**2)
K  = np.log(J)
dK = dJ / J

da = alpha * np.sqrt((dx / x)**2 + (dK / K)**2)
yerr = 2 * alpha * da   # Propagated into α²

# ---------------------------------------------------------------------------
# LINEAR FIT OF α² vs E — near the band edge (indices 16:23)
# ---------------------------------------------------------------------------

fit_slice = slice(16, 23)
E_fit     = E_eV[fit_slice]
a_sq_fit  = alpha_sq[fit_slice]

E_mean    = np.mean(E_fit)
a_sq_mean = np.mean(a_sq_fit)

slope_best = np.sum((E_fit - E_mean) * a_sq_fit) / np.sum((E_fit - E_mean)**2)
intercept  = a_sq_mean - slope_best * E_mean

# Worst-fit slope for uncertainty
slope_worst  = ((a_sq_fit[0] - yerr[16]) - (a_sq_fit[6] + yerr[22])) / (E_fit[0] - E_fit[6])
intercept_wf = a_sq_fit[6] - slope_worst * E_fit[6] + yerr[22]

delta_slope     = slope_best - slope_worst
delta_intercept = intercept_wf - intercept

# Band gap energy: α² = 0  →  Eg = −c / m
E_g      = -intercept / slope_best
E_g_err  = E_g * np.sqrt((delta_intercept / intercept)**2 + (delta_slope / slope_best)**2)

# ---------------------------------------------------------------------------
# PLOT
# ---------------------------------------------------------------------------

E_fit_line = np.arange(1.385, 1.402, 0.001)

fig, ax = plt.subplots(figsize=(8, 5))
ax.errorbar(E_eV, alpha_sq, yerr=yerr, fmt="k*", capsize=2, ecolor="k",
            label="Recorded Data", zorder=2)
ax.plot(E_fit_line, slope_best * E_fit_line + intercept, "r--",
        label=f"Linear fit  →  Eg = {E_g:.3f} eV")
ax.axvline(E_g, color="orange", linestyle=":", linewidth=1.0, label="Band edge")

ax.set_xlabel("Photon Energy, E (eV)", fontsize=13)
ax.set_ylabel(r"$\alpha^2 \; (\mathrm{cm}^{-2})$", fontsize=13)
ax.set_title("GaAs Optical Absorption — Direct Band Gap Extraction", fontsize=12)
ax.legend(fontsize=9)
ax.grid(alpha=0.4)
plt.tight_layout()
plt.savefig("bandgap_fit.png", dpi=150, bbox_inches="tight")
plt.show()

# ---------------------------------------------------------------------------
# RESULTS
# ---------------------------------------------------------------------------

print("\n── Band Gap Energy Results ──")
print(f"  Best-fit slope:         {slope_best:.4e}  cm⁻²/eV")
print(f"  Worst-fit slope:        {slope_worst:.4e}  cm⁻²/eV")
print(f"  Band gap energy Eg:     {E_g:.4f} ± {E_g_err:.4f}  eV")
print(f"  Literature value (GaAs): 1.42 eV")
