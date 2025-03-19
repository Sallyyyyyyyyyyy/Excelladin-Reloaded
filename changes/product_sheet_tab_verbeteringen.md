# Verbeteringen in ProductSheet functionaliteit

## Overzicht van wijzigingen

### 0. Hoofdletterongevoelige instellingen (Kritieke fix)

**Bestanden: modules/settings.py en modules/gui/product_sheet_tab.py**
- Verbeterd: `haalOp` en `stelIn` methodes in settings.py zijn nu hoofdletterongevoelig
- Verbeterd: `laadOpgeslagenImportSheet` methode in product_sheet_tab.py controleert nu hoofdletterongevoelig
- Probleem opgelost: Instellingen werden niet correct opgeslagen/opgehaald door inconsistentie in hoofdlettergebruik

**Voordelen:**
- Oplossing voor het probleem waarbij de importsheet niet werd onthouden bij herstart
- Robuustere instellingen die niet afhankelijk zijn van exact hoofdlettergebruik
- Behoud van origineel hoofdlettergebruik in config.ini bestand
- Dubbele bescherming tegen hoofdlettergevoeligheid (zowel in settings.py als in product_sheet_tab.py)

De volgende verbeteringen zijn aangebracht in de ProductSheet functionaliteit van Excelladin Reloaded om problemen met bestandspaden en directory-beheer op te lossen:

### 1. Pad-conversie functionaliteit

**Bestand: modules/settings.py**
- Toegevoegd: `maak_relatief_pad` functie om absolute paden te converteren naar relatieve paden
- Toegevoegd: `maak_absoluut_pad` functie om relatieve paden te converteren naar absolute paden
- Toegevoegd: `zorg_voor_directory` functie om te zorgen dat een directory bestaat

**Voordelen:**
- Consistente methode voor pad-conversie in de hele applicatie
- Relatieve paden in configuratie voor betere portabiliteit
- Absolute paden voor bestandsoperaties voor betere betrouwbaarheid

### 2. Automatische aanmaak van Importsheet directory

**Bestand: modules/gui/product_sheet_tab.py**
- Toegevoegd: `_zorg_voor_importsheet_directory` methode die automatisch de Importsheet directory aanmaakt als deze niet bestaat
- Deze methode wordt aangeroepen bij het opstarten en wanneer nodig bij het aanmaken van nieuwe bestanden

**Voordelen:**
- Voorkomt fouten door ontbrekende directory
- Betere gebruikerservaring zonder handmatige directory-aanmaak

### 3. Verbeterde foutafhandeling

**Bestand: modules/gui/product_sheet_tab.py**
- Verbeterd: `laadOpgeslagenImportSheet` methode met duidelijk onderscheid tussen verschillende foutsituaties
- Toegevoegd: Gedetailleerde foutmeldingen en logging
- Verbeterd: Duidelijke gebruikersfeedback bij fouten

**Voordelen:**
- Duidelijker onderscheid tussen "bestand bestaat niet" en "pad is niet geldig" situaties
- Betere diagnose van problemen via logging
- Gebruiker krijgt specifiekere informatie over wat er mis is

### 4. Robuuste padbeheer

**Bestand: modules/gui/product_sheet_tab.py**
- Gewijzigd: Consistente conversie tussen relatieve en absolute paden
- Gewijzigd: Gebruik van absolute paden voor alle bestandsoperaties
- Gewijzigd: Opslag van relatieve paden in configuratie

**Voordelen:**
- Werkt ongeacht vanuit welke directory de applicatie wordt gestart
- Betere portabiliteit van configuratie tussen verschillende systemen
- Minder kans op fouten bij bestandsoperaties

## Technische details

### Hoofdletterongevoelige instellingen

**In settings.py:**

```python
def haalOp(self, sectie, optie, standaard=None):
    """
    Haal een instelling op
    """
    try:
        # Converteer sectie en optie naar lowercase voor hoofdletterongevoelige vergelijking
        sectie_lower = sectie.lower()
        optie_lower = optie.lower()
        
        # Zoek door alle secties en opties op een hoofdletterongevoelige manier
        for config_sectie in self.config.sections():
            if config_sectie.lower() == sectie_lower:
                for config_optie in self.config.options(config_sectie):
                    if config_optie.lower() == optie_lower:
                        return self.config.get(config_sectie, config_optie)
        
        return standaard
    except Exception as e:
        logger.logFout(f"Fout bij ophalen instelling {sectie}.{optie}: {e}")
        return standaard
```

**In product_sheet_tab.py:**

```python
def laadOpgeslagenImportSheet(self):
    """Laad de opgeslagen importsheet uit de instellingen"""
    # Controleer of onthouden is ingeschakeld (hoofdletterongevoelig)
    onthoud_waarde = instellingen.haalOp('RentPro', 'OnthoudImportSheet', 'False')
    onthoud = onthoud_waarde.lower() == 'true'
    self.onthoudVar.set(onthoud)
    
    if onthoud:
        # Haal het pad op en converteer naar absoluut pad
        rel_pad = instellingen.haalOp('RentPro', 'ImportSheet', '')
        # ...
```

### Nieuwe functies in settings.py

```python
def maak_relatief_pad(pad):
    """
    Converteer een absoluut pad naar een relatief pad t.o.v. de huidige werkdirectory
    """
    # Implementatie...

def maak_absoluut_pad(pad):
    """
    Converteer een relatief pad naar een absoluut pad
    """
    # Implementatie...

def zorg_voor_directory(directory_pad):
    """
    Zorgt ervoor dat de opgegeven directory bestaat, maakt deze aan indien nodig
    """
    # Implementatie...
```

### Verbeterde methoden in product_sheet_tab.py

```python
def _zorg_voor_importsheet_directory(self):
    """Zorgt ervoor dat de Importsheet directory bestaat"""
    # Implementatie...

def laadOpgeslagenImportSheet(self):
    """Laad de opgeslagen importsheet uit de instellingen"""
    # Verbeterde implementatie met betere foutafhandeling...

def slaImportSheetPadOp(self, pad):
    """Sla het pad naar de importsheet op in de instellingen"""
    # Verbeterde implementatie met relatieve paden...
```

## Conclusie

Deze verbeteringen maken de ProductSheet functionaliteit van Excelladin Reloaded robuuster en gebruiksvriendelijker. De applicatie kan nu beter omgaan met verschillende pad-situaties, geeft duidelijkere foutmeldingen, en zorgt automatisch voor de benodigde directory-structuur. De kritieke fix voor hoofdletterongevoelige instellingen zorgt ervoor dat de importsheet correct wordt onthouden tussen sessies, wat een belangrijke verbetering is voor de gebruikerservaring.
