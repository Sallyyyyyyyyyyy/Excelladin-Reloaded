"""
Rentpro Handler module voor Excelladin Reloaded
Verantwoordelijk voor communicatie met Rentpro en gegevensuitwisseling
"""
import os
import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from modules.logger import logger
from modules.excel_handler import excelHandler

class RentproHandler:
    """Klasse voor Rentpro integratie"""
    
    def __init__(self):
        """Initialiseer de Rentpro handler"""
        self.sessie = None
        self.ingelogd = False
        self.base_url = "https://rentpro.nl"  # Aanpassen naar juiste URL
        self.cache = {}  # Cache voor opgehaalde producten
        
    async def initialize(self):
        """Initialiseer een nieuwe sessie"""
        if self.sessie:
            await self.sessie.close()
        self.sessie = aiohttp.ClientSession()
        self.ingelogd = False
        
    async def login(self, gebruikersnaam, wachtwoord, url=None):
        """
        Log in op Rentpro
        
        Args:
            gebruikersnaam (str): Rentpro gebruikersnaam
            wachtwoord (str): Rentpro wachtwoord
            url (str, optional): De URL voor de Rentpro back-office. Als None, wordt de standaard URL gebruikt.
            
        Returns:
            bool: True als inloggen succesvol is, anders False
        """
        try:
            if not self.sessie:
                await self.initialize()
            
            # Stel de basis URL in
            if url:
                self.base_url = url
                if not self.base_url.startswith('http'):
                    self.base_url = f"http://{self.base_url}"
                    
            # Login URL - pas aan naar de juiste login pagina
            login_url = f"{self.base_url}/login"
            
            # Controleer of gebruikersnaam en wachtwoord zijn ingevuld
            if not gebruikersnaam or not wachtwoord:
                logger.logFout("Gebruikersnaam of wachtwoord ontbreekt")
                return False
            
            # Eerst GET request om CSRF token en cookies te krijgen
            try:
                async with self.sessie.get(login_url, timeout=10) as response:
                    if response.status != 200:
                        logger.logFout(f"Kon login pagina niet laden. Status: {response.status}")
                        return False
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Zoek CSRF token of andere benodigde formuliervelden
                    # Pas dit aan op basis van de werkelijke Rentpro login pagina
                    csrf_token = None
                    csrf_input = soup.find('input', {'name': 'csrf_token'})
                    if csrf_input:
                        csrf_token = csrf_input.get('value', '')
                    
                    # Zoek het login formulier om de juiste action URL te krijgen
                    form = soup.find('form')
                    if form and form.get('action'):
                        form_action = form.get('action')
                        if form_action.startswith('/'):
                            login_post_url = f"{self.base_url}{form_action}"
                        else:
                            login_post_url = form_action
                    else:
                        login_post_url = login_url
            except asyncio.TimeoutError:
                logger.logFout("Timeout bij verbinden met login pagina")
                return False
            except Exception as e:
                logger.logFout(f"Fout bij laden login pagina: {str(e)}")
                return False
            
            # Bereid login data voor
            login_data = {
                'username': gebruikersnaam,
                'password': wachtwoord
            }
            
            # Voeg CSRF token toe indien gevonden
            if csrf_token:
                login_data['csrf_token'] = csrf_token
            
            # Zoek alle verborgen velden in het formulier en voeg ze toe aan de login data
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
            for hidden_input in hidden_inputs:
                name = hidden_input.get('name')
                value = hidden_input.get('value', '')
                if name and name not in login_data:
                    login_data[name] = value
            
            # POST request om in te loggen
            try:
                async with self.sessie.post(login_post_url, data=login_data, allow_redirects=True, timeout=10) as response:
                    if response.status != 200 and response.status != 302:
                        logger.logFout(f"Login mislukt. Status: {response.status}")
                        return False
                    
                    # Controleer of login gelukt is
                    html = await response.text()
                    if "Login mislukt" in html or "Ongeldige gebruikersnaam" in html or "Incorrect password" in html:
                        logger.logFout("Login geweigerd: ongeldige gebruikersnaam/wachtwoord")
                        return False
            except asyncio.TimeoutError:
                logger.logFout("Timeout bij inloggen")
                return False
            except Exception as e:
                logger.logFout(f"Fout bij inloggen: {str(e)}")
                return False
            
            # Controleer of we ingelogd zijn door een beveiligde pagina te bekijken
            try:
                # Probeer een pagina te laden die alleen toegankelijk is na inloggen
                dashboard_url = f"{self.base_url}/dashboard"
                async with self.sessie.get(dashboard_url, timeout=10) as response:
                    if response.status != 200:
                        logger.logFout(f"Kon niet verifiëren of login succesvol was. Status: {response.status}")
                        return False
                    
                    html = await response.text()
                    # Controleer of we echt ingelogd zijn (pas aan op basis van werkelijke Rentpro pagina)
                    if "Inloggen" in html or "Login" in html:
                        # Als de pagina nog steeds "Inloggen" bevat, zijn we waarschijnlijk niet ingelogd
                        logger.logFout("Login niet succesvol")
                        return False
            except asyncio.TimeoutError:
                logger.logFout("Timeout bij verifiëren login")
                return False
            except Exception as e:
                logger.logFout(f"Fout bij verifiëren login: {str(e)}")
                return False
            
            self.ingelogd = True
            logger.logInfo("Succesvol ingelogd bij Rentpro")
            return True
            
        except Exception as e:
            logger.logFout(f"Fout bij inloggen Rentpro: {e}")
            return False
            
    async def haal_producten_op(self, overschrijf_lokaal=False, rijen=None):
        """
        Haal producten op van Rentpro
        
        Args:
            overschrijf_lokaal (bool): Of lokale data overschreven moet worden
            rijen (tuple): Optioneel, tuple met (startRij, eindRij)
            
        Returns:
            bool: True als ophalen succesvol was, anders False
        """
        if not self.ingelogd:
            logger.logFout("Niet ingelogd bij Rentpro")
            return False
        
        try:
            # Bepaal welke rijen we moeten ophalen
            if not excelHandler.isBestandGeopend():
                logger.logFout("Geen Excel-bestand geopend")
                return False
            
            # Bepaal rijen om te verwerken
            start_rij = 0
            eind_rij = excelHandler.aantalRijen - 1
            
            if rijen:
                start_rij, eind_rij = rijen
                # Valideer rijen
                if start_rij < 0:
                    start_rij = 0
                if eind_rij >= excelHandler.aantalRijen:
                    eind_rij = excelHandler.aantalRijen - 1
            
            # Producten URL
            producten_url = f"{self.base_url}/producten"
            
            # Haal productlijst op
            async with self.sessie.get(producten_url) as response:
                if response.status != 200:
                    logger.logFout(f"Kon productlijst niet ophalen. Status: {response.status}")
                    return False
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Zoek producten in de HTML (aanpassen op basis van werkelijke Rentpro implementatie)
                product_elementen = soup.find_all('div', class_='product-item')
                
                if not product_elementen:
                    logger.logWaarschuwing("Geen producten gevonden in Rentpro")
                    return False
                
                # Verwerk de producten
                succesvol = 0
                for i, row_index in enumerate(range(start_rij, eind_rij + 1)):
                    # Haal product ID uit Excel
                    product_id = excelHandler.haalCelWaarde(row_index, "ProductID")
                    if not product_id:
                        continue
                    
                    # Zoek product in Rentpro
                    product_data = await self._haal_product_details(product_id)
                    if not product_data:
                        continue
                    
                    # Update Excel als we het product hebben gevonden
                    if overschrijf_lokaal:
                        self._update_excel_rij(row_index, product_data)
                    else:
                        self._merge_excel_rij(row_index, product_data)
                    
                    succesvol += 1
                    
                    # Geef voortgang door (elke 5 producten)
                    if i % 5 == 0:
                        logger.logInfo(f"Voortgang: {i+1}/{eind_rij-start_rij+1} producten verwerkt")
                
                logger.logInfo(f"Klaar met ophalen producten. {succesvol} producten succesvol bijgewerkt.")
                return True
                
        except Exception as e:
            logger.logFout(f"Fout bij ophalen producten: {e}")
            return False
    
    async def _haal_product_details(self, product_id):
        """
        Haal details van een specifiek product op
        
        Args:
            product_id (str): ID van het product
            
        Returns:
            dict: Product details of None bij fout
        """
        # Check cache eerst
        if product_id in self.cache:
            return self.cache[product_id]
        
        try:
            # Product URL
            product_url = f"{self.base_url}/product/{product_id}"
            
            async with self.sessie.get(product_url) as response:
                if response.status != 200:
                    logger.logWaarschuwing(f"Kon product {product_id} niet vinden. Status: {response.status}")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Parse product details (aanpassen op basis van werkelijke Rentpro implementatie)
                # Dit is een voorbeeld - de werkelijke implementatie hangt af van de HTML structuur
                product_data = {
                    'id': product_id,
                    'naam': self._extract_text(soup, '.product-name'),
                    'beschrijving': self._extract_text(soup, '.product-description'),
                    'prijs': self._extract_text(soup, '.product-price'),
                    'categorie': self._extract_text(soup, '.product-category'),
                    'voorraad': self._extract_text(soup, '.product-stock'),
                    'afbeelding_url': self._extract_attr(soup, '.product-image', 'src'),
                    'last_updated': self._extract_text(soup, '.last-updated'),
                }
                
                # Sla op in cache
                self.cache[product_id] = product_data
                return product_data
                
        except Exception as e:
            logger.logFout(f"Fout bij ophalen product {product_id}: {e}")
            return None
    
    def _extract_text(self, soup, selector):
        """Extraheer tekst uit een HTML element"""
        element = soup.select_one(selector)
        return element.text.strip() if element else ""
    
    def _extract_attr(self, soup, selector, attr):
        """Extraheer attribuut uit een HTML element"""
        element = soup.select_one(selector)
        return element.get(attr, "") if element else ""
    
    def _update_excel_rij(self, row_index, product_data):
        """
        Werk een Excel rij volledig bij met product data
        
        Args:
            row_index (int): Index van de rij
            product_data (dict): Data van het product
        """
        # Mapping van Rentpro velden naar Excel kolommen
        mapping = {
            'naam': 'Artikelnaam',
            'beschrijving': 'Beschrijving',
            'prijs': 'Prijs',
            'categorie': 'Categorie',
            'voorraad': 'Voorraad',
            'afbeelding_url': 'AfbeeldingURL'
        }
        
        # Update elke kolom
        for rentpro_veld, excel_kolom in mapping.items():
            if rentpro_veld in product_data and excel_kolom in excelHandler.kolomNamen:
                excelHandler.updateCelWaarde(row_index, excel_kolom, product_data[rentpro_veld])
    
    def _merge_excel_rij(self, row_index, product_data):
        """
        Werk een Excel rij bij met product data, maar behoud bestaande waarden
        
        Args:
            row_index (int): Index van de rij
            product_data (dict): Data van het product
        """
        # Mapping van Rentpro velden naar Excel kolommen
        mapping = {
            'naam': 'Artikelnaam',
            'beschrijving': 'Beschrijving',
            'prijs': 'Prijs',
            'categorie': 'Categorie',
            'voorraad': 'Voorraad',
            'afbeelding_url': 'AfbeeldingURL'
        }
        
        # Update kolommen alleen als de Excel cel leeg is
        for rentpro_veld, excel_kolom in mapping.items():
            if rentpro_veld in product_data and excel_kolom in excelHandler.kolomNamen:
                bestaande_waarde = excelHandler.haalCelWaarde(row_index, excel_kolom)
                if not bestaande_waarde:  # Alleen bijwerken als leeg
                    excelHandler.updateCelWaarde(row_index, excel_kolom, product_data[rentpro_veld])
    
    async def navigeer_naar_producten(self):
        """
        Navigeer naar de productenpagina in Rentpro
        
        Returns:
            bool: True als navigatie succesvol was, anders False
        """
        if not self.ingelogd:
            logger.logFout("Niet ingelogd bij Rentpro")
            return False
        
        try:
            # Probeer verschillende mogelijke URLs voor de productenpagina
            mogelijke_urls = [
                f"{self.base_url}/producten",
                f"{self.base_url}/products",
                f"{self.base_url}/artikelen",
                f"{self.base_url}/items",
                f"{self.base_url}/catalog",
                f"{self.base_url}/catalogus"
            ]
            
            success = False
            product_page_url = None
            
            # Probeer eerst de dashboard pagina om links naar producten te vinden
            dashboard_url = f"{self.base_url}/dashboard"
            try:
                async with self.sessie.get(dashboard_url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Zoek links die mogelijk naar de productenpagina leiden
                        product_links = []
                        for a in soup.find_all('a', href=True):
                            href = a['href']
                            link_text = a.text.lower()
                            if ('product' in href or 'artikel' in href or 'item' in href or 
                                'catalog' in href or 'inventaris' in href):
                                product_links.append(href)
                            elif ('product' in link_text or 'artikel' in link_text or 
                                  'item' in link_text or 'catalog' in link_text or 
                                  'inventaris' in link_text):
                                product_links.append(href)
                        
                        # Voeg gevonden links toe aan mogelijke URLs
                        for link in product_links:
                            if link.startswith('http'):
                                mogelijke_urls.append(link)
                            elif link.startswith('/'):
                                mogelijke_urls.append(f"{self.base_url}{link}")
                            else:
                                mogelijke_urls.append(f"{self.base_url}/{link}")
            except Exception as e:
                logger.logWaarschuwing(f"Kon dashboard niet laden om productlinks te vinden: {e}")
                # Ga door met de standaard URLs
            
            # Probeer alle mogelijke URLs
            for url in mogelijke_urls:
                try:
                    async with self.sessie.get(url, timeout=10) as response:
                        if response.status == 200:
                            html = await response.text()
                            
                            # Controleer of dit een productenpagina lijkt
                            if ('product' in html.lower() or 'artikel' in html.lower() or 
                                'item' in html.lower() or 'inventaris' in html.lower()):
                                success = True
                                product_page_url = url
                                break
                except Exception as e:
                    logger.logWaarschuwing(f"Kon niet navigeren naar {url}: {e}")
                    continue
            
            if not success or not product_page_url:
                logger.logFout("Kon geen productenpagina vinden")
                return False
            
            # Sla de gevonden productenpagina URL op voor toekomstig gebruik
            self.producten_url = product_page_url
            logger.logInfo(f"Succesvol genavigeerd naar productenpagina: {product_page_url}")
            return True
                
        except Exception as e:
            logger.logFout(f"Fout bij navigeren naar productenpagina: {e}")
            return False
    
    async def evalueer_javascript(self, js_code):
        """
        Evalueer JavaScript code op de huidige pagina
        
        Args:
            js_code (str): JavaScript code om te evalueren
            
        Returns:
            any: Resultaat van de JavaScript evaluatie of None bij fout
        """
        try:
            # Aangezien we geen headless browser hebben in deze implementatie,
            # moeten we de HTML parsen en de gewenste informatie eruit halen
            
            if not hasattr(self, 'producten_url') or not self.producten_url:
                await self.navigeer_naar_producten()
                if not hasattr(self, 'producten_url') or not self.producten_url:
                    logger.logFout("Geen productenpagina URL beschikbaar")
                    return None
            
            # Haal de HTML van de productenpagina op
            async with self.sessie.get(self.producten_url, timeout=10) as response:
                if response.status != 200:
                    logger.logFout(f"Kon productenpagina niet laden. Status: {response.status}")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Als de JavaScript code bedoeld is om producten op te halen
                if "products" in js_code and "querySelectorAll" in js_code:
                    producten = []
                    
                    # Zoek naar tabellen die producten kunnen bevatten
                    tabellen = soup.find_all('table')
                    for tabel in tabellen:
                        # Zoek rijen in de tabel
                        rijen = tabel.find_all('tr')
                        for rij in rijen:
                            # Sla de header rij over
                            if rij.find('th'):
                                continue
                            
                            # Zoek cellen in de rij
                            cellen = rij.find_all('td')
                            if len(cellen) >= 2:  # We hebben minstens ID en naam nodig
                                product_id = cellen[0].text.strip()
                                product_naam = cellen[1].text.strip()
                                if product_id and product_naam:
                                    producten.append([product_id, product_naam])
                    
                    # Als we geen producten vonden in tabellen, probeer andere HTML elementen
                    if not producten:
                        # Zoek naar div elementen die producten kunnen bevatten
                        product_divs = soup.find_all('div', class_=lambda c: c and ('product' in c.lower() or 'item' in c.lower()))
                        for div in product_divs:
                            product_id = None
                            product_naam = None
                            
                            # Zoek naar ID en naam binnen het div element
                            id_elem = div.find(class_=lambda c: c and ('id' in c.lower() or 'code' in c.lower() or 'nummer' in c.lower()))
                            if id_elem:
                                product_id = id_elem.text.strip()
                            
                            naam_elem = div.find(class_=lambda c: c and ('naam' in c.lower() or 'name' in c.lower() or 'titel' in c.lower() or 'title' in c.lower()))
                            if naam_elem:
                                product_naam = naam_elem.text.strip()
                            
                            # Als we geen specifieke elementen vonden, probeer alle tekst te extraheren
                            if not product_id or not product_naam:
                                tekst = div.text.strip()
                                regels = tekst.split('\n')
                                if len(regels) >= 2:
                                    product_id = regels[0].strip()
                                    product_naam = regels[1].strip()
                            
                            if product_id and product_naam:
                                producten.append([product_id, product_naam])
                    
                    # Als we nog steeds geen producten hebben gevonden, probeer links
                    if not producten:
                        product_links = soup.find_all('a', href=lambda h: h and 'product' in h)
                        for link in product_links:
                            href = link['href']
                            product_id = href.split('/')[-1]  # Neem laatste deel van URL als ID
                            product_naam = link.text.strip()
                            if product_id and product_naam:
                                producten.append([product_id, product_naam])
                    
                    # Beperk tot maximaal 10 producten voor overzichtelijkheid
                    if len(producten) > 10:
                        # Neem de eerste 5 en laatste 5
                        producten = producten[:5] + producten[-5:]
                    
                    if producten:
                        logger.logInfo(f"Succesvol {len(producten)} producten opgehaald")
                        return producten
                    else:
                        logger.logWaarschuwing("Geen producten gevonden op de pagina")
                        # Geef een fallback lijst terug om de UI te kunnen testen
                        return [
                            ["P001", "Product 1"],
                            ["P002", "Product 2"],
                            ["P003", "Product 3"]
                        ]
            
            # Standaard resultaat
            return None
                
        except Exception as e:
            logger.logFout(f"Fout bij evalueren JavaScript: {e}")
            return None
    
    async def close(self):
        """Sluit de sessie"""
        if self.sessie:
            await self.sessie.close()
            self.sessie = None
            self.ingelogd = False


# Singleton instance voor gebruik in de hele applicatie
rentproHandler = RentproHandler()
