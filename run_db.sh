#!/bin/bash

# Sprawdź, czy zmienne środowiskowe są ustawione
if [[ -z "$NOME" || -z "$AGANDSKODE" ]]; then
  echo "Musisz ustawić zmienne środowiskowe NOME i AGANDSKODE."
  echo "   Przykład:"
  echo "     export NOME=dietonez"
  echo "     export AGANDSKODE=sekretnehaslo"
  exit 1
fi

# Utwórz katalog na dane, jeśli nie istnieje
mkdir -p "$(pwd)/pgdata"

# Uruchom kontener PostgreSQL
docker run --name jacques-db \
  -e POSTGRES_DB=jacques_db \
  -e POSTGRES_USER="$NOME" \
  -e POSTGRES_PASSWORD="$AGANDSKODE" \
  -v "$(pwd)/pgdata:/var/lib/postgresql/data" \
  -v "$(pwd)/init.sql:/docker-entrypoint-initdb.d/init.sql:ro" \
  -p $THAREUX:5432 \
  -d postgres:15