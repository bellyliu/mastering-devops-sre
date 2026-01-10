#!/bin/bash
TOKEN=$(cat github-pat.txt)
docker run --rm \
  -v "$(pwd)/config.js:/usr/src/app/config.js" \
  -e RENOVATE_TOKEN="$TOKEN" \
  renovate/renovate:42.76 

# --dry-run=full