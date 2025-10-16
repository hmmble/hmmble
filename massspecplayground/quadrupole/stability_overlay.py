import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

e = 1.602176634e-19
amu = 1.66053906660e-27

def _monodromy_matrix(a, q, steps=200):
    T = np.pi
    h = T / steps
    x1, v1 = 1.0, 0.0
    x2, v2 = 0.0, 1.0
    tau = 0.0
    def acc(x, tau_local): return -(a - 2.0*q*np.cos(2.0*tau_local)) * x
    for _ in range(steps):
        k1x1 = v1; k1v1 = acc(x1, tau)
        k2x1 = v1 + 0.5*h*k1v1; k2v1 = acc(x1 + 0.5*h*k1x1, tau + 0.5*h)
        k3x1 = v1 + 0.5*h*k2v1; k3v1 = acc(x1 + 0.5*h*k2x1, tau + 0.5*h)
        k4x1 = v1 + h*k3v1;      k4v1 = acc(x1 + h*k3x1, tau + h)
        x1 += (h/6.0)*(k1x1 + 2*k2x1 + 2*k3x1 + k4x1)
        v1 += (h/6.0)*(k1v1 + 2*k2v1 + 2*k3v1 + k4v1)

        k1x2 = v2; k1v2 = acc(x2, tau)
        k2x2 = v2 + 0.5*h*k1v2; k2v2 = acc(x2 + 0.5*h*k1x2, tau + 0.5*h)
        k3x2 = v2 + 0.5*h*k2v2; k3v2 = acc(x2 + 0.5*h*k2x2, tau + 0.5*h)
        k4x2 = v2 + h*k3v2;      k4v2 = acc(x2 + h*k3x2, tau + h)
        x2 += (h/6.0)*(k1x2 + 2*k2x2 + 2*k3x2 + k4x2)
        v2 += (h/6.0)*(k1v2 + 2*k2v2 + 2*k3v2 + k4v2)
        tau += h
    return np.array([[x1, x2],[v1, v2]], dtype=float)

def _stable_axis(a, q, steps=200):
    M = _monodromy_matrix(a, q, steps=steps)
    return abs(np.trace(M)) <= 2.0

def _stable_both(a, q, steps=200):
    return _stable_axis(a, q, steps=steps) and _stable_axis(-a, q, steps=steps)

def _trace_boundary(q_max=0.95, a_hi=0.95, q_samples=140, steps=200):
    q_grid = np.linspace(0.0, q_max, q_samples)
    a_vals = []
    for q in q_grid:
        lo, hi = 0.0, a_hi
        if not _stable_both(lo, q, steps=steps):
            found = False
            for guess in np.linspace(0.0, 0.3, 8):
                if _stable_both(guess, q, steps=steps):
                    lo = guess; found = True; break
            if not found:
                a_vals.append(np.nan); continue
        if _stable_both(hi, q, steps=steps):
            a_vals.append(hi); continue
        for _ in range(18):
            mid = 0.5*(lo + hi)
            if _stable_both(mid, q, steps=steps): lo = mid
            else: hi = mid
        a_vals.append(lo)
    qb = q_grid[~np.isnan(a_vals)]
    ab = np.array(a_vals)[~np.isnan(a_vals)]
    return qb, ab

def _to_VU(qb, ab, f_rf_Hz, r0_m, mz, z):
    Omega = 2*np.pi*f_rf_Hz
    m = (mz * amu) / z
    scale_V = m * r0_m**2 * Omega**2 / (2*e)
    scale_U = m * r0_m**2 * Omega**2 / (4*e)
    return scale_V * qb, scale_U * ab

def generate_overlay_VU(ions, f_rf_Hz=867_000.0, r0_mm=5.0,
                        q_samples=140, steps=200, title_prefix="Exploris",
                        filename_base="exploris_overlay"):
    qb, ab = _trace_boundary(q_samples=q_samples, steps=steps)
    r0_m = r0_mm * 1e-3
    fig, ax = plt.subplots(figsize=(10, 8))
    palette = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    handles, labels, allV, allU = [], [], [], []
    for idx, (mz, z) in enumerate(ions[:3]):
        Vb, Ub = _to_VU(qb, ab, f_rf_Hz, r0_m, mz, z)
        verts_closed = np.vstack([[Vb[0], 0.0], np.column_stack([Vb, Ub]), [Vb[-1], 0.0]])
        codes = np.full(len(verts_closed), Path.LINETO); codes[0] = Path.MOVETO
        patch = PathPatch(Path(verts_closed, codes), facecolor=palette[idx], alpha=0.35,
                          edgecolor=palette[idx], linewidth=2.0, label=f"m/z {mz:g} (z={z})")
        ax.add_patch(patch); handles.append(patch); labels.append(f"m/z {mz:g} (z={z})")
        allV.append(Vb); allU.append(Ub)
    ax.set_title(f"{title_prefix} stability regions — V (RF 0-pk) vs U (DC)\n"
                 f"{f_rf_Hz/1000:.0f} kHz, r₀ = {r0_mm:g} mm (x & y stable)")
    ax.set_xlabel("V (Volts, RF zero-to-peak)"); ax.set_ylabel("U (Volts, DC)")
    ax.grid(True, alpha=0.35)
    allV = np.concatenate(allV); allU = np.concatenate(allU)
    ax.set_xlim(0, 1.05*np.max(allV)); ax.set_ylim(0, 1.05*np.max(allU))
    ax.legend(handles, labels, loc="upper right")
    plt.tight_layout()
    svg = None  # We’ll export via Streamlit
    return fig
