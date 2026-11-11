#!/usr/bin/env bash
# Affiche le site en local. Ne lit que .env et n'écrit rien dans Neon.
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -f .env ]]; then
  echo "Fichier .env manquant : il doit contenir DATABASE_URL en lecture seule." >&2
  exit 1
fi

if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi

exec .venv/bin/python serve.py
