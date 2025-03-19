"""
Navigator voor RentPro integratie
Verantwoordelijk voor navigatie binnen RentPro en pagina-interactie
"""
import time
import asyncio
import threading
from selenium.webdriver.common.by import By
from modules.logger import logger

class Navigator:
    """
    Beheert de navigatie binnen RentPro
    Verantwoordelijk voor het verplaatsen tussen verschillende pagina's
    """
    
    def __init__(self, driver_manager, authenticator):
        """
        Initialiseer de navigator
        
        Args:
            driver_manager (DriverManager): Manager voor WebDriver operaties
            authenticator (Authenticator): Voor authenticatie en URL beheer
        """
        self.driver_manager = driver_manager
        self.authenticator = authenticator
        
    async def go_to_products(self):
        """
        Navigeer naar de productenpagina
        
        Returns:
            bool: True als navigatie succesvol was, anders False
        """
        # Controleer of ingelogd
        if not self.authenticator.is_logged_in():
            logger.logFout("Niet ingelogd bij RentPro")
            return False
            
        # Controleer of driver geïnitialiseerd is
        driver = self.driver_manager.get_driver()
        if not driver:
            logger.logFout("WebDriver niet geïnitialiseerd")
            return False
            
        # Maak een future om het resultaat van de thread terug te geven
        future = asyncio.get_event_loop().create_future()
        
        def _nav_process():
            try:
                # Gebruik lock voor thread safety
                with self.driver_manager.get_lock():
                    # Navigeer naar product pagina
                    product_url = f"{self.authenticator.base_url}/Product"
                    logger.logInfo(f"Navigeren naar productpagina: {product_url}")
                    
                    # Navigeer naar URL
                    driver.get(product_url)
                    
                    # Wacht tot pagina geladen is
                    self.driver_manager.wait_for_element(By.TAG_NAME, "body")
                    
                    # Wacht voor stabilisatie
                    logger.logInfo("Wachten op stabilisatie...")
                    time.sleep(3)
                    
                    # Controleer of we op de productpagina zijn - voor betrouwbaarheid meerdere checks
                    success = False
                    
                    # Poging 1: Controleer op het specifieke voorbeeldproduct
                    try:
                        product_check = driver.find_elements(
                            By.XPATH, "//*[contains(text(), 'dB DVA S1521N 21\" sub actief')]"
                        )
                        if product_check:
                            logger.logInfo("Specifiek voorbeeldproduct gevonden, navigatie succesvol")
                            success = True
                    except Exception:
                        logger.logWaarschuwing("Specifiek voorbeeldproduct niet gevonden, probeer alternatieve indicatoren")
                            
                    # Poging 2: Controleer op tekstindicatoren in de pagina
                    if not success:
                        page_source = driver.page_source.lower()
                        indicator_terms = ['product', 'artikel', 'item', 'inventaris', 'lijst']
                        indicators_found = [term for term in indicator_terms if term in page_source]
                        
                        if indicators_found:
                            logger.logInfo(f"Productpagina geladen op basis van tekstindicatoren: {', '.join(indicators_found)}")
                            success = True
                            
                    # Poging 3: Controleer op productlijst elementen
                    if not success:
                        try:
                            tables = driver.find_elements(By.TAG_NAME, "table")
                            product_tables = [
                                table for table in tables if 
                                ('product' in table.get_attribute('id').lower() if table.get_attribute('id') else False) or
                                ('product' in table.get_attribute('class').lower() if table.get_attribute('class') else False)
                            ]
                            
                            if product_tables:
                                logger.logInfo("Producttabel(len) gevonden, navigatie succesvol")
                                success = True
                        except Exception as e:
                            logger.logWaarschuwing(f"Kon geen producttabellen vinden: {e}")
                    
                    # Resultaat
                    if success:
                        future.set_result(True)
                    else:
                        logger.logFout("Kon productpagina niet herkennen na navigatie")
                        future.set_result(False)
            
            except Exception as e:
                logger.logFout(f"Fout bij navigeren naar productenpagina: {e}")
                future.set_result(False)
        
        # Start het navigatieproces in een aparte thread
        threading.Thread(target=_nav_process, daemon=True).start()
        
        try:
            # Wacht op het resultaat met timeout
            return await asyncio.wait_for(future, timeout=30)
        except asyncio.TimeoutError:
            logger.logFout("Timeout bij navigeren naar productenpagina")
            return False
        except Exception as e:
            logger.logFout(f"Fout bij navigeren naar productenpagina: {e}")
            return False
            
    async def go_to_product_detail(self, product_id):
        """
        Navigeer naar de detailpagina van een specifiek product
        
        Args:
            product_id (str): ID van het product
            
        Returns:
            bool: True als navigatie succesvol was, anders False
        """
        # Controleer of ingelogd
        if not self.authenticator.is_logged_in():
            logger.logFout("Niet ingelogd bij RentPro")
            return False
            
        # Controleer of driver geïnitialiseerd is
        driver = self.driver_manager.get_driver()
        if not driver:
            logger.logFout("WebDriver niet geïnitialiseerd")
            return False
            
        # Controleer of product ID is ingevuld
        if not product_id:
            logger.logFout("Product ID ontbreekt")
            return False
            
        # Maak een future om het resultaat van de thread terug te geven
        future = asyncio.get_event_loop().create_future()
        
        def _nav_process():
            try:
                # Gebruik lock voor thread safety
                with self.driver_manager.get_lock():
                    # Navigeer naar product detail pagina
                    product_url = f"{self.authenticator.base_url}/Product/Edit/{product_id}"
                    logger.logInfo(f"Navigeren naar product detail: {product_url}")
                    
                    # Navigeer naar URL
                    driver.get(product_url)
                    
                    # Wacht tot pagina geladen is
                    self.driver_manager.wait_for_element(By.TAG_NAME, "body")
                    
                    # Wacht voor stabilisatie
                    logger.logInfo("Wachten op stabilisatie...")
                    time.sleep(3)
                    
                    # Controleer of we op een product detail pagina zijn
                    success = False
                    page_source = driver.page_source.lower()
                    
                    # Controleer op termen die op een detailpagina zouden voorkomen
                    detail_indicators = ['bewerken', 'details', 'edit', 'eigenschappen', 'properties']
                    found_indicators = [indicator for indicator in detail_indicators if indicator in page_source]
                    
                    if found_indicators:
                        logger.logInfo(f"Product detailpagina geladen (indicators: {', '.join(found_indicators)})")
                        success = True
                    else:
                        # Controleer op formulierelementen die typisch zijn voor een detail pagina
                        form_elements = driver.find_elements(By.TAG_NAME, "form")
                        input_elements = driver.find_elements(By.TAG_NAME, "input")
                        
                        if form_elements and len(input_elements) > 3:  # Typisch voor een form
                            logger.logInfo("Product detailpagina geladen (formulier gedetecteerd)")
                            success = True
                    
                    # Resultaat
                    if success:
                        future.set_result(True)
                    else:
                        logger.logFout(f"Kon product detailpagina voor product {product_id} niet herkennen na navigatie")
                        future.set_result(False)
            
            except Exception as e:
                logger.logFout(f"Fout bij navigeren naar product detailpagina: {e}")
                future.set_result(False)
        
        # Start het navigatieproces in een aparte thread
        threading.Thread(target=_nav_process, daemon=True).start()
        
        try:
            # Wacht op het resultaat met timeout
            return await asyncio.wait_for(future, timeout=30)
        except asyncio.TimeoutError:
            logger.logFout("Timeout bij navigeren naar product detailpagina")
            return False
        except Exception as e:
            logger.logFout(f"Fout bij navigeren naar product detailpagina: {e}")
            return False
    
    async def go_to_dashboard(self):
        """
        Navigeer naar het dashboard / hoofdpagina
        
        Returns:
            bool: True als navigatie succesvol was, anders False
        """
        # Controleer of ingelogd
        if not self.authenticator.is_logged_in():
            logger.logFout("Niet ingelogd bij RentPro")
            return False
            
        # Controleer of driver geïnitialiseerd is
        driver = self.driver_manager.get_driver()
        if not driver:
            logger.logFout("WebDriver niet geïnitialiseerd")
            return False
            
        try:
            # Gebruik lock voor thread safety
            with self.driver_manager.get_lock():
                # Navigeer naar dashboard
                dashboard_url = self.authenticator.base_url
                logger.logInfo(f"Navigeren naar dashboard: {dashboard_url}")
                
                # Navigeer naar URL
                return self.driver_manager.navigate_to(dashboard_url)
        except Exception as e:
            logger.logFout(f"Fout bij navigeren naar dashboard: {e}")
            return False
