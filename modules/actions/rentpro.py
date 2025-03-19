"""
RentPro connector module voor Excelladin Reloaded
Verantwoordelijk voor de interactie met RentPro via Puppeteer
"""
import os
import sys
import asyncio
import configparser
from pyppeteer import launch
from modules.logger import logger

def run_async(coroutine):
    """
    Voer een coroutine asynchroon uit vanuit tkinter
    
    Args:
        coroutine: De coroutine die uitgevoerd moet worden
        
    Returns:
        Het resultaat van de coroutine
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)

class RentProConnector:
    """RentPro connector via Puppeteer"""
    
    def __init__(self, app=None):
        """
        Initialiseer de RentPro connector
        
        Args:
            app: Optioneel, de hoofdapplicatie voor status updates
        """
        self.app = app
        self.browser = None
        self.page = None
        self.is_verbonden = False
        self.credentials = self.laad_credentials()
        self.browser_settings = self.laad_browser_settings()
    
    def laad_credentials(self):
        """
        Laad inloggegevens uit config bestand
        
        Returns:
            dict: Dictionary met inloggegevens
        """
        try:
            config = configparser.ConfigParser()
            config.read('config/rentpro.ini')
            
            credentials = {
                'gebruikersnaam': config.get('RentPro', 'gebruikersnaam'),
                'wachtwoord': config.get('RentPro', 'wachtwoord'),
                'url': config.get('RentPro', 'url')
            }
            
            return credentials
        except Exception as e:
            logger.logFout(f"Fout bij laden RentPro inloggegevens: {e}")
            return {
                'gebruikersnaam': '',
                'wachtwoord': '',
                'url': 'http://metroeventsdc.rentpro5.nl/'
            }
    
    def laad_browser_settings(self):
        """
        Laad browser instellingen uit config bestand
        
        Returns:
            dict: Dictionary met browser instellingen
        """
        try:
            config = configparser.ConfigParser()
            config.read('config/rentpro.ini')
            
            settings = {
                'headless': config.getboolean('Browser', 'headless', fallback=False),
                'window_width': config.getint('Browser', 'window_width', fallback=1600),
                'window_height': config.getint('Browser', 'window_height', fallback=900),
                'timeout': config.getint('Browser', 'timeout', fallback=30),
                'debug_port': config.getint('Browser', 'debug_port', fallback=9222)
            }
            
            return settings
        except Exception as e:
            logger.logFout(f"Fout bij laden browser instellingen: {e}")
            return {
                'headless': False,
                'window_width': 1600,
                'window_height': 900,
                'timeout': 30,
                'debug_port': 9222
            }
    
    def updateVoortgang(self, percentage, bericht):
        """
        Update de voortgangsindicatie
        
        Args:
            percentage (float): Percentage voltooiing (0-100)
            bericht (str): Voortgangsbericht
        """
        if hasattr(self, 'voortgangBar'):
            self.voortgangBar['value'] = percentage
        
        if self.app:
            self.app.updateStatus(f"{bericht} ({percentage:.1f}%)")
            self.app.root.update_idletasks()
    
    async def verbind(self):
        """
        Start browser en log in bij RentPro
        
        Returns:
            bool: True als verbinding succesvol is, anders False
        """
        try:
            if self.is_verbonden:
                logger.logInfo("Al verbonden met RentPro")
                return True
            
            self.updateVoortgang(10, "Browser starten...")
            
            # Browser opties instellen
            browser_args = [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                f'--window-size={self.browser_settings["window_width"]},{self.browser_settings["window_height"]}',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                f'--remote-debugging-port={self.browser_settings["debug_port"]}'
            ]
            
            # Browser starten
            self.browser = await launch({
                'headless': self.browser_settings['headless'],
                'args': browser_args
            })
            
            self.updateVoortgang(20, "Nieuwe pagina openen...")
            self.page = await self.browser.newPage()
            
            # Viewport instellen
            await self.page.setViewport({
                'width': self.browser_settings['window_width'],
                'height': self.browser_settings['window_height']
            })
            
            # Event handlers instellen
            self.page.on('dialog', lambda dialog: asyncio.ensure_future(self._handle_dialog(dialog)))
            self.page.on('error', lambda err: logger.logFout(f"Browser error: {err}"))
            
            # Navigeer naar RentPro
            self.updateVoortgang(30, "Navigeren naar RentPro...")
            await self.page.goto(self.credentials['url'])
            
            # Controleer op iframe en switch indien nodig
            self.updateVoortgang(40, "Controleren op iframe...")
            iframes = await self.page.querySelectorAll('iframe')
            if iframes:
                logger.logInfo("Iframe gevonden, switchen...")
                await self.page.evaluate('() => { document.querySelector("iframe").focus(); }')
                frames = self.page.frames
                if len(frames) > 1:
                    self.page = frames[1]
            
            # Inloggen
            self.updateVoortgang(50, "Inloggen bij RentPro...")
            
            # Gebruikersnaam invullen
            await self.page.waitForSelector('input[name="UserName"]')
            await self.page.type('input[name="UserName"]', self.credentials['gebruikersnaam'])
            
            # Wachtwoord invullen
            await self.page.waitForSelector('input[name="Password"]')
            await self.page.type('input[name="Password"]', self.credentials['wachtwoord'])
            
            # Login knop klikken
            await self.page.waitForSelector('input[type="submit"][value="Log in"]')
            await self.page.click('input[type="submit"][value="Log in"]')
            
            # Wachten tot ingelogd
            self.updateVoortgang(70, "Wachten op inloggen...")
            await self.page.waitForNavigation()
            
            # Controleer of inloggen succesvol was
            self.updateVoortgang(90, "Controleren of inloggen succesvol was...")
            content = await self.page.content()
            if "Klanten vandaag online" in content:
                logger.logInfo("Succesvol ingelogd bij RentPro")
                self.is_verbonden = True
                self.updateVoortgang(100, "Verbonden met RentPro")
                return True
            else:
                logger.logFout("Inloggen bij RentPro mislukt")
                self.updateVoortgang(100, "Inloggen bij RentPro mislukt")
                return False
        
        except Exception as e:
            logger.logFout(f"Fout bij verbinden met RentPro: {e}")
            self.updateVoortgang(100, f"Fout bij verbinden met RentPro: {e}")
            return False
    
    async def _handle_dialog(self, dialog):
        """
        Handel dialoogvensters af
        
        Args:
            dialog: Het dialoogvenster
        """
        logger.logInfo(f"Dialog: {dialog.type}, {dialog.message}")
        await dialog.dismiss()
    
    async def navigeer_naar_producten(self):
        """
        Ga naar productpagina
        
        Returns:
            bool: True als navigatie succesvol is, anders False
        """
        try:
            if not self.is_verbonden:
                logger.logWaarschuwing("Niet verbonden met RentPro")
                return False
            
            self.updateVoortgang(50, "Navigeren naar productpagina...")
            await self.page.goto(f"{self.credentials['url']}Product")
            
            # Wachten tot pagina geladen is
            await self.page.waitForSelector('body')
            
            # Extra wachttijd voor volledige lading
            await asyncio.sleep(3)
            
            self.updateVoortgang(100, "Productpagina geladen")
            return True
        
        except Exception as e:
            logger.logFout(f"Fout bij navigeren naar productpagina: {e}")
            return False
    
    async def navigeer_naar_nieuw_product(self):
        """
        Ga naar pagina voor nieuw product
        
        Returns:
            bool: True als navigatie succesvol is, anders False
        """
        try:
            if not self.is_verbonden:
                logger.logWaarschuwing("Niet verbonden met RentPro")
                return False
            
            self.updateVoortgang(50, "Navigeren naar nieuw product pagina...")
            await self.page.goto(f"{self.credentials['url']}Product/Edit")
            
            # Wachten tot pagina geladen is
            await self.page.waitForSelector('body')
            
            self.updateVoortgang(100, "Nieuw product pagina geladen")
            return True
        
        except Exception as e:
            logger.logFout(f"Fout bij navigeren naar nieuw product pagina: {e}")
            return False
    
    async def vul_product_veld(self, veld_id, waarde):
        """
        Vul een specifiek veld
        
        Args:
            veld_id (str): ID van het veld
            waarde: Waarde om in te vullen
            
        Returns:
            bool: True als invullen succesvol is, anders False
        """
        try:
            if not self.is_verbonden:
                logger.logWaarschuwing("Niet verbonden met RentPro")
                return False
            
            # Controleer of het veld bestaat
            element = await self.page.querySelector(f'#{veld_id}')
            if not element:
                logger.logWaarschuwing(f"Veld met ID '{veld_id}' niet gevonden")
                return False
            
            # Bepaal het type element
            tag_name = await self.page.evaluate('el => el.tagName.toLowerCase()', element)
            
            # Afhandeling per veldtype
            if tag_name == 'input':
                input_type = await self.page.evaluate('el => el.type', element)
                
                if input_type == 'checkbox':
                    # Checkbox
                    is_checked = await self.page.evaluate('el => el.checked', element)
                    should_check = waarde in [True, 'true', 'True', '1', 1, 'yes', 'Yes', 'Y', 'y']
                    
                    if should_check != is_checked:
                        await element.click()
                
                elif input_type == 'radio':
                    # Radio button
                    radio_value = str(waarde)
                    radio_selector = f'input[name="{veld_id}"][value="{radio_value}"]'
                    await self.page.click(radio_selector)
                
                else:
                    # Tekstveld
                    await element.click({ 'clickCount': 3 })  # Selecteer alle tekst
                    await element.type(str(waarde))
            
            elif tag_name == 'select':
                # Dropdown
                option_value = str(waarde)
                await self.page.select(f'#{veld_id}', option_value)
            
            elif tag_name == 'textarea':
                # Tekstvak
                await element.click({ 'clickCount': 3 })  # Selecteer alle tekst
                await element.type(str(waarde))
            
            return True
        
        except Exception as e:
            logger.logFout(f"Fout bij invullen veld '{veld_id}': {e}")
            return False
    
    async def klik_opslaan(self):
        """
        Klik op de opslaan knop
        
        Returns:
            bool: True als klikken succesvol is, anders False
        """
        try:
            if not self.is_verbonden:
                logger.logWaarschuwing("Niet verbonden met RentPro")
                return False
            
            # Zoek de opslaan knop
            button = await self.page.querySelector('button:contains("Product opslaan")')
            if not button:
                logger.logWaarschuwing("Opslaan knop niet gevonden")
                return False
            
            # Scroll naar de knop
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await self.page.evaluate('(el) => el.scrollIntoView({block: "center"})', button)
            await asyncio.sleep(1)
            
            # Klik op de knop
            await button.click()
            
            # Wacht op paginawissel
            await self.page.waitForNavigation()
            
            return True
        
        except Exception as e:
            logger.logFout(f"Fout bij klikken op opslaan knop: {e}")
            return False
    
    async def lees_product_data(self, product_id):
        """
        Haal productgegevens op
        
        Args:
            product_id (str): ID van het product
            
        Returns:
            dict: Dictionary met productgegevens of None bij fout
        """
        try:
            if not self.is_verbonden:
                logger.logWaarschuwing("Niet verbonden met RentPro")
                return None
            
            # Navigeer naar productpagina
            await self.page.goto(f"{self.credentials['url']}Product/Edit/{product_id}")
            
            # Wachten tot pagina geladen is
            await self.page.waitForSelector('body')
            
            # Verzamel alle velden
            form_data = await self.page.evaluate('''
                () => {
                    const data = {};
                    const inputs = document.querySelectorAll('input, select, textarea');
                    
                    inputs.forEach(input => {
                        if (input.id) {
                            if (input.type === 'checkbox') {
                                data[input.id] = input.checked;
                            } else if (input.type === 'radio') {
                                if (input.checked) {
                                    data[input.name] = input.value;
                                }
                            } else {
                                data[input.id] = input.value;
                            }
                        }
                    });
                    
                    return data;
                }
            ''')
            
            return form_data
        
        except Exception as e:
            logger.logFout(f"Fout bij ophalen productgegevens: {e}")
            return None
    
    async def sluit(self):
        """
        Sluit de browser
        
        Returns:
            bool: True als sluiten succesvol is, anders False
        """
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.page = None
                self.is_verbonden = False
                logger.logInfo("Browser gesloten")
                return True
            return False
        
        except Exception as e:
            logger.logFout(f"Fout bij sluiten browser: {e}")
            return False
    
    def lees_veld_mappings(self):
        """
        Leest de eerste twee rijen van de Excel sheet voor veldnaam/ID mappings
        
        Returns:
            dict: Dictionary met veldnaam -> veld_id mappings
        """
        from modules.excel_handler import excelHandler
        
        if not excelHandler.isBestandGeopend():
            raise ValueError("Geen Excel-bestand geopend")
            
        # Lees alle kolommen in eerste rij (veldnamen)
        veldnamen = []
        veld_ids = []
        
        for kolom in excelHandler.kolomNamen:
            namen = excelHandler.haalKolomOp(kolom, (0, 0))
            ids = excelHandler.haalKolomOp(kolom, (1, 1))
            
            if namen and ids:
                veldnamen.append(namen[0])
                veld_ids.append(ids[0])
        
        # Maak mapping dictionary
        mappings = {}
        for i, naam in enumerate(veldnamen):
            if i < len(veld_ids) and naam and veld_ids[i]:
                mappings[naam] = veld_ids[i]
        
        return mappings
