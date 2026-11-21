"""Generuje małą próbkę PRNG w tym samym formacie co GUGiK (ZIP → XLSX → sharedStrings).

Wiersze są prawdziwymi rekordami PRNG (stan 2026-11) dla miejscowości z próbek
rejestru zabytków. Plik binarny nie jest trzymany w repozytorium — tworzy go
ten skrypt (`python tests/make_fixtures.py`) albo testy przy pierwszym uruchomieniu.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

HEADER = [
    "identyfikator IIP",
    "identyfikator PRNG",
    "nazwa główna",
    "element rozróżniający",
    "element rodzajowy",
    "dopełniacz",
    "przymiotnik",
    "status nazwy",
    "kategoria obiektu",
    "rodzaj obiektu",
    "nazwa miejscowości nadrzędnej",
    "identyfikator miejscowości nadrzędnej",
    "informacje dodatkowe",
    "system zewnętrzny",
    "identyfikator zewnętrzny",
    "tytuł dokumentu źródłowego",
    "data dokumentu źródłowego",
    "wydawca dokumentu źródłowego",
    "rodzaj reprezentacji",
    "współrzędne geograficzne",
    "współrzędne prostokątne XY",
    "nazwa historyczna",
    "nazwa oboczna",
    "nazwa dodatkowa",
    "język nazwy dodatkowej",
    "latynizacja nazwy dodatkowej",
    "endonim",
    "język endonimu",
    "latynizacja endonimu",
    "egzonim",
    "język egzonimu",
    "latynizacja egzonimu",
    "województwo",
    "powiat",
    "gmina",
    "identyfikator gminy",
    "początek wersji obiektu",
    "wersja obiektu",
    "ważna od",
]

# nazwa, rodzaj, współrzędne, województwo, powiat, gmina
LOCALITIES = [
    (
        "Aleksandrów Kujawski",
        "miasto",
        "52°52'36\" 18°41'36\"",
        "kujawsko-pomorskie",
        "aleksandrowski",
        "Aleksandrów Kujawski-gmina miejska",
    ),
    ("Bielice", "wieś", "50°54'54\" 17°43'35\"", "opolskie", "namysłowski", "Świerczów-gmina wiejska"),
    ("Bielice", "wieś", "50°33'25\" 17°29'39\"", "opolskie", "nyski", "Łambinowice-gmina wiejska"),
    ("Bierawa", "wieś", "50°16'48\" 18°14'30\"", "opolskie", "kędzierzyńsko-kozielski", "Bierawa-gmina wiejska"),
    (
        "Dąbrowa Bolesławiecka",
        "wieś",
        "51°19'33\" 15°34'44\"",
        "dolnośląskie",
        "bolesławiecki",
        "Bolesławiec-gmina wiejska",
    ),
    ("Dęblin", "miasto", "51°33'41\" 21°50'34\"", "lubelskie", "rycki", "Dęblin-gmina miejska"),
    ("Dzierżoniów", "miasto", "50°43'45\" 16°38'56\"", "dolnośląskie", "dzierżoniowski", "Dzierżoniów-gmina miejska"),
    ("Głogów", "miasto", "51°39'54\" 16°04'53\"", "dolnośląskie", "głogowski", "Głogów-gmina miejska"),
    ("Głogów", "wieś", "51°24'44\" 20°51'14\"", "mazowieckie", "przysuski", "Wieniawa-gmina wiejska"),
    ("Gorlice", "miasto", "49°39'17\" 21°09'35\"", "małopolskie", "gorlicki", "Gorlice-gmina miejska"),
    ("Jawor", "miasto", "51°03'03\" 16°11'35\"", "dolnośląskie", "jaworski", "Jawor-gmina miejska"),
    ("Jawor", "wieś", "51°35'35\" 17°20'06\"", "dolnośląskie", "milicki", "Cieszków-gmina wiejska"),
    ("Karpacz", "miasto", "50°46'28\" 15°45'17\"", "dolnośląskie", "karkonoski", "Karpacz-gmina miejska"),
    ("Luboń", "miasto", "52°20'45\" 16°52'39\"", "wielkopolskie", "poznański", "Luboń-gmina miejska"),
    ("Luboń", "wieś", "54°01'32\" 17°29'29\"", "pomorskie", "bytowski", "Lipnica-gmina wiejska"),
    ("Niedźwiedź", "wieś", "50°13'26\" 20°05'36\"", "małopolskie", "krakowski", "Słomniki-gmina miejsko-wiejska"),
    ("Niedźwiedź", "wieś", "49°37'17\" 20°04'48\"", "małopolskie", "limanowski", "Niedźwiedź-gmina wiejska"),
    ("Oświęcim", "miasto", "50°02'17\" 19°13'15\"", "małopolskie", "oświęcimski", "Oświęcim-gmina miejska"),
    ("Oświęcim", "wieś", "51°25'12\" 18°11'41\"", "wielkopolskie", "ostrzeszowski", "Doruchów-gmina wiejska"),
    ("Warszawa", "miasto", "52°13'47\" 21°00'42\"", "mazowieckie", "Warszawa", "Warszawa-gmina miejska"),
]


def _col(i: int) -> str:
    name = ""
    i += 1
    while i:
        i, rem = divmod(i - 1, 26)
        name = chr(65 + rem) + name
    return name


def _xlsx_bytes() -> bytes:
    strings: list[str] = []
    index: dict[str, int] = {}

    def sid(text: str) -> int:
        if text not in index:
            index[text] = len(strings)
            strings.append(text)
        return index[text]

    rows = [HEADER]
    for n, (nazwa, rodzaj, wsp, woj, powiat, gmina) in enumerate(LOCALITIES, start=1):
        row = [""] * len(HEADER)
        row[0], row[1], row[2] = f"PL.PZGiK.320.NGRP.{n}", str(n), nazwa
        row[8], row[9], row[19] = "miejscowość", rodzaj, wsp
        row[32], row[33], row[34] = woj, powiat, gmina
        rows.append(row)

    xml_rows = []
    for r, row in enumerate(rows, start=1):
        cells = []
        for c, value in enumerate(row):
            ref = f"{_col(c)}{r}"
            if value == "":
                cells.append(f'<c r="{ref}" s="1"/>')
            elif r > 1 and c == 1:
                cells.append(f'<c r="{ref}" s="1"><v>{value}</v></c>')
            else:
                cells.append(f'<c r="{ref}" s="1" t="s"><v>{sid(value)}</v></c>')
        xml_rows.append(f'<row r="{r}">{"".join(cells)}</row>')

    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    sheet = f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="{ns}"><sheetData>{"".join(xml_rows)}</sheetData></worksheet>'
    sst = "".join(f"<si><t>{escape(s)}</t></si>" for s in strings)
    shared = f'<?xml version="1.0" encoding="UTF-8"?><sst xmlns="{ns}" count="{len(strings)}" uniqueCount="{len(strings)}">{sst}</sst>'

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        )
        z.writestr("xl/workbook.xml", f'<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="{ns}"/>')
        z.writestr("xl/sharedStrings.xml", shared)
        z.writestr("xl/worksheets/sheet1.xml", sheet)
    return buf.getvalue()


def write_prng_fixture(target: Path) -> Path:
    """Zapisuje ZIP (jak u GUGiK) z plikiem legendy i właściwym XLSX."""
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Export danych PRNG z dnia 2026-11-20.txt", "próbka testowa")
        z.writestr("PRNG_legenda_nazwy kolumn_XLS SHP GML.XLSX", b"")
        z.writestr("PRNG_MIEJSCOWOSCI_XLSX.xlsx", _xlsx_bytes())
    return target


if __name__ == "__main__":
    print(write_prng_fixture(Path(__file__).parent / "fixtures" / "prng_sample.zip"))
