#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
. .venv/bin/activate
PIP_NO_CACHE_DIR=1 python -m pip install --disable-pip-version-check -r requirements-dev.txt
