"""
Acties tabblad voor Excelladin Reloaded
"""
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

from assets.theme import KLEUREN, STIJLEN
from modules.gui.components import Tooltip
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
        
        # Bouw de UI
        self._buildUI()
    
    def _buildUI(self):
        """Bouw de UI van het Acties tabblad"""
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
            text="Selecteer acties om uit te voeren op het Excel-bestand",
            **STIJLEN["label"],
            pady=10
        )
        instructieLabel.pack(fill=tk.X)
        
        # Bereik selectie frame
        bereikFrame = tk.Frame(
            container,
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
        
        allesRadio = ttk.Radiobutton(
            bereikFrame,
            text="Alles",
            variable=self.bereikVar,
            value="alles"
        )
        allesRadio.pack(side=tk.LEFT, padx=5)
        Tooltip(allesRadio, "Voer acties uit op alle rijen")
        
        enkelRadio = ttk.Radiobutton(
            bereikFrame,
            text="Rij:",
            variable=self.bereikVar,
            value="enkel"
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
        
        bereikRadio = ttk.Radiobutton(
            bereikFrame,
            text="Bereik:",
            variable=self.bereikVar,
            value="bereik"
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
        
        # Actielijst label
        actielijstLabel = tk.Label(
            container,
            text="Beschikbare Acties:",
            **STIJLEN["label"],
            anchor=tk.W,
            pady=5
        )
        actielijstLabel.pack(fill=tk.X, pady=(10, 0))
        
        # Scroll container voor acties
        actieScrollFrame = tk.Frame(
            container,
            background=KLEUREN["achtergrond"]
        )
        actieScrollFrame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(actieScrollFrame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas voor scrollbare inhoud
        self.actieCanvas = tk.Canvas(
            actieScrollFrame,
            background=KLEUREN["achtergrond"],
            yscrollcommand=scrollbar.set,
            highlightthickness=0
        )
        self.actieCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.actieCanvas.yview)
        
        # Frame voor acties in canvas
        self.actieListFrame = tk.Frame(
            self.actieCanvas,
            background=KLEUREN["achtergrond"]
        )
        
        # Canvas window
        self.actieCanvasWindow = self.actieCanvas.create_window(
            (0, 0),
            window=self.actieListFrame,
            anchor="nw",
            width=350  # Breedte van de canvas minus scrollbar
        )
        
        # Configureer canvas om mee te schalen met frame
        self.actieListFrame.bind("<Configure>", self._configureActieCanvas)
        self.actieCanvas.bind("<Configure>", self._onCanvasResize)
        
        # Uitvoerknop
        self.uitvoerButton = ttk.Button(
            container,
            text="Voer Geselecteerde Acties Uit",
            command=self.voerGeselecteerdeActiesUit
        )
        self.uitvoerButton.pack(fill=tk.X, pady=10)
        Tooltip(self.uitvoerButton, "Voer alle geselecteerde acties uit in volgorde")
    
    def _configureActieCanvas(self, event):
        """Pas de canvas grootte aan aan het actieListFrame"""
        # Update het scrollgebied naar het nieuwe formaat van het actieListFrame
        self.actieCanvas.configure(scrollregion=self.actieCanvas.bbox("all"))
    
    def _onCanvasResize(self, event):
        """Pas de breedte van het actieListFrame aan"""
        # Pas de breedte van het window aan aan de canvas
        self.actieCanvas.itemconfig(self.actieCanvasWindow, width=event.width)
    
    def updateNaLaden(self):
        """Update de actielijst na het laden van een Excel-bestand"""
        self._voegActiesToe()
    
    def _voegActiesToe(self):
        """Voeg beschikbare acties toe aan de actielijst"""
        # Verwijder bestaande actieframes
        for widget in self.actieListFrame.winfo_children():
            widget.destroy()
        
        # Voeg kolomvullen actie toe voor elke kolom als er een Excel-bestand is geladen
        if excelHandler.isBestandGeopend():
            for kolomNaam in excelHandler.kolomNamen:
                actieFrame = tk.Frame(
                    self.actieListFrame,
                    background=KLEUREN["achtergrond"],
                    padx=5,
                    pady=5,
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
            opslaan = messagebox.askyesno(
                "Opslaan",
                "Wil je de wijzigingen opslaan in het Excel-bestand?"
            )
            if opslaan and excelHandler.slaOp():
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
                messagebox.showwarning("Waarschuwing", "Selecteer ten minste één kolom")
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
        
        # Verzamel geselecteerde acties
        geselecteerdeActies = []
        
        for widget in self.actieListFrame.winfo_children():
            if hasattr(widget, 'checkVar') and widget.checkVar.get():
                if widget.actieType == "kolomVullen":
                    geselecteerdeActies.append((widget.actieType, widget.kolomNaam))
        
        if not geselecteerdeActies:
            self.app.toonFoutmelding("Fout", "Geen acties geselecteerd")
            return
        
        # Maak een tijdelijke workflow
        workflow = workflowManager.maakWorkflow("temp_workflow")
        
        # Doorloop geselecteerde acties en voeg ze toe aan de workflow
        for actieType, kolomNaam in geselecteerdeActies:
            if actieType == "kolomVullen":
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
            opslaan = messagebox.askyesno(
                "Opslaan",
                "Acties succesvol uitgevoerd. Wil je de wijzigingen opslaan?"
            )
            
            if opslaan:
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
