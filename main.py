"""
Excelladin Reloaded - Hoofdapplicatie
Een applicatie in 1001 Nachten-stijl voor het bewerken van Excel-bestanden
"""
import os
import sys
import traceback
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

# Exceptie handler voor onafgehandelde excepties
def exceptie_handler(exc_type, exc_value, exc_traceback):
    """
    Globale exceptie handler die alle onafgehandelde excepties naar het logbestand schrijft
    """
    # Formatteer de exceptie met volledige traceback
    exceptie_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.logFout(f"Onafgehandelde exceptie:\n{exceptie_details}")
    # Toon ook in de originele stderr voor debugging
    sys.__stderr__.write(f"Onafgehandelde exceptie:\n{exceptie_details}\n")

# Klasse voor het redirecten van stdout/stderr naar het logbestand
class LogRedirector:
    """
    Klasse die stdout/stderr output naar het logbestand redirect
    """
    def __init__(self, log_functie, originele_stream):
        self.log_functie = log_functie
        self.originele_stream = originele_stream
        self.buffer = ""
    
    def write(self, tekst):
        # Schrijf naar originele stream voor fallback
        self.originele_stream.write(tekst)
        
        # Voeg toe aan buffer en log complete regels
        self.buffer += tekst
        if '\n' in self.buffer:
            regels = self.buffer.split('\n')
            for regel in regels[:-1]:  # Alle complete regels behalve de laatste
                if regel.strip():  # Alleen niet-lege regels loggen
                    self.log_functie(regel)
            self.buffer = regels[-1]  # Bewaar onvolledige regel
    
    def flush(self):
        # Log eventuele resterende buffer inhoud
        if self.buffer.strip():
            self.log_functie(self.buffer)
            self.buffer = ""
        self.originele_stream.flush()

# Installeer de globale exceptie handler
sys.excepthook = exceptie_handler

# Redirect stdout en stderr naar het logbestand
sys.stdout = LogRedirector(logger.logInfo, sys.__stdout__)
sys.stderr = LogRedirector(logger.logFout, sys.__stderr__)

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
