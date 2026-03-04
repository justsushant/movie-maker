#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -d "$ROOT_DIR/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
elif [[ -d "$ROOT_DIR/venv" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/venv/bin/activate"
else
  echo "No virtualenv found. Expected .venv/ or venv/ in project root." >&2
  exit 1
fi

cd "$ROOT_DIR"
python -m pytest tests/ -v
