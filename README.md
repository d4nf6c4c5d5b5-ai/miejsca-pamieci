# Miejsca Pamięci

**Mapa trudnej historii Polski z otwartych danych.** Obozy, getta, cmentarze wojenne z I i II wojny światowej, mogiły powstańców, synagogi i kirkuty, schrony, forty i pomniki z państwowego rejestru zabytków na jednej mapie z wyszukiwarką.

**Demo:** https://d4nf6c4c5d5b5-ai.github.io/miejsca-pamieci/

## Jaki problem rozwiązuje

Państwowy rejestr zabytków zawiera ponad 81 tys. obiektów, w tym kilka tysięcy miejsc pamięci. Szukanie ich jest jednak trudne:

- rejestr nie ma kategorii typu „II wojna światowa” albo „dziedzictwo żydowskie”, tylko pola tekstowe z nazwą i funkcją obiektu;
- dane to plik CSV (29 MB, kodowanie Windows-1250), którego nie da się wygodnie przeglądać;
- obiekty z rejestru nie mają współrzędnych, więc nie można ich po prostu pokazać na mapie.

Miejsca Pamięci łączy trzy zbiory z dane.gov.pl, sam klasyfikuje obiekty i umieszcza je na mapie. Każdy (uczeń, nauczyciel, mieszkaniec, turysta) może sprawdzić, co wydarzyło się w jego okolicy: wpisać miejscowość albo kliknąć **„Co jest blisko mnie?”**.

Przykłady: `#q=oświęcim`, `#q=gorlice` (cmentarze z I wojny), `#q=łambinowice` (Stalag VIII B Lamsdorf), `#woj=podlaskie&bez=fortyfikacje`.

## Skąd są dane

Wszystkie dane pochodzą z [dane.gov.pl](https://dane.gov.pl) i są pobierane przez publiczne API (`https://api.dane.gov.pl/1.4`). Klucz API nie jest potrzebny.

| Zbiór | Wydawca | Do czego służy |
|---|---|---|
| [Rejestr zabytków nieruchomych](https://dane.gov.pl/pl/dataset/1130) (zbiór 1130) | Narodowy Instytut Dziedzictwa | ~81 tys. zabytków: nazwa, funkcja, chronologia, adres |
| [Pomniki historii](https://dane.gov.pl/pl/dataset/168) (zbiór 168) | Narodowy Instytut Dziedzictwa | obiekty najwyższej rangi z dokładnymi współrzędnymi (np. Westerplatte) |
| [Państwowy Rejestr Nazw Geograficznych: miejscowości](https://dane.gov.pl/pl/dataset/780) (zbiór 780) | GUGiK | ~124 tys. miejscowości ze współrzędnymi, do geokodowania |

Jak dokładnie klasyfikujemy obiekty i ustalamy ich położenie: [`docs/metodologia.md`](docs/metodologia.md).

> Położenie obiektów z rejestru jest **przybliżone do miejscowości** (rejestr nie publikuje współrzędnych). Aplikacja mówi o tym w karcie każdego obiektu i odsyła do oficjalnej karty w [zabytek.pl](https://zabytek.pl).

## Uruchomienie

### 1. Jedna komenda: Docker

```bash
git clone https://github.com/d4nf6c4c5d5b5-ai/miejsca-pamieci.git
cd miejsca-pamieci
docker compose up
```

Otwórz http://localhost:8080. Pierwsze uruchomienie pobiera ok. 55 MB danych z dane.gov.pl i buduje mapę (ok. 1–2 min). Kolejne starty korzystają z pobranych plików.

Bez internetu: `DATA_SOURCE=sample docker compose up` (mała próbka testowa).

### 2. Bez Dockera: sam Python 3.10+

Projekt nie ma zależności, wystarczy biblioteka standardowa.

```bash
python3 scripts/fetch_data.py   # pobiera dane z API dane.gov.pl → web/data/places.json
python3 scripts/serve.py        # http://localhost:8080
```

Lub krócej: `make data serve`. Wszystkie polecenia wyświetla `make help`.

### 3. Darmowy hosting: GitHub Pages

Workflow [`.github/workflows/pages.yml`](.github/workflows/pages.yml) przy każdym pushu do `main` i co tydzień:
pobiera świeże dane z dane.gov.pl, uruchamia testy, buduje `places.json` i publikuje stronę.
Na własnym forku: **Settings → Pages → Source: GitHub Actions**, potem **Actions → „Dane + demo” → Run workflow**.

### Konfiguracja

Zmienne środowiskowe opisuje [`.env.example`](.env.example) (`cp .env.example .env`). Projekt nie używa żadnych sekretów. Gdyby kiedyś były potrzebne, trafiają tylko do `.env`, który jest w `.gitignore`.

## Wydajność

| Technika | Efekt |
|---|---|
| Dane przetwarzane raz, przy budowie (nie w przeglądarce) | przeglądarka dostaje gotowy plik zamiast 3 zbiorów (~55 MB) |
| Kolumnowy JSON (`columns` + `rows`), kategorie jako maska bitowa | nazwy pól zapisane raz, nie w każdym rekordzie |
| Kompresja gzip (`places.json.gz`, Pages kompresuje automatycznie) | ok. 5× mniej danych do pobrania |
| `<link rel="preload">` danych | pobieranie danych startuje równolegle z bibliotekami mapy |
| Leaflet z rendererem Canvas + klastrowanie (`chunkedLoading`) | tysiące punktów bez zacinania, także na telefonie |
| Indeks wyszukiwania budowany raz (tekst bez polskich znaków), debounce 160 ms | filtrowanie w milisekundach, bez zapytań do serwera |
| Lista wyników stronicowana po 80 | szybkie renderowanie DOM |
| Strumieniowe czytanie XLSX (`iterparse`) | arkusz PRNG (190 MB XML) czytany wiersz po wierszu, bez ładowania całości do pamięci |
| Brak frameworka i kroku budowania JS | 3 pliki: HTML, CSS, JS (razem ~24 kB przed kompresją) |

Czas ładowania i liczba miejsc są widoczne w stopce aplikacji. Pomiary: [`docs/raport-koncowy.md`](docs/raport-koncowy.md#4-rezultaty).

## Struktura repozytorium

```
├── src/miejsca/          potok danych (Python, tylko stdlib)
│   ├── sources.py        pobieranie z API dane.gov.pl
│   ├── readers.py        czytniki CSV (cp1250) i XLSX (strumieniowo)
│   ├── categories.py     reguły klasyfikacji miejsc pamięci
│   ├── geo.py            geokodowanie po PRNG
│   └── build.py          budowa web/data/places.json
├── scripts/
│   ├── fetch_data.py     pobranie danych + budowa (odtwarzalność wyniku)
│   └── serve.py          serwer statyczny z gzip
├── web/                  aplikacja (HTML/CSS/JS + Leaflet)
├── tests/                testy + mała próbka danych (fixtures)
├── docs/                 dokumentacja projektu (ISO 21513, PMI, ISO 10013)
├── .github/              CI, publikacja na Pages, szablony zgłoszeń i PR
├── Dockerfile, docker-compose.yml
└── README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, CHANGELOG, .env.example
```

Duże pliki danych nie trafiają do repozytorium. Każdy odtworzy je skryptem `scripts/fetch_data.py`.

## Testy i jakość

```bash
make test   # 19 testów jednostkowych i end-to-end na próbce prawdziwych rekordów
make lint   # ruff (Python) + node --check (JS)
```

CI ([`ci.yml`](.github/workflows/ci.yml)) przy każdym PR uruchamia linter, testy na Pythonie 3.10/3.12/3.13 i sprawdza, czy obraz Dockera się buduje i serwuje aplikację.

## Dokumentacja

| Dokument | Identyfikator |
|---|---|
| [Raport końcowy (ISO 21513)](docs/raport-koncowy.md) | MP-DOC-002 |
| [Lessons learned (PMI)](docs/lessons-learned.md) | MP-DOC-003 |
| [Metodologia danych](docs/metodologia.md) | MP-DOC-004 |
| [Architektura i wydajność](docs/architektura.md) | MP-DOC-005 |
| [Rejestr dokumentów (ISO 10013)](docs/kontrola-dokumentow.md) | MP-DOC-001 |

## Wkład i licencja

Zgłoszenia błędów (również w danych) i pull requesty są mile widziane: [`CONTRIBUTING.md`](CONTRIBUTING.md). Obowiązuje [Kodeks postępowania](CODE_OF_CONDUCT.md).

Kod: licencja [MIT](LICENSE). Dane: informacja publiczna udostępniona w portalu dane.gov.pl przez Narodowy Instytut Dziedzictwa i Główny Urząd Geodezji i Kartografii, ponownie wykorzystywana z podaniem źródła. Podkład mapy: © współtwórcy OpenStreetMap.

---
<sub>Identyfikator: MP-DOC-000 · wersja 1.0 · autor: d4nf6c4c5d5b5-ai · 2026-11-21</sub>
