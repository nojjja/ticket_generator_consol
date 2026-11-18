$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Host 'Virtual environment is missing. Run .\setup.ps1 first.'
    exit 1
}
& $python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host 'The virtual environment Python is broken. Install Python from python.org, remove .venv, and run .\setup.ps1 again.'
    exit $LASTEXITCODE
}
& $python (Join-Path $PSScriptRoot 'main.py')
