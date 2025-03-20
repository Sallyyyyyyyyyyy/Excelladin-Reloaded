"""
Driver Manager voor RentPro integratie
Beheert de WebDriver voor browsergebaseerde functies
BELANGRIJK: In API-mode wordt deze driver NIET gebruikt
"""
import asyncio
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.logger import logger

class DriverManager:
    """
    Beheert de WebDriver voor RentPro browserinteracties
    Met API mode ondersteuning om browsergebruik volledig te vermijden indien gewenst
    """
    
    def __init__(self):
        """Initialiseer de manager zonder browser te starten"""
        self.driver = None
        self.is_initialized = False
        self.driver_lock = threading.Lock()
    
    def get_driver(self):
        """
        Geef de WebDriver instantie terug
        
        Returns:
            WebDriver: De huidige WebDriver of None als niet geïnitialiseerd
        """
        return self.driver
    
    def get_lock(self):
        """
        Geef het threading lock object voor thread-safe operaties
        
        Returns:
            Lock: Threading lock object
        """
        return self.driver_lock
    
    async def initialize(self):
        """
        Initialiseer een nieuwe WebDriver instantie
        
        Returns:
            bool: True als initialisatie succesvol was, anders False
        """
        # Sluit bestaande driver indien nodig
        await self.close()
        
        # Creëer future voor asynchrone werking
        future = asyncio.get_event_loop().create_future()
        
        def _init_driver():
            try:
                # Configureer browser opties
                options = webdriver.ChromeOptions()
                options.add_argument("--ignore-certificate-errors")
                options.add_argument("--disable-web-security")
                options.add_argument("--allow-running-insecure-content")
                options.add_argument("--window-size=1600,1000")
                
                # Deze regel verwijderd om automatisch sluiten te ondersteunen
                # options.add_experimental_option("detach", True)
                
                # Deze opties maken de browser headless (onzichtbaar)
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                
                # Stil debugging bericht
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                
                # Start de browser
                self.driver = webdriver.Chrome(options=options)
                
                # Stel timeouts in
                self.driver.set_page_load_timeout(30)
                self.driver.set_script_timeout(30)
                
                # Markeer als geïnitialiseerd
                self.is_initialized = True
                future.set_result(True)
                
            except Exception as e:
                logger.logFout(f"Fout bij initialiseren WebDriver: {e}")
                future.set_exception(e)
        
        # Start in achtergrond thread
        thread = threading.Thread(target=_init_driver, daemon=True)
        thread.start()
        
        try:
            # Wacht op resultaat
            await asyncio.wait_for(future, timeout=30)
            logger.logInfo("WebDriver succesvol gestart")
            return True
        except Exception as e:
            logger.logFout(f"Fout bij starten WebDriver: {e}")
            return False
    
    async def close(self):
        """
        Sluit de WebDriver indien actief
        
        Returns:
            bool: True als sluiten succesvol was of geen driver actief was, anders False
        """
        if self.driver:
            try:
                with self.driver_lock:
                    self.driver.quit()
                self.driver = None
                self.is_initialized = False
                logger.logInfo("WebDriver succesvol afgesloten")
                return True
            except Exception as e:
                logger.logFout(f"Fout bij sluiten WebDriver: {e}")
                self.driver = None
                self.is_initialized = False
                return False
        
        # Geen driver actief
        return True
