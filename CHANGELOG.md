# Changelog

Wszystkie istotne zmiany w projekcie. Format: [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/), wersjonowanie: [SemVer](https://semver.org/lang/pl/).

## [Unreleased]

## [1.0.0] - 2026-11-21

### Dodano
- Potok danych w Pythonie (tylko biblioteka standardowa): pobieranie zbiorów 1130, 168 i 780 przez API dane.gov.pl, z automatycznym wyborem aktualnego pliku.
- Klasyfikacja obiektów rejestru zabytków do 9 kategorii (obozy i getta, II wojna, dziedzictwo żydowskie, I wojna, powstania, wojna 1920, fortyfikacje, pomniki i miejsca pamięci, Pomniki Historii).
- Geokodowanie obiektów po Państwowym Rejestrze Nazw Geograficznych (dopasowanie: województwo + gmina + miejscowość, z rozstrzyganiem niejednoznacznych nazw).
- Aplikacja webowa: mapa z klastrowaniem, wyszukiwarka bez polskich znaków, filtry kategorii i województw, „Co jest blisko mnie?”, karta obiektu z linkiem do zabytek.pl, stan widoku w adresie URL, wersja mobilna.
- Uruchomienie jedną komendą (`docker compose up`) i publikacja na GitHub Pages z cotygodniową aktualizacją danych.
- CI: ruff, testy na Pythonie 3.10–3.13, test obrazu Dockera.
- Dokumentacja: raport końcowy (ISO 21513), lessons learned (PMI), metodologia, architektura, rejestr dokumentów (ISO 10013).

[Unreleased]: https://github.com/d4nf6c4c5d5b5-ai/miejsca-pamieci/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/d4nf6c4c5d5b5-ai/miejsca-pamieci/releases/tag/v1.0.0

---
<sub>Identyfikator: MP-DOC-008 · wersja 1.0 · autor: d4nf6c4c5d5b5-ai · 2026-11-21</sub>
