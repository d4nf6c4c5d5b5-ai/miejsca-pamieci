# Architektura i wydajność

| Metryka | |
|---|---|
| Identyfikator | MP-DOC-005 |
| Wersja | 1.0 |
| Status | Zatwierdzony |
| Autor | d4nf6c4c5d5b5-ai |
| Data | 2026-11-21 |

## 1. Przegląd

```
 dane.gov.pl API ──► scripts/fetch_data.py ──► web/data/places.json ──► przeglądarka (Leaflet)
   (1130, 168, 780)    src/miejsca/*             (+ .gz)                 web/index.html, app.js
                       pobierz → czytaj →
                       klasyfikuj → geokoduj
```

Architektura **„oblicz raz, serwuj statycznie”**: całe ciężkie przetwarzanie (55 MB danych źródłowych) odbywa się przy budowie, w CI albo w kontenerze. Aplikacja to statyczne pliki bez backendu i bazy danych, więc działa na darmowym hostingu (GitHub Pages) i skaluje się bez kosztów.

## 2. Decyzje techniczne

| Decyzja | Uzasadnienie | Rozważane alternatywy |
|---|---|---|
| Python, tylko biblioteka standardowa | zero instalacji; działa w CI, Dockerze i na komputerze ucznia; brak problemów z zależnościami | DuckDB: świetny do analityki CSV/Parquet, ale nie czyta XLSX w ZIP ani CSV w cp1250 bez dodatkowych kroków; tutaj nie był potrzebny, bo dane mieszczą się w pamięci |
| Statyczny JSON zamiast API/bazy | najszybszy możliwy czas odpowiedzi: zapytania filtrowane lokalnie w przeglądarce, bez sieci | serwer + SQLite/DuckDB: większy koszt utrzymania, potrzebny płatny hosting |
| Leaflet + MarkerCluster | lekki (~40 kB), dojrzały, działa na telefonach | MapLibre GL: ładniejsze kafelki wektorowe, ale cięższy i wymaga dostawcy stylu |
| Vanilla JS, brak kroku budowania | brak `node_modules`, łatwy wkład dla początkujących | React/Svelte: zbędne przy jednym widoku |
| GitHub Actions + Pages | darmowe, automatyczna cotygodniowa aktualizacja danych | Netlify/Vercel: równoważne, ale wymagają dodatkowego konta |

## 3. Wydajność: zastosowane techniki

**Potok danych**
- Strumieniowe czytanie XLSX (`xml.etree.ElementTree.iterparse` + `elem.clear()`): arkusz PRNG ma 190 MB XML i nie jest ładowany do pamięci w całości.
- Tylko 7 z 39 kolumn PRNG jest dekodowanych. Pozostałe są pomijane już na poziomie komórek.
- Indeks miejscowości to słowniki (wyszukiwanie O(1)), budowane jednokrotnie.
- Pobrane pliki są cache'owane (`data/raw/`, wolumen Dockera), więc kolejne budowy nie pobierają ich ponownie (`--force` wymusza pobranie).

**Transfer**
- Kolumnowy JSON: nazwy pól zapisane raz w `columns`, rekordy jako tablice.
- Kategorie jako maska bitowa (1 liczba zamiast listy tekstów).
- Współrzędne zaokrąglone do 5 miejsc po przecinku (~1 m), co wystarcza przy precyzji miejscowości.
- Rekordy posortowane przestrzennie, co daje lepszą kompresję gzip.
- Prekompresowany `places.json.gz` (serwer `scripts/serve.py` podaje go z `Content-Encoding: gzip`). GitHub Pages kompresuje automatycznie.
- Nagłówki cache: dane 1 h, pozostałe pliki 5 min.

**Przeglądarka**
- `<link rel="preload">` dla danych, więc pobieranie startuje równolegle z Leafletem. Skrypty mają `defer`, a `preconnect` jest ustawiony do serwerów kafelków i fontów.
- Renderer **Canvas** (`preferCanvas`) zamiast tysięcy elementów SVG/DOM.
- **Klastrowanie** z `chunkedLoading`: dodawanie markerów w porcjach nie blokuje interfejsu.
- Indeks wyszukiwania (tekst bez polskich znaków) budowany raz przy starcie. Filtrowanie to jeden przebieg po tablicy w pamięci.
- Debounce wyszukiwania 160 ms.
- Lista wyników stronicowana (80 pozycji), budowana przez `DocumentFragment`.
- Karta obiektu tworzona leniwie, dopiero przy otwarciu popupu.

**Pomiar.** Stopka aplikacji pokazuje czas pobrania danych i całkowity czas startu (`performance.now()`), a `#perf[data-filter-ms]` czas ostatniego filtrowania. Wyniki pomiarów są w [raporcie końcowym](raport-koncowy.md#4-rezultaty).

## 4. Bezpieczeństwo i prywatność

- Brak kluczy i haseł: API dane.gov.pl jest publiczne. Konfiguracja tylko przez zmienne środowiskowe (`.env.example`), a `.env` jest w `.gitignore`.
- Brak backendu i bazy danych, więc nie ma powierzchni ataku po stronie serwera.
- Lokalizacja użytkownika („Co jest blisko mnie?”) jest używana tylko w przeglądarce i nigdzie nie jest wysyłana.
- Teksty z danych są wstawiane przez `textContent`, nie `innerHTML` (ochrona przed XSS).
- Kontener działa jako użytkownik bez uprawnień roota.

## 5. Dostępność

Kontrast kolorów zgodny z WCAG AA dla tekstu. Widoczny fokus klawiatury. Link „Przejdź do listy”. Etykiety formularzy. `aria-live` dla liczby wyników. Obsługa `prefers-reduced-motion`. Krój Atkinson Hyperlegible zaprojektowany z myślą o czytelności dla osób słabowidzących.

## Historia zmian

| Wersja | Data | Autor | Opis zmian |
|---|---|---|---|
| 1.0 | 2026-11-21 | d4nf6c4c5d5b5-ai | Pierwsze wydanie. |
