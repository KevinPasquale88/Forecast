param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PipelineArgs
)
 
$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
 
function Write-Step {
    param([string]$Message)
    Write-Host "`n=====================================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
}
 
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor DarkCyan
}
 
function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}
 
function Write-ErrorAndExit {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    exit 1
}
 
Write-Step "STARTING FULL PIPELINE - PYTHON PROJECT"
 
Write-Info "Checking for Python 3..."
$pythonCmd = $null
 
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
    $pythonVersion = & py -3 --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        $pythonCmd = $null
    }
}
 
if (-not $pythonCmd -and (Get-Command python -ErrorAction SilentlyContinue)) {
    $pythonCmd = "python"
    $pythonVersion = & python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        $pythonCmd = $null
    }
}
 
if (-not $pythonCmd) {
    Write-Warn "Python was not found in PATH."
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Info "Attempting to install Python with Winget..."
        winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
        Write-ErrorAndExit "Please reopen PowerShell and run the script again."
    }
    Write-ErrorAndExit "Install Python 3 from https://www.python.org/downloads/windows/"
}
 
Write-Info "Python found: $pythonVersion"
 
Write-Step "SETTING UP PYTHON ENVIRONMENT"
Write-Info "Checking whether the virtual environment already exists..."
if (-not (Test-Path "env\Scripts\python.exe")) {
    Write-Info "Creating a new virtual environment in ./env"
    & $pythonCmd -3 -m venv env
    if ($LASTEXITCODE -ne 0) { Write-ErrorAndExit "Unable to create the virtual environment." }
} else {
    Write-Info "Virtual environment already exists."
}
 
Write-Info "Activating the virtual environment..."
. .\env\Scripts\Activate.ps1
 
Write-Info "Installing dependencies from requirements.txt..."
& python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { Write-ErrorAndExit "pip upgrade failed." }
& pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Write-ErrorAndExit "Dependency installation failed." }
 
Write-Step "CHECKING OLLAMA"
Write-Info "Checking whether Ollama is installed and reachable..."
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-ErrorAndExit "Ollama was not found. Install it from https://ollama.com/download/windows"
}
 
$ollamaRunning = $false
try {
    $null = & ollama ps 2>$null
    if ($LASTEXITCODE -eq 0) { $ollamaRunning = $true }
} catch {}
 
if (-not $ollamaRunning) {
    Write-Info "Starting Ollama in the background..."
    Start-Process ollama -ArgumentList 'serve' -WindowStyle Hidden
    Start-Sleep -Seconds 5
}
 
Write-Info "Verifying required Ollama models..."
$models = @(
    'jeffh/intfloat-e5-base-v2:q8_0',
    'twwch/m3e-base',
    'zyw0605688/gte-large-zh',
    'jeffh/intfloat-multilingual-e5-large-instruct:q8_0'
)
 
foreach ($model in $models) {
    $installed = & ollama list 2>$null | Select-String -Pattern [regex]::Escape($model)
    if ($installed) {
        Write-Info "Model already available: $model"
    } else {
        Write-Info "Downloading model: $model"
        & ollama pull $model
        if ($LASTEXITCODE -ne 0) { Write-ErrorAndExit "Failed to download model $model" }
    }
}
 
Write-Step "RUNNING PYTHON PIPELINE"
Write-Info "Launching main.py with the provided arguments..."
& python main.py @PipelineArgs
if ($LASTEXITCODE -ne 0) { Write-ErrorAndExit "The pipeline terminated with an error." }
 
Write-Step "PIPELINE COMPLETED"
Write-Host "Results are available in the project output folders." -ForegroundColor Green
Write-Host "Report generated: report.md and report.pdf" -ForegroundColor Green