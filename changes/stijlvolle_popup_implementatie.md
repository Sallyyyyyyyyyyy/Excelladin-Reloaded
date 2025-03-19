# Stijlvolle Popup Implementatie

## Installatie Vereisten
Voor deze functionaliteit is de `pyperclip` module vereist. Installeer deze met:
```
pip install pyperclip
```

## Overzicht
Alle standaard messagebox-popups in Excelladin Reloaded zijn vervangen door aangepaste Toplevel-widgets die volledig in de Excelladin-stijl zijn opgemaakt. Dit zorgt voor een consistente gebruikerservaring en een betere integratie met het 1001 Nachten thema van de applicatie.

## Nieuwe Functionaliteit

### StijlvollePopup Component
Er is een nieuwe `StijlvollePopup` klasse toegevoegd aan `modules/gui/components.py` die:
- Een Toplevel widget maakt met Excelladin thema-kleuren en -fonts
- Verschillende popup typen ondersteunt (info, waarschuwing, fout, vraag)
- Ondersteuning biedt voor één of twee actieknoppen
- Gecentreerd wordt weergegeven op het scherm
- Modaal is (blokkeert interactie met het hoofdvenster)
- Consistente padding, kleuren en lettertypen gebruikt uit assets/theme.py

### Kopieerknop voor Foutmeldingen
Alle foutmelding-popups hebben nu een "Kopieer Foutmelding" knop die:
- De volledige foutmelding naar het klembord kopieert
- Duidelijke visuele feedback geeft wanneer de tekst is gekopieerd
- Opvallend genoeg is maar past binnen de Excelladin stijl

### Nieuwe Methodes in ExcelladinApp
De ExcelladinApp klasse heeft nieuwe wrapper-methodes gekregen:
- `toonSuccesmelding(titel, bericht)` - Voor succesmeldingen
- `toonFoutmelding(titel, bericht)` - Voor foutmeldingen, inclusief kopieerknop
- `toonWaarschuwing(titel, bericht)` - Voor waarschuwingen
- `toonBevestigingVraag(titel, bericht)` - Voor ja/nee vragen, retourneert boolean

## Gewijzigde Bestanden
1. `modules/gui/components.py` - Toegevoegd: StijlvollePopup klasse
2. `modules/gui/app.py` - Gewijzigd: Vervangen messagebox door StijlvollePopup en toegevoegd nieuwe wrapper-methodes
3. `modules/gui/acties_tab.py` - Gewijzigd: Vervangen messagebox door StijlvollePopup
4. `modules/gui/product_sheet_tab.py` - Gewijzigd: Vervangen toonSuccesmeldingMetOpenKnop door StijlvollePopup
5. `modules/gui/sheet_kiezen_tab.py` - Gewijzigd: Geïmporteerd StijlvollePopup

## Voordelen
- Consistente gebruikerservaring in de hele applicatie
- Betere integratie met het 1001 Nachten thema
- Verbeterde functionaliteit met kopieerknop voor foutmeldingen
- Flexibelere popup-opties voor toekomstige uitbreidingen
- Modaal gedrag zorgt ervoor dat gebruikers eerst de popup moeten afhandelen
