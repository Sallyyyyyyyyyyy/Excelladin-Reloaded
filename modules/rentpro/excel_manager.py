"""
Excel Manager voor RentPro integratie
Verantwoordelijk voor het beheren van Excel interacties
"""
from modules.logger import logger
from modules.excel_handler import excelHandler

class ExcelManager:
    """
    Beheert alle Excel-gerelateerde functies voor RentPro integratie
    """
    
    def __init__(self):
        """Initialiseer de Excel manager"""
        pass
    
    def is_bestand_geopend(self):
        """
        Controleer of een Excel-bestand is geopend
        
        Returns:
            bool: True als een bestand is geopend, anders False
        """
        return excelHandler.isBestandGeopend()
    
    def get_row_range(self, start_row=None, end_row=None):
        """
        Bepaal het bereik van rijen om te verwerken
        
        Args:
            start_row (int, optional): Eerste rij om te verwerken (0-based)
            end_row (int, optional): Laatste rij om te verwerken (0-based)
            
        Returns:
            tuple: (start_row, end_row) of None bij fout
        """
        try:
            if excelHandler.isBestandGeopend():
                if start_row is not None and end_row is not None:
                    # Gebruik opgegeven bereik
                    return (start_row, end_row)
                else:
                    # Gebruik alle rijen met data
                    total_rows = excelHandler.getTotalRows()
                    if total_rows > 0:
                        return (0, total_rows - 1)
            
            return None
        except Exception as e:
            logger.logFout(f"Fout bij bepalen rijbereik: {e}")
            return None
    
    def get_product_id(self, row_index):
        """
        Haal het product ID op uit een rij
        
        Args:
            row_index (int): Index van de rij (0-based)
            
        Returns:
            str: Product ID of None bij fout
        """
        try:
            # Lees de eerste kolom (ProductID)
            product_id = excelHandler.getCellValue(row_index, 0)
            if product_id and isinstance(product_id, (str, int)):
                return str(product_id)
            return None
        except Exception as e:
            logger.logWaarschuwing(f"Kon product ID niet lezen van rij {row_index}: {e}")
            return None
    
    def update_product_row(self, row_index, product_data, overschrijf_lokaal=False):
        """
        Update een rij met productgegevens
        
        Args:
            row_index (int): Index van de rij om bij te werken (0-based)
            product_data (dict): Dictionary met productgegevens
            overschrijf_lokaal (bool): Of bestaande waarden overschreven moeten worden
            
        Returns:
            bool: True als update succesvol was, anders False
        """
        try:
            # Controleer of we geldige product data hebben
            if not product_data or not isinstance(product_data, dict):
                logger.logWaarschuwing(f"Ongeldige product data voor rij {row_index}")
                return False
            
            # Haal de huidige ID op en vergelijk
            current_id = self.get_product_id(row_index)
            if current_id != product_data.get('id'):
                logger.logWaarschuwing(f"Product ID mismatch: {current_id} != {product_data.get('id')}")
                return False
            
            # Update de relevante cellen
            # Kolom 1: Naam
            if 'naam' in product_data:
                if overschrijf_lokaal or not excelHandler.getCellValue(row_index, 1):
                    excelHandler.setCellValue(row_index, 1, product_data['naam'])
            
            # Kolom 2: Beschrijving
            if 'beschrijving' in product_data:
                if overschrijf_lokaal or not excelHandler.getCellValue(row_index, 2):
                    excelHandler.setCellValue(row_index, 2, product_data['beschrijving'])
            
            # Kolom 3: Prijs
            if 'prijs' in product_data:
                if overschrijf_lokaal or not excelHandler.getCellValue(row_index, 3):
                    excelHandler.setCellValue(row_index, 3, product_data['prijs'])
            
            # Kolom 4: Categorie
            if 'categorie' in product_data:
                if overschrijf_lokaal or not excelHandler.getCellValue(row_index, 4):
                    excelHandler.setCellValue(row_index, 4, product_data['categorie'])
            
            # Kolom 5: Voorraad
            if 'voorraad' in product_data:
                if overschrijf_lokaal or not excelHandler.getCellValue(row_index, 5):
                    excelHandler.setCellValue(row_index, 5, product_data['voorraad'])
            
            # Kolom 6: Afbeelding URL
            if 'afbeelding_url' in product_data:
                if overschrijf_lokaal or not excelHandler.getCellValue(row_index, 6):
                    excelHandler.setCellValue(row_index, 6, product_data['afbeelding_url'])
            
            # Kolom 7: Laatst bijgewerkt
            if 'last_updated' in product_data:
                excelHandler.setCellValue(row_index, 7, product_data['last_updated'])
            
            return True
        except Exception as e:
            logger.logFout(f"Fout bij updaten rij {row_index}: {e}")
            return False
