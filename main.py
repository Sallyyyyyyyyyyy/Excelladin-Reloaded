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


def maakVolledigeBackup():
    """Maak een volledige backup van de applicatie bij het opstarten"""
    import os
    import shutil
    import datetime
    
    logger.logInfo("Start maken van volledige applicatie backup")
    
    # Hergebruik application_path uit main
    app_root = application_path
    
    # Maak backup directory indien nodig
    backup_dir_naam = "!fullappbackups"
    backup_root = os.path.join(app_root, backup_dir_naam)
    os.makedirs(backup_root, exist_ok=True)
    
    # Maak een backup map met datum/tijd in de naam
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_map = os.path.join(backup_root, f"backup_{timestamp}")
    os.makedirs(backup_map)
    
    # Kopieer alle bestanden en mappen behalve !fullappbackups/
    for item in os.listdir(app_root):
        item_path = os.path.join(app_root, item)
        
        # Sla de backup directory zelf over
        if item == backup_dir_naam:
            continue
        
        # Kopieer bestanden of mappen
        try:
            if os.path.isfile(item_path):
                shutil.copy2(item_path, os.path.join(backup_map, item))
            elif os.path.isdir(item_path):
                shutil.copytree(item_path, os.path.join(backup_map, item))
        except Exception as e:
            logger.logWaarschuwing(f"Kon {item} niet kopiëren: {e}")
    
    logger.logInfo(f"Volledige applicatie backup gemaakt in: {backup_map}")
def main():
    """Start de Excelladin Reloaded applicatie"""
    logger.logInfo("Excelladin Reloaded wordt opgestart")

    # Maak volledige backup bij opstarten
    maakVolledigeBackup()
    
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
