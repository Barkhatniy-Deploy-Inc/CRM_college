# 0. Setup Environment & Cleanup
Write-Host "Setting up Local Environment..." -ForegroundColor Yellow

# Create logs directory
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Start Transcript
Start-Transcript -Path "logs\startup_script.log" -Append

# KILL PREVIOUS PROCESSES to avoid port conflicts and file locks
Write-Host "Killing old processes..." -ForegroundColor Red
Try { Stop-Process -Name "go" -ErrorAction SilentlyContinue } Catch {}
Try { Stop-Process -Name "node" -ErrorAction SilentlyContinue } Catch {}
# Note: execution might fail if we don't have permission or if they aren't running. SilentlyContinue handles that.

# Switch .env files to local
.\switch_env.ps1 local

# Verify build BEFORE starting (Fail fast)
Write-Host "Verifying builds..." -ForegroundColor Yellow
$buildErrors = $false

Write-Host "Building Auth..."
Push-Location backend/auth
go build -o auth_service.exe main.go
if ($LASTEXITCODE -ne 0) { Write-Host "Auth build failed!" -ForegroundColor Red; $buildErrors = $true }
Pop-Location

Write-Host "Building Schedule..."
Push-Location backend/schedule
go build -o schedule_service.exe main.go
if ($LASTEXITCODE -ne 0) { Write-Host "Schedule build failed!" -ForegroundColor Red; $buildErrors = $true }
Pop-Location

Write-Host "Building TechCard..."
Push-Location backend/techcard
go build -o techcard_service.exe main.go
if ($LASTEXITCODE -ne 0) { Write-Host "TechCard build failed!" -ForegroundColor Red; $buildErrors = $true }
Pop-Location

if ($buildErrors) {
    Write-Host "Build failed. Fix errors and try again." -ForegroundColor Red
    Stop-Transcript
    exit 1
}

# Reset Database
Write-Host "Resetting Database Container..." -ForegroundColor Red
docker-compose down -v

# Start Database Container
Write-Host "Starting Database..." -ForegroundColor Cyan
docker-compose up -d db

# Wait for DB to be ready
# Wait for DB port to be ready (TCP check)
Write-Host "Waiting for Database port 5432..."
$retries = 30
while ($retries -gt 0) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("localhost", 5432)
        $tcp.Close()
        Write-Host "`nDatabase port is open!" -ForegroundColor Green
        break
    } catch {
        Start-Sleep -Seconds 2
        $retries--
        Write-Host "." -NoNewline
    }
}

if ($retries -eq 0) {
    Write-Host "`nDatabase failed to start on port 5432 (Timeout)" -ForegroundColor Red
    Stop-Transcript
    exit 1
}

# Give Postgres a moment to handle initdb if it's the first run
Start-Sleep -Seconds 5

# Push Schema
Write-Host "Syncing Database Schema..." -ForegroundColor Cyan
Push-Location "backend/auth"; go run github.com/steebchen/prisma-client-go db push | Tee-Object -FilePath "..\..\logs\auth_db_push.log"; Pop-Location
Push-Location "backend/schedule"; go run github.com/steebchen/prisma-client-go db push | Tee-Object -FilePath "..\..\logs\schedule_db_push.log"; Pop-Location
Push-Location "backend/techcard"; go run github.com/steebchen/prisma-client-go db push | Tee-Object -FilePath "..\..\logs\techcard_db_push.log"; Pop-Location

Write-Host "Starting CRM College System..." -ForegroundColor Green

# 1. Start Auth Service
Write-Host "Starting Auth Service (Port 8000)..." -ForegroundColor Cyan
# Using the pre-built exe is safer and faster
Start-Process pwsh -WorkingDirectory "$PWD\backend\auth" -ArgumentList "-NoExit", "-Command", ".\auth_service.exe 2>&1 | Tee-Object -FilePath '..\..\logs\auth_service.log'"

# 2. Start Schedule Service
Write-Host "Starting Schedule Service (Port 8001)..." -ForegroundColor Cyan
Start-Process pwsh -WorkingDirectory "$PWD\backend\schedule" -ArgumentList "-NoExit", "-Command", ".\schedule_service.exe 2>&1 | Tee-Object -FilePath '..\..\logs\schedule_service.log'"

# 3. Start TechCard Service
Write-Host "Starting TechCard Service (Port 8002)..." -ForegroundColor Cyan
Start-Process pwsh -WorkingDirectory "$PWD\backend\techcard" -ArgumentList "-NoExit", "-Command", ".\techcard_service.exe 2>&1 | Tee-Object -FilePath '..\..\logs\techcard_service.log'"

# 4. Start Frontend
Write-Host "Starting Frontend (Vite Port 3000)..." -ForegroundColor Cyan
Start-Process pwsh -WorkingDirectory "$PWD\frontend" -ArgumentList "-NoExit", "-Command", "npm run dev 2>&1 | Tee-Object -FilePath '..\logs\frontend.log'"

Write-Host "All services started!" -ForegroundColor Green
Write-Host "Logs are being saved to ./logs/ directory"
Write-Host "Frontend: http://localhost:3000"

Stop-Transcript
