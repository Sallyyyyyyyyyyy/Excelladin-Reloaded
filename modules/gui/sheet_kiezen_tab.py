"""
Sheet Kiezen tabblad voor Excelladin Reloaded
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog

from assets.theme import KLEUREN, STIJLEN
from modules.gui.components import Tooltip, StijlvollePopup
from modules.settings import instellingen
from modules.excel_handler import excelHandler

class SheetKiezenTab:
    """
    Klasse voor het Sheet Kiezen tabblad
    """
    def __init__(self, parent, app):
        """
        Initialiseer het Sheet Kiezen tabblad
        
        Args:
            parent: Het parent frame waarin dit tabblad wordt geplaatst
            app: De hoofdapplicatie (ExcelladinApp instance)
        """
        self.parent = parent
        self.app = app
        
        # Bouw de UI
        self._buildUI()
    
    def _buildUI(self):
        """Bouw de UI van het Sheet Kiezen tabblad"""
        # Hoofdcontainer met padding
        container = tk.Frame(
            self.parent,
            background=KLEUREN["achtergrond"],
            padx=20,
            pady=20
        )
        container.pack(fill=tk.BOTH, expand=True)
        
        # Label met instructie
        instructieLabel = tk.Label(
            container,
            text="Selecteer een Excel-bestand om te bewerken",
            **STIJLEN["label"],
            pady=10
        )
        instructieLabel.pack(fill=tk.X)
        
        # Bestandsselectie frame
        bestandsFrame = tk.Frame(
            container,
            background=KLEUREN["achtergrond"]
        )
        bestandsFrame.pack(fill=tk.X, pady=10)
        
        # Bestandspad entry
        self.bestandspadVar = tk.StringVar()
        self.bestandspadEntry = tk.Entry(
            bestandsFrame,
            textvariable=self.bestandspadVar,
            **STIJLEN["entry"],
            width=30
        )
        self.bestandspadEntry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Blader knop
        self.bladerButton = tk.Button(
            bestandsFrame,
            text="...",  # Korte tekst die altijd past
            command=self.kiesExcelBestand,
            width=8,  # Kleinere breedte nodig voor kortere tekst
            bg="#000080",  # Donkerblauw
            fg="#FFFF00",  # Fel geel
            font=("Arial", 10, "bold")
        )
        self.bladerButton.pack(side=tk.RIGHT, padx=(10, 0))
        Tooltip(self.bladerButton, "Klik om een Excel-bestand te selecteren")
        
        # Checkbox om bestand te onthouden (tk.Checkbutton in plaats van ttk voor betere werking)
        self.onthoudBestandVar = tk.BooleanVar(value=instellingen.haalOp('Algemeen', 'OnthoudBestand') == 'True')
        self.onthoudBestandCheck = tk.Checkbutton(
            container,
            text="Onthoud dit bestand voor volgende sessie",
            variable=self.onthoudBestandVar,
            command=self.onthoudBestandUpdate,
            background=KLEUREN["achtergrond"],
            activebackground=KLEUREN["achtergrond"],
            foreground=KLEUREN["tekst"],
            selectcolor="#444444"  # Donkere achtergrond voor betere zichtbaarheid van checkmark
        )
        self.onthoudBestandCheck.pack(fill=tk.X, pady=10)
        Tooltip(self.onthoudBestandCheck, "Als dit is aangevinkt, wordt het bestand automatisch geladen bij het opstarten")
        
        # Laad knop - nu direct na de checkbox
        self.laadButton = ttk.Button(
            container,
            text="Laad Geselecteerd Bestand",
            command=self.laadGeselecteerdBestand
        )
        self.laadButton.pack(fill=tk.X, pady=10)
        Tooltip(self.laadButton, "Klik om het geselecteerde Excel-bestand te laden")
        
        # Frame voor bestandsinformatie
        infoFrame = tk.Frame(
            container,
            background=KLEUREN["achtergrond"],
            relief=tk.GROOVE,
            borderwidth=1,
            padx=10,
            pady=10
        )
        infoFrame.pack(fill=tk.X, pady=10)
        
        # Bestandsinformatie labels
        self.bestandsInfoLabel = tk.Label(
            infoFrame,
            text="Geen bestand geladen",
            **STIJLEN["label"],
            anchor=tk.W
        )
        self.bestandsInfoLabel.pack(fill=tk.X)
        
        self.rijInfoLabel = tk.Label(
            infoFrame,
            text="Rijen: 0",
            **STIJLEN["label"],
            anchor=tk.W
        )
        self.rijInfoLabel.pack(fill=tk.X)
        
        self.kolomInfoLabel = tk.Label(
            infoFrame,
            text="Kolommen: 0",
            **STIJLEN["label"],
            anchor=tk.W
        )
        self.kolomInfoLabel.pack(fill=tk.X)
    
    def kiesExcelBestand(self):
        """Toon bestandskiezer om een Excel-bestand te selecteren"""
        bestandspad = filedialog.askopenfilename(
            title="Selecteer Excel-bestand",
            filetypes=[("Excel bestanden", "*.xlsx *.xls")]
        )
        
        if bestandspad:
            self.bestandspadVar.set(bestandspad)
    
    def onthoudBestandUpdate(self):
        """Update de 'onthoud bestand' instelling"""
        onthoud = self.onthoudBestandVar.get()
        instellingen.stelOnthoudBestandIn(onthoud)
        
        # Forceer visuele update van de checkbox
        if onthoud:
            self.onthoudBestandCheck.select()
        else:
            self.onthoudBestandCheck.deselect()
    
    def laadGeselecteerdBestand(self):
        """Laad het geselecteerde Excel-bestand"""
        bestandspad = self.bestandspadVar.get()
        
        if not bestandspad:
            self.app.toonFoutmelding("Fout", "Geen bestand geselecteerd")
            return
        
        self.app.laadExcelBestand(bestandspad)
    
    def updateNaLaden(self, bestandspad):
        """
        Update de UI na het laden van een Excel-bestand
        
        Args:
            bestandspad (str): Pad naar het geladen Excel-bestand
        """
        # Update UI
        self.bestandspadVar.set(bestandspad)
        self.bestandsInfoLabel.config(text=f"Bestand: {os.path.basename(bestandspad)}")
        self.rijInfoLabel.config(text=f"Rijen: {excelHandler.haalRijAantal()}")
        self.kolomInfoLabel.config(text=f"Kolommen: {len(excelHandler.kolomNamen)}")
        
        # Sla op als laatste bestand indien nodig
        if self.onthoudBestandVar.get():
            instellingen.stelLaatsteBestandIn(bestandspad)
