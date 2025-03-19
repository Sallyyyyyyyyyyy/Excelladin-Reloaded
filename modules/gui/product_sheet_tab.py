"""
ProductSheet tabblad voor Excelladin Reloaded
"""
import os
import tkinter as tk
import shutil
import subprocess
from tkinter import filedialog

from assets.theme import KLEUREN, STIJLEN, FONTS
from modules.gui.components import Tooltip, StijlvollePopup
from modules.logger import logger
from modules.settings import instellingen, maak_absoluut_pad, maak_relatief_pad, zorg_voor_directory

class ProductSheetTab:
    """
    Klasse voor het ProductSheet tabblad
    """
    def __init__(self, parent, app):
        """
        Initialiseer het ProductSheet tabblad
        
        Args:
            parent: Het parent frame waarin dit tabblad wordt geplaatst
            app: De hoofdapplicatie (ExcelladinApp instance)
        """
        self.parent = parent
        self.app = app
        
        # Bouw de UI
        self._buildUI()
    
    def _buildUI(self):
        """Bouw de UI van het ProductSheet tabblad"""
        # Hoofdcontainer met padding
        container = tk.Frame(
            self.parent,
            background=KLEUREN["achtergrond"],
            padx=20,
            pady=20
        )
        container.pack(fill=tk.BOTH, expand=True)
        
        # ===== RentPro importsheet beheer sectie =====
        self._buildRentProSection(container)
    
    def _buildRentProSection(self, container):
        """Bouw de RentPro importsheet beheer sectie"""
        # Zorg dat de Importsheet directory bestaat
        self._zorg_voor_importsheet_directory()
        
        # Frame voor RentPro sectie
        rentProFrame = tk.Frame(
            container,
            background=KLEUREN["achtergrond"],
            relief=tk.GROOVE,
            borderwidth=1,
            padx=10,
            pady=10
        )
        rentProFrame.pack(fill=tk.X, expand=True)
        
        # Titel voor RentPro sectie
        rentProTitel = tk.Label(
            rentProFrame,
            text="RentPro importsheet beheer",
            foreground=KLEUREN["tekst"],
            background=KLEUREN["achtergrond"],
            font=FONTS["subtitel"],
            pady=5
        )
        rentProTitel.pack(anchor=tk.W)
        
        # Knop voor nieuwe importsheet
        nieuweSheetButton = tk.Button(
            rentProFrame,
            text="Klik hier om een nieuwe RentPro importsheet te maken",
            command=self.maakNieuweImportSheet,
            bg="#000080",  # Donkerblauw
            fg="#FFFF00",  # Fel geel
            font=("Arial", 10, "bold"),
            pady=5
        )
        nieuweSheetButton.pack(fill=tk.X, pady=10)
        Tooltip(nieuweSheetButton, "Maakt een kopie van het lege importsheet template")
        
        # Frame voor geselecteerde importsheet
        self.importSheetFrame = tk.Frame(
            rentProFrame,
            background=KLEUREN["achtergrond"],
            pady=5
        )
        self.importSheetFrame.pack(fill=tk.X)
        
        # Label voor geselecteerde importsheet
        self.importSheetLabel = tk.Label(
            self.importSheetFrame,
            text="Klik op de knop hierboven om een nieuwe importsheet aan te maken",
            **STIJLEN["label"],
            anchor=tk.W,
            wraplength=350
        )
        self.importSheetLabel.pack(fill=tk.X)
    
    def _zorg_voor_importsheet_directory(self):
        """Zorgt ervoor dat de Importsheet directory bestaat"""
        importsheet_dir = "Importsheet"
        if not zorg_voor_directory(importsheet_dir):
            self.app.toonFoutmelding(
                "Fout", 
                f"Kon de Importsheet directory niet aanmaken. Controleer de schrijfrechten."
            )
            logger.logFout(f"Kon de Importsheet directory niet aanmaken")
            return False
        return True
    
    def maakNieuweImportSheet(self):
        """Maak een nieuwe RentPro importsheet op basis van het template"""
        # Zorg dat de Importsheet directory bestaat
        if not self._zorg_voor_importsheet_directory():
            return
        
        # Pad naar template
        template_pad = os.path.join("Importsheet", "products2import_leeg.xlsx")
        abs_template_pad = maak_absoluut_pad(template_pad)
        
        if not os.path.exists(abs_template_pad):
            self.app.toonFoutmelding("Fout", f"Template bestand niet gevonden: {abs_template_pad}")
            logger.logFout(f"Template bestand niet gevonden: {abs_template_pad}")
            return
        
        # Bepaal het pad voor de nieuwe importsheet
        importsheet_dir = "Importsheet"
        basis_naam = "products2import.xlsx"
        nieuw_pad = os.path.join(importsheet_dir, basis_naam)
        abs_nieuw_pad = maak_absoluut_pad(nieuw_pad)
        
        # Controleer of het bestand al bestaat en voeg versienummer toe indien nodig
        versie = 1
        while os.path.exists(abs_nieuw_pad):
            nieuw_pad = os.path.join(importsheet_dir, f"products2import_v{versie}.xlsx")
            abs_nieuw_pad = maak_absoluut_pad(nieuw_pad)
            versie += 1
        
        try:
            # Kopieer het template naar het nieuwe pad
            shutil.copy2(abs_template_pad, abs_nieuw_pad)
            
            # Toon succesmelding met optie om te openen in verkenner
            self.toonSuccesmeldingMetOpenKnop(
                "Succes", 
                f"Nieuwe importsheet aangemaakt: {abs_nieuw_pad}",
                abs_nieuw_pad
            )
            
            # Update de UI
            self.importSheetLabel.config(text=f"Geselecteerde importsheet: {os.path.basename(nieuw_pad)}")
            
        except Exception as e:
            self.app.toonFoutmelding("Fout", f"Kon importsheet niet aanmaken: {e}")
    
    def toonSuccesmeldingMetOpenKnop(self, titel, bericht, bestandspad):
        """
        Toon een succesmelding met een knop om het bestand in Verkenner te openen
        
        Args:
            titel (str): Titel van de succesmelding
            bericht (str): Succesmeldingstekst
            bestandspad (str): Pad naar het bestand dat geopend moet worden
        """
        # Eerst de normale succesmelding tonen
        self.app.toonSuccesmelding(titel, bericht)
        
        # Daarna een aparte dialoog met de Open knop
        popup = StijlvollePopup(
            self.parent,
            "Bestand openen",
            "Wilt u de locatie van het bestand openen in Verkenner?",
            popup_type="vraag",
            actie_knoppen=[
                {
                    'tekst': 'Ja, open in Verkenner', 
                    'commando': lambda: [self.openInVerkenner(bestandspad), popup._sluit_popup()],
                    'primair': True
                },
                {
                    'tekst': 'Nee, bedankt', 
                    'commando': lambda: popup._sluit_popup()
                }
            ]
        )
    
    def openInVerkenner(self, pad):
        """Open het opgegeven pad in de Windows Verkenner"""
        try:
            # Gebruik het juiste commando voor het besturingssysteem
            if os.name == 'nt':  # Windows
                subprocess.Popen(f'explorer /select,"{pad}"')
            elif os.name == 'posix':  # macOS of Linux
                if os.path.isdir(pad):
                    subprocess.Popen(['open', pad])
                else:
                    subprocess.Popen(['open', '-R', pad])
            else:
                self.app.toonFoutmelding("Fout", "Niet-ondersteund besturingssysteem")
        except Exception as e:
            self.app.toonFoutmelding("Fout", f"Kon Verkenner niet openen: {e}")
