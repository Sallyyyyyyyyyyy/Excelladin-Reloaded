"""
Excel Manager voor RentPro integratie
Verantwoordelijk voor de interactie tussen RentPro data en Excel
"""
from modules.logger import logger
from modules.excel_handler import excelHandler

class ExcelManager:
    """
    Beheert de interactie tussen RentPro gegevens en Excel
    Scheidt de Excel-specifieke logica van de rest van de applicatie
    """
    
    def __init__(self):
        """
        Initialiseer de Excel manager
        """
        self.excel_handler = excelHandler  # Singleton uit de bestaande applicatie
        
    def is_bestand_geopend(self):
        """
        Controleert of er een Excel bestand is geopend
        
        Returns:
            bool: True als er een bestand is geopend, anders False
        """
        return self.excel_handler.isBestandGeopend()
        
    def update_product_row(self, row_index, product_data, overschrijf_lokaal=True):
        """
        Werk een Excel rij bij met product data
        
        Args:
            row_index (int): Index van de rij
            product_data (dict): Data van het product
            overschrijf_lokaal (bool): Of lokale data overschreven moet worden
            
        Returns:
            bool: True als update succesvol was, anders False
        """
        try:
            if not self.is_bestand_geopend():
                logger.logFout("Geen Excel-bestand geopend")
                return False
            
            # Mapping van RentPro velden naar Excel kolommen
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
                if rentpro_veld not in product_data:
                    continue
                    
                if excel_kolom not in self.excel_handler.kolomNamen:
                    logger.logWaarschuwing(f"Kolom {excel_kolom} niet gevonden in Excel bestand")
                    continue
                
                waarde = product_data[rentpro_veld]
                
                if overschrijf_lokaal:
                    # Overschrijf lokale data altijd
                    self.excel_handler.updateCelWaarde(row_index, excel_kolom, waarde)
                else:
                    # Alleen bijwerken als de cel leeg is
                    bestaande_waarde = self.excel_handler.haalCelWaarde(row_index, excel_kolom)
                    if not bestaande_waarde:
                        self.excel_handler.updateCelWaarde(row_index, excel_kolom, waarde)
            
            return True
            
        except Exception as e:
            logger.logFout(f"Fout bij bijwerken Excel rij {row_index}: {e}")
            return False
    
    def get_product_id(self, row_index):
        """
        Haal het product ID op uit een Excel rij
        
        Args:
            row_index (int): Index van de rij
            
        Returns:
            str: Product ID of None als niet gevonden
        """
        try:
            if not self.is_bestand_geopend():
                logger.logFout("Geen Excel-bestand geopend")
                return None
                
            product_id = self.excel_handler.haalCelWaarde(row_index, "ProductID")
            if not product_id:
                logger.logWaarschuwing(f"Geen ProductID gevonden in rij {row_index}")
                return None
                
            return product_id
            
        except Exception as e:
            logger.logFout(f"Fout bij ophalen ProductID uit rij {row_index}: {e}")
            return None
    
    def get_row_range(self, start_row=None, end_row=None):
        """
        Bepaal het bereik van rijen om te verwerken
        
        Args:
            start_row (int, optional): Eerste rij (0-based)
            end_row (int, optional): Laatste rij (0-based)
            
        Returns:
            tuple: (start_rij, eind_rij) of None bij fout
        """
        try:
            if not self.is_bestand_geopend():
                logger.logFout("Geen Excel-bestand geopend")
                return None
                
            # Bepaal totaal aantal rijen
            aantal_rijen = self.excel_handler.haalRijAantal()
            if aantal_rijen <= 0:
                logger.logFout("Excel bestand bevat geen rijen")
                return None
                
            # Bepaal start rij
            if start_row is None:
                start_rij = 0
            else:
                start_rij = max(0, min(start_row, aantal_rijen - 1))
                
            # Bepaal eind rij
            if end_row is None:
                eind_rij = aantal_rijen - 1
            else:
                eind_rij = max(start_rij, min(end_row, aantal_rijen - 1))
                
            return (start_rij, eind_rij)
            
        except Exception as e:
            logger.logFout(f"Fout bij bepalen rijbereik: {e}")
            return None

    def get_rows_with_product_ids(self, start_row=None, end_row=None):
        """
        Geef een lijst met rij-indices die een product ID hebben
        
        Args:
            start_row (int, optional): Eerste rij (0-based)
            end_row (int, optional): Laatste rij (0-based)
            
        Returns:
            list: Lijst met rij-indices die een product ID hebben
        """
        try:
            range_result = self.get_row_range(start_row, end_row)
            if not range_result:
                return []
                
            start_rij, eind_rij = range_result
            
            # Zoek rijen met product IDs
            rijen_met_id = []
            for rij in range(start_rij, eind_rij + 1):
                product_id = self.get_product_id(rij)
                if product_id:
                    rijen_met_id.append(rij)
                    
            return rijen_met_id
            
        except Exception as e:
            logger.logFout(f"Fout bij zoeken naar rijen met product IDs: {e}")
            return []
