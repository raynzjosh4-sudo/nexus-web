# Run daily sitemap generation and ping Google
$ErrorActionPreference = 'Stop'

Write-Host "Running sitemap generation: $(Get-Date)"

# Path to project
$projectDir = "C:\nexus websites\nexus_web"
# Prefer virtualenv python if available
$venvPython = Join-Path $projectDir "venv\Scripts\python.exe"
$python = if (Test-Path $venvPython) { $venvPython } else { 'python' }

Push-Location $projectDir

# Run generator
& $python run_sitemap_generation.py
$exit = $LASTEXITCODE
if ($exit -ne 0) {
    Write-Host "Sitemap generation failed with exit code $exit" -ForegroundColor Red
    Pop-Location
    exit $exit
}

Write-Host "Sitemap generation completed successfully." -ForegroundColor Green

# Ping Google to notify of new sitemap
$sitemapUrl = 'https://static.nexassearch.com/static/sitemaps/sitemap_index.xml'
try {
    Write-Host "Pinging Google for sitemap: $sitemapUrl"
    $resp = Invoke-WebRequest -Uri "https://www.google.com/ping?sitemap=$([System.Uri]::EscapeDataString($sitemapUrl))" -UseBasicParsing -Method Get -TimeoutSec 30
    Write-Host "Google ping response status: $($resp.StatusCode)"
} catch {
    Write-Host "Google ping failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Pop-Location
Write-Host "Done."