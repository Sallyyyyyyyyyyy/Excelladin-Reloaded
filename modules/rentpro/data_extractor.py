"""
Data Extractor voor RentPro integratie
Verantwoordelijk voor het extraheren van gegevens uit de RentPro interface
BELANGRIJK: In API-mode wordt deze module NIET gebruikt
"""
import asyncio
import json
import time
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from modules.logger import logger

class DataExtractor:
    """
    Extraheert data uit de RentPro interface via browser
    BELANGRIJK: Alleen gebruikt in browser mode, niet in API mode
    """
    
    def __init__(self, driver_manager, navigator):
        """
        Initialiseer de data extractor
        
        Args:
            driver_manager (DriverManager): De driver manager instantie
            navigator (Navigator): De navigator instantie
        """
        self.driver_manager = driver_manager
        self.navigator = navigator
        self.base_url = "http://metroeventsdc.rentpro5.nl"
    
    async def get_products_list(self):
        """
        Haal een lijst van alle producten op
        
        Returns:
            list: Een lijst van tuples (product_id, product_naam)
        """
        try:
            # Navigeer eerst naar de productenpagina
            navigate_success = await self.navigator.go_to_products()
            if not navigate_success:
                logger.logFout("Kon niet navigeren naar productenpagina")
                return []
            
            # Controleer of driver geïnitialiseerd is
            driver = self.driver_manager.get_driver()
            if not driver:
                logger.logFout("WebDriver niet geïnitialiseerd voor data extractie")
                return []
            
            # Creëer een future voor async werking
            future = asyncio.get_event_loop().create_future()
            
            def _extract_process():
                try:
                    with self.driver_manager.get_lock():
                        # Wacht tot de producten tabel is geladen
                        try:
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "table.grid"))
                            )
                        except Exception:
                            logger.logWaarschuwing("Kon producten tabel niet vinden")
                            future.set_result([])
                            return
                        
                        # Zoek alle productrijen
                        product_rows = driver.find_elements(By.CSS_SELECTOR, "table.grid tbody tr")
                        if not product_rows:
                            logger.logWaarschuwing("Geen productrijen gevonden")
                            future.set_result([])
                            return
                        
                        # Extraheer product IDs en namen
                        products = []
                        for row in product_rows:
                            try:
                                cells = row.find_elements(By.TAG_NAME, "td")
                                if len(cells) >= 2:
                                    product_id = cells[0].text.strip()
                                    product_name = cells[1].text.strip()
                                    if product_id and product_name:
                                        products.append((product_id, product_name))
                            except Exception as e:
                                logger.logWaarschuwing(f"Fout bij verwerken productrij: {e}")
                        
                        logger.logInfo(f"{len(products)} producten gevonden")
                        future.set_result(products)
                
                except Exception as e:
                    logger.logFout(f"Fout bij extractie productenlijst: {e}")
                    future.set_result([])
            
            # Start extractie in aparte thread
            thread = threading.Thread(target=_extract_process, daemon=True)
            thread.start()
            
            # Wacht op resultaat
            return await asyncio.wait_for(future, timeout=30)
        
        except Exception as e:
            logger.logFout(f"Fout bij ophalen productenlijst: {e}")
            return []
    
    async def get_product_details(self, product_id):
        """
        Haal details van een specifiek product op
        
        Args:
            product_id (str): ID van het product
            
        Returns:
            dict: Product gegevens of None bij fout
        """
        try:
            # Navigeer eerst naar de product details pagina
            navigate_success = await self.navigator.go_to_product_details(product_id)
            if not navigate_success:
                logger.logFout(f"Kon niet navigeren naar details voor product {product_id}")
                return None
            
            # Controleer of driver geïnitialiseerd is
            driver = self.driver_manager.get_driver()
            if not driver:
                logger.logFout("WebDriver niet geïnitialiseerd voor data extractie")
                return None
            
            # Creëer een future voor async werking
            future = asyncio.get_event_loop().create_future()
            
            def _extract_process():
                try:
                    with self.driver_manager.get_lock():
                        # Wacht tot de pagina is geladen
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        
                        # Extraheer gegevens uit formuliervelden of detailsvelden
                        product_data = {
                            'id': product_id,
                            'naam': self._extract_field_value(driver, "Naam"),
                            'beschrijving': self._extract_field_value(driver, "Beschrijving") or self._extract_field_value(driver, "Omschrijving"),
                            'prijs': self._extract_field_value(driver, "Prijs") or "0.00",
                            'categorie': self._extract_field_value(driver, "Categorie") or "Onbekend",
                            'voorraad': self._extract_field_value(driver, "Voorraad") or "0",
                            'afbeelding_url': self._extract_image_url(driver),
                            'last_updated': self._extract_field_value(driver, "Laatst bijgewerkt") or self._get_current_datetime()
                        }
                        
                        logger.logInfo(f"Details opgehaald voor product {product_id}")
                        future.set_result(product_data)
                
                except Exception as e:
                    logger.logFout(f"Fout bij extractie productdetails: {e}")
                    future.set_result(None)
            
            # Start extractie in aparte thread
            thread = threading.Thread(target=_extract_process, daemon=True)
            thread.start()
            
            # Wacht op resultaat
            return await asyncio.wait_for(future, timeout=30)
        
        except Exception as e:
            logger.logFout(f"Fout bij ophalen productdetails: {e}")
            return None
    
    def _extract_field_value(self, driver, field_name):
        """
        Helper methode om veldwaarde te extraheren uit het formulier
        
        Args:
            driver (WebDriver): Selenium driver instantie
            field_name (str): Naam van het veld om te zoeken
            
        Returns:
            str: Waarde van het veld of lege string
        """
        try:
            # Zoek labels met tekst
            label_xpath = f"//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{field_name.lower()}')]"
            labels = driver.find_elements(By.XPATH, label_xpath)
            
            if labels:
                # Zoek het bijbehorende invoerveld of waarde-element
                for label in labels:
                    # Probeer for-attribuut te gebruiken als het beschikbaar is
                    for_id = label.get_attribute("for")
                    if for_id:
                        # Zoek element met dit ID
                        try:
                            field = driver.find_element(By.ID, for_id)
                            value = field.get_attribute("value") or field.text
                            if value:
                                return value.strip()
                        except Exception:
                            pass
                    
                    # Zoek buurgelement
                    parent = label.find_element(By.XPATH, "./..")
                    siblings = parent.find_elements(By.XPATH, "./*")
                    for sibling in siblings:
                        if sibling != label:
                            value = sibling.get_attribute("value") or sibling.text
                            if value:
                                return value.strip()
            
            # Alternatieve zoekmethode: zoek in tabel
            rows_xpath = "//table//tr"
            rows = driver.find_elements(By.XPATH, rows_xpath)
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 2:
                    header_text = cells[0].text.lower()
                    if field_name.lower() in header_text:
                        return cells[1].text.strip()
            
            # Niets gevonden
            return ""
        except Exception:
            return ""
    
    def _extract_image_url(self, driver):
        """
        Helper methode om afbeelding URL te extraheren
        
        Args:
            driver (WebDriver): Selenium driver instantie
            
        Returns:
            str: URL van de productafbeelding of lege string
        """
        try:
            # Zoek productafbeelding
            img_selectors = ["img.product-image", ".product-details img", "img[alt*='product']"]
            for selector in img_selectors:
                try:
                    img = driver.find_element(By.CSS_SELECTOR, selector)
                    src = img.get_attribute("src")
                    if src:
                        return src
                except Exception:
                    continue
            
            # Geen afbeelding gevonden
            return ""
        except Exception:
            return ""
    
    def _get_current_datetime(self):
        """
        Helper methode om huidige datum en tijd te krijgen
        
        Returns:
            str: Huidige datum en tijd als string
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
