"""
Rentpro Handler module voor Excelladin Reloaded
Deze module importeert de nieuwe handler met API-mode uit modules/rentpro/handler.py

Dit bestand bestaat voor backwards compatibiliteit en zorgt dat alle bestaande imports
blijven werken terwijl de nieuwe API-mode wordt gebruikt.
"""
from modules.rentpro.handler import rentproHandler

# Singleton instance is nu geïmporteerd van de nieuwe implementatie
# en wordt automatisch gebruikt door bestaande code
