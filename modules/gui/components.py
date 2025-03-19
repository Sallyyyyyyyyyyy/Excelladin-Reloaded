"""
Herbruikbare UI-componenten voor Excelladin Reloaded
"""
import tkinter as tk
from assets.theme import TOOLTIP_STIJL

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
