# Dev launcher: always use the venv interpreter that lives next to this project.
#
#   .\run.ps1              -> python manage.py runserver
#   .\run.ps1 check        -> python manage.py check
#   .\run.ps1 test blog    -> python manage.py test blog
#
# Why: D:\python is a separate global Python (Django 6.0.4, no django-summernote).
# Running "python manage.py runserver" without an *active* venv picks that one up
# and fails with "ModuleNotFoundError: No module named 'django_summernote'".
#
# NOTE: do not set $ErrorActionPreference = 'Stop' here. Django writes progress
# and log lines to stderr, and PowerShell would turn those into terminating
# errors and kill runserver.

$candidates = @(
    (Join-Path (Split-Path -Parent $PSScriptRoot) 'venv\Scripts\python.exe'),
    (Join-Path $PSScriptRoot 'venv\Scripts\python.exe')
)

$venvPython = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $venvPython) {
    Write-Host 'venv python not found. Looked for:' -ForegroundColor Red
    $candidates | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    exit 1
}

Set-Location $PSScriptRoot

if ($args.Count -eq 0) {
    $args = @('runserver')
}

& $venvPython 'manage.py' @args
exit $LASTEXITCODE
