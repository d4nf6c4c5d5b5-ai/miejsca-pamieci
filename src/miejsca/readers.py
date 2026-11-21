"""Czytniki surowych plików z dane.gov.pl (tylko biblioteka standardowa Pythona)."""

from __future__ import annotations

import csv
import io
import zipfile
from collections.abc import Iterator
from pathlib import Path
from xml.etree.ElementTree import iterparse

# Pliki CSV Narodowego Instytutu Dziedzictwa są w kodowaniu Windows-1250.
NID_ENCODING = "cp1250"


def _open_text(path: Path, encoding: str) -> io.TextIOWrapper:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return io.TextIOWrapper(io.BytesIO(raw[3:]), encoding="utf-8", newline="")
    try:
        raw.decode("utf-8")
        enc = "utf-8"
    except UnicodeDecodeError:
        enc = encoding
    return io.TextIOWrapper(io.BytesIO(raw), encoding=enc, newline="")


def read_nid_register(path: Path) -> Iterator[dict[str, str]]:
    """Rejestr zabytków nieruchomych (dane.gov.pl, zbiór 1130)."""
    with _open_text(path, NID_ENCODING) as fh:
        for row in csv.DictReader(fh, delimiter=";", quotechar='"'):
            yield {k.strip(): (v or "").strip() for k, v in row.items() if k}


def read_monuments_of_history(path: Path) -> Iterator[dict[str, str]]:
    """Pomniki Historii (dane.gov.pl, zbiór 168) — mają własne współrzędne E/N."""
    with _open_text(path, NID_ENCODING) as fh:
        for row in csv.DictReader(fh, delimiter=";", quotechar='"'):
            yield {k.strip(): (v or "").strip() for k, v in row.items() if k}


# --- PRNG: XLSX spakowany w ZIP, czytany strumieniowo ---------------------------------

_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
PRNG_COLUMNS = {
    "nazwa główna": "nazwa",
    "kategoria obiektu": "kategoria",
    "rodzaj obiektu": "rodzaj",
    "współrzędne geograficzne": "wsp",
    "województwo": "woj",
    "powiat": "powiat",
    "gmina": "gmina",
}


def _col_index(ref: str) -> int:
    letters = "".join(ch for ch in ref if ch.isalpha())
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch) - 64)
    return idx - 1


def _shared_strings(xlsx: zipfile.ZipFile) -> list[str]:
    names = [n for n in xlsx.namelist() if n.endswith("sharedStrings.xml")]
    if not names:
        return []
    strings: list[str] = []
    with xlsx.open(names[0]) as fh:
        for _, elem in iterparse(fh, events=("end",)):
            if elem.tag == f"{_NS}si":
                strings.append("".join(t.text or "" for t in elem.iter(f"{_NS}t")))
                elem.clear()
    return strings


def _open_xlsx(path: Path) -> zipfile.ZipFile:
    """Przyjmuje .xlsx albo .zip zawierający jeden .xlsx (tak publikuje GUGiK)."""
    outer = zipfile.ZipFile(path)
    if any(n.startswith("xl/") for n in outer.namelist()):
        return outer
    inner = next(n for n in outer.namelist() if n.lower().endswith(".xlsx") and "legenda" not in n.lower())
    return zipfile.ZipFile(io.BytesIO(outer.read(inner)))


def read_prng_localities(path: Path) -> Iterator[dict[str, str]]:
    """Miejscowości z PRNG (dane.gov.pl, zbiór 780) — tylko potrzebne kolumny."""
    xlsx = _open_xlsx(path)
    strings = _shared_strings(xlsx)
    sheet = next(n for n in xlsx.namelist() if n.startswith("xl/worksheets/sheet"))
    wanted: dict[int, str] = {}
    with xlsx.open(sheet) as fh:
        for _, elem in iterparse(fh, events=("end",)):
            if elem.tag != f"{_NS}row":
                continue
            values: dict[int, str] = {}
            for cell in elem.iter(f"{_NS}c"):
                idx = _col_index(cell.get("r", ""))
                if wanted and idx not in wanted:
                    continue
                kind = cell.get("t")
                if kind == "inlineStr":
                    text = "".join(t.text or "" for t in cell.iter(f"{_NS}t"))
                else:
                    v = cell.find(f"{_NS}v")
                    text = "" if v is None or v.text is None else v.text
                    if kind == "s" and text:
                        text = strings[int(text)]
                values[idx] = text
            elem.clear()
            if not wanted:
                wanted = {i: PRNG_COLUMNS[h.strip()] for i, h in values.items() if h.strip() in PRNG_COLUMNS}
                missing = set(PRNG_COLUMNS.values()) - set(wanted.values())
                if missing:
                    raise ValueError(f"PRNG: brak kolumn {sorted(missing)}")
                continue
            yield {name: values.get(i, "") for i, name in wanted.items()}
