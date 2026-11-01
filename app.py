import tempfile
from pathlib import Path
from typing import Any

import streamlit as st

from src.body_profiler import BodyProfiler
from src.size_matcher import list_brands, recommend_size

st.set_page_config(page_title="FitMatch AI", page_icon="👕", layout="centered")

DEFAULTS = {"step": 1, "height_cm": 175, "brand": list_brands()[0], "photo": None}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def inject_css() -> None:
    """Injects assets/style.css into the page."""
    css_path = Path(__file__).parent / "assets" / "style.css"
    css_content = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


@st.cache_resource
def get_profiler() -> BodyProfiler:
    """Loads the MediaPipe model once per server process."""
    return BodyProfiler()


def go_to(step: int, clear_photo: bool = False) -> None:
    """Moves the wizard to another step and reruns the script."""
    st.session_state.step = step
    if clear_photo:
        st.session_state.photo = None
    st.rerun()


def analyse(photo: Any, height_cm: float) -> dict:
    """Saves the photo to a temp file and returns the body measurements."""
    suffix = Path(getattr(photo, "name", "photo.jpg")).suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(photo.getvalue())
    try:
        return get_profiler().extract_measurements(tmp.name, height_cm)
    finally:
        Path(tmp.name).unlink(missing_ok=True)


def step_setup() -> None:
    st.markdown('<div class="app-title">FitMatch AI</div>', unsafe_allow_html=True)
    st.markdown("**Snap a photo, get your size.** Our AI measures your shoulders and chest, "
                "then finds your best fit at your favourite brand.")
    height = st.slider("Your real height (cm)", 140, 210, st.session_state.height_cm)
    brands = list_brands()
    brand = st.selectbox("Target brand", brands, index=brands.index(st.session_state.brand))
    if st.button("Next: How to Pose ➔", type="primary", use_container_width=True):
        st.session_state.height_cm, st.session_state.brand = height, brand
        go_to(2)


def step_pose_guide() -> None:
    st.title("📸 How to pose for accurate sizing")
    st.markdown("- Stand straight, facing the camera directly.\n"
                "- Keep your arms slightly away from your body (A-pose).\n"
                "- Ensure your head and feet are visible in the frame.")
    guide_path = Path(__file__).parent / "assets" / "pose_guide.png"
    if guide_path.is_file():
        st.image(str(guide_path), caption="Ideal pose for AI measurement")
    else:
        st.info("Reference photo coming soon - follow the steps above.")
    back, camera = st.columns(2)
    if back.button("⬅️ Back", use_container_width=True):
        go_to(1)
    if camera.button("Open Camera 📸", type="primary", use_container_width=True):
        go_to(3)


def step_capture() -> None:
    st.title("📷 Your photo")
    tab_camera, tab_upload = st.tabs(["📷 Take Photo", "📁 Upload Image"])
    with tab_camera:
        camera = st.camera_input("Stand straight, facing the camera")
    with tab_upload:
        uploaded = st.file_uploader("Choose a photo", type=["jpg", "jpeg", "png"])
    photo = camera or uploaded
    if photo is not None:
        st.session_state.photo = photo
        go_to(4)
    if st.button("⬅️ Back to Guide", use_container_width=True):
        go_to(2)


def step_results() -> None:
    brand, photo = st.session_state.brand, st.session_state.photo
    try:
        with st.spinner("Analysing your photo..."):
            measurements = analyse(photo, float(st.session_state.height_cm))
    except ValueError as exc:
        st.error(str(exc))
        if st.button("🔄 Try Again", type="primary", use_container_width=True):
            go_to(3, clear_photo=True)
        return
    result = recommend_size(measurements["chest_cm"], brand)
    st.subheader("✨ Your Results")
    st.image(photo, caption="Your photo", use_container_width=True)
    if not result["size"]:
        st.error(result["message"])
    else:
        with st.container(key="results-card"):
            st.success(f"Your recommended {brand} size is **{result['size']}**")
            c1, c2, c3 = st.columns(3)
            c1.metric("Size", result["size"])
            c2.metric("Chest (est.)", f"{measurements['chest_cm']} cm")
            c3.metric("Shoulders", f"{measurements['shoulder_cm']} cm")
        if result["boundary_warning"]:
            st.warning(result["boundary_warning"])
    if st.button("Start Over", use_container_width=True):
        go_to(1, clear_photo=True)


inject_css()
STEPS = {1: step_setup, 2: step_pose_guide, 3: step_capture, 4: step_results}
STEPS[st.session_state.step]()
