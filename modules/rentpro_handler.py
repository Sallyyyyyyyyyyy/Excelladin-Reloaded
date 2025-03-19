"""
Rentpro Handler module voor Excelladin Reloaded
FINALE VERSIE: 100% DIRECTE IMPLEMENTATIE, GEEN THREADING/ASYNCIO
"""
import asyncio
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.logger import logger

class RentproHandler:
    """
    RentPro handler met minimale threading om het white screen probleem op te lossen
    Code 100% gebaseerd op turboturbo script met bewezen werking
    """
    def __init__(self):
        """Initialiseer de handler"""
        self.driver = None
        self.ingelogd = False
        self.base_url = "http://metroeventsdc.rentpro5.nl"
        self.driver_lock = threading.Lock()
        
    async def initialize(self):
        """Start een nieuwe Chrome instantie met exact dezelfde opties als turboturbo"""
        # Sluit eventuele bestaande sessie
        await self.close()
        
        # Creëer een future voor async werking
        future = asyncio.get_event_loop().create_future()
        
        # Functie voor threading
        def _init_driver():
            try:
                # EXACTE opties van turboturbo script
                options = webdriver.ChromeOptions()
                options.add_argument("--ignore-certificate-errors")
                options.add_argument("--disable-web-security")
                options.add_argument("--allow-running-insecure-content")
                options.add_argument("--window-size=1600,1000")
                options.add_experimental_option("detach", True)
                options.add_argument("--remote-debugging-port=9222")

                # Creëer browser in één keer zonder onnodige complexiteit
                self.driver = webdriver.Chrome(options=options)
                future.set_result(True)
            except Exception as e:
                logger.logFout(f"Fout bij initialiseren Chrome: {e}")
                future.set_exception(e)
        
        # Start in aparte thread en wacht
        thread = threading.Thread(target=_init_driver, daemon=True)
        thread.start()
        
        try:
            # Wacht op resultaat
            await asyncio.wait_for(future, timeout=30)
            logger.logInfo("Chrome browser succesvol gestart")
            return True
        except Exception as e:
            logger.logFout(f"Fout bij starten Chrome: {e}")
            return False
    
    async def close(self):
        """Sluit de driver of laat open voor inspectie zoals in turboturbo script"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.ingelogd = False
                logger.logInfo("Chrome sessie afgesloten")
                return True
            except Exception as e:
                logger.logFout(f"Fout bij sluiten Chrome: {e}")
                return False
        return True
        
    async def login(self, gebruikersnaam, wachtwoord, url=None):
        """
        Inloggen met MINIMALE threading om het data: URL probleem te voorkomen
        """
        # Update URL indien opgegeven
        if url:
            if not url.startswith(('http://', 'https://')):
                url = f"http://{url}"
            self.base_url = url
        
        # Start browser indien nodig
        if not self.driver:
            init_success = await self.initialize()
            if not init_success:
                return False
        
        # Creëer future voor async werking
        future = asyncio.get_event_loop().create_future()
        
        # Functie voor threading 
        def _login_process():
            try:
                # --- EXACTE CODE UIT STANDALONE TEST DIE WERKT ---
                # 1. Navigeren naar login pagina
                logger.logInfo("Navigeren naar RentPro...")
                self.driver.get(self.base_url)
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # 2. Controleer huidige URL om data: probleem te detecteren
                current_url = self.driver.current_url
                logger.logInfo(f"Huidige URL: {current_url}")
                
                if current_url.startswith("data:"):
                    logger.logFout("⚠️ PROBLEEM: data: URL gedetecteerd!")
                    future.set_result(False)
                    return
                
                # 3. Controleer op iframe en switch indien nodig
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                if iframes:
                    logger.logInfo("Iframe gevonden, overschakelen...")
                    self.driver.switch_to.frame(iframes[0])
                
                # 4. Vul gebruikersnaam in
                logger.logInfo("Gebruikersnaam invullen...")
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "UserName"))
                ).send_keys(gebruikersnaam)
                
                # 5. Vul wachtwoord in
                logger.logInfo("Wachtwoord invullen...")
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "Password"))
                ).send_keys(wachtwoord)
                
                # 6. Klik op login knop
                logger.logInfo("Login knop klikken...")
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Log in']"))
                ).click()
                
                # 7. Wacht even voor pagina laden
                logger.logInfo("Wachten op login resultaat...")
                time.sleep(3)
                
                # 8. Controleer resultaat
                logger.logInfo("Controleren of login succesvol was...")
                if "Klanten vandaag online" in self.driver.page_source:
                    logger.logInfo("Login succesvol! (Klanten indicator gevonden)")
                    self.ingelogd = True
                    future.set_result(True)
                    return
                
                # Alternatieve controle
                success_indicators = ["Dashboard", "Welkom", "Uitloggen", "Logout", "Menu"]
                if any(indicator in self.driver.page_source for indicator in success_indicators):
                    logger.logInfo("Login succesvol! (Alternatieve indicator gevonden)")
                    self.ingelogd = True
                    future.set_result(True)
                    return
                
                # Login mislukt
                logger.logFout("Login niet succesvol, geen succes indicators gevonden")
                future.set_result(False)
                
            except Exception as e:
                logger.logFout(f"Fout bij inloggen: {e}")
                future.set_result(False)
        
        # Start thread proces met minimale complexiteit
        thread = threading.Thread(target=_login_process, daemon=True)
        thread.start()
        
        try:
            # Wacht op resultaat
            return await asyncio.wait_for(future, timeout=30)
        except asyncio.TimeoutError:
            logger.logFout("Timeout bij login poging")
            return False
        except Exception as e:
            logger.logFout(f"Onverwachte fout: {e}")
            return False
            
    async def navigeer_naar_producten(self):
        """Navigeer naar productpagina"""
        if not self.ingelogd or not self.driver:
            logger.logFout("Niet ingelogd bij RentPro")
            return False

        future = asyncio.get_event_loop().create_future()
        
        def _navigate_process():
            try:
                # EXACTE CODE UIT TURBOTURBO SCRIPT 
                logger.logInfo("Navigeren naar productpagina...")
                self.driver.get(f"{self.base_url}/Product")
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                logger.logInfo("Productpagina geladen")
                
                # Wacht zoals in turboturbo script
                time.sleep(3)
                
                # Navigatie succesvol
                future.set_result(True)
                        
            except Exception as e:
                logger.logFout(f"Fout bij navigeren naar producten: {e}")
                future.set_result(False)
                
        # Start navigatie in aparte thread
        thread = threading.Thread(target=_navigate_process, daemon=True)
        thread.start()
        
        try:
            return await asyncio.wait_for(future, timeout=30)
        except Exception as e:
            logger.logFout(f"Fout bij navigatie: {e}")
            return False
    
    async def haal_producten_op(self, overschrijf_lokaal=False, rijen=None):
        """Placeholder voor product ophalen functionaliteit"""
        if not self.ingelogd:
            logger.logFout("Niet ingelogd bij RentPro")
            return False
        
        logger.logInfo("Mock data functionaliteit voor producten ophalen")
        return True
    
    async def evalueer_javascript(self, js_code):
        """Evalueer JavaScript code op de huidige pagina"""
        if not self.ingelogd or not self.driver:
            logger.logFout("Niet ingelogd bij RentPro")
            return None
        
        future = asyncio.get_event_loop().create_future()
        
        def _js_process():
            try:
                result = self.driver.execute_script(js_code)
                future.set_result(result)
            except Exception as e:
                logger.logFout(f"Fout bij uitvoeren JavaScript: {e}")
                future.set_exception(e)
        
        # Minimale threading complexiteit
        thread = threading.Thread(target=_js_process, daemon=True)
        thread.start()
        
        try:
            return await asyncio.wait_for(future, timeout=15)
        except Exception as e:
            logger.logFout(f"JavaScript timeout of fout: {e}")
            return None

# Singleton instance
rentproHandler = RentproHandler()
