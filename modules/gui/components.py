"""
Herbruikbare UI-componenten voor Excelladin Reloaded
"""
import tkinter as tk
import pyperclip
from assets.theme import TOOLTIP_STIJL, KLEUREN, FONTS, STIJLEN

class Tooltip:
    """
    Tooltip klasse voor het tonen van tooltips bij hover
    """
    def __init__(self, widget, tekst):
        """
        Initialiseer een tooltip
        
        Args:
            widget: Het widget waaraan de tooltip wordt gekoppeld
            tekst (str): De tekst die in de tooltip wordt getoond
        """
        self.widget = widget
        self.tekst = tekst
        self.tooltipWindow = None
        self.widget.bind("<Enter>", self.toon)
        self.widget.bind("<Leave>", self.verberg)
    
    def toon(self, event=None):
        """Toon de tooltip"""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Maak tooltipvenster
        self.tooltipWindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            tw, text=self.tekst, justify='left',
            **TOOLTIP_STIJL
        )
        label.pack()
    
    def verberg(self, event=None):
        """Verberg de tooltip"""
        if self.tooltipWindow:
            self.tooltipWindow.destroy()
            self.tooltipWindow = None


class StijlvollePopup:
    """
    Stijlvolle popup klasse voor het tonen van meldingen in Excelladin stijl
    Vervangt de standaard messagebox popups met aangepaste Toplevel widgets
    """
    def __init__(self, parent, titel, bericht, popup_type="info", actie_knoppen=None, kopieer_knop=False):
        """
        Initialiseer een stijlvolle popup
        
        Args:
            parent: Het parent widget waaraan de popup wordt gekoppeld
            titel (str): De titel van de popup
            bericht (str): De tekst die in de popup wordt getoond
            popup_type (str): Type popup ('info', 'waarschuwing', 'fout', 'vraag')
            actie_knoppen (list): Lijst met dictionaries voor actieknoppen, elk met 'tekst' en 'commando'
                                  Bijvoorbeeld: [{'tekst': 'Ja', 'commando': self.ja_actie}, {'tekst': 'Nee', 'commando': self.nee_actie}]
            kopieer_knop (bool): Of er een kopieerknop moet worden toegevoegd (standaard False)
        """
        self.parent = parent
        self.titel = titel
        self.bericht = bericht
        self.popup_type = popup_type
        self.actie_knoppen = actie_knoppen or []
        self.kopieer_knop = kopieer_knop
        self.resultaat = None
        
        # Maak de popup
        self._maak_popup()
    
    def _maak_popup(self):
        """Maak de popup met Excelladin stijl"""
        # Bepaal kleuren op basis van type
        if self.popup_type == "fout":
            achtergrond_kleur = KLEUREN["fout"]
            icoon_tekst = "❌"
        elif self.popup_type == "waarschuwing":
            achtergrond_kleur = "#b87333"  # Brons/koper kleur voor waarschuwingen
            icoon_tekst = "⚠️"
        elif self.popup_type == "vraag":
            achtergrond_kleur = "#0a0d2c"  # Donker marineblauw
            icoon_tekst = "❓"
        else:  # info/succes
            achtergrond_kleur = KLEUREN["succes"]
            icoon_tekst = "✓"
        
        # Maak toplevel widget
        self.popup = tk.Toplevel(self.parent)
        self.popup.title(self.titel)
        self.popup.configure(background=achtergrond_kleur)
        self.popup.resizable(False, False)
        
        # Zorg dat de popup modaal is (blokkeert interactie met hoofdvenster)
        self.popup.transient(self.parent)
        self.popup.grab_set()
        
        # Bepaal grootte op basis van berichtlengte
        breedte = min(max(len(self.bericht) * 7, 300), 500)  # Min 300, max 500 pixels
        hoogte = 150 + (self.bericht.count('\n') * 20)  # Basisgrootte + extra voor regels
        
        # Voeg padding toe
        hoofdframe = tk.Frame(
            self.popup,
            background=achtergrond_kleur,
            padx=15,
            pady=15
        )
        hoofdframe.pack(fill=tk.BOTH, expand=True)
        
        # Bovenste frame voor icoon en titel
        bovenframe = tk.Frame(
            hoofdframe,
            background=achtergrond_kleur
        )
        bovenframe.pack(fill=tk.X, pady=(0, 10))
        
        # Icoon (als tekst)
        icoon_label = tk.Label(
            bovenframe,
            text=icoon_tekst,
            font=("Arial", 24),
            background=achtergrond_kleur,
            foreground=KLEUREN["tekst"]
        )
        icoon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Titel
        titel_label = tk.Label(
            bovenframe,
            text=self.titel,
            font=FONTS["subtitel"],
            background=achtergrond_kleur,
            foreground=KLEUREN["tekst"],
            anchor=tk.W
        )
        titel_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bericht
        bericht_frame = tk.Frame(
            hoofdframe,
            background=achtergrond_kleur,
            padx=5,
            pady=5
        )
        bericht_frame.pack(fill=tk.BOTH, expand=True)
        
        # Als het een foutmelding is en kopieerknop is ingeschakeld, gebruik Text widget voor selectie
        if self.popup_type == "fout" and self.kopieer_knop:
            self.bericht_text = tk.Text(
                bericht_frame,
                wrap=tk.WORD,
                width=breedte // 8,  # Breedte in karakters
                height=min(10, 3 + self.bericht.count('\n')),  # Hoogte in regels
                background=achtergrond_kleur,
                foreground=KLEUREN["tekst"],
                font=FONTS["normaal"],
                relief=tk.FLAT,
                borderwidth=0,
                highlightthickness=0
            )
            self.bericht_text.insert(tk.END, self.bericht)
            self.bericht_text.config(state=tk.DISABLED)  # Maak read-only
            self.bericht_text.pack(fill=tk.BOTH, expand=True)
            
            # Selecteer alle tekst voor gemakkelijk kopiëren met Ctrl+C
            self.bericht_text.tag_add(tk.SEL, "1.0", tk.END)
            self.bericht_text.mark_set(tk.INSERT, "1.0")
            self.bericht_text.see(tk.INSERT)
            
            # Bind Ctrl+C aan kopiëren
            self.bericht_text.bind("<Control-c>", lambda e: self._kopieer_naar_klembord())
        else:
            # Gebruik standaard Label voor andere meldingen
            bericht_label = tk.Label(
                bericht_frame,
                text=self.bericht,
                wraplength=breedte - 50,  # Rekening houden met padding
                justify=tk.LEFT,
                background=achtergrond_kleur,
                foreground=KLEUREN["tekst"],
                font=FONTS["normaal"]
            )
            bericht_label.pack(fill=tk.BOTH, expand=True)
        
        # Knoppen frame
        knoppen_frame = tk.Frame(
            hoofdframe,
            background=achtergrond_kleur,
            pady=10
        )
        knoppen_frame.pack(fill=tk.X)
        
        # Kopieerknop indien nodig
        if self.kopieer_knop:
            kopieer_knop = tk.Button(
                knoppen_frame,
                text="Kopieer Foutmelding",
                command=lambda: self._kopieer_naar_klembord(),
                bg="#000080",  # Donkerblauw
                fg="#FFFF00",  # Fel geel
                font=("Arial", 10),
                padx=10,
                pady=5
            )
            kopieer_knop.pack(side=tk.LEFT, padx=5)
            
            # Tooltip voor kopieerknop
            Tooltip(kopieer_knop, "Kopieer de volledige foutmelding naar het klembord")
        
        # Voeg actieknoppen toe
        if self.actie_knoppen:
            # Meerdere knoppen
            for knop_info in self.actie_knoppen:
                knop = tk.Button(
                    knoppen_frame,
                    text=knop_info['tekst'],
                    command=knop_info['commando'],
                    bg="#000080" if knop_info.get('primair', False) else "#555555",  # Donkerblauw voor primair, grijs voor secundair
                    fg="#FFFF00",  # Fel geel
                    font=("Arial", 10, "bold") if knop_info.get('primair', False) else ("Arial", 10),
                    padx=10,
                    pady=5
                )
                knop.pack(side=tk.RIGHT, padx=5)
        else:
            # Standaard OK knop
            ok_knop = tk.Button(
                knoppen_frame,
                text="OK",
                command=self._sluit_popup,
                bg="#000080",  # Donkerblauw
                fg="#FFFF00",  # Fel geel
                font=("Arial", 10, "bold"),
                padx=20,
                pady=5
            )
            ok_knop.pack(side=tk.RIGHT, padx=5)
            
            # Focus op OK knop
            ok_knop.focus_set()
            
            # Bind Enter toets aan OK knop
            self.popup.bind("<Return>", lambda event: self._sluit_popup())
        
        # Centreer de popup op het scherm
        self.popup.update_idletasks()
        popup_breedte = self.popup.winfo_width()
        popup_hoogte = self.popup.winfo_height()
        x = (self.popup.winfo_screenwidth() // 2) - (popup_breedte // 2)
        y = (self.popup.winfo_screenheight() // 2) - (popup_hoogte // 2)
        self.popup.geometry(f"{popup_breedte}x{popup_hoogte}+{x}+{y}")
    
    def _kopieer_naar_klembord(self):
        """Kopieer de foutmelding naar het klembord en toon feedback"""
        try:
            # Kopieer naar klembord
            if hasattr(self, 'bericht_text') and self.popup_type == "fout":
                # Als we een Text widget gebruiken, haal de tekst daaruit
                tekst = self.bericht_text.get("1.0", tk.END).strip()
                pyperclip.copy(tekst)
            else:
                # Anders gebruik het originele bericht
                pyperclip.copy(self.bericht)
            
            # Toon korte feedback
            feedback = tk.Label(
                self.popup,
                text="Gekopieerd!",
                background="#4CAF50",  # Groen
                foreground="white",
                font=("Arial", 10),
                padx=10,
                pady=5
            )
            feedback.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
            
            # Verwijder feedback na 1.5 seconden
            self.popup.after(1500, feedback.destroy)
            
        except Exception as e:
            # Toon foutmelding als kopiëren mislukt
            fout_label = tk.Label(
                self.popup,
                text=f"Kopiëren mislukt: {e}",
                background="#F44336",  # Rood
                foreground="white",
                font=("Arial", 10),
                padx=10,
                pady=5
            )
            fout_label.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
            
            # Verwijder foutmelding na 2 seconden
            self.popup.after(2000, fout_label.destroy)
    
    def _sluit_popup(self):
        """Sluit de popup"""
        self.popup.destroy()
    
    def wacht_op_antwoord(self):
        """
        Wacht tot de gebruiker een keuze heeft gemaakt (voor vraag popups)
        
        Returns:
            bool: True als de gebruiker 'Ja' kiest, False als de gebruiker 'Nee' kiest
        """
        # Wacht tot de popup wordt gesloten
        self.parent.wait_window(self.popup)
        return self.resultaat
    
    def ja_actie(self):
        """Actie voor 'Ja' knop"""
        self.resultaat = True
        self._sluit_popup()
    
    def nee_actie(self):
        """Actie voor 'Nee' knop"""
        self.resultaat = False
        self._sluit_popup()
