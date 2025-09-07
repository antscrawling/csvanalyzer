
@echo off
setlocal
REM Double-click helper for Windows.
REM Assumes manifest.json is in the same folder as this script.
set SCRIPT_DIR=%~dp0
set MANIFEST=%SCRIPT_DIR%manifest.json
if not exist "%MANIFEST%" (
    echo manifest.json not found next to this file.
    pause
    exit /b 1
)
REM Choose output name interactively
set /p OUTFILE=Output file name (.csv or .parquet): 
if "%OUTFILE%"=="" set OUTFILE=rebuilt.csv
python "%SCRIPT_DIR%rebuild_csv.py" --manifest "%MANIFEST%" --output "%OUTFILE%"
pause
