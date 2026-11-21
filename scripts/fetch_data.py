#!/usr/bin/env python3
"""Pobiera dane z API dane.gov.pl i buduje web/data/places.json.

Użycie:
    python scripts/fetch_data.py            # pobierz (jeśli brak) i zbuduj
    python scripts/fetch_data.py --force    # wymuś ponowne pobranie
    python scripts/fetch_data.py --sample   # zbuduj z próbki w tests/fixtures (bez internetu)

Wymaga tylko Pythona 3.10+ (biblioteka standardowa).
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from miejsca.build import build_gazetteer, build_places, write_output  # noqa: E402
from miejsca.readers import read_monuments_of_history, read_nid_register, read_prng_localities  # noqa: E402
from miejsca.sources import SOURCES, download  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="pobierz pliki ponownie")
    parser.add_argument("--sample", action="store_true", help="użyj próbki z tests/fixtures (offline)")
    parser.add_argument("--raw-dir", type=Path, default=Path(os.environ.get("DATA_DIR", ROOT / "data" / "raw")))
    parser.add_argument("--out-dir", type=Path, default=Path(os.environ.get("OUTPUT_DIR", ROOT / "web" / "data")))
    args = parser.parse_args()

    t0 = time.perf_counter()
    if args.sample:
        paths = {
            "rejestr": FIXTURES / "rejestr_sample.csv",
            "pomniki": FIXTURES / "pomniki_sample.csv",
            "prng": FIXTURES / "prng_sample.zip",
        }
        if not paths["prng"].exists():
            sys.path.insert(0, str(ROOT / "tests"))
            from make_fixtures import write_prng_fixture  # noqa: PLC0415

            write_prng_fixture(paths["prng"])
        meta = [{"key": k, "title": f"próbka testowa ({p.name})", "dataset_url": None} for k, p in paths.items()]
    else:
        paths, meta = {}, []
        for source in SOURCES:
            print(f"↓ {source.description} (zbiór {source.dataset_id}) …", flush=True)
            path, info = download(source, args.raw_dir, force=args.force)
            paths[source.key] = path
            meta.append({"key": source.key, "dataset_id": source.dataset_id, "description": source.description, **info})
            print(f"  ✓ {path.name}: {path.stat().st_size / 1e6:.1f} MB", flush=True)

    print("• Indeks miejscowości PRNG …", flush=True)
    gaz = build_gazetteer(read_prng_localities(paths["prng"]))
    print(f"  ✓ {len(gaz):,} kluczy miejscowości", flush=True)

    print("• Klasyfikacja i geokodowanie rejestru zabytków …", flush=True)
    rows, extra = build_places(read_nid_register(paths["rejestr"]), read_monuments_of_history(paths["pomniki"]), gaz)
    target = write_output(rows, extra, meta, args.out_dir)

    s = extra["stats"]
    found = s.get("rejestr_miejsca_pamieci", 0)
    located = found - s.get("bez_wspolrzednych", 0)
    print(f"  ✓ miejsca pamięci w rejestrze: {found:,} z {s.get('rejestr_wszystkie', 0):,} zabytków")
    print(f"  ✓ zlokalizowane: {located:,} ({located / max(found, 1):.1%})")
    print(f"  ✓ pomniki historii: {s.get('pomniki_historii', 0)}")
    print(f"✔ {target} ({target.stat().st_size / 1e3:.0f} kB) w {time.perf_counter() - t0:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
