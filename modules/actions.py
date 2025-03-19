"""
Actions module voor Excelladin Reloaded
Bevat de logica voor het definiëren en uitvoeren van acties op Excel-kolommen
"""
from modules.logger import logger
from modules.excel_handler import excelHandler

# Importeer RentPro acties
from modules.actions.rentpro_inlezen import (
    RentProInlezenActie,
    RentProMeerdereInlezenActie,
    RentProZoekInlezenActie
)
from modules.actions.rentpro_upload import (
    RentProUploadActie,
    RentProBulkUploadActie,
    RentProUpdateActie
)

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

class KolomVullenActie(ActieBasis):
    """Actie om een kolom te vullen met gecombineerde data uit andere kolommen"""
    
    def __init__(self):
        """Initialiseer de kolom vullen actie"""
        super().__init__(
            naam="kolomVullen",
            beschrijving="Vul een kolom met gecombineerde data uit andere kolommen",
            categorie="Lokale sheet bijwerken"
        )
    
    def voerUit(self, parameters, rijen=None):
        """
        Voer de kolom vullen actie uit
        
        Args:
            parameters (dict): Parameters voor de actie, moet bevatten:
                - doelKolom (str): Naam van de kolom om te vullen
                - bronKolommen (list): Lijst met namen van bronkolommen
                - formaat (str): Formaat string met {kolomnaam} placeholders
            rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik te bewerken
            
        Returns:
            ActieResultaat: Resultaat van de actie
        """
        try:
            # Controleer verplichte parameters
            verplicht = ["doelKolom", "bronKolommen", "formaat"]
            for param in verplicht:
                if param not in parameters:
                    return ActieResultaat(
                        False, 
                        f"Ontbrekende parameter: {param}"
                    )
            
            doelKolom = parameters["doelKolom"]
            bronKolommen = parameters["bronKolommen"]
            formaat = parameters["formaat"]
            
            # Controleer of er een bestand is geopend
            if not excelHandler.isBestandGeopend():
                return ActieResultaat(
                    False, 
                    "Kan actie niet uitvoeren: Geen Excel-bestand geopend"
                )
            
            # Controleer of alle bronkolommen bestaan
            for kolom in bronKolommen:
                if kolom not in excelHandler.kolomNamen:
                    return ActieResultaat(
                        False, 
                        f"Bronkolom '{kolom}' bestaat niet in het bestand"
                    )
            
            # Bepaal het aantal rijen
            if rijen:
                startRij, eindRij = rijen
                aantalRijen = eindRij - startRij + 1
            else:
                aantalRijen = excelHandler.haalRijAantal()
                startRij, eindRij = 0, aantalRijen - 1
            
            # Haal gegevens op uit bronkolommen
            kolomData = {}
            for kolom in bronKolommen:
                kolomData[kolom] = excelHandler.haalKolomOp(kolom, rijen)
                if kolomData[kolom] is None:
                    return ActieResultaat(
                        False, 
                        f"Fout bij ophalen gegevens uit kolom '{kolom}'"
                    )
            
            # Genereer nieuwe waarden voor doelkolom
            nieuweWaarden = []
            for i in range(aantalRijen):
                rijData = {kolom: str(kolomData[kolom][i]) for kolom in bronKolommen}
                try:
                    nieuweWaarde = formaat.format(**rijData)
                    nieuweWaarden.append(nieuweWaarde)
                except KeyError as e:
                    logger.logWaarschuwing(f"Ontbrekende kolom in formaat: {e}")
                    nieuweWaarden.append("")
                except Exception as e:
                    logger.logWaarschuwing(f"Fout bij formatteren rij {i+startRij}: {e}")
                    nieuweWaarden.append("")
            
            # Update de doelkolom
            if excelHandler.bewerkKolom(doelKolom, nieuweWaarden, rijen):
                logger.logActie(f"Kolom '{doelKolom}' gevuld met data uit {', '.join(bronKolommen)}")
                rijBereik = f"rijen {startRij+1}-{eindRij+1}" if rijen is not None else "alle rijen"
                return ActieResultaat(
                    True, 
                    f"Kolom '{doelKolom}' succesvol gevuld voor {rijBereik}"
                )
            else:
                return ActieResultaat(
                    False, 
                    f"Fout bij schrijven naar kolom '{doelKolom}'"
                )
        except Exception as e:
            logger.logFout(f"Fout bij uitvoeren KolomVullenActie: {e}")
            return ActieResultaat(False, f"Fout bij uitvoeren actie: {e}")

class KolomSchoonmakenActie(ActieBasis):
    """Actie om een kolom op te schonen (onnodige tekens verwijderen)"""
    
    def __init__(self):
        """Initialiseer de kolom schoonmaken actie"""
        super().__init__(
            naam="kolomSchoonmaken",
            beschrijving="Schoon een kolom op door onnodige tekens te verwijderen",
            categorie="Lokale sheet bijwerken"
        )
    
    def voerUit(self, parameters, rijen=None):
        """
        Voer de kolom schoonmaken actie uit
        
        Args:
            parameters (dict): Parameters voor de actie, moet bevatten:
                - kolom (str): Naam van de kolom om schoon te maken
                - verwijderSpaties (bool): Verwijder extra spaties
                - verwijderLeestekens (bool): Verwijder leestekens
            rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik te bewerken
            
        Returns:
            ActieResultaat: Resultaat van de actie
        """
        try:
            # Controleer verplichte parameters
            if "kolom" not in parameters:
                return ActieResultaat(False, "Ontbrekende parameter: kolom")
            
            kolom = parameters["kolom"]
            verwijderSpaties = parameters.get("verwijderSpaties", False)
            verwijderLeestekens = parameters.get("verwijderLeestekens", False)
            
            # Controleer of er een bestand is geopend
            if not excelHandler.isBestandGeopend():
                return ActieResultaat(
                    False, 
                    "Kan actie niet uitvoeren: Geen Excel-bestand geopend"
                )
            
            # Controleer of de kolom bestaat
            if kolom not in excelHandler.kolomNamen:
                return ActieResultaat(
                    False, 
                    f"Kolom '{kolom}' bestaat niet in het bestand"
                )
            
            # Haal de kolomgegevens op
            kolomData = excelHandler.haalKolomOp(kolom, rijen)
            if kolomData is None:
                return ActieResultaat(
                    False, 
                    f"Fout bij ophalen gegevens uit kolom '{kolom}'"
                )
            
            # Maak de data schoon
            schoneData = []
            import re
            
            for waarde in kolomData:
                # Converteer naar string
                waarde = str(waarde)
                
                # Verwijder leestekens indien nodig
                if verwijderLeestekens:
                    waarde = re.sub(r'[^\w\s]', '', waarde)
                
                # Verwijder extra spaties indien nodig
                if verwijderSpaties:
                    waarde = re.sub(r'\s+', ' ', waarde).strip()
                
                schoneData.append(waarde)
            
            # Update de kolom
            if excelHandler.bewerkKolom(kolom, schoneData, rijen):
                rijBereik = f"rijen {rijen[0]+1}-{rijen[1]+1}" if rijen is not None else "alle rijen"
                return ActieResultaat(
                    True, 
                    f"Kolom '{kolom}' succesvol schoongemaakt voor {rijBereik}"
                )
            else:
                return ActieResultaat(
                    False, 
                    f"Fout bij schrijven naar kolom '{kolom}'"
                )
        except Exception as e:
            logger.logFout(f"Fout bij uitvoeren KolomSchoonmakenActie: {e}")
            return ActieResultaat(False, f"Fout bij uitvoeren actie: {e}")

# Lijst met beschikbare acties
BESCHIKBARE_ACTIES = {
    # Lokale sheet acties
    "kolomVullen": KolomVullenActie(),
    "kolomSchoonmaken": KolomSchoonmakenActie(),
    
    # RentPro inlezen acties
    "rentProInlezen": RentProInlezenActie(),
    "rentProMeerdereInlezen": RentProMeerdereInlezenActie(),
    "rentProZoekInlezen": RentProZoekInlezenActie(),
    
    # RentPro upload acties
    "rentProUpload": RentProUploadActie(),
    "rentProBulkUpload": RentProBulkUploadActie(),
    "rentProUpdate": RentProUpdateActie(),
}

def haalActieOp(actieNaam):
    """
    Haal een actie op basis van naam
    
    Args:
        actieNaam (str): Naam van de actie
        
    Returns:
        ActieBasis: De actie of None als de actie niet bestaat
    """
    return BESCHIKBARE_ACTIES.get(actieNaam)

def voerActieUit(actieNaam, parameters, rijen=None):
    """
    Voer een actie uit
    
    Args:
        actieNaam (str): Naam van de actie
        parameters (dict): Parameters voor de actie
        rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik te bewerken
        
    Returns:
        ActieResultaat: Resultaat van de actie
    """
    actie = haalActieOp(actieNaam)
    
    if actie is None:
        logger.logFout(f"Actie '{actieNaam}' bestaat niet")
        return ActieResultaat(False, f"Actie '{actieNaam}' bestaat niet")
    
    logger.logInfo(f"Voer actie uit: {actieNaam}")
    return actie.voerUit(parameters, rijen)
