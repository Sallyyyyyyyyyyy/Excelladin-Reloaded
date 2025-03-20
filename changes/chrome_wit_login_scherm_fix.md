# Chrome wit scherm fix bij RentPro login

## Probleem
Bij het openen van de RentPro loginpagina in Chrome werd een wit scherm getoond in plaats van de loginpagina. De browser navigeerde naar een URL die begint met `data:`, wat wijst op een probleem met Cross-Site Document Blocking in Chrome.

## Oorzaak
Chrome's veiligheidsfeatures voor site-isolatie blokkeren bepaalde cross-origin navigaties, wat resulteert in een "data:" URL met een wit scherm in plaats van de verwachte inlogpagina.

## Oplossing
De volgende Chrome opties zijn toegevoegd aan de WebDriver configuratie om dit probleem te verhelpen:

```python
# Fix voor wit scherm / data: URL probleem
options.add_argument("--disable-features=CrossSiteDocumentBlockingIfIsolating,CrossSiteDocumentBlockingAlways")
options.add_argument("--disable-site-isolation-trials")
options.add_argument("--disable-web-security")
options.add_argument("--disable-site-isolation-for-policy")
```

## Gewijzigde bestanden
- `modules/rentpro/driver_manager.py` - Chrome opties uitgebreid met bovenstaande fix

## Test
Een test script `test_login_fix.py` is toegevoegd om de fix te verifiëren. Dit script initialiseert Chrome met de nieuwe opties en controleert of de loginpagina correct wordt geladen.

## Technische achtergrond
Chrome's site isolatie is een veiligheidsfunctie die elke website in een apart proces uitvoert. Voor bepaalde webapplicaties zoals RentPro, die mogelijk cross-origin content laden binnen iframes, kan dit problemen veroorzaken. Door deze functies selectief uit te schakelen in onze testomgeving, kunnen we de applicatie correct gebruiken zonder invloed op de algemene browsersecurity.
