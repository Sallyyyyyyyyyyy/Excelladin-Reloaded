# GitLens Terminal Reactivatie Fix

## Probleem
VSCode terminals kunnen soms problemen vertonen in combinatie met GitLens extensie, waardoor ze niet goed werken of niet reageren.

## Oorzaak
De workspaceStorage map in VSCode kan beschadigd raken, wat invloed heeft op de terminal functionaliteit. Het volledig uitschakelen van extensies (safe mode) kan werken maar schakelt ook GitLens uit.

## Oplossing
Een aangepast script dat de terminals reset zonder GitLens functionaliteit te verliezen:

1. Het script `reactivate_terminals_gitlens.bat` is aangemaakt als alternatief voor `fix_vscode_terminals.bat`
2. Dit script:
   - Controleert of VSCode is geïnstalleerd en in PATH staat
   - Maakt een backup van de huidige workspaceStorage map
   - Sluit alle VSCode processen af
   - Wist de workspaceStorage map (waar terminal-gerelateerde instellingen worden opgeslagen)
   - Herstart VSCode met alle extensies ingeschakeld
   - Opent automatisch het huidige project

## Verbeteringen t.o.v. originele versie
Het script biedt nu:
- Betere foutafhandeling (controleert of VSCode is geïnstalleerd)
- Automatische backup van workspaceStorage met tijdstempel
- Duidelijkere voortgangsindicaties
- Betere controle van map-existentie
- Terugrolmogelijkheid via backups bij problemen

## Verschil met bestaande fix
Het oorspronkelijke `fix_vscode_terminals.bat` script start VSCode in safe mode (zonder extensies), wat betekent dat GitLens niet beschikbaar is. De nieuwe oplossing behoudt alle extensies waaronder GitLens.

## Gebruik
1. Sla al je werk op in VSCode
2. Voer `reactivate_terminals_gitlens.bat` uit
3. Wacht tot VSCode opnieuw is opgestart

Dit script kan handig zijn wanneer terminals niet reageren of wanneer GitLens-functionaliteit nodig is terwijl terminals moeten worden gereset.

## Herstellen na problemen
Als er problemen optreden na het uitvoeren van het script:
1. Sluit VSCode volledig
2. Herstel de backup uit de %TEMP%\vscode_backup\[tijdstempel] map die het script heeft gemaakt
3. Herstart VSCode
