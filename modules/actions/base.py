"""
Basis klassen voor acties in Excelladin Reloaded
"""
from modules.logger import logger

class ActieResultaat:
    """Resultaat van een actie"""
    def __init__(self, succes, bericht):
        self.succes = succes
        self.bericht = bericht

class ActieBasis:
    """Basis klasse voor alle acties"""
    
    def __init__(self, naam, beschrijving, categorie="Algemeen"):
        """
        Initialiseer een actie
        
        Args:
            naam (str): Naam van de actie
            beschrijving (str): Beschrijving van de actie
            categorie (str): Categorie van de actie (nieuw)
        """
        self.naam = naam
        self.beschrijving = beschrijving
        self.categorie = categorie
    
    def voerUit(self, parameters, rijen=None):
        """
        Voer de actie uit (implementeer in subklassen)
        
        Args:
            parameters (dict): Parameters voor de actie
            rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik te bewerken
            
        Returns:
            ActieResultaat: Resultaat van de actie
        """
        raise NotImplementedError("Deze methode moet worden geïmplementeerd in subklassen")
