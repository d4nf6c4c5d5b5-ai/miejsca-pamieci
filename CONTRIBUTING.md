# Jak współtworzyć Miejsca Pamięci

Dziękujemy, że chcesz pomóc. Przydaje się każdy wkład: zgłoszenie złej kategorii obiektu, poprawka literówki czy nowa funkcja.

## Zgłaszanie błędów

1. Sprawdź w [Issues](../../issues), czy ktoś już tego nie zgłosił.
2. Wybierz szablon:
   - **Zgłoszenie błędu**: coś nie działa w aplikacji;
   - **Błąd w danych lub kategorii**: obiekt jest w złej kategorii, w złym miejscu, brakuje go albo nie powinno go być;
   - **Propozycja funkcji**: pomysł na ulepszenie.
3. Dołącz link do widoku (adres strony zapisuje wyszukiwanie i otwarty obiekt, np. `#q=gorlice&obiekt=PL.1.9...`).

Błędy w samych danych źródłowych (np. literówka w nazwie zabytku) zgłaszamy też wydawcy: Narodowemu Instytutowi Dziedzictwa przez [zabytek.pl](https://zabytek.pl).

## Zmiany w kodzie

```bash
git clone https://github.com/<twoj-login>/miejsca-pamieci.git
cd miejsca-pamieci
git checkout -b poprawka/krotki-opis
make sample serve        # aplikacja na próbce danych: http://localhost:8080
make test lint           # przed wysłaniem PR
python tests/e2e_smoke.py   # opcjonalnie: test w przeglądarce (pip install playwright)
```

Do lintera potrzebny jest `ruff` (`pip install ruff`). Reszta projektu wymaga tylko Pythona 3.10+.

### Zasady

- **Jeden PR = jedna zmiana.** Mniejsze PR-y szybciej przechodzą przegląd.
- **Testy:** zmiana logiki (zwłaszcza reguł w `src/miejsca/categories.py`) wymaga testu w `tests/` z przykładem prawdziwego rekordu.
- **Bez dużych danych w repozytorium.** Pliki z `data/raw/` i `web/data/places.json` są generowane skryptem `scripts/fetch_data.py`. Mała próbka w `tests/fixtures/` jest w porządku.
- **Bez sekretów w kodzie.** Konfiguracja tylko przez zmienne środowiskowe (`.env.example`).
- **Styl:** `ruff format` dla Pythona; JS bez frameworków, w stylu istniejącego `web/app.js`.
- **Komunikaty commitów:** tryb rozkazujący, np. `Dodaj kategorię „Wojna 1920”`, `Popraw geokodowanie gmin miejsko-wiejskich`.
- **Changelog:** dopisz zmianę do sekcji `Unreleased` w `CHANGELOG.md`.
- **Dokumenty z `docs/`:** przy zmianie podbij wersję i dodaj wiersz w tabeli „Historia zmian” (zasady: [`docs/kontrola-dokumentow.md`](docs/kontrola-dokumentow.md)).

### Pull request

1. Wypchnij gałąź i otwórz PR do `main`. Szablon PR podpowie, co opisać.
2. CI uruchomi linter, testy i budowę obrazu Dockera. Wszystko musi być zielone.
3. Opiekun projektu przegląda PR zwykle w ciągu kilku dni.

## Zmiana reguł klasyfikacji

Kategorie wynikają z wyrażeń regularnych na polach `NAZWA` i `FUNKCJA` rejestru. Jak je zmieniać:

1. Znajdź przykład złej klasyfikacji (identyfikator INSPIRE).
2. Dodaj test w `tests/test_pipeline.py`, który dziś nie przechodzi.
3. Popraw regułę w `src/miejsca/categories.py`.
4. Uruchom pełne budowanie (`make data`) i porównaj statystyki kategorii przed zmianą i po niej. Wynik wpisz w opisie PR.

---
<sub>Identyfikator: MP-DOC-006 · wersja 1.0 · autor: d4nf6c4c5d5b5-ai · 2026-11-21</sub>
