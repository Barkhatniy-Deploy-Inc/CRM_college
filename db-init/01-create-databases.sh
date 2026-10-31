#!/bin/sh
set -eu

if [ -z "$AUTH_DB_NAME" ] || [ -z "$SCHEDULE_DB_NAME" ] || [ -z "$TECHCARD_DB_NAME" ] || \
   [ "$AUTH_DB_NAME" = "$SCHEDULE_DB_NAME" ] || [ "$AUTH_DB_NAME" = "$TECHCARD_DB_NAME" ] || \
   [ "$SCHEDULE_DB_NAME" = "$TECHCARD_DB_NAME" ]; then
  echo 'Database names must be non-empty and distinct' >&2
  exit 1
fi

# The official Postgres entrypoint runs this only for a new data volume.
# SQL variables and format(%I) safely quote configurable database identifiers.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
  --set=auth_db="$AUTH_DB_NAME" \
  --set=schedule_db="$SCHEDULE_DB_NAME" \
  --set=techcard_db="$TECHCARD_DB_NAME" <<'SQL'
SELECT format('CREATE DATABASE %I', name)
FROM (SELECT DISTINCT unnest(ARRAY[:'auth_db', :'schedule_db', :'techcard_db']) AS name) requested
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = requested.name)
\gexec
SQL
