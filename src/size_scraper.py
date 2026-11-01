import glob
import os
from pathlib import Path
from typing import Dict, List
from playwright.sync_api import sync_playwright

LOCAL_PAGE_NAME = "hm_test.html"
SIZE_SELECTORS: List[str] = [
    '[data-testid*="size" i]',
    '[class*="size" i]',
    '[id*="size" i]',
    '[aria-label*="taille" i]',
    "text=/GUIDE DES TAILLES/i",
]


def find_local_page() -> Path:
    """Returns the saved product page: the project root first, then any subfolder."""
    root_copy = Path(os.path.abspath(LOCAL_PAGE_NAME))
    if root_copy.exists():
        return root_copy
    matches = glob.glob(f"**/{LOCAL_PAGE_NAME}", recursive=True)
    matches = [m for m in matches if not m.startswith("venv")]
    if not matches:
        raise FileNotFoundError(f"Could not find {LOCAL_PAGE_NAME} in the project.")
    return Path(os.path.abspath(matches[0]))


def scrape_local_page(page_path: Path) -> Dict[str, str]:
    """Loads a saved product page in headless Chromium and returns its sizing text."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(page_path.as_uri(), wait_until="domcontentloaded")

            sizing_chunks: List[str] = []
            for selector in SIZE_SELECTORS:
                for text in page.locator(selector).all_inner_texts():
                    cleaned = text.strip()
                    if cleaned and cleaned not in sizing_chunks:
                        sizing_chunks.append(cleaned)

            return {
                "sizing_elements": "\n---\n".join(sizing_chunks),
                "full_page_text": page.inner_text("body"),
            }
        finally:
            browser.close()


if __name__ == "__main__":
    try:
        local_page = find_local_page()
        print(f"[System] Reading {local_page}")
        result = scrape_local_page(local_page)
        print("\n=== SIZING ELEMENTS ===")
        print(result["sizing_elements"] or "(none found)")
        print("\n=== FULL PAGE TEXT ===")
        print(result["full_page_text"] or "(page is empty)")
    except Exception as e:
        print(f"Error: {e}")
