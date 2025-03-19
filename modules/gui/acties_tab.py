"""
Acties tabblad voor Excelladin Reloaded
"""
import tkinter as tk
from tkinter import ttk, simpledialog

from assets.theme import KLEUREN, STIJLEN
from modules.gui.components import Tooltip, StijlvollePopup
from modules.excel_handler import excelHandler
from modules.actions import BESCHIKBARE_ACTIES, voerActieUit
from modules.workflow import workflowManager

class ActiesTab:
    """
    Klasse voor het Acties tabblad
    """
    def __init__(self, parent, app):
        """
        Initialiseer het Acties tabblad
        
        Args:
            parent: Het parent frame waarin dit tabblad wordt geplaatst
            app: De hoofdapplicatie (ExcelladinApp instance)
        """
        self.parent = parent
        self.app = app
        self.categorieFrames = {}
        
        # Bouw de UI
        self._buildUI()
    
    def _buildUI(self):
        """Bouw de UI van het Acties tabblad"""
        # Hoofdcontainer met padding
        self.container = tk.Frame(
            self.parent,
            background=KLEUREN["achtergrond"],
            padx=20,
            pady=20
        )
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Label met instructie
        instructieLabel = tk.Label(
            self.container,
            text="Selecteer acties om uit te voeren op het Excel-bestand",
            **STIJLEN["label"],
            pady=10
        )
        instructieLabel.pack(fill=tk.X)
        
        # Bereik selectie frame
        bereikFrame = tk.Frame(
            self.container,
            background=KLEUREN["achtergrond"],
            padx=10,
            pady=10
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
        Tooltip(allesRadio, "Voer acties uit op alle rijen")
        
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
        Tooltip(enkelRadio, "Voer acties uit op één specifieke rij")
        
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
        Tooltip(bereikRadio, "Voer acties uit op een bereik van rijen")
        
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
        
        # Bouw categorietabbladen
        self._buildCategorieTabbladen()
        
        # Uitvoerknop
        self.uitvoerButton = ttk.Button(
            self.container,
            text="Voer Geselecteerde Acties Uit",
            command=self.voerGeselecteerdeActiesUit
        )
        self.uitvoerButton.pack(fill=tk.X, pady=10)
        Tooltip(self.uitvoerButton, "Voer alle geselecteerde acties uit in volgorde")
    
    def _buildCategorieTabbladen(self):
        """Bouw tabbladen voor actiecategorieën"""
        self.categorieTabs = ttk.Notebook(self.container)
        self.categorieTabs.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Frames voor categorieën
        self.categorieFrames = {}
        for categorie in ["Inlezen vanuit RentPro", "Lokale sheet bijwerken", "Uploaden naar RentPro", "Algemeen"]:
            frame = tk.Frame(
                self.categorieTabs,
                background=KLEUREN["achtergrond"],
                padx=10, pady=10
            )
            
            # Actieknoppen bovenaan categorie
            buttonFrame = tk.Frame(frame, background=KLEUREN["achtergrond"])
            buttonFrame.pack(fill=tk.X, pady=5)
            
            selectAllBtn = tk.Button(
                buttonFrame, 
                text="Selecteer alles", 
                command=lambda c=categorie: self.selecteerAlleActies(c, True),
                bg="#000080",  # Donkerblauw
                fg="#FFFF00",  # Fel geel
                font=("Arial", 10)
            )
            selectAllBtn.pack(side=tk.LEFT, padx=5)
            Tooltip(selectAllBtn, f"Selecteer alle acties in de categorie '{categorie}'")
            
            deselectAllBtn = tk.Button(
                buttonFrame, 
                text="Deselecteer alles",
                command=lambda c=categorie: self.selecteerAlleActies(c, False),
                bg="#000080",  # Donkerblauw
                fg="#FFFF00",  # Fel geel
                font=("Arial", 10)
            )
            deselectAllBtn.pack(side=tk.LEFT, padx=5)
            Tooltip(deselectAllBtn, f"Deselecteer alle acties in de categorie '{categorie}'")
            
            # Scroll container voor acties
            actieScrollFrame = tk.Frame(
                frame,
                background=KLEUREN["achtergrond"]
            )
            actieScrollFrame.pack(fill=tk.BOTH, expand=True)
            
            # Scrollbar
            scrollbar = tk.Scrollbar(actieScrollFrame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Canvas voor scrollbare inhoud
            actieCanvas = tk.Canvas(
                actieScrollFrame,
                background=KLEUREN["achtergrond"],
                yscrollcommand=scrollbar.set,
                highlightthickness=0
            )
            actieCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=actieCanvas.yview)
            
            # Frame voor acties in canvas
            actieListFrame = tk.Frame(
                actieCanvas,
                background=KLEUREN["achtergrond"]
            )
            
            # Canvas window
            actieCanvasWindow = actieCanvas.create_window(
                (0, 0),
                window=actieListFrame,
                anchor="nw",
                width=350  # Breedte minus scrollbar
            )
            
            # Configuratie voor scrolling
            actieListFrame.bind("<Configure>", 
                              lambda event, canvas=actieCanvas: canvas.configure(
                                  scrollregion=canvas.bbox("all")
                              ))
            actieCanvas.bind("<Configure>", 
                           lambda event, canvas=actieCanvas, win=actieCanvasWindow: 
                           canvas.itemconfig(win, width=event.width))
            
            # Sla referenties op voor later gebruik
            self.categorieFrames[categorie] = {
                'frame': frame,
                'actieListFrame': actieListFrame,
                'actieCanvas': actieCanvas,
                'scrollbar': scrollbar
            }
            
            # Voeg toe aan tabblad
            self.categorieTabs.add(frame, text=categorie)
    
    def selecteerAlleActies(self, categorie, select=True):
        """
        Selecteer of deselecteer alle acties in een categorie
        
        Args:
            categorie (str): De categorie waarvan alle acties geselecteerd/gedeselecteerd moeten worden
            select (bool): True om te selecteren, False om te deselecteren
        """
        if categorie not in self.categorieFrames:
            return
        
        actieListFrame = self.categorieFrames[categorie]['actieListFrame']
        for widget in actieListFrame.winfo_children():
            if hasattr(widget, 'checkVar'):
                widget.checkVar.set(select)
    
    def updateNaLaden(self):
        """Update de actielijst na het laden van een Excel-bestand"""
        self._voegActiesToe()
    
    def _voegActiesToe(self):
        """Voeg beschikbare acties toe aan de actielijst, gegroepeerd per categorie"""
        # Initialiseer lege groepen
        actie_groepen = {}
        
        # Groepeer acties per categorie
        for actieNaam, actie in BESCHIKBARE_ACTIES.items():
            categorie = actie.categorie
            if categorie not in actie_groepen:
                actie_groepen[categorie] = []
            actie_groepen[categorie].append((actieNaam, actie))
        
        # Voor elke categorie, voeg acties toe aan het juiste frame
        for categorie, acties in actie_groepen.items():
            if categorie not in self.categorieFrames:
                continue
                
            actieListFrame = self.categorieFrames[categorie]['actieListFrame']
            
            # Verwijder bestaande actieframes
            for widget in actieListFrame.winfo_children():
                widget.destroy()
            
            for actieNaam, actie in acties:
                # Maak actie-frame
                actieFrame = tk.Frame(
                    actieListFrame,
                    background=KLEUREN["achtergrond"],
                    padx=5, pady=5,
                    relief=tk.GROOVE,
                    borderwidth=1
                )
                actieFrame.pack(fill=tk.X, pady=2)
                
                # Selectie checkbox
                checkVar = tk.BooleanVar(value=False)
                checkBox = ttk.Checkbutton(
                    actieFrame,
                    text=f"{actie.naam}",
                    variable=checkVar
                )
                checkBox.pack(side=tk.LEFT)
                
                # Hover tooltip met beschrijving
                Tooltip(checkBox, actie.beschrijving)
                
                # Uitvoerknop
                uitvoerBtn = ttk.Button(
                    actieFrame,
                    text="Uitvoeren",
                    command=lambda a=actieNaam: self.voerActieUit(a)
                )
                uitvoerBtn.pack(side=tk.RIGHT)
                Tooltip(uitvoerBtn, f"Voer actie '{actie.naam}' direct uit")
                
                # Informatie label
                infoLabel = tk.Label(
                    actieFrame,
                    text=actie.beschrijving[:40] + "..." if len(actie.beschrijving) > 40 else actie.beschrijving,
                    **STIJLEN["label"],
                    anchor=tk.W
                )
                infoLabel.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                
                # Bewaar referenties
                actieFrame.checkVar = checkVar
                actieFrame.uitvoerBtn = uitvoerBtn
                actieFrame.actieNaam = actieNaam
                actieFrame.actieType = actie.__class__.__name__
        
        # Voeg kolomvullen actie toe voor elke kolom als er een Excel-bestand is geladen
        if excelHandler.isBestandGeopend():
            categorie = "Lokale sheet bijwerken"
            if categorie in self.categorieFrames:
                actieListFrame = self.categorieFrames[categorie]['actieListFrame']
                
                for kolomNaam in excelHandler.kolomNamen:
                    actieFrame = tk.Frame(
                        actieListFrame,
                        background=KLEUREN["achtergrond"],
                        padx=5, pady=5,
                        relief=tk.GROOVE,
                        borderwidth=1
                    )
                    actieFrame.pack(fill=tk.X, pady=2)
                    
                    # Selectie checkbox
                    checkVar = tk.BooleanVar(value=False)
                    checkBox = ttk.Checkbutton(
                        actieFrame,
                        text=f"{kolomNaam} vullen",
                        variable=checkVar
                    )
                    checkBox.pack(side=tk.LEFT)
                    
                    # Uitvoerknop voor deze actie
                    uitvoerBtn = ttk.Button(
                        actieFrame,
                        text="Uitvoeren",
                        command=lambda k=kolomNaam: self.voerKolomVullenActieUit(k)
                    )
                    uitvoerBtn.pack(side=tk.RIGHT)
                    Tooltip(uitvoerBtn, f"Vul kolom '{kolomNaam}' met gecombineerde data uit andere kolommen")
                    
                    # Bewaar de variabelen en widgets voor later gebruik
                    actieFrame.checkVar = checkVar
                    actieFrame.uitvoerBtn = uitvoerBtn
                    actieFrame.kolomNaam = kolomNaam
                    actieFrame.actieType = "kolomVullen"
    
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
    
    def voerActieUit(self, actieNaam):
        """
        Voer een actie uit op basis van naam
        
        Args:
            actieNaam (str): Naam van de actie om uit te voeren
        """
        if not excelHandler.isBestandGeopend():
            self.app.toonFoutmelding("Fout", "Geen Excel-bestand geopend")
            return
        
        actie = BESCHIKBARE_ACTIES.get(actieNaam)
        if not actie:
            self.app.toonFoutmelding("Fout", f"Actie '{actieNaam}' bestaat niet")
            return
        
        # Vraag om parameters op basis van actie type
        parameters = self._vraagActieParameters(actie)
        if not parameters:
            return
        
        # Bepaal bereik
        bereik = self.haalGeselecteerdBereik()
        
        # Voer actie uit
        self.app.updateStatus(f"Bezig met uitvoeren van actie '{actieNaam}'...")
        resultaat = voerActieUit(actieNaam, parameters, bereik)
        
        if resultaat.succes:
            self.app.updateStatus("Actie succesvol uitgevoerd")
            self.app.toonSuccesmelding("Succes", resultaat.bericht)
            # Vraag of gebruiker wil opslaan
            popup = StijlvollePopup(
                self.app.root,
                "Opslaan",
                "Wil je de wijzigingen opslaan in het Excel-bestand?",
                popup_type="vraag",
                actie_knoppen=[
                    {'tekst': 'Ja', 'commando': lambda: popup.ja_actie(), 'primair': True},
                    {'tekst': 'Nee', 'commando': lambda: popup.nee_actie()}
                ]
            )
            if popup.wacht_op_antwoord() and excelHandler.slaOp():
                self.app.updateStatus("Wijzigingen opgeslagen")
        else:
            self.app.updateStatus("Fout bij uitvoeren actie")
            self.app.toonFoutmelding("Fout", resultaat.bericht)
    
    def _vraagActieParameters(self, actie):
        """
        Vraag parameters voor een actie op basis van het type
        
        Args:
            actie: De actie waarvoor parameters gevraagd moeten worden
            
        Returns:
            dict: Dictionary met parameters of None bij annuleren
        """
        # Implementeer hier de logica om parameters te vragen op basis van actie type
        # Dit is een eenvoudige implementatie die uitgebreid kan worden
        
        if isinstance(actie, BESCHIKBARE_ACTIES["kolomVullen"].__class__):
            # Vraag om bronkolommen en formaat
            bronKolommen = self._toonKolomKeuzeDlg()
            if not bronKolommen:
                return None
            
            # Vraag om doelkolom
            doelKolom = simpledialog.askstring(
                "Doelkolom", 
                "Geef de naam van de doelkolom op"
            )
            if not doelKolom:
                return None
            
            # Vraag om formaat string
            formaat = simpledialog.askstring(
                "Formaat", 
                "Geef het formaat op. Gebruik {kolomnaam} voor waarden uit kolommen.\nVoorbeeld: '{Voornaam} {Achternaam}'"
            )
            if not formaat:
                return None
            
            return {
                "doelKolom": doelKolom,
                "bronKolommen": bronKolommen,
                "formaat": formaat
            }
        
        elif isinstance(actie, BESCHIKBARE_ACTIES["kolomSchoonmaken"].__class__):
            # Vraag om kolom
            kolom = simpledialog.askstring(
                "Kolom", 
                "Geef de naam van de kolom op die je wilt schoonmaken"
            )
            if not kolom:
                return None
            
            # Vraag opties
            verwijderSpaties = tk.messagebox.askyesno(
                "Verwijder spaties", 
                "Wil je extra spaties verwijderen?"
            )
            
            verwijderLeestekens = tk.messagebox.askyesno(
                "Verwijder leestekens", 
                "Wil je leestekens verwijderen?"
            )
            
            return {
                "kolom": kolom,
                "verwijderSpaties": verwijderSpaties,
                "verwijderLeestekens": verwijderLeestekens
            }
        
        # Voeg hier meer actie types toe
        
        # Standaard: vraag om parameters via dialoog
        self.app.toonWaarschuwing("Niet geïmplementeerd", f"Parameters vragen voor actie '{actie.naam}' is nog niet geïmplementeerd")
        return None
    
    def voerKolomVullenActieUit(self, kolomNaam):
        """
        Voer een kolomVullen actie uit voor de gegeven kolom
        
        Args:
            kolomNaam (str): Naam van de kolom om te vullen
        """
        if not excelHandler.isBestandGeopend():
            self.app.toonFoutmelding("Fout", "Geen Excel-bestand geopend")
            return
        
        # Vraag om bronkolommen en formaat
        
        # Toon kolomkeuzedialoog
        bronKolommen = self._toonKolomKeuzeDlg()
        if not bronKolommen:
            return
        
        # Vraag om formaat string
        formaat = simpledialog.askstring(
            "Formaat", 
            "Geef het formaat op. Gebruik {kolomnaam} voor waarden uit kolommen.\nVoorbeeld: '{Voornaam} {Achternaam}'"
        )
        
        if not formaat:
            return
        
        # Maak parameters
        parameters = {
            "doelKolom": kolomNaam,
            "bronKolommen": bronKolommen,
            "formaat": formaat
        }
        
        # Bepaal bereik
        bereik = self.haalGeselecteerdBereik()
        
        # Voer actie uit
        self.app.updateStatus(f"Bezig met vullen van kolom '{kolomNaam}'...")
        resultaat = voerActieUit("kolomVullen", parameters, bereik)
        
        if resultaat.succes:
            self.app.updateStatus("Kolom succesvol gevuld")
            self.app.toonSuccesmelding("Succes", resultaat.bericht)
            # Vraag of gebruiker wil opslaan
            popup = StijlvollePopup(
                self.app.root,
                "Opslaan",
                "Wil je de wijzigingen opslaan in het Excel-bestand?",
                popup_type="vraag",
                actie_knoppen=[
                    {'tekst': 'Ja', 'commando': lambda: popup.ja_actie(), 'primair': True},
                    {'tekst': 'Nee', 'commando': lambda: popup.nee_actie()}
                ]
            )
            if popup.wacht_op_antwoord() and excelHandler.slaOp():
                self.app.updateStatus("Wijzigingen opgeslagen")
        else:
            self.app.updateStatus("Fout bij vullen kolom")
            self.app.toonFoutmelding("Fout", resultaat.bericht)
    
    def _toonKolomKeuzeDlg(self):
        """
        Toon een dialoog om bronkolommen te selecteren
        
        Returns:
            list: Lijst met geselecteerde kolomnamen of None bij annuleren
        """
        # Maak een nieuw dialoogvenster
        dlg = tk.Toplevel(self.app.root)
        dlg.title("Selecteer Bronkolommen")
        dlg.geometry("300x400")
        dlg.transient(self.app.root)
        dlg.grab_set()
        
        # Centereer op het hoofdvenster
        dlg.update_idletasks()
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() - dlg.winfo_width()) // 2
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() - dlg.winfo_height()) // 2
        dlg.geometry(f"+{x}+{y}")
        
        # Instructie label
        instructieLabel = tk.Label(
            dlg,
            text="Selecteer de kolommen die je wilt gebruiken als bron",
            **STIJLEN["label"],
            wraplength=280,
            justify=tk.LEFT,
            padx=10,
            pady=10
        )
        instructieLabel.pack(fill=tk.X)
        
        # Frame voor checkboxes
        checkFrame = tk.Frame(dlg, background=KLEUREN["achtergrond"])
        checkFrame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas voor scrolling
        canvas = tk.Canvas(
            checkFrame,
            background=KLEUREN["achtergrond"],
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(checkFrame, orient="vertical", command=canvas.yview)
        
        scrollFrame = tk.Frame(canvas, background=KLEUREN["achtergrond"])
        
        scrollFrame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollFrame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Voeg checkboxes toe voor elke kolom
        checkVars = {}
        for kolom in excelHandler.kolomNamen:
            var = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(
                scrollFrame,
                text=kolom,
                variable=var
            )
            checkbox.pack(anchor=tk.W, pady=2)
            checkVars[kolom] = var
        
        # Buttons
        buttonFrame = tk.Frame(dlg, background=KLEUREN["achtergrond"])
        buttonFrame.pack(fill=tk.X, padx=10, pady=10)
        
        # Resultaat opslag
        result = {"kolommen": None}
        
        # OK button functie
        def bevestig():
            geselecteerd = [k for k, v in checkVars.items() if v.get()]
            if not geselecteerd:
                self.app.toonWaarschuwing("Waarschuwing", "Selecteer ten minste één kolom")
                return
            
            result["kolommen"] = geselecteerd
            dlg.destroy()
        
        # Annuleren button functie
        def annuleer():
            dlg.destroy()
        
        # Buttons
        okButton = ttk.Button(buttonFrame, text="OK", command=bevestig)
        cancelButton = ttk.Button(buttonFrame, text="Annuleren", command=annuleer)
        
        okButton.pack(side=tk.RIGHT, padx=5)
        cancelButton.pack(side=tk.RIGHT, padx=5)
        
        # Wacht tot dialoog sluit
        self.app.root.wait_window(dlg)
        
        return result["kolommen"]
    
    def voerGeselecteerdeActiesUit(self):
        """Voer alle geselecteerde acties uit in volgorde"""
        if not excelHandler.isBestandGeopend():
            self.app.toonFoutmelding("Fout", "Geen Excel-bestand geopend")
            return
        
        # Verzamel geselecteerde acties uit alle categorieën
        geselecteerdeActies = []
        
        for categorie, frames in self.categorieFrames.items():
            actieListFrame = frames['actieListFrame']
            
            for widget in actieListFrame.winfo_children():
                if hasattr(widget, 'checkVar') and widget.checkVar.get():
                    if hasattr(widget, 'actieNaam'):
                        geselecteerdeActies.append(widget.actieNaam)
                    elif hasattr(widget, 'kolomNaam') and widget.actieType == "kolomVullen":
                        geselecteerdeActies.append(("kolomVullen", widget.kolomNaam))
        
        if not geselecteerdeActies:
            self.app.toonFoutmelding("Fout", "Geen acties geselecteerd")
            return
        
        # Maak een tijdelijke workflow
        workflow = workflowManager.maakWorkflow("temp_workflow")
        
        # Doorloop geselecteerde acties en voeg ze toe aan de workflow
        for actie in geselecteerdeActies:
            if isinstance(actie, tuple) and actie[0] == "kolomVullen":
                # Speciale afhandeling voor kolomVullen acties
                actieType, kolomNaam = actie
                
                # Vraag om bronkolommen en formaat
                bronKolommen = self._toonKolomKeuzeDlg()
                if not bronKolommen:
                    continue
                
                # Vraag om formaat string
                formaat = simpledialog.askstring(
                    "Formaat", 
                    f"Geef het formaat op voor kolom {kolomNaam}.\nGebruik {{kolomnaam}} voor waarden uit kolommen.\nVoorbeeld: '{{Voornaam}} {{Achternaam}}'"
                )
                
                if not formaat:
                    continue
                
                # Maak parameters
                parameters = {
                    "doelKolom": kolomNaam,
                    "bronKolommen": bronKolommen,
                    "formaat": formaat
                }
                
                # Voeg toe aan workflow
                workflow.voegActieToe(actieType, parameters)
            else:
                # Standaard acties
                actieNaam = actie
                actie_obj = BESCHIKBARE_ACTIES.get(actieNaam)
                
                if not actie_obj:
                    self.app.toonWaarschuwing("Waarschuwing", f"Actie '{actieNaam}' bestaat niet")
                    continue
                
                # Vraag parameters
                parameters = self._vraagActieParameters(actie_obj)
                if not parameters:
                    continue
                
                # Voeg toe aan workflow
                workflow.voegActieToe(actieNaam, parameters)
        
        if not workflow.acties:
            self.app.toonFoutmelding("Info", "Geen acties geconfigureerd")
            return
        
        # Bepaal bereik
        bereik = self.haalGeselecteerdBereik()
        
        # Voer workflow uit met voortgangsupdate
        def updateVoortgang(percentage, actieNaam):
            self.app.updateStatus(f"Uitvoeren: {actieNaam} ({percentage:.1f}%)")
            self.app.root.update_idletasks()
        
        self.app.updateStatus("Bezig met uitvoeren van acties...")
        succes = workflow.voerUit(updateVoortgang, bereik)
        
        # Verwijder tijdelijke workflow
        workflowManager.verwijderWorkflow("temp_workflow")
        
        if succes:
            # Vraag of gebruiker het resultaat wil opslaan
            popup = StijlvollePopup(
                self.app.root,
                "Opslaan",
                "Acties succesvol uitgevoerd. Wil je de wijzigingen opslaan?",
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
                else:
                    self.app.updateStatus("Fout bij opslaan")
                    self.app.toonFoutmelding("Fout", "Kon wijzigingen niet opslaan")
            else:
                self.app.updateStatus("Wijzigingen niet opgeslagen")
        else:
            self.app.updateStatus("Fout bij uitvoeren acties")
            self.app.toonFoutmelding("Fout", "Er is een fout opgetreden bij het uitvoeren van de acties")
