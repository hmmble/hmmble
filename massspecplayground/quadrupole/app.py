import streamlit as st
from stability_overlay import generate_overlay_VU

st.set_page_config(page_title="Quadrupole Stability Overlays", layout="centered")
st.title("Quadrupole Stability — V vs U")
st.caption("Exploris defaults: f = 867 kHz, r₀ = 5 mm; stability required in x and y.")

col1, col2 = st.columns(2)
with col1:
    f_khz = st.number_input("RF frequency (kHz)", value=867, min_value=100, max_value=5000, step=1)
    r0_mm = st.number_input("r₀ (mm)", value=5.0, min_value=1.0, max_value=10.0, step=0.1)
with col2:
    q_samples = st.slider("Boundary resolution (q samples)", 100, 240, 140, step=10)
    steps = st.slider("Solver steps (RK4)", 160, 360, 200, step=20)

st.markdown("**Enter up to three ions as `m/z:z`** (e.g., `262:2`). Leave blanks if unused.")
c1, c2, c3 = st.columns(3)
ion1 = c1.text_input("Ion 1", "262:2")
ion2 = c2.text_input("Ion 2", "524:1")
ion3 = c3.text_input("Ion 3", "1522:1")

def parse(pair):
    pair = pair.strip()
    if not pair: return None
    m, z = pair.split(":")
    return (float(m), int(z))

ions = [x for x in (parse(ion1), parse(ion2), parse(ion3)) if x]

if st.button("Generate plot"):
    fig = generate_overlay_VU(
        ions=ions,
        f_rf_Hz=f_khz * 1e3,
        r0_mm=r0_mm,
        q_samples=q_samples,
        steps=steps,
        title_prefix="Exploris",
        filename_base="exploris_overlay"
    )
    st.pyplot(fig)
    # Optional: save exports for download
    import io
    buf_png = io.BytesIO()
    fig.savefig(buf_png, format="png", dpi=260, bbox_inches="tight")
    st.download_button("Download PNG", data=buf_png.getvalue(), file_name="overlay.png", mime="image/png")
    buf_pdf = io.BytesIO()
    fig.savefig(buf_pdf, format="pdf", dpi=320, bbox_inches="tight")
    st.download_button("Download PDF", data=buf_pdf.getvalue(), file_name="overlay.pdf", mime="application/pdf")
