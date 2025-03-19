@echo off
setlocal enabledelayedexpansion

echo VSCode Terminal Reactivatie Script voor GitLens
echo ---------------------------------------------
echo.
echo Dit script zal:
echo 1. Controleren of VSCode is geïnstalleerd
echo 2. Een backup maken van workspaceStorage
echo 3. Alle VSCode processen afsluiten
echo 4. De terminal instellingen opschonen
echo 5. VSCode herstarten met behoud van GitLens
echo.
echo Let op: Sla je werk op voor je dit uitvoert!
echo.
pause

:: Controleer of VSCode is geïnstalleerd
where code >nul 2>nul
if %errorlevel% neq 0 (
    echo VSCode is niet gevonden. Zorg dat het is geïnstalleerd en in je PATH staat.
    pause
    exit /b 1
)

:: Maak een backup van workspaceStorage
set backup_folder=%TEMP%\vscode_backup
set timestamp=%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_folder=%backup_folder%\%timestamp%
set backup_folder=%backup_folder: =%

echo Maken van backup in: %backup_folder%
if not exist "%backup_folder%" mkdir "%backup_folder%"
if exist "%APPDATA%\Code\User\workspaceStorage" (
    xcopy /E /I /Y "%APPDATA%\Code\User\workspaceStorage" "%backup_folder%\workspaceStorage" >nul
    echo Backup voltooid.
) else (
    echo Geen workspaceStorage map gevonden om te backuppen.
)

echo Sluiten van alle VSCode processen...
taskkill /F /IM Code.exe /T >nul 2>nul
if %errorlevel% equ 0 (
    echo VSCode processen afgesloten.
) else (
    echo Geen VSCode processen gevonden om af te sluiten.
)
timeout /t 2 /nobreak >nul

echo Opruimen van terminal instellingen...
if exist "%APPDATA%\Code\User\workspaceStorage" (
    rmdir /S /Q "%APPDATA%\Code\User\workspaceStorage"
    mkdir "%APPDATA%\Code\User\workspaceStorage"
    echo Terminal instellingen opgeschoond.
) else (
    echo Geen workspaceStorage map gevonden.
    mkdir "%APPDATA%\Code\User\workspaceStorage" 2>nul
)
timeout /t 1 /nobreak >nul

echo Herstarten van VSCode met project: %CD%
start "" "code" "%CD%"

echo.
echo Klaar! VSCode zou opnieuw moeten starten zonder terminal problemen.
echo GitLens extensie zou nu normaal moeten functioneren.
echo.
echo Als je problemen ondervindt, is er een backup gemaakt in: %backup_folder%
echo.
pause
