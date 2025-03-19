#!/usr/bin/env python
"""
Excelladin Reloaded - HTML Parser en ProductSheet Patch
Deze patch voegt functionaliteit toe om HTML bronbestanden te analyseren
en daaruit een ProductSheet te genereren.
"""
import os
import sys
import shutil
import datetime
import traceback
import importlib.util
import re

def pas_patch_toe():
    """
    Hoofdfunctie van de patch
    """
    # Log initialiseren
    log_entries = []
    log_entries.append(f"=== Excelladin Reloaded HTML Parser Patch ===")
    log_entries.append(f"Uitgevoerd op: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_entries.append("=" * 50)
    
    try:
        # Maak nieuwe html_parser.py module
        success_html_parser = maak_html_parser_module()
        if not success_html_parser:
            log_entries.append("FOUT: Kon de html_parser.py module niet aanmaken")
            schrijf_log(log_entries)
            return False
        
        log_entries.append("HTML Parser module succesvol aangemaakt")
        
        # Pas de gui.py module aan
        success_gui = pas_gui_module_aan()
        if not success_gui:
            log_entries.append("FOUT: Kon de gui.py module niet aanpassen")
            schrijf_log(log_entries)
            return False
        
        log_entries.append("GUI module succesvol aangepast")
        
        # Probeer BeautifulSoup te installeren als die nog niet is geïnstalleerd
        success_bs4 = installeer_beautifulsoup()
        if not success_bs4:
            log_entries.append("WAARSCHUWING: Kon BeautifulSoup4 niet automatisch installeren")
            log_entries.append("Voer handmatig 'pip install beautifulsoup4' uit om de functionaliteit te activeren")
        else:
            log_entries.append("BeautifulSoup4 succesvol geïnstalleerd of was al aanwezig")
        
        # Probeer patch logging naar logger module te sturen
        try:
            from modules.logger import logger
            logger.logPatch("HTML Parser en ProductSheet patch succesvol uitgevoerd")
        except Exception as e:
            log_entries.append(f"Info: Kon niet loggen naar logger module: {str(e)}")
        
        log_entries.append("Patch succesvol uitgevoerd!")
        schrijf_log(log_entries)
        return True
        
    except Exception as e:
        log_entries.append(f"FOUT: Onverwachte fout tijdens uitvoeren patch: {str(e)}")
        log_entries.append(traceback.format_exc())
        schrijf_log(log_entries)
        return False

def maak_html_parser_module():
    """
    Maak een nieuwe html_parser.py module
    
    Returns:
        bool: True als de module succesvol is aangemaakt, anders False
    """
    try:
        # Zorg dat de modules directory bestaat
        if not os.path.exists('modules'):
            os.makedirs('modules')
        
        # Pad naar de nieuwe module
        module_pad = os.path.join('modules', 'html_parser.py')
        
        # Controleer of het bestand al bestaat en maak een backup
        if os.path.exists(module_pad):
            backup_pad = f"{module_pad}.backup.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy2(module_pad, backup_pad)
            print(f"Backup gemaakt van bestaand html_parser.py: {backup_pad}")
        
        # HTML parser module inhoud
        html_parser_code = '''"""
HTML Parser module voor Excelladin Reloaded
Verantwoordelijk voor het analyseren van HTML bronbestanden en het extraheren van invoervelden
"""
import os
import re
from bs4 import BeautifulSoup
from modules.logger import logger

class HtmlParser:
    """
    HtmlParser klasse voor het verwerken van HTML bronbestanden
    """
    
    def __init__(self):
        """Initialiseer de HtmlParser"""
        self.bestand = None
        self.soup = None
        self.invoervelden = []
    
    def laad_bestand(self, bestandspad):
        """
        Laad een HTML bronbestand
        
        Args:
            bestandspad (str): Pad naar het HTML bronbestand
            
        Returns:
            bool: True als het bestand succesvol is geladen, anders False
        """
        try:
            # Controleer of het bestand bestaat
            if not os.path.exists(bestandspad):
                logger.logFout(f"Bestand niet gevonden: {bestandspad}")
                return False
            
            # Laad het bestand
            with open(bestandspad, 'r', encoding='utf-8', errors='replace') as f:
                inhoud = f.read()
            
            # Parse de inhoud
            self.soup = BeautifulSoup(inhoud, 'html.parser')
            self.bestand = bestandspad
            
            logger.logInfo(f"HTML bronbestand geladen: {bestandspad}")
            
            # Extraheer invoervelden
            self.zoek_invoervelden()
            
            return True
        except Exception as e:
            logger.logFout(f"Fout bij laden HTML bronbestand: {e}")
            return False
    
    def zoek_invoervelden(self):
        """
        Zoek naar invoervelden in het geladen HTML bestand
        
        Returns:
            list: Lijst met gevonden invoervelden
        """
        if not self.soup:
            logger.logWaarschuwing("Kan niet zoeken naar invoervelden: Geen bestand geladen")
            return []
        
        self.invoervelden = []
        
        # Zoek naar alle <input> elementen
        inputs = self.soup.find_all('input')
        for inp in inputs:
            veld_type = inp.get('type', 'text')
            veld_naam = inp.get('name', '')
            veld_id = inp.get('id', '')
            veld_waarde = inp.get('value', '')
            placeholder = inp.get('placeholder', '')
            
            # Sla alleen relevante invoervelden op
            if veld_type not in ['hidden', 'submit', 'button', 'image', 'reset']:
                self.invoervelden.append({
                    'type': veld_type,
                    'naam': veld_naam,
                    'id': veld_id,
                    'waarde': veld_waarde,
                    'placeholder': placeholder,
                    'element': 'input'
                })
        
        # Zoek naar <select> elementen (dropdown menu's)
        selects = self.soup.find_all('select')
        for select in selects:
            opties = []
            for option in select.find_all('option'):
                opties.append({
                    'waarde': option.get('value', ''),
                    'tekst': option.text.strip()
                })
            
            self.invoervelden.append({
                'type': 'select',
                'naam': select.get('name', ''),
                'id': select.get('id', ''),
                'opties': opties,
                'element': 'select'
            })
        
        # Zoek naar <textarea> elementen
        textareas = self.soup.find_all('textarea')
        for textarea in textareas:
            self.invoervelden.append({
                'type': 'textarea',
                'naam': textarea.get('name', ''),
                'id': textarea.get('id', ''),
                'waarde': textarea.text.strip(),
                'placeholder': textarea.get('placeholder', ''),
                'element': 'textarea'
            })
        
        # Zoek naar checkboxes en radiobuttons (behandeld als groepen)
        checkbox_groepen = {}
        radio_groepen = {}
        
        for inp in inputs:
            veld_type = inp.get('type', 'text')
            veld_naam = inp.get('name', '')
            
            if veld_type == 'checkbox' and veld_naam:
                if veld_naam not in checkbox_groepen:
                    checkbox_groepen[veld_naam] = []
                checkbox_groepen[veld_naam].append({
                    'id': inp.get('id', ''),
                    'waarde': inp.get('value', ''),
                    'label': self.vind_label_voor_input(inp)
                })
            
            elif veld_type == 'radio' and veld_naam:
                if veld_naam not in radio_groepen:
                    radio_groepen[veld_naam] = []
                radio_groepen[veld_naam].append({
                    'id': inp.get('id', ''),
                    'waarde': inp.get('value', ''),
                    'label': self.vind_label_voor_input(inp)
                })
        
        # Voeg checkbox groepen toe aan invoervelden
        for naam, opties in checkbox_groepen.items():
            self.invoervelden.append({
                'type': 'checkbox_groep',
                'naam': naam,
                'opties': opties,
                'element': 'input_groep'
            })
        
        # Voeg radio groepen toe aan invoervelden
        for naam, opties in radio_groepen.items():
            self.invoervelden.append({
                'type': 'radio_groep',
                'naam': naam,
                'opties': opties,
                'element': 'input_groep'
            })
        
        logger.logInfo(f"{len(self.invoervelden)} invoervelden gevonden in HTML bronbestand")
        return self.invoervelden
    
    def vind_label_voor_input(self, input_element):
        """
        Zoek het label dat bij een input element hoort
        
        Args:
            input_element: Het input element waarvoor een label wordt gezocht
            
        Returns:
            str: De tekst van het label of een lege string als er geen label is gevonden
        """
        # Probeer eerst het label te vinden via de 'id' van het input element
        input_id = input_element.get('id')
        if input_id:
            label = self.soup.find('label', attrs={'for': input_id})
            if label:
                return label.text.strip()
        
        # Als dat niet lukt, kijk of het input element zelf in een label element zit
        parent = input_element.parent
        while parent and parent.name != 'form' and parent.name != 'body':
            if parent.name == 'label':
                # Verwijder de tekst van eventuele sub-elementen
                label_tekst = parent.text.strip()
                for sub in parent.find_all():
                    if sub.text.strip():
                        label_tekst = label_tekst.replace(sub.text.strip(), '')
                return label_tekst.strip()
            parent = parent.parent
        
        return ""
    
    def genereer_excel_kolommen(self):
        """
        Genereer kolomnamen voor een Excel bestand op basis van de gevonden invoervelden
        
        Returns:
            list: Lijst met kolomnamen
        """
        kolommen = ['Veld_Type', 'Veld_Naam', 'Veld_ID', 'Veld_Waarde', 'Veld_Placeholder', 'Element_Type']
        
        # Voeg extra kolommen toe voor specifieke veldtypes
        # (bijv. voor dropdowns, checkboxes, radio buttons)
        has_options = any(veld.get('opties') for veld in self.invoervelden if veld.get('type') in ['select', 'checkbox_groep', 'radio_groep'])
        if has_options:
            kolommen.append('Opties')
        
        return kolommen
    
    def genereer_excel_data(self):
        """
        Genereer gegevens voor een Excel bestand op basis van de gevonden invoervelden
        
        Returns:
            list: Lijst met rijen (elke rij is een dict met kolomnaam: waarde)
        """
        if not self.invoervelden:
            return []
        
        excel_data = []
        
        for veld in self.invoervelden:
            rij = {
                'Veld_Type': veld.get('type', ''),
                'Veld_Naam': veld.get('naam', ''),
                'Veld_ID': veld.get('id', ''),
                'Veld_Waarde': veld.get('waarde', ''),
                'Veld_Placeholder': veld.get('placeholder', ''),
                'Element_Type': veld.get('element', '')
            }
            
            # Voeg opties toe als string voor select, checkbox_groep, radio_groep
            if veld.get('type') in ['select', 'checkbox_groep', 'radio_groep'] and 'opties' in veld:
                if veld.get('type') == 'select':
                    opties_str = '; '.join([f"{opt.get('tekst', '')}={opt.get('waarde', '')}" for opt in veld['opties']])
                else:  # checkbox_groep of radio_groep
                    opties_str = '; '.join([f"{opt.get('label', '')}={opt.get('waarde', '')}" for opt in veld['opties']])
                rij['Opties'] = opties_str
            
            excel_data.append(rij)
        
        return excel_data

# Singleton instance voor gebruik in de hele applicatie
html_parser = HtmlParser()
'''
        
        # Schrijf naar bestand
        with open(module_pad, 'w', encoding='utf-8') as f:
            f.write(html_parser_code)
        
        print(f"HTML Parser module succesvol aangemaakt: {module_pad}")
        return True
    
    except Exception as e:
        print(f"Fout bij aanmaken HTML Parser module: {e}")
        print(traceback.format_exc())
        return False

def pas_gui_module_aan():
    """
    Pas de gui.py module aan om het ProductSheet tabblad te updaten
    
    Returns:
        bool: True als de module succesvol is aangepast, anders False
    """
    try:
        # Pad naar gui.py
        gui_pad = os.path.join('modules', 'gui.py')
        
        # Controleer of het bestand bestaat
        if not os.path.exists(gui_pad):
            print(f"FOUT: Bestand {gui_pad} niet gevonden!")
            return False
        
        # Maak backup van het bestand
        backup_pad = f"{gui_pad}.backup.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(gui_pad, backup_pad)
        print(f"Backup gemaakt van gui.py: {backup_pad}")
        
        # Lees de inhoud van het bestand
        with open(gui_pad, 'r', encoding='utf-8') as f:
            inhoud = f.read()
        
        # Vervang de _maakProductSheetTab methode
        oud_patroon = re.compile(r'def _maakProductSheetTab\(self\):.*?def', re.DOTALL)
        match = oud_patroon.search(inhoud)
        
        if not match:
            print("FOUT: Kon de _maakProductSheetTab methode niet vinden in gui.py")
            return False
        
        # De nieuwe methode
        nieuwe_methode = '''def _maakProductSheetTab(self):
    """Maak de inhoud van het ProductSheet aanmaken tabblad"""
    # Hoofdcontainer met padding
    container = tk.Frame(
        self.tabProductSheet,
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
        self.toonFoutmelding("Fout", "Geen HTML bronbestand geselecteerd")
        return
    
    self.updateStatus(f"Bezig met analyseren van {os.path.basename(bestandspad)}...")
    
    # Laad het HTML bestand
    if html_parser.laad_bestand(bestandspad):
        # Controleer of er invoervelden zijn gevonden
        if html_parser.invoervelden:
            self.updateStatus("HTML bronbestand succesvol geanalyseerd")
            self.resultaatLabel.config(
                text=f"Gevonden in {os.path.basename(bestandspad)}: {len(html_parser.invoervelden)} invoervelden"
            )
            
            # Toon de gevonden invoervelden
            self._toonInvoervelden(html_parser.invoervelden)
            
            # Vraag waar het Excel bestand moet worden opgeslagen
            self._maakExcelBestand(html_parser)
        else:
            self.updateStatus("Geen invoervelden gevonden")
            self.resultaatLabel.config(text=f"Geen invoervelden gevonden in {os.path.basename(bestandspad)}")
            self._verbergInvoervelden()
    else:
        self.updateStatus("Fout bij analyseren bestand")
        self.toonFoutmelding("Fout", f"Kon bestand '{bestandspad}' niet analyseren")
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
    
    self.updateStatus("Bezig met maken Excel bestand...")
    
    try:
        # Maak een DataFrame
        kolommen = parser.genereer_excel_kolommen()
        data = parser.genereer_excel_data()
        
        if not data:
            self.toonFoutmelding("Fout", "Geen gegevens om op te slaan")
            self.updateStatus("Fout: Geen gegevens om op te slaan")
            return
        
        # Converteer naar DataFrame
        df = pd.DataFrame(data)
        
        # Sla op als Excel
        df.to_excel(bestandspad, index=False)
        
        self.updateStatus("Excel bestand succesvol gemaakt")
        self.toonSuccesmelding(
            "Succes", 
            f"ProductSheet is opgeslagen als '{os.path.basename(bestandspad)}'"
        )
    except Exception as e:
        self.updateStatus("Fout bij maken Excel bestand")
        self.toonFoutmelding("Fout", f"Kon Excel bestand niet maken: {e}")

def '''
        
        # Voeg de nieuwe methode toe
        nieuwe_inhoud = oud_patroon.sub(nieuwe_methode, inhoud)
        
        # Controleer of we daadwerkelijk een wijziging hebben aangebracht
        if nieuwe_inhoud == inhoud:
            print("WAARSCHUWING: Geen wijzigingen aangebracht in gui.py")
            return False
        
        # Schrijf de nieuwe inhoud terug naar het bestand
        with open(gui_pad, 'w', encoding='utf-8') as f:
            f.write(nieuwe_inhoud)
        
        print(f"GUI module (gui.py) succesvol aangepast")
        return True
        
    except Exception as e:
        print(f"Fout bij aanpassen GUI module: {e}")
        print(traceback.format_exc())
        return False

def installeer_beautifulsoup():
    """
    Installeer BeautifulSoup4 als het nog niet is geïnstalleerd
    
    Returns:
        bool: True als BeautifulSoup4 is geïnstalleerd of al aanwezig was, anders False
    """
    try:
        # Controleer of BeautifulSoup4 al is geïnstalleerd
        try:
            import bs4
            print("BeautifulSoup4 is al geïnstalleerd")
            return True
        except ImportError:
            pass
        
        # Probeer BeautifulSoup4 te installeren met pip
        import subprocess
        print("BeautifulSoup4 wordt geïnstalleerd...")
        
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "beautifulsoup4"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Fout bij installeren BeautifulSoup4: {result.stderr}")
            return False
        
        print("BeautifulSoup4 succesvol geïnstalleerd")
        return True
    
    except Exception as e:
        print(f"Fout bij installeren BeautifulSoup4: {e}")
        print(traceback.format_exc())
        return False

def schrijf_log(log_entries):
    """
    Schrijft de log naar de console en naar een bestand
    
    Args:
        log_entries (list): Lijst met log-regels
    """
    # Zorg dat logs directory bestaat
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Zorg dat patch_historie subdirectory bestaat
    patch_historie_dir = os.path.join('logs', 'patch_historie')
    if not os.path.exists(patch_historie_dir):
        os.makedirs(patch_historie_dir)
    
    # Maak logbestandsnaam
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_bestand = os.path.join(patch_historie_dir, f"patch_geschiedenis{timestamp}.txt")
    
    # Schrijf log naar bestand
    with open(log_bestand, 'w', encoding='utf-8') as bestand:
        for regel in log_entries:
            bestand.write(regel + "\n")
    
    # Toon log op console
    for regel in log_entries:
        print(regel)
    
    print("\nLog is ook opgeslagen in:", log_bestand)

if __name__ == "__main__":
    # Zorg ervoor dat we in de root directory van de applicatie zitten
    # Controleer of modules directory bestaat
    if not os.path.exists('modules'):
        # Probeer naar parent directory te gaan als we in een submap zitten
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        
        if os.path.exists(os.path.join(parent_dir, 'modules')):
            os.chdir(parent_dir)
        else:
            # Zoek recursief naar de applicatie root
            for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(os.getcwd()))):
                if 'modules' in dirs and 'main.py' in files:
                    os.chdir(root)
                    print(f"Applicatie root gevonden: {os.getcwd()}")
                    break
    
    # Voer de patch toe
    print("\n=== Excelladin Reloaded HTML Parser Patch ===")
    print("Deze patch voegt functionaliteit toe om HTML bronbestanden te analyseren")
    print("en daaruit een ProductSheet te genereren.\n")
    
    succes = pas_patch_toe()
    
    if succes:
        print("\nPatch is succesvol uitgevoerd!")
        print("Je kunt nu HTML bronbestanden analyseren in het '1 ProductSheet Aanmaken' tabblad.")
    else:
        print("\nPatch is NIET succesvol uitgevoerd. Zie logbestand voor details.")
    
    input("\nDruk op Enter om af te sluiten...")