#!/usr/bin/env bash
# usage: ./safety.sh

echo "Checking libraries with safety ..."
poetry export --without-hashes -f requirements.txt | safety check --full-report --stdin
