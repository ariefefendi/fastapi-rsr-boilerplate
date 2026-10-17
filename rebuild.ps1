<#
.SYNOPSIS
  Rebuild image TANPA cache lalu restart container.

.EXAMPLE
  .\rebuild.ps1                 # rebuild no-cache + restart (data MySQL AMAN)
  .\rebuild.ps1 -Fresh          # sama, tapi HAPUS volume MySQL (database kosong lagi)
  .\rebuild.ps1 -Prune          # sama, tapi bersihkan juga build cache Docker
  .\rebuild.ps1 -NoLogs         # tidak menampilkan log di akhir

  Jika diblokir execution policy:
  powershell -ExecutionPolicy Bypass -File .\rebuild.ps1
#>
param(
    [switch]$Fresh,
    [switch]$Prune,
    [switch]$NoLogs
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

function Run($cmd) {
    Write-Host ">> $cmd" -ForegroundColor Cyan
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) { throw "Perintah gagal: $cmd" }
}

if ($Fresh) {
    Write-Host "PERINGATAN: volume MySQL akan DIHAPUS (semua data hilang)." -ForegroundColor Yellow
    $ans = Read-Host "Lanjut? (y/N)"
    if ($ans -ne "y") { Write-Host "Dibatalkan."; exit 0 }
    Run "docker compose down --volumes --remove-orphans"
} else {
    Run "docker compose down --remove-orphans"
}

if ($Prune) {
    Run "docker builder prune -f"
}

# --no-cache : abaikan semua layer cache
# --pull     : ambil ulang base image (python:3.12-slim) versi terbaru
Run "docker compose build --no-cache --pull"

# --force-recreate : buat ulang container walau konfigurasi tidak berubah
# --renew-anon-volumes : jangan pakai ulang anonymous volume lama
Run "docker compose up -d --force-recreate --renew-anon-volumes"

Run "docker compose ps"

if (-not $NoLogs) {
    Write-Host "Menampilkan log (Ctrl+C untuk keluar, container tetap jalan)..." -ForegroundColor Green
    docker compose logs -f web
}
