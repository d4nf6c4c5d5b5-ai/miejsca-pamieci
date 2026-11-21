"""Pobieranie zbiorów z API dane.gov.pl.

Adresy plików zmieniają się przy każdej aktualizacji zbioru, dlatego nie są
wpisane na sztywno: pytamy API o listę zasobów zbioru i wybieramy właściwy
po tytule i formacie.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

API_URL = os.environ.get("DANE_API_URL", "https://api.dane.gov.pl/1.4").rstrip("/")
USER_AGENT = "miejsca-pamieci/1.0 (+https://github.com/; open-source)"
TIMEOUT = int(os.environ.get("HTTP_TIMEOUT", "120"))


@dataclass(frozen=True)
class Source:
    key: str
    dataset_id: int
    title_pattern: str
    fmt: str
    filename: str
    description: str


SOURCES: list[Source] = [
    Source(
        "rejestr",
        1130,
        r"plik CSV",
        "csv",
        "rejestr_zabytkow_nieruchomych.csv",
        "Rejestr zabytków nieruchomych — Narodowy Instytut Dziedzictwa",
    ),
    Source(
        "pomniki", 168, r"plik CSV", "csv", "pomniki_historii.csv", "Pomniki historii — Narodowy Instytut Dziedzictwa"
    ),
    Source(
        "prng",
        780,
        r"miejscowości.*XLSX",
        "zip",
        "prng_miejscowosci_xlsx.zip",
        "Państwowy Rejestr Nazw Geograficznych — miejscowości (GUGiK)",
    ),
]


def _get(url: str) -> urllib.request.addinfourl:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    last: Exception | None = None
    for attempt in range(4):
        try:
            return urllib.request.urlopen(req, timeout=TIMEOUT)  # noqa: S310 (stały, zaufany host)
        except Exception as exc:  # pragma: no cover - zależne od sieci
            last = exc
            time.sleep(2**attempt)
    raise RuntimeError(f"Nie udało się pobrać {url}: {last}")


def resource_info(source: Source) -> dict:
    """Zwraca metadane zasobu (adres pliku, datę danych) z API dane.gov.pl."""
    with _get(f"{API_URL}/datasets/{source.dataset_id}/resources?per_page=100") as resp:
        payload = json.load(resp)
    rx = re.compile(source.title_pattern, re.IGNORECASE)
    for item in payload.get("data", []):
        attrs = item.get("attributes", {})
        # `link` wskazuje aktualny plik u wydawcy (np. GUGiK publikuje PRNG co tydzień),
        # `download_url` to kopia/przekierowanie w dane.gov.pl — używane jako zapas.
        url = attrs.get("link") or attrs.get("download_url") or attrs.get("file_url") or ""
        if rx.search(attrs.get("title", "")) and (attrs.get("format") or "").lower() == source.fmt:
            return {
                "resource_id": item.get("id"),
                "title": attrs.get("title"),
                "url": url,
                "fallback_url": attrs.get("download_url"),
                "data_date": attrs.get("data_date"),
                "dataset_url": f"https://dane.gov.pl/pl/dataset/{source.dataset_id}",
            }
    raise LookupError(f"Nie znaleziono zasobu '{source.title_pattern}' w zbiorze {source.dataset_id}")


def download(source: Source, raw_dir: Path, force: bool = False) -> tuple[Path, dict]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    target = raw_dir / source.filename
    meta_path = raw_dir / f"{source.filename}.meta.json"
    if target.exists() and meta_path.exists() and not force:
        return target, json.loads(meta_path.read_text(encoding="utf-8"))
    info = resource_info(source)
    tmp = target.with_suffix(target.suffix + ".part")
    try:
        resp = _get(info["url"])
    except RuntimeError:
        if not info.get("fallback_url"):
            raise
        resp = _get(info["fallback_url"])
    with resp, open(tmp, "wb") as out:
        shutil.copyfileobj(resp, out, length=1 << 20)
    tmp.replace(target)
    info["downloaded_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    info["bytes"] = target.stat().st_size
    meta_path.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    return target, info
