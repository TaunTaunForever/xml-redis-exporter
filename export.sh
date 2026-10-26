#!/bin/sh

set -eu

verbose=""

if [ "${1:-}" = "-v" ]; then
    verbose="-v"
    shift
fi

if [ "$#" -ne 1 ]; then
    echo "Usage: ./export.sh [-v] /path/to/xml"
    exit 1
fi

xml_path="$1"

if [ ! -f "$xml_path" ]; then
    echo "XML file not found: $xml_path"
    exit 1
fi

docker compose up -d --wait redis

docker compose run --rm \
    -v "$(cd "$(dirname "$xml_path")" && pwd)/$(basename "$xml_path"):/data/input.xml:ro" \
    exporter $verbose /data/input.xml