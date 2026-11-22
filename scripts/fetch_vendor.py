#!/usr/bin/env python3
"""Pobiera biblioteki mapy (Leaflet, Leaflet.markercluster) do web/vendor/.

Dzięki temu strona nie zależy w czasie działania od zewnętrznych CDN
(unpkg/jsdelivr bywają wolne lub zablokowane w niektórych sieciach).
Pliki są pobierane z rejestru npm w przypiętych wersjach, a ich integralność
jest sprawdzana sumą SHA-512 z metadanych rejestru.

Użycie:  python3 scripts/fetch_vendor.py
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "web" / "vendor"
REGISTRY = "https://registry.npmjs.org"

# pakiet, wersja, pliki z paczki (ścieżki względem package/dist/)
PACKAGES = [
    (
        "leaflet",
        "1.9.4",
        [
            "leaflet.js",
            "leaflet.css",
            "images/layers.png",
            "images/layers-2x.png",
            "images/marker-icon.png",
            "images/marker-icon-2x.png",
            "images/marker-shadow.png",
        ],
    ),
    ("leaflet.markercluster", "1.5.3", ["leaflet.markercluster.js", "MarkerCluster.css"]),
]


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "miejsca-pamieci/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 (stały, zaufany host)
        return resp.read()


def fetch(name: str, version: str, files: list[str]) -> None:
    target = VENDOR / name
    if all((target / f).exists() for f in files):
        print(f"  ✓ {name}@{version} (już pobrane)")
        return
    meta = json.loads(_get(f"{REGISTRY}/{name}/{version}"))
    tarball = _get(meta["dist"]["tarball"])
    algo, expected = meta["dist"]["integrity"].split("-", 1)
    actual = base64.b64encode(hashlib.new(algo, tarball).digest()).decode()
    if actual != expected:
        raise RuntimeError(f"{name}@{version}: suma kontrolna się nie zgadza")
    with tarfile.open(fileobj=io.BytesIO(tarball), mode="r:gz") as tar:
        for f in files:
            member = tar.extractfile(f"package/dist/{f}")
            if member is None:
                raise RuntimeError(f"{name}@{version}: brak pliku {f}")
            out = target / f
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(member.read())
    print(f"  ✓ {name}@{version} → web/vendor/{name}/")


def main() -> int:
    print("• Biblioteki mapy (npm) …", flush=True)
    try:
        for name, version, files in PACKAGES:
            fetch(name, version, files)
    except Exception as exc:  # pragma: no cover - zależne od sieci
        print(f"  ! Nie udało się pobrać bibliotek ({exc}). Strona użyje CDN jako zapasu.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
