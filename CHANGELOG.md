# Changelog

Wszystkie istotne zmiany w projekcie. Format: [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/), wersjonowanie: [SemVer](https://semver.org/lang/pl/).

## [Unreleased]

## [1.2.0] - 2026-11-23

### Dodano
- Przycisk „Losuj miejsce”: mapa przelatuje do losowego miejsca spośród widocznych (z uwzględnieniem filtrów) i otwiera jego kartę. Przy `prefers-reduced-motion` bez animacji.
- Test end-to-end w przeglądarce Chromium (`tests/e2e_smoke.py`, Playwright) uruchamiany w CI przy każdym PR: ładowanie mapy, wyszukiwarka, stan w URL, „Losuj miejsce”, widok desktop i mobilny.

## [1.1.0] - 2026-11-23

### Dodano
- Szybki start kontenera: zbudowana mapa jest trzymana w wolumenie `map-data`, więc każde kolejne `docker compose up` startuje w kilka sekund. `REFRESH=1` wymusza pobranie świeżych danych (`scripts/docker-start.sh`).

## [1.0.2] - 2026-11-22

### Poprawiono
- Mapa nie ładowała się w sieciach, w których unpkg.com działa wolno: Leaflet jest teraz serwowany z tej samej domeny (`scripts/fetch_vendor.py`, pliki z rejestru npm z kontrolą SHA-512), a CDN jsDelivr służy tylko jako zapas.
- Fonty Google ładowane bez blokowania wyświetlania strony.
- Czytelny komunikat, gdy biblioteki mapy nie mogą się wczytać.

## [1.0.1] - 2026-11-21

### Poprawiono
- Klasyfikacja: rodzinne kaplice grobowe („mauzoleum”), obeliski i figury religijne nie są już liczone jako miejsca pamięci (−385 fałszywych trafień).
- Wygląd znaczników klastrów na mapie.
- Pomiar czasu startu w stopce liczony od otwarcia strony.

## [1.0.0] - 2026-11-21

### Dodano
- Potok danych w Pythonie (tylko biblioteka standardowa): pobieranie zbiorów 1130, 168 i 780 przez API dane.gov.pl, z automatycznym wyborem aktualnego pliku.
- Klasyfikacja obiektów rejestru zabytków do 9 kategorii (obozy i getta, II wojna, dziedzictwo żydowskie, I wojna, powstania, wojna 1920, fortyfikacje, pomniki i miejsca pamięci, Pomniki Historii).
- Geokodowanie obiektów po Państwowym Rejestrze Nazw Geograficznych (dopasowanie: województwo + gmina + miejscowość, z rozstrzyganiem niejednoznacznych nazw).
- Aplikacja webowa: mapa z klastrowaniem, wyszukiwarka bez polskich znaków, filtry kategorii i województw, „Co jest blisko mnie?”, karta obiektu z linkiem do zabytek.pl, stan widoku w adresie URL, wersja mobilna.
- Uruchomienie jedną komendą (`docker compose up`) i publikacja na GitHub Pages z cotygodniową aktualizacją danych.
- CI: ruff, testy na Pythonie 3.10–3.13, test obrazu Dockera.
- Dokumentacja: raport końcowy (ISO 21513), lessons learned (PMI), metodologia, architektura, rejestr dokumentów (ISO 10013).

[Unreleased]: https://github.com/d4nf6c4c5d5b5-ai/miejsca-pamieci/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/d4nf6c4c5d5b5-ai/miejsca-pamieci/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/d4nf6c4c5d5b5-ai/miejsca-pamieci/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/d4nf6c4c5d5b5-ai/miejsca-pamieci/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/d4nf6c4c5d5b5-ai/miejsca-pamieci/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/d4nf6c4c5d5b5-ai/miejsca-pamieci/releases/tag/v1.0.0

---
<sub>Identyfikator: MP-DOC-008 · wersja 1.0 · autor: d4nf6c4c5d5b5-ai · 2026-11-21</sub>
