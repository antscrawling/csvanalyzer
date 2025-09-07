#!/bin/bash
# Script to run 'ruff check --fix' on all Python files in the current directory

for file in *.py; do
  if [ -f "$file" ]; then
    ruff check "$file" --fix
  fi
done
