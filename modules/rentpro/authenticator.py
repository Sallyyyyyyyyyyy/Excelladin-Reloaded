"""
Authenticator voor RentPro integratie
Verantwoordelijk voor browser-gebaseerde authenticatie
BELANGRIJK: In API-mode wordt deze module NIET gebruikt
"""
import asyncio
import time
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.logger import logger

class Authenticator:
    """
    Beheert de authenticatie process voor RentPro in browser mode
    BELANGRIJK: Alleen gebruikt in browser mode, niet in API mode
    """
    
    def __init__(self, driver_manager):
        """
        Initialiseer de authenticator
        
        Args:
            driver_manager (DriverManager): De driver manager instantie
        """
        self.driver_manager = driver_manager
        self.base_url = "http://metroeventsdc.rentpro5.nl"
    
    async def login(self, username, password, url=None):
        """
        Log in op RentPro via de browser
        
        Args:
            username (str): Gebruikersnaam
            password (str): Wachtwoord
            url (str, optional): Base URL voor RentPro
            
        Returns:
            bool: True als inloggen succesvol was, anders False
        """
        try:
            # Update URL indien opgegeven
            if url:
                if not url.startswith(('http://', 'https://')):
                    url = f"http://{url}"
                self.base_url = url
            
            # Controleer of driver geïnitialiseerd is
            driver = self.driver_manager.get_driver()
            if not driver:
                logger.logFout("WebDriver niet geïnitialiseerd voor login")
                return False
            
            # Creëer een future voor async werking
            future = asyncio.get_event_loop().create_future()
            
            def _login_process():
                try:
                    with self.driver_manager.get_lock():
                        # Navigeer naar login pagina
                        logger.logInfo("Navigeren naar login pagina...")
                        driver.get(f"{self.base_url}/Account/Login")
                        
                        # Wacht op laden body element
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        
                        # Controleer huidige URL (voor data: URL probleem)
                        current_url = driver.current_url
                        logger.logInfo(f"Huidige URL: {current_url}")
                        
                        if current_url.startswith("data:"):
                            logger.logFout("PROBLEEM: data: URL gedetecteerd!")
                            future.set_result(False)
                            return
                        
                        # Controleer op iframe en switch indien nodig
                        iframes = driver.find_elements(By.TAG_NAME, "iframe")
                        if iframes:
                            logger.logInfo("Iframe gevonden, overschakelen...")
                            driver.switch_to.frame(iframes[0])
                        
                        # Vul inloggegevens in
                        logger.logInfo("Inloggegevens invullen...")
                        username_field = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.NAME, "UserName"))
                        )
                        username_field.clear()
                        username_field.send_keys(username)
                        
                        password_field = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.NAME, "Password"))
                        )
                        password_field.clear()
                        password_field.send_keys(password)
                        
                        # Klik op login knop
                        logger.logInfo("Login knop klikken...")
                        login_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Log in']"))
                        )
                        login_button.click()
                        
                        # Wacht op pagina laden na login
                        logger.logInfo("Wachten op login resultaat...")
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        
                        # Controleer login succes
                        page_source = driver.page_source
                        
                        if "Log in" in page_source and "UserName" in page_source:
                            logger.logFout("Login niet succesvol, nog steeds op login pagina")
                            future.set_result(False)
                            return
                        
                        # Controleer voor succes indicators
                        success_indicators = [
                            "Klanten vandaag online", "Dashboard", "Welkom", 
                            "Uitloggen", "Logout", "Menu"
                        ]
                        
                        if any(indicator in page_source for indicator in success_indicators):
                            logger.logInfo("Login succesvol! (indicator gevonden)")
                            future.set_result(True)
                            return
                        
                        # Geen succes indicators gevonden
                        logger.logFout("Login niet succesvol, geen succes indicators gevonden")
                        future.set_result(False)
                
                except Exception as e:
                    logger.logFout(f"Fout bij login process: {e}")
                    future.set_result(False)
            
            # Start thread process
            thread = threading.Thread(target=_login_process, daemon=True)
            thread.start()
            
            # Wacht op resultaat
            return await asyncio.wait_for(future, timeout=30)
        
        except Exception as e:
            logger.logFout(f"Fout bij login: {e}")
            return False
