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
        
    async def login(self, gebruikersnaam, wachtwoord):
        """
        Log in op Rentpro
        
        Args:
            gebruikersnaam (str): Rentpro gebruikersnaam
            wachtwoord (str): Rentpro wachtwoord
            
        Returns:
            bool: True als inloggen succesvol is, anders False
        """
        try:
            if not self.sessie:
                await self.initialize()
                
            # Login URL
            login_url = f"{self.base_url}/login"
            
            # Eerst GET request om CSRF token te krijgen
            async with self.sessie.get(login_url) as response:
                if response.status != 200:
                    logger.logFout(f"Kon login pagina niet laden. Status: {response.status}")
                    return False
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Zoek CSRF token (aanpassen op basis van werkelijke Rentpro implementatie)
                csrf_token = soup.find('input', {'name': 'csrf_token'})
                if csrf_token:
                    csrf_token = csrf_token.get('value', '')
                else:
                    csrf_token = ''
            
            # Login data
            login_data = {
                'username': gebruikersnaam,
                'password': wachtwoord,
                'csrf_token': csrf_token
            }
            
            # POST request om in te loggen
            async with self.sessie.post(login_url, data=login_data, allow_redirects=True) as response:
                if response.status != 200:
                    logger.logFout(f"Login mislukt. Status: {response.status}")
                    return False
                
                # Controleer of login gelukt is (aanpassen op basis van werkelijke Rentpro implementatie)
                html = await response.text()
                if "Login mislukt" in html or "Ongeldige gebruikersnaam" in html:
                    logger.logFout("Login geweigerd: ongeldige gebruikersnaam/wachtwoord")
                    return False
            
            # Check of we ingelogd zijn door een beveiligde pagina te bekijken
            dashboard_url = f"{self.base_url}/dashboard"
            async with self.sessie.get(dashboard_url) as response:
                if response.status != 200:
                    logger.logFout("Kon niet verifiëren of login succesvol was")
                    return False
                
                html = await response.text()
                if "Inloggen" in html:
                    logger.logFout("Login niet succesvol")
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
    
    async def close(self):
        """Sluit de sessie"""
        if self.sessie:
            await self.sessie.close()
            self.sessie = None
            self.ingelogd = False


# Singleton instance voor gebruik in de hele applicatie
rentproHandler = RentproHandler()
