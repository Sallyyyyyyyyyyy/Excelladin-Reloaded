"""
Excelladin Reloaded - Hoofdapplicatie
Een applicatie in 1001 Nachten-stijl voor het bewerken van Excel-bestanden
"""
import os
import sys
import tkinter as tk

# Zorg dat we modules kunnen importeren
if getattr(sys, 'frozen', False):
    # We draaien als executable
    application_path = os.path.dirname(sys.executable)
else:
    # We draaien als script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Voeg applicatiemap toe aan sys.path
sys.path.insert(0, application_path)

# Importeer modules
from modules.logger import logger
from modules.gui import ExcelladinApp
from modules.helpers import clean_pycache


import ctypes
if os.name == 'nt':  # Als we op Windows draaien
    # Verberg het console venster
    console_venster = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.ShowWindow(console_venster, 0)

def check_voor_patches():
    """Controleer of er patches beschikbaar zijn en pas ze toe indien nodig"""
    patch_bestand = os.path.join(application_path, "Patch2theRescue.py")
    
    if os.path.exists(patch_bestand):
        logger.logInfo("Patch bestand gevonden, bezig met toepassen...")
        try:
            # Importeer het patch bestand als module
            import importlib.util
            spec = importlib.util.spec_from_file_location("patch_module", patch_bestand)
            patch_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(patch_module)
            
            # Voer de patch toe
            if hasattr(patch_module, 'pas_patch_toe'):
                patch_module.pas_patch_toe()
                logger.logInfo("Patch succesvol toegepast")
            else:
                logger.logWaarschuwing("Patch bestand heeft geen 'pas_patch_toe' functie")
        except Exception as e:
            logger.logFout(f"Fout bij toepassen patch: {e}")


# Verwijder Python cache bestanden
clean_pycache()

def main():
    """Start de Excelladin Reloaded applicatie"""
    logger.logInfo("Excelladin Reloaded wordt opgestart")
    
    # Controleer voor patches
    # check_voor_patches() # Uitgeschakeld door RebuildMain
    
    # Maak het hoofdvenster
    root = tk.Tk()
    app = ExcelladinApp(root)
    
    # Start de applicatie
    try:
        logger.logInfo("Applicatie gestart")
        root.mainloop()
    except Exception as e:
        logger.logFout(f"Onverwachte fout in hoofdapplicatie: {e}")
    finally:
        logger.logInfo("Applicatie afgesloten")

if __name__ == "__main__":
    main()
