#!/bin/bash
TOKEN=$(cat github-pat.txt)
docker run --rm -i \
  -v "$(pwd)/config.js:/usr/src/app/config.js" \
  -e RENOVATE_TOKEN="$TOKEN" \
  -e LOG_LEVEL="debug" \
  renovate/renovate:42.76

  # -e RENOVATE_FETCH_CHANGELOGS="disabled" \
  # -e RENOVATE_FETCH_RELEASE_NOTES="disabled" \
# Remove --dry-run=full after testing
# Change LOG_LEVEL to "debug" for detailed logs