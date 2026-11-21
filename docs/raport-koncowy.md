# Raport końcowy projektu „Miejsca Pamięci”

| Metryka | |
|---|---|
| Identyfikator | MP-DOC-002 |
| Wersja | 1.0 |
| Status | Zatwierdzony |
| Autor | d4nf6c4c5d5b5-ai |
| Data | 2026-11-21 |
| Podstawa | szkielet raportu zamknięcia projektu wg ISO 21513: cel, rezultaty, porównanie z planem, wpływ, wnioski |
| Repozytorium | https://github.com/d4nf6c4c5d5b5-ai/miejsca-pamieci |
| Demo | https://d4nf6c4c5d5b5-ai.github.io/miejsca-pamieci/ |

## 1. Streszczenie

Projekt dostarczył otwartoźródłową aplikację, która z trzech zbiorów dane.gov.pl (NID, GUGiK) buduje mapę **{{MIEJSCA}} miejsc pamięci** w Polsce: obozów, cmentarzy wojennych, synagog i kirkutów, mogił powstańców, fortyfikacji i Pomników Historii. Dane są pobierane i przetwarzane automatycznie, aplikacja działa po jednej komendzie (`docker compose up`) i na darmowym GitHub Pages, a dane aktualizują się co tydzień. Wszystkie cele zakresowe zrealizowano. Główne odstępstwo od planu to zmiana tematu w pierwszym dniu (pkt 5.1).

## 2. Cel projektu

### 2.1. Problem społeczny

Wiedza o miejscach pamięci w najbliższej okolicy jest rozproszona. Państwowy rejestr zabytków je zawiera, ale:
(a) nie ma kategorii historycznych, (b) jest udostępniany jako 29-megabajtowy CSV, (c) nie zawiera współrzędnych. Nauczyciel planujący lekcję w terenie, mieszkaniec czy turysta nie może łatwo sprawdzić, że np. pod Gorlicami jest kilkadziesiąt cmentarzy z I wojny światowej, a w Łambinowicach był Stalag VIII B.

### 2.2. Cele

| ID | Cel | Miernik sukcesu |
|---|---|---|
| C1 | Wyodrębnić miejsca pamięci z rejestru zabytków | jawne, przetestowane reguły; ≥ 8 kategorii |
| C2 | Umieścić je na mapie mimo braku współrzędnych | ≥ 95% obiektów zlokalizowanych |
| C3 | Udostępnić wyszukiwarkę dla każdego | działa na telefonie, wyszukiwanie po miejscowości, „blisko mnie” |
| C4 | Zapewnić odtwarzalność i otwartość | publiczne repozytorium MIT, skrypt pobierający dane z API, CI |
| C5 | Łatwe uruchomienie i wydajność | jedna komenda; pierwsze wyświetlenie mapy < 3 s |

### 2.3. Odbiorcy

Uczniowie i nauczyciele historii, mieszkańcy, turyści, przewodnicy, organizacje zajmujące się upamiętnianiem.

## 3. Zakres

**W zakresie:** potok danych (pobranie, klasyfikacja, geokodowanie), aplikacja webowa, wdrożenie (Docker, Pages), CI, dokumentacja.
**Poza zakresem:** opisy historyczne obiektów, dokładne współrzędne pojedynczych obiektów rejestru (brak w danych źródłowych), zabytki ruchome i archeologiczne.

## 4. Rezultaty

### 4.1. Produkty

| Produkt | Stan | Lokalizacja |
|---|---|---|
| Potok danych (Python, stdlib) | ✅ | `src/miejsca/`, `scripts/fetch_data.py` |
| Aplikacja mapy | ✅ | `web/`, demo na GitHub Pages |
| Uruchomienie jedną komendą | ✅ | `docker-compose.yml` |
| Automatyczna aktualizacja danych i publikacja | ✅ | `.github/workflows/pages.yml` |
| CI (linter, testy, Docker) | ✅ | `.github/workflows/ci.yml` |
| Testy (19, na prawdziwych rekordach) | ✅ | `tests/` |
| Dokumentacja (ISO 21513, PMI, ISO 10013) | ✅ | `docs/` |

### 4.2. Dane: wyniki pełnej budowy

| Wskaźnik | Wartość |
|---|---|
| Rekordy w rejestrze zabytków nieruchomych | {{REJESTR}} |
| Miejsca pamięci wyodrębnione z rejestru | {{MP_REJESTR}} |
| Zlokalizowane (geokodowanie PRNG) | {{ZLOK}} |
| Lokalizacje Pomników Historii | {{PH}} |
| **Razem na mapie** | **{{MIEJSCA}}** |
{{KATEGORIE}}

### 4.3. Wydajność

| Wskaźnik | Wartość | Jak mierzono |
|---|---|---|
| Rozmiar `places.json` | {{ROZMIAR}} | plik po budowie |
| Rozmiar po kompresji gzip | {{ROZMIAR_GZ}} | `places.json.gz` |
| Czas budowy danych w CI | {{CZAS_BUDOWY}} | log GitHub Actions |
| Start aplikacji (dane + mapa) | {{START}} | `performance.now()`, stopka aplikacji, GitHub Pages |
| Filtrowanie / wyszukiwanie | {{FILTR}} | `#perf[data-filter-ms]` |
| Kod aplikacji (HTML+CSS+JS) | ~24 kB | bez kompresji, bez frameworków |

Techniki optymalizacji opisuje [architektura](architektura.md#3-wydajność-zastosowane-techniki).

## 5. Porównanie z planem

### 5.1. Zakres

| Element planu | Plan | Wykonanie | Odchylenie i przyczyna |
|---|---|---|---|
| Temat | Porównywarka szkół (wyniki egzaminów) | Mapa miejsc pamięci | **Zmiana.** Wyników egzaminów dla pojedynczych szkół nie ma na dane.gov.pl (są tylko średnie wojewódzkie GUS). Zmianę wprowadzono w pierwszym dniu, więc nie wpłynęła na termin (LL-01). |
| Mapa z dokładnymi punktami | Tak | Punkty z dokładnością do miejscowości | Rejestr nie zawiera współrzędnych. Rozwiązanie: geokodowanie po PRNG i jawna informacja w karcie obiektu (LL-07). |
| Kategorie | 5 | 9 | Rozszerzenie: dane pozwoliły wyróżnić m.in. wojnę 1920 i Pomniki Historii. |
| „Co jest blisko mnie?” | Opcjonalnie | Zrealizowano | — |

### 5.2. Harmonogram

| Etap | Plan | Wykonanie |
|---|---|---|
| Wybór tematu i rozpoznanie danych | dzień 1 | dzień 1 (z jedną zmianą tematu) |
| Potok danych + testy | dni 2–3 | dzień 1–2 |
| Aplikacja webowa | dni 3–4 | dzień 2 |
| CI, Docker, Pages | dzień 5 | dzień 2 |
| Dokumentacja i prezentacja | dni 6–7 | dzień 2–3 |

Projekt zakończono w terminie (1 tydzień).

### 5.3. Zasoby i koszty

Plan i wykonanie: 0 zł. Wszystkie narzędzia i usługi są bezpłatne (GitHub, GitHub Actions, GitHub Pages, OpenStreetMap, dane.gov.pl).

### 5.4. Jakość

| Wymaganie zadania | Stan |
|---|---|
| Publiczne repozytorium, licencja MIT, README | ✅ |
| README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, CHANGELOG, .env.example | ✅ |
| Kod w `src/`, testy w `tests/`, dokumentacja w `docs/` | ✅ |
| Duże dane poza repozytorium; skrypt w `scripts/` pobiera je z API | ✅ |
| `.github/`: szablony zgłoszeń i PR, CI z testami i linterem przy każdym PR | ✅ |
| Klucze i hasła tylko w zmiennych środowiskowych | ✅ (projekt nie potrzebuje żadnych) |
| Raport ISO 21513, lessons learned PMI, kontrola dokumentów ISO 10013 | ✅ |
| Uruchomienie jedną komendą + darmowy hosting | ✅ |

## 6. Wpływ

- **Społeczny i edukacyjny:** narzędzie pozwala w kilka sekund znaleźć miejsca pamięci w swojej okolicy, np. do zaplanowania lekcji historii w terenie, wycieczki szkolnej czy porządkowania zapomnianych mogił przed 1 listopada. Wiele cmentarzy z I wojny i kirkutów jest zapomnianych, a ich pokazanie na mapie zwiększa szansę na opiekę nad nimi.
- **Dla otwartych danych:** projekt pokazuje wartość łączenia zbiorów różnych instytucji (NID + GUGiK) i wskazuje konkretne usprawnienia dla wydawców (współrzędne w zbiorze 1130, kodowanie UTF-8; [rekomendacje R-04, R-05](lessons-learned.md#4-rekomendacje)).
- **Odtwarzalność:** każdy może zbudować identyczny wynik z publicznych danych jedną komendą, a reguły klasyfikacji są jawne i testowane.
- **Ryzyka i ograniczenia:** przybliżone położenie obiektów, możliwe błędy klasyfikacji regułowej (mechanizm zgłaszania: szablon „Błąd w danych”).

## 7. Wnioski

1. Największe ryzyko projektów na otwartych danych leży w danych, nie w kodzie. Rozpoznanie danych przed wyborem tematu uratowało harmonogram.
2. Architektura statyczna („oblicz raz, serwuj statycznie”) dała jednocześnie najlepszą wydajność, zerowy koszt i najprostsze uruchomienie.
3. Jawne reguły z testami na prawdziwych rekordach są wystarczająco dobre do klasyfikacji tekstu urzędowego i, w przeciwieństwie do modeli ML, łatwo je sprawdzić i poprawić.
4. Szczegóły: [lessons learned](lessons-learned.md).

## 8. Przekazanie i utrzymanie

- Dane aktualizują się automatycznie co tydzień (workflow `pages.yml`). Nieudane pobranie nie podmienia działającej wersji demo.
- Zgłoszenia przez GitHub Issues (szablony: błąd, błąd w danych, propozycja).
- Proponowane kierunki rozwoju: opisy z Wikidanych, trasy edukacyjne, eksport listy do PDF dla nauczycieli.

## Historia zmian

| Wersja | Data | Autor | Opis zmian |
|---|---|---|---|
| 1.0 | 2026-11-21 | d4nf6c4c5d5b5-ai | Raport po zakończeniu projektu, z wynikami pierwszej pełnej budowy danych. |
