# Metodologia danych

| Metryka | |
|---|---|
| Identyfikator | MP-DOC-004 |
| Wersja | 1.1 |
| Status | Zatwierdzony |
| Autor | d4nf6c4c5d5b5-ai |
| Data | 2026-11-21 |

## 1. Źródła

| Klucz | Zbiór na dane.gov.pl | Zasób | Format | Uwagi |
|---|---|---|---|---|
| `rejestr` | [1130: Rejestr zabytków nieruchomych](https://dane.gov.pl/pl/dataset/1130) | „plik CSV” | CSV, `;`, Windows-1250, ~29 MB | 81 279 rekordów (stan na 30.09.2026), **bez współrzędnych** |
| `pomniki` | [168: Pomniki historii](https://dane.gov.pl/pl/dataset/168) | „plik CSV” | CSV, `;`, Windows-1250 | 184 rekordy (134 Pomniki Historii, część w kilku lokalizacjach), współrzędne `E`/`N` z przecinkiem dziesiętnym |
| `prng` | [780: PRNG – miejscowości](https://dane.gov.pl/pl/dataset/780) | „miejscowości – format XLSX” | ZIP → XLSX, ~25 MB | 124 232 miejscowości, współrzędne w stopniach, minutach i sekundach |

### Jak skrypt znajduje pliki

Adresy plików zmieniają się przy każdej aktualizacji (np. `/media/resources/20261002/…`). Dlatego `src/miejsca/sources.py` pyta API `GET /1.4/datasets/{id}/resources` i wybiera zasób po tytule i formacie. Dla PRNG pole `link` wskazuje aktualny plik u GUGiK (aktualizowany co tydzień), a `file_url` kopię w dane.gov.pl z 2021 r. Dlatego najpierw używamy `link`, a `download_url` jest zapasem.

Metadane każdego pobrania (identyfikator zasobu, data danych, adres, rozmiar, czas pobrania) trafiają do `data/raw/*.meta.json` i do pola `sources` w `places.json`.

## 2. Klasyfikacja: co jest „miejscem pamięci”

Rejestr nie ma pola kategorii historycznej. Kategorie wyznaczamy jawnymi regułami (wyrażenia regularne) na polach `NAZWA` i `FUNKCJA` (`src/miejsca/categories.py`):

| Kategoria | Przykładowe słowa kluczowe | Przykład z rejestru |
|---|---|---|
| Obozy i getta | obóz, obozu, stalag, oflag, getto, Lager | „teren po Stalagu VIII B (344) Lamsdorf” |
| II wojna światowa | „II wojn…”, 1939, hitlerowski, okupacja | „cmentarz wojenny z II wojny światowej” |
| Dziedzictwo żydowskie | synagoga, bożnica, cmentarz żydowski, kirkut, mykwa | „synagoga” (Dzierżoniów) |
| I wojna światowa | „I wojn…” (ale nie „II”), 1914–1918 | „cmentarz wojenny nr 87 z I wojny światowej” |
| Powstania narodowe | powstanie, powstańców, insurekcja | „mogiła powstańców śląskich” |
| Wojna 1920 | 1920, polsko-rosyjska, bolszewicka | „mogiła zbiorowa obrońców Wisły z 22 sierpnia 1920 r.” |
| Fortyfikacje | fort, schron, bunkier, bateria, umocnienie, twierdza | „Fort III Dęblin”, „schron bojowy nr 8 typu Ringstand 58c” |
| Pomniki i miejsca pamięci | pomnik, mogiła, cmentarz wojenny, egzekucja, ofiar, poległych | „pomnik - grób zbiorowy ofiar obozów…” |
| Pomniki Historii | cały zbiór 168 | „Pole Bitwy na Westerplatte” |

Reguły dodatkowe:

- **Chronologia:** fortyfikacja lub pomnik z lat 1930–1950 dostaje też kategorię „II wojna”, a z lat 1914–1919 kategorię „I wojna” (np. schron „1944–1945”).
- **Wykluczenia** (fałszywe trafienia znalezione w danych): schroniska turystyczne („schron…”), fortepiany („fort…”), pomniki nagrobne i nagrobki, kapliczki, ogrodzenia, figury i pomniki religijne („pomnik Św. Trójcy”). Rodzinne kaplice grobowe („mauzoleum”) i obeliski bez związku z wojną nie są liczone jako miejsca pamięci.
- **Świadomie pominięte:** średniowieczne mury, baszty i wieże obronne. To zabytki architektury obronnej, nie miejsca pamięci, i zdominowałyby mapę.
- Obiekt może mieć **kilka kategorii** (np. „cmentarz wojenny z I i II wojny”). Kolor znacznika wynika z kategorii o najwyższym priorytecie (kolejność w tabeli).

## 3. Geokodowanie

Rejestr podaje adres (`WOJEWODZTWO`, `POWIAT`, `GMINA`, `MIEJSCOWOSC`, `ULICA`, `NR_ADRESOWY`), ale nie współrzędne. Ustalamy je z PRNG (`src/miejsca/geo.py`):

1. Normalizacja nazw: małe litery, usunięcie nawiasów, ujednolicenie myślników. Nazwy gmin sprowadzamy do rdzenia: NID `Dzierżoniów (gm. miejska)` i `Słomniki - obszar wiejski`, a PRNG `Dzierżoniów-gmina miejska` i `Słomniki-gmina miejsko-wiejska` dają `dzierżoniów` i `słomniki`.
2. Dopasowanie po kolei, od najdokładniejszego klucza:
   1. województwo + gmina + miejscowość,
   2. województwo + powiat + miejscowość,
   3. województwo + miejscowość, tylko gdy nazwa jest jednoznaczna,
   4. siedziba gminy (precyzja „gmina”).
3. Gdy w kluczu jest kilka obiektów PRNG, wybieramy według rodzaju: miasto > wieś > osada > część miasta > kolonia > część wsi > przysiółek.
4. Obiekty z tej samej miejscowości dostają deterministyczne przesunięcie o 75–250 m, żeby nie nakładały się w jednym punkcie. Na mapie rozsuwa je klaster.

**Wynik kontrolny:** na pełnych danych (2026-11-21) wszystkie 2 651 miejsc pamięci z rejestru dopasowano już pierwszym kluczem (100%). Pomniki Historii mają własne, dokładne współrzędne.

**Ograniczenie:** punkt na mapie to miejscowość, nie dokładne położenie obiektu. Mówi o tym karta każdego obiektu. Ograniczenie wynika z danych źródłowych (zob. rekomendacje w [lessons learned](lessons-learned.md)).

## 4. Format wyjściowy `web/data/places.json`

```json
{
  "version": 1,
  "generated": "2026-11-21T19:00:00Z",
  "sources": [ { "key": "rejestr", "resource_id": "2730055", "data_date": "2026-09-30", "url": "…" } ],
  "categories": [ { "key": "obozy", "label": "Obozy i getta", "color": "#b42318", "description": "…" } ],
  "voivodeships": [ "dolnośląskie", "…" ],
  "stats": { "rejestr_wszystkie": 81279, "…": 0 },
  "columns": ["id","name","func","chron","mask","lat","lon","woj","powiat","gmina","place","addr","prec","src"],
  "rows": [ ["PL.1.9.ZIPOZ.NID_N_02_BK.97369","synagoga","synagoga","1875 r.",4,50.72785,16.65011,0,"dzierżoniowski","Dzierżoniów (gm. miejska)","Dzierżoniów","Ignacego Krasickiego 28",1,0] ]
}
```

- `mask`: kategorie jako bity (bit 0 = pierwsza kategoria z `categories`);
- `prec`: 0 = dokładne, 1 = miejscowość, 2 = gmina;
- `src`: 0 = rejestr zabytków, 1 = Pomniki Historii.

## 5. Jakość danych: kontrole automatyczne

- Testy jednostkowe na prawdziwych rekordach (`tests/fixtures/`, kodowanie Windows-1250 jak w oryginale).
- Odrzucanie współrzędnych spoza obszaru Polski.
- Workflow publikacji zapisuje w podsumowaniu (Step Summary) statystyki: liczbę rekordów, liczbę miejsc pamięci, odsetek zlokalizowanych, liczności kategorii. Każda aktualizacja danych zostawia więc ślad do porównania.

## Historia zmian

| Wersja | Data | Autor | Opis zmian |
|---|---|---|---|
| 1.0 | 2026-11-21 | d4nf6c4c5d5b5-ai | Pierwsze wydanie. |
| 1.1 | 2026-11-21 | d4nf6c4c5d5b5-ai | Nowe wykluczenia (mauzolea rodzinne, figury religijne), aktualny wynik geokodowania. |
