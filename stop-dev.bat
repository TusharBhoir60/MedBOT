@echo off
setlocal
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq cmd.exe" /v ^| findstr /i "MedBot Backend"') do (
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq cmd.exe" /v ^| findstr /i "MedBot Frontend"') do (
    taskkill /f /pid %%a >nul 2>&1
)
endlocal
