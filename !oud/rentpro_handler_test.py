"""
Vereenvoudigde testversie van Rentpro Handler voor debug-doeleinden
Bevat alleen de essentiële functionaliteit voor authenticatie en navigatie
"""
import asyncio
import time
import threading
import os
import sys

# Voeg het hoofddirectory toe aan sys.path voor correcte imports bij direct uitvoeren
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from modules.logger import logger

class RentproHandler:
    """Vereenvoudigde klasse voor Rentpro integratie via Selenium WebDriver"""
    
    def __init__(self):
        """Initialiseer de Rentpro handler"""
        self.driver = None
        self.ingelogd = False
        self.base_url = "http://metroeventsdc.rentpro5.nl"  # Bewezen werkende URL uit turboturbo scripts
        self.timeout = 15  # Hogere timeout voor betere betrouwbaarheid
        self._driver_lock = threading.Lock()
    
    async def initialize(self):
        """Initialiseer WebDriver (Chrome)"""
        logger.logInfo("WebDriver initialiseren...")
        
        # Start driver in een aparte thread om async compatibiliteit te behouden
        future = asyncio.get_event_loop().create_future()
        
        def _init_driver():
            try:
                # Chrome opties gebaseerd op turboturbo script
                options = webdriver.ChromeOptions()
                options.add_argument("--ignore-certificate-errors")
                options.add_argument("--disable-web-security")
                options.add_argument("--allow-running-insecure-content")
                options.add_argument("--window-size=1600,1000")
                
                with self._driver_lock:
                    self.driver = webdriver.Chrome(options=options)
                    future.set_result(True)
            except Exception as e:
                future.set_exception(e)
        
        threading.Thread(target=_init_driver, daemon=True).start()
        
        try:
            await future
            logger.logInfo("WebDriver succesvol geïnitialiseerd")
            return True
        except Exception as e:
            logger.logFout(f"Fout bij initialiseren WebDriver: {e}")
            return False
    
    async def close(self):
        """Sluit WebDriver"""
        if self.driver:
            try:
                with self._driver_lock:
                    self.driver.quit()
                    self.driver = None
                    self.ingelogd = False
                logger.logInfo("WebDriver sessie gesloten")
                return True
            except Exception as e:
                logger.logFout(f"Fout bij sluiten WebDriver: {e}")
                return False
        return True
    
    async def login(self, gebruikersnaam, wachtwoord, url=None):
        """Login functionaliteit uit turboturbo scripts"""
        if not gebruikersnaam or not wachtwoord:
            logger.logFout("Gebruikersnaam of wachtwoord ontbreekt")
            return False
            
        if not self.driver:
            success = await self.initialize()
            if not success:
                return False
                
        if url:
            self.base_url = url
            if not self.base_url.startswith('http'):
                self.base_url = f"http://{self.base_url}"
        
        future = asyncio.get_event_loop().create_future()
        
        def _login_process():
            try:
                with self._driver_lock:
                    # 1. Navigeer naar login pagina
                    logger.logInfo(f"Navigeren naar {self.base_url}")
                    self.driver.get(self.base_url)
                    
                    # 2. Wacht op body element
                    WebDriverWait(self.driver, self.timeout).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # 3. Controleer op iframes zoals in turboturbo script
                    iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                    if iframes:
                        logger.logInfo("Iframe gevonden, overschakelen")
                        self.driver.switch_to.frame(iframes[0])
                    
                    # 4. Vul gebruikersnaam in
                    try:
                        username_field = WebDriverWait(self.driver, self.timeout).until(
                            EC.presence_of_element_located((By.NAME, "UserName"))
                        )
                        username_field.clear()
                        username_field.send_keys(gebruikersnaam)
                        logger.logInfo("Gebruikersnaam ingevuld")
                    except (TimeoutException, NoSuchElementException) as e:
                        logger.logFout(f"Kon gebruikersnaamveld niet vinden: {e}")
                        future.set_result(False)
                        return
                    
                    # 5. Vul wachtwoord in
                    try:
                        password_field = WebDriverWait(self.driver, self.timeout).until(
                            EC.presence_of_element_located((By.NAME, "Password"))
                        )
                        password_field.clear()
                        password_field.send_keys(wachtwoord)
                        logger.logInfo("Wachtwoord ingevuld")
                    except (TimeoutException, NoSuchElementException) as e:
                        logger.logFout(f"Kon wachtwoordveld niet vinden: {e}")
                        future.set_result(False)
                        return
                    
                    # 6. Klik op login knop (exacte XPath uit turboturbo script)
                    try:
                        login_button = WebDriverWait(self.driver, self.timeout).until(
                            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Log in']"))
                        )
                        login_button.click()
                        logger.logInfo("Login knop geklikt")
                    except (TimeoutException, NoSuchElementException) as e:
                        logger.logFout(f"Kon login knop niet vinden: {e}")
                        future.set_result(False)
                        return
                    
                    # 7. Wacht na login
                    time.sleep(3)
                    
                    # 8. Controleer op "Klanten vandaag online" (bewezen indicator uit turboturbo script)
                    try:
                        klanten_indicator = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Klanten vandaag online')]")
                        if klanten_indicator:
                            logger.logInfo("Succesvol ingelogd (Klanten vandaag online gevonden)")
                            self.ingelogd = True
                            future.set_result(True)
                            return
                        else:
                            logger.logFout("Kon login niet bevestigen, indicator niet gevonden")
                            future.set_result(False)
                    except Exception as e:
                        logger.logFout(f"Fout bij verifiëren login: {e}")
                        future.set_result(False)
            
            except Exception as e:
                logger.logFout(f"Fout tijdens login: {e}")
                future.set_result(False)
        
        threading.Thread(target=_login_process, daemon=True).start()
        return await future
    
    async def navigate_to_products(self):
        """Navigeer naar productpagina volgens turboturbo script"""
        if not self.ingelogd or not self.driver:
            logger.logFout("Niet ingelogd bij Rentpro")
            return False
            
        future = asyncio.get_event_loop().create_future()
        
        def _navigate_process():
            try:
                with self._driver_lock:
                    # 1. Navigeer naar productpagina
                    product_url = f"{self.base_url}/Product"
                    logger.logInfo(f"Navigeren naar productpagina: {product_url}")
                    self.driver.get(product_url)
                    
                    # 2. Wacht op body element
                    WebDriverWait(self.driver, self.timeout).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # 3. Stabilisatietijd zoals in turboturbo script
                    logger.logInfo("Wachten op stabilisatie (3s)")
                    time.sleep(3)
                    
                    # 4. Controleer op specifiek product uit turboturbo script
                    try:
                        product_check = self.driver.find_elements(
                            By.XPATH, "//*[contains(text(), 'dB DVA S1521N 21\" sub actief')]"
                        )
                        if product_check:
                            logger.logInfo("Productpagina succesvol geladen (product gevonden)")
                            future.set_result(True)
                            return
                    except Exception:
                        pass
                    
                    # 5. Controleer alternatief op productindicatoren
                    page_source = self.driver.page_source.lower()
                    if ('product' in page_source or 'artikel' in page_source):
                        logger.logInfo("Productpagina succesvol geladen")
                        future.set_result(True)
                    else:
                        logger.logFout("Kon productpagina niet laden of herkennen")
                        future.set_result(False)
            
            except Exception as e:
                logger.logFout(f"Fout bij navigeren naar productpagina: {e}")
                future.set_result(False)
        
        threading.Thread(target=_navigate_process, daemon=True).start()
        return await future

# Testfunctie om script zelfstandig te kunnen testen
async def test_handler():
    handler = RentproHandler()
    try:
        # Test login
        print("=== TEST: Login ===")
        logger.logInfo("=== TEST: Login ===")
        login_success = await handler.login("sally", "e7VBPymQ")  # Testcredentials uit turboturbo script
        print(f"Login resultaat: {'Succes' if login_success else 'Mislukt'}")
        logger.logInfo(f"Login resultaat: {'Succes' if login_success else 'Mislukt'}")
        
        if login_success:
            # Test navigatie
            print("=== TEST: Navigatie naar producten ===")
            logger.logInfo("=== TEST: Navigatie naar producten ===")
            nav_success = await handler.navigate_to_products()
            print(f"Navigatie resultaat: {'Succes' if nav_success else 'Mislukt'}")
            logger.logInfo(f"Navigatie resultaat: {'Succes' if nav_success else 'Mislukt'}")
    
    finally:
        # Sluit browser
        await handler.close()

# Singleton instance (zoals in originele implementatie)
rentproHandler = RentproHandler()

# Voer test uit wanneer script direct wordt uitgevoerd
if __name__ == "__main__":
    print("RentPro Handler test script wordt uitgevoerd...")
    asyncio.run(test_handler())
