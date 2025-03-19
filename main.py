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

# Verwijder Python cache bestanden
clean_pycache()

def main():
    """Start de Excelladin Reloaded applicatie"""
    logger.logInfo("Excelladin Reloaded wordt opgestart")
    
    # Patch functionaliteit verwijderd om stabiliteitsproblemen te voorkomen
    
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
