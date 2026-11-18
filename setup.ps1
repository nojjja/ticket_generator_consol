$ErrorActionPreference = 'Stop'

$launcher = Get-Command py -ErrorAction SilentlyContinue
if ($launcher) {
    & $launcher.Source -3 -m venv .venv
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Host 'Python 3 was not found. Install it from python.org, enable Add python.exe to PATH, then reopen PowerShell.'
        exit 1
    }
    & python -m venv .venv
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host 'The virtual environment Python could not run. Install Python from python.org, remove the broken .venv folder, then run .\setup.ps1 again.'
    exit $LASTEXITCODE
}
Write-Host 'Environment is ready. Start the app with .\run.ps1'
