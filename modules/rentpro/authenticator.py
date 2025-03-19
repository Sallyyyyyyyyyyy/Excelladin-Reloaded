"""
Authenticator voor RentPro integratie
Verantwoordelijk voor authenticatie en sessiemanagement
Gebaseerd op het turboturbo script
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.logger import logger

class Authenticator:
    """
    Beheert het inloggen en authenticatieproces voor RentPro
    Direct overgenomen van het turboturbo script voor maximale betrouwbaarheid
    """
    
    def __init__(self, driver_manager):
        """Initialiseer de authenticator"""
        self.driver_manager = driver_manager
        self.is_authenticated = False
        self.base_url = "http://metroeventsdc.rentpro5.nl"  # Standaard URL
    
    def set_base_url(self, url):
        """Stel de basis URL in"""
        if url:
            if not url.startswith(('http://', 'https://')):
                url = f"http://{url}"
            self.base_url = url
        return self.base_url
    
    async def login(self, gebruikersnaam, wachtwoord, url=None):
        """Log in bij RentPro exact zoals in het turboturbo script"""
        # Controleer inloggegevens
        if not gebruikersnaam or not wachtwoord:
            logger.logFout("Gebruikersnaam of wachtwoord ontbreekt")
            return False
        
        # Stel de basis URL in indien opgegeven
        if url:
            self.set_base_url(url)
        
        try:
            # Haal de driver op
            driver = self.driver_manager.get_driver()
            if not driver:
                logger.logFout("WebDriver niet geïnitialiseerd")
                return False
            
            # 1. Navigeer naar de RentPro pagina (exact zoals turboturbo script)
            logger.logInfo(f"Navigeren naar {self.base_url}")
            driver.get(self.base_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 2. Zoek en schakel over naar iframe indien aanwezig
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                logger.logInfo("Iframe gevonden, overschakelen naar iframe")
                driver.switch_to.frame(iframes[0])
            
            # 3. Vul gebruikersnaam in
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "UserName"))
            ).send_keys(gebruikersnaam)
            logger.logInfo("Gebruikersnaam ingevuld")
            
            # 4. Vul wachtwoord in
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Password"))
            ).send_keys(wachtwoord)
            logger.logInfo("Wachtwoord ingevuld")
            
            # 5. Klik op login knop
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Log in']"))
            ).click()
            logger.logInfo("Login knop geklikt")
            
            # 6. Wacht even voor pagina laden
            time.sleep(3)
            
            # 7. Controleer of login succesvol was
            if driver.find_elements(By.XPATH, "//*[contains(text(), 'Klanten vandaag online')]"):
                logger.logInfo("Succesvol ingelogd bij RentPro (Klanten vandaag online gevonden)")
                self.is_authenticated = True
                return True
            
            # Alternatieve controle
            success_indicators = ["Dashboard", "Welkom", "Uitloggen", "Logout", "Menu"]
            page_source = driver.page_source
            logged_in = any(indicator in page_source for indicator in success_indicators)
            
            if logged_in:
                logger.logInfo("Succesvol ingelogd bij RentPro (Alternatieve indicator gevonden)")
                self.is_authenticated = True
                return True
            
            logger.logFout("Login niet succesvol, kon niet verifiëren of we zijn ingelogd")
            return False
            
        except Exception as e:
            logger.logFout(f"Fout bij inloggen: {e}")
            return False
    
    def is_logged_in(self):
        """Controleer of we zijn ingelogd"""
        return self.is_authenticated
    
    def logout(self):
        """Uitloggen uit RentPro"""
        if not self.is_authenticated:
            return True  # Al uitgelogd
        
        driver = self.driver_manager.get_driver()
        if not driver:
            return False
        
        try:
            # Zoek en klik op uitlog link
            logout_elements = [
                "//a[contains(text(), 'Uitloggen')]",
                "//a[contains(text(), 'Logout')]",
                "//a[contains(@href, 'logout')]"
            ]
            
            for xpath in logout_elements:
                elements = driver.find_elements(By.XPATH, xpath)
                if elements:
                    elements[0].click()
                    logger.logInfo("Succesvol uitgelogd uit RentPro")
                    self.is_authenticated = False
                    return True
            
            # Als geen uitlog link gevonden, log dit
            logger.logInfo("Geen uitlog link gevonden, sessie wordt gesloten")
            self.is_authenticated = False
            return True
            
        except Exception as e:
            logger.logFout(f"Fout bij uitloggen: {e}")
            return False
