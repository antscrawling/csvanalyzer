# CSV Chunker Toolkit

Create compressed, memory‑efficient chunks from a huge CSV and later rebuild them
back into a single CSV for Excel (or keep as Parquet for analytics).

## What's inside
- **pack_csv.py** — split a CSV into compressed Parquet chunks + a manifest.
- **rebuild_csv.py** — rebuild the chunks back to a single CSV (Excel-friendly) or Parquet.
- **click_to_rebuild_to_complete_set.bat** — Windows double‑click wrapper.
- **click_to_rebuild_to_complete_set.command** — macOS/Linux double‑click wrapper.
- **requirements.txt** — dependencies.

## Quick start

1) Install deps (once):
   ```bash
   python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2) Pack a huge CSV into chunks (default ~128MB parquet parts):
   ```bash
   python pack_csv.py --input your_big.csv --outdir chunks_out --target-size-mb 128
   ```
   Options:
   - `--target-size-mb` target compressed size per chunk (approximate).
   - `--rows-per-chunk` force row-based chunking instead (overrides target size).
   - `--compression zstd|snappy|gzip` default: zstd.
   - `--delimiter` default: ","
   - `--encoding` default: "utf-8"

3) Rebuild to a single CSV for Excel:
   ```bash
   python rebuild_csv.py --manifest chunks_out/manifest.json --output rebuilt.csv
   ```
   Or rebuild to a single Parquet:
   ```bash
   python rebuild_csv.py --manifest chunks_out/manifest.json --output rebuilt.parquet
   ```

## Make a true one‑file “click to rebuild” app (optional)
Use PyInstaller to create a single‑file executable for your platform:
```bash
pip install pyinstaller
pyinstaller --onefile rebuild_csv.py
# Windows output: dist\rebuild_csv.exe  (rename to click_to_rebuild_to_complete_set.exe)
# macOS output:   dist/rebuild_csv       (rename to click_to_rebuild_to_complete_set)
```

## Why Parquet chunks?
- Columnar + compressed (zstd/snappy) → **much smaller** and **faster** than CSV.
- Cross‑platform and widely supported (Python/pandas/Arrow/Spark/DuckDB/Polars).

## Fast alternatives for very large data
- **DuckDB**: query CSVs directly and write Parquet/Arrow super fast.
  ```bash
  duckdb -c "COPY (SELECT * FROM 'your_big.csv') TO 'your_big.parquet' (FORMAT 'parquet');"
  ```
- **SQLite**: `sqlite-utils insert` can ingest CSV and let you query without loading all rows into RAM.
- **Polars**: `scan_csv` + `sink_parquet` for streaming transformations.

# CSV Analyzer

This project provides tools for analyzing retail sales data, including a FastAPI-based API (`app.py`) and a data generation script (`main.py`) that creates a DuckDB database.
