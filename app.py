import tempfile
from pathlib import Path
from typing import Any, Optional

import streamlit as st

from src.body_profiler import BodyProfiler
from src.size_matcher import list_brands, recommend_size

st.set_page_config(page_title="FitMatch AI", page_icon="👕", layout="wide")


@st.cache_resource
def get_profiler() -> BodyProfiler:
    """Loads the MediaPipe model once per server process."""
    return BodyProfiler()


def analyse(photo: Any, height_cm: float) -> dict:
    """Saves the photo to a temp file and returns the body measurements."""
    suffix = Path(getattr(photo, "name", "photo.jpg")).suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(photo.getvalue())
    try:
        return get_profiler().extract_measurements(tmp.name, height_cm)
    finally:
        Path(tmp.name).unlink(missing_ok=True)


def show_results(photo: Any, measurements: dict, brand: str) -> None:
    """Renders the photo next to the size recommendation."""
    result = recommend_size(measurements["chest_cm"], brand)
    st.divider()
    img_col, res_col = st.columns([1, 1], gap="large")
    img_col.image(photo, caption="Your photo", use_container_width=True)
    with res_col:
        st.subheader("✨ Your Results")
        if not result["size"]:
            st.error(result["message"])
            return
        st.success(f"Your recommended {brand} size is **{result['size']}**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Size", result["size"])
        c2.metric("Chest (est.)", f"{measurements['chest_cm']} cm")
        c3.metric("Shoulders", f"{measurements['shoulder_cm']} cm")
        if result["boundary_warning"]:
            st.warning(result["boundary_warning"])


st.sidebar.header("⚙️ Settings")
brand = st.sidebar.selectbox("Target brand", list_brands())
height_cm = st.sidebar.slider("Your real height (cm)", 140, 210, 175)

st.title("👕 FitMatch AI")
st.markdown("**Snap a photo, get your size.** Our AI measures your shoulders and chest, "
            "then finds your best fit at your favourite brand.")

tab_camera, tab_upload = st.tabs(["📷 Take Photo", "📁 Upload Image"])
with tab_camera:
    camera = st.camera_input("Stand straight, facing the camera")
with tab_upload:
    uploaded = st.file_uploader("Choose a photo", type=["jpg", "jpeg", "png"])

photo: Optional[Any] = camera or uploaded
if photo is None:
    st.info("👆 Take or upload a photo to get started. Sizes are set in the sidebar.")
else:
    try:
        with st.spinner("Analysing your photo..."):
            measurements = analyse(photo, float(height_cm))
        show_results(photo, measurements, brand)
    except (ValueError, FileNotFoundError) as exc:
        st.error(str(exc))
