@echo off
echo VSCode Terminal Fix Script
echo -------------------------
echo.
echo Dit script zal:
echo 1. Alle VSCode processen afsluiten
echo 2. De terminal instellingen opschonen
echo 3. VSCode herstarten in veilige modus (zonder extensies)
echo.
echo Let op: Sla je werk op voor je dit uitvoert!
echo.
pause

echo Sluiten van alle VSCode processen...
taskkill /F /IM Code.exe /T
timeout /t 2 /nobreak > nul

echo Opruimen van terminal instellingen...
rmdir /S /Q "%APPDATA%\Code\User\workspaceStorage"
mkdir "%APPDATA%\Code\User\workspaceStorage"
timeout /t 1 /nobreak > nul

echo Herstarten van VSCode in veilige modus...
start "" "code" --disable-extensions

echo Klaar! VSCode zou opnieuw moeten starten zonder terminal problemen.
echo.
pause
