"""
ProductSheet tabblad voor Excelladin Reloaded
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog

from assets.theme import KLEUREN, STIJLEN, FONTS
from modules.gui.components import Tooltip
from modules.logger import logger

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
        
        # Label met instructie
        instructieLabel = tk.Label(
            container,
            text="Hier kunt u een nieuw ProductSheet aanmaken op basis van webpagina broncode",
            **STIJLEN["label"],
            pady=10,
            wraplength=350  # Zorg dat lange tekst netjes wordt afgebroken
        )
        instructieLabel.pack(fill=tk.X)
        
        # HTML bronbestand frame
        htmlFrame = tk.Frame(
            container,
            background=KLEUREN["achtergrond"],
            pady=10
        )
        htmlFrame.pack(fill=tk.X)
        
        # Label voor HTML bestand selectie
        htmlLabel = tk.Label(
            htmlFrame,
            text="Selecteer HTML bronbestand:",
            **STIJLEN["label"],
            anchor=tk.W
        )
        htmlLabel.pack(fill=tk.X)
        
        # Bestandsselectie frame
        bestandsFrame = tk.Frame(
            htmlFrame,
            background=KLEUREN["achtergrond"],
            pady=5
        )
        bestandsFrame.pack(fill=tk.X)
        
        # Bestandspad entry
        self.htmlBestandspadVar = tk.StringVar()
        self.htmlBestandspadEntry = tk.Entry(
            bestandsFrame,
            textvariable=self.htmlBestandspadVar,
            **STIJLEN["entry"],
            width=30
        )
        self.htmlBestandspadEntry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Blader knop
        self.htmlBladerButton = tk.Button(
            bestandsFrame,
            text="Bladeren",
            command=self.kiesHtmlBestand,
            bg="#000080",  # Donkerblauw
            fg="#FFFF00",  # Fel geel
            font=("Arial", 10, "bold")
        )
        self.htmlBladerButton.pack(side=tk.RIGHT, padx=(10, 0))
        Tooltip(self.htmlBladerButton, "Klik om een HTML bronbestand te selecteren")
        
        # Knop om de productsheet te genereren
        self.maakSheetButton = ttk.Button(
            htmlFrame,
            text="Maak import sheet a.d.h.v. geselecteerde bronpagina",
            command=self.maakProductSheet
        )
        self.maakSheetButton.pack(fill=tk.X, pady=(10, 0))
        Tooltip(self.maakSheetButton, "Analyseert het geselecteerde HTML bronbestand en maakt een import Excel sheet aan")
        
        # Frame voor resultaten
        self.resultaatFrame = tk.Frame(
            container,
            background=KLEUREN["achtergrond"],
            relief=tk.GROOVE,
            borderwidth=1,
            padx=10,
            pady=10
        )
        self.resultaatFrame.pack(fill=tk.X, pady=10, expand=True)
        
        # Resultaat label
        self.resultaatLabel = tk.Label(
            self.resultaatFrame,
            text="Geen HTML bronbestand geanalyseerd",
            **STIJLEN["label"],
            anchor=tk.W,
            wraplength=350
        )
        self.resultaatLabel.pack(fill=tk.X)
        
        # Lijst met gevonden invoervelden (initieel verborgen)
        self.invoerveldenFrame = tk.Frame(
            self.resultaatFrame,
            background=KLEUREN["achtergrond"]
        )
        
        # Scrollbar voor invoervelden lijst
        scrollbar = tk.Scrollbar(self.invoerveldenFrame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas voor scrollbare inhoud
        self.invoerveldenCanvas = tk.Canvas(
            self.invoerveldenFrame,
            background=KLEUREN["achtergrond"],
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.invoerveldenCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.invoerveldenCanvas.yview)
        
        # Frame voor invoervelden in canvas
        self.invoerveldenListFrame = tk.Frame(
            self.invoerveldenCanvas,
            background=KLEUREN["achtergrond"]
        )
        
        # Canvas window
        self.invoerveldenCanvasWindow = self.invoerveldenCanvas.create_window(
            (0, 0),
            window=self.invoerveldenListFrame,
            anchor="nw",
            width=350  # Breedte van de canvas minus scrollbar
        )
        
        # Configureer canvas om mee te schalen met frame
        self.invoerveldenListFrame.bind("<Configure>", self._configureInvoerveldenCanvas)
        self.invoerveldenCanvas.bind("<Configure>", self._onInvoerveldenCanvasResize)
    
    def _configureInvoerveldenCanvas(self, event):
        """Pas de canvas grootte aan aan het invoerveldenListFrame"""
        # Update het scrollgebied naar het nieuwe formaat van het invoerveldenListFrame
        self.invoerveldenCanvas.configure(scrollregion=self.invoerveldenCanvas.bbox("all"))
    
    def _onInvoerveldenCanvasResize(self, event):
        """Pas de breedte van het invoerveldenListFrame aan"""
        # Pas de breedte van het window aan aan de canvas
        self.invoerveldenCanvas.itemconfig(self.invoerveldenCanvasWindow, width=event.width)
    
    def kiesHtmlBestand(self):
        """Toon bestandskiezer om een HTML bronbestand te selecteren"""
        bestandspad = filedialog.askopenfilename(
            title="Selecteer HTML bronbestand",
            filetypes=[
                ("HTML bestanden", "*.html;*.htm"),
                ("Tekstbestanden", "*.txt"),
                ("Alle bestanden", "*.*")
            ]
        )
        
        if bestandspad:
            self.htmlBestandspadVar.set(bestandspad)
    
    def maakProductSheet(self):
        """Analyseer het HTML bronbestand en maak een ProductSheet Excel bestand"""
        from modules.html_parser import html_parser
        
        bestandspad = self.htmlBestandspadVar.get()
        
        if not bestandspad:
            self.app.toonFoutmelding("Fout", "Geen HTML bronbestand geselecteerd")
            return
        
        self.app.updateStatus(f"Bezig met analyseren van {os.path.basename(bestandspad)}...")
        
        # Laad het HTML bestand
        if html_parser.laad_bestand(bestandspad):
            # Controleer of er invoervelden zijn gevonden
            if html_parser.invoervelden:
                self.app.updateStatus("HTML bronbestand succesvol geanalyseerd")
                self.resultaatLabel.config(
                    text=f"Gevonden in {os.path.basename(bestandspad)}: {len(html_parser.invoervelden)} invoervelden"
                )
                
                # Toon de gevonden invoervelden
                self._toonInvoervelden(html_parser.invoervelden)
                
                # Vraag waar het Excel bestand moet worden opgeslagen
                self._maakExcelBestand(html_parser)
            else:
                self.app.updateStatus("Geen invoervelden gevonden")
                self.resultaatLabel.config(text=f"Geen invoervelden gevonden in {os.path.basename(bestandspad)}")
                self._verbergInvoervelden()
        else:
            self.app.updateStatus("Fout bij analyseren bestand")
            self.app.toonFoutmelding("Fout", f"Kon bestand '{bestandspad}' niet analyseren")
            self._verbergInvoervelden()
    
    def _toonInvoervelden(self, invoervelden):
        """
        Toon de gevonden invoervelden in de UI
        
        Args:
            invoervelden (list): Lijst met gevonden invoervelden
        """
        # Verwijder bestaande invoervelden
        for widget in self.invoerveldenListFrame.winfo_children():
            widget.destroy()
        
        # Toon het frame
        self.invoerveldenFrame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Voeg een header toe
        headerFrame = tk.Frame(
            self.invoerveldenListFrame,
            background=KLEUREN["header_achtergrond"],
            padx=5,
            pady=5
        )
        headerFrame.pack(fill=tk.X)
        
        headerLabel = tk.Label(
            headerFrame,
            text="Gevonden Invoervelden:",
            foreground=KLEUREN["tekst"],
            background=KLEUREN["header_achtergrond"],
            font=FONTS["subtitel"]
        )
        headerLabel.pack(anchor=tk.W)
        
        # Voeg elke invoerveld toe
        for i, veld in enumerate(invoervelden):
            veldFrame = tk.Frame(
                self.invoerveldenListFrame,
                background=KLEUREN["achtergrond"],
                padx=5,
                pady=5,
                relief=tk.GROOVE,
                borderwidth=1
            )
            veldFrame.pack(fill=tk.X, pady=2)
            
            # Type en naam
            typeNaamFrame = tk.Frame(veldFrame, background=KLEUREN["achtergrond"])
            typeNaamFrame.pack(fill=tk.X)
            
            typeLabel = tk.Label(
                typeNaamFrame,
                text=f"Type: {veld.get('type', '')}",
                **STIJLEN["label"],
                anchor=tk.W,
                width=20
            )
            typeLabel.pack(side=tk.LEFT)
            
            naamLabel = tk.Label(
                typeNaamFrame,
                text=f"Naam: {veld.get('naam', '')}",
                **STIJLEN["label"],
                anchor=tk.W
            )
            naamLabel.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # ID en waarde/placeholder
            idWaardeFrame = tk.Frame(veldFrame, background=KLEUREN["achtergrond"])
            idWaardeFrame.pack(fill=tk.X)
            
            idLabel = tk.Label(
                idWaardeFrame,
                text=f"ID: {veld.get('id', '')}",
                **STIJLEN["label"],
                anchor=tk.W,
                width=20
            )
            idLabel.pack(side=tk.LEFT)
            
            # Toon relevante informatie, afhankelijk van het type veld
            if veld.get('type') in ['select', 'checkbox_groep', 'radio_groep']:
                waardeLabel = tk.Label(
                    idWaardeFrame,
                    text=f"Opties: {len(veld.get('opties', []))}",
                    **STIJLEN["label"],
                    anchor=tk.W
                )
            else:
                info = veld.get('placeholder', '') or veld.get('waarde', '')
                waardeLabel = tk.Label(
                    idWaardeFrame,
                    text=f"Info: {info}",
                    **STIJLEN["label"],
                    anchor=tk.W
                )
            
            waardeLabel.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _verbergInvoervelden(self):
        """Verberg het invoervelden frame"""
        self.invoerveldenFrame.pack_forget()
    
    def _maakExcelBestand(self, parser):
        """
        Maak een Excel bestand met de gevonden invoervelden
        
        Args:
            parser: De html_parser instance met de gevonden invoervelden
        """
        import pandas as pd
        
        # Vraag waar het Excel bestand moet worden opgeslagen
        bestandspad = filedialog.asksaveasfilename(
            title="Sla ProductSheet op als",
            defaultextension=".xlsx",
            filetypes=[("Excel bestanden", "*.xlsx")]
        )
        
        if not bestandspad:
            return
        
        self.app.updateStatus("Bezig met maken Excel bestand...")
        
        try:
            # Maak een DataFrame
            kolommen = parser.genereer_excel_kolommen()
            data = parser.genereer_excel_data()
            
            if not data:
                self.app.toonFoutmelding("Fout", "Geen gegevens om op te slaan")
                self.app.updateStatus("Fout: Geen gegevens om op te slaan")
                return
            
            # Converteer naar DataFrame
            df = pd.DataFrame(data)
            
            # Sla op als Excel
            df.to_excel(bestandspad, index=False)
            
            self.app.updateStatus("Excel bestand succesvol gemaakt")
            self.app.toonSuccesmelding(
                "Succes", 
                f"ProductSheet is opgeslagen als '{os.path.basename(bestandspad)}'"
            )
        except Exception as e:
            self.app.updateStatus("Fout bij maken Excel bestand")
            self.app.toonFoutmelding("Fout", f"Kon Excel bestand niet maken: {e}")
