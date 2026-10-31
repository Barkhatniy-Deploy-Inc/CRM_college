#!/usr/bin/env bash
# Run only against a disposable Compose project with an empty test volume.
set -euo pipefail
cd "$(dirname "$0")/.."
case "${COMPOSE_PROJECT_NAME:-}" in
  crmtest*) ;;
  *) echo 'Set COMPOSE_PROJECT_NAME to an isolated name beginning with crmtest.' >&2; exit 1 ;;
esac
if [[ "${PG_BACKUP_TEST_ALLOW:-}" != 1 ]]; then
  echo 'Set PG_BACKUP_TEST_ALLOW=1 only for a disposable test database.' >&2
  exit 1
fi

backup_parent=$(mktemp -d "${TMPDIR:-/tmp}/crm-backup-test.XXXXXX")
for service in auth schedule techcard; do
  docker compose exec -T db sh -ec '
    case "$1" in auth) db=$AUTH_DB_NAME;; schedule) db=$SCHEDULE_DB_NAME;; techcard) db=$TECHCARD_DB_NAME;; esac
    psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$db" -c "CREATE TABLE crm_backup_probe (value integer NOT NULL); INSERT INTO crm_backup_probe VALUES (12345);"
  ' -- "$service"
done
python3 scripts/postgres_backup.py "$backup_parent/archive"
for service in auth schedule techcard; do
  target="crm_backup_verify_$service"
  docker compose exec -T db sh -ec 'createdb -U "$POSTGRES_USER" "$1"' -- "$target"
  docker compose exec -T db sh -ec 'pg_restore --exit-on-error --no-owner --no-privileges -U "$POSTGRES_USER" -d "$1"' -- "$target" < "$backup_parent/archive/$service.dump"
  result=$(docker compose exec -T db sh -ec 'psql -X -A -t -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$1" -c "SELECT value FROM crm_backup_probe"' -- "$target")
  [[ "$result" == 12345 ]]
  echo "Verified $service backup and restored data"
done
printf 'Backup test archives: %s\n' "$backup_parent/archive"
