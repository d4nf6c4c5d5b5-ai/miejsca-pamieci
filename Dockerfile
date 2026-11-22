# Miejsca Pamięci — obraz z potokiem danych i serwerem statycznym.
# Tylko biblioteka standardowa Pythona: brak instalacji zależności.
FROM python:3.12-alpine

LABEL org.opencontainers.image.title="miejsca-pamieci" \
      org.opencontainers.image.description="Mapa miejsc pamięci w Polsce (dane.gov.pl)" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080 DATA_DIR=/data/raw
WORKDIR /app
COPY src ./src
COPY scripts ./scripts
COPY tests ./tests
COPY web ./web

# Biblioteki mapy pobierane przy budowie obrazu (strona nie zależy od CDN).
RUN python scripts/fetch_vendor.py || echo "Brak sieci przy budowie: strona użyje CDN jako zapasu"

RUN adduser -D -H app && mkdir -p /data/raw && chown -R app /data /app/web
USER app
EXPOSE 8080

# Przy starcie: pobierz dane (jeśli brak w wolumenie), zbuduj places.json, uruchom serwer.
# DATA_SOURCE=sample -> wersja offline z próbki testowej.
CMD ["sh", "-c", "if [ \"$DATA_SOURCE\" = sample ]; then python scripts/fetch_data.py --sample; else python scripts/fetch_data.py || python scripts/fetch_data.py --sample; fi && exec python scripts/serve.py"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=120s \
  CMD wget -qO- http://127.0.0.1:${PORT}/ >/dev/null || exit 1
