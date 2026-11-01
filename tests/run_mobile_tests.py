"""Local QA: drives the Streamlit wizard on an emulated iPhone 13 with each image in test_images/."""
from pathlib import Path
from typing import List, Tuple

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

APP_URL = "http://localhost:8501"
IMAGE_DIR = Path(__file__).resolve().parent.parent / "test_images"
GATE_ERROR = "We couldn't clearly see your shoulders or hips"
NO_PERSON_ERROR = "No person detected"
RESULTS_MARKER = "Your Results"


def collect_images() -> List[Path]:
    """Returns every .jpg/.JPG/.png image in test_images/, sorted by name."""
    images = {p for p in IMAGE_DIR.iterdir() if p.suffix.lower() in {".jpg", ".png"}}
    return sorted(images)


def classify(page: Page) -> str:
    """Waits up to 5 s for an outcome and returns it as a label."""
    outcome = "TIMEOUT - no result or error appeared"
    try:
        page.wait_for_function(
            "markers => markers.some(t => document.body.innerText.includes(t))",
            arg=[GATE_ERROR, NO_PERSON_ERROR, RESULTS_MARKER],
            timeout=5000,
        )
    except PlaywrightTimeoutError:
        return outcome
    text = page.inner_text("body")
    if GATE_ERROR in text:
        return "REJECTED - Caught by Quality Gate (shoulders/hips)"
    if NO_PERSON_ERROR in text:
        return "REJECTED - Caught by Quality Gate (no person)"
    return "PASS - Size Generated"


def run_image(playwright, image: Path) -> str:
    """Runs the full wizard flow for one image in a fresh mobile context."""
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(**playwright.devices["iPhone 13"])
    page = context.new_page()
    try:
        page.goto(APP_URL)
        page.get_by_role("button", name="Next: How to Pose ➔").click()
        page.wait_for_timeout(1500)
        page.get_by_role("button", name="Open Camera 📸").click()
        page.wait_for_timeout(1500)
        page.locator('input[type="file"]').first.set_input_files(str(image))
        return classify(page)
    except Exception as exc:
        return f"ERROR - {type(exc).__name__}: {str(exc).splitlines()[0]}"
    finally:
        context.close()
        browser.close()


def main() -> None:
    results: List[Tuple[str, str]] = []
    with sync_playwright() as playwright:
        for image in collect_images():
            outcome = run_image(playwright, image)
            tag = "PASS - Size Generated" if outcome.startswith("PASS") else outcome
            print(f"[{tag}] {image.name}", flush=True)
            results.append((image.name, outcome))
    print("\n=== SUMMARY ===")
    for name, outcome in results:
        print(f"{name}: {outcome}")


if __name__ == "__main__":
    main()
