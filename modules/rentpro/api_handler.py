"""
RentPro API Handler - Browserloze implementatie voor RentPro integratie
Verantwoordelijk voor het communiceren met RentPro via directe HTTP requests
zonder afhankelijkheid van een browser

Deze module is de kern van de API-mode in de RentPro handler
"""
import asyncio
import re
import json
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
from modules.logger import logger

class ApiHandler:
    """
    Handler voor directe HTTP communicatie met RentPro
    Vermijdt browserafhankelijkheid door rechtstreeks HTTP-requests te gebruiken
    """
    
    def __init__(self):
        """Initialiseer de API handler"""
        self.session = requests.Session()
        self.base_url = "http://metroeventsdc.rentpro5.nl"
        self.logged_in = False
        self.csrf_token = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 Excelladin/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "nl,en-US;q=0.7,en;q=0.3",
            "Origin": "http://metroeventsdc.rentpro5.nl",
            "Connection": "keep-alive"
        }
    
    async def login(self, username, password, url=None):
        """
        Log in op RentPro via directe HTTP requests
        
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
                
            # Reset sessie voor schone start
            self.session = requests.Session()
            self.logged_in = False
            
            # Stap 1: Haal login pagina op voor verificatie token
            logger.logInfo("Login pagina ophalen...")
            login_url = f"{self.base_url}/Account/Login"
            
            response = self.session.get(login_url, headers=self.headers)
            if response.status_code != 200:
                logger.logFout(f"Fout bij ophalen login pagina: {response.status_code}")
                return False
            
            # Stap 2: Extracteer verificatie token
            soup = BeautifulSoup(response.text, 'html.parser')
            token_field = soup.select_one('input[name="__RequestVerificationToken"]')
            
            if not token_field:
                logger.logFout("Kon verificatie token niet vinden")
                return False
                
            token = token_field.get('value')
            if token:
                # Toon deel van token voor debug doeleinden
                masked_token = token[:10] + '...'
                logger.logInfo(f"Verificatie token gevonden: {masked_token}")
                self.csrf_token = token
            else:
                logger.logFout("Leeg verificatie token gevonden")
                return False
            
            # Stap 3: Verstuur login verzoek
            logger.logInfo("Login uitvoeren...")
            login_data = {
                "UserName": username,
                "Password": password,
                "__RequestVerificationToken": token
            }
            
            login_headers = self.headers.copy()
            login_headers.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": login_url
            })
            
            response = self.session.post(
                login_url,
                data=login_data,
                headers=login_headers,
                allow_redirects=True
            )
            
            # Debug: Sla response op
            with open("login_response.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            logger.logInfo("Response opgeslagen in login_response.html")
            
            # Stap 4: Controleer login status
            if "Logout" in response.text or "Uitloggen" in response.text:
                logger.logInfo("✅ LOGIN SUCCESVOL! (login indicator gevonden)")
                self.logged_in = True
                return True
            
            # Alternatieve success indicatoren
            success_indicators = ["Dashboard", "Welkom", "Menu", "Klanten vandaag online"]
            if any(indicator in response.text for indicator in success_indicators):
                logger.logInfo("✅ LOGIN SUCCESVOL! (alternatieve indicator gevonden)")
                self.logged_in = True
                return True
            
            # Login mislukt
            logger.logFout("❌ Login mislukt, geen success indicators gevonden")
            if "Incorrect" in response.text or "ongeld" in response.text.lower():
                logger.logFout("Foutmelding: ongeldige inloggegevens")
            return False
            
        except Exception as e:
            logger.logFout(f"Kritieke fout bij login: {e}")
            return False
    
    async def wait_on_product_page(self):
        """
        Controleert of we op de RentPro productpagina zijn en wacht op verdere acties
        
        Returns:
            bool: True als verificatie succesvol is, anders False
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.logInfo(f"[{timestamp}] [LOCATION] Verificatie van productpagina gestart")
            
            # Haal huidige pagina op
            products_url = f"{self.base_url}/Product"
            response = self.session.get(
                products_url,
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.logFout(f"[{timestamp}] [LOCATION] Fout bij verificatie productpagina: {response.status_code}")
                return False
            
            # Parse HTML en controleer op productpagina elementen
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Controleer op tabellen met class="grid"
            grid_tables = soup.select('table.grid')
            if not grid_tables:
                logger.logWaarschuwing(f"[{timestamp}] [LOCATION] Geen product tabellen gevonden")
                return False
                
            # Controleer op RentPro headers of menu-elementen
            rentpro_elements = soup.select('header .navbar') or soup.select('#main-menu') or soup.select('.rentpro-header')
            if not rentpro_elements:
                logger.logWaarschuwing(f"[{timestamp}] [LOCATION] Geen RentPro menu-elementen gevonden")
                return False
            
            # Controleer op productpagina specifieke elementen
            product_indicators = ["Product", "Producten", "Artikelen", "Artikelnummer"]
            page_text = soup.get_text()
            if not any(indicator in page_text for indicator in product_indicators):
                logger.logWaarschuwing(f"[{timestamp}] [LOCATION] Geen productpagina indicators gevonden")
                return False
            
            logger.logInfo(f"[{timestamp}] [LOCATION] ✅ Verificatie succesvol: We zijn op de productpagina")
            return True
            
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.logFout(f"[{timestamp}] [LOCATION] Fout bij verificatie productpagina: {e}")
            return False
    
    async def navigate_to_products(self, wait_after_navigation=False):
        """
        Navigeer naar de productenpagina via HTTP
        
        Args:
            wait_after_navigation (bool): Als True, blijf op de pagina na succesvolle navigatie
            
        Returns:
            bool: True bij success, anders False
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if not self.logged_in:
                logger.logFout(f"[{timestamp}] Niet ingelogd bij navigeren naar producten")
                return False
            
            # Navigeer naar producten pagina
            logger.logInfo(f"[{timestamp}] Navigeren naar productenpagina...")
            products_url = f"{self.base_url}/Product"
            response = self.session.get(
                products_url,
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.logFout(f"[{timestamp}] Fout bij navigeren naar producten: {response.status_code}")
                return False
            
            # Success
            logger.logInfo(f"[{timestamp}] ✅ Succesvol genavigeerd naar productenpagina")
            
            # Als wait_after_navigation is True, toon product informatie en wacht
            if wait_after_navigation:
                # Haal productlijst op
                products = await self.get_products_list()
                
                if products:
                    # Toon eerste drie en laatste drie producten
                    first_three = products[:3]
                    last_three = products[-3:] if len(products) > 3 else []
                    
                    logger.logInfo(f"[{timestamp}] Eerste drie producten:")
                    for product in first_three:
                        logger.logInfo(f"[{timestamp}]   - ID: {product['id']}, Naam: {product['naam']}")
                    
                    if last_three and last_three != first_three:
                        logger.logInfo(f"[{timestamp}] Laatste drie producten:")
                        for product in last_three:
                            logger.logInfo(f"[{timestamp}]   - ID: {product['id']}, Naam: {product['naam']}")
                
                # Verifieer dat we op de productpagina zijn
                is_on_product_page = await self.wait_on_product_page()
                
                if is_on_product_page:
                    logger.logInfo(f"[{timestamp}] [WAITING] Systeem staat klaar voor nieuwe instructies op productpagina")
                    logger.logInfo(f"[{timestamp}] [WAITING] Sessie blijft actief, wachtend op commando's...")
                else:
                    logger.logWaarschuwing(f"[{timestamp}] [WAITING] Kon niet bevestigen dat we op de productpagina zijn")
            
            return True
            
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.logFout(f"[{timestamp}] Fout bij navigeren naar producten: {e}")
            return False
    
    async def get_products_list(self):
        """
        Haal lijst van producten op via HTTP requests
        
        Returns:
            list: Lijst van producten als dictionaries met 'id' en 'naam' sleutels
        """
        try:
            if not self.logged_in:
                logger.logFout("Niet ingelogd bij ophalen productlijst")
                return []
            
            # Haal productlijst op
            products_url = f"{self.base_url}/Product"
            response = self.session.get(
                products_url,
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.logFout(f"Fout bij ophalen productlijst: {response.status_code}")
                return []
            
            # Parse HTML en zoek producten tabel
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Zoek de producten tabel (heeft class noBold gvItems)
            product_table = soup.select_one('table.gvItems')
            if not product_table:
                product_table = soup.select_one('table.noBold')
                if not product_table:
                    logger.logWaarschuwing("Geen producttabel gevonden in HTML")
                    return []
            
            # Zoek alle product rijen (alternating even/oneven classes)
            product_rows = product_table.select('tr.even, tr.oneven')
            if not product_rows:
                logger.logWaarschuwing("Geen productrijen gevonden in tabel")
                return []
            
            # Extraheer product IDs en namen
            products = []
            for row in product_rows:
                cells = row.select('td')
                if len(cells) >= 4:  # Zorg dat er genoeg kolommen zijn
                    # Eerste kolom (0) bevat ID, vierde kolom (3) bevat naam
                    product_id_cell = cells[0]
                    product_name_cell = cells[3]
                    
                    # Haal de waarden uit de cellen
                    # Merk op dat de ID/naam in een <a> tag kunnen zitten
                    product_id = product_id_cell.get_text(strip=True)
                    product_name = product_name_cell.get_text(strip=True)
                    
                    # Als er geen tekst is, probeer dan de inhoud van een <a> tag
                    if not product_id and product_id_cell.find('a'):
                        product_id = product_id_cell.find('a').get_text(strip=True)
                    
                    if not product_name and product_name_cell.find('a'):
                        product_name = product_name_cell.find('a').get_text(strip=True)
                    
                    if product_id and product_name:
                        products.append({
                            'id': product_id,
                            'naam': product_name
                        })
            
            logger.logInfo(f"{len(products)} producten gevonden")
            return products
            
        except Exception as e:
            logger.logFout(f"Fout bij ophalen productlijst: {e}")
            return []
    
    async def get_product_details(self, product_id):
        """
        Haal details van een specifiek product op via HTTP
        
        Args:
            product_id (str): ID van het product
            
        Returns:
            dict: Product gegevens of None bij fout
        """
        try:
            if not self.logged_in:
                logger.logFout("Niet ingelogd bij ophalen productdetails")
                return None
            
            # Haal productdetails op (probeer eerst Edit pagina, dan Details pagina)
            edit_url = f"{self.base_url}/Product/Edit/{product_id}"
            response = self.session.get(
                edit_url,
                headers=self.headers,
                allow_redirects=True
            )
            
            if response.status_code != 200:
                # Probeer de details pagina als edit niet werkt
                details_url = f"{self.base_url}/Product/Details/{product_id}"
                response = self.session.get(
                    details_url, 
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    logger.logFout(f"Fout bij ophalen productdetails: {response.status_code}")
                    return None
            
            # Parse HTML en extraheer productgegevens
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Zoek belangrijke velden op basis van id of label
            product_data = {
                'id': product_id,
                'naam': self._extract_input_value(soup, 'Product_Name') or self._extract_field_value(soup, "Naam"),
                'beschrijving': self._extract_input_value(soup, 'Product_Decription') or self._extract_field_value(soup, "Omschrijving"),
                'prijs': self._extract_input_value(soup, 'ProductPrice') or self._extract_field_value(soup, "Prijs") or "0.00",
                'categorie': self._extract_input_value(soup, 'Product_CategoryID') or self._extract_field_value(soup, "Categorie") or "Onbekend",
                'voorraad': self._extract_input_value(soup, 'Stock') or self._extract_field_value(soup, "Voorraad") or "0",
                'afbeelding_url': self._extract_image_url(soup),
                'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return product_data
            
        except Exception as e:
            logger.logFout(f"Fout bij ophalen productdetails voor {product_id}: {e}")
            return None
    
    def _extract_input_value(self, soup, input_id):
        """Helper methode om waarde van input veld te extraheren op basis van ID"""
        try:
            input_elem = soup.find('input', id=input_id)
            if input_elem and input_elem.has_attr('value'):
                return input_elem['value']
                
            # Probeer ook textarea
            textarea = soup.find('textarea', id=input_id)
            if textarea:
                return textarea.get_text(strip=True)
                
            # Probeer ook select
            select = soup.find('select', id=input_id)
            if select:
                selected_option = select.find('option', selected=True)
                if selected_option:
                    return selected_option.get_text(strip=True)
            
            return ""
        except Exception:
            return ""
    
    def _extract_field_value(self, soup, field_name):
        """Helper methode om veldwaarde te extraheren uit HTML"""
        try:
            # Zoek label met veldnaam
            label = soup.find('label', string=re.compile(field_name, re.IGNORECASE))
            if label and label.parent:
                # Vind de waarde in het volgende element of sibling
                value_elem = label.find_next('div') or label.find_next('span') or label.find_next('p')
                if value_elem:
                    return value_elem.get_text(strip=True)
            
            # Alternatieve methode: zoek in table met twee kolommen
            rows = soup.select('table tr')
            for row in rows:
                cells = row.select('td, th')
                if len(cells) >= 2 and field_name.lower() in cells[0].get_text().lower():
                    return cells[1].get_text(strip=True)
            
            return ""
        except Exception:
            return ""
    
    def _extract_image_url(self, soup):
        """Helper methode om afbeelding URL te extraheren"""
        try:
            # Zoek productafbeelding
            img = soup.select_one('img.product-image') or soup.select_one('.product-details img')
            if img and img.has_attr('src'):
                src = img['src']
                # Maak relatieve URL absoluut indien nodig
                if src.startswith('/'):
                    return f"{self.base_url}{src}"
                return src
            return ""
        except Exception:
            return ""
    
    def _get_current_datetime(self):
        """Helper methode om huidige datum en tijd te krijgen"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
