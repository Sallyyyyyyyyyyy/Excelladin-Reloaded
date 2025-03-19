while ($true) {
    cd "C:\Users\boots\SynologyDrive\Metro\07. Website\Excelladin Reloaded v1"

    # Check of er wijzigingen zijn
    $status = git status --porcelain
    if ($status) {
        git add .
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        git commit -m "Auto-sync: $timestamp"
        git push origin main
        Write-Host "Wijzigingen gepusht op $timestamp"
    } else {
        Write-Host "Geen wijzigingen om te pushen."
    }

    # Wacht 60 seconden
    Start-Sleep -Seconds 60
}