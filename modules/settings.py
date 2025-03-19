"""
Settings module voor Excelladin Reloaded
Beheert applicatie-instellingen zoals laatst geopende bestanden
"""
import os
import configparser
from modules.logger import logger

class Instellingen:
    """Instellingen klasse voor het beheren van applicatie-instellingen"""
    
    def __init__(self, configBestand="config.ini"):
        """
        Initialiseer de instellingen
        
        Args:
            configBestand (str): Pad naar het configuratiebestand
        """
        self.configBestand = configBestand
        self.config = configparser.ConfigParser()
        
        # Standaardinstellingen
        self.standaardInstellingen = {
            'Algemeen': {
                'LaatsteBestand': '',
                'OnthoudBestand': 'False',
            },
            'Interface': {
                'ToonTooltips': 'True',
            }
        }
        
        # Laad bestaande instellingen of maak nieuwe
        if os.path.exists(self.configBestand):
            try:
                self.config.read(self.configBestand, encoding='utf-8')
                logger.logInfo("Instellingen geladen uit bestand")
            except Exception as e:
                logger.logFout(f"Fout bij laden instellingen: {e}")
                self._maakStandaardInstellingen()
        else:
            self._maakStandaardInstellingen()
    
    def _maakStandaardInstellingen(self):
        """Maak standaardinstellingen aan"""
        for sectie, opties in self.standaardInstellingen.items():
            if not self.config.has_section(sectie):
                self.config.add_section(sectie)
            
            for optie, waarde in opties.items():
                self.config.set(sectie, optie, waarde)
        
        self.slaOp()
        logger.logInfo("Standaardinstellingen aangemaakt")
    
    def haalOp(self, sectie, optie, standaard=None):
        """
        Haal een instelling op
        
        Args:
            sectie (str): Configuratie sectie
            optie (str): Optienaam
            standaard: Standaardwaarde als de optie niet bestaat
            
        Returns:
            Waarde van de optie of standaardwaarde
        """
        try:
            if self.config.has_option(sectie, optie):
                return self.config.get(sectie, optie)
            return standaard
        except Exception as e:
            logger.logFout(f"Fout bij ophalen instelling {sectie}.{optie}: {e}")
            return standaard
    
    def stelIn(self, sectie, optie, waarde):
        """
        Stel een instelling in
        
        Args:
            sectie (str): Configuratie sectie
            optie (str): Optienaam
            waarde: Nieuwe waarde voor de optie
        """
        try:
            if not self.config.has_section(sectie):
                self.config.add_section(sectie)
            
            self.config.set(sectie, optie, str(waarde))
            self.slaOp()
            logger.logInfo(f"Instelling {sectie}.{optie} ingesteld op {waarde}")
        except Exception as e:
            logger.logFout(f"Fout bij instellen {sectie}.{optie}: {e}")
    
    def slaOp(self):
        """Sla instellingen op naar bestand"""
        try:
            with open(self.configBestand, 'w', encoding='utf-8') as bestand:
                self.config.write(bestand)
        except Exception as e:
            logger.logFout(f"Kon instellingen niet opslaan: {e}")
    
    def haalLaatsteBestand(self):
        """
        Haal het laatst gebruikte bestand op
        
        Returns:
            str: Pad naar laatst gebruikte bestand of leeg als er geen is
        """
        onthoud = self.haalOp('Algemeen', 'OnthoudBestand') == 'True'
        if onthoud:
            return self.haalOp('Algemeen', 'LaatsteBestand', '')
        return ''
    
    def stelLaatsteBestandIn(self, bestandspad):
        """
        Sla het laatst gebruikte bestand op
        
        Args:
            bestandspad (str): Pad naar het bestand
        """
        self.stelIn('Algemeen', 'LaatsteBestand', bestandspad)
    
    def stelOnthoudBestandIn(self, onthoud):
        """
        Stel in of het laatst gebruikte bestand moet worden onthouden
        
        Args:
            onthoud (bool): True als het bestand moet worden onthouden
        """
        self.stelIn('Algemeen', 'OnthoudBestand', str(onthoud))

# Singleton instance voor gebruik in de hele applicatie
instellingen = Instellingen()