# ProductSheet Tab Vereenvoudiging

## Uitgevoerde wijzigingen

1. **Verwijderde functionaliteit**:
   - De functie "Selecteer bestaande importsheet" is verwijderd
   - De hele HTML broncode analyse sectie is verwijderd
   - Alle bijbehorende methodes voor HTML analyse zijn verwijderd
   - De "Onthoud deze sheet voor volgende sessie" functionaliteit is verwijderd

2. **Behouden functionaliteit**:
   - Alleen de functie om een nieuwe importsheet aan te maken is behouden
   - De basis UI is vereenvoudigd tot alleen de RentPro importsheet beheer sectie

3. **Verbeterde methodes**:
   - `_buildUI`: Vereenvoudigd om alleen de RentPro sectie te tonen
   - `_buildRentProSection`: Aangepast om alleen de nieuwe importsheet functionaliteit te bevatten

4. **Verwijderde methodes**:
   - `_configureInvoerveldenCanvas`
   - `_onInvoerveldenCanvasResize`
   - `kiesHtmlBestand`
   - `maakProductSheet`
   - `_toonInvoervelden`
   - `_verbergInvoervelden`
   - `selecteerBestaandeImportSheet`
   - `slaImportSheetPadOp`
   - `laadOpgeslagenImportSheet`
   - `_maakExcelBestand`
   - `toggleOnthoudImportSheet`

5. **Geoptimaliseerde code**:
   - Vereenvoudigde `maakNieuweImportSheet` methode zonder onthoud-functionaliteit
   - Verwijderde alle code gerelateerd aan het onthouden van importsheets

Deze wijzigingen hebben de ProductSheet tab aanzienlijk vereenvoudigd, waardoor deze nu alleen focust op het aanmaken van nieuwe importsheets voor RentPro zonder onnodige functionaliteit.
