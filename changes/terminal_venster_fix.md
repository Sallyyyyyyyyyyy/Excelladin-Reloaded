# Terminal Venster Fix

## Probleem
Bij het starten van de applicatie verscheen er een Windows Terminal venster dat een melding toonde over het verwijderen van oude logbestanden:
```
Oud logbestand verwijderd: logs\All_logs_combined_2025-03-17_23-25-47.txt
```

## Oorzaak
De logger module gebruikte `print()` statements om informatie over het opruimen van oude logbestanden en andere foutmeldingen naar de console te schrijven. Deze print statements veroorzaakten dat een terminal venster werd geopend bij het starten van de applicatie.

## Oplossing 1: Logger Aanpassingen
Alle `print()` statements in de logger module zijn verwijderd of vervangen door logging naar het logbestand zelf:

1. In de `_ruim_oude_logs_op()` methode:
   - Verwijderd: `print(f"Oud logbestand verwijderd: {oud_bestand}")`
   - Vervangen: `print(f"Kon oud logbestand niet verwijderen: {e}")` door logging naar het logbestand
   - Vervangen: `print(f"Fout bij opruimen oude logbestanden: {e}")` door logging naar het logbestand

2. In de `__init__()` methode:
   - Verwijderd: `print(f"Waarschuwing: Aangepaste logbestandsnaam '{logBestandsnaam}' wordt genegeerd...")`

3. In de `log()` methode:
   - Verwijderd: `print(f"Kon niet naar logbestand schrijven: {e}")`

4. In de `haalRecenteLogs()` methode:
   - Verwijderd: `print(f"Kon logbestand niet lezen: {e}")`

Deze wijzigingen zorgen ervoor dat er geen terminal venster meer verschijnt bij het starten van de applicatie, terwijl de belangrijke foutmeldingen nog steeds worden gelogd naar het logbestand.

## Oplossing 2: Console Venster Verbergen
Naast het verwijderen van de print statements is er ook code toegevoegd aan main.py om het console venster actief te verbergen op Windows systemen:

```python
import ctypes
if os.name == 'nt':  # Als we op Windows draaien
    # Verberg het console venster
    console_venster = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.ShowWindow(console_venster, 0)
```

Deze code is toegevoegd direct na de imports en voor de eerste functie in main.py. De code:
1. Importeert de ctypes module voor toegang tot Windows API functies
2. Controleert of de applicatie op Windows draait (os.name == 'nt')
3. Haalt een handle op naar het console venster met GetConsoleWindow()
4. Verbergt het venster met ShowWindow() en parameter 0 (SW_HIDE)

Deze oplossing zorgt ervoor dat zelfs als er nog print statements of andere console output zou zijn, het console venster niet zichtbaar is voor de gebruiker. De code is veilig voor andere besturingssystemen omdat de Windows-specifieke code alleen wordt uitgevoerd op Windows.
