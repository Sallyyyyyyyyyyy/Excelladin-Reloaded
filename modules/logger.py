"""
Logger module voor Excelladin Reloaded
Verantwoordelijk voor het bijhouden van alle acties en fouten
"""
import os
import datetime
import glob

class Logger:
    """Logger klasse voor het bijhouden van acties en fouten in Excelladin Reloaded"""
    
    def __init__(self, logBestandsnaam=None, max_logfiles=5):
        """
        Initialiseer de logger
        
        Args:
            logBestandsnaam (str): Oude parameter, wordt genegeerd voor backwards compatibiliteit
            max_logfiles (int): Maximum aantal logbestanden dat bewaard wordt
        """
        # Melding geven als oude parameter wordt gebruikt
        if logBestandsnaam is not None and logBestandsnaam != "PatchCalling4Emergency.txt":
            # Verwijder print statement om terminal venster te voorkomen
            pass
            
        # Zorg dat de logs map bestaat
        if not os.path.exists("logs"):
            os.makedirs("logs")
            
        # Genereer bestandsnaam op basis van datum en tijd
        nu = datetime.datetime.now()
        datumtijd = nu.strftime("%Y-%m-%d_%H-%M-%S")
        
        # Maak volledige pad naar logbestand
        self.logBestandsnaam = os.path.join("logs", f"All_logs_combined_{datumtijd}.txt")
        self.max_logfiles = max_logfiles
        
        # Controleer en ruim oude logbestanden op indien nodig
        self._ruim_oude_logs_op()
        
        # Maak nieuw logbestand
        with open(self.logBestandsnaam, 'w', encoding='utf-8') as bestand:
            bestand.write("=== Excelladin Reloaded Log Bestand ===\n")
            bestand.write("Gestart op: {}\n".format(
                nu.strftime("%Y-%m-%d %H:%M:%S")
            ))
            bestand.write("==========================================\n\n")
    
    def _ruim_oude_logs_op(self):
        """Verwijder oude logbestanden als er meer zijn dan max_logfiles"""
        try:
            # Zoek alle logbestanden
            logbestanden = glob.glob(os.path.join("logs", "All_logs_combined_*.txt"))
            
            # Sorteer op datum (nieuwste eerst)
            logbestanden.sort(reverse=True)
            
            # Behoud alleen de nieuwste max_logfiles
            if len(logbestanden) >= self.max_logfiles:
                for oud_bestand in logbestanden[self.max_logfiles-1:]:
                    try:
                        os.remove(oud_bestand)
                        # Verwijder print statement om terminal venster te voorkomen
                    except Exception as e:
                        # Log naar bestand in plaats van naar console
                        with open(self.logBestandsnaam, 'a', encoding='utf-8') as bestand:
                            bestand.write(f"Kon oud logbestand niet verwijderen: {e}\n")
        except Exception as e:
            # Log naar bestand in plaats van naar console
            with open(self.logBestandsnaam, 'a', encoding='utf-8') as bestand:
                bestand.write(f"Fout bij opruimen oude logbestanden: {e}\n")
    
    def _formateerBericht(self, berichtType, bericht):
        """
        Formateer een logbericht in 1001 Nachten stijl
        
        Args:
            berichtType (str): Type bericht (INFO, WAARSCHUWING, FOUT)
            bericht (str): Het te loggen bericht
            
        Returns:
            str: Geformatteerd bericht
        """
        huidigetijd = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1001 Nachten stijl berichten
        prefixen = {
            "INFO": "O wijze gebruiker, ",
            "WAARSCHUWING": "Wees gewaarschuwd, o reiziger, ",
            "FOUT": "Bij Allah's baard! Een ramp is geschied: ",
            "ACTIE": "De geest van Excelladin voerde uit: ",
            "PATCH": "De magiër heeft de code bezworen: "
        }
        
        prefix = prefixen.get(berichtType, "")
        
        return f"[{huidigetijd}] [{berichtType}] {prefix}{bericht}"
    
    def log(self, bericht, berichtType="INFO"):
        """
        Log een bericht naar het logbestand
        
        Args:
            bericht (str): Het te loggen bericht
            berichtType (str): Type bericht (INFO, WAARSCHUWING, FOUT)
        """
        try:
            with open(self.logBestandsnaam, 'a', encoding='utf-8') as bestand:
                bestand.write(self._formateerBericht(berichtType, bericht) + "\n")
        except Exception as e:
            # Verwijder print statement om terminal venster te voorkomen
            pass
    
    def logInfo(self, bericht):
        """Log een informatiebericht"""
        self.log(bericht, "INFO")
    
    def logWaarschuwing(self, bericht):
        """Log een waarschuwingsbericht"""
        self.log(bericht, "WAARSCHUWING")
    
    def logFout(self, bericht):
        """Log een foutbericht"""
        self.log(bericht, "FOUT")
    
    def logActie(self, bericht):
        """Log een actiebericht"""
        self.log(bericht, "ACTIE")
    
    def logPatch(self, bericht):
        """Log een patchbericht"""
        self.log(bericht, "PATCH")
    
    def haalRecenteLogs(self, aantalRegels=10):
        """
        Haal de meest recente logregels op
        
        Args:
            aantalRegels (int): Aantal regels om op te halen
            
        Returns:
            list: Lijst met recente logregels
        """
        try:
            with open(self.logBestandsnaam, 'r', encoding='utf-8') as bestand:
                alleRegels = bestand.readlines()
                return alleRegels[-aantalRegels:] if len(alleRegels) > aantalRegels else alleRegels
        except Exception as e:
            # Verwijder print statement om terminal venster te voorkomen
            return []

# Singleton instance voor gebruik in de hele applicatie
logger = Logger()
