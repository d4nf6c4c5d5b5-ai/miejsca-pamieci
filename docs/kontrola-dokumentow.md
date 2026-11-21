# Rejestr i zasady kontroli dokumentów

| Metryka | |
|---|---|
| Identyfikator | MP-DOC-001 |
| Wersja | 1.0 |
| Status | Zatwierdzony |
| Autor | d4nf6c4c5d5b5-ai |
| Data | 2026-11-21 |
| Podstawa | ISO 10013 (wytyczne dla udokumentowanej informacji) |

## 1. Cel

Dokument określa, jak w projekcie Miejsca Pamięci tworzymy, identyfikujemy, wersjonujemy, zatwierdzamy i przechowujemy dokumenty. Zawiera też rejestr wszystkich dokumentów.

## 2. Zasady

### 2.1. Identyfikacja

Każdy dokument ma niepowtarzalny identyfikator `MP-DOC-NNN` (MP = Miejsca Pamięci, NNN = kolejny numer). Identyfikator nie zmienia się przy kolejnych wersjach. Numerów wycofanych dokumentów nie używamy ponownie.

### 2.2. Metryka dokumentu

Dokumenty w `docs/` zaczynają się tabelą metryki: identyfikator, wersja, status, autor, data, ewentualnie podstawa. Kończą się tabelą **Historia zmian**. Pliki w katalogu głównym (README, CONTRIBUTING itd.) mają skróconą metrykę w stopce, bo GitHub wyświetla je jako stronę projektu.

### 2.3. Wersjonowanie

- `X.0`: zmiana istotna (nowa sekcja, zmiana ustaleń, nowe dane);
- `X.Y`: poprawka redakcyjna lub uzupełnienie.

Każda zmiana wersji dostaje wiersz w historii zmian: wersja, data, autor, opis.

### 2.4. Statusy

`Projekt` → `Do przeglądu` → `Zatwierdzony` → (`Wycofany`).

### 2.5. Przegląd i zatwierdzanie

Zmiany w dokumentach przechodzą przez pull request, tak jak kod. Zatwierdzenie oznacza akceptację PR przez opiekuna repozytorium. Pełny ślad zmian (kto, kiedy, co) zapewnia historia Git.

### 2.6. Przechowywanie i dostęp

Dokumenty są plikami Markdown w publicznym repozytorium. Wersją obowiązującą jest wersja na gałęzi `main`. Starsze wersje są dostępne w historii Git i w wydaniach (tagach).

### 2.7. Dokumenty zewnętrzne

Dokumenty zewnętrzne (opisy zbiorów na dane.gov.pl, dokumentacja API, legenda kolumn PRNG) przywołujemy linkiem w [metodologii](metodologia.md) i nie kopiujemy ich do repozytorium.

## 3. Rejestr dokumentów

| ID | Dokument | Plik | Wersja | Status | Autor | Data |
|---|---|---|---|---|---|---|
| MP-DOC-000 | README: opis projektu i uruchomienie | [`README.md`](../README.md) | 1.0 | Zatwierdzony | d4nf6c4c5d5b5-ai | 2026-11-21 |
| MP-DOC-001 | Rejestr i zasady kontroli dokumentów | [`docs/kontrola-dokumentow.md`](kontrola-dokumentow.md) | 1.0 | Zatwierdzony | d4nf6c4c5d5b5-ai | 2026-11-21 |
| MP-DOC-002 | Raport końcowy | [`docs/raport-koncowy.md`](raport-koncowy.md) | 1.0 | Zatwierdzony | d4nf6c4c5d5b5-ai | 2026-11-21 |
| MP-DOC-003 | Lessons learned | [`docs/lessons-learned.md`](lessons-learned.md) | 1.0 | Zatwierdzony | d4nf6c4c5d5b5-ai | 2026-11-21 |
| MP-DOC-004 | Metodologia danych | [`docs/metodologia.md`](metodologia.md) | 1.0 | Zatwierdzony | d4nf6c4c5d5b5-ai | 2026-11-21 |
| MP-DOC-005 | Architektura i wydajność | [`docs/architektura.md`](architektura.md) | 1.0 | Zatwierdzony | d4nf6c4c5d5b5-ai | 2026-11-21 |
| MP-DOC-006 | Zasady współtworzenia | [`CONTRIBUTING.md`](../CONTRIBUTING.md) | 1.0 | Zatwierdzony | d4nf6c4c5d5b5-ai | 2026-11-21 |
| MP-DOC-007 | Kodeks postępowania | [`CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md) | 1.0 | Zatwierdzony | d4nf6c4c5d5b5-ai | 2026-11-21 |
| MP-DOC-008 | Rejestr zmian | [`CHANGELOG.md`](../CHANGELOG.md) | 1.0 | Zatwierdzony | d4nf6c4c5d5b5-ai | 2026-11-21 |

## Historia zmian

| Wersja | Data | Autor | Opis zmian |
|---|---|---|---|
| 1.0 | 2026-11-21 | d4nf6c4c5d5b5-ai | Pierwsze wydanie: zasady i rejestr 9 dokumentów. |
