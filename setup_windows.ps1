$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
py -m venv .venv
& "$root\.venv\Scripts\python.exe" -m pip install --upgrade pip
& "$root\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& "$root\.venv\Scripts\python.exe" scripts\generate_demo_data.py --days 60 --entities 12
& "$root\.venv\Scripts\python.exe" scripts\run_pipeline.py
& "$root\.venv\Scripts\python.exe" -m pytest -q tests
Write-Host "Setup complete. Start the dashboard with:"
Write-Host ".\.venv\Scripts\python.exe -m streamlit run app.py"

