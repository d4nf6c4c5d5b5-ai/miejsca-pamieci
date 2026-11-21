"""Geokodowanie obiektów po nazwie miejscowości (Państwowy Rejestr Nazw Geograficznych).

Rejestr zabytków nieruchomych udostępnia adres, ale nie współrzędne.
PRNG (GUGiK, dane.gov.pl) zawiera ~124 tys. miejscowości z punktem
głównym, więc obiekt dostaje współrzędne swojej miejscowości.
Dopasowanie idzie od najbardziej do najmniej precyzyjnego klucza.
"""

from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from dataclasses import dataclass, field

_DMS = re.compile(r"(\d+)°\s*(\d+)'\s*(\d+(?:[.,]\d+)?)\"?")

# Im mniejsza liczba, tym lepszy kandydat, gdy nazwa się powtarza.
RANK = {
    "miasto": 0,
    "wieś": 1,
    "osada": 2,
    "osada leśna": 3,
    "część miasta": 4,
    "kolonia": 5,
    "część wsi": 6,
    "przysiółek wsi": 7,
}


def parse_dms(text: str) -> tuple[float, float] | None:
    """'50°43'05" 16°39'17"' -> (50.71806, 16.65472)."""
    parts = _DMS.findall(text or "")
    if len(parts) != 2:
        return None
    lat, lon = (int(d) + int(m) / 60 + float(s.replace(",", ".")) / 3600 for d, m, s in parts)
    if not (48.5 < lat < 55.5 and 13.5 < lon < 24.5):
        return None
    return round(lat, 5), round(lon, 5)


def norm(text: str) -> str:
    """Normalizacja nazwy do porównań: małe litery, bez nawiasów i nadmiarowych spacji."""
    text = unicodedata.normalize("NFC", text or "").lower()
    text = re.sub(r"\(.*?\)", " ", text)
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"\s*-\s*", "-", text)
    return re.sub(r"\s+", " ", text).strip()


def gmina_base_nid(gmina: str) -> str:
    """NID: 'Dzierżoniów (gm. miejska)', 'Czchów - obszar wiejski' -> 'dzierżoniów', 'czchów'."""
    g = re.sub(r"\(gm\..*?\)", "", gmina or "")
    g = re.sub(r"\s*-\s*(miasto|obszar wiejski)\s*$", "", g, flags=re.IGNORECASE)
    return norm(g)


def gmina_base_prng(gmina: str) -> str:
    """PRNG: 'Pleszew-gmina miejsko-wiejska' -> 'pleszew'."""
    return norm((gmina or "").rsplit("-gmina", 1)[0])


@dataclass
class Gazetteer:
    by_gmina: dict[tuple[str, str, str], tuple[int, float, float]] = field(default_factory=dict)
    by_powiat: dict[tuple[str, str, str], tuple[int, float, float]] = field(default_factory=dict)
    by_woj: dict[tuple[str, str], list[tuple[int, float, float]]] = field(default_factory=dict)

    @staticmethod
    def _keep_best(index: dict, key, value) -> None:
        current = index.get(key)
        if current is None or value[0] < current[0]:
            index[key] = value

    def add(self, nazwa: str, rodzaj: str, coords: str, woj: str, powiat: str, gmina: str) -> bool:
        point = parse_dms(coords)
        if not point or not nazwa:
            return False
        value = (RANK.get((rodzaj or "").strip(), 9), *point)
        n, w = norm(nazwa), norm(woj)
        self._keep_best(self.by_gmina, (w, gmina_base_prng(gmina), n), value)
        self._keep_best(self.by_powiat, (w, norm(powiat), n), value)
        self.by_woj.setdefault((w, n), []).append(value)
        return True

    def __len__(self) -> int:
        return len(self.by_gmina)

    def locate(self, woj: str, powiat: str, gmina: str, miejscowosc: str) -> tuple[float, float, str] | None:
        """Zwraca (lat, lon, precyzja) albo None. Precyzja: 'miejscowosc' lub 'gmina'."""
        w, n, g = norm(woj), norm(miejscowosc), gmina_base_nid(gmina)
        for index, key in ((self.by_gmina, (w, g, n)), (self.by_powiat, (w, norm(powiat), n))):
            hit = index.get(key)
            if hit:
                return hit[1], hit[2], "miejscowosc"
        candidates = self.by_woj.get((w, n), [])
        if candidates:
            best = min(c[0] for c in candidates)
            top = {(c[1], c[2]) for c in candidates if c[0] == best}
            if len(top) == 1:
                lat, lon = top.pop()
                return lat, lon, "miejscowosc"
        # Ostatnia deska ratunku: siedziba gminy o tej samej nazwie co gmina.
        hit = self.by_gmina.get((w, g, g)) or self.by_powiat.get((w, norm(powiat), g))
        if hit:
            return hit[1], hit[2], "gmina"
        return None


def jitter(lat: float, lon: float, key: str, meters: float = 250.0) -> tuple[float, float]:
    """Deterministyczne, niewielkie przesunięcie, by obiekty z tej samej miejscowości
    nie leżały w jednym punkcie (rozsuwa je klaster na mapie)."""
    digest = hashlib.blake2b(key.encode(), digest_size=4).digest()
    angle = digest[0] / 255 * 2 * math.pi
    dist = (0.3 + 0.7 * digest[1] / 255) * meters
    dlat = dist * math.cos(angle) / 111_320
    dlon = dist * math.sin(angle) / (111_320 * math.cos(math.radians(lat)))
    return round(lat + dlat, 5), round(lon + dlon, 5)
