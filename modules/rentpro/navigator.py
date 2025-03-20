"""
Navigator voor RentPro integratie
Verantwoordelijk voor navigatie in de RentPro interface
BELANGRIJK: In API-mode wordt deze module NIET gebruikt
"""
import asyncio
import time
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.logger import logger

class Navigator:
    """
    Beheert de navigatie binnen de RentPro interface
    BELANGRIJK: Alleen gebruikt in browser mode, niet in API mode
    """
    
    def __init__(self, driver_manager, authenticator):
        """
        Initialiseer de navigator
        
        Args:
            driver_manager (DriverManager): De driver manager instantie
            authenticator (Authenticator): De authenticator instantie
        """
        self.driver_manager = driver_manager
        self.authenticator = authenticator
        self.base_url = "http://metroeventsdc.rentpro5.nl"
    
    async def go_to_products(self):
        """
        Navigeer naar de productenpagina
        
        Returns:
            bool: True als navigatie succesvol was, anders False
        """
        try:
            # Controleer of driver geïnitialiseerd is
            driver = self.driver_manager.get_driver()
            if not driver:
                logger.logFout("WebDriver niet geïnitialiseerd voor navigatie")
                return False
            
            # Creëer een future voor async werking
            future = asyncio.get_event_loop().create_future()
            
            def _navigate_process():
                try:
                    with self.driver_manager.get_lock():
                        # Navigeer naar producten pagina
                        logger.logInfo("Navigeren naar productenpagina...")
                        products_url = f"{self.base_url}/Product"
                        driver.get(products_url)
                        
                        # Wacht op laden body element
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        
                        # Controleer of we op de juiste pagina zijn
                        current_url = driver.current_url
                        
                        # Als we naar de login pagina zijn omgeleid
                        if "Account/Login" in current_url:
                            logger.logWaarschuwing("Doorgestuurd naar login pagina - sessie mogelijk verlopen")
                            future.set_result(False)
                            return
                        
                        # Wacht kort voor stabiliteit
                        time.sleep(1)
                        
                        # Controleer specifieke elementen op de product pagina
                        try:
                            # Zoek producten tabel, knop of andere indicator
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "table.grid"))
                            )
                            logger.logInfo("Productenpagina succesvol geladen")
                            future.set_result(True)
                            return
                        except Exception:
                            logger.logWaarschuwing("Geen producten tabel gevonden op pagina")
                        
                        # Als we hier komen, is navigatie waarschijnlijk gelukt maar niet bevestigd
                        logger.logInfo("Pagina geladen zonder bevestiging van producten tabel")
                        future.set_result(True)
                
                except Exception as e:
                    logger.logFout(f"Fout bij navigatie: {e}")
                    future.set_result(False)
            
            # Start navigatie in aparte thread
            thread = threading.Thread(target=_navigate_process, daemon=True)
            thread.start()
            
            # Wacht op resultaat
            return await asyncio.wait_for(future, timeout=30)
        
        except Exception as e:
            logger.logFout(f"Fout bij navigatie naar producten: {e}")
            return False
    
    async def go_to_product_details(self, product_id):
        """
        Navigeer naar de detailpagina van een specifiek product
        
        Args:
            product_id (str): ID van het product
            
        Returns:
            bool: True als navigatie succesvol was, anders False
        """
        try:
            # Controleer of driver geïnitialiseerd is
            driver = self.driver_manager.get_driver()
            if not driver:
                logger.logFout("WebDriver niet geïnitialiseerd voor navigatie")
                return False
            
            # Creëer een future voor async werking
            future = asyncio.get_event_loop().create_future()
            
            def _navigate_process():
                try:
                    with self.driver_manager.get_lock():
                        # Navigeer naar product details pagina
                        logger.logInfo(f"Navigeren naar product details voor {product_id}...")
                        details_url = f"{self.base_url}/Product/Details/{product_id}"
                        driver.get(details_url)
                        
                        # Wacht op laden body element
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        
                        # Controleer of we op de juiste pagina zijn
                        current_url = driver.current_url
                        
                        # Als we naar de login pagina zijn omgeleid
                        if "Account/Login" in current_url:
                            logger.logWaarschuwing("Doorgestuurd naar login pagina - sessie mogelijk verlopen")
                            future.set_result(False)
                            return
                        
                        # Als we naar een foutpagina zijn omgeleid
                        if "Error" in current_url or "NotFound" in current_url:
                            logger.logWaarschuwing(f"Product {product_id} niet gevonden")
                            future.set_result(False)
                            return
                        
                        # Wacht kort voor stabiliteit
                        time.sleep(1)
                        
                        # Controleer of we details pagina hebben
                        try:
                            # Zoek details formulier of product naam
                            WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "form.product-details, .product-name, #product-details"))
                            )
                            logger.logInfo(f"Product details voor {product_id} succesvol geladen")
                            future.set_result(True)
                            return
                        except Exception:
                            logger.logWaarschuwing("Specifieke product details elementen niet gevonden")
                        
                        # Als we hier komen, is navigatie waarschijnlijk gelukt maar niet bevestigd
                        logger.logInfo(f"Product details pagina voor {product_id} geladen zonder bevestiging van details elementen")
                        future.set_result(True)
                
                except Exception as e:
                    logger.logFout(f"Fout bij navigatie naar product details: {e}")
                    future.set_result(False)
            
            # Start navigatie in aparte thread
            thread = threading.Thread(target=_navigate_process, daemon=True)
            thread.start()
            
            # Wacht op resultaat
            return await asyncio.wait_for(future, timeout=30)
        
        except Exception as e:
            logger.logFout(f"Fout bij navigatie naar product details: {e}")
            return False
