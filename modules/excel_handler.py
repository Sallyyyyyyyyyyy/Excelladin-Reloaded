"""
Excel Handler module voor Excelladin Reloaded
Verantwoordelijk voor het inlezen, bewerken en opslaan van Excel-bestanden
"""
import os
import datetime
import pandas as pd
from modules.logger import logger

class ExcelHandler:
    """
    ExcelHandler klasse voor het verwerken van Excel-bestanden
    """
    
    def __init__(self):
        """Initialiseer de ExcelHandler"""
        self.huidigBestand = None
        self.huidigDataFrame = None
        self.kolomNamen = []
    
    def openBestand(self, bestandspad):
        """
        Open een Excel-bestand en laad de gegevens
        
        Args:
            bestandspad (str): Pad naar het Excel-bestand
            
        Returns:
            bool: True als het bestand succesvol is geopend, anders False
        """
        try:
            # Controleer of het bestand bestaat
            if not os.path.exists(bestandspad):
                logger.logFout(f"Bestand niet gevonden: {bestandspad}")
                return False
            
            # Laad het bestand met pandas
            self.huidigDataFrame = pd.read_excel(bestandspad)
            self.huidigBestand = bestandspad
            self.kolomNamen = list(self.huidigDataFrame.columns)
            
            logger.logInfo(f"Excel-bestand geopend: {bestandspad}")
            logger.logInfo(f"Kolommen gevonden: {', '.join(self.kolomNamen)}")
            
            return True
        except Exception as e:
            logger.logFout(f"Fout bij openen Excel-bestand: {e}")
            return False
    
    def bewerkKolom(self, kolomNaam, nieuweWaarden, rijen=None):
        """
        Bewerk waarden in een specifieke kolom
        
        Args:
            kolomNaam (str): Naam van de kolom die bewerkt moet worden
            nieuweWaarden (list): Lijst met nieuwe waarden voor de kolom
            rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik te bewerken
            
        Returns:
            bool: True als de bewerking succesvol was, anders False
        """
        if self.huidigDataFrame is None:
            logger.logFout("Kan kolom niet bewerken: Geen bestand geopend")
            return False
        
        try:
            # Controleer of de kolom bestaat
            if kolomNaam not in self.kolomNamen:
                logger.logFout(f"Kolom '{kolomNaam}' bestaat niet")
                return False
            
            # Als de kolom nog niet bestaat, voeg deze toe
            if kolomNaam not in self.huidigDataFrame.columns:
                self.huidigDataFrame[kolomNaam] = ""
                self.kolomNamen.append(kolomNaam)
            
            # Bepaal welke rijen moeten worden bewerkt
            if rijen:
                startRij, eindRij = rijen
                # Controleer bereik
                if startRij < 0:
                    startRij = 0
                if eindRij >= len(self.huidigDataFrame):
                    eindRij = len(self.huidigDataFrame) - 1
                
                # Controleer of we genoeg waarden hebben
                benodigdeWaarden = eindRij - startRij + 1
                if len(nieuweWaarden) < benodigdeWaarden:
                    logger.logWaarschuwing("Niet genoeg waarden om alle rijen te vullen")
                    # Vul aan met lege strings indien nodig
                    nieuweWaarden.extend([""] * (benodigdeWaarden - len(nieuweWaarden)))
                
                # Update alleen de geselecteerde rijen
                for i in range(startRij, eindRij + 1):
                    self.huidigDataFrame.at[i, kolomNaam] = nieuweWaarden[i - startRij]
            else:
                # Update alle rijen
                benodigdeWaarden = len(self.huidigDataFrame)
                if len(nieuweWaarden) < benodigdeWaarden:
                    logger.logWaarschuwing("Niet genoeg waarden om alle rijen te vullen")
                    # Vul aan met lege strings indien nodig
                    nieuweWaarden.extend([""] * (benodigdeWaarden - len(nieuweWaarden)))
                
                # Beperk tot aantal rijen in DataFrame
                nieuweWaarden = nieuweWaarden[:benodigdeWaarden]
                self.huidigDataFrame[kolomNaam] = nieuweWaarden
            
            logger.logActie(f"Kolom '{kolomNaam}' succesvol bewerkt")
            return True
        except Exception as e:
            logger.logFout(f"Fout bij bewerken kolom '{kolomNaam}': {e}")
            return False
    
    def haalKolomOp(self, kolomNaam, rijen=None):
        """
        Haal waarden op uit een specifieke kolom
        
        Args:
            kolomNaam (str): Naam van de kolom
            rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik op te halen
            
        Returns:
            list: Lijst met waarden uit de kolom of None bij fout
        """
        if self.huidigDataFrame is None:
            logger.logFout("Kan kolom niet ophalen: Geen bestand geopend")
            return None
        
        try:
            # Controleer of de kolom bestaat
            if kolomNaam not in self.kolomNamen:
                logger.logFout(f"Kolom '{kolomNaam}' bestaat niet")
                return None
            
            # Haal kolom waarden op
            if rijen:
                startRij, eindRij = rijen
                # Controleer bereik
                if startRij < 0:
                    startRij = 0
                if eindRij >= len(self.huidigDataFrame):
                    eindRij = len(self.huidigDataFrame) - 1
                
                return self.huidigDataFrame[kolomNaam].iloc[startRij:eindRij + 1].tolist()
            else:
                return self.huidigDataFrame[kolomNaam].tolist()
        except Exception as e:
            logger.logFout(f"Fout bij ophalen kolom '{kolomNaam}': {e}")
            return None
    
    def slaOp(self):
        """
        Sla het huidige Excel-bestand op
        
        Returns:
            bool: True als het opslaan succesvol was, anders False
        """
        if not self.huidigBestand or self.huidigDataFrame is None:
            logger.logFout("Kan niet opslaan: Geen bestand geopend")
            return False
        
        try:
            # Backup functionaliteit verwijderd om stabiliteitsproblemen te voorkomen
            
            # Sla op naar origineel bestand
            self.huidigDataFrame.to_excel(self.huidigBestand, index=False)
            logger.logInfo(f"Excel-bestand opgeslagen: {self.huidigBestand}")
            
            return True
        except Exception as e:
            logger.logFout(f"Fout bij opslaan Excel-bestand: {e}")
            return False
    
    def haalRijAantal(self):
        """
        Haal het aantal rijen op in het huidige bestand
        
        Returns:
            int: Aantal rijen of 0 als er geen bestand is geopend
        """
        if self.huidigDataFrame is None:
            return 0
        
        return len(self.huidigDataFrame)
    
    def isBestandGeopend(self):
        """
        Controleer of er een bestand is geopend
        
        Returns:
            bool: True als er een bestand is geopend, anders False
        """
        return self.huidigBestand is not None and self.huidigDataFrame is not None

# Singleton instance voor gebruik in de hele applicatie
excelHandler = ExcelHandler()
