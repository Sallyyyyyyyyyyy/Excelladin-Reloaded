"""
HTML Parser module voor Excelladin Reloaded
Verantwoordelijk voor het analyseren van HTML bronbestanden en het extraheren van invoervelden
"""
import os
import re
from bs4 import BeautifulSoup
from modules.logger import logger

class HtmlParser:
    """
    HtmlParser klasse voor het verwerken van HTML bronbestanden
    """
    
    def __init__(self):
        """Initialiseer de HtmlParser"""
        self.bestand = None
        self.soup = None
        self.invoervelden = []
    
    def laad_bestand(self, bestandspad):
        """
        Laad een HTML bronbestand
        
        Args:
            bestandspad (str): Pad naar het HTML bronbestand
            
        Returns:
            bool: True als het bestand succesvol is geladen, anders False
        """
        try:
            # Controleer of het bestand bestaat
            if not os.path.exists(bestandspad):
                logger.logFout(f"Bestand niet gevonden: {bestandspad}")
                return False
            
            # Laad het bestand
            with open(bestandspad, 'r', encoding='utf-8', errors='replace') as f:
                inhoud = f.read()
            
            # Parse de inhoud
            self.soup = BeautifulSoup(inhoud, 'html.parser')
            self.bestand = bestandspad
            
            logger.logInfo(f"HTML bronbestand geladen: {bestandspad}")
            
            # Extraheer invoervelden
            self.zoek_invoervelden()
            
            return True
        except Exception as e:
            logger.logFout(f"Fout bij laden HTML bronbestand: {e}")
            return False
    
    def zoek_invoervelden(self):
        """
        Zoek naar invoervelden in het geladen HTML bestand
        
        Returns:
            list: Lijst met gevonden invoervelden
        """
        if not self.soup:
            logger.logWaarschuwing("Kan niet zoeken naar invoervelden: Geen bestand geladen")
            return []
        
        self.invoervelden = []
        
        # Zoek naar alle <input> elementen
        inputs = self.soup.find_all('input')
        for inp in inputs:
            veld_type = inp.get('type', 'text')
            veld_naam = inp.get('name', '')
            veld_id = inp.get('id', '')
            veld_waarde = inp.get('value', '')
            placeholder = inp.get('placeholder', '')
            
            # Sla alleen relevante invoervelden op
            if veld_type not in ['hidden', 'submit', 'button', 'image', 'reset']:
                self.invoervelden.append({
                    'type': veld_type,
                    'naam': veld_naam,
                    'id': veld_id,
                    'waarde': veld_waarde,
                    'placeholder': placeholder,
                    'element': 'input'
                })
        
        # Zoek naar <select> elementen (dropdown menu's)
        selects = self.soup.find_all('select')
        for select in selects:
            opties = []
            for option in select.find_all('option'):
                opties.append({
                    'waarde': option.get('value', ''),
                    'tekst': option.text.strip()
                })
            
            self.invoervelden.append({
                'type': 'select',
                'naam': select.get('name', ''),
                'id': select.get('id', ''),
                'opties': opties,
                'element': 'select'
            })
        
        # Zoek naar <textarea> elementen
        textareas = self.soup.find_all('textarea')
        for textarea in textareas:
            self.invoervelden.append({
                'type': 'textarea',
                'naam': textarea.get('name', ''),
                'id': textarea.get('id', ''),
                'waarde': textarea.text.strip(),
                'placeholder': textarea.get('placeholder', ''),
                'element': 'textarea'
            })
        
        # Zoek naar checkboxes en radiobuttons (behandeld als groepen)
        checkbox_groepen = {}
        radio_groepen = {}
        
        for inp in inputs:
            veld_type = inp.get('type', 'text')
            veld_naam = inp.get('name', '')
            
            if veld_type == 'checkbox' and veld_naam:
                if veld_naam not in checkbox_groepen:
                    checkbox_groepen[veld_naam] = []
                checkbox_groepen[veld_naam].append({
                    'id': inp.get('id', ''),
                    'waarde': inp.get('value', ''),
                    'label': self.vind_label_voor_input(inp)
                })
            
            elif veld_type == 'radio' and veld_naam:
                if veld_naam not in radio_groepen:
                    radio_groepen[veld_naam] = []
                radio_groepen[veld_naam].append({
                    'id': inp.get('id', ''),
                    'waarde': inp.get('value', ''),
                    'label': self.vind_label_voor_input(inp)
                })
        
        # Voeg checkbox groepen toe aan invoervelden
        for naam, opties in checkbox_groepen.items():
            self.invoervelden.append({
                'type': 'checkbox_groep',
                'naam': naam,
                'opties': opties,
                'element': 'input_groep'
            })
        
        # Voeg radio groepen toe aan invoervelden
        for naam, opties in radio_groepen.items():
            self.invoervelden.append({
                'type': 'radio_groep',
                'naam': naam,
                'opties': opties,
                'element': 'input_groep'
            })
        
        logger.logInfo(f"{len(self.invoervelden)} invoervelden gevonden in HTML bronbestand")
        return self.invoervelden
    
    def vind_label_voor_input(self, input_element):
        """
        Zoek het label dat bij een input element hoort
        
        Args:
            input_element: Het input element waarvoor een label wordt gezocht
            
        Returns:
            str: De tekst van het label of een lege string als er geen label is gevonden
        """
        # Probeer eerst het label te vinden via de 'id' van het input element
        input_id = input_element.get('id')
        if input_id:
            label = self.soup.find('label', attrs={'for': input_id})
            if label:
                return label.text.strip()
        
        # Als dat niet lukt, kijk of het input element zelf in een label element zit
        parent = input_element.parent
        while parent and parent.name != 'form' and parent.name != 'body':
            if parent.name == 'label':
                # Verwijder de tekst van eventuele sub-elementen
                label_tekst = parent.text.strip()
                for sub in parent.find_all():
                    if sub.text.strip():
                        label_tekst = label_tekst.replace(sub.text.strip(), '')
                return label_tekst.strip()
            parent = parent.parent
        
        return ""
    
    def genereer_excel_kolommen(self):
        """
        Genereer kolomnamen voor een Excel bestand op basis van de gevonden invoervelden
        
        Returns:
            list: Lijst met kolomnamen
        """
        kolommen = ['Veld_Type', 'Veld_Naam', 'Veld_ID', 'Veld_Waarde', 'Veld_Placeholder', 'Element_Type']
        
        # Voeg extra kolommen toe voor specifieke veldtypes
        # (bijv. voor dropdowns, checkboxes, radio buttons)
        has_options = any(veld.get('opties') for veld in self.invoervelden if veld.get('type') in ['select', 'checkbox_groep', 'radio_groep'])
        if has_options:
            kolommen.append('Opties')
        
        return kolommen
    
    def genereer_excel_data(self):
        """
        Genereer gegevens voor een Excel bestand op basis van de gevonden invoervelden
        
        Returns:
            list: Lijst met rijen (elke rij is een dict met kolomnaam: waarde)
        """
        if not self.invoervelden:
            return []
        
        excel_data = []
        
        for veld in self.invoervelden:
            rij = {
                'Veld_Type': veld.get('type', ''),
                'Veld_Naam': veld.get('naam', ''),
                'Veld_ID': veld.get('id', ''),
                'Veld_Waarde': veld.get('waarde', ''),
                'Veld_Placeholder': veld.get('placeholder', ''),
                'Element_Type': veld.get('element', '')
            }
            
            # Voeg opties toe als string voor select, checkbox_groep, radio_groep
            if veld.get('type') in ['select', 'checkbox_groep', 'radio_groep'] and 'opties' in veld:
                if veld.get('type') == 'select':
                    opties_str = '; '.join([f"{opt.get('tekst', '')}={opt.get('waarde', '')}" for opt in veld['opties']])
                else:  # checkbox_groep of radio_groep
                    opties_str = '; '.join([f"{opt.get('label', '')}={opt.get('waarde', '')}" for opt in veld['opties']])
                rij['Opties'] = opties_str
            
            excel_data.append(rij)
        
        return excel_data

# Singleton instance voor gebruik in de hele applicatie
html_parser = HtmlParser()
