"""
GUI module voor Excelladin Reloaded
Verantwoordelijk voor alle visuele elementen en interacties

Deze module is nu opgesplitst in kleinere componenten volgens het MVC-patroon:
- modules/gui/app.py: Hoofdapplicatie klasse
- modules/gui/components.py: Herbruikbare UI-componenten
- modules/gui/product_sheet_tab.py: ProductSheet tabblad
- modules/gui/sheet_kiezen_tab.py: Sheet Kiezen tabblad
- modules/gui/acties_tab.py: Acties tabblad
"""

# Importeer en exporteer de ExcelladinApp klasse
from modules.gui.app import ExcelladinApp

# Exporteer alleen de hoofdklasse
__all__ = ['ExcelladinApp']
