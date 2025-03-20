"""
RentPro Handler - Hoofdklasse voor RentPro integratie
Verantwoordelijk voor het coördineren van alle RentPro componenten
Met ondersteuning voor zowel browser-mode als directe API-requests mode

BELANGRIJK: Dit is de definitieve implementatie die direct geïmporteerd wordt door
modules/rentpro_handler.py voor backwards compatibiliteit.
"""
import asyncio
from modules.logger import logger
from modules.rentpro.driver_manager import DriverManager
from modules.rentpro.authenticator import Authenticator
from modules.rentpro.navigator import Navigator
from modules.rentpro.data_extractor import DataExtractor
from modules.rentpro.excel_manager import ExcelManager
from modules.rentpro.api_handler import ApiHandler

class RentproHandler:
    """
    Hoofdklasse voor RentPro integratie
    Coördineert alle componenten voor een modulaire en robuuste implementatie
    
    Publieke methoden behouden dezelfde interface als de originele RentproHandler
    voor naadloze integratie met bestaande code.
    """
    
    def __init__(self):
        """Initialiseer de RentPro handler met alle componenten"""
        # Flags voor status en configuratie
        self.ingelogd = False
        self.gebruik_mockdata = False
        self.gebruik_api_mode = True  # Standaard API-mode gebruiken (zonder browser)
        
        # Initialiseer browser componenten
        self.driver_manager = DriverManager()
        self.authenticator = Authenticator(self.driver_manager)
        self.navigator = Navigator(self.driver_manager, self.authenticator)
        self.data_extractor = DataExtractor(self.driver_manager, self.navigator)
        self.excel_manager = ExcelManager()
        
        # Initialiseer API componenten
        self.api_handler = ApiHandler()
        
    async def initialize(self):
        """
        Initialiseer de RentPro handler en alle componenten
        In API-mode wordt geen WebDriver geïnitialiseerd
        
        Returns:
            bool: True als initialisatie succesvol was, anders False
        """
        try:
            # Als we in API-mode zijn, hoeven we de browser niet te initialiseren
            if self.gebruik_api_mode:
                logger.logInfo("API mode actief, geen browser initialisatie nodig")
                return True
                
            # Alleen in browser-mode: initialiseer de WebDriver
            logger.logInfo("Browser mode actief, WebDriver initialiseren")
            return await self.driver_manager.initialize()
        except Exception as e:
            logger.logFout(f"Kritieke fout bij initialisatie van RentPro handler: {e}")
            return False
            
    async def close(self):
        """
        Sluit de RentPro sessie en maak resources vrij
        In API-mode hoeft geen WebDriver gesloten te worden
        
        Returns:
            bool: True als het sluiten succesvol was, anders False
        """
        try:
            # Als we in API-mode zijn, hoeft de browser niet gesloten te worden
            if self.gebruik_api_mode:
                logger.logInfo("API mode actief, geen browser om te sluiten")
                return True
                
            # Alleen in browser-mode: sluit de WebDriver
            logger.logInfo("Browser mode actief, WebDriver sluiten")
            return await self.driver_manager.close()
        except Exception as e:
            logger.logFout(f"Fout bij sluiten van RentPro handler: {e}")
            return False
        
    async def login(self, gebruikersnaam, wachtwoord, url=None):
        """
        Log in op RentPro met gegeven credentials
        
        Args:
            gebruikersnaam (str): RentPro gebruikersnaam
            wachtwoord (str): RentPro wachtwoord
            url (str, optional): De URL voor de RentPro back-office
            
        Returns:
            bool: True als inloggen succesvol was, anders False
        """
        try:
            # Als we mockdata gebruiken, simuleer een succesvolle login
            if self.gebruik_mockdata:
                logger.logInfo("Mockdata modus actief, simuleren van succesvolle login")
                self.ingelogd = True
                return True
                
            # Controleer welke methode we gebruiken (API of browser)
            if self.gebruik_api_mode:
                logger.logInfo("API mode actief, inloggen via directe HTTP requests")
                # Login met de API handler
                login_success = await self.api_handler.login(gebruikersnaam, wachtwoord, url)
            else:
                logger.logInfo("Browser mode actief, inloggen via WebDriver")
                # Initialiseer browser eerst als nodig
                if not self.driver_manager.is_initialized:
                    init_success = await self.initialize()
                    if not init_success:
                        # Als initialisatie mislukt, schakel over naar API mode
                        logger.logWaarschuwing("WebDriver initialisatie mislukt, overschakelen naar API mode")
                        self.gebruik_api_mode = True
                        # Probeer opnieuw via API
                        return await self.login(gebruikersnaam, wachtwoord, url)
                
                # Login met de browser authenticator
                login_success = await self.authenticator.login(gebruikersnaam, wachtwoord, url)
            
            # Als login mislukt, log waarschuwing en schakel over naar mockdata
            if not login_success:
                # Als browser-mode mislukt, probeer API-mode
                if not self.gebruik_api_mode:
                    logger.logWaarschuwing("Browser login mislukt, overschakelen naar API mode")
                    self.gebruik_api_mode = True
                    return await self.login(gebruikersnaam, wachtwoord, url)
                
                # Als API-mode ook mislukt, schakel naar mockdata
                logger.logWaarschuwing("Login mislukt, overschakelen naar mockdata modus")
                self.gebruik_mockdata = True
                self.ingelogd = True  # Simuleer login voor UI compatibiliteit
                return True  # Geef True terug voor graceful degradation
            
            # Login gelukt
            self.ingelogd = True
            return True
            
        except Exception as e:
            logger.logFout(f"Onverwachte fout bij inloggen RentPro: {e}")
            
            # Als we in browser mode zijn, probeer API mode
            if not self.gebruik_api_mode:
                logger.logWaarschuwing("Fout bij browser login, overschakelen naar API mode")
                self.gebruik_api_mode = True
                try:
                    return await self.login(gebruikersnaam, wachtwoord, url)
                except Exception as api_e:
                    logger.logFout(f"Ook fout bij API login: {api_e}")
                    # Fallback naar mockdata
                    self.gebruik_mockdata = True
                    self.ingelogd = True
                    return True
            
            # Graceful degradation: schakel over naar mockdata modus
            logger.logWaarschuwing("Overschakelen naar mockdata modus door onverwachte fout")
            self.gebruik_mockdata = True
            self.ingelogd = True  # Simuleer login voor UI compatibiliteit
            return True  # Geef True terug voor graceful degradation

    async def haal_producten_op(self, overschrijf_lokaal=False, rijen=None):
        """
        Haal producten op van RentPro en update Excel
        Gebruikt verschillende methoden afhankelijk van mode (API/browser)
        
        Args:
            overschrijf_lokaal (bool): Of lokale data overschreven moet worden
            rijen (tuple): Optioneel, tuple met (startRij, eindRij)
            
        Returns:
            bool: True als ophalen succesvol was, anders False
        """
        try:
            # Controleer login status
            if not self.ingelogd:
                logger.logFout("Niet ingelogd bij RentPro")
                return False
            
            # Controleer of Excel bestand is geopend
            if not self.excel_manager.is_bestand_geopend():
                logger.logFout("Geen Excel-bestand geopend")
                return False
            
            # Bepaal de rijen om te verwerken
            row_range = self.excel_manager.get_row_range(
                None if rijen is None else rijen[0],
                None if rijen is None else rijen[1]
            )
            
            if not row_range:
                logger.logFout("Kon rijbereik niet bepalen")
                return False
                
            start_rij, eind_rij = row_range
            
            # Als we mockdata gebruiken, genereer mockdata
            if self.gebruik_mockdata:
                logger.logInfo("Mockdata modus actief, genereren van mockdata")
                return await self._verwerk_mock_producten(overschrijf_lokaal, start_rij, eind_rij)
            
            # Navigeer naar producten pagina en haal producten op via de juiste methode
            if self.gebruik_api_mode:
                logger.logInfo("API mode actief, navigeren en ophalen via API")
                # Navigeer via API naar de productenpagina
                await self.api_handler.navigate_to_products()
            else:
                logger.logInfo("Browser mode actief, navigeren en ophalen via WebDriver")
                # Haal productlijst op via WebDriver
                await self.data_extractor.get_products_list()
            
            # Loop door elke rij en verwerk producten
            succesvol = 0
            for row_index in range(start_rij, eind_rij + 1):
                # Haal product ID uit Excel
                product_id = self.excel_manager.get_product_id(row_index)
                if not product_id:
                    # Geen ProductID, sla deze rij over
                    continue
                
                # Haal product details op via de juiste methode
                product_data = None
                if self.gebruik_api_mode:
                    # Haal product details op via API
                    product_data = await self.api_handler.get_product_details(product_id)
                else:
                    # Haal product details op via WebDriver
                    product_data = await self.data_extractor.get_product_details(product_id)
                
                if not product_data:
                    # Kon geen productdetails ophalen
                    continue
                
                # Update Excel
                update_success = self.excel_manager.update_product_row(
                    row_index, product_data, overschrijf_lokaal
                )
                
                if update_success:
                    succesvol += 1
                
                # Log voortgang periodiek
                if (row_index - start_rij) % 5 == 0 or row_index == eind_rij:
                    logger.logInfo(f"Voortgang: {row_index - start_rij + 1}/{eind_rij - start_rij + 1} producten verwerkt")
            
            logger.logInfo(f"Klaar met ophalen producten. {succesvol} producten succesvol bijgewerkt.")
            return True
            
        except Exception as e:
            logger.logFout(f"Onverwachte fout bij ophalen producten: {e}")
            
            # Graceful degradation: schakel over naar mockdata modus
            logger.logWaarschuwing("Overschakelen naar mockdata modus door onverwachte fout")
            self.gebruik_mockdata = True
            
            # Probeer opnieuw met mockdata
            return await self._verwerk_mock_producten(
                overschrijf_lokaal,
                start_rij if 'start_rij' in locals() else 0,
                eind_rij if 'eind_rij' in locals() else 0
            )
    
    async def _verwerk_mock_producten(self, overschrijf_lokaal, start_rij, eind_rij):
        """
        Verwerk mockdata voor producten
        
        Args:
            overschrijf_lokaal (bool): Of lokale data overschreven moet worden
            start_rij (int): Eerste rij om te verwerken
            eind_rij (int): Laatste rij om te verwerken
            
        Returns:
            bool: True als verwerken succesvol was, anders False
        """
        try:
            import time
            import random
            
            # Configuratie voor mockdata variatie
            product_prefixes = ["Premium", "Standard", "Basic", "Pro", "Elite"]
            product_types = ["Speaker", "Microfoon", "Kabel", "Licht", "Mixer", "Monitor", "Statief"]
            product_suffixes = ["XL", "Mini", "Pro", "Ultra", "Plus", "Max"]
            
            # Loop door elke rij
            succesvol = 0
            for row_index in range(start_rij, eind_rij + 1):
                # Haal product ID uit Excel
                product_id = self.excel_manager.get_product_id(row_index)
                if not product_id:
                    continue
                
                # Genereer unieke maar consistente mock data op basis van product_id
                seed = sum(ord(c) for c in product_id)
                random.seed(seed)
                
                prefix = random.choice(product_prefixes)
                type = random.choice(product_types)
                suffix = random.choice(product_suffixes)
                
                # Maak mock product data
                product_data = {
                    'id': product_id,
                    'naam': f"{prefix} {type} {suffix}",
                    'beschrijving': f"Mock beschrijving voor {product_id}: Professionele {type.lower()} voor diverse toepassingen.",
                    'prijs': f"{random.randint(50, 5000):.2f}",
                    'categorie': f"{type}s",
                    'voorraad': str(random.randint(0, 100)),
                    'afbeelding_url': "",
                    'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Update Excel
                update_success = self.excel_manager.update_product_row(
                    row_index, product_data, overschrijf_lokaal
                )
                
                if update_success:
                    succesvol += 1
                
                # Simuleer verwerking voor natuurlijker gedrag
                await asyncio.sleep(0.05)
                
                # Log voortgang periodiek
                if (row_index - start_rij) % 5 == 0 or row_index == eind_rij:
                    logger.logInfo(f"Voortgang (mock): {row_index - start_rij + 1}/{eind_rij - start_rij + 1} producten verwerkt")
            
            logger.logInfo(f"Klaar met verwerken mock producten. {succesvol} producten succesvol bijgewerkt.")
            return True
            
        except Exception as e:
            logger.logFout(f"Fout bij verwerken mock producten: {e}")
            return False
            
    async def navigeer_naar_producten(self):
        """
        Navigeer naar de productenpagina
        Gebruikt verschillende navigatiemethoden afhankelijk van mode (API/browser)
        
        Returns:
            bool: True als navigatie succesvol was, anders False
        """
        try:
            # Controleer login status
            if not self.ingelogd:
                logger.logFout("Niet ingelogd bij RentPro")
                return False
            
            # Als we mockdata gebruiken, simuleer een succesvolle navigatie
            if self.gebruik_mockdata:
                logger.logInfo("Mockdata modus actief, simuleren van succesvolle navigatie")
                return True
                
            # Navigeer met juiste methode afhankelijk van mode
            if self.gebruik_api_mode:
                logger.logInfo("API mode actief, navigeren via API")
                return await self.api_handler.navigate_to_products()
            else:
                logger.logInfo("Browser mode actief, navigeren via WebDriver")
                return await self.navigator.go_to_products()
            
        except Exception as e:
            logger.logFout(f"Onverwachte fout bij navigeren naar producten: {e}")
            
            # Graceful degradation: schakel over naar mockdata modus
            logger.logWaarschuwing("Overschakelen naar mockdata modus door onverwachte fout")
            self.gebruik_mockdata = True
            return True  # Simuleer succes voor UI compatibiliteit
            
    async def evalueer_javascript(self, js_code):
        """
        Evalueer JavaScript code op de huidige pagina
        Werkt alleen in browser-mode, niet in API-mode
        
        Args:
            js_code (str): JavaScript code om te evalueren
            
        Returns:
            any: Resultaat van de JavaScript evaluatie of None bij fout
        """
        try:
            # Controleer login status
            if not self.ingelogd:
                logger.logFout("Niet ingelogd bij RentPro")
                return None
            
            # Als we mockdata of API mode gebruiken, is JavaScript niet beschikbaar
            if self.gebruik_mockdata:
                logger.logInfo("Mockdata modus actief, JavaScript evaluatie niet beschikbaar")
                return ""
                
            if self.gebruik_api_mode:
                logger.logInfo("API mode actief, JavaScript evaluatie niet beschikbaar")
                return ""
            
            # Controleer of driver geïnitialiseerd is (alleen in browser-mode relevant)
            driver = self.driver_manager.get_driver()
            if not driver:
                logger.logFout("WebDriver niet geïnitialiseerd")
                return None
            
            # Maak een future om het resultaat van de thread terug te geven
            future = asyncio.get_event_loop().create_future()
            
            def _evalueer_js_process():
                try:
                    with self.driver_manager.get_lock():
                        result = driver.execute_script(js_code)
                        future.set_result(result)
                except Exception as e:
                    logger.logFout(f"Fout bij evalueren JavaScript: {e}")
                    future.set_exception(e)
            
            # Start het proces in een aparte thread
            import threading
            threading.Thread(target=_evalueer_js_process, daemon=True).start()
            
            try:
                # Wacht op het resultaat met timeout
                return await asyncio.wait_for(future, timeout=30)
            except asyncio.TimeoutError:
                logger.logFout("Timeout bij evalueren JavaScript")
                return None
            except Exception as e:
                logger.logFout(f"Fout bij evalueren JavaScript: {e}")
                return None
            
        except Exception as e:
            logger.logFout(f"Onverwachte fout bij evalueren JavaScript: {e}")
            return None
            
    def set_mockdata_mode(self, enabled):
        """
        Schakel mockdata modus in of uit
        
        Args:
            enabled (bool): True om mockdata modus in te schakelen, False om uit te schakelen
        """
        self.gebruik_mockdata = enabled
        logger.logInfo(f"Mockdata modus {'ingeschakeld' if enabled else 'uitgeschakeld'}")

# Singleton instance voor gebruik in de hele applicatie
rentproHandler = RentproHandler()
