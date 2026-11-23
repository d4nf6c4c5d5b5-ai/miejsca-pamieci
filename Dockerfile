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

RUN adduser -D -H app && mkdir -p /data/raw /app/web/data && chown -R app /data /app/web
USER app
EXPOSE 8080

# Przy starcie:
#  - jeśli w wolumenie jest już zbudowana mapa (web/data/places.json) -> start w kilka sekund,
#  - jeśli nie: pobierz dane z dane.gov.pl i zbuduj (pierwszy raz ok. 2-3 min),
#  - REFRESH=1 wymusza ponowne pobranie danych, DATA_SOURCE=sample -> próbka offline.
CMD ["sh", "scripts/docker-start.sh"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=120s \
  CMD wget -qO- http://127.0.0.1:${PORT}/ >/dev/null || exit 1
