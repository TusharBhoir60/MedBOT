@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "FRONTEND_DIR=%ROOT%frontend"
set "VENV_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo Creating backend virtual environment...
    py -3 -m venv "%BACKEND_DIR%\.venv"
)

call "%BACKEND_DIR%\.venv\Scripts\activate.bat"

if not exist "%BACKEND_DIR%\.venv\Lib\site-packages" (
    echo Installing backend requirements...
    python -m pip install --upgrade pip
    python -m pip install -r "%BACKEND_DIR%\requirements.txt"
)

where docker >nul 2>&1
if errorlevel 1 (
    echo Docker was not found. Skipping database container startup.
) else (
    echo Starting database service...
    docker compose -f "%ROOT%docker-compose.yml" up -d db
)

set "APP_ENV=development"
set "DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/aarogya"
set "SYNC_DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/aarogya"
set "ALLOWED_HOSTS=[\"localhost\",\"127.0.0.1\",\"api\"]"
set "ALLOWED_ORIGINS=[\"http://localhost:3000\"]"
set "LOG_LEVEL=INFO"
set "LOG_FORMAT=CONSOLE"
set "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000"

if not exist "%FRONTEND_DIR%\node_modules" (
    echo Installing frontend dependencies...
    cd /d "%FRONTEND_DIR%" && npm install
)

start "MedBot Backend" cmd /k "pushd \"%BACKEND_DIR%\" && call .venv\Scripts\activate.bat && python -m uvicorn main:app --host 127.0.0.1 --port 8000"

set "BACKEND_READY=0"
for /l %%i in (1,1,30) do (
    powershell -NoProfile -Command "try { $resp = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/api/v1/health/live' -TimeoutSec 2; if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300) { exit 0 } } catch { exit 1 }" >nul 2>&1
    if not errorlevel 1 (
        set "BACKEND_READY=1"
        goto :start_frontend
    )
    timeout /t 1 /nobreak >nul
)

:start_frontend
if "%BACKEND_READY%"=="1" (
    start "MedBot Frontend" cmd /k "pushd \"%FRONTEND_DIR%\" && npm run dev"
) else (
    echo Backend did not become ready in time. Please check the backend window.
)

echo.
echo Development stack started.
echo Backend: http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:3000
echo Database: 127.0.0.1:5433

echo.
echo Close the command windows to stop the services.
endlocal
