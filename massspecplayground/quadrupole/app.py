# app.py
import io
import streamlit as st
from stability_overlay import generate_overlay_VU

st.set_page_config(page_title="Quadrupole Stability Overlays", layout="centered")
st.title("Mathieu Stability Diagram — V vs U ")
st.caption("Defaults: RF = 867 kHz, r₀ = 5 mm; V = RF Amplitude (0-peak), U = Isolating DC; stability required in x and y.")

col1, col2 = st.columns(2)
with col1:
    f_khz = st.number_input("RF frequency (kHz)", value=867, min_value=100, max_value=5000, step=1)
    r0_mm = st.number_input("r₀ (mm)", value=5.0, min_value=1.0, max_value=10.0, step=0.1)
with col2:
    q_samples = st.slider("Boundary resolution (q samples)", 100, 260, 140, step=10)
    steps = st.slider("Solver steps (RK4)", 160, 360, 200, step=20)

st.markdown("**Enter up to three ions as `m/z:z`** (e.g., `262:2`).")
c1, c2, c3 = st.columns(3)
ion1 = c1.text_input("Ion 1", "262:2")
ion2 = c2.text_input("Ion 2", "524:1")
ion3 = c3.text_input("Ion 3", "1522:1")

# Custom axis ranges
st.markdown("### Axis ranges")
use_custom = st.checkbox("Use custom V/U ranges (Volts)", value=False)
vmin = vmax = umin = umax = None
if use_custom:
    a1, a2, a3, a4 = st.columns(4)
    vmin = a1.number_input("V min (V)", min_value=0.0, value=0.0, step=50.0)
    vmax = a2.number_input("V max (V)", min_value=1.0, value=2000.0, step=50.0)
    umin = a3.number_input("U min (V)", min_value=0.0, value=0.0, step=25.0)
    umax = a4.number_input("U max (V)", min_value=1.0, value=500.0, step=25.0)

def parse(pair):
    pair = pair.strip()
    if not pair: return None
    m, z = pair.split(":")
    return (float(m), int(z))

ions = [x for x in (parse(ion1), parse(ion2), parse(ion3)) if x]

@st.cache_resource
def render_overlay_cached(ions, f_rf_Hz, r0_mm, q_samples, steps, vmin, vmax, umin, umax):
    return generate_overlay_VU(
        ions=ions,
        f_rf_Hz=f_rf_Hz,
        r0_mm=r0_mm,
        q_samples=q_samples,
        steps=steps,
        title_prefix="Quadrupole",
        filename_base="exploris_overlay",
        v_min=vmin, v_max=vmax,
        u_min=umin, u_max=umax
    )

if st.button("Generate plot"):
    fig = render_overlay_cached(
        ions, f_khz*1e3, r0_mm, q_samples, steps,
        vmin if use_custom else None,
        vmax if use_custom else None,
        umin if use_custom else None,
        umax if use_custom else None
    )
    st.pyplot(fig, use_container_width=True)
    buf_png = io.BytesIO(); fig.savefig(buf_png, format="png", dpi=260, bbox_inches="tight")
    st.download_button("Download PNG", data=buf_png.getvalue(), file_name="overlay.png", mime="image/png")
    buf_pdf = io.BytesIO(); fig.savefig(buf_pdf, format="pdf", dpi=320, bbox_inches="tight")
    st.download_button("Download PDF", data=buf_pdf.getvalue(), file_name="overlay.pdf", mime="application/pdf")
