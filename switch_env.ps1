param(
    [ValidateSet("local", "prod")]
    [string]$Mode = "local"
)

$Services = @("backend/auth", "backend/schedule", "backend/techcard")

Write-Host "Switching environment to: $Mode" -ForegroundColor Yellow

foreach ($Service in $Services) {
    $Source = "$Service/.env.$Mode"
    $Dest = "$Service/.env"

    if (Test-Path $Source) {
        Copy-Item -Path $Source -Destination $Dest -Force
        Write-Host "  [+] Updated $Service" -ForegroundColor Green
    } else {
        Write-Warning "  [-] Config $Source not found!"
    }
}

Write-Host "Environment switch complete." -ForegroundColor Green
