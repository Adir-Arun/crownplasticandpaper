#!/usr/bin/env bash
# Vercel build: apply the upgrade layer to the committed snapshot in site/.
set -euo pipefail
test -f site/index.html || { echo "site/ is missing: run the 'Snapshot live site' GitHub Action"; exit 1; }
python3 upgrade/apply.py site
