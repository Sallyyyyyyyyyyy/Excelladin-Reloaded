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
        self.is_ingelogd = False
        
        # Laad opgeslagen inloggegevens
        from modules.settings import haalRentproGebruikersnaam, haalRentproWachtwoord, haalRentproURL
        self.opgeslagen_gebruikersnaam = haalRentproGebruikersnaam()
        self.opgeslagen_wachtwoord = haalRentproWachtwoord()
        self.opgeslagen_url = haalRentproURL()
        
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
        label_stijl = STIJLEN["label"].copy()
        del label_stijl["font"]
        quoteLabel = tk.Label(
            self.container,
            text="\"Als een dief in de nacht, zo stil haalt Excelladin uw gegevens binnen...\"",
            **label_stijl,
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
            width=30,
            bg="#000080",  # Donkerblauw
            fg="#FFFF00",  # Geel
            insertbackground="#FFFF00"  # Cursor kleur
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
            width=30,
            bg="#000080",  # Donkerblauw
            fg="#FFFF00",  # Geel
            insertbackground="#FFFF00",  # Cursor kleur
            show="*"
        )
        wachtwoordEntry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # URL naar back-office
        urlFrame = tk.Frame(inlogFrame, background=KLEUREN["achtergrond"])
        urlFrame.pack(fill=tk.X, pady=5)
        
        urlLabel = tk.Label(
            urlFrame,
            text="Back-office URL:",
            **STIJLEN["label"],
            width=15,
            anchor=tk.W
        )
        urlLabel.pack(side=tk.LEFT)
        
        self.urlVar = tk.StringVar()
        urlEntry = tk.Entry(
            urlFrame,
            textvariable=self.urlVar,
            width=30,
            bg="#000080",  # Donkerblauw
            fg="#FFFF00",  # Geel
            insertbackground="#FFFF00"  # Cursor kleur
        )
        urlEntry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
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
        
        # Inlogknop en status frame
        inlogActieFrame = tk.Frame(inlogFrame, background=KLEUREN["achtergrond"])
        inlogActieFrame.pack(fill=tk.X, pady=5)
        
        # Inlogknop
        self.inlogButton = tk.Button(
            inlogActieFrame,
            text="Log In",
            command=self.login_zonder_synchronisatie,
            bg="#b01345",  # Rood in 1001 Nachten stijl
            fg="#FFFFFF",  # Wit
            font=("Arial", 10, "bold"),
            padx=10
        )
        self.inlogButton.pack(side=tk.LEFT, padx=(0, 10))
        Tooltip(self.inlogButton, "Log in bij Rentpro zonder synchronisatie te starten")
        
        # Status indicator
        self.statusLabel = tk.Label(
            inlogActieFrame,
            text="Niet ingelogd",
            fg="#FF0000",  # Rood voor niet ingelogd
            background=KLEUREN["achtergrond"],
            font=("Arial", 10)
        )
        self.statusLabel.pack(side=tk.LEFT)
        
        # Productenoverzicht frame
        self.productenFrame = tk.Frame(
            self.container,
            background=KLEUREN["achtergrond"],
            padx=10,
            pady=10,
            relief=tk.GROOVE,
            borderwidth=1
        )
        self.productenFrame.pack(fill=tk.X, pady=10)
        
        # Titel voor productenoverzicht
        label_stijl = STIJLEN["label"].copy()
        del label_stijl["font"]
        productenLabel = tk.Label(
            self.productenFrame,
            text="Productenoverzicht",
            **label_stijl,
            font=("Arial", 12, "bold")
        )
        productenLabel.pack(fill=tk.X)
        
        # Opmerking dat dit alleen voor preview is
        previewLabel = tk.Label(
            self.productenFrame,
            text="(Alleen voor weergave/preview)",
            **STIJLEN["label"],
            font=("Arial", 8, "italic")
        )
        previewLabel.pack(fill=tk.X)
        
        # Eerste 3 producten
        eersteProductenFrame = tk.Frame(self.productenFrame, background=KLEUREN["achtergrond"])
        eersteProductenFrame.pack(fill=tk.X, pady=(5, 2))
        
        eersteProductenLabel = tk.Label(
            eersteProductenFrame,
            text="Dit zijn de eerste 3 producten:",
            **STIJLEN["label"],
            anchor=tk.W
        )
        eersteProductenLabel.pack(fill=tk.X)
        
        eersteProductenScroll = tk.Scrollbar(eersteProductenFrame)
        eersteProductenScroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.eersteProductenText = tk.Text(
            eersteProductenFrame,
            **STIJLEN["entry"],
            height=3,
            yscrollcommand=eersteProductenScroll.set,
            state=tk.DISABLED
        )
        self.eersteProductenText.pack(fill=tk.X)
        eersteProductenScroll.config(command=self.eersteProductenText.yview)
        
        # Laatste 3 producten
        laatsteProductenFrame = tk.Frame(self.productenFrame, background=KLEUREN["achtergrond"])
        laatsteProductenFrame.pack(fill=tk.X, pady=(2, 5))
        
        laatsteProductenLabel = tk.Label(
            laatsteProductenFrame,
            text="Dit zijn de laatste 3 producten:",
            **STIJLEN["label"],
            anchor=tk.W
        )
        laatsteProductenLabel.pack(fill=tk.X)
        
        laatsteProductenScroll = tk.Scrollbar(laatsteProductenFrame)
        laatsteProductenScroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.laatsteProductenText = tk.Text(
            laatsteProductenFrame,
            **STIJLEN["entry"],
            height=3,
            yscrollcommand=laatsteProductenScroll.set,
            state=tk.DISABLED
        )
        self.laatsteProductenText.pack(fill=tk.X)
        laatsteProductenScroll.config(command=self.laatsteProductenText.yview)
        
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
        
        # Live logging frame in de voet
        logFrame = tk.Frame(
            self.container,
            background=KLEUREN["achtergrond"],
            padx=10,
            pady=10,
            relief=tk.GROOVE,
            borderwidth=1
        )
        logFrame.pack(fill=tk.X, pady=10, side=tk.BOTTOM)
        
        # Titel voor live logging
        logLabel = tk.Label(
            logFrame,
            text="Live Logging",
            **label_stijl,
            font=("Arial", 10, "bold")
        )
        logLabel.pack(fill=tk.X)
        
        # Scrollbaar tekstveld voor live logging
        logScroll = tk.Scrollbar(logFrame)
        logScroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.logText = tk.Text(
            logFrame,
            **STIJLEN["entry"],
            height=3,
            yscrollcommand=logScroll.set,
            state=tk.DISABLED
        )
        self.logText.pack(fill=tk.X)
        logScroll.config(command=self.logText.yview)
        
        # Vul opgeslagen inloggegevens in als ze beschikbaar zijn
        if self.opgeslagen_gebruikersnaam:
            self.gebruikersnaamVar.set(self.opgeslagen_gebruikersnaam)
            self.onthoudInlogVar.set(True)
        if self.opgeslagen_wachtwoord:
            self.wachtwoordVar.set(self.opgeslagen_wachtwoord)
            self.onthoudInlogVar.set(True)
        
        # Vul opgeslagen URL in als beschikbaar
        if self.opgeslagen_url:
            self.urlVar.set(self.opgeslagen_url)
        else:
            # Standaard URL
            self.urlVar.set("http://metroeventsdc.rentpro5.nl/")
        
        # Initiële status
        self.updateResultaat("Gereed voor synchronisatie met Rentpro")
        self.updateLogText("Live logging geactiveerd")
    
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
    
    def updateLogText(self, tekst):
        """
        Voeg tekst toe aan het live logging veld
        
        Args:
            tekst (str): De tekst om toe te voegen
        """
        self.logText.config(state=tk.NORMAL)
        self.logText.insert(tk.END, tekst + "\n")
        self.logText.see(tk.END)  # Scroll naar nieuwste bericht
        self.logText.config(state=tk.DISABLED)
    
    def toon_overschrijf_waarschuwing(self):
        """Toon een waarschuwing als de gebruiker lokale data wil overschrijven"""
        if self.overschrijfVar.get():
            self.app.toonWaarschuwing(
                "Let op!", 
                "Je staat op het punt om lokale data te overschrijven met gegevens uit Rentpro. " +
                "Bestaande gegevens kunnen verloren gaan. Wees hier voorzichtig mee!"
            )
    
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
        url = self.urlVar.get().strip()
        
        if not gebruikersnaam or not wachtwoord:
            self.app.toonFoutmelding("Ontbrekende gegevens", "Vul de gebruikersnaam en wachtwoord in")
            return
        
        if not url:
            self.app.toonFoutmelding("Ontbrekende gegevens", "Vul de back-office URL in")
            return
        
        # Haal opties op
        overschrijf_lokaal = self.overschrijfVar.get()
        bereik = self.haalGeselecteerdBereik()
        
        # Sla inloggegevens op indien gewenst
        if self.onthoudInlogVar.get():
            from modules.settings import stelRentproGebruikersnaamIn, stelRentproWachtwoordIn, stelRentproURLIn
            stelRentproGebruikersnaamIn(gebruikersnaam)
            stelRentproWachtwoordIn(wachtwoord)
            stelRentproURLIn(url)
        else:
            # Verwijder opgeslagen inloggegevens als gebruiker niet wil onthouden
            from modules.settings import stelRentproGebruikersnaamIn, stelRentproWachtwoordIn, stelRentproURLIn
            stelRentproGebruikersnaamIn("")
            stelRentproWachtwoordIn("")
            stelRentproURLIn("")
        
        # Start de synchronisatie in een aparte thread
        self.is_bezig = True
        self.voortgangBalk.start(10)  # Start de voortgangsbalk (interval in ms)
        self.voortgangLabel.config(text="Bezig met synchroniseren...")
        self.app.updateStatus("Bezig met Rentpro synchronisatie...")
        self.updateResultaat(f"Synchronisatie gestart {'(overschrijven)' if overschrijf_lokaal else '(alleen lege velden)'}")
        self.updateLogText(f"Synchronisatie gestart met {url}")
        
        # Disable start knop tijdens verwerking
        self.startButton.config(state=tk.DISABLED)
        
        # Start een asyncio event loop in een aparte thread
        threading.Thread(target=self.run_async_task, args=(gebruikersnaam, wachtwoord, url, overschrijf_lokaal, bereik), daemon=True).start()
    
    def run_async_task(self, gebruikersnaam, wachtwoord, url, overschrijf_lokaal, bereik):
        """
        Voer asyncio taken uit in een aparte thread
        
        Args:
            gebruikersnaam (str): Rentpro gebruikersnaam
            wachtwoord (str): Rentpro wachtwoord
            url (str): De URL voor de Rentpro back-office
            overschrijf_lokaal (bool): Of lokale data overschreven moet worden
            bereik (tuple): Bereik van rijen om te synchroniseren of None voor alles
        """
        asyncio.run(self.synchroniseer(gebruikersnaam, wachtwoord, url, overschrijf_lokaal, bereik))
    
    async def synchroniseer(self, gebruikersnaam, wachtwoord, url, overschrijf_lokaal, bereik):
        """
        Asynchrone functie voor synchronisatie met Rentpro
        
        Args:
            gebruikersnaam (str): Rentpro gebruikersnaam
            wachtwoord (str): Rentpro wachtwoord
            url (str): De URL voor de Rentpro back-office
            overschrijf_lokaal (bool): Of lokale data overschreven moet worden
            bereik (tuple): Bereik van rijen om te synchroniseren of None voor alles
        """
        try:
            # Update UI
            self.update_ui_status("Verbinding maken met Rentpro...")
            self.updateLogText("Verbinding maken met Rentpro...")
            
            # Initialiseer de sessie
            await rentproHandler.initialize()
            
            # Login
            self.update_ui_status("Inloggen bij Rentpro...")
            self.updateLogText("Inloggen bij Rentpro...")
            login_success = await rentproHandler.login(gebruikersnaam, wachtwoord, url)
            
            if not login_success:
                self.update_ui_error("Inloggen bij Rentpro mislukt. Controleer je inloggegevens.")
                self.updateLogText("Inloggen bij Rentpro mislukt. Controleer je inloggegevens.")
                return
            
            # Haal producten op
            self.update_ui_status("Ophalen van productgegevens...")
            self.updateLogText("Ophalen van productgegevens...")
            success = await rentproHandler.haal_producten_op(overschrijf_lokaal, bereik)
            
            if success:
                self.update_ui_success("Synchronisatie succesvol afgerond")
                self.updateLogText("Synchronisatie succesvol afgerond")
                
                # Vraag of gebruiker het resultaat wil opslaan
                self.app.root.after(0, lambda: self.vraag_opslaan())
            else:
                self.update_ui_error("Fout bij ophalen van productgegevens")
                self.updateLogText("Fout bij ophalen van productgegevens")
                
        except Exception as e:
            logger.logFout(f"Fout bij synchronisatie: {e}")
            self.update_ui_error(f"Fout bij synchronisatie: {str(e)}")
            self.updateLogText(f"Fout bij synchronisatie: {str(e)}")
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
                    self.updateLogText("Wijzigingen opgeslagen in Excel-bestand")
                else:
                    self.app.updateStatus("Fout bij opslaan")
                    self.app.toonFoutmelding("Fout", "Kon wijzigingen niet opslaan")
                    self.updateResultaat("FOUT: Kon wijzigingen niet opslaan")
                    self.updateLogText("FOUT: Kon wijzigingen niet opslaan")
            else:
                self.updateResultaat("Wijzigingen NIET opgeslagen")
                self.updateLogText("Wijzigingen NIET opgeslagen")
                self.app.updateStatus("Wijzigingen niet opgeslagen")
    
    def login_zonder_synchronisatie(self):
        """Log in bij Rentpro zonder synchronisatie te starten"""
        if self.is_bezig:
            self.app.toonWaarschuwing("Bezig", "Er is al een actie bezig")
            return
        
        # Check inloggegevens
        gebruikersnaam = self.gebruikersnaamVar.get().strip()
        wachtwoord = self.wachtwoordVar.get().strip()
        url = self.urlVar.get().strip()
        
        if not gebruikersnaam or not wachtwoord:
            self.app.toonFoutmelding("Ontbrekende gegevens", "Vul de gebruikersnaam en wachtwoord in")
            return
        
        if not url:
            self.app.toonFoutmelding("Ontbrekende gegevens", "Vul de back-office URL in")
            return
        
        # Sla inloggegevens op indien gewenst
        if self.onthoudInlogVar.get():
            from modules.settings import stelRentproGebruikersnaamIn, stelRentproWachtwoordIn, stelRentproURLIn
            stelRentproGebruikersnaamIn(gebruikersnaam)
            stelRentproWachtwoordIn(wachtwoord)
            stelRentproURLIn(url)
        
        # Start het inloggen in een aparte thread
        self.is_bezig = True
        self.voortgangBalk.start(10)  # Start de voortgangsbalk (interval in ms)
        self.voortgangLabel.config(text="Bezig met inloggen...")
        self.app.updateStatus("Bezig met inloggen bij Rentpro...")
        self.updateResultaat("Inloggen bij Rentpro...")
        self.updateLogText("Inloggen bij Rentpro...")
        
        # Disable knoppen tijdens verwerking
        self.inlogButton.config(state=tk.DISABLED)
        self.startButton.config(state=tk.DISABLED)
        
        # Start een asyncio event loop in een aparte thread
        threading.Thread(target=self.run_login_task, args=(gebruikersnaam, wachtwoord, url), daemon=True).start()
    
    def run_login_task(self, gebruikersnaam, wachtwoord, url):
        """
        Voer asyncio login taak uit in een aparte thread
        
        Args:
            gebruikersnaam (str): Rentpro gebruikersnaam
            wachtwoord (str): Rentpro wachtwoord
            url (str): De URL voor de Rentpro back-office
        """
        asyncio.run(self.login_en_toon_producten(gebruikersnaam, wachtwoord, url))
    
    async def login_en_toon_producten(self, gebruikersnaam, wachtwoord, url):
        """
        Asynchrone functie voor inloggen en producten ophalen
        
        Args:
            gebruikersnaam (str): Rentpro gebruikersnaam
            wachtwoord (str): Rentpro wachtwoord
            url (str): De URL voor de Rentpro back-office
        """
        try:
            # Update UI
            self.update_ui_status("Verbinding maken met Rentpro...")
            self.updateLogText("Verbinding maken met Rentpro...")
            
            # Initialiseer de sessie
            await rentproHandler.initialize()
            
            # Login
            self.update_ui_status("Inloggen bij Rentpro...")
            self.updateLogText("Inloggen bij Rentpro...")
            login_success = await rentproHandler.login(gebruikersnaam, wachtwoord, url)
            
            if not login_success:
                self.update_ui_error("Inloggen bij Rentpro mislukt. Controleer je inloggegevens.")
                self.updateLogText("Inloggen bij Rentpro mislukt. Controleer je inloggegevens.")
                return
            
            # Update status
            self.is_ingelogd = True
            self.app.root.after(0, lambda: self.statusLabel.config(text="Ingelogd ✓", fg="#00AA00"))
            self.update_ui_success("Succesvol ingelogd bij Rentpro")
            self.updateLogText("Succesvol ingelogd bij Rentpro")
            
            # Haal producten op en toon overzicht
            self.update_ui_status("Ophalen van productenoverzicht...")
            self.updateLogText("Ophalen van productenoverzicht...")
            producten = await self.haal_producten_op()
            if producten:
                self.app.root.after(0, lambda: self.toon_product_overzicht(producten))
                self.update_ui_success("Productenoverzicht bijgewerkt")
                self.updateLogText("Productenoverzicht bijgewerkt")
            else:
                self.update_ui_error("Geen producten gevonden of fout bij ophalen")
                self.updateLogText("Geen producten gevonden of fout bij ophalen")
                
        except Exception as e:
            logger.logFout(f"Fout bij inloggen: {e}")
            self.update_ui_error(f"Fout bij inloggen: {str(e)}")
            self.updateLogText(f"Fout bij inloggen: {str(e)}")
        finally:
            # Sluit de sessie
            await rentproHandler.close()
            
            # Herstel UI
            self.app.root.after(0, self.reset_login_ui)
    
    def reset_login_ui(self):
        """Reset de UI na inloggen"""
        self.is_bezig = False
        self.voortgangBalk.stop()
        self.inlogButton.config(state=tk.NORMAL)
        self.startButton.config(state=tk.NORMAL)
    
    def toon_product_overzicht(self, producten):
        """
        Toon een overzicht van producten in de gescheiden tekstvelden
        
        Args:
            producten (list): Lijst van tuples met (product_id, product_naam)
        """
        if not producten:
            return
        
        # Maak het eerste tekstveld bewerkbaar
        self.eersteProductenText.config(state=tk.NORMAL)
        self.eersteProductenText.delete(1.0, tk.END)
        
        # Toon de eerste 3 producten
        eerste_producten = producten[:3]
        for product_id, product_naam in eerste_producten:
            self.eersteProductenText.insert(tk.END, f"{product_id:<10} {product_naam}\n")
        
        # Maak het eerste tekstveld weer alleen-lezen
        self.eersteProductenText.config(state=tk.DISABLED)
        
        # Maak het tweede tekstveld bewerkbaar
        self.laatsteProductenText.config(state=tk.NORMAL)
        self.laatsteProductenText.delete(1.0, tk.END)
        
        # Toon de laatste 3 producten
        laatste_producten = producten[-3:] if len(producten) > 3 else []
        for product_id, product_naam in laatste_producten:
            self.laatsteProductenText.insert(tk.END, f"{product_id:<10} {product_naam}\n")
        
        # Maak het tweede tekstveld weer alleen-lezen
        self.laatsteProductenText.config(state=tk.DISABLED)
    
    async def haal_producten_op(self):
        """
        Haal producten op uit Rentpro via API-mode of browser-mode
        
        Returns:
            list: Lijst van tuples met (product_id, product_naam)
        """
        try:
            # Navigeer naar de productpagina
            await rentproHandler.navigeer_naar_producten()
            
            # Controleer of we in API-mode zijn
            if rentproHandler.gebruik_api_mode:
                # Haal producten op via API handler
                logger.logInfo("Producten ophalen via API")
                self.updateLogText("Producten ophalen via API")
                producten_lijst = await rentproHandler.api_handler.get_products_list()
                
                # Converteer naar het verwachte formaat (list of tuples)
                producten = []
                for product in producten_lijst:
                    if "id" in product and "naam" in product:
                        producten.append((product["id"], product["naam"]))
                
                return producten
            else:
                # Browser mode - gebruik JavaScript
                logger.logInfo("Producten ophalen via browser JavaScript")
                self.updateLogText("Producten ophalen via browser JavaScript")
                js_code = """
                (function() {
                    const rows = document.querySelectorAll('table.grid tbody tr');
                    const products = [];
                    
                    for (let row of rows) {
                        const idCell = row.querySelector('td:nth-child(1)');
                        const nameCell = row.querySelector('td:nth-child(2)');
                        
                        if (idCell && nameCell) {
                            products.push([idCell.textContent.trim(), nameCell.textContent.trim()]);
                        }
                    }
                    
                    return products;
                })();
                """
                
                producten = await rentproHandler.evalueer_javascript(js_code)
                
                if not producten or not isinstance(producten, list):
                    logger.logFout("Geen producten gevonden of ongeldig formaat")
                    self.updateLogText("Geen producten gevonden of ongeldig formaat")
                    return []
                
                return producten
        except Exception as e:
            logger.logFout(f"Fout bij ophalen producten: {e}")
            self.updateLogText(f"Fout bij ophalen producten: {e}")
            return []
