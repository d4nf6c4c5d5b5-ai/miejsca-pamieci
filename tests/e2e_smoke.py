"""Test end-to-end w prawdziwej przeglądarce (Chromium, Playwright).

Uruchamiany w CI po zbudowaniu próbki danych i pobraniu Leafleta:
    python scripts/fetch_vendor.py && python scripts/fetch_data.py --sample
    python tests/e2e_smoke.py

Sprawdza, że strona się ładuje, mapa i lista działają, wyszukiwarka filtruje,
a przycisk „Losuj miejsce” otwiera kartę obiektu. Nie korzysta z internetu
poza kafelkami mapy (te mogą się nie wczytać — test ich nie wymaga).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PORT = 8765
URL = f"http://127.0.0.1:{PORT}/"


def wait_for_server(timeout: float = 15) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(URL, timeout=1)  # noqa: S310 (lokalny serwer testowy)
            return
        except OSError:
            time.sleep(0.2)
    raise RuntimeError("Serwer nie wystartował")


def main() -> int:
    server = subprocess.Popen(  # noqa: S603
        [sys.executable, "scripts/serve.py", "--host", "127.0.0.1", "--port", str(PORT)], cwd=ROOT
    )
    errors: list[str] = []
    try:
        wait_for_server()
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
            for name, viewport in (
                ("desktop", {"width": 1280, "height": 800}),
                ("mobile", {"width": 390, "height": 844}),
            ):
                page = browser.new_page(viewport=viewport)
                page.on("pageerror", lambda e, n=name: errors.append(f"{n}: {e}"))
                page.goto(URL)

                count = page.locator("#count")
                expect(count).to_contain_text("na mapie", timeout=15000)
                expect(page.locator("#perf")).to_contain_text("Mapa gotowa")
                expect(page.locator(".leaflet-container")).to_be_visible()
                assert page.locator("#results li").count() > 0, "pusta lista wyników"

                page.fill("#q", "oswiecim")
                expect(count).to_contain_text("na mapie")
                # wyszukiwanie ma debounce — czekamy, aż stan trafi do adresu URL
                page.wait_for_function("location.hash.includes('q=oswiecim')", timeout=5000)
                page.fill("#q", "")
                page.wait_for_function("!location.hash.includes('q=')", timeout=5000)

                page.click("#random")
                expect(page.locator(".leaflet-popup-content .plaque-name")).to_be_visible(timeout=10000)
                print(f"✓ {name}: {count.inner_text()}, losowe: {page.locator('.plaque-name').inner_text()}")
                page.close()
            browser.close()
    finally:
        server.terminate()
    if errors:
        print("Błędy JavaScript:", *errors, sep="\n  ")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
