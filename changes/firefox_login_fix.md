# Firefox browser implementatie voor RentPro login

## Probleem
Bij het openen van de RentPro loginpagina in Chrome werd een wit scherm getoond in plaats van de loginpagina. Verschillende aanpassingen van Chrome-opties hebben dit probleem niet kunnen oplossen.

## Oplossing
Een volledige omschakeling naar Firefox als browser in plaats van Chrome. Firefox heeft minder problemen met cross-origin navigatie en site-isolatie, wat dit specifieke probleem vermijdt.

## Gewijzigde bestanden

1. `modules/rentpro/driver_manager.py`:
   - Volledig omgeschakeld van Chrome naar Firefox WebDriver
   - GeckoDriverManager toegevoegd voor automatische driver-installatie

2. `requirements.txt`:
   - `webdriver_manager` pakket toegevoegd om GeckoDriverManager te ondersteunen

3. Testbestand:
   - Nieuw testbestand `test_firefox_login.py` toegevoegd om de Firefox-implementatie te testen

## Voordelen van Firefox
- Geen last van Chrome's strikte site-isolatie die problemen veroorzaakt met iframes
- Consistenter gedrag bij cross-domain navigatie
- Minder gevoelig voor wijzigingen in beveiligingsbeleid met browserupdates

## Installatie
Voor het gebruik van deze oplossing moet Firefox geïnstalleerd zijn op het systeem en moet het `webdriver_manager` pakket geïnstalleerd worden:

```
pip install -r requirements.txt
```

De GeckoDriver (Firefox WebDriver) wordt automatisch gedownload bij het eerste gebruik.

## Test
De Firefox-implementatie kan getest worden via:

```
python test_firefox_login.py
```

Dit script test of de login correct werkt en de volledige RentPro pagina toegankelijk is.
