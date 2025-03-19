"""
RentPro upload module voor Excelladin Reloaded
Verantwoordelijk voor het uploaden van data naar RentPro
"""
import asyncio
from modules.logger import logger
from modules.excel_handler import excelHandler
from modules.actions.base import ActieBasis, ActieResultaat
from modules.actions.rentpro import RentProConnector, run_async

class RentProUploadActie(ActieBasis):
    """Actie om product data te uploaden naar RentPro"""
    
    def __init__(self):
        """Initialiseer de RentPro upload actie"""
        super().__init__(
            naam="rentProUpload",
            beschrijving="Uploadt productdata van Excel naar RentPro",
            categorie="Uploaden naar RentPro"
        )
    
    def voerUit(self, parameters, rijen=None):
        """
        Implementatie van de actie
        
        Args:
            parameters (dict): Parameters voor de actie, moet bevatten:
                - bronKolommen (list): Lijst met kolomnamen om te gebruiken als bron
            rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik te bewerken
            
        Returns:
            ActieResultaat: Resultaat van de actie
        """
        try:
            # Controleer verplichte parameters
            verplicht = ["bronKolommen"]
            for param in verplicht:
                if param not in parameters:
                    return ActieResultaat(
                        False, 
                        f"Ontbrekende parameter: {param}"
                    )
            
            bronKolommen = parameters["bronKolommen"]
            
            # Controleer of er een bestand is geopend
            if not excelHandler.isBestandGeopend():
                return ActieResultaat(
                    False, 
                    "Kan actie niet uitvoeren: Geen Excel-bestand geopend"
                )
            
            # Controleer of alle bronkolommen bestaan
            for kolom in bronKolommen:
                if kolom not in excelHandler.kolomNamen:
                    return ActieResultaat(
                        False, 
                        f"Bronkolom '{kolom}' bestaat niet in het bestand"
                    )
            
            # Bepaal het aantal rijen
            if rijen:
                startRij, eindRij = rijen
                aantalRijen = eindRij - startRij + 1
            else:
                aantalRijen = excelHandler.haalRijAantal()
                startRij, eindRij = 0, aantalRijen - 1
            
            # Maak RentPro connector
            connector = RentProConnector()
            
            # Verbind met RentPro
            logger.logInfo("Verbinden met RentPro...")
            if not run_async(connector.verbind()):
                return ActieResultaat(
                    False,
                    "Kon niet verbinden met RentPro"
                )
            
            # Lees veldmappings
            try:
                veld_mappings = connector.lees_veld_mappings()
            except Exception as e:
                run_async(connector.sluit())
                return ActieResultaat(
                    False,
                    f"Fout bij lezen veldmappings: {e}"
                )
            
            # Verwerk elke rij
            for rij_index in range(startRij, eindRij + 1):
                # Navigeer naar nieuw product pagina
                logger.logInfo(f"Navigeren naar nieuw product pagina voor rij {rij_index+1}...")
                if not run_async(connector.navigeer_naar_nieuw_product()):
                    logger.logWaarschuwing(f"Kon niet navigeren naar nieuw product pagina voor rij {rij_index+1}")
                    continue
                
                # Verzamel data uit Excel
                rij_data = {}
                for kolom in bronKolommen:
                    waarden = excelHandler.haalKolomOp(kolom, (rij_index, rij_index))
                    if waarden and waarden[0]:  # Controleer of er een waarde is
                        rij_data[kolom] = waarden[0]
                
                # Controleer of er data is
                if not rij_data:
                    logger.logWaarschuwing(f"Geen data gevonden voor rij {rij_index+1}")
                    continue
                
                # Vul formulier in
                logger.logInfo(f"Invullen formulier voor rij {rij_index+1}...")
                for kolom, waarde in rij_data.items():
                    if kolom in veld_mappings:
                        veld_id = veld_mappings[kolom]
                        logger.logInfo(f"Invullen veld '{veld_id}' met waarde '{waarde}'")
                        run_async(connector.vul_product_veld(veld_id, waarde))
                
                # Sla product op
                logger.logInfo(f"Opslaan product voor rij {rij_index+1}...")
                if not run_async(connector.klik_opslaan()):
                    logger.logWaarschuwing(f"Kon product niet opslaan voor rij {rij_index+1}")
                    continue
                
                logger.logInfo(f"Product succesvol opgeslagen voor rij {rij_index+1}")
            
            # Sluit browser
            run_async(connector.sluit())
            
            return ActieResultaat(
                True,
                f"Product data succesvol geüpload voor rijen {startRij+1} t/m {eindRij+1}"
            )
        
        except Exception as e:
            logger.logFout(f"Fout bij uitvoeren RentProUploadActie: {e}")
            return ActieResultaat(False, f"Fout bij uitvoeren actie: {e}")

class RentProBulkUploadActie(ActieBasis):
    """Actie om meerdere producten in bulk te uploaden naar RentPro"""
    
    def __init__(self):
        """Initialiseer de RentPro bulk upload actie"""
        super().__init__(
            naam="rentProBulkUpload",
            beschrijving="Uploadt meerdere producten in bulk van Excel naar RentPro",
            categorie="Uploaden naar RentPro"
        )
    
    def voerUit(self, parameters, rijen=None):
        """
        Implementatie van de actie
        
        Args:
            parameters (dict): Parameters voor de actie, moet bevatten:
                - bronKolommen (list): Lijst met kolomnamen om te gebruiken als bron
                - batch_grootte (int): Aantal producten per batch
            rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik te bewerken
            
        Returns:
            ActieResultaat: Resultaat van de actie
        """
        try:
            # Controleer verplichte parameters
            verplicht = ["bronKolommen"]
            for param in verplicht:
                if param not in parameters:
                    return ActieResultaat(
                        False, 
                        f"Ontbrekende parameter: {param}"
                    )
            
            bronKolommen = parameters["bronKolommen"]
            batch_grootte = parameters.get("batch_grootte", 10)
            
            # Controleer of er een bestand is geopend
            if not excelHandler.isBestandGeopend():
                return ActieResultaat(
                    False, 
                    "Kan actie niet uitvoeren: Geen Excel-bestand geopend"
                )
            
            # Controleer of alle bronkolommen bestaan
            for kolom in bronKolommen:
                if kolom not in excelHandler.kolomNamen:
                    return ActieResultaat(
                        False, 
                        f"Bronkolom '{kolom}' bestaat niet in het bestand"
                    )
            
            # Bepaal het aantal rijen
            if rijen:
                startRij, eindRij = rijen
                aantalRijen = eindRij - startRij + 1
            else:
                aantalRijen = excelHandler.haalRijAantal()
                startRij, eindRij = 0, aantalRijen - 1
            
            # Maak RentPro connector
            connector = RentProConnector()
            
            # Verbind met RentPro
            logger.logInfo("Verbinden met RentPro...")
            if not run_async(connector.verbind()):
                return ActieResultaat(
                    False,
                    "Kon niet verbinden met RentPro"
                )
            
            # Lees veldmappings
            try:
                veld_mappings = connector.lees_veld_mappings()
            except Exception as e:
                run_async(connector.sluit())
                return ActieResultaat(
                    False,
                    f"Fout bij lezen veldmappings: {e}"
                )
            
            # Verwerk in batches
            totaal_verwerkt = 0
            for batch_start in range(startRij, eindRij + 1, batch_grootte):
                batch_eind = min(batch_start + batch_grootte - 1, eindRij)
                
                logger.logInfo(f"Verwerken batch rijen {batch_start+1} t/m {batch_eind+1}...")
                
                # Verwerk elke rij in de batch
                for rij_index in range(batch_start, batch_eind + 1):
                    # Navigeer naar nieuw product pagina
                    logger.logInfo(f"Navigeren naar nieuw product pagina voor rij {rij_index+1}...")
                    if not run_async(connector.navigeer_naar_nieuw_product()):
                        logger.logWaarschuwing(f"Kon niet navigeren naar nieuw product pagina voor rij {rij_index+1}")
                        continue
                    
                    # Verzamel data uit Excel
                    rij_data = {}
                    for kolom in bronKolommen:
                        waarden = excelHandler.haalKolomOp(kolom, (rij_index, rij_index))
                        if waarden and waarden[0]:  # Controleer of er een waarde is
                            rij_data[kolom] = waarden[0]
                    
                    # Controleer of er data is
                    if not rij_data:
                        logger.logWaarschuwing(f"Geen data gevonden voor rij {rij_index+1}")
                        continue
                    
                    # Vul formulier in
                    logger.logInfo(f"Invullen formulier voor rij {rij_index+1}...")
                    for kolom, waarde in rij_data.items():
                        if kolom in veld_mappings:
                            veld_id = veld_mappings[kolom]
                            logger.logInfo(f"Invullen veld '{veld_id}' met waarde '{waarde}'")
                            run_async(connector.vul_product_veld(veld_id, waarde))
                    
                    # Sla product op
                    logger.logInfo(f"Opslaan product voor rij {rij_index+1}...")
                    if not run_async(connector.klik_opslaan()):
                        logger.logWaarschuwing(f"Kon product niet opslaan voor rij {rij_index+1}")
                        continue
                    
                    logger.logInfo(f"Product succesvol opgeslagen voor rij {rij_index+1}")
                    totaal_verwerkt += 1
            
            # Sluit browser
            run_async(connector.sluit())
            
            return ActieResultaat(
                True,
                f"{totaal_verwerkt} producten succesvol geüpload"
            )
        
        except Exception as e:
            logger.logFout(f"Fout bij uitvoeren RentProBulkUploadActie: {e}")
            return ActieResultaat(False, f"Fout bij uitvoeren actie: {e}")

class RentProUpdateActie(ActieBasis):
    """Actie om bestaande producten te updaten in RentPro"""
    
    def __init__(self):
        """Initialiseer de RentPro update actie"""
        super().__init__(
            naam="rentProUpdate",
            beschrijving="Update bestaande producten in RentPro met data uit Excel",
            categorie="Uploaden naar RentPro"
        )
    
    def voerUit(self, parameters, rijen=None):
        """
        Implementatie van de actie
        
        Args:
            parameters (dict): Parameters voor de actie, moet bevatten:
                - product_id_kolom (str): Kolomnaam met product IDs
                - bronKolommen (list): Lijst met kolomnamen om te gebruiken als bron
            rijen (tuple): Optioneel, tuple met (startRij, eindRij) om alleen een bereik te bewerken
            
        Returns:
            ActieResultaat: Resultaat van de actie
        """
        try:
            # Controleer verplichte parameters
            verplicht = ["product_id_kolom", "bronKolommen"]
            for param in verplicht:
                if param not in parameters:
                    return ActieResultaat(
                        False, 
                        f"Ontbrekende parameter: {param}"
                    )
            
            product_id_kolom = parameters["product_id_kolom"]
            bronKolommen = parameters["bronKolommen"]
            
            # Controleer of er een bestand is geopend
            if not excelHandler.isBestandGeopend():
                return ActieResultaat(
                    False, 
                    "Kan actie niet uitvoeren: Geen Excel-bestand geopend"
                )
            
            # Controleer of alle kolommen bestaan
            if product_id_kolom not in excelHandler.kolomNamen:
                return ActieResultaat(
                    False, 
                    f"Kolom '{product_id_kolom}' met product IDs bestaat niet in het bestand"
                )
            
            for kolom in bronKolommen:
                if kolom not in excelHandler.kolomNamen:
                    return ActieResultaat(
                        False, 
                        f"Bronkolom '{kolom}' bestaat niet in het bestand"
                    )
            
            # Bepaal het aantal rijen
            if rijen:
                startRij, eindRij = rijen
                aantalRijen = eindRij - startRij + 1
            else:
                aantalRijen = excelHandler.haalRijAantal()
                startRij, eindRij = 0, aantalRijen - 1
            
            # Maak RentPro connector
            connector = RentProConnector()
            
            # Verbind met RentPro
            logger.logInfo("Verbinden met RentPro...")
            if not run_async(connector.verbind()):
                return ActieResultaat(
                    False,
                    "Kon niet verbinden met RentPro"
                )
            
            # Lees veldmappings
            try:
                veld_mappings = connector.lees_veld_mappings()
            except Exception as e:
                run_async(connector.sluit())
                return ActieResultaat(
                    False,
                    f"Fout bij lezen veldmappings: {e}"
                )
            
            # Haal product IDs op
            product_ids = excelHandler.haalKolomOp(product_id_kolom, rijen)
            
            # Verwerk elke rij
            totaal_verwerkt = 0
            for i, product_id in enumerate(product_ids):
                rij_index = startRij + i
                
                # Controleer of product ID geldig is
                if not product_id:
                    logger.logWaarschuwing(f"Geen product ID gevonden voor rij {rij_index+1}")
                    continue
                
                # Navigeer naar product pagina
                logger.logInfo(f"Navigeren naar product pagina voor ID {product_id} (rij {rij_index+1})...")
                
                # Haal huidige product data op
                product_data = run_async(connector.lees_product_data(product_id))
                
                if not product_data:
                    logger.logWaarschuwing(f"Kon geen data ophalen voor product ID: {product_id}")
                    continue
                
                # Verzamel data uit Excel
                rij_data = {}
                for kolom in bronKolommen:
                    waarden = excelHandler.haalKolomOp(kolom, (rij_index, rij_index))
                    if waarden and waarden[0]:  # Controleer of er een waarde is
                        rij_data[kolom] = waarden[0]
                
                # Controleer of er data is
                if not rij_data:
                    logger.logWaarschuwing(f"Geen data gevonden voor rij {rij_index+1}")
                    continue
                
                # Vul formulier in
                logger.logInfo(f"Bijwerken formulier voor product ID {product_id} (rij {rij_index+1})...")
                for kolom, waarde in rij_data.items():
                    if kolom in veld_mappings:
                        veld_id = veld_mappings[kolom]
                        logger.logInfo(f"Bijwerken veld '{veld_id}' met waarde '{waarde}'")
                        run_async(connector.vul_product_veld(veld_id, waarde))
                
                # Sla product op
                logger.logInfo(f"Opslaan product voor ID {product_id} (rij {rij_index+1})...")
                if not run_async(connector.klik_opslaan()):
                    logger.logWaarschuwing(f"Kon product niet opslaan voor ID {product_id} (rij {rij_index+1})")
                    continue
                
                logger.logInfo(f"Product succesvol bijgewerkt voor ID {product_id} (rij {rij_index+1})")
                totaal_verwerkt += 1
            
            # Sluit browser
            run_async(connector.sluit())
            
            return ActieResultaat(
                True,
                f"{totaal_verwerkt} producten succesvol bijgewerkt in RentPro"
            )
        
        except Exception as e:
            logger.logFout(f"Fout bij uitvoeren RentProUpdateActie: {e}")
            return ActieResultaat(False, f"Fout bij uitvoeren actie: {e}")
