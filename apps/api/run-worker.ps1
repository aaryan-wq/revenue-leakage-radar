# Run Celery worker from apps/api with the project virtualenv.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$venvCelery = Join-Path $PSScriptRoot ".venv\Scripts\celery.exe"
if (-not (Test-Path $venvCelery)) {
    Write-Error "Virtualenv not found. Run: python -m venv .venv; .venv\Scripts\pip install -r requirements.txt"
}

# Windows requires --pool=solo (prefork causes PermissionError).
& $venvCelery -A workers.celery_app worker -l info --pool=solo @args
