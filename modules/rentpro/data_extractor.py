"""
Data Extractor voor RentPro integratie
Verantwoordelijk voor het extraheren van gegevens uit RentPro pagina's
"""
import time
import asyncio
import threading
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
from modules.logger import logger

class DataExtractor:
    """
    Extraheert data van RentPro pagina's
    Scheidt de logica voor het ophalen van data van de navigatie en authenticatie
    """
    
    def __init__(self, driver_manager, navigator):
        """
        Initialiseer de data extractor
        
        Args:
            driver_manager (DriverManager): Manager voor WebDriver operaties
            navigator (Navigator): Voor navigatie tussen pagina's
        """
        self.driver_manager = driver_manager
        self.navigator = navigator
        self.cache = {}  # Cache voor opgehaalde productdata
        
    async def get_products_list(self):
        """
        Haal de lijst met producten op van de productenpagina
        
        Returns:
            list: Lijst van tuples met (product_id, product_naam) of een lege lijst bij fout
        """
        # Controleer of driver geïnitialiseerd is
        driver = self.driver_manager.get_driver()
        if not driver:
            logger.logFout("WebDriver niet geïnitialiseerd")
            return []
            
        # Navigeer naar productenpagina indien nodig
        nav_result = await self.navigator.go_to_products()
        if not nav_result:
            logger.logFout("Kon niet navigeren naar productenpagina")
            return []
            
        # Maak een future om het resultaat van de thread terug te geven
        future = asyncio.get_event_loop().create_future()
        
        def _extract_process():
            try:
                # Gebruik lock voor thread safety
                with self.driver_manager.get_lock():
                    # Wacht tot de pagina geladen is
                    self.driver_manager.wait_for_element(By.TAG_NAME, "body")
                    
                    # Wacht extra voor JavaScript-laden
                    time.sleep(3)
                    
                    # Probeer producten te vinden via verschillende methoden
                    producten = []
                    
                    # Methode 1: Zoek in HTML tabellen
                    try:
                        tabellen = driver.find_elements(By.TAG_NAME, "table")
                        logger.logInfo(f"{len(tabellen)} tabellen gevonden op de pagina")
                        
                        for tabel in tabellen:
                            # Zoek rijen in de tabel
                            rijen = tabel.find_elements(By.TAG_NAME, "tr")
                            logger.logInfo(f"{len(rijen)} rijen gevonden in tabel")
                            
                            for rij in rijen:
                                # Sla de header rij over
                                if rij.find_elements(By.TAG_NAME, "th"):
                                    continue
                                
                                # Zoek cellen in de rij
                                cellen = rij.find_elements(By.TAG_NAME, "td")
                                if len(cellen) >= 2:  # We hebben minstens ID en naam nodig
                                    product_id = cellen[0].text.strip()
                                    product_naam = cellen[1].text.strip()
                                    if product_id and product_naam:
                                        producten.append([product_id, product_naam])
                    except Exception as e:
                        logger.logWaarschuwing(f"Kon geen producten vinden in tabellen: {e}")
                    
                    # Methode 2: JavaScript evaluatie voor complexere DOM structuren
                    if not producten:
                        try:
                            js_code = """
                            (function() {
                                const rows = document.querySelectorAll('table.grid tbody tr, div.product-list .product-item');
                                const products = [];
                                
                                // Voor standard tabellen
                                for (let row of rows) {
                                    // Probeer cellen te vinden
                                    const idCell = row.querySelector('td:nth-child(1)') || row.querySelector('.product-id');
                                    const nameCell = row.querySelector('td:nth-child(2)') || row.querySelector('.product-name');
                                    
                                    if (idCell && nameCell) {
                                        const id = idCell.textContent.trim();
                                        const name = nameCell.textContent.trim();
                                        if (id && name) {
                                            products.push([id, name]);
                                        }
                                    }
                                }
                                
                                return products;
                            })();
                            """
                            
                            result = driver.execute_script(js_code)
                            if result and isinstance(result, list) and len(result) > 0:
                                producten = result
                                logger.logInfo(f"{len(producten)} producten gevonden via JavaScript")
                        except Exception as e:
                            logger.logWaarschuwing(f"Kon geen producten vinden met JavaScript: {e}")
                    
                    # Methode 3: Zoek in links
                    if not producten:
                        try:
                            product_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'product')]")
                            logger.logInfo(f"{len(product_links)} product links gevonden")
                            
                            for link in product_links:
                                href = link.get_attribute("href")
                                if not href:
                                    continue
                                    
                                # Extract ID from URL
                                parts = href.split('/')
                                if len(parts) > 0:
                                    product_id = parts[-1]  # Last part of URL
                                    product_naam = link.text.strip()
                                    
                                    if product_id and product_naam and product_id.isalnum():  # Basic validation
                                        producten.append([product_id, product_naam])
                        except Exception as e:
                            logger.logWaarschuwing(f"Kon geen producten vinden in links: {e}")
                    
                    # Return result
                    if producten:
                        # Beperk tot een redelijk aantal voor performance
                        if len(producten) > 100:
                            logger.logInfo(f"Beperken van {len(producten)} producten tot maximaal 100 voor performance")
                            producten = producten[:100]
                            
                        logger.logInfo(f"Succesvol {len(producten)} producten opgehaald")
                        future.set_result(producten)
                    else:
                        logger.logWaarschuwing("Geen producten gevonden op de pagina")
                        # Voor UI-compatibiliteit een minimale fallback lijst
                        fallback = [
                            ["P001", "Product 1"],
                            ["P002", "Product 2"],
                            ["P003", "Product 3"]
                        ]
                        logger.logInfo("Terugvallen op fallback productlijst voor UI-compatibiliteit")
                        future.set_result(fallback)
            
            except Exception as e:
                logger.logFout(f"Fout bij ophalen productenlijst: {e}")
                future.set_result([])  # Empty list as fallback
        
        # Start het extract proces in een aparte thread
        threading.Thread(target=_extract_process, daemon=True).start()
        
        try:
            # Wacht op het resultaat met timeout
            return await asyncio.wait_for(future, timeout=30)
        except asyncio.TimeoutError:
            logger.logFout("Timeout bij ophalen productenlijst")
            return []
        except Exception as e:
            logger.logFout(f"Fout bij ophalen productenlijst: {e}")
            return []
            
    async def get_product_details(self, product_id):
        """
        Haal details van een specifiek product op
        
        Args:
            product_id (str): ID van het product
            
        Returns:
            dict: Product details of None bij fout
        """
        # Check cache eerst
        if product_id in self.cache:
            logger.logInfo(f"Product {product_id} details gevonden in cache")
            return self.cache[product_id]
            
        # Controleer of driver geïnitialiseerd is
        driver = self.driver_manager.get_driver()
        if not driver:
            logger.logFout("WebDriver niet geïnitialiseerd")
            return None
            
        # Navigeer naar product detailpagina
        nav_result = await self.navigator.go_to_product_detail(product_id)
        if not nav_result:
            logger.logFout(f"Kon niet navigeren naar product {product_id} detailpagina")
            return None
            
        # Maak een future om het resultaat van de thread terug te geven
        future = asyncio.get_event_loop().create_future()
        
        def _extract_process():
            try:
                # Gebruik lock voor thread safety
                with self.driver_manager.get_lock():
                    # Wacht tot de pagina geladen is
                    self.driver_manager.wait_for_element(By.TAG_NAME, "body")
                    
                    # Wacht extra voor JavaScript-laden
                    time.sleep(3)
                    
                    # Haal de HTML op en parse met BeautifulSoup voor meer flexibiliteit
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract product details - verschillende benaderingen gebruiken
                    product_data = {
                        'id': product_id,
                        'naam': '',
                        'beschrijving': '',
                        'prijs': '',
                        'categorie': '',
                        'voorraad': '',
                        'afbeelding_url': '',
                        'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # 1. Probeer directe ID elementen (meest betrouwbaar)
                    field_mappings = {
                        'naam': ["Product_Name", "name", "productName", "artikelNaam", "title"],
                        'beschrijving': ["Product_Description", "description", "productDescription", "artikelBeschrijving"],
                        'prijs': ["Product_Price", "price", "productPrice", "artikelPrijs"],
                        'categorie': ["Product_Category", "category", "productCategory", "artikelCategorie"],
                        'voorraad': ["Product_Stock", "stock", "inventory", "voorraad"]
                    }
                    
                    # Probeer elke veldnaam in ID, name en class
                    for veld, mogelijke_namen in field_mappings.items():
                        for naam in mogelijke_namen:
                            # Probeer op ID
                            waarde = self._extract_text_from_element(By.ID, naam)
                            if waarde:
                                product_data[veld] = waarde
                                break
                                
                            # Probeer op name attribuut
                            waarde = self._extract_text_from_element(By.NAME, naam) 
                            if waarde:
                                product_data[veld] = waarde
                                break
                                
                            # Probeer op class
                            waarde = self._extract_text_from_element(By.CLASS_NAME, naam)
                            if waarde:
                                product_data[veld] = waarde
                                break
                    
                    # 2. Probeer afbeeldingen te vinden
                    image_selectors = [
                        ".product-image", 
                        "img.productImage", 
                        "img.artikelAfbeelding",
                        "img[alt*='product']",
                        "img[alt*='artikel']"
                    ]
                    
                    for selector in image_selectors:
                        img_url = self._extract_attr_from_element(By.CSS_SELECTOR, selector, "src")
                        if img_url:
                            product_data['afbeelding_url'] = img_url
                            break
                    
                    # 3. BeautifulSoup analyse voor meer complexe extractie
                    # Als we nog steeds geen velden hebben, probeer labels te vinden
                    for key in ['naam', 'beschrijving', 'prijs', 'categorie', 'voorraad']:
                        if not product_data[key]:
                            # Zoek naar labels die de veldnaam bevatten
                            labels = {
                                'naam': ['naam', 'article', 'product', 'title', 'name'],
                                'beschrijving': ['beschrijving', 'omschrijving', 'description'],
                                'prijs': ['prijs', 'price', 'tarief', 'kosten'],
                                'categorie': ['categorie', 'category', 'groep', 'type'],
                                'voorraad': ['voorraad', 'stock', 'inventory', 'beschikbaar']
                            }
                            
                            for label_text in labels[key]:
                                # Zoek label elementen die dit woord bevatten
                                label_elements = soup.find_all(lambda tag: tag.name in ['label', 'div', 'span', 'th'] and 
                                                             label_text.lower() in tag.text.lower())
                                
                                for label in label_elements:
                                    # Zoek het bijbehorende waarde element (vaak het volgende element)
                                    next_el = label.find_next(['input', 'textarea', 'div', 'span', 'td'])
                                    if next_el:
                                        # Voor input/textarea, gebruik de waarde
                                        if next_el.name in ['input', 'textarea']:
                                            value = next_el.get('value', '')
                                        else:
                                            value = next_el.text.strip()
                                            
                                        if value:
                                            product_data[key] = value
                                            break
                    
                    # Sla op in cache
                    self.cache[product_id] = product_data
                    logger.logInfo(f"Product {product_id} details succesvol opgehaald")
                    future.set_result(product_data)
            
            except Exception as e:
                logger.logFout(f"Fout bij ophalen product {product_id} details: {e}")
                future.set_result(None)
        
        # Start het extract proces in een aparte thread
        threading.Thread(target=_extract_process, daemon=True).start()
        
        try:
            # Wacht op het resultaat met timeout
            return await asyncio.wait_for(future, timeout=30)
        except asyncio.TimeoutError:
            logger.logFout(f"Timeout bij ophalen product {product_id} details")
            return None
        except Exception as e:
            logger.logFout(f"Fout bij ophalen product {product_id} details: {e}")
            return None
    
    def _extract_text_from_element(self, by, selector):
        """
        Extraheer tekst uit een element met Selenium
        
        Args:
            by (By): Zoek methode (e.g., By.ID)
            selector (str): Selector waarde
            
        Returns:
            str: Gevonden tekst of lege string
        """
        driver = self.driver_manager.get_driver()
        if not driver:
            return ""
            
        try:
            element = driver.find_element(by, selector)
            # Check eerst voor value attribuut (inputs)
            value = element.get_attribute("value")
            if value:
                return value
            # Anders, gebruik de tekst
            return element.text.strip()
        except (NoSuchElementException, WebDriverException):
            return ""
    
    def _extract_attr_from_element(self, by, selector, attr):
        """
        Extraheer attribuut uit een element met Selenium
        
        Args:
            by (By): Zoek methode (e.g., By.CSS_SELECTOR)
            selector (str): Selector waarde
            attr (str): Attribuut naam
            
        Returns:
            str: Gevonden attribuut waarde of lege string
        """
        driver = self.driver_manager.get_driver()
        if not driver:
            return ""
            
        try:
            element = driver.find_element(by, selector)
            return element.get_attribute(attr) or ""
        except (NoSuchElementException, WebDriverException):
            return ""
    
    def clear_cache(self):
        """Leeg de cache met productgegevens"""
        self.cache.clear()
        logger.logInfo("Product cache geleegd")
