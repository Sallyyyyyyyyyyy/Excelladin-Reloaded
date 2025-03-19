"""
Rentpro tabblad voor Excelladin Reloaded
Verantwoordelijk voor de Rentpro integratie UI
"""
import tkinter as tk
from tkinter import ttk
import asyncio
import threading

from assets.theme import KLEUREN, STIJLEN
from modules.gui.components import Tooltip, StijlvollePopup
from modules.excel_handler import excelHandler
from modules.rentpro_handler import rentproHandler
from modules.logger import logger

class RentproTab:
    """
    Klasse voor het Rentpro tabblad
    """
    def __init__(self, parent, app):
        """
        Initialiseer het Rentpro tabblad
        
        Args:
            parent: Het parent frame waarin dit tabblad wordt geplaatst
            app: De hoofdapplicatie (ExcelladinApp instance)
        """
        self.parent = parent
        self.app = app
        self.is_bezig = False
        
        # Bouw de UI
        self._buildUI()
    
    def _buildUI(self):
        """Bouw de UI van het Rentpro tabblad"""
        # Hoofdcontainer met padding
        self.container = tk.Frame(
            self.parent,
            background=KLEUREN["achtergrond"],
            padx=20,
            pady=20
        )
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Label met instructie
        # Maak een kopie van de label stijl zonder de font parameter
        label_stijl = STIJLEN["label"].copy()
        del label_stijl["font"]
        instructieLabel = tk.Label(
            self.container,
            text="Gegevens downloaden van Rentpro",
            **label_stijl,
            pady=10,
            font=("Arial", 14, "bold")
        )
        instructieLabel.pack(fill=tk.X)
        
        # Thematische quote
        quoteLabel = tk.Label(
            self.container,
            text="\"Als een dief in de nacht, zo stil haalt Excelladin uw gegevens binnen...\"",
            **STIJLEN["label"],
            font=("Arial", 10, "italic"),
            fg="#fdb04d"  # Gouden kleur voor de quote
        )
        quoteLabel.pack(fill=tk.X, pady=(0, 10))
        
        # Frame voor inloggegevens
        inlogFrame = tk.Frame(
            self.container,
            background=KLEUREN["achtergrond"],
            padx=10,
            pady=10,
            relief=tk.GROOVE,
            borderwidth=1
        )
        inlogFrame.pack(fill=tk.X, pady=10)
        
        # Inlogsectie titel
        label_stijl = STIJLEN["label"].copy()
        del label_stijl["font"]
        inlogLabel = tk.Label(
            inlogFrame,
            text="Inloggegevens Rentpro",
            **label_stijl,
            font=("Arial", 12, "bold")
        )
        inlogLabel.pack(fill=tk.X)
        
        # Gebruikersnaam
        gebruikersnaamFrame = tk.Frame(inlogFrame, background=KLEUREN["achtergrond"])
        gebruikersnaamFrame.pack(fill=tk.X, pady=5)
        
        gebruikersnaamLabel = tk.Label(
            gebruikersnaamFrame,
            text="Gebruikersnaam:",
            **STIJLEN["label"],
            width=15,
            anchor=tk.W
        )
        gebruikersnaamLabel.pack(side=tk.LEFT)
        
        self.gebruikersnaamVar = tk.StringVar()
        gebruikersnaamEntry = tk.Entry(
            gebruikersnaamFrame,
            textvariable=self.gebruikersnaamVar,
            **STIJLEN["entry"],
            width=30
        )
        gebruikersnaamEntry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Wachtwoord
        wachtwoordFrame = tk.Frame(inlogFrame, background=KLEUREN["achtergrond"])
        wachtwoordFrame.pack(fill=tk.X, pady=5)
        
        wachtwoordLabel = tk.Label(
            wachtwoordFrame,
            text="Wachtwoord:",
            **STIJLEN["label"],
            width=15,
            anchor=tk.W
        )
        wachtwoordLabel.pack(side=tk.LEFT)
        
        self.wachtwoordVar = tk.StringVar()
        wachtwoordEntry = tk.Entry(
            wachtwoordFrame,
            textvariable=self.wachtwoordVar,
            **STIJLEN["entry"],
            width=30,
            show="*"
        )
        wachtwoordEntry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Frame voor synchronisatie opties
        optiesFrame = tk.Frame(
            self.container,
            background=KLEUREN["achtergrond"],
            padx=10,
            pady=10,
            relief=tk.GROOVE,
            borderwidth=1
        )
        optiesFrame.pack(fill=tk.X, pady=10)
        
        # Titel voor opties
        label_stijl = STIJLEN["label"].copy()
        del label_stijl["font"]
        optiesLabel = tk.Label(
            optiesFrame,
            text="Synchronisatie Opties",
            **label_stijl,
            font=("Arial", 12, "bold")
        )
        optiesLabel.pack(fill=tk.X)
        
        # Onthoud inloggegevens optie
        self.onthoudInlogVar = tk.BooleanVar(value=False)
        onthoudInlogCheck = tk.Checkbutton(
            inlogFrame,
            text="Inloggegevens onthouden",
            variable=self.onthoudInlogVar,
            background=KLEUREN["achtergrond"],
            foreground="#FFFFFF",
            selectcolor="#b01345",
            activebackground=KLEUREN["achtergrond"],
            activeforeground="#FFFFFF"
        )
        onthoudInlogCheck.pack(anchor=tk.W, pady=5)
        Tooltip(onthoudInlogCheck, "Sla inloggegevens op voor volgende sessie")
        
        # Overschrijf lokale data optie
        self.overschrijfVar = tk.BooleanVar(value=False)
        overschrijfCheck = tk.Checkbutton(
            optiesFrame,
            text="Lokale data overschrijven",
            variable=self.overschrijfVar,
            background=KLEUREN["achtergrond"],
            foreground="#FFFFFF",
            selectcolor="#b01345",
            activebackground=KLEUREN["achtergrond"],
            activeforeground="#FFFFFF",
            command=self.toon_overschrijf_waarschuwing
        )
        overschrijfCheck.pack(anchor=tk.W, pady=5)
        Tooltip(overschrijfCheck, "Als deze optie ingeschakeld is, worden lokale gegevens overschreven door Rentpro data. Anders worden alleen lege velden aangevuld.")
        
        # Bereik selectie frame
        bereikFrame = tk.Frame(
            optiesFrame,
            background=KLEUREN["achtergrond"],
            padx=5,
            pady=5
        )
        bereikFrame.pack(fill=tk.X)
        
        bereikLabel = tk.Label(
            bereikFrame,
            text="Bereik:",
            **STIJLEN["label"]
        )
        bereikLabel.pack(side=tk.LEFT)
        
        # Bereik opties
        self.bereikVar = tk.StringVar(value="alles")
        
        allesRadio = tk.Radiobutton(
            bereikFrame,
            text="Alles",
            variable=self.bereikVar,
            value="alles",
            background=KLEUREN["achtergrond"],
            foreground="#FFFFFF",  # Witte tekst voor betere zichtbaarheid
            selectcolor="#b01345",  # Duidelijke selectiekleur
            activebackground=KLEUREN["achtergrond"],
            activeforeground="#FFFFFF"
        )
        allesRadio.pack(side=tk.LEFT, padx=5)
        Tooltip(allesRadio, "Synchroniseer alle rijen")
        
        enkelRadio = tk.Radiobutton(
            bereikFrame,
            text="Rij:",
            variable=self.bereikVar,
            value="enkel",
            background=KLEUREN["achtergrond"],
            foreground="#FFFFFF",  # Witte tekst voor betere zichtbaarheid
            selectcolor="#b01345",  # Duidelijke selectiekleur
            activebackground=KLEUREN["achtergrond"],
            activeforeground="#FFFFFF"
        )
        enkelRadio.pack(side=tk.LEFT, padx=5)
        Tooltip(enkelRadio, "Synchroniseer één specifieke rij")
        
        # Rij invoer voor 'enkel'
        self.enkelRijVar = tk.StringVar(value="1")
        enkelRijEntry = tk.Entry(
            bereikFrame,
            textvariable=self.enkelRijVar,
            **STIJLEN["entry"],
            width=5
        )
        enkelRijEntry.pack(side=tk.LEFT)
        
        bereikRadio = tk.Radiobutton(
            bereikFrame,
            text="Bereik:",
            variable=self.bereikVar,
            value="bereik",
            background=KLEUREN["achtergrond"],
            foreground="#FFFFFF",  # Witte tekst voor betere zichtbaarheid
            selectcolor="#b01345",  # Duidelijke selectiekleur
            activebackground=KLEUREN["achtergrond"],
            activeforeground="#FFFFFF"
        )
        bereikRadio.pack(side=tk.LEFT, padx=5)
        Tooltip(bereikRadio, "Synchroniseer een bereik van rijen")
        
        # Bereik invoer
        self.vanRijVar = tk.StringVar(value="1")
        vanRijEntry = tk.Entry(
            bereikFrame,
            textvariable=self.vanRijVar,
            **STIJLEN["entry"],
            width=5
        )
        vanRijEntry.pack(side=tk.LEFT)
        
        totLabel = tk.Label(
            bereikFrame,
            text="tot",
            **STIJLEN["label"]
        )
        totLabel.pack(side=tk.LEFT, padx=2)
        
        self.totRijVar = tk.StringVar(value="10")
        totRijEntry = tk.Entry(
            bereikFrame,
            textvariable=self.totRijVar,
            **STIJLEN["entry"],
            width=5
        )
        totRijEntry.pack(side=tk.LEFT)
        
        # Actieknoppen
        actieFrame = tk.Frame(
            self.container,
            background=KLEUREN["achtergrond"],
            padx=10,
            pady=10
        )
        actieFrame.pack(fill=tk.X, pady=10)
        
        # Start knop met thematische tekst
        self.startButton = tk.Button(
            actieFrame,
            text="Open Sesam! Start Synchronisatie",
            command=self.start_synchronisatie,
            bg="#007bff",  # Blauw
            fg="#FFFFFF",  # Wit
            font=("Arial", 12, "bold"),
            height=2
        )
        self.startButton.pack(fill=tk.X)
        Tooltip(self.startButton, "Start de synchronisatie met Rentpro - Laat de magie beginnen!")
        
        # Voortgangsbalk
        voortgangFrame = tk.Frame(
            self.container,
            background=KLEUREN["achtergrond"],
            padx=10,
            pady=10
        )
        voortgangFrame.pack(fill=tk.X, pady=10)
        
        self.voortgangLabel = tk.Label(
            voortgangFrame,
            text="Gereed",
            **STIJLEN["label"]
        )
        self.voortgangLabel.pack(fill=tk.X)
        
        self.voortgangBalk = ttk.Progressbar(
            voortgangFrame,
            orient=tk.HORIZONTAL,
            length=100,
            mode='indeterminate'
        )
        self.voortgangBalk.pack(fill=tk.X, pady=5)
        
        # Resultatenweergave
        resultaatFrame = tk.Frame(
            self.container,
            background=KLEUREN["achtergrond"],
            padx=10,
            pady=10,
            relief=tk.GROOVE,
            borderwidth=1
        )
        resultaatFrame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        label_stijl = STIJLEN["label"].copy()
        del label_stijl["font"]
        resultaatLabel = tk.Label(
            resultaatFrame,
            text="Resultaten",
            **label_stijl,
            font=("Arial", 12, "bold")
        )
        resultaatLabel.pack(fill=tk.X)
        
        # Scrollbare tekstweergave voor resultaten
        resultaatScroll = tk.Scrollbar(resultaatFrame)
        resultaatScroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.resultaatText = tk.Text(
            resultaatFrame,
            **STIJLEN["entry"],
            height=10,
            yscrollcommand=resultaatScroll.set,
            state=tk.DISABLED
        )
        self.resultaatText.pack(fill=tk.BOTH, expand=True)
        resultaatScroll.config(command=self.resultaatText.yview)
        
        # Initiële status
        self.updateResultaat("Gereed voor synchronisatie met Rentpro")
    
    def haalGeselecteerdBereik(self):
        """
        Haal het geselecteerde regelbereik op
        
        Returns:
            tuple: (startRij, eindRij) of None als 'alles' is geselecteerd
        """
        bereikType = self.bereikVar.get()
        
        try:
            if bereikType == "enkel":
                rij = int(self.enkelRijVar.get()) - 1  # Pas aan voor 0-index
                return (rij, rij)
            elif bereikType == "bereik":
                vanRij = int(self.vanRijVar.get()) - 1  # Pas aan voor 0-index
                totRij = int(self.totRijVar.get()) - 1  # Pas aan voor 0-index
                return (vanRij, totRij)
            else:  # "alles"
                return None
        except ValueError:
            self.app.toonFoutmelding("Fout", "Ongeldige rijwaarden. Gebruik gehele getallen.")
            return None
    
    def updateResultaat(self, tekst):
        """
        Voeg tekst toe aan het resultaatveld
        
        Args:
            tekst (str): De tekst om toe te voegen
        """
        self.resultaatText.config(state=tk.NORMAL)
        self.resultaatText.insert(tk.END, tekst + "\n")
        self.resultaatText.see(tk.END)
        self.resultaatText.config(state=tk.DISABLED)
    
    def start_synchronisatie(self):
        """Start de synchronisatie met Rentpro"""
        if self.is_bezig:
            self.app.toonWaarschuwing("Bezig", "Er is al een synchronisatie bezig")
            return
        
        if not excelHandler.isBestandGeopend():
            self.app.toonFoutmelding("Fout", "Geen Excel-bestand geopend")
            return
        
        # Check inloggegevens
        gebruikersnaam = self.gebruikersnaamVar.get().strip()
        wachtwoord = self.wachtwoordVar.get().strip()
        
        if not gebruikersnaam or not wachtwoord:
            self.app.toonFoutmelding("Ontbrekende gegevens", "Vul de gebruikersnaam en wachtwoord in")
            return
        
        # Haal opties op
        overschrijf_lokaal = self.overschrijfVar.get()
        bereik = self.haalGeselecteerdBereik()
        
        # Start de synchronisatie in een aparte thread
        self.is_bezig = True
        self.voortgangBalk.start(10)  # Start de voortgangsbalk (interval in ms)
        self.voortgangLabel.config(text="Bezig met synchroniseren...")
        self.app.updateStatus("Bezig met Rentpro synchronisatie...")
        self.updateResultaat(f"Synchronisatie gestart {'(overschrijven)' if overschrijf_lokaal else '(alleen lege velden)'}")
        
        # Disable start knop tijdens verwerking
        self.startButton.config(state=tk.DISABLED)
        
        # Start een asyncio event loop in een aparte thread
        threading.Thread(target=self.run_async_task, args=(gebruikersnaam, wachtwoord, overschrijf_lokaal, bereik), daemon=True).start()
    
    def run_async_task(self, gebruikersnaam, wachtwoord, overschrijf_lokaal, bereik):
        """
        Voer asyncio taken uit in een aparte thread
        
        Args:
            gebruikersnaam (str): Rentpro gebruikersnaam
            wachtwoord (str): Rentpro wachtwoord
            overschrijf_lokaal (bool): Of lokale data overschreven moet worden
            bereik (tuple): Bereik van rijen om te synchroniseren of None voor alles
        """
        asyncio.run(self.synchroniseer(gebruikersnaam, wachtwoord, overschrijf_lokaal, bereik))
    
    async def synchroniseer(self, gebruikersnaam, wachtwoord, overschrijf_lokaal, bereik):
        """
        Asynchrone functie voor synchronisatie met Rentpro
        
        Args:
            gebruikersnaam (str): Rentpro gebruikersnaam
            wachtwoord (str): Rentpro wachtwoord
            overschrijf_lokaal (bool): Of lokale data overschreven moet worden
            bereik (tuple): Bereik van rijen om te synchroniseren of None voor alles
        """
        try:
            # Update UI
            self.update_ui_status("Verbinding maken met Rentpro...")
            
            # Initialiseer de sessie
            await rentproHandler.initialize()
            
            # Login
            self.update_ui_status("Inloggen bij Rentpro...")
            login_success = await rentproHandler.login(gebruikersnaam, wachtwoord)
            
            if not login_success:
                self.update_ui_error("Inloggen bij Rentpro mislukt. Controleer je inloggegevens.")
                return
            
            # Haal producten op
            self.update_ui_status("Ophalen van productgegevens...")
            success = await rentproHandler.haal_producten_op(overschrijf_lokaal, bereik)
            
            if success:
                self.update_ui_success("Synchronisatie succesvol afgerond")
                
                # Vraag of gebruiker het resultaat wil opslaan
                self.app.root.after(0, lambda: self.vraag_opslaan())
            else:
                self.update_ui_error("Fout bij ophalen van productgegevens")
                
        except Exception as e:
            logger.logFout(f"Fout bij synchronisatie: {e}")
            self.update_ui_error(f"Fout bij synchronisatie: {str(e)}")
        finally:
            # Sluit de sessie
            await rentproHandler.close()
            
            # Herstel UI
            self.app.root.after(0, self.reset_ui)
    
    def update_ui_status(self, status):
        """
        Update UI met statusbericht
        
        Args:
            status (str): Statusbericht
        """
        logger.logInfo(status)
        self.app.root.after(0, lambda: self.voortgangLabel.config(text=status))
        self.app.root.after(0, lambda: self.app.updateStatus(status))
        self.app.root.after(0, lambda: self.updateResultaat(status))
    
    def update_ui_error(self, error):
        """
        Update UI met foutmelding
        
        Args:
            error (str): Foutmelding
        """
        logger.logFout(error)
        self.app.root.after(0, lambda: self.voortgangLabel.config(text="Fout: " + error))
        self.app.root.after(0, lambda: self.app.updateStatus("Fout bij Rentpro synchronisatie"))
        self.app.root.after(0, lambda: self.updateResultaat("FOUT: " + error))
        self.app.root.after(0, lambda: self.app.toonFoutmelding("Synchronisatie fout", error))
    
    def update_ui_success(self, message):
        """
        Update UI met succesmelding
        
        Args:
            message (str): Succesmelding
        """
        logger.logInfo(message)
        self.app.root.after(0, lambda: self.voortgangLabel.config(text=message))
        self.app.root.after(0, lambda: self.app.updateStatus(message))
        self.app.root.after(0, lambda: self.updateResultaat(message))
    
    def reset_ui(self):
        """Reset de UI na synchronisatie"""
        self.is_bezig = False
        self.voortgangBalk.stop()
        self.startButton.config(state=tk.NORMAL)
    
    def vraag_opslaan(self):
        """Vraag of de gebruiker het resultaat wil opslaan"""
        if not self.is_bezig:  # Voorkom dubbele dialogen
            popup = StijlvollePopup(
                self.app.root,
                "Opslaan",
                "Synchronisatie succesvol. Wil je de wijzigingen opslaan?",
                popup_type="vraag",
                actie_knoppen=[
                    {'tekst': 'Ja', 'commando': lambda: popup.ja_actie(), 'primair': True},
                    {'tekst': 'Nee', 'commando': lambda: popup.nee_actie()}
                ]
            )
            
            if popup.wacht_op_antwoord():
                if excelHandler.slaOp():
                    self.app.updateStatus("Wijzigingen opgeslagen")
                    self.app.toonSuccesmelding("Succes", "Wijzigingen zijn opgeslagen")
                    self.updateResultaat("Wijzigingen opgeslagen in Excel-bestand")
                else:
                    self.app.updateStatus("Fout bij opslaan")
                    self.app.toonFoutmelding("Fout", "Kon wijzigingen niet opslaan")
                    self.updateResultaat("FOUT: Kon wijzigingen niet opslaan")
            else:
                self.updateResultaat("Wijzigingen NIET opgeslagen")
                self.app.updateStatus("Wijzigingen niet opgeslagen")
