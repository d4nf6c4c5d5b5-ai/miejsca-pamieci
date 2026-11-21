"""Testy potoku danych. Uruchomienie: `python -m unittest discover -s tests -v`."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from make_fixtures import write_prng_fixture  # noqa: E402
from miejsca.build import COLUMNS, build_gazetteer, build_places, write_output  # noqa: E402
from miejsca.categories import BIT, CATEGORY_KEYS, classify, years  # noqa: E402
from miejsca.geo import Gazetteer, gmina_base_nid, gmina_base_prng, jitter, parse_dms  # noqa: E402
from miejsca.readers import read_monuments_of_history, read_nid_register, read_prng_localities  # noqa: E402

FIX = ROOT / "tests" / "fixtures"


def prng_path() -> Path:
    path = FIX / "prng_sample.zip"
    if not path.exists():
        write_prng_fixture(path)
    return path


class TestCategories(unittest.TestCase):
    def test_camps(self):
        self.assertIn("obozy", classify("teren po Stalagu VIII B (344) Lamsdorf", "obóz koncentracyjny"))
        self.assertIn("obozy", classify("obóz koncentracyjny Auschwitz-Birkenau", "obóz koncentracyjny"))

    def test_world_wars_are_distinguished(self):
        ww1 = classify("cmentarz wojenny nr 87 z I wojny światowej", "cmentarz I wojna światowa")
        ww2 = classify("cmentarz wojenny z II wojny światowej", "cmentarz II wojna światowa")
        self.assertIn("ww1", ww1)
        self.assertNotIn("ww2", ww1)
        self.assertIn("ww2", ww2)
        self.assertNotIn("ww1", ww2)

    def test_both_wars(self):
        cats = classify("cmentarz wojenny z I i II wojny światowej", "cmentarz I wojna światowa")
        self.assertIn("ww1", cats)
        self.assertIn("ww2", cats)

    def test_jewish_heritage(self):
        self.assertEqual(classify("synagoga", "synagoga"), ["zydowskie"])
        self.assertIn("zydowskie", classify("kirkut", "cmentarz żydowski"))

    def test_bunker_gets_ww2_from_chronology(self):
        cats = classify("schron bojowy nr 8 typu Ringstand 58c", "schron", "1944 - 1945")
        self.assertEqual(cats, ["ww2", "fortyfikacje"])

    def test_forts_with_inflection(self):
        self.assertIn("fortyfikacje", classify("Bastion Fortu Owcza Góra", "bastion"))
        self.assertIn("fortyfikacje", classify("Fort III Dęblin", "zespół - fort"))

    def test_false_positives_are_excluded(self):
        self.assertEqual(classify("schronisko Samotnia", "schronisko turystyczne"), [])
        self.assertEqual(classify("park pałacowy", "park"), [])
        self.assertEqual(classify("willa zarządu fabryki fortepianów", "willa"), [])
        self.assertEqual(classify("pomnik nagrobny Piotra i Tekli", "pomnik"), [])
        self.assertEqual(classify("kościół pw. św. Michała", "kościół"), [])
        # Grobowce rodzinne i figury religijne to nie miejsca pamięci w sensie tego projektu.
        self.assertEqual(classify("kaplica grobowa rodziny Stadnickich", "mauzoleum"), [])
        self.assertEqual(classify("pomnik Św. Trójcy", "obelisk/kolumna"), [])
        # …ale pomnik bitwy już tak.
        self.assertIn("pamiec", classify("pomnik upamiętniający Bitwę pod Kijami", "pomnik"))

    def test_order_follows_priority(self):
        cats = classify("mogiła zbiorowa Polaków z Polen Lager", "cmentarz II wojna światowa")
        self.assertEqual(cats, sorted(cats, key=CATEGORY_KEYS.index))
        self.assertEqual(cats[0], "obozy")

    def test_years(self):
        self.assertEqual(years("1914 - 1918"), (1914, 1918))
        self.assertEqual(years("2. poł. XIX w."), None)

    def test_bits_unique(self):
        self.assertEqual(len(set(BIT.values())), len(CATEGORY_KEYS))


class TestGeo(unittest.TestCase):
    def test_parse_dms(self):
        lat, lon = parse_dms("50°43'05\" 16°39'17\"")
        self.assertAlmostEqual(lat, 50.71806, places=4)
        self.assertAlmostEqual(lon, 16.65472, places=4)
        self.assertIsNone(parse_dms(""))
        self.assertIsNone(parse_dms("10°00'00\" 10°00'00\""))  # poza Polską

    def test_gmina_names(self):
        self.assertEqual(gmina_base_nid("Dzierżoniów (gm. miejska)"), "dzierżoniów")
        self.assertEqual(gmina_base_nid("Słomniki - obszar wiejski"), "słomniki")
        self.assertEqual(gmina_base_nid("Cieszanów - miasto"), "cieszanów")
        self.assertEqual(gmina_base_prng("Słomniki-gmina miejsko-wiejska"), "słomniki")
        self.assertEqual(gmina_base_prng("Bielsko-Biała-gmina miejska"), "bielsko-biała")

    def test_disambiguation_by_gmina(self):
        gaz = build_gazetteer(read_prng_localities(prng_path()))
        # Dwie wsie „Bielice” w opolskim — wybieramy tę z gminy Łambinowice.
        lat, lon, prec = gaz.locate("opolskie", "nyski", "Łambinowice", "Bielice")
        self.assertAlmostEqual(lat, 50.557, places=2)
        self.assertEqual(prec, "miejscowosc")
        # Dwa „Niedźwiedzie” w małopolskim — gmina Słomniki.
        lat, _, _ = gaz.locate("małopolskie", "krakowski", "Słomniki - obszar wiejski", "Niedźwiedź")
        self.assertAlmostEqual(lat, 50.224, places=2)

    def test_ambiguous_without_gmina_returns_none(self):
        gaz = Gazetteer()
        gaz.add("Abisynia", "wieś", "51°53'15\" 17°49'23\"", "wielkopolskie", "pleszewski", "Pleszew-gmina wiejska")
        gaz.add("Abisynia", "wieś", "52°53'15\" 17°49'23\"", "wielkopolskie", "inny", "Inna-gmina wiejska")
        self.assertIsNone(gaz.locate("wielkopolskie", "", "", "Abisynia"))

    def test_jitter_is_small_and_deterministic(self):
        a = jitter(52.0, 21.0, "id-1")
        self.assertEqual(a, jitter(52.0, 21.0, "id-1"))
        self.assertLess(abs(a[0] - 52.0), 0.01)
        self.assertLess(abs(a[1] - 21.0), 0.01)


class TestReaders(unittest.TestCase):
    def test_nid_cp1250(self):
        rows = list(read_nid_register(FIX / "rejestr_sample.csv"))
        self.assertEqual(len(rows), 14)
        self.assertEqual(rows[3]["NAZWA"], "synagoga")
        self.assertEqual(rows[3]["MIEJSCOWOSC"], "Dzierżoniów")

    def test_monuments(self):
        rows = list(read_monuments_of_history(FIX / "pomniki_sample.csv"))
        self.assertEqual(rows[1]["NAZWA"], "Pole Bitwy na Westerplatte")
        self.assertEqual(rows[1]["N"], "54,40806763")

    def test_prng_columns(self):
        rows = list(read_prng_localities(prng_path()))
        self.assertEqual(len(rows), 20)
        self.assertEqual(set(rows[0]), {"nazwa", "kategoria", "rodzaj", "wsp", "woj", "powiat", "gmina"})


class TestBuild(unittest.TestCase):
    def test_end_to_end(self):
        gaz = build_gazetteer(read_prng_localities(prng_path()))
        rows, extra = build_places(
            read_nid_register(FIX / "rejestr_sample.csv"), read_monuments_of_history(FIX / "pomniki_sample.csv"), gaz
        )
        names = {r[1] for r in rows}
        self.assertIn("synagoga", names)
        self.assertIn("Pole Bitwy na Westerplatte", names)
        self.assertNotIn("schronisko Samotnia", names)
        self.assertNotIn("park pałacowy", names)
        self.assertEqual(extra["stats"].get("bez_wspolrzednych", 0), 0)
        for r in rows:
            self.assertEqual(len(r), len(COLUMNS))
            self.assertTrue(49 < r[5] < 55 and 14 < r[6] < 24.5)

        with tempfile.TemporaryDirectory() as tmp:
            target = write_output(rows, extra, [], Path(tmp))
            payload = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(payload["columns"], COLUMNS)
            self.assertEqual(len(payload["rows"]), len(rows))
            self.assertTrue((Path(tmp) / "places.json.gz").exists())


if __name__ == "__main__":
    unittest.main()
