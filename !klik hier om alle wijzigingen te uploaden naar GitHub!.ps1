# Navigeer naar de juiste directory
cd "C:\Users\boots\SynologyDrive\Metro\07. Website\Excelladin Reloaded v1"

# Zorg ervoor dat we naar de juiste repository pushen
git remote set-url origin https://github.com/Sallyyyyyyyyyyy/Excelladin-Reloaded-v1.git

# Check of er wijzigingen zijn
$status = git status --porcelain
if ($status) {
    # Voeg alle wijzigingen toe, inclusief verwijderde bestanden
    git add --all
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit -m "Manuele sync: $timestamp"
    
    # Push naar GitHub, inclusief verwijderde bestanden
    git push origin main
    
    Write-Host "Wijzigingen gepusht op $timestamp (inclusief verwijderde bestanden)" -ForegroundColor Green
} else {
    Write-Host "Geen wijzigingen om te pushen." -ForegroundColor Yellow
}

# Houd het venster open tot de gebruiker een toets indrukt
Write-Host "`nDruk op een toets om dit venster te sluiten..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
