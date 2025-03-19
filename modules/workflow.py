"""
Workflow module voor Excelladin Reloaded
Beheert het combineren en in volgorde uitvoeren van meerdere acties
"""
from modules.logger import logger
from modules.actions import voerActieUit, ActieResultaat

class Workflow:
    """Workflow klasse voor het uitvoeren van meerdere acties in volgorde"""
    
    def __init__(self, naam):
        """
        Initialiseer een workflow
        
        Args:
            naam (str): Naam van de workflow
        """
        self.naam = naam
        self.acties = []  # lijst met (actieNaam, parameters) tuples
        self.voortgang = 0
        self.resultaten = []
    
    def voegActieToe(self, actieNaam, parameters):
        """
        Voeg een actie toe aan de workflow
        
        Args:
            actieNaam (str): Naam van de actie
            parameters (dict): Parameters voor de actie
        """
        self.acties.append((actieNaam, parameters))
        logger.logInfo(f"Actie '{actieNaam}' toegevoegd aan workflow '{self.naam}'")
    
    def verwijderActie(self, index):
        """
        Verwijder een actie uit de workflow
        
        Args:
            index (int): Index van de actie om te verwijderen
            
        Returns:
            bool: True als de actie is verwijderd, anders False
        """
        if 0 <= index < len(self.acties):
            verwijderd = self.acties.pop(index)
            logger.logInfo(f"Actie '{verwijderd[0]}' verwijderd uit workflow '{self.naam}'")
            return True
        else:
            logger.logWaarschuwing(f"Kan actie {index} niet verwijderen uit workflow '{self.naam}': Ongeldige index")
            return False
    
    def haalVoortgang(self):
        """
        Haal de huidige voortgang op
        
        Returns:
            float: Voortgang percentage (0-100)
        """
        if not self.acties:
            return 100.0
        
        return (self.voortgang / len(self.acties)) * 100
    
    def haalResultaten(self):
        """
        Haal de resultaten van uitgevoerde acties op
        
        Returns:
            list: Lijst met ActieResultaat objecten
        """
        return self.resultaten
    
    def voerUit(self, voortgangCallback=None, rijen=None):
        """
        Voer alle acties in de workflow uit
        
        Args:
            voortgangCallback (callable): Callback functie om voortgang te rapporteren,
                                           ontvangt percentage en huidige actienaam
            rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik te bewerken
            
        Returns:
            bool: True als alle acties succesvol zijn uitgevoerd, anders False
        """
        if not self.acties:
            logger.logWaarschuwing(f"Workflow '{self.naam}' bevat geen acties")
            return True
        
        logger.logInfo(f"Start uitvoering workflow '{self.naam}'")
        self.voortgang = 0
        self.resultaten = []
        
        for i, (actieNaam, parameters) in enumerate(self.acties):
            logger.logInfo(f"Uitvoeren actie {i+1}/{len(self.acties)}: {actieNaam}")
            
            # Voer de actie uit
            resultaat = voerActieUit(actieNaam, parameters, rijen)
            self.resultaten.append(resultaat)
            
            # Update voortgang
            self.voortgang = i + 1
            if voortgangCallback:
                percentage = self.haalVoortgang()
                voortgangCallback(percentage, actieNaam)
            
            # Stop bij fout als niet alle acties uitgevoerd moeten worden
            if not resultaat.succes:
                logger.logFout(f"Fout bij uitvoeren actie '{actieNaam}': {resultaat.bericht}")
                return False
        
        logger.logInfo(f"Workflow '{self.naam}' succesvol uitgevoerd")
        return True

class WorkflowManager:
    """Manager voor het beheren van workflows"""
    
    def __init__(self):
        """Initialiseer de WorkflowManager"""
        self.workflows = {}
    
    def maakWorkflow(self, naam):
        """
        Maak een nieuwe workflow
        
        Args:
            naam (str): Naam van de workflow
            
        Returns:
            Workflow: De nieuwe workflow
        """
        if naam in self.workflows:
            logger.logWaarschuwing(f"Workflow '{naam}' bestaat al, wordt opnieuw aangemaakt")
        
        workflow = Workflow(naam)
        self.workflows[naam] = workflow
        logger.logInfo(f"Nieuwe workflow aangemaakt: '{naam}'")
        
        return workflow
    
    def verwijderWorkflow(self, naam):
        """
        Verwijder een workflow
        
        Args:
            naam (str): Naam van de workflow
            
        Returns:
            bool: True als de workflow is verwijderd, anders False
        """
        if naam in self.workflows:
            del self.workflows[naam]
            logger.logInfo(f"Workflow verwijderd: '{naam}'")
            return True
        else:
            logger.logWaarschuwing(f"Kan workflow '{naam}' niet verwijderen: Bestaat niet")
            return False
    
    def haalWorkflowOp(self, naam):
        """
        Haal een workflow op basis van naam
        
        Args:
            naam (str): Naam van de workflow
            
        Returns:
            Workflow: De workflow of None als de workflow niet bestaat
        """
        return self.workflows.get(naam)
    
    def haalAlleWorkflowsOp(self):
        """
        Haal alle workflows op
        
        Returns:
            dict: Dictionary met alle workflows (naam: workflow)
        """
        return self.workflows
    
    def voerWorkflowUit(self, naam, voortgangCallback=None, rijen=None):
        """
        Voer een workflow uit op basis van naam
        
        Args:
            naam (str): Naam van de workflow
            voortgangCallback (callable): Callback functie om voortgang te rapporteren
            rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik te bewerken
            
        Returns:
            bool: True als de workflow succesvol is uitgevoerd, anders False
        """
        workflow = self.haalWorkflowOp(naam)
        
        if workflow is None:
            logger.logFout(f"Kan workflow '{naam}' niet uitvoeren: Bestaat niet")
            return False
        
        return workflow.voerUit(voortgangCallback, rijen)

# Singleton instance voor gebruik in de hele applicatie
workflowManager = WorkflowManager()