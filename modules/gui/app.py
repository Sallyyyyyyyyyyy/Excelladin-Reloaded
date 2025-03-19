"""
Hoofdmodule voor de Excelladin Reloaded GUI
Bevat de ExcelladinApp klasse die de basis vormt voor de GUI
"""
import os
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

from modules.logger import logger
from modules.settings import instellingen
from modules.excel_handler import excelHandler

from assets.theme import KLEUREN, FONTS, STIJLEN

from modules.gui.components import Tooltip, StijlvollePopup
from modules.gui.product_sheet_tab import ProductSheetTab
from modules.gui.sheet_kiezen_tab import SheetKiezenTab
from modules.gui.acties_tab import ActiesTab
from modules.gui.rentpro_tab import RentproTab

class ExcelladinApp:
    """
    Hoofdklasse voor de Excelladin Reloaded applicatie
    """
    def __init__(self, root):
        """
        Initialiseer de applicatie
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Excelladin Reloaded")
        
        # Detecteer schermresolutie en pas venstergrootte aan
        scherm_breedte = self.root.winfo_screenwidth()
        scherm_hoogte = self.root.winfo_screenheight()
        
        # Stel gewenste app-breedte in
        app_breedte = 400
        
        # Bereken maximale veilige hoogte (rekening houdend met taakbalk en vensterdecoraties)
        # Windows taakbalk is ongeveer 40-50 pixels, vensterdecoraties ongeveer 30-40 pixels
        # We houden een veiligheidsmarge van 100 pixels aan voor verschillende DPI-instellingen
        veilige_hoogte = scherm_hoogte - 100
        
        # Beperk de hoogte tot een redelijke waarde (niet te klein, niet te groot)
        app_hoogte = min(700, veilige_hoogte)  # Maximaal 700 pixels, of minder indien nodig
        app_hoogte = max(500, app_hoogte)      # Minimaal 500 pixels voor bruikbaarheid
        
        # Stel venstergrootte in
        self.root.geometry(f"{app_breedte}x{app_hoogte}")
        self.root.resizable(False, False)
        
        # Configureer stijlen
        self._configureerStijlen()
        
        # Bouw de GUI
        self._buildGUI()
        
        # Laad laatste bestand indien nodig
        laatsteBestand = instellingen.haalLaatsteBestand()
        if laatsteBestand and os.path.exists(laatsteBestand):
            self.laadExcelBestand(laatsteBestand)
    
    def opslaanEnAfsluiten(self):
        """Sla wijzigingen op en sluit de applicatie af"""
        if excelHandler.isBestandGeopend():
            if excelHandler.slaOp():
                self.updateStatus("Wijzigingen opgeslagen")
                self.root.destroy()
            else:
                self.toonFoutmelding("Fout", "Kon wijzigingen niet opslaan")
        else:
            self.root.destroy()
    
    def bevestigAfsluiten(self):
        """Vraag om bevestiging voordat de applicatie wordt afgesloten"""
        popup = StijlvollePopup(
            self.root,
            "Afsluiten",
            "Weet je zeker dat je Excelladin Reloaded wilt afsluiten zonder op te slaan?",
            popup_type="vraag",
            actie_knoppen=[
                {'tekst': 'Ja', 'commando': lambda: popup.ja_actie(), 'primair': True},
                {'tekst': 'Nee', 'commando': lambda: popup.nee_actie()}
            ]
        )
        if popup.wacht_op_antwoord():
            self.root.destroy()
    
    def _configureerStijlen(self):
        """Configureer de stijlen voor Tkinter widgets"""
        # Zorg dat Papyrus beschikbaar is
        beschikbareFonts = tkFont.families()
        titelFont = FONTS["titel"][0] if FONTS["titel"][0] in beschikbareFonts else "Arial"
        
        # Pas lettertype aan indien nodig
        self.titelFont = (titelFont, FONTS["titel"][1], FONTS["titel"][2])
        
        # Configureer stijlen voor ttk widgets
        self.stijl = ttk.Style()
        
        # Maak een speciaal donker thema aan voor ttk widgets
        # Deze instellingen zorgen dat de knoppen daadwerkelijk de donkere kleur gebruiken
        self.stijl.theme_create("ExcelladinThema", parent="alt", 
            settings={
                "TButton": {
                    "configure": {
                        "background": "#0a0d2c",  # Donker marineblauw
                        "foreground": KLEUREN["tekst"],  # Felgeel
                        "font": FONTS["normaal"],
                        "relief": "raised",
                        "borderwidth": 1,
                        "padding": (10, 5)
                    },
                    "map": {
                        "background": [
                            ("active", KLEUREN["button_hover"]),
                            ("disabled", "#555555")
                        ],
                        "foreground": [
                            ("disabled", "#999999")
                        ]
                    }
                },
                "TCheckbutton": {
                    "configure": {
                        "background": KLEUREN["achtergrond"],
                        "foreground": KLEUREN["tekst"],
                        "font": FONTS["normaal"]
                    }
                },
                "TRadiobutton": {
                    "configure": {
                        "background": KLEUREN["achtergrond"],
                        "foreground": KLEUREN["tekst"],
                        "font": FONTS["normaal"]
                    }
                },
                "TNotebook": {
                    "configure": {
                        "background": KLEUREN["achtergrond"],
                        "tabmargins": [2, 5, 2, 0]
                    }
                },
                "TNotebook.Tab": {
                    "configure": {
                        "background": KLEUREN["tabblad_inactief"],
                        "foreground": KLEUREN["tekst"],
                        "font": FONTS["normaal"],
                        "padding": [10, 5]
                    },
                    "map": {
                        "background": [
                            ("selected", KLEUREN["tabblad_actief"])
                        ],
                        "foreground": [
                            ("selected", "#FFFF00")
                        ]
                    }
                }
            }
        )
        
        # Activeer het nieuwe thema
        self.stijl.theme_use("ExcelladinThema")
    
    def _buildGUI(self):
        """Bouw de complete GUI"""
        # Maak hoofdframe
        self.hoofdFrame = tk.Frame(
            self.root,
            background=KLEUREN["achtergrond"]
        )
        self.hoofdFrame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._maakHeader()
        
        # Tabbladen
        self._maakTabbladen()
        
        # Statusbalk met Opslaan en Afsluiten knoppen
        self._maakStatusbalk()
    
    def _maakHeader(self):
        """Maak de header met titel"""
        self.headerFrame = tk.Frame(
            self.hoofdFrame,
            **STIJLEN["header"],
            height=50
        )
        self.headerFrame.pack(fill=tk.X)
        
        # Laad en toon afbeelding (links)
        try:
            from PIL import Image, ImageTk
            import os
            
            img_path = os.path.join('assets', 'alladin.jpg')
            if os.path.exists(img_path):
                # Open de afbeelding en pas de grootte aan
                original_img = Image.open(img_path)
                # Bereken nieuwe grootte met behoud van aspect ratio
                width, height = original_img.size
                new_height = 50
                new_width = int(width * (new_height / height))
                resized_img = original_img.resize((new_width, new_height), Image.LANCZOS)
                
                # Converteer naar PhotoImage voor Tkinter
                tk_img = ImageTk.PhotoImage(resized_img)
                
                # Maak label met afbeelding
                self.logoLabel = tk.Label(
                    self.headerFrame,
                    image=tk_img,
                    background=STIJLEN["header"]["background"]
                )
                self.logoLabel.image = tk_img  # Bewaar referentie
                self.logoLabel.pack(side=tk.LEFT, padx=5)
                
                logger.logInfo("Logo afbeelding succesvol geladen")
            else:
                logger.logWaarschuwing(f"Afbeelding niet gevonden: {img_path}")
                # Fallback naar placeholder als afbeelding niet bestaat
                self.logoPlaceholder = tk.Label(
                    self.headerFrame,
                    text="[Logo]",
                    foreground=STIJLEN["label"]["foreground"],
                    font=STIJLEN["label"]["font"],
                    background=STIJLEN["header"]["background"],
                    width=10,
                    height=2
                )
                self.logoPlaceholder.pack(side=tk.LEFT)
        except Exception as e:
            logger.logFout(f"Fout bij laden logo afbeelding: {e}")
            # Fallback naar placeholder bij fouten
            self.logoPlaceholder = tk.Label(
                self.headerFrame,
                text="[Logo]",
                foreground=STIJLEN["label"]["foreground"],
                font=STIJLEN["label"]["font"],
                background=STIJLEN["header"]["background"],
                width=10,
                height=2
            )
            self.logoPlaceholder.pack(side=tk.LEFT)
        
        # Titel (rechts)
        self.titelLabel = tk.Label(
            self.headerFrame,
            text="Excelladin Reloaded",
            **STIJLEN["titel_label"]
        )
        self.titelLabel.pack(side=tk.RIGHT, padx=10)
    
    def _maakTabbladen(self):
        """Maak de tabbladen"""
        self.tabControl = ttk.Notebook(self.hoofdFrame)
        self.tabControl.pack(fill=tk.BOTH, expand=True)
        
        # Tabblad 1: ProductSheet aanmaken
        self.tabProductSheet = tk.Frame(
            self.tabControl,
            background=KLEUREN["achtergrond"]
        )
        self.tabControl.add(self.tabProductSheet, text="ProductSheet")
        self.productSheetTab = ProductSheetTab(self.tabProductSheet, self)
        
        # Tabblad 2: Sheet Kiezen
        self.tabSheetKiezen = tk.Frame(
            self.tabControl,
            background=KLEUREN["achtergrond"]
        )
        self.tabControl.add(self.tabSheetKiezen, text="Sheet Kiezen")
        self.sheetKiezenTab = SheetKiezenTab(self.tabSheetKiezen, self)
        
        # Tabblad 3: Acties
        self.tabActies = tk.Frame(
            self.tabControl,
            background=KLEUREN["achtergrond"]
        )
        self.tabControl.add(self.tabActies, text="Acties")
        self.actiesTab = ActiesTab(self.tabActies, self)
        
        # Tabblad 4: Downloaden van gegevens (voorheen Rentpro)
        self.tabRentpro = tk.Frame(
            self.tabControl,
            background=KLEUREN["achtergrond"]
        )
        self.tabControl.add(self.tabRentpro, text="Downloaden van gegevens")
        self.rentproTab = RentproTab(self.tabRentpro, self)
    
    def _maakStatusbalk(self):
        """Maak de statusbalk onderaan het scherm"""
        self.statusFrame = tk.Frame(
            self.hoofdFrame,
            background=STIJLEN["status"]["background"],
            height=30
        )
        self.statusFrame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Statuslabel
        self.statusLabel = tk.Label(
            self.statusFrame,
            text="Gereed",
            **STIJLEN["status"]
        )
        self.statusLabel.pack(side=tk.LEFT, padx=10)

        # Opslaan en Afsluiten knop
        self.opslaanAfsluitenButton = tk.Button(
            self.statusFrame,
            text="Opslaan en Afsluiten",
            command=self.opslaanEnAfsluiten,
            bg="#990000",  # Donkerrood
            fg="#FFFFFF",  # Wit
            font=("Arial", 10, "bold")
        )
        self.opslaanAfsluitenButton.pack(side=tk.RIGHT, padx=10)
        Tooltip(self.opslaanAfsluitenButton, "Sla wijzigingen op en sluit de applicatie af")
        
        # Afsluitknop
        self.afsluitButton = tk.Button(
            self.statusFrame,
            text="Afsluiten",
            command=self.bevestigAfsluiten,
            bg="#990000",  # Donkerrood
            fg="#FFFFFF",  # Wit
            font=("Arial", 10, "bold")
        )
        self.afsluitButton.pack(side=tk.RIGHT, padx=10)
        Tooltip(self.afsluitButton, "Sluit de applicatie af zonder op te slaan")
    
    def updateStatus(self, statusTekst):
        """
        Update de statustekst
        
        Args:
            statusTekst (str): Nieuwe statustekst
        """
        self.statusLabel.config(text=statusTekst)
        self.root.update_idletasks()
    
    def toonFoutmeldingMetKopieerKnop(self, titel, bericht):
        """
        Toon een foutmelding popup met een kopieerknop
        
        Args:
            titel (str): Titel van de foutmelding
            bericht (str): Foutmeldingstekst
        """
        StijlvollePopup(self.root, titel, bericht, popup_type="fout", kopieer_knop=True)
    
    def toonFoutmelding(self, titel, bericht):
        """
        Toon een foutmelding popup
        
        Args:
            titel (str): Titel van de foutmelding
            bericht (str): Foutmeldingstekst
        """
        self.toonFoutmeldingMetKopieerKnop(titel, bericht)
    
    def toonSuccesmelding(self, titel, bericht):
        """
        Toon een succesmelding popup
        
        Args:
            titel (str): Titel van de succesmelding
            bericht (str): Succesmeldingstekst
        """
        StijlvollePopup(self.root, titel, bericht, popup_type="info")
    
    def toonWaarschuwing(self, titel, bericht):
        """
        Toon een waarschuwing popup
        
        Args:
            titel (str): Titel van de waarschuwing
            bericht (str): Waarschuwingstekst
        """
        StijlvollePopup(self.root, titel, bericht, popup_type="waarschuwing")
    
    def toonBevestigingVraag(self, titel, bericht):
        """
        Toon een bevestigingsvraag popup
        
        Args:
            titel (str): Titel van de vraag
            bericht (str): Vraagtekst
        
        Returns:
            bool: True als de gebruiker 'Ja' kiest, False als de gebruiker 'Nee' kiest
        """
        popup = StijlvollePopup(
            self.root,
            titel,
            bericht,
            popup_type="vraag",
            actie_knoppen=[
                {'tekst': 'Ja', 'commando': lambda: popup.ja_actie(), 'primair': True},
                {'tekst': 'Nee', 'commando': lambda: popup.nee_actie()}
            ]
        )
        return popup.wacht_op_antwoord()
    
    def laadExcelBestand(self, bestandspad):
        """
        Laad een Excel-bestand en update de UI
        
        Args:
            bestandspad (str): Pad naar het Excel-bestand
        """
        self.updateStatus(f"Bezig met laden van {os.path.basename(bestandspad)}...")
        
        # Laad het bestand
        if excelHandler.openBestand(bestandspad):
            # Update UI in Sheet Kiezen tab
            self.sheetKiezenTab.updateNaLaden(bestandspad)
            
            # Update UI in Acties tab
            self.actiesTab.updateNaLaden()
            
            self.updateStatus("Bestand succesvol geladen")
            self.toonSuccesmelding("Succes", f"Bestand '{os.path.basename(bestandspad)}' succesvol geladen")
        else:
            self.updateStatus("Fout bij laden bestand")
            self.toonFoutmelding("Fout", f"Kon bestand '{bestandspad}' niet laden")
