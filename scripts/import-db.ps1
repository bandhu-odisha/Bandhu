# Import bandhu_odisha_new.sql.gz into MySQL container
# Run from project root. Requires: Docker running, docker-compose up -d already done.

param(
    [string]$DumpGz = "$env:USERPROFILE\Desktop\bandhu_odisha_new.sql.gz",
    [string]$ProjectRoot = $PSScriptRoot + "\.."
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot

Write-Host "Bandhu DB Import" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan

# 1. Ensure MySQL container is running
Write-Host "`nChecking MySQL container..." -ForegroundColor Yellow
$running = docker ps --filter "name=bandhu-mysql" --format "{{.Names}}" 2>$null
if (-not $running) {
    Write-Host "Starting MySQL container (docker-compose up -d)..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "Waiting for MySQL to be ready (up to 60s)..." -ForegroundColor Yellow
    $waited = 0
    while ($waited -lt 60) {
        $ok = docker exec bandhu-mysql mysqladmin ping -h localhost -u root -pbandhu_root_pass 2>$null
        if ($LASTEXITCODE -eq 0) { break }
        Start-Sleep -Seconds 3
        $waited += 3
    }
    if ($waited -ge 60) { Write-Error "MySQL did not become ready." }
}
Write-Host "MySQL container is running." -ForegroundColor Green

# 2. Decompress dump if we have .gz
$sqlFile = Join-Path $ProjectRoot "bandhu_import.sql"
if (Test-Path $DumpGz) {
    Write-Host "`nDecompressing $DumpGz ..." -ForegroundColor Yellow
    $in = [System.IO.File]::OpenRead($DumpGz)
    $out = [System.IO.File]::Create($sqlFile)
    $gzip = [System.IO.Compression.GzipStream]::new($in, [System.IO.Compression.CompressionMode]::Decompress)
    $gzip.CopyTo($out)
    $gzip.Close(); $out.Close(); $in.Close()
    Write-Host "Decompressed to $sqlFile" -ForegroundColor Green
} elseif (Test-Path (Join-Path $ProjectRoot "dump_head.sql")) {
    $sqlFile = Join-Path $ProjectRoot "dump_head.sql"
    Write-Host "`nUsing existing dump_head.sql" -ForegroundColor Yellow
} else {
    Write-Error "No dump found. Put bandhu_odisha_new.sql.gz on Desktop or run with -DumpGz path."
}

# 3. Import into MySQL (streaming to avoid loading full dump in memory)
Write-Host "`nImporting into database bandhu_odisha_new (this may take a minute)..." -ForegroundColor Yellow
$sqlPath = (Resolve-Path $sqlFile).Path
cmd /c "docker exec -i bandhu-mysql mysql -u bandhu_root -pbandhu_local bandhu_odisha_new < `"$sqlPath`""
if ($LASTEXITCODE -ne 0) {
    Write-Error "Import failed. Check Docker and MySQL container."
}
Write-Host "Import completed." -ForegroundColor Green

# Cleanup temp if we created it
if ($sqlFile -eq (Join-Path $ProjectRoot "bandhu_import.sql")) {
    Remove-Item $sqlFile -Force -ErrorAction SilentlyContinue
}

Write-Host "`nDone. You can run: python manage.py runserver" -ForegroundColor Cyan
