"""
Sterk vereenvoudigde RentPro handler gebaseerd op het werkende turboturbo script
"""
import time
import asyncio
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.logger import logger

class MinimalRentproHandler:
    """Minimale klasse voor testen, rechtstreeks gebaseerd op werkende turboturbo script"""
    
    def __init__(self):
        """Initialiseer de minimale RentPro handler"""
        self.driver = None
        self.ingelogd = False
        self.url = "http://metroeventsdc.rentpro5.nl"
    
    async def test_login(self):
        """Test login functionaliteit met exacte waarden van turboturbo script"""
        
        # Start een nieuwe Chrome browser
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--window-size=1600,1000")
        options.add_experimental_option("detach", True)  # ✅ Chrome blijft open
        options.add_argument("--remote-debugging-port=9222")  # ✅ Nodig voor script 2
        
        try:
            # Start browser
            logger.logInfo("Browser starten...")
            self.driver = webdriver.Chrome(options=options)
            
            # Navigeer naar de URL
            logger.logInfo(f"Navigeren naar {self.url}")
            self.driver.get(self.url)
            
            # Wacht op het laden van de pagina
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Controleer op iframes en switch
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                logger.logInfo(f"Iframe gevonden, overschakelen...")
                self.driver.switch_to.frame(iframes[0])
            
            # Vul gebruikersnaam in
            logger.logInfo("Gebruikersnaam invullen...")
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "UserName"))
            )
            username_field.send_keys("sally")
            
            # Vul wachtwoord in
            logger.logInfo("Wachtwoord invullen...")
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Password"))
            )
            password_field.send_keys("e7VBPymQ")
            
            # Klik op login knop
            logger.logInfo("Login knop klikken...")
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Log in']"))
            )
            login_button.click()
            
            # Wacht even
            time.sleep(3)
            
            # Controleer of we zijn ingelogd
            if self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Klanten vandaag online')]"):
                logger.logInfo("✅ Succesvol ingelogd")
                self.ingelogd = True
                
                # Ga naar productpagina
                logger.logInfo("Navigeren naar productpagina...")
                self.driver.get(f"{self.url}/Product")
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # Wacht op stabilisatie
                time.sleep(3)
                
                # Controleer of we op de productpagina zijn
                try:
                    product_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'dB DVA S1521N 21\" sub actief')]"))
                    )
                    logger.logInfo("✅ Productpagina succesvol geladen")
                    return True
                except Exception as e:
                    logger.logFout(f"Kon niet verifiëren of we op de productpagina zijn: {e}")
                    return False
            else:
                logger.logFout("Login niet succesvol. Kon 'Klanten vandaag online' niet vinden.")
                return False
            
        except Exception as e:
            logger.logFout(f"Fout tijdens test: {e}")
            return False
        finally:
            # Browser open laten, zoals in turboturbo script
            logger.logInfo("Browser blijft open voor inspectie")

# Functie om het script te testen
async def test():
    handler = MinimalRentproHandler()
    result = await handler.test_login()
    print(f"Test resultaat: {'SUCCES' if result else 'FOUT'}")

# Direct uitvoeren bij aanroepen script
if __name__ == "__main__":
    print("Minimale RentPro test wordt uitgevoerd...")
    asyncio.run(test())
