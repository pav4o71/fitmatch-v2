import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.size_matcher import list_brands, recommend_size


def test_brands_present() -> None:
    assert {"H&M", "Zara", "Uniqlo"} <= set(list_brands())


def test_hm_mid_range_no_warning() -> None:
    result = recommend_size(98.0, "H&M")
    assert result["size"] == "M" and result["boundary_warning"] is None


def test_upper_boundary_warning() -> None:
    result = recommend_size(109.0, "H&M")
    assert result["size"] == "L" and "XL" in result["boundary_warning"]


def test_lower_boundary_warning() -> None:
    result = recommend_size(102.5, "H&M")
    assert result["size"] == "L" and "M" in result["boundary_warning"]


def test_out_of_range() -> None:
    assert recommend_size(60.0, "Zara")["size"] is None
    assert recommend_size(200.0, "Uniqlo")["size"] is None


def test_every_brand_resolves_fallback() -> None:
    for brand in list_brands():
        assert recommend_size(100.0, brand)["size"] is not None


def test_profiler_on_test_photo() -> None:
    from src.body_profiler import BodyProfiler
    photo = Path(__file__).resolve().parent.parent / "test_photo.jpg.JPG"
    out = BodyProfiler().extract_measurements(str(photo), 180.0)
    assert set(out) == {"shoulder_cm", "chest_cm"}
