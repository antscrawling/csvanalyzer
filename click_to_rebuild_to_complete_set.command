#!/usr/bin/env bash
# Double-click helper for macOS/Linux.
DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST="$DIR/manifest.json"
if [ ! -f "$MANIFEST" ]; then
  echo "manifest.json not found next to this file."
  exit 1
fi
echo -n "Output file name (.csv or .parquet) [rebuilt.csv]: "
read OUTFILE
if [ -z "$OUTFILE" ]; then OUTFILE="rebuilt.csv"; fi
python3 "$DIR/rebuild_csv.py" --manifest "$MANIFEST" --output "$OUTFILE"
