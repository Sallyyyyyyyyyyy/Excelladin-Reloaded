"""
Driver Manager voor RentPro integratie
Verantwoordelijk voor het initialiseren, beheren en sluiten van de WebDriver
Direct gebaseerd op het turboturbo script
"""
import time
import threading
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.logger import logger

class DriverManager:
    """
    Beheert de Selenium WebDriver instantie
    Implementatie is exact overgenomen van het turboturbo script
    """
    
    def __init__(self, timeout=15):
        """Initialiseer de Driver Manager"""
        self.driver = None
        self.timeout = timeout
        self._driver_lock = threading.Lock()  # Thread-safe toegang tot driver
        self.is_initialized = False
        
    async def initialize(self):
        """
        Initialiseer een nieuwe WebDriver sessie exact zoals in turboturbo script
        """
        # Sluit bestaande driver indien aanwezig
        await self.close()
        
        # Start een nieuwe driver in een aparte thread voor async compatibiliteit
        future = asyncio.get_event_loop().create_future()
        
        def _init_driver():
            try:
                # Chrome opties zoals in turboturbo script
                options = webdriver.ChromeOptions()
                options.add_argument("--ignore-certificate-errors")
                options.add_argument("--disable-web-security")
                options.add_argument("--allow-running-insecure-content")
                options.add_argument("--window-size=1600,1000")
                options.add_experimental_option("detach", True)  # Chrome blijft open voor debug
                options.add_argument("--remote-debugging-port=9222")  # Voor externe tools
                
                with self._driver_lock:
                    self.driver = webdriver.Chrome(options=options)
                    future.set_result(True)
            except Exception as e:
                future.set_exception(e)
        
        # Start de driver initialisatie in een aparte thread
        threading.Thread(target=_init_driver, daemon=True).start()
        
        try:
            # Wacht op het resultaat met timeout
            await asyncio.wait_for(future, timeout=30)
            logger.logInfo("WebDriver succesvol geïnitialiseerd")
            self.is_initialized = True
            return True
        except asyncio.TimeoutError:
            logger.logFout("Timeout bij initialiseren WebDriver")
            return False
        except Exception as e:
            logger.logFout(f"Fout bij initialiseren WebDriver: {e}")
            return False
    
    async def close(self):
        """Sluit de WebDriver sessie"""
        if self.driver:
            try:
                with self._driver_lock:
                    self.driver.quit()
                    self.driver = None
                    self.is_initialized = False
                logger.logInfo("WebDriver sessie gesloten")
                return True
            except Exception as e:
                logger.logFout(f"Fout bij sluiten WebDriver: {e}")
                return False
        return True
        
    def get_driver(self):
        """Verkrijg de WebDriver instantie"""
        return self.driver
    
    def get_lock(self):
        """Verkrijg het lock object voor thread-safety"""
        return self._driver_lock
    
    def wait_for_element(self, by, value, timeout=None):
        """Wacht op een element en geef het terug als het gevonden is"""
        if not self.driver:
            logger.logFout("WebDriver niet geïnitialiseerd")
            return None
            
        if timeout is None:
            timeout = self.timeout
            
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            logger.logWaarschuwing(f"Kon element {by}='{value}' niet vinden: {e}")
            return None
    
    def wait_for_clickable(self, by, value, timeout=None):
        """Wacht tot een element klikbaar is en geef het terug"""
        if not self.driver:
            logger.logFout("WebDriver niet geïnitialiseerd")
            return None
            
        if timeout is None:
            timeout = self.timeout
            
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except Exception as e:
            logger.logWaarschuwing(f"Kon klikbaar element {by}='{value}' niet vinden: {e}")
            return None
    
    def navigate_to(self, url):
        """Navigeer naar een specifieke URL"""
        if not self.driver:
            logger.logFout("WebDriver niet geïnitialiseerd")
            return False
            
        try:
            # Zorg dat URL correct geformatteerd is
            if not url.lower().startswith(('http://', 'https://')):
                url = f"http://{url}"
                
            logger.logInfo(f"Navigeren naar URL: {url}")
            self.driver.get(url)
            
            # Wacht tot de pagina geladen is
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.logInfo(f"Navigatie succesvol naar: {self.driver.current_url}")
            return True
        except Exception as e:
            logger.logFout(f"Fout bij navigeren naar {url}: {e}")
            return False
    
    def switch_to_iframe(self):
        """Zoek naar iframes op de pagina en schakel over naar de eerste indien gevonden"""
        if not self.driver:
            logger.logFout("WebDriver niet geïnitialiseerd")
            return False
            
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                logger.logInfo(f"Iframe gevonden, overschakelen naar iframe")
                self.driver.switch_to.frame(iframes[0])
                return True
            return False
        except Exception as e:
            logger.logFout(f"Fout bij overschakelen naar iframe: {e}")
            return False
            
    def switch_to_default_content(self):
        """Schakel terug naar de hoofdinhoud (uit iframes)"""
        if not self.driver:
            logger.logFout("WebDriver niet geïnitialiseerd")
            return False
            
        try:
            self.driver.switch_to.default_content()
            return True
        except Exception as e:
            logger.logFout(f"Fout bij overschakelen naar hoofdinhoud: {e}")
            return False
