#!/usr/bin/env bash
# Purpose: Push the README and a short tagline to the Docker Hub repository page
# Scope: Docker Hub repository metadata for washad/thailint
# Overview: Docker Hub stores a page description independently of the image, and `docker push`
#     never sets it, so a repository can accumulate pulls while its page stays blank. This script
#     authenticates with the Docker Hub API using the same credentials the publish flow already
#     loads, then PATCHes the short description and the full description, using README.md verbatim
#     for the latter. Run automatically as part of `just publish`, and safe to run on its own.
# Dependencies: curl, python3, .env carrying DOCKERHUB_USERNAME and DOCKERHUB_TOKEN, README.md
# Exports: Exit codes (0=synced, 1=error)
# Interfaces: No arguments; reads credentials from .env and content from README.md
# Related: scripts/publish.sh, justfile (_publish-docker-only)

set -euo pipefail

SHORT_DESCRIPTION="Catch the mistakes AI coding assistants keep making - a multi-language linter for AI-generated code."

if [ ! -f .env ]; then
    echo "❌ .env not found; cannot read Docker Hub credentials." >&2
    exit 1
fi

DOCKERHUB_USERNAME=$(grep '^DOCKERHUB_USERNAME=' .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")
DOCKERHUB_TOKEN=$(grep '^DOCKERHUB_TOKEN=' .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")

if [ -z "$DOCKERHUB_USERNAME" ] || [ -z "$DOCKERHUB_TOKEN" ]; then
    echo "❌ DOCKERHUB_USERNAME or DOCKERHUB_TOKEN missing from .env" >&2
    exit 1
fi

echo "Authenticating with the Docker Hub API..."
JWT=$(curl -s -X POST https://hub.docker.com/v2/users/login/ \
    -H "Content-Type: application/json" \
    -d "$(U="$DOCKERHUB_USERNAME" P="$DOCKERHUB_TOKEN" python3 -c "
import json, os
print(json.dumps({'username': os.environ['U'], 'password': os.environ['P']}))
")" | python3 -c "
import sys, json
try:
    print(json.load(sys.stdin).get('token', ''))
except Exception:
    print('')
")

if [ -z "$JWT" ]; then
    echo "❌ Docker Hub API authentication failed." >&2
    exit 1
fi
echo "✓ Authenticated"

echo "Pushing description to hub.docker.com/r/$DOCKERHUB_USERNAME/thailint ..."
PAYLOAD=$(python3 -c "
import json, sys
short = sys.argv[1]
full = open('README.md', encoding='utf-8').read()
print(json.dumps({'description': short, 'full_description': full}))
" "$SHORT_DESCRIPTION")

STATUS=$(curl -s -o /tmp/dockerhub-sync-response.json -w '%{http_code}' \
    -X PATCH "https://hub.docker.com/v2/repositories/$DOCKERHUB_USERNAME/thailint/" \
    -H "Authorization: JWT $JWT" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

if [ "$STATUS" != "200" ]; then
    echo "❌ Docker Hub rejected the update (HTTP $STATUS):" >&2
    head -c 400 /tmp/dockerhub-sync-response.json >&2
    echo >&2
    exit 1
fi

echo "✓ Docker Hub page description synced from README.md"
