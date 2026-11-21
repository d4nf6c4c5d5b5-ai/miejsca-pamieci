"""Klasyfikacja obiektów z rejestru zabytków do kategorii „miejsc pamięci”.

Rejestr zabytków nieruchomych (NID) nie ma pola „kategoria historyczna”,
więc kategorię wyznaczamy regułami na polach NAZWA, FUNKCJA i CHRONOLOGIA.
Reguły są celowo jawne i proste, żeby każdy mógł je sprawdzić i poprawić
(zob. docs/metodologia.md).
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    key: str
    label: str
    color: str
    description: str


# Kolejność = priorytet przy wyborze kategorii głównej (kolor znacznika).
CATEGORIES: list[Category] = [
    Category("obozy", "Obozy i getta", "#b42318", "Niemieckie obozy koncentracyjne, obozy pracy i jenieckie, getta."),
    Category("ww2", "II wojna światowa", "#c4320a", "Cmentarze, mogiły, schrony i pomniki z lat 1939–1945."),
    Category("zydowskie", "Dziedzictwo żydowskie", "#1d4ed8", "Synagogi, cmentarze żydowskie (kirkuty), mykwy."),
    Category("ww1", "I wojna światowa", "#6d28d9", "Cmentarze i umocnienia z lat 1914–1918."),
    Category(
        "powstania",
        "Powstania narodowe",
        "#047857",
        "Mogiły i pomniki powstańców (styczniowe, śląskie, wielkopolskie…).",
    ),
    Category("wojna1920", "Wojna 1920", "#a16207", "Miejsca związane z wojną polsko-bolszewicką."),
    Category("fortyfikacje", "Fortyfikacje", "#475467", "Forty, schrony, bunkry, baterie i twierdze."),
    Category("pamiec", "Pomniki i miejsca pamięci", "#0e7490", "Pomniki, mogiły zbiorowe, miejsca egzekucji i kaźni."),
    Category(
        "pomnik_historii", "Pomniki Historii", "#be185d", "Obiekty o najwyższej randze — wpisane jako Pomnik Historii."
    ),
]

CATEGORY_KEYS = [c.key for c in CATEGORIES]
BIT = {key: 1 << i for i, key in enumerate(CATEGORY_KEYS)}

_I = re.IGNORECASE
RULES: dict[str, re.Pattern[str]] = {
    "obozy": re.compile(r"ob[oó]z(?!in)|obozu|obozow|stalag|oflag|getto|lager", _I),
    "ww2": re.compile(r"\bII\s+wojn|1939|II\s*w\.\s*ś|wojny\s+obronnej|hitlerowsk|okupac", _I),
    "zydowskie": re.compile(r"żydow|zydow|synagog|bożnic|boznic|kirkut|mykw|ohel|judai", _I),
    "ww1": re.compile(r"(?<![I\w])I\s+wojn|1914|1915|1916|1917|1918", _I),
    "powstania": re.compile(r"powstan|powstań|insurekc", _I),
    "wojna1920": re.compile(r"1920|polsko-rosyjsk|polsko-bolszewick|bolszewick", _I),
    "fortyfikacje": re.compile(
        r"\bfort(?:u|y|ów|em|ach)?\b|fortyfik|forteczn|twierdz|schron(?!isk)|bunkier|bunkr|bateri|"
        r"umocnien|dzieło\s+obronn|element\s+obronn|działobitn|okop|blokhaus|kazamat|reduta|"
        r"prochowni|strażnica\s+obronn|punkt\s+oporu|obszar\s+warown",
        _I,
    ),
    "pamiec": re.compile(
        r"pomnik|mogił|kwater[ay]\s+wojen|cmentarz\s+wojen|cmentarz\s+wojsk|"
        r"miejsc[ae]\s+pamięci|mauzole|ofiar|egzekuc|straceń|kaźni|martyrolog|poległ|pomordowan|zamordowan|"
        r"obelisk|kopiec",
        _I,
    ),
}

# Fałszywe trafienia: obiekty, które pasują słowem, ale nie są miejscem pamięci.
_EXCLUDE = re.compile(r"schronisk|koszar\w*\s+d\.\s+obozu|ogrodzenie|kapliczk|fortepian|pomnik\s+nagrobn|nagrobek", _I)

_YEAR = re.compile(r"(1[0-9]{3})")


def years(chronologia: str) -> tuple[int, int] | None:
    """Zwraca (od, do) z pola CHRONOLOGIA, np. '1914 - 1918' -> (1914, 1918)."""
    found = [int(y) for y in _YEAR.findall(chronologia or "")]
    if not found:
        return None
    return min(found), max(found)


def classify(nazwa: str, funkcja: str, chronologia: str = "") -> list[str]:
    """Zwraca listę kluczy kategorii (posortowaną wg priorytetu) albo []."""
    text = f"{nazwa or ''} | {funkcja or ''}"
    if _EXCLUDE.search(text):
        return []
    found = [key for key, rx in RULES.items() if rx.search(text)]

    # Uzupełnienie po chronologii: obiekty militarne/pamięci z lat wojen.
    span = years(chronologia)
    military = {"fortyfikacje", "pamiec"} & set(found)
    if span and military:
        start, end = span
        if 1939 <= end <= 1950 and start >= 1930 and "ww2" not in found:
            found.append("ww2")
        if start >= 1914 and end <= 1919 and "ww1" not in found:
            found.append("ww1")

    # „1920” w samej chronologii nie wystarcza — to musi wynikać z nazwy/funkcji.
    order = {k: i for i, k in enumerate(CATEGORY_KEYS)}
    return sorted(set(found), key=order.__getitem__)


def mask(keys: list[str]) -> int:
    value = 0
    for key in keys:
        value |= BIT[key]
    return value
