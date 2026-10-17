<#
.SYNOPSIS
  Tampilkan semua URL aplikasi dan cek status HTTP-nya.

.EXAMPLE
  .\urls.ps1
  .\urls.ps1 -BaseUrl http://localhost:8001     # jika port di compose diubah

  Jika diblokir execution policy:
  powershell -ExecutionPolicy Bypass -File .\urls.ps1
#>
param(
    [string]$BaseUrl = "http://localhost:8000"
)

$BaseUrl = $BaseUrl.TrimEnd("/")

$endpoints = @(
    [pscustomobject]@{ Keperluan = "Root app";             Path = "/" }
    [pscustomobject]@{ Keperluan = "Swagger UI";           Path = "/docs" }
    [pscustomobject]@{ Keperluan = "ReDoc";                Path = "/redoc" }
    [pscustomobject]@{ Keperluan = "Skema OpenAPI (JSON)"; Path = "/openapi.json" }
    [pscustomobject]@{ Keperluan = "Endpoint Units";       Path = "/master-data/units" }
)

$results = $endpoints | ForEach-Object {
    $url = "$BaseUrl$($_.Path)"
    try {
        $status = (Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 5).StatusCode
    } catch {
        $status = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { "DOWN" }
    }
    [pscustomobject]@{ Keperluan = $_.Keperluan; URL = $url; Status = $status }
}

$results | Format-Table -AutoSize

Write-Host "Keterangan: 200 = OK | 404 di root = normal | 500 di Units = cek tabel/DB | DOWN = container belum jalan"
Write-Host "Cek log: docker compose logs --tail 50 web"