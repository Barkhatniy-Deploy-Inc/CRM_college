#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

compose() { docker compose "$@"; }

case "${1:-help}" in
  init)
    python3 - <<'PY'
from pathlib import Path
import os
import secrets
import re

target = Path('.env')
content = Path('.env.example').read_text()
content = content.replace('DB_PASSWORD=\n', f'DB_PASSWORD={secrets.token_hex(24)}\n')
content = content.replace('SECRET_KEY=\n', f'SECRET_KEY={secrets.token_hex(32)}\n')
content = content.replace('INTERNAL_API_TOKEN=\n', f'INTERNAL_API_TOKEN={secrets.token_hex(32)}\n')
try:
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
except FileExistsError:
    existing = target.read_text()
    if not re.search(r'(?m)^\s*(?:export\s+)?INTERNAL_API_TOKEN\s*=', existing):
        with target.open('a') as env_file:
            env_file.write('\nINTERNAL_API_TOKEN=' + secrets.token_hex(32) + '\n')
        print('Added missing INTERNAL_API_TOKEN; existing settings were preserved.')
    else:
        print('.env already exists; kept the existing configuration.')
else:
    with os.fdopen(descriptor, 'w') as env_file:
        env_file.write(content)
    print('Created .env with generated secrets (permissions 0600).')
PY
    ;;
  up)
    compose config --quiet
    compose up -d --build --wait --wait-timeout 180
    ;;
  migrate)
    compose up -d --wait --wait-timeout 120 db
    for service in auth schedule techcard; do
      compose run --build --rm --no-deps "$service" alembic upgrade head
    done
    ;;
  tunnel)
    # Read the resolved token without printing it or evaluating .env as shell code.
    compose --profile tunnel config --format json | python3 -c '
import json, sys
token = json.load(sys.stdin)["services"]["ngrok"]["environment"].get("NGROK_AUTHTOKEN", "")
if not token or not token.strip():
    sys.exit("Set NGROK_AUTHTOKEN in .env before starting the tunnel.")
'
    compose up -d --build --wait --wait-timeout 180
    compose --profile tunnel up -d ngrok
    echo 'Tunnel inspector: http://localhost:4040 (default port). Run ./scripts/local.sh url.'
    ;;
  url)
    compose --profile tunnel exec -T ngrok wget -qO- http://127.0.0.1:4040/api/tunnels | python3 -c '
import json, sys
urls = [t["public_url"] for t in json.load(sys.stdin).get("tunnels", []) if t["public_url"].startswith("https://")]
if not urls:
    sys.exit("Tunnel is not ready. Check: docker compose --profile tunnel logs ngrok")
print("\n".join(urls))
'
    ;;
  down)
    compose --profile tunnel down
    ;;
  logs)
    compose --profile tunnel logs --tail=100 -f "${@:2}"
    ;;
  status)
    compose --profile tunnel ps -a
    ;;
  check)
    python3 scripts/check_local.py "${2:-http://localhost:8080}"
    ;;
  *)
    echo 'Usage: ./scripts/local.sh {init|up|migrate|tunnel|url|down|logs [service]|status|check [base-url]}'
    ;;
esac
