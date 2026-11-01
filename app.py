import tempfile
from pathlib import Path

import streamlit as st

from src.body_profiler import BodyProfiler
from src.size_matcher import list_brands, recommend_size

st.set_page_config(page_title="FitMatch - AI Size Recommendation", layout="wide")


@st.cache_resource
def get_profiler() -> BodyProfiler:
    """Loads the MediaPipe model once per server process."""
    return BodyProfiler()


st.title("FitMatch")
st.caption("Upload a full-body or upper-body photo and get your size for the brand you want.")

left, right = st.columns(2)
with left:
    uploaded = st.file_uploader("Your photo (stand straight, facing the camera)", type=["jpg", "jpeg", "png"])
    camera = st.camera_input("...or take a photo")
    height_cm = st.slider("Your real height (cm)", 140, 210, 175)
    brand = st.selectbox("Target brand", list_brands())

photo = uploaded or camera
with right:
    if photo is None:
        st.info("Add a photo to get started.")
    else:
        st.image(photo, width=300)
        suffix = Path(getattr(photo, "name", "photo.jpg")).suffix or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(photo.getvalue())
        try:
            with st.spinner("Analysing your photo..."):
                measurements = get_profiler().extract_measurements(tmp.name, float(height_cm))
            result = recommend_size(measurements["chest_cm"], brand)
            if result["size"]:
                st.success(f"Your recommended {brand} size: {result['size']}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Chest (est.)", f"{measurements['chest_cm']} cm")
                col2.metric("Shoulders", f"{measurements['shoulder_cm']} cm")
                col3.metric(f"{brand} size", result["size"])
                if result["boundary_warning"]:
                    st.warning(result["boundary_warning"])
            else:
                st.error(result["message"])
        except (ValueError, FileNotFoundError) as exc:
            st.error(str(exc))
        finally:
            Path(tmp.name).unlink(missing_ok=True)
