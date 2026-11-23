#!/bin/sh
# Start kontenera: buduje dane tylko wtedy, gdy trzeba, potem uruchamia serwer.
set -e
OUT=web/data/places.json

SAMPLE_MARK=web/data/.sample

if [ "$DATA_SOURCE" = "sample" ]; then
  python scripts/fetch_data.py --sample && touch "$SAMPLE_MARK"
elif [ "$REFRESH" = "1" ]; then
  python scripts/fetch_data.py --force && rm -f "$SAMPLE_MARK"
elif [ -f "$OUT" ] && [ ! -f "$SAMPLE_MARK" ]; then
  echo "✓ Mapa już zbudowana ($OUT) — start bez pobierania. Aktualizacja danych: REFRESH=1 docker compose up"
else
  echo "Pierwsze uruchomienie: pobieram dane z dane.gov.pl (ok. 2-3 min)…"
  if python scripts/fetch_data.py; then
    rm -f "$SAMPLE_MARK"
  else
    echo "! Nie udało się pobrać danych — uruchamiam wersję z próbką testową."
    python scripts/fetch_data.py --sample && touch "$SAMPLE_MARK"
  fi
fi

exec python scripts/serve.py
