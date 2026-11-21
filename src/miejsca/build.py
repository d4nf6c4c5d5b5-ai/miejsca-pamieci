"""Budowa zoptymalizowanego zbioru `places.json` dla aplikacji webowej."""

from __future__ import annotations

import gzip
import json
import time
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

from .categories import CATEGORIES, classify, mask
from .geo import Gazetteer, jitter

PREC_EXACT, PREC_LOCALITY, PREC_GMINA = 0, 1, 2
SRC_REGISTER, SRC_MONUMENTS = 0, 1

COLUMNS = [
    "id",
    "name",
    "func",
    "chron",
    "mask",
    "lat",
    "lon",
    "woj",
    "powiat",
    "gmina",
    "place",
    "addr",
    "prec",
    "src",
]


def build_gazetteer(rows: Iterable[dict[str, str]]) -> Gazetteer:
    gaz = Gazetteer()
    for r in rows:
        if r.get("kategoria", "miejscowość") != "miejscowość":
            continue
        gaz.add(r["nazwa"], r["rodzaj"], r["wsp"], r["woj"], r["powiat"], r["gmina"])
    return gaz


def _num(text: str) -> float | None:
    try:
        return float((text or "").replace(",", "."))
    except ValueError:
        return None


def _addr(ulica: str, nr: str) -> str:
    return " ".join(p for p in (ulica, nr) if p)


def build_places(
    register: Iterable[dict[str, str]], monuments: Iterable[dict[str, str]], gaz: Gazetteer
) -> tuple[list[list], dict]:
    rows: list[list] = []
    stats: Counter[str] = Counter()
    woj_index: dict[str, int] = {}

    def woj_id(name: str) -> int:
        return woj_index.setdefault(name, len(woj_index))

    for r in register:
        stats["rejestr_wszystkie"] += 1
        cats = classify(r.get("NAZWA", ""), r.get("FUNKCJA", ""), r.get("CHRONOLOGIA", ""))
        if not cats:
            continue
        stats["rejestr_miejsca_pamieci"] += 1
        hit = gaz.locate(r.get("WOJEWODZTWO", ""), r.get("POWIAT", ""), r.get("GMINA", ""), r.get("MIEJSCOWOSC", ""))
        if not hit:
            stats["bez_wspolrzednych"] += 1
            continue
        lat, lon, prec = hit
        lat, lon = jitter(lat, lon, r["INSPIRE_ID"], 400 if prec == "gmina" else 250)
        stats[f"precyzja_{prec}"] += 1
        for c in cats:
            stats[f"kat_{c}"] += 1
        rows.append(
            [
                r["INSPIRE_ID"],
                r.get("NAZWA", ""),
                r.get("FUNKCJA", ""),
                r.get("CHRONOLOGIA", ""),
                mask(cats),
                lat,
                lon,
                woj_id(r.get("WOJEWODZTWO", "")),
                r.get("POWIAT", ""),
                r.get("GMINA", ""),
                r.get("MIEJSCOWOSC", ""),
                _addr(r.get("ULICA", ""), r.get("NR_ADRESOWY", "")),
                PREC_LOCALITY if prec == "miejscowosc" else PREC_GMINA,
                SRC_REGISTER,
            ]
        )

    for r in monuments:
        lon, lat = _num(r.get("E", "")), _num(r.get("N", ""))
        if lat is None or lon is None:
            stats["pomniki_bez_wspolrzednych"] += 1
            continue
        cats = sorted(
            set(classify(r.get("NAZWA", ""), r.get("RODZAJ_POMNIKA_HISTORII", ""))) | {"pomnik_historii"},
            key=[c.key for c in CATEGORIES].index,
        )
        stats["pomniki_historii"] += 1
        rows.append(
            [
                r["INSPIRE_ID"],
                r.get("NAZWA", ""),
                r.get("RODZAJ_POMNIKA_HISTORII", ""),
                r.get("DATA_WPISU", ""),
                mask(cats),
                round(lat, 5),
                round(lon, 5),
                woj_id(r.get("WOJEWODZTWO", "")),
                r.get("POWIAT", ""),
                r.get("GMINA", ""),
                r.get("MIEJSCOWOSC", ""),
                _addr(r.get("ULICA", ""), r.get("NR_ADRESOWY", "")),
                PREC_EXACT,
                SRC_MONUMENTS,
            ]
        )

    # Sortowanie po geohashu-light (siatka 0.5°) poprawia kompresję i lokalność danych.
    rows.sort(key=lambda x: (round(x[5] * 2), round(x[6] * 2), x[1]))
    voivodeships = [name for name, _ in sorted(woj_index.items(), key=lambda kv: kv[1])]
    return rows, {"stats": dict(stats), "voivodeships": voivodeships}


def write_output(rows: list[list], extra: dict, sources_meta: list[dict], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sources": sources_meta,
        "categories": [c.__dict__ for c in CATEGORIES],
        "voivodeships": extra["voivodeships"],
        "stats": extra["stats"],
        "columns": COLUMNS,
        "rows": rows,
    }
    target = out_dir / "places.json"
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    target.write_bytes(data)
    # Wersja .gz dla serwerów, które potrafią podać plik prekompresowany.
    (out_dir / "places.json.gz").write_bytes(gzip.compress(data, compresslevel=9))
    return target
