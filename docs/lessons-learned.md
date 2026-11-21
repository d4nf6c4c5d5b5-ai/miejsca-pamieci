# Lessons learned

| Metryka | |
|---|---|
| Identyfikator | MP-DOC-003 |
| Wersja | 1.1 |
| Status | Zatwierdzony |
| Autor | d4nf6c4c5d5b5-ai |
| Data | 2026-11-21 |
| Podstawa | PMI, PMBOK® Guide: proces zbierania i rejestrowania wniosków (lessons learned register) |

## 1. Co zadziałało

| ID | Obszar | Opis | Dlaczego zadziałało |
|---|---|---|---|
| LL-01 | Dane | Sprawdzenie dostępności danych **przed** wyborem tematu | Pierwszy pomysł (porównywarka szkół) upadł po 30 minutach, a nie po tygodniu: wyników egzaminów na poziomie szkół nie ma na dane.gov.pl |
| LL-02 | Dane | Pobieranie adresów plików z API zamiast wpisywania ich na sztywno | Pliki NID zmieniają adres przy każdej aktualizacji, a skrypt dalej działa |
| LL-03 | Architektura | „Oblicz raz, serwuj statycznie” | Darmowy hosting, natychmiastowe filtrowanie, brak serwera do utrzymania |
| LL-04 | Jakość | Testy na prawdziwych rekordach w oryginalnym kodowaniu (cp1250) | Wykryły problemy z kodowaniem i fałszywe trafienia reguł, zanim trafiły na mapę |
| LL-05 | Uruchamianie | Brak zależności (tylko stdlib) | `docker compose up` i `python3 scripts/fetch_data.py` działają bez `pip install` |
| LL-06 | Dane | Łączenie zbiorów różnych instytucji (NID + GUGiK) | Rejestr bez współrzędnych stał się mapą dzięki PRNG: 100% dopasowań |

## 2. Co nie zadziałało albo sprawiło problem

| ID | Obszar | Problem | Skutek | Jak rozwiązano |
|---|---|---|---|---|
| LL-07 | Dane | Rejestr zabytków **nie ma współrzędnych**, a REST API NID też ich nie zwraca (tylko Pomniki Historii je mają) | Nie dało się od razu pokazać obiektów na mapie | Geokodowanie po PRNG z dokładnością do miejscowości i jawna informacja o tym w karcie obiektu |
| LL-08 | Dane | Kodowanie Windows-1250 w CSV bez deklaracji | Polskie znaki jako „�” przy naiwnym odczycie | Wykrywanie: UTF-8, a przy błędzie cp1250 |
| LL-09 | Dane | Dla PRNG pole `file_url` w dane.gov.pl wskazuje kopię z **2021 r.** | Ryzyko budowy na nieaktualnych danych | Priorytet dla pola `link` (aktualny plik GUGiK), `download_url` jako zapas |
| LL-10 | Klasyfikacja | Proste słowa kluczowe dają fałszywe trafienia: „schronisko” (schron), „fortepian” (fort), „pomnik nagrobny”, kapliczka „Męczeńskiej śmierci” | Na mapie pojawiłyby się obiekty niezwiązane z tematem | Lista wykluczeń + test dla każdego znalezionego przypadku |
| LL-11 | Klasyfikacja | „I wojna” zawiera się w „II wojna” | Cmentarze z II wojny trafiały do I wojny | Wyrażenie z lookbehind `(?<![I\w])I\s+wojn` + test |
| LL-13 | Klasyfikacja | Słowo „mauzoleum” w regule „miejsca pamięci” złapało 385 rodzinnych kaplic grobowych | Co ósmy obiekt na mapie był nie na temat | Przegląd próbki po pierwszej pełnej budowie, zawężenie reguły + testy (v1.0.1) |
| LL-12 | Klasyfikacja | Nazwy gmin zapisane inaczej w NID i PRNG („Słomniki - obszar wiejski” i „Słomniki-gmina miejsko-wiejska”) | Brak dopasowań | Normalizacja do rdzenia nazwy gminy |

## 3. Co zrobilibyśmy inaczej

1. **Prototyp na danych w pierwszej godzinie.** Najwięcej ryzyka było w danych (brak współrzędnych, kodowanie), nie w interfejsie. Wczesny „spike” na pełnym pliku oszczędza czas.
2. **Ręczna próbka kontrolna od początku:** 100 losowych obiektów oznaczonych przez człowieka, żeby liczyć precyzję i czułość reguł liczbowo, a nie tylko przeglądem przykładów.
3. **Wcześniejszy kontakt z wydawcą danych** (NID) w sprawie współrzędnych obiektów rejestru. Mapa zabytek.pl je ma, więc istnieją, ale nie ma ich w otwartym zbiorze.
4. **Krótsza lista kategorii na start** (np. 4) i dopiero potem rozszerzanie. Mniej reguł to mniej przypadków brzegowych do przetestowania.

## 4. Rekomendacje

| ID | Dla kogo | Rekomendacja |
|---|---|---|
| R-01 | Kolejne projekty | Zaczynać od pytania „czy dane naprawdę istnieją w potrzebnej szczegółowości?”, a nie od pomysłu na aplikację. |
| R-02 | Kolejne projekty | Zapisywać metadane każdego pobrania (zasób, data danych, rozmiar), żeby wynik był odtwarzalny i porównywalny w czasie. |
| R-03 | Kolejne projekty | Reguły klasyfikacji trzymać jawnie w kodzie z testami. Każdy fałszywy wynik zgłoszony przez użytkownika to nowy test. |
| R-04 | Narodowy Instytut Dziedzictwa | Dodać współrzędne (lub geometrię) do otwartego zbioru 1130, tak jak w zbiorze Pomników Historii. Zwiększy to wartość danych dla wszystkich użytkowników. |
| R-05 | Narodowy Instytut Dziedzictwa | Publikować CSV w UTF-8 albo deklarować kodowanie w opisie zasobu. |
| R-06 | Rozwój projektu | Dodać opisy historyczne (np. z Wikipedii lub Wikidanych po identyfikatorze) i warstwę „trasy edukacyjne” dla szkół. |

## Historia zmian

| Wersja | Data | Autor | Opis zmian |
|---|---|---|---|
| 1.0 | 2026-11-21 | d4nf6c4c5d5b5-ai | Pierwsze wydanie po zakończeniu projektu. |
| 1.1 | 2026-11-21 | d4nf6c4c5d5b5-ai | Dodano LL-13 (fałszywe trafienia „mauzoleum”). |
